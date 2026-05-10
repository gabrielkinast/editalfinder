# Preservação taxonómica no loader (contexto Recovery C)

## Onde os campos “não vazios” são contados

Em `scripts/load_ready_sources.py`, a função `_simulate_source` compara, para cada item de edital, o **standardized** (`norm.extras` → `in_ex`) com o **payload mapeado** (`map_to_db_schema` → `ex`). Para cada chave em `TRACK_FIELDS`, incrementa `field_preserved_non_empty` quando **entrada e saída** são não vazias — sem ir à base de dados, excepto quando se usa `--overwrite-fields` (pré-visualização de diff de merge).

## Por que `setor_estrategico` aparece como “preservado” 41 vezes

`fields_preserved_non_empty_total.setor_estrategico = 41` significa: em todos os 41 itens, o standardized tinha `setor_estrategico` nos extras **e** o resultado de `map_to_db_schema` também — **não** indica que o valor final na tabela coincida com o cap da Recovery C.

## Onde o estado real diverge

No **apply**, `CORE/loader.py` faz:

1. `existing = fetch_edital_by_link(...)`
2. `merged_extras = _rebuild_merged_extras(existing, extras_new)`

Dentro de `_rebuild_merged_extras`, `merge_extras_dict` **une listas** (`cur + v` deduplicado). Assim, `setor_estrategico` na BD e o payload novo podem **acumular** etiquetas únicas até ultrapassar 3.

`extras_to_filter_columns` (em `CORE/taxonomy_filtros.py`) copia `merged_extras['setor_estrategico']` para a coluna espelho `setor_estrategico`.

## Campos taxonómicos no mesmo padrão de merge

Qualquer lista em `extras` submetida ao mesmo merge vê o mesmo comportamento de união. A coluna espelho `setor_estrategico` é a que está ligada ao aviso `setor_estrategico_muito_amplo` na validação global.

## Solução segura implementada

- CLI: `--overwrite-fields setor_estrategico` (v1 só este campo).
- Obrigatório: `--sources` explícito.
- Apply real: manter `--apply --staging` como guardas existentes.
- Implementação: `taxonomy_replace_keys` em `_rebuild_merged_extras` substitui o valor fundido pelo do payload novo quando não vazio.

Ver relatório de dry-run: `audit_reports_main_pipeline/recovery_c_taxonomy_overwrite_dryrun/` (quando gerado).
