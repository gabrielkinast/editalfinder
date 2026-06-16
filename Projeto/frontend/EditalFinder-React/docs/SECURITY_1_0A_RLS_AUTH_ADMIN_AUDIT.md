# SECURITY 1.0A — Supabase RLS / Auth / Admin Permission Audit

**Data:** 2026-06-10  
**Tipo:** Auditoria read-only (diagnóstico — **nenhuma alteração** em RLS, schema, policies ou banco)  
**Contexto:** Bug C — admin no EXE/Tauri reportou erro de policy/RLS ao cadastrar edital manual em `/cadastros`. FRONTEND 1.1F já trata o erro na UI; este patch explica a causa provável.

---

## 1. Objetivo

Descobrir por que o frontend pode mostrar usuário **admin** e ainda assim o Supabase bloquear `INSERT`/`UPDATE` em `public.edital`, sem aplicar correções.

---

## 2. Escopo read-only

| Permitido | Proibido |
|-----------|----------|
| Leitura de código e docs versionados | `CREATE/ALTER POLICY` |
| Análise de payload e RBAC local | Migrations / apply SQL |
| Queries SQL **documentadas** para execução manual | `INSERT`/`UPDATE`/`DELETE` reais |
| Referência a testes mock (FRONTEND 1.1F) | `service_role` no frontend |
| `npm test` / `npm run build` | Alterar `isAdminUser` ou payload |

---

## 3. O que foi analisado

### Frontend

- `src/services/supabaseClient.js`, `src/config/env.js`
- `src/services/dataService.js` (`createEdital`, `getAllEditaisAdmin`)
- `src/services/authService.js`, `src/contexts/AuthContext.jsx`
- `src/utils/permissions.js`, `src/permissions.js`, `src/hooks/usePermissions.js`
- `src/router/ProtectedRoute.jsx`, `src/router/index.jsx`
- `src/pages/Cadastros.jsx`, `src/components/admin/EditalForm.jsx`
- `src/utils/admin/buildEditalWritePayload.js`
- `src/utils/admin/adminPermissionDiagnostic.js`, `handleManualEditalSaveError.js`
- `docs/FRONTEND_1_1F_CADASTRO_POLICY_ERROR_HANDLING.md`

### Backend / schema / docs

- `backend/database/schema_current.sql`
- `backend/CORE/schema_rls_policies.sql`, `backend/CORE/schema_sql_completo.sql`
- `backend/docs/sql/RLS_CLIENTE.sql`, `SECURITY_RLS_EXAMPLES.sql`
- `backend/docs/sql/CREATE_EDITAL_FEEDBACK.sql`, `CREATE_APP_FEEDBACK.sql`
- `backend/docs/FRONTEND_BACKEND_CONTEXT.md`, `AUTH_SIGNUP_PROFILE_DIAGNOSTIC.md`
- `docs/PROJECT_TECHNICAL_MAP.md`

---

## 4. Como o frontend autentica

| Pergunta | Resposta |
|----------|----------|
| Cliente usa anon key? | **Sim** — `createClient(SUPABASE_URL, SUPABASE_ANON_KEY)` em `supabaseClient.js` |
| `service_role` no frontend? | **Não** — apenas comentários de proibição em `env.js`; nenhum uso em runtime |
| Login via Supabase Auth? | **Sim** — `authService.login` → `supabase.auth.signInWithPassword` |
| Flow OAuth | **`implicit`** (`flowType: 'implicit'`) — tokens no hash em web; callback trata `access_token`/`refresh_token` no hash |
| Tauri diferente? | **Sim** — `detectSessionInUrl: !IS_TAURI_BUILD` (Tauri não parseia URL automaticamente); sessão via `persistSession: true` + login explícito |
| Recuperação de usuário | `AuthContext` → `getCurrentSession()` → `fetchProfileByAuthUserId(auth.uid())` em `public.usuario` |
| Perfil / role | Tabela **`public.usuario`** (`tipo_usuario`, `nivel_acesso`, `auth_user_id`), **não** `user_metadata`/`app_metadata` do JWT para RBAC |
| Claims JWT no RBAC? | **Não** — admin é derivado da linha `usuario`, não de `auth.jwt()` no frontend |

Fluxo resumido:

```
signInWithPassword → JWT (role authenticated) + session localStorage
→ SELECT public.usuario WHERE auth_user_id = auth.uid()
→ buildAppUser → AuthContext.user (id_usuario, tipo, nivel)
```

---

## 5. Como o frontend identifica admin

