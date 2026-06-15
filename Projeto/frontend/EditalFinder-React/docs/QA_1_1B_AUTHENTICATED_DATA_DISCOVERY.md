# QA 1.1B — Authenticated E2E Data Discovery Fix

## Problema (pós QA 1.1 com credenciais)

- `auth.setup` passou; login real OK; 7 passed; 2 skipped.
- `editais-detail` e `grants-links` skipavam em `_helpers.js:133` (`editais-stats-bar` não visível em ~2s).

## Causa raiz

1. **`requireCatalogData` não refazia login** — `report-problem` chamava `loginIfConfigured` no `beforeEach`; os specs de dados só confiavam no `storageState` e iam direto para `/editais`.
2. **Sessão Supabase em localStorage** — às vezes o redirect para login ocorria antes do bootstrap do `AuthContext` restaurar a sessão.
3. **Sem espera de loading** — stats bar existe durante loading, mas a página podia ainda estar em `ProtectedRoute` / login.
4. **Timeout curto efetivo** — `isVisible().catch(() => false)` sem `waitFor` robusto.
5. **Grants.gov** — selector `[data-source*="Grants"]` podia falhar; fonte real está em `fonte_recurso_display` → novo `data-fonte`.

## Correções

| Item | Arquivo |
|------|---------|
| `waitForEditaisCatalog`, `ensureAuthenticatedOnEditais`, `requireCatalogReady` | `tests/e2e/_catalog.js` |
| Relogin se redirect login | `_catalog.js` |
| Espera `editais-loading` sumir | `_catalog.js` + `EditaisPage.jsx` |
| `data-fonte` nos cards | `EditalCard.jsx` |
| Evidência de skip (png/json/txt) | `qa/artifacts/playwright/debug-authenticated-data/` |
| Sanidade autenticada | `authenticated-smoke.spec.js` |

## Rodar

```powershell
$env:E2E_USER_EMAIL="..."
$env:E2E_USER_PASSWORD="..."
npm run e2e
Remove-Item Env:E2E_USER_EMAIL
Remove-Item Env:E2E_USER_PASSWORD
```

Se ainda houver skip, inspecionar `qa/artifacts/playwright/debug-authenticated-data/*-skip.*`.
