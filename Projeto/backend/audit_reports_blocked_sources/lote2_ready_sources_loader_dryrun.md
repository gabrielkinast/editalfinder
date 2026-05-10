# Dry-run combinado — lote 2 (readiness **canónico**)

**Data:** 2026-05-02  

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources horizon_europe,erc,doe_arpae,nato_diana,iarpa --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Resultado (última execução)

| Verificação | Valor |
|-------------|------:|
| Fontes seleccionadas | 5 |
| Itens standardized | 57 |
| would_upsert | 57 |
| Erros de mapeamento | 0 |
| critical_empty_items | 0 |
| Documentos preservados (itens) | 8 |
| pdf_url preservado (itens) | 8 |
| validacao_status preservado | 57 |
| qualidade_dado preservada | 57 |
| Canonização skip | 0 |
| sam_gov incluída | Não |
| official_link_only (amostra) | 0 |

## Slice temporário

`audit_reports_blocked_sources/lote2_readiness_for_loader_apply_slice.json` está marcado como **DEPRECATED**: o `readiness_for_loader.json` canónico foi regenerado após alinhar `retransform_by_source.json` (merge parcial + regras de readiness). **Não é necessário** para novos dry-runs.

## Artefactos

- Resumo completo: `audit_reports_loader_ready/load_ready_summary.json`
