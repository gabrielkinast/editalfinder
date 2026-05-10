# Recovery A — Métricas por fonte

Dados alinhados a `recovery_a_by_source.json` (pasta `audit_reports_main_pipeline/`).

## banco_da_amazonia

- **Standardized:** 26
- **mapping_errors (loader-only):** 0
- **Notas:** `validacao_status` tendencialmente `incompleto` quando faltam prazo/valor (não inventados)

## dod_sbir_sttr

- **Standardized:** 6 (`https://www.sbir.gov/topics/<id>`)
- **mapping_errors:** 0
- **Notas:** coleta HTML por **429** na API; soft-continue local `dod_sbir_sttr_recovery_a_local` no transformer; qualidade `incompleto` com aviso `opportunity_gate_dod_sbir_sttr_topic`

## esa_star

- **Standardized:** 0
- **mapping_errors:** 0 (sem itens)
- **Notas:** manter blocked até fonte pública útil
