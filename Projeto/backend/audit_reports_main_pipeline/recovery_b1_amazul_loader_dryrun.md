# Recovery B.1 — loader dry-run AMAZUL

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources amazul --exclude-blocked --input-dir audit_reports_main_pipeline/recovery_b1_amazul/standardized --readiness audit_reports_main_pipeline/recovery_b_readiness_official_dryrun.json --output-dir audit_reports_main_pipeline/recovery_b1_amazul_loader_dryrun
```

## Resultados

| Métrica | Valor |
|---------|------:|
| `sources_selected` | 1 |
| `would_upsert_total` | 20 |
| `mapping_errors_total` | 0 |
| `critical_empty_items_total` | 0 |
| `documentos_perdidos_no_payload_total` | 0 |
| `destination_counts_total` | edital: 20 |

## Critérios Recovery B.1

- **mapping_errors** / **critical_empty**: **0**
- **Título ruído** / **institucional genérico**: **0** na amostra local
- **credito_tipo_recurso_incoerente**: espera-se **queda** no próximo `post_daily` após apply — `reembolsavel=false` em licitações calibradas (objeto pode conter a palavra “crédito” sem ser linha de crédito bancário)
- **suspeito**: **0** no `amazul_standardized.json` deste dry-run; staging só alinha após carga
- **Prazo vencido**: pode permanecer como warning com `prazo_envio` real; **não** se inventam prazos

Relatório completo: `audit_reports_main_pipeline/recovery_b1_amazul_loader_dryrun/load_ready_summary.json`.
