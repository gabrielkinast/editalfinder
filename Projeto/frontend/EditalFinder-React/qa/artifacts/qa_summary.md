# QA Summary — EditalFinder

Atualizado: 2026-06-10

## SECURITY 1.0B + FRONTEND 1.1I — Cadastro manual admin (staging)

| Verificação | Resultado |
| ----------- | --------- |
| Policy `edital_admin_insert` | Aplicada |
| Policy `edital_admin_update` | Aplicada |
| Hotfix `edital_admin_select` | Aplicada manualmente no Supabase |
| Cadastro admin | **OK** — edital ID **2448** |
| Listagem Cadastros → Editais | **OK** — item visível |
| Fonte exibida | `Cadastro Manual` |
| Unit tests | 256/256 pass (pós-1.1I) |

Migration versionada atualizada: `backend/migrations/20260610_security_1_0b_edital_admin_write_policy.sql` (inclui SELECT).

## BACKEND 10.3B — Grants.gov duplicate resolution (staging)

| Verificação | Resultado |
| ----------- | --------- |
| Dry-run duplicate_targets | 97 candidatos, 0 inválidos |
| Apply controlado | **97 ocultados** (`extras.curadoria_front.hidden_duplicate`) |
| Deleções | **0** |
| Canônicos preservados | **97** visíveis |
| Testes `test_grants_duplicate_resolution.py` | **23 passed** |

## BACKEND 10.3C — Grants duplicate visibility backfill

| Verificação | Resultado |
| ----------- | --------- |
| Apply controlado | **ok=96**, already_ok=1, errors=0 |
| Auditoria pós-apply | hidden=97, visible=181, issues=0, visibility_compliant=97 |
| Testes `test_grants_duplicate_visibility_backfill.py` | **11 passed** |

## FRONTEND 10.3C — Defensive hidden duplicate filter

| Verificação | Resultado |
| ----------- | --------- |
| `isCuradoriaHidden` — `visibility` + `hidden_duplicate` | Implementado |
| Filtro em `getEditais` + `filterCatalog` | Implementado |
| Testes `editalVisibility.test.js` | **13 passed** |
| `npm test` (suite completa) | **269/269 passed** |
| `npm run build` | **OK** |
| `npm run e2e` (sem credenciais QA) | **5 passed**, **4 skipped** (auth) |
| E2E autenticado (staging, credenciais QA) | **10 passed** (referência pós-backend 10.3C) |

## FRONTEND 1.2B — Status filters + export status column

| Verificação | Resultado |
| ----------- | --------- |
| Filtro sidebar "Filtrar por status" (OR) | Implementado |
| Passo `semanticStatus` em `filterCatalog` | Implementado |
| PDF coluna Status | Implementado |
| XLSX colunas Status + Status Detalhado | Implementado |
| Testes unitários 1.2B | **283/283 passed** (suite completa) |
| `npm run build` | **OK** |
| `npm run e2e` (sem credenciais QA) | **5 passed**, **5 skipped** (auth) |
| E2E `editais-status-filter.spec.js` | Registrado; requer credenciais QA |

## QA 1.2 — Expanded Playwright E2E regression suite

| Verificação | Resultado |
| ----------- | --------- |
| Novos specs | `editais-filters`, `editais-export`, `dashboard-smoke`, `radar-smoke`, `cadastros-smoke`, `external-links` |
| `report-problem` expandido | 2 testes |
| Helpers QA 1.2 | `saveE2EEvidence`, `skipWithEvidence`, `safeDownloadClick`, etc. |
| Escrita opt-in | `E2E_ALLOW_WRITE_TESTS=1` |
| `npm test` | **283/283 passed** |
| `npm run e2e` sem credenciais | **5 passed**, **13 skipped** (auth) |
| `npm run e2e` com credenciais QA | Referência pré-1.2: **10 passed**; pós-1.2: rodar localmente |

---

## QA 1.1C — Grants.gov E2E Targeting

Última execução E2E: 2026-06-10 21:04

## Execução final E2E (com credenciais QA)

| Métrica | Valor |
| ------- | ----- |
| Data/hora | 10/06/2026 21:04 |
| Duração total | 1.0 min |
| Passed | **10** |
| Failed | **0** |
| Skipped | **0** |

## Resultado por camada

