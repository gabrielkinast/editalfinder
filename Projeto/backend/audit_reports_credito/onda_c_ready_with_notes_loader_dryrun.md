# Onda C — dry-run oficial loader (ready_with_notes)

- **Data:** `2026-05-10T03:22:32Z`

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources ukri_funding,eit,esa_osip --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Verificação (tarefa 6)

| Critério | OK |
|---|---:|
| `sources_selected_eq_3` | **True** |
| `would_upsert_eq_45` | **True** |
| `mapping_errors_0` | **True** |
| `critical_empty_0` | **True** |
| `docs_lost_0` | **True** |
| `destination_edital_only` | **True** |
| `excluded_not_in_selected` | **True** |
| `selected_fontes` | **['eit', 'esa_osip', 'ukri_funding']** |

## Resumo

- sources_selected: **3**
- would_upsert_total: **45**
- mapping_errors_total: **0**
- critical_empty_items_total: **0**
- documentos_perdidos_no_payload_total: **0**
- destination_counts_total: `{'edital': 45}`

## Por fonte

Detalhe em `onda_c_ready_with_notes_loader_dryrun.json`.

## Próximo passo

Dry-run oficial limpo. Etapa seguinte (com autorização e variáveis de staging): `python scripts/load_ready_sources.py --apply --staging --test-db-before-apply --sources ukri_funding,eit,esa_osip --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json`

**Apply não executado nesta tarefa.**