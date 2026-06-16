# QA Summary — Latest Run

Generated at: 2026-06-15T15:40:23.171Z

## Environment

- Auth configured: yes (e***@gmail.com)
- Write tests enabled: no
- CI: no
- Platform: win32 · Node v24.15.0
- Supabase URL in env: yes

## Results

| Layer | Status | Passed | Failed | Skipped | Duration |
| --- | --- | ---: | ---: | ---: | ---: |
| Unit | passed | 301 | 0 | 0 | 4.2s |
| Build | passed | — | 0 | — | 5.7s |
| E2E | passed | 18 | 0 | 1 | 116.8s |

## E2E Specs

| Status | Project | File | Test | Duration |
| --- | --- | --- | --- | ---: |
| passed | auth-setup | `auth.setup.js` | authenticate for E2E | 5.8s |
| passed | public | `smoke.spec.js` | app-load: raiz redireciona para login quando não autenticado [P0] | 2.6s |
| passed | public | `smoke.spec.js` | login-page: formulário renderiza sem erro fatal [P0] | 2.1s |
| passed | public | `smoke.spec.js` | protected-route: /editais redireciona para login sem auth [P0] | 2.3s |
| passed | public | `smoke.spec.js` | protected-route: /dashboard redireciona para login sem auth [P0] | 2.4s |
| passed | public | `smoke.spec.js` | router-basename: assets da SPA carregam (sem tela em branco) [P0] | 1.9s |
| passed | authenticated | `authenticated-smoke.spec.js` | editais carrega fora do login com stats ou cards [P0] | 43.3s |
| passed | authenticated | `cadastros-smoke.spec.js` | abre modal novo edital sem salvar [P2] | 39.0s |
| skipped | authenticated | `cadastros-smoke.spec.js` | cria edital manual com flag E2E_ALLOW_WRITE_TESTS [P3] | 1.3s |
| passed | authenticated | `dashboard-smoke.spec.js` | dashboard renderiza KPIs e link para editais [P2] | 31.7s |
| passed | authenticated | `editais-detail.spec.js` | abre os primeiros 10 editais e registra detalhes quebrados [P1] | 81.7s |
| passed | authenticated | `editais-export.spec.js` | export XLSX e PDF iniciam download [P2] | 43.1s |
| passed | authenticated | `editais-filters.spec.js` | busca por título do card + filtro status sem erro fatal [P2] | 57.1s |
| passed | authenticated | `editais-status-filter.spec.js` | aplica e remove filtro Aberto sem quebrar lista [P2] | 32.2s |
| passed | authenticated | `external-links.spec.js` | botões externos de cards não usam URLs inválidas [P2] | 31.1s |
| passed | authenticated | `grants-links.spec.js` | botões externos não apontam para page-not-found [P1] | 15.8s |
| passed | authenticated | `radar-smoke.spec.js` | radar renderiza placeholder ou cards [P2] | 5.8s |
| passed | authenticated | `report-problem.spec.js` | modal geral mostra ambiente + orientação de reporte [P1] | 8.1s |
| passed | authenticated | `report-problem.spec.js` | botão de envio Gmail ou fallback existe sem enviar e-mail [P2] | 4.9s |

## Artifacts

- Logs: `qa/artifacts/logs/`
- Playwright JSON: `qa/artifacts/playwright/results.json`
- Playwright HTML: `qa/artifacts/playwright/html/`
- QA results: `qa/artifacts/qa_results.json`
- Run state: `qa/artifacts/qa_run_state.json`

## Notes

- E2E autenticados fazem skip sem `E2E_USER_EMAIL` / `E2E_USER_PASSWORD`.
- Escrita em Cadastros exige `E2E_ALLOW_WRITE_TESTS=1`.
- Skips por dados/permissões são esperados em alguns ambientes.
- Gerado por `npm run qa:local` (QA 1.3A).
