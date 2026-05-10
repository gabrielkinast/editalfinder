# Auditoria loader-only

- Ficheiros standardized processados: **94**
- Itens analisados (amostra): **1093**
- Itens com alerta de payload: **1093**

## Top 10 perdas de dados (campos)
- `programa`: 1067
- `acao`: 1041
- `tipo_recurso`: 693
- `regiao`: 579
- `temas`: 155
- `valor`: 26
- `publico_alvo`: 24
- `data_publicacao`: 3
- `contrapartida`: 1

## Top 10 fontes com maior problema no payload
- `china_mofcom_tendering` (china_mofcom_tendering_standardized.json): problemas=50, amostra=50, readiness=0.0
- `european_defence_fund` (european_defence_fund_standardized.json): problemas=50, amostra=50, readiness=0.0
- `fappr` (fappr_standardized.json): problemas=50, amostra=50, readiness=0.0
- `grants_gov` (grants_gov_standardized.json): problemas=50, amostra=50, readiness=0.0
- `japan_jsps` (japan_jsps_standardized.json): problemas=50, amostra=50, readiness=0.0
- `china_cas` (china_cas_standardized.json): problemas=35, amostra=35, readiness=0.0
- `darpa_opportunities` (darpa_opportunities_standardized.json): problemas=34, amostra=34, readiness=0.0
- `japan_jaea` (japan_jaea_standardized.json): problemas=30, amostra=30, readiness=0.0
- `japan_kakenhi` (japan_kakenhi_standardized.json): problemas=30, amostra=30, readiness=0.0
- `japan_kek` (japan_kek_standardized.json): problemas=30, amostra=30, readiness=0.0

## Top 10 campos para schema/map_to_db_schema
- `tipo_oportunidade`: 1093
- `setor_estrategico`: 1093
- `setor_economico`: 705
- `area_tecnologica`: 605
- `area`: 580
- `documentos`: 424
- `area_cientifica`: 342
- `publico_alvo`: 24
- `validacao_status`: 14
- `qualidade_dado`: 14

## Recomendações prioritárias
1. Reduzir perdas em `_strip_payload` para campos críticos vindos de `extras`.
2. Garantir preservação de `pdf_url` e `documentos` no payload final.
3. Revisar rota de `perfil_ideal`/classificação para não sumir no payload.
4. Identificar colunas candidatas no schema pelos tops de `audit_loader_only_schema_gaps.json`.
5. Mitigar risco de sobrescrita por vazios nos loaders com mais alertas.