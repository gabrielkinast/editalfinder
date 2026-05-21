# Segurança RLS — `public.cliente`

Este documento acompanha o script [`sql/RLS_CLIENTE.sql`](sql/RLS_CLIENTE.sql), que ativa **Row Level Security** em `public.cliente` com base no **Supabase Auth** (`auth.uid()`) e no perfil interno `public.usuario` (`auth_user_id`, `tipo_usuario`, `status`).

## Pré-requisitos

1. **Supabase Auth** em uso: pedidos à API PostgREST com JWT de utilizador autenticado passam a role **`authenticated`**.
2. **`public.usuario`**: coluna `auth_user_id` (UUID) alinhada a `auth.users.id`; `status = 'Ativo'` (valor exato no SQL). As funções auxiliares usam **`SECURITY DEFINER`** para poderem ler `usuario` ao avaliar policies **sem** exigir `GRANT SELECT` em `usuario` para o role `authenticated` (recomendado no Supabase).
3. **`public.cliente.id_usuario`**: identifica o dono do registo; deve corresponder a `usuario.id_usuario` do criador (o frontend já envia isso para não-admin).
4. **Sequência de `id_cliente`**: se a PK for `SERIAL`/`BIGSERIAL`, após revogar `PUBLIC` pode ser necessário conceder `USAGE, SELECT` na sequência a `authenticated` (ver comentário no final do script SQL).
5. **Staging primeiro**: aplicar o script num ambiente de teste, validar CRUD com dois utilizadores e um administrador antes de produção.

## Resumo das policies

| Operação | Administrador (`tipo_usuario` ∈ {`Administrador`,`Admin`} e `Ativo`) | Utilizador comum (`Ativo`) |
|----------|------------------------------------------------------------------------|----------------------------|
| **SELECT** | Todas as linhas | Apenas `id_usuario = current_app_user_id()` |
| **INSERT** | Qualquer payload permitido pelo schema | Só se `id_usuario = current_app_user_id()` (não nulo) |
| **UPDATE** | Qualquer linha; pode alterar `id_usuario` | Só linhas próprias; **WITH CHECK** impede mudar `id_usuario` para outro utilizador |
| **DELETE** | Qualquer linha | Só linhas com `id_usuario = current_app_user_id()` |

Funções auxiliares (definidas em [`sql/RLS_CLIENTE.sql`](sql/RLS_CLIENTE.sql)):

- **`public.current_app_user_id()`** — `SECURITY DEFINER`, `STABLE`, `search_path = public`: devolve `id_usuario` onde `usuario.auth_user_id = auth.uid()` e `status = 'Ativo'`.
- **`public.current_app_user_is_admin()`** — idem: `true` se existir linha com `tipo_usuario IN ('Administrador','Admin')` e `Ativo`.

## Grants e `anon`

- **`authenticated`**: `SELECT`, `INSERT`, `UPDATE`, `DELETE` em `public.cliente` + `EXECUTE` nas duas funções.
- **`anon`**: `REVOKE ALL` em `cliente` — pedidos **sem** JWT não devem ler nem escrever clientes.
- **`service_role`**: não é usada no frontend; no servidor continua a ignorar RLS no Supabase (uso só em Edge Functions / jobs confiáveis).

## Como testar (manual)

1. No **SQL Editor**, aplicar `RLS_CLIENTE.sql` (ou blocos por fases: funções → RLS → policies → grants).
2. **Utilizador A** (não admin): login na app → Cadastros / lista de clientes → confirmar que só aparecem linhas com `id_usuario` igual ao de A.
3. **Utilizador B**: confirmar que não vê clientes de A (nem via consola de rede alterando filtros no JS — o PostgREST aplica RLS).
4. **Admin**: confirmar listagem de todos os clientes e possibilidade de INSERT/UPDATE/DELETE alargados.
5. **UPDATE como comum**: tentar gravar outro `id_usuario` (ex. via REST directo) → deve falhar no `WITH CHECK`.
6. **Sem login**: pedido `select` em `cliente` com só a chave anon → deve falhar por falta de privilégio / política.

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Utilizador sem `auth_user_id` ou `status` ≠ `'Ativo'` | `current_app_user_id()` fica nulo → sem linhas em SELECT; INSERT/UPDATE bloqueados — alinhar dados antes de activar RLS. |
| `status` ou `tipo_usuario` com capitalização diferente na BD | Ajustar o SQL (ex. `lower(trim(status))`) ou normalizar dados. |
| Sequência sem `GRANT` | Inserções falham após `REVOKE PUBLIC` — aplicar o `GRANT` na sequência indicada no script. |
| Jobs ETL com **anon** | Passam a não aceder a `cliente`; usar `service_role` só no servidor ou role dedicada. |
| Linhas `cliente.id_usuario` NULL | Não-admin não as vê; admin vê e pode gerir — coerente com o modelo documentado no frontend. |

## Rollback