| Verificação | Fonte no código | Resultado | Risco |
|-------------|-----------------|-----------|-------|
| `isAdminUser()` existe? | `src/utils/permissions.js` | Sim | — |
| Email hardcoded? | `isAdminUser` | **Não** | Baixo |
| `tipo_usuario`? | `Administrador` / `Admin` (case-insensitive) | Sim | Médio se RLS não usar mesma regra |
| Tabela `usuario`? | AuthContext carrega perfil; admin vem de `tipo_usuario` / `nivel_acesso` | Sim | Divergência se linha inativa ou sem `auth_user_id` |
| `user_metadata` / `app_metadata`? | Não usados para RBAC | Não | — |
| Claims JWT? | Não usados no frontend | Não | RLS no banco pode usar `auth.uid()` sem espelhar `tipo_usuario` |
| `getPermissions()` | `src/permissions.js` — ADMIN level 1 | Mapeia `tipo`/`nivel` → flags UI | UI only |
| Cadastros liberado por? | `ProtectedRoute requiredPermission="canViewCadastros"` | Consultor+ e Admin têm `canViewCadastros: true` | Rota ≠ permissão de INSERT no Postgres |
| Criar edital liberado por? | `permissions.canCreate` em `Cadastros.jsx` | Consultor e Admin (`canCreate: true`) | **INSERT Supabase é independente** |

**Divergência central:** RBAC é **100% client-side** após ler `public.usuario`. RLS no Postgres avalia **JWT + policies** — não lê o React.

---

## 6. Como ProtectedRoute libera páginas

Arquivo: `src/router/index.jsx`

| Rota | Guard |
|------|-------|
| `/cadastros` | `ProtectedRoute requiredPermission="canViewCadastros"` |
| `/editais`, `/dashboard`, etc. | `ProtectedRoute` (só `authenticated`) |

`ProtectedRoute.jsx`:

1. `loading` → spinner
2. `!authenticated` → redirect `/login`
3. Se `requiredPermission` → `getPermissions(user.nivel \|\| user.tipo)[requiredPermission]`; se false → `/dashboard`

**Não há** verificação Supabase/RLS na rota — apenas sessão app + mapa local de permissões.

---

## 7. Como o payload de cadastro é montado

Cadeia:

```
EditalForm.handleSubmit
  → buildEditalWritePayload(formData)
  → Cadastros.handleSave
  → dataService.createEdital(formData)
  → supabase.from('edital').insert([row])
```

`buildEditalWritePayload` (`EDITAL_ADMIN_WRITE_FIELDS`):

`titulo`, `descricao`, `objetivo`, `temas`, `publico_alvo`, `fonte_recurso`, `valor_maximo`, `data_publicacao`, `prazo_envio`, `situacao`, `pdf_url`, `link`, `orgao_responsavel`, `id_organizacao`, `estado`, `ativo`

Removidos explicitamente: `organizacao`, `organizacao_responsavel`, `id_edital`, `status` (mapeado para `ativo`).

---

## 8. Campos enviados e ausentes

### Enviados (quando preenchidos no form)

| Campo | Observação |
|-------|------------|
| `titulo`, `descricao`, `link` | Core do cadastro |
| `fonte_recurso` | Não confundir com `fonte` da view |
| `orgao_responsavel` | Textual; **não** `organizacao_responsavel` |
| `id_organizacao` | Omitido se vazio |
| `prazo_envio`, `data_publicacao` | Datas |
| `ativo` | De `status` Ativo/Inativo |
| `pdf_url`, `objetivo`, `temas`, etc. | Opcionais |

### Não enviados (relevantes para RLS)

| Campo | No schema `public.edital`? | No payload? |
|-------|---------------------------|-------------|
| `created_by` | **Não** (schema auditado 2026-06) | Não |
| `user_id` | **Não** | Não |
| `id_usuario` | **Não** em `edital` | Não |
| `owner_id` / `created_by_user_id` | **Não** | Não |
| `organizacao_responsavel` | **Não** (coluna inexistente) | Removido |
| `extras` | Sim (jsonb) | **Não** no formulário admin atual |

### Perguntas do patch

| # | Resposta |
|---|----------|
| Schema tem `created_by` / `user_id`? | **Não** em `schema_current.sql` (107 colunas de `edital`) |
| Payload satisfaz `created_by = auth.uid()`? | **N/A** — coluna ausente; policy desse tipo exigiria migration |
| `with_check` versionado para `edital` INSERT? | **Não encontrado** para `authenticated` |
| Ausência de `created_by` explica o erro? | **Parcialmente** — só se policy exigir coluna que não existe (apareceria como schema/validation, não sempre como “policy”) |
| Adicionar campo no frontend seria seguro? | **Somente após** confirmar coluna + policy no cluster; **não** neste patch |
| Precisa confirmar policy real? | **Sim — obrigatório** antes de SECURITY 1.0B |

---

