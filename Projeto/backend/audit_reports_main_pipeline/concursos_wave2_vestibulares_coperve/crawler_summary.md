# Crawler Wave 2 — Vestibulares UFSC (Coperve)

- **Fonte:** `coperve` | **tipo:** vestibular / programa_ingresso
- **Coleta (UTC):** `2026-05-16T20:19:44.139509+00:00`
- **URLs candidatas:** 12
- **Descartados:** 3
- **Standardized:** 9
- **Nota:** UFSC/Coperve — Vunesp indisponível (403); Comvest bloqueado em robots; Fuvest com SSL intermitente.

## Dry-run loader

```bash
python scripts/load_concursos_selecao.py --dry-run \
  --input-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/standardized \
  --output-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/loader_dryrun \
  --sources coperve
```
