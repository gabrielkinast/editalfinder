# Badesul — loader dry-run (ready_with_notes)

- Decisão de readiness: `badesul -> ready_with_notes`
- PNCP: `mantido blocked`
- Execução: apenas `dry-run` (sem apply, sem mudanças em banco)

## Comando executado

`python scripts/load_ready_sources.py --dry-run --sources badesul --exclude-blocked --readiness audit_reports_blocked_sources/readiness_for_loader_badesul_override.json --input-dir audit_reports_blocked_sources/lote1_fix_badesul_pncp/standardized`

## Resultado

- `sources_selected`: **1**
- `sources_excluded`: **1**
- `itens_standardized_total`: **7**
- `would_upsert_total`: **7**
- `would_ignore_total`: **0**
- `mapping_errors_total`: **0**
- `docs_input_items_total`: **7**
- `docs_preserved_items_total`: **7**
- `documentos_perdidos_no_payload_total`: **0**
- `standardized_com_documentos_nao_pdf_total`: **7**
- `payload_com_documentos_nao_pdf_total`: **7**
- `perda_documentos_nao_pdf_total`: **0**
- `apply_status`: `not_requested`

## Recorte por fonte

- `badesul`: `itens_standardized=7`, `would_upsert=7`, `mapping_errors=0`, `docs_preserved_items=7`.

## Confirmações de segurança

- Não foi executado `--apply`.
- Não houve carga em produção.
- PNCP permanece bloqueado e não foi alterado nesta etapa.
