# Recovery B — loader dry-run oficial (isolado)

## Comando

`python scripts/load_ready_sources.py --dry-run --sources amazul,ambev,badesul --exclude-blocked --input-dir audit_reports_main_pipeline/recovery_b_official_dryrun_standardized --readiness audit_reports_main_pipeline/recovery_b_readiness_official_dryrun.json --output-dir audit_reports_main_pipeline/recovery_b_official_loader_dryrun_bundle`

## Resultados verificados

| Métrica | Valor |
|---|---:|
| `sources_selected` | 3 |
| `would_upsert_total` | 32 |
| `mapping_errors_total` | 0 |
| `critical_empty_items_total` | 0 |
| `documentos_perdidos_no_payload_total` | 0 |
| `destination_counts_total` | `{"edital": 32}` |
| `validacao_status=suspeito` (amostra payload) | 0 |

## Ruído / institucional

- Títulos ruído (lista canónica curta): **0** — ver `recovery_b_official_dryrun_context.json`.
- Login isolado (heurística): **0**.
- Página institucional BADESUL `/home`: **0**.

## Artefactos

- Resumo completo: `audit_reports_main_pipeline/recovery_b_official_loader_dryrun_bundle/load_ready_summary.json`
- Slice JSON: `recovery_b_official_loader_dryrun.json`
