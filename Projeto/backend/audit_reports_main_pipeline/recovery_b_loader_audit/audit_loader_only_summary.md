# Auditoria loader-only

## Interpretação
- Isto **não** executa crawler nem transformer: só mede **standardized → normalizar → map_to_db_schema → _strip_payload**.
- Compare com a auditoria completa (JSON bruto) para separar perdas do **transformer** vs **loader/schema**.

- Ficheiros standardized processados: **3**
- Itens analisados (amostra): **32**
- Itens com alerta de payload: **32**

## Top 10 perdas de dados (campos)
- `content_type`: 32
- `acao`: 25
- `programa`: 25
- `temas`: 13
- `valor`: 8
- `regiao`: 7

## Top 10 fontes com maior problema no payload
- `amazul` (amazul_standardized.json): problemas=20, amostra=20, readiness=0.0
- `ambev` (ambev_standardized.json): problemas=7, amostra=7, readiness=0.0
- `badesul` (badesul_standardized.json): problemas=5, amostra=5, readiness=0.0

## Top 10 campos para schema/map_to_db_schema

## Recomendações prioritárias
1. Reduzir perdas em `_strip_payload` para campos críticos vindos de `extras`.
2. Garantir preservação de `pdf_url` e `documentos` no payload final.
3. Revisar rota de `perfil_ideal`/classificação para não sumir no payload.
4. Identificar colunas candidatas no schema pelos tops de `audit_loader_only_schema_gaps.json`.
5. Mitigar risco de sobrescrita por vazios nos loaders com mais alertas.