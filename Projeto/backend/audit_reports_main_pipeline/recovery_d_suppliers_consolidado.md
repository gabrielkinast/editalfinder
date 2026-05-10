# Recovery D — Supplier Portals (GD / LM / BAE)

## 1. Resumo executivo

Recovery D cobre apenas general_dynamics_suppliers, lockheed_martin_suppliers e bae_systems_suppliers para reduzir suspeito_ativo_true relacionado a portais corporativos. Inclui filtro opcional Recovery D nos crawlers, harvest HICX sem index de login, calibracao taxonomy local tipo oportunidade_fornecedor e validacao incompleta/acesso_limitado. Dry-run apenas — sem apply, schema ou Supabase.

## 2. Contexto

Após Recoveries A, B/B.1 e C a validação global mantém critical_errors=0. O backlog para radar é especialmente `suspeito_ativo_true` quando status suspeito coexiste com ativo=true. Esta onda isola apenas três crawlers europeus/americanos de suppliers; outras fontes permanecem intocadas.

## 3. O que foi alterado

- `supplier_recovery_d_filter=True` nos três `main_*_suppliers.py`.
- `bae_harvest`: removida página HICX `app/index.html`.
- `merge_bae_items(portal_items, allowed)` corrigido em `main_bae_systems_suppliers.py`.
- Lockheed: somente `suppliers.html` como listagem.
- `taxonomy_filtros`: novas funções `calibrate_general_dynamics_suppliers_extras`, `calibrate_lockheed_martin_suppliers_extras`, `calibrate_bae_systems_suppliers_extras` com núcleo `_calibrate_supplier_portal_recovery_d_core`.

## 4. Resultado operacional

| Métrica | Antes | Depois | Variação | Interpretação |
|---|---:|---:|---:|---|
| `mapping_errors_total` | — | 0 | 0 alvo | Nenhum erro de payload/maping no loader dry-run |
| `critical_empty_items_total` | — | 0 | 0 alvo | Todos os registros preservam campos críticos mínimos |
| `faq_em_urls` | — | 0 (heurística substring /faq|/help nos itens standardized) | — | Nenhum URL de FAQ coletado após filtros |
| `titulo_com_menos_de_9_chars` | — | 3 (SUPPLiERS caps, revisão típulos) | — | Radar pode marcar ruído; candidatos deactivate listados aparte |

## 5. Resultado por fonte

| Fonte | Antes | Depois | Ganho | Observação |
|---|---:|---:|---:|---|
| general_dynamics_suppliers | 11 linhas crawler | 7 standardized | PDF código conduta/scorecard e ruídos filtrados | Mentor-Protégé e secções estruturais mantidas como conteudo publico. |
| lockheed_martin_suppliers | ~20 crawler | 19 standardized | Sem seed business-areas | Capacidades ainda presentes através de links no hub suppliers. |
| bae_systems_suppliers | 3 crawler (login index) | 2 standardized | Index login removido do harvest fixo | discovery-login permanece como supplier registration público. |

## 6. Interpretação

Ver bloco `interpretacao` em `padrao_documentacao_onda` no JSON consolidado.

## 7. Riscos e limitações

Capacidades LM ainda escapam via links do hub; próximo passo pode ser deny `/capabilities/` condicionado.

## 8. Decisão recomendada

Manter aplicacao pendente até revisão humana dos candidatos ativo=false (alta/med.) — Dry-run com mapping_errors=0 e critical_empty=0; desativação apenas documentada aqui.

## 9. Próximos passos

1. Avaliar deny de path /capabilities/ para links oriundos de suppliers LM.
2. Aplicar retransformação + loader (--apply) apenas após QA dos candidatos.
3. Rodar nova post_daily_validation após atualização staging.

## 10. Evidências técnicas

Ver `evidencias_tecnicas` no JSON `recovery_d_suppliers_consolidado.json`.
