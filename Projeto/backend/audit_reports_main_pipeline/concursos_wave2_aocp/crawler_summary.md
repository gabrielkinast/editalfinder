# Crawler piloto — Instituto AOCP

- **Fonte:** `aocp`
- **API lista:** `https://link.institutoaocp.org.br/api/concursos`
- **Filtro status lista:** `['IN_PROGRESS', 'NEW']`
- **Coleta (UTC):** `2026-05-16T21:18:44.365275+00:00`
- **Registos na API (total):** 383
- **Candidatos (lista filtrada `inscricoes-abertas`):** 33
- **Descartados:** 31
- **Standardized:** 2
- **Ficheiro:** `audit_reports_main_pipeline/concursos_wave2_aocp/standardized/aocp_standardized.json`

## Próximo passo

`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_aocp/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_aocp/loader_dryrun --sources aocp`
