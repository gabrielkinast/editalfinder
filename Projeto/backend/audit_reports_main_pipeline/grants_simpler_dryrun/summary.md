# Dry-run Simpler.Grants.gov

- **Modo API:** `legacy_search2_fallback`
- **Itens pipeline:** 30
- **Revisão (curadoria):** 7
- **Páginas:** 3 | **Max itens:** 50

## Diagnóstico

- HTML SSR em `/search` não lista oportunidades (SPA); dados via API ou fallback `search2`.
- Link canônico: `https://simpler.grants.gov/opportunity/{legacy_id|uuid}`
- `robots.txt`: Allow `/`; Disallow `/api/`
- Rate limit API: 60 req/min (usar `SIMPLER_GRANTS_SLEEP_SEC`, default 0.35s)

## Artefatos

- `audit_reports_main_pipeline\grants_simpler_dryrun\raw\grants_simpler_raw.json`
- `audit_reports_main_pipeline\grants_simpler_dryrun\standardized\grants_simpler_standardized.json`

**Não executar apply** — apenas revisão humana.

> Defina `SIMPLER_GRANTS_API_KEY` para busca direta na API Simpler; sem chave, o dry-run usa `api.grants.gov/search2` + links Simpler.
