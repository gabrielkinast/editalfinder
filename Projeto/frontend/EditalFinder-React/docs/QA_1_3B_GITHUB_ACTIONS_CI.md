# QA 1.3B — GitHub Actions CI with Secrets + QA Artifacts

**Data:** 2026-06-10

---

## 1. Objetivo

Executar automaticamente o pipeline QA local (QA 1.3A) no GitHub Actions e publicar artefatos para revisão.

**Escopo:** read-only — unit, build, E2E público + autenticado (sem escrita no banco).

---

## 2. Workflow

| Item | Valor |
|------|-------|
| Arquivo | `.github/workflows/qa.yml` |
| Nome | `QA` |
| Job | `qa-frontend` |
| Runner | `ubuntu-latest` |
| Working directory | `frontend/EditalFinder-React` |
| Node | **22** (LTS; sem `engines` no `package.json`) |

### Triggers

- `push` → branches `main`, `master`
- `pull_request` → branches `main`, `master`
- `workflow_dispatch` (execução manual)

### Passos

1. `actions/checkout@v4`
2. `actions/setup-node@v4` (Node 22, cache npm)
3. `npm ci`
4. `npx playwright install --with-deps chromium`
5. `npm run qa:local` (unit → build → e2e → `qa_results.json` + `qa_summary_latest.md`)
6. Publicar `qa_summary_latest.md` em `$GITHUB_STEP_SUMMARY`
7. Upload artefatos (`if: always()`)

---

## 3. Secrets do repositório

Configurar em **Settings → Secrets and variables → Actions**:

| Secret | Obrigatório | Uso |
|--------|-------------|-----|
| `E2E_USER_EMAIL` | Recomendado | Login E2E autenticado |
| `E2E_USER_PASSWORD` | Recomendado | Login E2E autenticado |
| `VITE_SUPABASE_URL` | Recomendado | Build Vite + dados reais E2E |
| `VITE_SUPABASE_ANON_KEY` | Recomendado | Build Vite + dados reais E2E |

### Não configurar no CI normal

| Variável | Motivo |
|----------|--------|
| `E2E_ALLOW_WRITE_TESTS` | Escrita real em Cadastros — cria registro no DB |
| `SUPABASE_SERVICE_ROLE_KEY` / `SERVICE_ROLE` | Proibido no frontend/E2E |
| Qualquer `.env` commitado | Secrets só via GitHub Secrets |

### Sem secrets

O job **ainda roda** e deve passar se unit/build/E2E público passarem. Specs autenticados fazem skip (`SKIP_NO_AUTH`). `qa_results.json` terá `environment.authConfigured: false`.

### Com secrets (meta esperada)

| Camada | Resultado típico |
|--------|------------------|
| Unit | 290 passed |
| Build | passed |
| E2E | **18 passed / 1 skipped** (único skip = escrita opt-in Cadastros) |

---

## 4. Artefatos publicados

Nome: `editalfinder-qa-artifacts` (retenção 14 dias)

| Caminho | Conteúdo |
|---------|----------|
| `qa/artifacts/qa_results.json` | JSON consolidado |
| `qa/artifacts/qa_summary_latest.md` | Resumo legível |
| `qa/artifacts/qa_run_state.json` | Exit codes e durações |
| `qa/artifacts/logs/` | `unit.log`, `build.log`, `e2e.log`, `qa-local.log` (sanitizados) |
| `qa/artifacts/playwright/results.json` | Resultado Playwright |
| `qa/artifacts/playwright/html/` | Relatório HTML |
| `qa/artifacts/playwright/test-results/` | Trace/vídeo/screenshot **somente em falha** |

**Não publicados:** `.env`, `.env.local`, `playwright/.auth/user.json` (sessão).

---

## 5. Segurança

1. Secrets injetados via `${{ secrets.* }}` — nunca hardcoded.
2. `qa/run-local-qa.mjs` + `sanitizeLogText()` mascaram senha, JWT, anon key nos logs.
3. Playwright: `trace`/`video` = `retain-on-failure` apenas; inputs `type="password"` são mascarados nos traces por padrão.
4. CI não define `E2E_ALLOW_WRITE_TESTS`.
5. Sem `service_role`, sem alteração backend/RLS/schema.

---

## 6. Como rodar manualmente

1. GitHub → **Actions** → workflow **QA**
2. **Run workflow** → escolher branch → **Run workflow**

Ou push/PR para `main`/`master`.

---

## 7. Interpretar skips no CI

| Situação | Comportamento |
|----------|---------------|
| Sem `E2E_USER_*` | 13 specs autenticados skipped; job passa se público OK |
| Com credenciais | 18 passed / 1 skipped (escrita opt-in) |
| Sem catálogo | Skip com evidência em `debug-e2e/` |
| `SKIP_WRITE_OPT_IN_DISABLED` | Esperado — escrita não habilitada |

Skips **não falham** o job (`exit 0` do Playwright).

---

## 8. Interpretar falhas

| Falha | Onde olhar |
|-------|------------|
| Unit | `logs/unit.log` no artefato |
| Build | `logs/build.log` |
| E2E | `logs/e2e.log`, `playwright/html/`, `test-results/` (trace em falha) |
| Resumo rápido | Aba **Summary** do job (`qa_summary_latest.md`) |

---

## 9. Limitações

- Build roda duas vezes (`qa:local` + `webServer` do Playwright) — aceitável.
- Node local pode ser 24; CI usa 22 LTS (sem `engines` fixo no projeto).
- Escrita opt-in requer workflow manual separado (futuro).

---

## 10. Próximo patch opcional

**QA 1.3D** (ou manual workflow) — `workflow_dispatch` com `E2E_ALLOW_WRITE_TESTS=1` em ambiente descartável + cleanup documentado.

## Referências

- `docs/QA_1_3A_STANDARDIZED_QA_SCRIPTS.md`
- `docs/QA_1_3C_REDUCE_E2E_SKIPS.md`
- `docs/QA_AUTOMATION_GUIDE.md`
