# QA 1.3A — Standardized QA Scripts + Automatic QA Results

**Data:** 2026-06-10

---

## 1. Objetivo

Padronizar a execução local de QA (unit + build + E2E) e gerar automaticamente:

- `qa/artifacts/qa_results.json`
- `qa/artifacts/qa_summary_latest.md`

sem depender de atualização manual.

## 2. Scripts npm

| Script | Ação |
|--------|------|
| `npm run qa:unit` | Alias de `npm test` |
| `npm run qa:build` | Alias de `npm run build` |
| `npm run qa:e2e` | Alias de `npm run e2e` |
| `npm run qa:results` | Gera `qa_results.json` a partir de logs/state |
| `npm run qa:summary` | Gera `qa_summary_latest.md` a partir de `qa_results.json` |
| `npm run qa:local` | Pipeline completo + artefatos |

## 3. Como rodar QA básico

```powershell
cd frontend/EditalFinder-React
npm run qa:local
```

## 4. Com credenciais E2E

```powershell
$env:E2E_USER_EMAIL="..."
$env:E2E_USER_PASSWORD="..."
npm run qa:local
Remove-Item Env:E2E_USER_EMAIL
Remove-Item Env:E2E_USER_PASSWORD
```

## 5. Com escrita opt-in (Cadastros)

```powershell
$env:E2E_ALLOW_WRITE_TESTS="1"
# + credenciais acima
npm run qa:local
Remove-Item Env:E2E_ALLOW_WRITE_TESTS
```

## 6. Artefatos

| Caminho | Conteúdo |
|---------|----------|
| `qa/artifacts/logs/unit.log` | Saída `npm test` (sanitizada) |
| `qa/artifacts/logs/build.log` | Saída `npm run build` |
| `qa/artifacts/logs/e2e.log` | Saída `npm run e2e` |
| `qa/artifacts/logs/qa-local.log` | Orquestrador |
| `qa/artifacts/qa_run_state.json` | Exit codes e durações |
| `qa/artifacts/qa_results.json` | JSON consolidado |
| `qa/artifacts/qa_summary_latest.md` | Resumo legível |
| `qa/artifacts/playwright/results.json` | Playwright JSON reporter |
| `qa/artifacts/playwright/html/` | Relatório HTML |

`qa/artifacts/qa_summary.md` recebe/atualiza seção **Última execução automática** sem apagar histórico.

## 7. Sanitização

Logs passam por `sanitizeLogText()`:

- senhas (`E2E_USER_PASSWORD`)
- e-mails mascarados
- JWT / Bearer / access_token / refresh_token
- chaves Supabase sensíveis

## 8. Interpretar skips

- Sem credenciais: specs autenticados skipped (esperado).
- Sem catálogo/permissão: skip com evidência em `debug-e2e/`.
- Escrita Cadastros: skip com `SKIP_WRITE_OPT_IN_DISABLED` sem `E2E_ALLOW_WRITE_TESTS=1`.
- Com credenciais QA (pós QA 1.3C): meta **18 passed / 1 skipped** (único skip = escrita opt-in).

## 9. Falhas

`qa:local` retorna exit code **1** se unit, build ou e2e falharem — mas ainda gera logs e tenta `qa_results` / `qa_summary`.

## 10. Próximo patch

**QA 1.3B** — implementado: `.github/workflows/qa.yml` — ver `docs/QA_1_3B_GITHUB_ACTIONS_CI.md`.

Próximo opcional: workflow manual para escrita opt-in em ambiente descartável.

## Referências

- `docs/QA_AUTOMATION_GUIDE.md`
- `docs/QA_1_2_EXPANDED_E2E_REGRESSION_SUITE.md`
- `docs/QA_1_3B_GITHUB_ACTIONS_CI.md`
- `docs/QA_1_3C_REDUCE_E2E_SKIPS.md`
