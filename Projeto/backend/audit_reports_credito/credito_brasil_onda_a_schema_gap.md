# Crédito Brasil — Onda A: alinhamento `public.edital` × payload do loader

## Contexto

No staging, o apply do lote (fontes `bnb`, `banco_da_amazonia`, `bdmg`) falhou por colunas ausentes em `public.edital`, em sequência (`contrapartida`, `descricao_original`, …). O payload efetivo do upsert é produzido por `CORE/loader.py` (`map_to_db_schema` → `_rebuild_merged_extras` → `_merge_db_row` → `extras_to_filter_columns` → `_strip_payload`).

## Metodologia

1. Itens lidos de `audit_reports_retransform/standardized/{bnb,banco_da_amazonia,bdmg}_standardized.json`.
2. Cada registo normalizado com `schema.normalizar`, roteado apenas para `edital`.
3. Payload simulado como insert novo: `_merge_db_row(None, mapped, _rebuild_merged_extras(None, extras_new), item_n)` com `EDITALFINDER_EXTENDED_SCHEMA=true`.
4. Conjunto de chaves do payload comparado com as colunas declaradas em `migrations/20260505_add_missing_edital_columns_from_loader_payload.sql`.

## Resultado

| Métrica | Valor |
|--------|--------|
| Chaves distintas no payload (após strip) | 64 |
| Colunas cobertas pela migration 2026-05-05 | 104 |
| Colunas do payload **não** presentes na migration | **0** |

Conclusão: a migration aditiva cobre **todas** as chaves que o loader envia no upsert para as amostras analisadas. As colunas extra na migration antecipam campos definidos em `_LEGACY_EDITAL_COLUMNS | _EXTENDED_EXTRA_COLUMNS` que ainda não apareceram neste subconjunto de ficheiros.

## Chaves que permanecem só em `extras` (JSONB)

Não são colunas de topo no upsert; o loader mantém-nas dentro de `extras` (não passam em `_strip_payload` como colunas separadas). Exemplos observados nas amostras:

`acao_identificada`, `coletado_em`, `content_hash`, `cronograma`, `descricao_completa`, `destination_table`, `extraction_richness`, `field_confidence`, `metodo_classificacao`, `metodo_extracao`, `necessita_traducao`, `opportunity_gate_*`, `origem`, `palavras_chave_detectadas`, `pdf_enrichment`, `programa_identificado`, `public_investment_scope`, entre outras.

Para promover qualquer uma destas chaves a coluna física no futuro, alinhar: migration `ADD COLUMN`, entrada em `_EXTENDED_EXTRA_COLUMNS` e mapeamento em `extras_to_filter_columns` (ou `map_to_db_schema`).

## Artefatos

- Detalhe coluna a coluna (exemplos e fontes): `credito_brasil_onda_a_schema_gap.json`
- Migration aditiva: `migrations/20260505_add_missing_edital_columns_from_loader_payload.sql`
- Views (staging): `migrations/20260505_recreate_edital_views_credito_staging.sql`
- Verificação: `docs/sql/check_edital_payload_columns.sql`

## Aplicação no staging (ordem)

1. Executar `migrations/20260505_add_missing_edital_columns_from_loader_payload.sql` (inclui `NOTIFY pgrst, 'reload schema'`).
2. Opcional: `migrations/20260505_recreate_edital_views_credito_staging.sql`.
3. Executar `docs/sql/check_edital_payload_columns.sql` e confirmar lista vazia de colunas em falta.
4. Repetir o apply para `bnb`, `banco_da_amazonia`, `bdmg`.
