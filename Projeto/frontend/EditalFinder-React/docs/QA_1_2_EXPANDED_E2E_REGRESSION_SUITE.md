# QA 1.2 — Expanded Playwright E2E Regression Suite

**Data:** 2026-06-10  
**Base:** QA 1.1 harness + FRONTEND 1.2B (filtros/export status).

---

## 1. Objetivo

Expandir a suíte E2E para cobrir fluxos principais do EditalFinder (Editais, Dashboard, Radar, Cadastros, exportações, links externos, report problem) sem depender de dados raros nem de timeouts longos.

## 2. Specs adicionados / expandidos

| Arquivo | Camada | Cobertura |
|---------|--------|-----------|
| `editais-filters.spec.js` | 2/3 | Busca por título do card + filtro status |
| `editais-export.spec.js` | 2 | Download XLSX + PDF |
| `dashboard-smoke.spec.js` | 2 | KPIs + navegação para Editais |
| `radar-smoke.spec.js` | 2 | Render + placeholder/cards |
| `cadastros-smoke.spec.js` | 2 / escrita | Modal sem salvar; criação opt-in |
| `external-links.spec.js` | 2/3 | URLs externas genéricas (não só Grants) |
| `report-problem.spec.js` | 2 | Expandido: Gmail/fallback |
| *(existentes)* | 1–3 | `smoke`, `authenticated-smoke`, `editais-detail`, `grants-links`, `editais-status-filter` |

## 3. Camadas

| Camada | Projeto | Requisito |
|--------|---------|-----------|
| Público | `public` | Nenhum |
| Autenticado | `authenticated` | `E2E_USER_EMAIL` + `E2E_USER_PASSWORD` (ou skip) |
| Dados | `authenticated` | Auth + Supabase no build + catálogo > 0 |
| Escrita opt-in | `authenticated` | + `E2E_ALLOW_WRITE_TESTS=1` |

## 4. Como rodar sem credenciais

```bash
npm test
npm run build
npm run e2e
```

Specs autenticados fazem `test.skip` com mensagem clara (`SKIP_NO_AUTH`).

## 5. Como rodar com credenciais

```powershell
$env:E2E_USER_EMAIL="..."
$env:E2E_USER_PASSWORD="..."
npm run e2e
Remove-Item Env:E2E_USER_EMAIL
Remove-Item Env:E2E_USER_PASSWORD
```

## 6. Escrita real (Cadastros)

```powershell
$env:E2E_ALLOW_WRITE_TESTS="1"
# + credenciais acima
npm run e2e
```

Sem a flag, o teste `cria edital manual` é **sempre skipped**. Nenhum teste deleta dados.

## 7. Artefatos

| Pasta | Conteúdo |
|-------|----------|
| `qa/artifacts/playwright/html` | Relatório HTML |
| `qa/artifacts/playwright/results.json` | JSON Playwright |
| `qa/artifacts/playwright/test-results` | trace/video/screenshot em falha |
| `qa/artifacts/playwright/debug-authenticated-data/` | Skips de catálogo/Grants (QA 1.1) |
| `qa/artifacts/playwright/debug-e2e/` | Skips gerais QA 1.2 |

## 8. Como interpretar skips

- `E2E_USER_* não configurados` — esperado em CI/local sem credenciais.
- `no_visible_cards` / `catalog_received_zero` — ambiente sem dados ou filtros agressivos.
- `download_timeout_or_blocked` — headless sem suporte a download; evidência salva.
- `cadastro_without_permission` — usuário sem `canCreate` (QA 1.3C).
- `cadastro_novo_edital_not_visible` — aba Editais não ativa ou botão ausente (evidência em `debug-e2e/`).
- `status_filters_not_visible` — collapse **Filtrar por status** não expandiu (QA 1.3C: usar `openStatusFilterSection`).
- `SKIP_WRITE_OPT_IN_DISABLED` — teste de escrita ignorado sem `E2E_ALLOW_WRITE_TESTS=1` (padrão).

## 9. Helpers (QA 1.2 + QA 1.3C)

`tests/e2e/_helpers.js`:

- `waitForPageReady`, `requireAuthenticatedPage`, `waitForAuthenticatedAppReady`, `waitForEditaisCatalogReady`
- `getFirstVisibleCard`, `getFirstVisibleEditalCard`, `getCardTitle`, `getSearchableCardTitle`
- `safeDownloadClick`, `saveE2EEvidence`, `skipWithEvidence`
- `isWriteTestsAllowed`, `skipIfNoWriteTests`
- `openEditaisSidebarIfNeeded`, `openStatusFilterSection`, `toggleFirstAvailableStatusFilter`
- `navigateCadastrosEditaisTab`, `closeAdminEditalModal`
- `ensureEditaisFiltersVisible` (expande collapse de status)

## 10. testids adicionados

| testid | Onde |
|--------|------|
| `editais-search-input` | Header (busca Editais) |
| `editais-export-pdf` | Botão PDF |
| `editais-export-xlsx` | Botão Planilha |
| `radar-page` | Wrapper Radar |
| `radar-placeholder` | Estado vazio |
| `radar-card` | Card de recomendação |
| `cadastros-page` | Wrapper Cadastros |
| `cadastros-tab-editais` | Aba Editais na sidebar (QA 1.3C) |
| `cadastro-novo-edital` | Botão + Novo edital |
| `edital-form-titulo` / `edital-form-link` / `edital-form-submit` | Formulário |
| `edital-form-cancel` / `edital-form-close` | Fechar modal sem salvar (QA 1.3C) |
| `semantic-status-section` / `semantic-status-section-toggle` | Collapse filtro status (QA 1.3C) |
| `app-feedback-submit` | Botão Gmail no report |

## 11. Limitações

- Conteúdo binário PDF/XLSX não validado em E2E (coberto por unit tests).
- Contagens exatas de KPIs não assertadas.
- Grants.gov pode skipar se não houver cards (`grants-links.spec.js`).
- Escrita em Cadastros deixa registro no DB (opt-in; não há cleanup).

## 12. Próximo patch recomendado

**QA 1.3B** — GitHub Actions/CI com secrets. Local: `npm run qa:local` (QA 1.3A). Skips evitáveis: ver `docs/QA_1_3C_REDUCE_E2E_SKIPS.md`.

## Referências

- `docs/QA_AUTOMATION_GUIDE.md`
- `docs/QA_1_1_PLAYWRIGHT_HARNESS_FIX.md`
- `docs/QA_1_3C_REDUCE_E2E_SKIPS.md`
