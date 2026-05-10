# Transform Paths

## Funções transform_*

- `transform_cnpq` -> `transform_generic`
- `transform_finep` -> `transform_generic` + ajuste local `tipo_recurso`
- `transform_fapergs` -> `transform_generic`
- `transform_embrapii` -> `transform_generic`
- `transform_bndes` -> `transform_generic` (wrapper multi-fontes)

## Pipeline comum (`_transform_item_with_result`)

- `noise_filter.should_discard_item`
- `opportunity_gate.evaluate_item_dict`
- relax local `pncp_defesa/compras_defesa` (transformer apenas)
- normalização de documentos/PDF
- `enrich_opportunity_classification` + `br_public_hints`
- `apply_quality_to_payload` (`validacao_status`)
- `sanitize_for_postgres`

## Loader

- `main.py` -> `CORE/transformer.py` gera `*_standardized.json`
- `main.py` -> `CORE/loader.py` consome standardized via `load_standardized_json`
- auditorias (`audit_pipeline.py`, `audit_docs_pipeline.py`) chamam `loader.map_to_db_schema` em dry-run