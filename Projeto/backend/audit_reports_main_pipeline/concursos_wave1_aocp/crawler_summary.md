# Crawler piloto — Instituto AOCP

- **Fonte:** `aocp`
- **API lista:** `https://link.aocp.com.br/api/concursos`
- **Filtro status lista:** `IN_PROGRESS`
- **Coleta (UTC):** `2026-05-14T22:23:31.711997+00:00`
- **Registos na API (total):** 230
- **Candidatos (lista filtrada `IN_PROGRESS`):** 1
- **Descartados:** 1
- **Standardized:** 0
- **Ficheiro:** `D:/Computational_Physics/My Projects/edital/audit_reports_main_pipeline/concursos_wave1_aocp/standardized/aocp_standardized.json`

## Próximo passo

`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_aocp/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_aocp/loader_dryrun --sources aocp`
