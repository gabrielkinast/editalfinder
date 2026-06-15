# QA Automation Guide — EditalFinder

Guia prático para rodar e estender a automação de QA.

- Diagnóstico inicial: `DESKTOP_QA_1_0_INTENSIVE_EXE_SMOKE_TEST.md`
- Harness E2E (QA 1.1): `QA_1_1_PLAYWRIGHT_HARNESS_FIX.md`
- Dados autenticados (QA 1.1B): `QA_1_1B_AUTHENTICATED_DATA_DISCOVERY.md`
- Suíte expandida (QA 1.2): `QA_1_2_EXPANDED_E2E_REGRESSION_SUITE.md`
- Scripts padronizados (QA 1.3A): `QA_1_3A_STANDARDIZED_QA_SCRIPTS.md`
- Skips E2E (QA 1.3C): `QA_1_3C_REDUCE_E2E_SKIPS.md`
- CI GitHub Actions (QA 1.3B): `QA_1_3B_GITHUB_ACTIONS_CI.md`
- Auditoria de dependências (SECURITY 1.1): `SECURITY_1_1_FRONTEND_DEPENDENCY_AUDIT.md`
- Substituição export XLSX (SECURITY 1.2): `SECURITY_1_2_REPLACE_XLSX_EXPORT_DEPENDENCY.md`

## Camadas e comandos

```bash
# A) Unit/integration (obrigatório, parte do release)
npm test

# B) Web E2E (Playwright — QA 1.1)
npx playwright install chromium   # 1x por máquina
npm run e2e                       # build + preview + testes (webServer automático)
npm run e2e:report                # abre HTML em qa/artifacts/playwright/html

# Com credenciais QA (não commitar):
# E2E_USER_EMAIL=... E2E_USER_PASSWORD=... npm run e2e

# Escrita real em Cadastros (opt-in — cria registro no DB):
# E2E_ALLOW_WRITE_TESTS=1 E2E_USER_EMAIL=... E2E_USER_PASSWORD=... npm run e2e

# C) QA local completo (QA 1.3A) — unit + build + e2e + qa_results.json + qa_summary_latest.md
npm run qa:local
npm run qa:results   # regenera só qa_results.json (requer logs/state)
npm run qa:summary   # regenera só qa_summary_latest.md

# D) Windows desktop smoke (pywinauto, opt-in)
python -m venv .venv-qa
.\.venv-qa\Scripts\Activate.ps1
pip install -r qa/requirements.txt
python qa/windows_desktop_smoke.py --exe "src-tauri/target/release/editalfinder.exe"
```

## CI GitHub Actions (QA 1.3B)

Workflow: `.github/workflows/qa.yml` (raiz do repositório `edital`).

| Trigger | Branches |
|---------|----------|
| `push` / `pull_request` | `main`, `master` |
| `workflow_dispatch` | manual |

O job `qa-frontend` roda `npm run qa:local` em `frontend/EditalFinder-React` com secrets:

- `E2E_USER_EMAIL`, `E2E_USER_PASSWORD`
- `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`

**Não** configurar `E2E_ALLOW_WRITE_TESTS` no CI normal (read-only).

Artefatos: `editalfinder-qa-artifacts` (14 dias). Resumo na aba **Summary** do job.

Detalhes: `docs/QA_1_3B_GITHUB_ACTIONS_CI.md`.

## Auditoria de dependências (SECURITY 1.1)

Após mudanças em `package-lock.json`, rodar:

```bash
npm audit
npm audit --omit=dev
```

Correção segura: `npm audit fix` (sem `--force`). Export XLSX usa **exceljs** (SECURITY 1.2) — `xlsx` removido; ver `docs/SECURITY_1_2_REPLACE_XLSX_EXPORT_DEPENDENCY.md`.

## Camadas E2E (Playwright)

| Camada | Projeto | Requisito |
| ------ | ------- | --------- |
| 1 Public | `public` | Nenhum — login/redirect/basename |
| 2 Auth | `authenticated` | `E2E_USER_EMAIL` + `E2E_USER_PASSWORD` |
| 3 Data | `authenticated` | Auth + `VITE_SUPABASE_*` no build + catálogo > 0 |
| 4 Write opt-in | `authenticated` | + `E2E_ALLOW_WRITE_TESTS=1` (só `cadastros-smoke`) |

