# Crawler piloto — IBFC (Instituto Brasileiro de Formação e Capacitação)

- **Fonte:** `ibfc`
- **Listagens:** `https://concursos.ibfc.org.br/index/abertos/,https://concursos.ibfc.org.br/index/1/`
- **Coleta (UTC):** `2026-05-14T21:38:08.798736+00:00`
- **URLs candidatas (bruto):** 10
- **Descartados:** 9
- **Standardized:** 1
- **Ficheiro:** `D:/Computational_Physics/My Projects/edital/audit_reports_main_pipeline/concursos_wave1_ibfc/standardized/ibfc_standardized.json`

## Próximo passo

`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_ibfc/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_ibfc/loader_dryrun --sources ibfc`