## 9. Policies / RLS encontradas no repositório

### `public.edital`

| Fonte | SELECT anon | SELECT auth | INSERT auth | UPDATE auth | DELETE auth | Observação |
|-------|-------------|-------------|-------------|-------------|-------------|------------|
| `CORE/schema_rls_policies.sql` | — (comentado) | — | — | — | — | RLS ON; só `service_role_all_edital` |
| `CORE/schema_sql_completo.sql` | via `anon_all_edital` FOR ALL | — | via **anon** FOR ALL | via anon | via anon | **Legado/dev** — não documenta `authenticated` |
| Migrations `backend/migrations/*` | — | — | — | — | — | **Sem policies de edital** |
| `schema_consolidado_editalfinder.sql` | Exemplo comentado | — | — | — | — | Apenas documentação |

### `public.usuario`

| Fonte | Policies |
|-------|----------|
| `FIX_SIGNUP_PROFILE_CREATION.sql` | Exemplos comentados: `usuario_insert_own` (`auth.uid() = auth_user_id`) |
| `SECURITY_RLS_EXAMPLES.sql` | Exemplos conceituais SELECT/UPDATE own |

### `public.cliente`

| Fonte | INSERT authenticated |
|-------|---------------------|
| `RLS_CLIENTE.sql` | **Sim** — `current_app_user_is_admin()` OR `id_usuario = current_app_user_id()` |

Funções versionadas (usadas em RLS de cliente):

- `current_app_user_id()` — `usuario.auth_user_id = auth.uid()`, status Ativo
- `current_app_user_is_admin()` — `tipo_usuario IN ('Administrador','Admin')`, Ativo

**Não há** equivalente versionado `edital_insert_admin` no repo.

### `public.edital_feedback`

| Fonte | INSERT authenticated |
|-------|---------------------|
| `CREATE_EDITAL_FEEDBACK.sql` | `edital_feedback_insert_own` — exige `id_usuario` ligado a `auth.uid()` via `usuario` |

### Views

| View | Policies no repo |
|------|------------------|
| `vw_editais_front` | Herda RLS de `edital` (view sobre tabela base) |
| `vw_editais_admin` | `SELECT *` de `vw_editais_front` — **sem policies próprias versionadas** |

---

## 10. Lacunas (policies reais podem existir só no Supabase)

1. **Policies ativas de `public.edital` no cluster QA/prod** não estão integralmente versionadas — arquivos no repo divergem (`anon_all` vs `service_role_only`).
2. **INSERT/UPDATE/DELETE para role `authenticated` em `edital`** — não há migration canónica aplicável.
3. **Diferença staging vs EXE** — mesmo código; políticas e dados de `usuario` podem diferir por ambiente.
4. **`organizacao`** — referenciada no admin; tabela pode não existir no PostgREST cache (doc schema).
5. **Confirmação manual** via `pg_policies` no SQL Editor é **necessária** (queries na §15).

---

## 11. Hipóteses H1–H5

### H1 — Policy exige `created_by = auth.uid()` ou equivalente

| | |
|-|-|
| **A favor** | Padrão comum em apps multi-tenant |
| **Contra** | `schema_current.sql` **não** lista `created_by`/`user_id` em `edital` |
| **Risco** | Médio |
| **Classificação** | **Baixa** (sem coluna no schema versionado) |

### H2 — UI admin diverge do JWT/RLS

| | |
|-|-|
| **A favor** | Frontend usa `usuario.tipo_usuario`; RLS de `cliente` usa `current_app_user_is_admin()` — **mesmo critério**, mas **edital não tem policy equivalente versionada** |
| **Contra** | Se policy de edital existir no cluster e usar mesma função, admin deveria passar **se** `auth_user_id` e status Ativo corretos |
| **Risco** | Alto (divergência percebida pelo usuário) |
| **Classificação** | **Média–alta** |

### H3 — Tauri perde sessão/claim

| | |
|-|-|
| **A favor** | `detectSessionInUrl: false` no Tauri; fluxo de callback diferente |
| **Contra** | E2E e uso real: login, `/editais`, detalhe, Grants — **leitura autenticada funciona**; falha reportada é no **INSERT** |
| **Risco** | Médio para sessão; baixo como causa única |
| **Classificação** | **Baixa–média** |

### H4 — Payload inválido aparece como policy

| | |
|-|-|
| **A favor** | `link NOT NULL`, unique `edital_link_key`; campos removidos pelo sanitizer |
| **Contra** | Erros de constraint costumam ser `23502`/`23505` (classificados como validation/duplicate em 1.1F) |
| **Risco** | Médio |
| **Classificação** | **Média** (secundária) |

### H5 — Policy simplesmente não permite INSERT em `edital` para `authenticated`

