# Auditoria de acesso — clientes (`public.cliente`)

## Problema original

Com `dataService.getClients()` a fazer `select('*')` em `public.cliente` **sem filtro por utilizador**, qualquer utilizador autenticado com permissão de ver Cadastros ou de usar o Radar via Supabase (chave **anon** + políticas RLS permissivas ou ausentes) podia **listar todos os clientes** da base. O isolamento dependia quase só do que o UI mostrava, não de uma regra explícita no cliente.

## Modelo de dados

### Tabela `public.cliente` (campos relevantes)

- `id_cliente`, `nome_empresa`, `razao_social`, `cnpj`, `setor`, `porte_empresa`, `interesse_temas`, `interesse_valor_min`, `interesse_valor_max`, `status`, …
- **`id_usuario`**: dono do registo (ligação ao utilizador que criou / detém o cliente).

### Tabela `public.usuario`

- `id_usuario`, `nome`, `nome_email`, `senha`, `tipo_usuario`, `nivel_acesso`, `status`

A sessão no frontend (`authService` + `AuthContext`) persiste `id_usuario`, `tipo` (mapeado de `tipo_usuario`), `nivel` (mapeado de `nivel_acesso`), entre outros.

## Regras implementadas (frontend)

| Papel | Ver clientes | Criar | Editar / apagar |
|--------|----------------|-------|------------------|
| **Administrador** | Todos (sem filtro `id_usuario` na query) | `id_usuario` do utilizador atual quando existir na sessão | Qualquer linha (update/delete sem restrição extra de dono na query) |
| **Utilizador comum / consultor** | Apenas linhas com `cliente.id_usuario === currentUser.id_usuario` | `id_usuario` obrigatoriamente preenchido com o da sessão | Apenas do próprio `id_usuario` (filtro `.eq('id_usuario', …)` no update/delete) |

- Cliente com **`id_usuario` NULL**: **não** é visível para não-admin (`canViewClient` exige dono coincidente).
- **Pré-cadastro** (Cadastros): só abre se `canViewClient(currentUser, cliente)`; caso contrário mensagem: *"Você não tem permissão para acessar este cliente."*
- **Radar**: lista lateral alimentada por `getClients({ user })` + filtro defensivo `filterClientsForUser`; se a seleção deixar de existir na lista permitida, passa ao **primeiro** cliente permitido (em vez de ficar com ID órfão).

### Critério de administrador (`isAdminUser`)

Alinhado a `src/permissions.js` / `getPermissions`:

- `tipo` / `tipo_usuario` (string) igual a **Administrador** ou **Admin** (case-insensitive), **ou**
- `nivel` / `nivel_acesso` que mapeia para o perfil com **nível 1** (`PERMISSIONS.ADMIN`).

## Arquivos alterados

| Arquivo | Alteração |
|---------|-----------|
| `src/utils/permissions.js` | **Novo:** `isAdminUser`, `canViewClient`, `canEditClient`, `attachOwnerToClientPayload`, `sanitizeClientWritePayload`, `filterClientsForUser`, helpers de id. |
| `src/services/dataService.js` | `getClients({ user })` com `.eq('id_usuario', …)` para não-admin; `createClient` / `updateClient` / `deleteClient` com opções `{ user }` e restrições de dono. |
| `src/utils/normalizeCliente.js` | Garantir `id_usuario` normalizado na linha do cliente. |
| `src/pages/Cadastros.jsx` | `useAuth`, chamadas ao service com `{ user }`, validações de pré-cadastro e edição, payload de criação com dono. |
| `src/pages/RadarFomento.jsx` | `useAuth`, `getClients({ user })`, `filterClientsForUser`, seleção ao trocar lista. |

## Limitações

1. **Segurança real** continua a depender das **políticas RLS** no Supabase sobre `cliente`. O frontend reduz vazamento de dados na UI e na anon key, mas um cliente malicioso ainda pode tentar pedidos directos; RLS deve garantir o mesmo isolamento no servidor.
2. **Conta demo** `admin@finder.com` em produção **sem** `id_usuario` na sessão: continua a ser tratada como admin por `tipo`/`nivel`, mas criação de cliente pode gravar sem `id_usuario` se a sessão não tiver o campo — cenário marginal.
3. **Senha em texto** na tabela `usuario` (login actual) é **risco de segurança**; deve ser tratada noutra fase (hash, Supabase Auth, etc.) — não alterado nesta tarefa.

## Recomendação futura (RLS)

Definir políticas em `public.cliente`, por exemplo:

- `SELECT` / `UPDATE` / `DELETE`: para não-admin, `id_usuario = auth.uid()` mapeado para `id_usuario` da aplicação **ou** JWT custom com `id_usuario`; administradores com claim `admin`.

Enquanto a app usa login próprio (não Supabase Auth JWT), o mapeamento típico é: políticas baseadas em `id_usuario` igual ao utilizador da sessão validado por Edge Function ou por service restrito — o documento de produto deve fechar o modelo.

## Build

Após as alterações, executar `npm run build` no projeto `frontend/EditalFinder-React` e confirmar sucesso.

## Testes manuais sugeridos

1. Login como **administrador** → Cadastros → Clientes: ver lista completa (incl. clientes de outros donos, se existirem).
2. Login como **utilizador comum** com `id_usuario` definido → apenas clientes com o mesmo `id_usuario`.
3. Criar cliente como comum → verificar em `public.cliente` que `id_usuario` corresponde ao logado.
4. Radar com o mesmo utilizador → apenas clientes permitidos na lateral.
5. Pré-cadastro: tentar abrir cliente não permitido (se conseguir forçar na UI) → mensagem de bloqueio.

## Validação concluída

Registo de verificação em **staging**, com **RLS** activo em `public.cliente` e documentação em [`RLS_CLIENTE_SECURITY.md`](RLS_CLIENTE_SECURITY.md) / [`sql/RLS_CLIENTE.sql`](sql/RLS_CLIENTE.sql):

- **Login Supabase Auth** — a funcionar na aplicação.
- **`usuario.auth_user_id`** — preenchido para **admin** e **Caroline**.
- **`cliente.id_usuario`** — regra de dono a funcionar em conjunto com o frontend e com as policies.
- **Admin** — vê os clientes aplicáveis à sua regra (os seus e, conforme policy, o conjunto completo de administrador).
- **Caroline** — **não** vê clientes do admin (isolamento confirmado).
- **Criação de cliente** — restabelecida com **sessão autenticada** correta; o problema observado antes foi **sessão encerrada ou sem JWT**, não defeito das policies RLS.
- **RLS `cliente`** — tratado como **validado em staging**; produção exige nova bateria de testes após deploy de SQL e app.
