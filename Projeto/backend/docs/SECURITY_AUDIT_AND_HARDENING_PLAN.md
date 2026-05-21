# EditalFinder — Auditoria de segurança e plano de endurecimento

**Âmbito:** frontend (React/Vite), integração Supabase (anon), autenticação/sessão actual, isolamento por `id_usuario`, variáveis de ambiente.  
**Data do relatório:** baseado no estado do repositório na análise estática (sem consulta ao painel Supabase nem execução de SQL).

**Restrições desta entrega:** apenas documentação — sem alterações a código de aplicação, sem migrações executadas, sem mudanças de schema.

---

## 1. Resumo executivo

| Área | Situação | Severidade |
|------|-----------|------------|
| Senha `usuario.senha` | Comparada em claro no cliente após `select('*')`; registo grava senha em claro | **Crítica** |
| Sessão | `localStorage` (`editalFinderUser`) sem assinatura, expiração ou vínculo a token | **Alta** |
| Identidade adulterável | Qualquer utilizador pode editar `localStorage` e fingir outro `id_usuario` / `tipo` | **Alta** |
| Supabase no browser | Apenas chave **anon** no código analisado — correcto; risco move-se para **RLS** e políticas | **Média–Alta** (depende do projeto) |
| Isolamento cliente/favoritos | Filtros e `.eq('id_usuario')` no **frontend**; não substitui RLS se anon tiver acesso amplo | **Alta** se RLS fraca |
| Pré-cadastro | Rascunho em **localStorage** por `clienteId`; não é segredo de servidor mas é dados no dispositivo | **Baixa–Média** |
| `service_role` no front | Não encontrado no código fonte analisado | **OK** (manter regra) |

---

## 2. Auditoria — autenticação actual

### 2.1 Ficheiros mapeados

| Ficheiro | Papel |
|----------|--------|
| `frontend/EditalFinder-React/src/services/authService.js` | `login`, `registerUser`, `logout`, `getUser`; consulta/insert em `public.usuario` |
| `frontend/EditalFinder-React/src/contexts/AuthContext.jsx` | Estado `user`, `login`, `register`, `logout`, hidratação inicial a partir de `getUser()` |
| `frontend/EditalFinder-React/src/pages/Login.jsx` | Modos Entrar / Criar conta, validação mínima de senha (6 caracteres no registo) |
| `frontend/EditalFinder-React/src/services/supabaseClient.js` | Cliente `createClient(URL, SUPABASE_ANON_KEY)` |
| `frontend/EditalFinder-React/src/config/env.js` | `SUPABASE_ANON_KEY`, comentário explícito contra `service_role` |

### 2.2 Fluxo de login

1. Com Supabase configurado: `select('*').eq('nome_email', emailNormalizado).single()` em `usuario`.
2. Se `usuario.senha === password` (comparação **literal no browser**), monta `userData` **sem** incluir a senha no objecto guardado.
3. Grava `JSON.stringify(userData)` em `localStorage` chave **`editalFinderUser`**.
4. Conta demo: `admin@finder.com` / `123456` (comportamento especial, `id_usuario` só em DEV).

### 2.3 Fluxo de registo (`registerUser`)

- Validação de formato/comprimento no cliente.
- Verifica duplicado de `nome_email`.
- `insert` com `tipo_usuario: 'Consultor'`, `nivel_acesso: 2`, `status: 'Ativo'`, **`senha` em texto plano** na coluna.
- `select` devolve `id_usuario` e preenche a mesma estrutura de sessão que o login.

### 2.4 Logout

- `localStorage.removeItem('editalFinderUser')` + `setUser(null)`.

### 2.5 Formato `editalFinderUser` (sessão)

Campos típicos: `id_usuario`, `email`, `nome`, `tipo`, `nivel`, `status` (espelho de `tipo_usuario` / `nivel_acesso`). **Não há token JWT**, refresh, nem expiração automática.

### 2.6 Permissões no app

