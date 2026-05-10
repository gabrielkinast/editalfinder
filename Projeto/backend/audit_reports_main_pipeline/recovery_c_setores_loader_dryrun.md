# Recovery C — loader dry-run (EMBRAPII + NUCLEP)

## Resumo

| Métrica | Valor |
|--------|------:|
| Fontes | 2 |
| Itens standardized | 41 |
| `would_upsert_total` | 41 |
| `mapping_errors_total` | **0** |
| `critical_empty_items_total` | **0** |
| `documentos_perdidos_no_payload_total` | **0** |
| Destinos | `edital`: 41 |

## Verificações Recovery C

- **`setor_estrategico` com mais de 3 valores** no bundle `recovery_c_setores/standardized`: **0** (validação por script pós-retransform).
- **Auditoria semântica** (`recovery_c_setores_semantic/audit_semantic_summary.json`): não há flag `titulo_ruidoso` no resumo; aparecem `area_cientifica_sem_evidencia` (20) e `publico_alvo_sem_evidencia` (1) — dívida incremental, não bloqueio de mapeamento.
- **Setores excedentes** foram movidos para `extras.tags_secundarias` e a lista completa preservada em `extras.setores_detectados` onde aplicável.

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources embrapii,nuclep --exclude-blocked --input-dir audit_reports_main_pipeline/recovery_c_setores/standardized --readiness audit_reports_retransform/readiness_for_loader.json --output-dir audit_reports_main_pipeline/recovery_c_setores_loader_dryrun
```

Relatório completo: `audit_reports_main_pipeline/recovery_c_setores_loader_dryrun/load_ready_summary.json`.