Helpers: `tests/e2e/_helpers.js` + `tests/e2e/_catalog.js` (`waitForEditaisCatalog`, `requireCatalogReady`, `saveSkipEvidence`, `saveE2EEvidence`, `skipWithEvidence`).

Evidência de skip: `qa/artifacts/playwright/debug-authenticated-data/` (catálogo/Grants) e `qa/artifacts/playwright/debug-e2e/` (QA 1.2).

**Basename:** use `appPath('/editais')` — nunca `page.goto('/editais')` absoluto.

## data-testid estáveis (contrato de teste)

Adicionados sem alterar o visual:

| testid | onde |
| ------ | ---- |
| `dashboard-page` | wrapper do Dashboard |
| `dashboard-refresh-button` | botão "Atualizar dados" |
| `editais-page` | wrapper da tela de Editais |
| `editais-stats-bar` | barra "Mostrando X de Y recebidos" |
| `relax-filters-button` | botão "Relaxar filtros" |
| `edital-card` (+ `data-edital-id`, `data-source`) | card de edital |
| `edital-open-detail` | botão "Detalhes" do card |
| `report-problem-button` | botão geral de reporte |
| `login-page` | tela de login |
| `editais-loading` | skeleton de carga da lista |
| `data-fonte` | atributo no card (fonte_recurso para QA) |
| `login-submit` | botão Entrar |
| `report-problem-modal` | modal de reporte do app |
| `app-feedback-runtime-badge` | "Ambiente detectado" no modal |
| `app-feedback-guidance` | orientação print/detalhes no modal |
| `edital-feedback-guidance` | orientação no reporte de edital |
| `editais-search-input` | busca global no Header (Editais) |
| `editais-export-pdf` / `editais-export-xlsx` | botões de exportação |
| `semantic-status-*` | checkboxes filtro status (1.2B) |
| `radar-page` / `radar-placeholder` / `radar-card` | Radar |
| `cadastros-page` / `cadastro-novo-edital` | Cadastros admin |
| `edital-form-titulo` / `edital-form-link` / `edital-form-submit` | formulário manual |
| `app-feedback-submit` | botão Gmail no report geral |
| `report-problem-close` | fechar modal report (×, Cancelar, Fechar) |

> Regra: `data-testid`/`data-*` são permitidos por não alterarem comportamento visual.

## Matriz de fluxos

Editar `src/utils/qa/smokeFlows.js` (fonte única consumida por specs e docs).

## Instrumentação dev (gated, sem segredos)

| Flag (localStorage) | Env (Vite) | Efeito |
| ------------------- | ---------- | ------ |
| `EDITALFINDER_DEBUG_EXTERNAL_LINKS` | `VITE_DEBUG_EXTERNAL_LINKS` | loga URL externa escolhida por botão |
| `EDITALFINDER_DEBUG_ROUTES` | `VITE_DEBUG_ROUTES` | loga rota atual |
| `EDITALFINDER_DEBUG_DATA_COUNTS` | `VITE_DEBUG_DATA_COUNTS` | loga contagens raw/catalog/filtered |

Utilitários: `src/utils/qa/externalLinkDebug.js`, `src/utils/qa/routeDebug.js`,
`src/utils/debugDataCounts.js`.

## Helpers de URL oficial

`src/utils/edital/officialEditalUrl.js`:

- `getOfficialEditalUrl(item)` → melhor URL (canônica para Grants.gov, nunca page-not-found);
- `resolveOfficialEditalUrlInfo(item)` → `{ url, fieldUsed, canonicalized, source }`.

## Convenções

- Não usar `service_role` no frontend; E2E roda só com `anon` key.
- Não deletar registros; testes são read-only por padrão.
- Escrita em Cadastros só com `E2E_ALLOW_WRITE_TESTS=1`.
- Sem OCR; preferir `data-testid` e UIA.
- Camada A deve permanecer verde no `npm test` (gate do `desktop:release`).
