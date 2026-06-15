# FRONTEND 1.1F — Cadastro Edital Policy Error Handling + Admin Diagnostic

## Reporte real (Bug C)

| Campo | Valor |
|-------|-------|
| Página | `/cadastros` — cadastro manual de edital |
| Ambiente | Desktop/EXE Tauri |
| Usuário | Admin/colega do projeto |
| Sintoma | Erro ao cadastrar edital; mensagem de policy Supabase (RLS) |
| Impacto | `alert()` genérico; risco de percepção de perda de dados; sem diagnóstico admin vs banco |

## Causa provável

1. `dataService.createEdital` faz `insert` direto na tabela `edital` sem `created_by` / `id_usuario`.
2. O frontend usa RBAC local (`permissions.js`, `isAdminUser`) — perfil admin na UI pode não coincidir com o que a policy RLS/JWT do Supabase permite.
3. Divergência entre “admin na interface” e “usuário autorizado no banco”.

**Limitação deste patch:** não altera RLS, schema, backend, migrations nem usa `service_role`. Apenas melhora resiliência, rascunho local, diagnóstico e reporte.

## Comportamento antes / depois

| Antes | Depois |
|-------|--------|
| `alert('Erro ao salvar: ' + error.message)` | Painel na tela (`EditalSaveErrorPanel`) |
| Modal podia fechar ou confundir o usuário | Modal permanece aberto; formulário preservado |
| Sem rascunho | Rascunho em `localStorage` (`pending_manual_editais:v1`) |
| Reporte genérico | Metadata estruturada (`manual_edital_create`) |
| Admin via mesmo texto que demais perfis | Mensagem específica de divergência admin/RLS |

## Classificação de erro Supabase

Arquivo: `src/utils/supabase/supabaseErrorClassifier.js`

| Kind | Gatilhos |
|------|----------|
| `rls_policy` | Mensagens RLS, `policy`, violação de segurança |
| `permission_denied` | 401/403, `permission denied`, `insufficient privileges` |
| `schema` | PGRST204/205, coluna/tabela não encontrada |
| `duplicate` | 23505, unique constraint |
| `network` | fetch failed, offline, CORS |
| `validation` | not-null, check constraint, payload inválido |
| `unknown` | Demais casos |

`getSupabaseSafeErrorDetails` expõe apenas `message`, `code`, `details`, `hint`, `status` — nunca tokens/keys.

## Diagnóstico admin vs RLS

Arquivo: `src/utils/admin/adminPermissionDiagnostic.js`

Quando `frontendIsAdmin === true` e erro é `rls_policy` ou `permission_denied`:

- **Título:** Permissão de administrador não reconhecida pelo banco
- **Texto:** Explica bloqueio pelo Supabase e que dados foram preservados/rascunho local

Caso contrário:

- **Título:** Não foi possível cadastrar este edital
- **Texto:** Bloqueio por regra de permissão; dados preservados

Registra campos seguros: `isAuthenticated`, `hasUserId`, `frontendRole`, `supabaseErrorKind`, `runtime`, `localDraftId`, e nota que `created_by`/`id_usuario` podem estar ausentes no payload (apenas diagnóstico).

## Rascunho local

Arquivo: `src/utils/admin/pendingManualEditalDrafts.js`

Chave: `editalfinder:pending_manual_editais:v1`

Salvo automaticamente em falhas: `rls_policy`, `permission_denied`, `network`, `schema`.

Estrutura: `localId`, `createdAt`, `payload` (sanitizado), `context` (rota, operação, erro, runtime, flags admin/auth).

Máximo 20 rascunhos; sem tokens/secrets.

## Reporte melhorado

`EditalSaveErrorPanel` usa `AppReportProblemButton` com metadata:

```json
{
  "origem": "manual_edital_create",
  "componente": "Cadastros",
  "acao": "submit",
  "operation": "insert",
  "table": "edital",
  "errorKind": "rls_policy",
  "supabaseCode": "...",
  "supabaseStatus": 403,
  "frontendIsAdmin": true,
  "localDraftId": "draft_..."
}
```

Orientação no e-mail (via `appFeedbackGuidance`):

- **Desktop/EXE:** anexar print da tela
- **Web:** descrever com máximo de detalhes

## Fluxo no formulário

1. Submit → `createEdital` / `updateEdital`
2. Sucesso → fecha modal, recarrega lista (inalterado)
3. Erro (editais) → `processManualEditalSaveError` → painel + rascunho; **não** fecha modal
4. Ações: Tentar novamente (dispensa painel), Copiar dados, Reportar problema, detalhe técnico recolhível

## Arquivos principais

| Arquivo | Papel |
|---------|-------|
| `supabaseErrorClassifier.js` | Classificação e mensagens amigáveis |
| `pendingManualEditalDrafts.js` | Fila local de rascunhos |
| `adminPermissionDiagnostic.js` | Diagnóstico admin + `reportMetadata` |
| `handleManualEditalSaveError.js` | Orquestração no catch |
| `EditalSaveErrorPanel.jsx` | UI de erro |
| `Cadastros.jsx` | Integração no `handleSave` |
| `EditalForm.jsx` | Painel acima do form |

## Como testar

```bash
cd frontend/EditalFinder-React
npm test
npm run build
npm run e2e
```

Testes unitários novos:

- `src/utils/supabase/supabaseErrorClassifier.test.js`
- `src/utils/admin/manualEditalPolicy.test.js`

Teste manual (reproduzir Bug C):

1. Login como admin no EXE ou web
2. `/cadastros` → Novo edital → preencher → Salvar
3. Se RLS bloquear: verificar painel admin, formulário preenchido, rascunho em DevTools → Application → localStorage
4. Reportar problema e conferir metadata no mailto (sem tokens)

## Próximo patch recomendado

**SECURITY 1.0A** — alinhar RLS/policies Supabase com perfis reais (possível inclusão de `created_by` / claims JWT), sem contornar permissões no frontend.