No próprio [`RLS_CLIENTE.sql`](sql/RLS_CLIENTE.sql) existe uma secção **comentada** no final: `DROP POLICY` → `DISABLE ROW LEVEL SECURITY` → `DROP FUNCTION` → repor `GRANT` para `anon`/`authenticated` conforme o estado anterior do projecto.

Revise os grants de rollback: o bloco sugerido é genérico; o seu ambiente pode ter tido permissões diferentes.

## Frontend vs RLS

- **Frontend**: filtra por UX e reduz chamadas inúteis; pode ser contornado por um cliente HTTP malicioso.
- **RLS**: garante no **Postgres** que cada linha satisfaz as mesmas regras de posse/admin, independentemente do cliente.

Ambos devem coexistir: UI limpa + garantia no banco.

## Checklist multiutilizador

- [ ] Dois utilizadores não-admin com `auth_user_id` distintos e `Ativo`.
- [ ] Cada um só lista os seus clientes.
- [ ] Admin lista todos.
- [ ] Comum não altera `id_usuario` de um cliente alheio (teste directo à API).
- [ ] Comum não apaga cliente alheio.
- [ ] Logout / pedido anon não lê `cliente`.
- [ ] Inserção de cliente como comum grava `id_usuario` correto e passa RLS.

## Validação concluída

Registo de verificação em **staging** (ambiente de testes), após integração Supabase Auth + RLS em `public.cliente`:

- **Login Supabase Auth** — fluxo de autenticação operacional na app.
- **`public.usuario.auth_user_id`** — preenchido para o **administrador** e para **Caroline** (ligação estável a `auth.users`).
- **`public.cliente.id_usuario`** — dono do registo alinhado ao modelo; isolamento por utilizador coerente com as policies.
- **Administrador** — visualização de clientes conforme a regra definida (os seus e o conjunto aplicável a admin, conforme policy de `SELECT`).
- **Caroline** (utilizador comum) — **não** visualiza clientes pertencentes ao admin (isolamento por dono confirmado).
- **Criação de cliente** — voltou a funcionar após garantir **sessão autenticada** válida (JWT presente nos pedidos PostgREST); o incidente anterior foi atribuído a **sessão encerrada / ausência de sessão**, e **não** a falha das policies em si.
- **RLS em `cliente`** — considerado **validado em staging** para prosseguimento do plano de endurecimento; produção deve repetir smoke tests antes de aplicar o mesmo conjunto.

Para detalhe do modelo de acesso na UI e no serviço, ver também [`CLIENT_ACCESS_SECURITY_AUDIT.md`](CLIENT_ACCESS_SECURITY_AUDIT.md).

## Debug pós-aplicação

### Sintoma: “Erro ao carregar dados” na página Cadastros (ou zero clientes com erro no console)

1. **Consola (DEV)** — Com o build de desenvolvimento, procure:
   - `[dataService.getClients] supabase` — inclui `message`, `code`, `details`, `hint` do PostgREST.
   - `[Cadastros] loadData falhou` — inclui o separador `tab` ativo.
   - Avisos sobre **sem sessão** / **sem access_token** antes da query.

2. **`permission denied for table usuario`** (ou erro ao avaliar política)  
   - Causa típica com funções **SECURITY INVOKER**: o role `authenticated` não consegue ler `public.usuario` dentro da função.  
   - **Correcção:** voltar a criar as funções com **`SECURITY DEFINER`** como no script atual em `RLS_CLIENTE.sql` (bloco `CREATE OR REPLACE FUNCTION`).

3. **`permission denied for table cliente`** ou `42501`  
   - Confirmar `GRANT SELECT, INSERT, UPDATE, DELETE ON public.cliente TO authenticated` e que o pedido leva **JWT** (utilizador com sessão), não só a chave anon sem `Authorization`.

4. **Zero linhas sem erro**  
   - `auth.uid()` nulo (sem sessão) → políticas não concedem linhas.  
   - `current_app_user_id()` nulo: `auth_user_id` / `status` na linha de `usuario` não batem com o SQL (`'Ativo'` exacto).  
   - `id_usuario` do cliente ≠ `id_usuario` do perfil (dados).

5. **Rede** — No pedido a `.../rest/v1/cliente`, verificar cabeçalho **`Authorization: Bearer ...`** e resposta JSON de erro do PostgREST.

6. **Reaplicar só as funções** (SQL Editor), sem desactivar RLS:

```sql
-- Colar apenas os dois CREATE OR REPLACE FUNCTION ... SECURITY DEFINER
-- do ficheiro docs/sql/RLS_CLIENTE.sql
```

## Instrução de aplicação manual

1. Abrir o **Supabase Dashboard** → **SQL** → novo query.
2. Colar o conteúdo de `docs/sql/RLS_CLIENTE.sql`.
3. Rever o nome da **sequência** de `id_cliente` (`\d public.cliente` no `psql` ou editor de tabelas) e descomentar/ajustar o `GRANT` da sequência se os inserts falharem.
4. Executar o script **uma vez** por ambiente.
5. Percorrer a secção **Como testar** e o **checklist** acima.