- `src/permissions.js` + `usePermissions.js`: RBAC por `user.nivel` ou `user.tipo` (ex.: Administrador nível 1).
- **Não há verificação criptográfica** de que o `user` em memória corresponde a um login válido recente.

### 2.7 Respostas directas (checklist do pedido)

| Pergunta | Resposta |
|----------|----------|
| A senha é comparada no frontend? | **Sim** — após o row completo chegar ao cliente (`usuario.senha === password`). |
| A senha é armazenada em texto puro na base? | **O código assume coluna `senha` legível**; insert de registo envia a senha em claro. Hash não é aplicado no front. |
| O frontend consulta `public.usuario` directo? | **Sim** (Supabase PostgREST com anon). |
| O utilizador pode adulterar `localStorage` e virar outro `id_usuario`? | **Sim.** O app confia no JSON; APIs subsequentes que dependam só do `id_usuario` enviado pelo cliente **sem RLS** são vulneráveis a escalamento horizontal de dados. |
| Existe token real? | **Não** no modelo actual (sessão = objecto em `localStorage`). |
| Existe Supabase Auth (`auth.users`)? | **Não integrado** no fluxo actual — login é custom sobre tabela `usuario`. |
| Existe sessão expirada? | **Não** implementada no código analisado. |

---

## 3. Auditoria — dados sensíveis (tabelas / views usadas pelo frontend)

Estado **RLS / políticas**: **não verificável** só pelo repositório. Deve ser confirmado no Supabase (SQL editor ou UI: *Table → RLS*). A coluna “Políticas” abaixo indica o **mínimo esperado** para endurecimento.

| Objeto | Uso no front (referência) | Dados sensíveis | Exposição típica | Políticas / RLS (esperado) |
|--------|---------------------------|-----------------|-------------------|----------------------------|
| `public.usuario` | `authService`, `dataService.getUsers` / CRUD cadastros | Senha, e-mail, perfil | **Privado** por utilizador; admins para gestão | SELECT/INSERT/UPDATE restritos; **nunca** SELECT de `senha` para anon; insert público só com política muito restrita ou via RPC |
| `public.cliente` | `dataService.getClients`, CRUD; Radar | Dados empresariais, `id_usuario` | **Por dono** + admin | RLS: `id_usuario = current_setting(...)` ou `auth.uid()` mapeado |
| `public.edital_favorito` | `favoritosService` tabela + view favoritos | Preferências, prazos | **Por dono** | RLS por `id_usuario` |
| `vw_editais_favoritos_front` (ou env) | `fetchFavoritos` | Join favoritos/editais | Leitura filtrada | View `security_invoker` ou RLS nas tabelas base |
| `vw_editais_front` / `VITE_VIEW_EDITAIS` | `getEditais` | Catálogo público de editais | Tipicamente **leitura pública** filtrada | SELECT anon OK se view não expuser PII interno |
| `public.edital` | Admin CRUD cadastros | Conteúdo edital | Misto | RLS: escrita só role admin/service |
| `public.edital_anexo` | `dataService` | URLs / metadados | Depende | RLS alinhado a `edital` |
| `vw_noticias_front` / `noticia` | Feed notícias | Conteúdo público | Geralmente leitura | SELECT controlado |
| `vw_pesquisas_front` / `pesquisa` | Idem | Idem | Idem | Idem |
| `vw_fornecedores_front` | Portais | Dados agregados | Leitura pública típica | Idem |
| `vw_investimentos_front` | Portais | Idem | Idem | Idem |
| `public.organizacao` | Cadastros | Referencial | Interno | RLS ou só service |

**Pré-cadastro:** persistência principal em **`localStorage`** (chaves por `clienteId` / fingerprint em `precadastroProjetoInitialState.js`); `sessionStorage` para contexto Radar (`precadastro_context_${id}`) em `Cadastros.jsx`. **Não há tabela dedicada** de pré-cadastro identificada no `dataService` — risco é sobretudo **XSS** ou partilha de máquina, não leak via PostgREST.

