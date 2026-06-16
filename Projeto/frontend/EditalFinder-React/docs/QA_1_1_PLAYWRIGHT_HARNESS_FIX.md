# QA 1.1 — Playwright E2E Harness Fix

## Estado anterior

- `@playwright/test@1.60.0` já instalado.
- Primeira execução (2026-06-10): **0 passed, 6 failed**.
- Falhas eram de **setup do harness**, não regressão funcional confirmada.

## Causas das falhas

| # | Causa | Sintoma |
|---|--------|---------|
| 1 | Rotas protegidas sem auth | `page.goto('/editais')` → redirect login; `editais-stats-bar` ausente |
| 2 | Basename `/editalfinder` ignorado | `page.goto('/editais')` ia para `http://host/editais` em vez de `/editalfinder/editais` |
| 3 | `baseURL` sem basename | Playwright não prefixava rotas corretamente |
| 4 | Build preview sem env explícito | `.env.local` agora carregado no config Node + embutido no `vite build` |
| 5 | Specs misturavam camadas | Testes públicos e autenticados no mesmo arquivo sem skip |

## Estratégia de auth (Opção A — login real)

- Variáveis: `E2E_USER_EMAIL`, `E2E_USER_PASSWORD` (shell ou `.env.local`, **nunca commitar**).
- `tests/e2e/auth.setup.js` faz login uma vez e salva `playwright/.auth/user.json` (gitignored).
- Projeto `authenticated` usa `storageState`.
- **Sem credenciais:** specs auth/data fazem `test.skip()` com mensagem `SKIP_NO_AUTH`.
- **Sem bypass invasivo** no app (`VITE_E2E_AUTH_BYPASS` não foi adicionado).

## Basename / baseURL

- Preview web usa `base: /editalfinder/` (vite.config.js).
- Playwright `baseURL`: `http://127.0.0.1:4173/editalfinder` (override: `E2E_BASE_URL`).
- Helper `appPath('/editais')` → `./editais` (path relativo — preserva basename).
- **Nunca** usar `page.goto('/editais')` com barra inicial absoluta.

## Env / Supabase

- `tests/e2e/_env.js` carrega `.env.local` no processo Playwright.
- `hasSupabaseEnv()` verifica `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY`.
- Log seguro no startup: booleans + `supabaseHost` — **sem anon key**.
- Testes de dados (`requireCatalogData`) fazem skip se env ausente ou catálogo vazio.

## Camadas E2E

| Camada | Projeto | Specs | Requisitos |
|--------|---------|-------|------------|
| 1 — Public | `public` | `smoke.spec.js` | Nenhum |
| 2 — Auth | `authenticated` | `report-problem.spec.js` | `E2E_USER_*` |
| 3 — Data | `authenticated` | `editais-detail`, `grants-links` | Auth + Supabase + catálogo > 0 |

## Como rodar

### Sem credenciais (só Camada 1)

```bash
npm test
npm run e2e
```

Esperado: **5 passed** (public) + **3 skipped** (authenticated).

### Com credenciais QA

```powershell
$env:E2E_USER_EMAIL="seu-qa@example.com"
$env:E2E_USER_PASSWORD="***"
npm run e2e
```

### Relatório HTML

```bash
npm run e2e:report
```

Artefatos:

- `qa/artifacts/playwright/results.json`
- `qa/artifacts/playwright/html/`
- `qa/artifacts/playwright/test-results/` (screenshots, traces, vídeos em falha)

## Interpretar skips

| Mensagem | Significado |
|----------|-------------|
| `E2E_USER_EMAIL e E2E_USER_PASSWORD não configurados` | Normal sem credenciais QA |
| `VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY ausentes` | Build sem Supabase |
| `Catálogo vazio ou barra de stats indisponível` | Auth falhou ou RLS/dados |
| `Nenhum card Grants.gov visível` | Skip aceitável em grants-links |

## Limitações

- Não testa Tauri/EXE (Camada C/D separadas).
- Login real depende de conta Supabase estável (sem 2FA bloqueando).
- `webServer` roda `build + preview` (~2 min na primeira vez).
- Testes de dados dependem do staging/produção configurado em `.env.local`.

## Próximo patch recomendado

1. **FRONTEND 1.1F** — cadastro/policy RLS + rascunho local.
2. Credenciais QA dedicadas no CI (secrets do GitHub, não no repo).
3. **BACKEND 10.3B** apply + filtro `hidden_duplicate` no frontend.