| Camada | Ferramenta | Status | Resultado |
| ------ | ---------- | ------ | --------- |
| A — Unit | `node --test` | Executado | 239/239 pass |
| B — Build | `npm run build` | Executado | OK |
| B1 — E2E Public | Playwright `public` | Executado | 5/5 pass |
| B2 — E2E Auth setup | `auth.setup.js` | Executado | 1/1 pass |
| B2 — Auth smoke | `authenticated-smoke.spec.js` | Executado | pass — `/editais` autenticado |
| B3 — Editais detail | `editais-detail.spec.js` | Executado | pass — primeiros 10 editais |
| B3 — Grants links | `grants-links.spec.js` | Executado | **pass** — links externos sem `page-not-found` |
| B2 — Report problem | `report-problem.spec.js` | Executado | pass — modal de reporte |

## Testes validados nesta execução

1. `auth.setup.js` — authenticate for E2E
2. `smoke.spec.js` — 5 testes públicos
3. `authenticated-smoke.spec.js` — `/editais` autenticado
4. `editais-detail.spec.js` — primeiros 10 editais
5. `grants-links.spec.js` — links externos sem page-not-found
6. `report-problem.spec.js` — modal de reporte

## Contexto QA 1.1C (grants-links)

Correção aplicada antes desta execução: targeting determinístico Grants.gov, hooks `window.open`/`location.assign` antes do goto, skip rápido com evidência quando não há cards Grants (execução atual encontrou Grants e **passou**).

## Evidência (se skip/falha em execuções futuras)

| Situação | Arquivos |
| -------- | -------- |
| Skip (sem Grants visível) | `debug-authenticated-data/grants-links-skip.{json,txt,png}` |
| Falha URL quebrada | `debug-authenticated-data/grants-links-failure.{json,txt,png}` |
| Reporte HTML | `qa/artifacts/playwright/html/` |

## Como reproduzir

```powershell
$env:E2E_USER_EMAIL="..."
$env:E2E_USER_PASSWORD="..."
npm run e2e
Remove-Item Env:E2E_USER_EMAIL
Remove-Item Env:E2E_USER_PASSWORD
```

Não commitar credenciais.

## QA 1.3C — Reduce avoidable E2E skips (2026-06-10)

| Verificação | Resultado |
| ----------- | --------- |
| Diagnóstico 4 skips | Cadastros: aba errada; Filtros: collapse fechado; Escrita: opt-in esperado |
| Skips removidos | 3 (modal sem salvar, editais-filters, editais-status-filter) |
| Skip legítimo | `cria edital manual` — `SKIP_WRITE_OPT_IN_DISABLED` |
| `npm run qa:local` + credenciais | **18 passed / 1 skipped / 0 failed** |
| Doc | `docs/QA_1_3C_REDUCE_E2E_SKIPS.md` |

## QA 1.3B — GitHub Actions CI (2026-06-10)

| Verificação | Resultado |
| ----------- | --------- |
| Workflow | `.github/workflows/qa.yml` — job `qa-frontend` |
| Pipeline | `npm run qa:local` (unit + build + e2e) |
| Secrets | `E2E_USER_*`, `VITE_SUPABASE_*` via GitHub Secrets |
| Escrita | **Bloqueada** — sem `E2E_ALLOW_WRITE_TESTS` |
| Artefatos | `editalfinder-qa-artifacts` + step summary |
| Doc | `docs/QA_1_3B_GITHUB_ACTIONS_CI.md` |

## SECURITY 1.1 — Frontend dependency audit (2026-06-10)

| Verificação | Resultado |
| ----------- | --------- |
| Antes | 9 vulnerabilities (4 moderate, 5 high) |
| Correção | `npm audit fix` (sem `--force`) |
| Depois | **1 high** — `xlsx` sem fix no npm |
| QA pós-fix | 290 unit · build OK · E2E 18/1 com credenciais |
| Doc | `docs/SECURITY_1_1_FRONTEND_DEPENDENCY_AUDIT.md` |
| Artefatos | `qa/artifacts/npm_audit_before.json`, `npm_audit_after.json` |

## SECURITY 1.2 — Replace xlsx export (2026-06-10)

| Verificação | Resultado |
| ----------- | --------- |
| Removido | `xlsx` (package.json + lock) |
| Substituído por | `exceljs@^4.4.0` + override `uuid@^11.1.0` |
| Módulo | `src/utils/export/spreadsheetExport.js` |
| `npm audit` | **0 vulnerabilities** |
| QA | 301 unit · E2E 18/1 com credenciais |
| Doc | `docs/SECURITY_1_2_REPLACE_XLSX_EXPORT_DEPENDENCY.md` |

## Última execução automática

Atualizado: 2026-06-15T15:40:23.171Z

| Camada | Status | Detalhe |
| --- | --- | --- |
| Unit | passed | 301 passed |
| Build | passed | 5.7s |
| E2E | passed | 18 passed, 1 skipped |

Ver detalhes: `qa/artifacts/qa_summary_latest.md`