---

## 4. Auditoria — isolamento por `id_usuario`

### 4.1 Implementação actual (código)

| Área | Comportamento |
|------|----------------|
| **Cliente** | `getClients({ user })`: não-admin → `.eq('id_usuario', uid)`; admin → sem filtro. Updates/deletes com `.eq('id_usuario')` para não-admin. |
| **Cadastros** | `utils/permissions.js` — `canViewClient` / `canEditClient`; pré-cadastro bloqueado com mensagem se não permitido. |
| **Radar** | Mesmo `getClients` + `filterClientsForUser`; selecção reposta se ID inválido. |
| **Favoritos** | `fetchFavoritos` com `.eq('id_usuario', …)`; writes com `id_usuario` no payload; DEV fallback documentado. |
| **Admin** | Vê todos os clientes (query sem filtro) conforme regra de produto. |

### 4.2 Front vs banco

- A lógica **também** está no cliente (filtros, botões). **A barreira real** é: **RLS** (e eventualmente revogação de grants) para que **mesmo** com `localStorage` adulterado ou DevTools, o PostgREST **não** devolva nem escreva linhas de outros utilizadores.

### 4.3 Risco de “consultar todos” via Supabase client

Se a política anon para `cliente` ou `edital_favorito` for `USING (true)` ou equivalente permissivo, **qualquer script** com a mesma anon key recupera todas as linhas. O UI esconde, mas **não protege**.

---

## 5. Auditoria — `service_role`, env e segredos

### 5.1 Código frontend

- `env.js` e comentários reforçam: **apenas anon/public**.
- Grep por `service_role` / `SERVICE_ROLE` no `src`: apenas menções **documentais** em `env.js`.

### 5.2 Ficheiros de ambiente

| Ficheiro | Versão no repo |
|----------|----------------|
| `frontend/EditalFinder-React/.env.example` | Placeholders; sem segredos reais |
| `.env` / `.env.local` | **Ignorados pelo git** (ver `.gitignore`) |

### 5.3 `.gitignore`

- **Raiz** (`edital/.gitignore`): `.env`, `.env.*`, `CORE/.env`, padrões `*.key`, `*.pem`, `service_role*.json`, etc.
- **Frontend** (`frontend/EditalFinder-React/.gitignore`): `.env`, `.env.local`, `.env.*` com excepção `!.env.example`.

**Risco residual:** commit acidental de chaves fora desses padrões; revisão periódica e pre-commit hooks recomendados.

### 5.4 Logs

- `dataService` / `authService`: logs de desenvolvimento com contagens ou códigos de erro — **não** devem incluir passwords (o código actual não faz `console.log` da senha; manter a regra em reviews).

---

## 6. Diagnóstico RLS (prioridades)

**Tabelas com RLS obrigatório (recomendado):**

1. `public.usuario` — especialmente coluna `senha`; inserts públicos só se política for extremamente limitada ou substituída por Edge Function.
2. `public.cliente` — isolamento por dono + excepção admin.
3. `public.edital_favorito` — idem.
4. Tabelas de **escrita admin** (`edital`, `organizacao`, …) — sem acesso anon de escrita amplo.

**Views:** preferir `security_invoker` (Postgres 15+) ou garantir que as políticas nas tabelas base restringem o que a view expõe.

**Ficheiro de exemplos SQL (não executado):** ver `docs/sql/SECURITY_RLS_EXAMPLES.sql` — ilustrações comentadas para discussão com DBA; **não** são migrações aplicadas.

---

## 7. Arquitectura segura — opções

### Opção A — Supabase Auth (recomendada para ~2 meses com menor reinventar)

