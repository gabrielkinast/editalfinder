# Crawler piloto — Legalle Concursos

- **Fonte:** `legalle`
- **Listagens:** `https://portal.editais.legalleconcursos.com.br/edital/index/abertos/,https://portal.editais.legalleconcursos.com.br/edital/index/1/`
- **Coleta (UTC):** `2026-05-15T16:18:00.842925+00:00`
- **URLs candidatas (bruto):** 60
- **Descartados:** 55
- **Standardized:** 5
- **Ficheiro:** `D:/Computational_Physics/My Projects/edital/audit_reports_main_pipeline/concursos_wave1_legalle/standardized/legalle_standardized.json`

## Próximo passo

`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_legalle/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_legalle/loader_dryrun --sources legalle`
