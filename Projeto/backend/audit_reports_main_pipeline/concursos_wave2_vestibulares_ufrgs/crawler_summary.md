# Crawler Wave 2 — Vestibulares UFRGS (CV / COPERSE)

- **Fonte:** `ufrgs_cv`
- **Hub:** https://vestibular.ufrgs.br
- **Coleta (UTC):** `2026-05-16T20:29:46.343382+00:00`
- **URLs candidatas:** 17
- **Descartados:** 10
- **Standardized:** 7 (`valido`: 0)

## Loader dry-run

```bash
python scripts/load_concursos_selecao.py --dry-run \
  --input-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/standardized \
  --output-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/loader_dryrun \
  --sources ufrgs_cv
```