- `signUp` / `signInWithPassword`, sessão JWT gerida pelo SDK, refresh, expiração.
- `public.usuario` vira **perfil de aplicação** com `auth_user_id uuid` único referenciando `auth.users.id`.
- RLS com `auth.uid()` (e claims opcionais para admin).
- Encerrar comparação de senha no cliente sobre coluna `senha`; migrar passwords ou forçar reset.

**Prós:** MFA, e-mail de confirmação, menos código custom de sessão. **Contras:** migração de utilizadores existentes e políticas RLS a desenhar.

### Opção B — API própria + cookies httpOnly

- Browser fala só com API; API usa service role ou DB directo com credenciais servidor.
- Senhas com hash (Argon2/bcrypt) no servidor.
- RLS opcional se a API for o único caminho.

**Prós:** controlo total. **Contras:** mais tempo (auth, hardening, hosting da API) para prazo semelhante.

### Recomendação (prazo ~2 meses)

**Opção A (Supabase Auth + perfil + RLS)** como caminho principal: alinha com a stack já em uso, reduz superfície de sessão em `localStorage` e concentra políticas no Postgres.

---

## 8. Plano de migração em fases

### Fase Segurança 1 — Baseline (1–2 semanas)

- [ ] Inventariar no Supabase: RLS on/off por tabela; policies existentes; grants anon.
- [ ] Confirmar que **nenhum** bundle ou repo contém `service_role`.
- [ ] Rever `.gitignore` e histórico recente por fuga de `.env`.
- [ ] Documentar matriz “rota → tabela → operação”.

### Fase Segurança 2 — Auth (3–6 semanas, em paralelo com RLS desenho)

- [ ] Introduzir Supabase Auth; fluxo sign-up/sign-in.
- [ ] Adicionar `auth_user_id` (uuid) em `usuario`; trigger ou app: criar perfil após primeiro login.
- [ ] Migração de utilizadores legacy: convite de reset de password ou script one-shot (fora do browser).
- [ ] Manter login legacy atrás de feature flag só até cutover.

### Fase Segurança 3 — RLS dono/admin (2–4 semanas)

- [ ] `cliente`, `edital_favorito`: policies owner; role admin via claim ou tabela de roles.
- [ ] Rever views favoritas / editais para não vazar colunas internas.

### Fase Segurança 4 — Senha (1–2 semanas)

- [ ] Deixar de ler/escrever `usuario.senha` no cliente; coluna deprecated ou removida após migração.
- [ ] Forçar redefinição para utilizadores só legacy.

### Fase Segurança 5 — QA e documentação (contínuo)

- [ ] Testes multi-utilizador + tentativa de bypass (Postman com anon key + payloads maliciosos).
- [ ] Runbook de incidentes e rotação de chaves.

---

## 9. Checklist de testes (pós-endurecimento)

1. Dois browsers / contas: A não vê dados de B em `cliente` e `edital_favorito` **via API** (não só UI).
2. `localStorage` adulterado com `id_usuario` de outrem → pedidos Supabase **falham** ou devolvem vazio.
3. Registo público não cria `Administrador` nem eleva `nivel_acesso`.
4. Sessão expira / refresh conforme política Supabase Auth.
5. Portais/views públicas continuam acessíveis conforme desenho.
6. Regressão: Radar, Cadastros, favoritos, pré-cadastro.

---

## 10. Próximos passos imediatos

1. **Workshop Supabase** (1 sessão): exportar políticas actuais e comparar com a matriz deste documento.
2. **Congelar** novos endpoints anon sem RLS.
3. **Roadmap** da Fase 2 com owner técnico e data de cutover do login legacy.

---

## Anexos no repositório

| Ficheiro | Conteúdo |
|----------|----------|
| `docs/sql/SECURITY_RLS_EXAMPLES.sql` | Exemplos comentados de políticas — **referência apenas; não executar como migração automática** |
| `docs/AUTH_SIGNUP_MVP.md` | Comportamento actual do sign-up MVP |
| `docs/CLIENT_ACCESS_SECURITY_AUDIT.md` | Isolamento de clientes no front |
