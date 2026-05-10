# Plano de deduplicação (dry-run)

- Grupos avaliados: **50**
- merge_seguro: **13**
- revisar_manual: **37**
- manter_todos: **0**

## Top 10 grupos

- pdf_url | qtd=20 | canônico=761 | recomendação=revisar_manual | confiança=baixa
- pdf_url | qtd=14 | canônico=520 | recomendação=revisar_manual | confiança=baixa
- pdf_url | qtd=12 | canônico=666 | recomendação=revisar_manual | confiança=baixa
- pdf_url | qtd=11 | canônico=328 | recomendação=revisar_manual | confiança=baixa
- pdf_url | qtd=11 | canônico=727 | recomendação=revisar_manual | confiança=baixa
- pdf_url | qtd=8 | canônico=558 | recomendação=revisar_manual | confiança=baixa
- pdf_url | qtd=6 | canônico=240 | recomendação=revisar_manual | confiança=baixa
- hash_deduplicacao | qtd=5 | canônico=230 | recomendação=merge_seguro | confiança=alta
- hash_deduplicacao | qtd=5 | canônico=568 | recomendação=merge_seguro | confiança=alta
- fonte_titulo_normalizado | qtd=5 | canônico=230 | recomendação=revisar_manual | confiança=média

## Proposta futura (não executada)

- Mesclar `extras` por merge profundo.
- Mesclar `extras.documentos` por URL única.
- Preservar IDs antigos em `extras.merged_from_ids`.
- Registrar eventos em `edital_historico`.
- Em etapa futura, marcar duplicatas como `ativo=false` sem delete.