| | |
|-|-|
| **A favor** | Repo versiona RLS ON + policies **service_role** (ou legado **anon**); loader backend usa service_role; **nenhuma** policy INSERT `authenticated` documentada; sintoma = “row-level security policy” no cadastro manual |
| **Contra** | SELECT em `edital` na tela admin pode funcionar com policy SELECT distinta |
| **Risco** | **Crítico** para feature cadastro manual |
| **Classificação** | **Alta** |

### Hipótese mais provável

**H5 (alta)** — o cluster provavelmente **não concede INSERT** em `public.edital` ao role `authenticated` (JWT do usuário logado), enquanto o pipeline/backend usa `service_role`.

**H2 (média–alta)** — reforço: mesmo sendo admin na UI, **não há ponte versionada** entre `isAdminUser()` e uma policy `edital_insert_admin` no Postgres.

**H1 (baixa)** — improvável como causa primária dado schema sem coluna de dono.

---

## 12. Correções possíveis (NÃO aplicadas neste patch)

| Opção | Descrição | Pré-requisito |
|-------|-----------|---------------|
| **SECURITY 1.0B** | Policy `INSERT`/`UPDATE` em `edital` para `authenticated` + `current_app_user_is_admin()` | Confirmar `pg_policies` no cluster |
| **Coluna de auditoria** | `created_by uuid` ou `id_usuario_criador bigint` + policy | Migration + alinhar payload |
| **RPC SECURITY DEFINER** | `insert_edital_admin(payload)` validando admin | Revisão DBA; não expor service_role |
| **Edge Function** | Escrita server-side com validação | Backend; fora do escopo frontend |
| **Frontend only** | Adicionar `created_by` sem policy | **Inseguro / inútil** — rejeitado |

---

## 13. Cobertura de testes mock (FRONTEND 1.1F)

Sem insert real no Supabase. Testes existentes:

| Arquivo | Cobertura |
|---------|-----------|
| `manualEditalPolicy.test.js` | RLS mock → rascunho, mensagem admin, metadata sem secrets |
| `supabaseErrorClassifier.test.js` | Classificação `rls_policy`, redação de tokens |
| `buildEditalWritePayload.test.js` | Sanitização payload |

**Não é necessário** duplicar testes neste patch.

---

## 14. Queries SQL recomendadas (execução manual no Supabase SQL Editor)

```sql
-- Policies ativas
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

```sql
-- Colunas relevantes
SELECT table_schema, table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('edital', 'usuario', 'usuarios', 'profiles', 'edital_feedback')
ORDER BY table_name, ordinal_position;
```

```sql
-- RLS ligado?
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('edital', 'usuario', 'usuarios', 'profiles', 'edital_feedback')
ORDER BY tablename;
```

```sql
-- Funções helper (se existirem)
SELECT proname, prosecdef
FROM pg_proc
WHERE proname IN ('current_app_user_id', 'current_app_user_is_admin')
  AND pronamespace = 'public'::regnamespace;
```

```sql
-- Perfil do usuário afetado (substituir e-mail; não colar em logs públicos)
SELECT id_usuario, auth_user_id, tipo_usuario, nivel_acesso, status, nome_email
FROM public.usuario
WHERE nome_email = '<email-do-reporter>'
LIMIT 1;
```

**Não** incluir tokens, anon key ou dados sensíveis em tickets.

---

## 15. Próximo patch recomendado

**SECURITY 1.0B — RLS Edital Write Policy Alignment**

1. Executar queries §14 no cluster QA (mesmo projeto do EXE).
2. Comparar com `RLS_CLIENTE.sql` (padrão `current_app_user_is_admin()`).
3. Se confirmado H5: criar migration `edital_insert_update_admin` (e opcionalmente consultor) **apenas após** revisão DBA.
4. Atualizar `buildEditalWritePayload` **somente** se policy exigir colunas novas confirmadas.
5. Teste E2E opcional: cadastro manual em staging com usuário QA admin (fora deste patch de auditoria).

---

## 16. Validação deste patch

| Check | Resultado |
|-------|-----------|
| RLS/schema alterados? | **Não** |
| Secrets logados? | **Não** |
| `npm test` | **239/239 pass** |
| `npm run build` | **OK** |
| E2E | Verde na execução QA 10/06/2026 21:04 (10 pass) — cadastro manual não coberto por E2E |

---

## Referências

- `docs/FRONTEND_1_1F_CADASTRO_POLICY_ERROR_HANDLING.md`
- `backend/docs/sql/RLS_CLIENTE.sql`
- `backend/CORE/schema_rls_policies.sql`
- `qa/artifacts/qa_results.json` (E2E 10 passed, 2026-06-10)
