# Auditoria loader-only

- Ficheiros standardized processados: **3**
- Itens analisados (amostra): **43**
- Itens com alerta de payload: **43**

## Top 10 perdas de dados (campos)
- `acao`: 43
- `regiao`: 43
- `programa`: 41
- `tipo_recurso`: 19
- `temas`: 15
- `publico_alvo`: 10

## Top 10 fontes com maior problema no payload
- `bndes` (bndes_standardized.json): problemas=19, amostra=19, readiness=0.0
- `cnpq` (cnpq_standardized.json): problemas=14, amostra=14, readiness=0.0
- `finep` (finep_standardized.json): problemas=10, amostra=10, readiness=0.0

## Top 10 campos para schema/map_to_db_schema
- `tipo_oportunidade`: 43
- `setor_economico`: 43
- `setor_estrategico`: 43
- `area`: 34
- `area_tecnologica`: 10
- `publico_alvo`: 10
- `area_cientifica`: 5

## Recomendações prioritárias
1. Reduzir perdas em `_strip_payload` para campos críticos vindos de `extras`.
2. Garantir preservação de `pdf_url` e `documentos` no payload final.
3. Revisar rota de `perfil_ideal`/classificação para não sumir no payload.
4. Identificar colunas candidatas no schema pelos tops de `audit_loader_only_schema_gaps.json`.
5. Mitigar risco de sobrescrita por vazios nos loaders com mais alertas.