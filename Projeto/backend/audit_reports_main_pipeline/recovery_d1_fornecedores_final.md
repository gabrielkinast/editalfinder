# Recovery D — Fornecedores & Investimentos (final)

## 1. Resumo executivo

Recovery D finaliza marcações para a secção produto «Fornecedores & Investimentos»: extras de roteamento, tipos supplier/documentação, cap de qualidade para não simular edital forte. Apply e Supabase ficam pendentes.

## 2. Contexto

Ver `fornecedores_investimentos_backend_design.md` e constantes em `taxonomy_filtros.py`.

## 3. O que foi alterado

- `TIPO_OPORTUNIDADE_FORNECEDORES_INVESTIMENTOS` e conjuntos de títulos D.1.
- `_apply_recovery_d_fornecedores_investimentos_routing` + QA metadata.
- `item_quality`: cap documentação / hub.
- Proposta SQL `docs/sql/VW_FORNECEDORES_FRONT_PROPOSTA.sql`.

## 4. Resultado operacional

| Métrica | Antes | Depois | Variação | Interpretação |
|---|---:|---:|---:|---|
| `itens_total` | — | 26 | — |  |
| `loader_would_upsert` | — | 26 | — |  |
| `mapping_errors_total` | — | 0 | — |  |
| `critical_empty_items_total` | — | 0 | — |  |
| `faq_help_heuristic` | — | 0 | — |  |
| `login_isolado` | — | 0 | — |  |
| `validacao_suspeito_top` | — | 0 | — |  |
| `setor_estrategico_gt3` | — | 0 | — |  |
| `frontend_section_fornecedores` | — | 26 | — |  |
| `mostrar_no_radar_false` | — | 26 | — |  |
| `mostrar_em_fornecedores_true` | — | 26 | — |  |
| `mostrar_em_investimentos_false` | — | 26 | — |  |
| `portal_tipo_preenchido` | — | 26 | — |  |
| `documentacao_com_mostrar_radar_true` | — | 0 | — |  |
| `todos_checks_ok` | — | True | — | Gate QA automático Recovery D final |

## 5. Resultado por fonte

Ver distribuições em `metricas_antes_depois` no JSON.

## 6. Interpretação

Ver `padrao_documentacao_onda.interpretacao` no JSON.

## 7. Riscos e limitações

Consumidores legacy do payload podem assumir tipo_oportunidade antigo — rever API pública.
View SQL requer validação DBA e índices em extras.

## 8. Decisão recomendada

Opção 1 (preferida): aplicar os 26 itens em staging com extras de fornecedores e mostrar_no_radar=false.

## 9. Próximos passos

1. QA rápido no staging após apply (quando autorizado).
2. Implementar rota UI «Fornecedores» filtrando extras.frontend_section.
3. Planejar vw_investimentos_front quando existirem dados.

## 10. Evidências técnicas

JSON `recovery_d1_fornecedores_final.json` → `evidencias_tecnicas`.
