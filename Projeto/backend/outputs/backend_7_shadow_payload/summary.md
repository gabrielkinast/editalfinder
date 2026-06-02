# Payload tabela sombra — Backend 7

**Registros processados:** 1232

## Cobertura por campo

- `prazo_status`: 1232 (100.0%)
- `prazo_confidence`: 1232 (100.0%)
- `tipo_registro`: 1232 (100.0%)
- `kind_confidence`: 1232 (100.0%)
- `modalidade_normalizada`: 1232 (100.0%)
- `modalidade_label`: 1232 (100.0%)
- `modalidade_confidence`: 1232 (100.0%)
- `escopo_geografico`: 1232 (100.0%)
- `escopo_confidence`: 1232 (100.0%)
- `fonte_normalizada`: 1232 (100.0%)
- `source_scope`: 1232 (100.0%)
- `area_tematica_normalizada`: 1232 (100.0%)
- `area_tematica_label`: 1232 (100.0%)
- `area_tematica_confidence`: 1232 (100.0%)
- `backend_enrichment`: 1232 (100.0%)
- `enrichment_version`: 1232 (100.0%)
- `pais_origem`: 1225 (99.4%)
- `qualidade_flags`: 1174 (95.3%)
- `area_tematica_secondary`: 878 (71.3%)
- `prazo_data`: 207 (16.8%)
- `prazo_raw`: 207 (16.8%)
- `prazo_source_field`: 207 (16.8%)

## Revisão humana
- Baixa confiança (qualquer campo): **500**
- Prazo baixa confiança: **91**
- Mudanças sensíveis de tipo (notícia/pesquisa/concurso): **70**
- Área baixa confiança ou sem classificação: **500**

Nenhuma escrita no banco (modo dry-run). Use `--write-shadow` com env de proteção.

Para gravar: `EDITALFINDER_ALLOW_SHADOW_WRITE=true` + `--write-shadow`

Artefatos: `shadow_payload.json`, `low_confidence_rows.json`, `risky_kind_changes.json`,
`risky_area_changes.json`, `deadline_low_confidence.json`.