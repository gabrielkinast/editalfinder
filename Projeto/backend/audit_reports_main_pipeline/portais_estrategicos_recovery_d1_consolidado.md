# Portais estratégicos — primeira carga consolidada (Recovery D.1 Fornecedores)

**Ambiente:** staging  
**Tabela:** `public.portal_estrategico` (não `public.edital`)  
**Data de referência dos relatórios:** 2026-05-10  

Este documento consolida a primeira carga de **Portais estratégicos / Fornecedores**, com base nos artefactos de apply, validação pós-carga, desenho backend e relatório Recovery D.1 final. **Não foi executado novo apply** na elaboração deste consolidado.

---

## 1. Fontes e volumes

| Fonte | Itens (would_upsert) |
|--------|----------------------|
| `general_dynamics_suppliers` | 6 |
| `lockheed_martin_suppliers` | 18 |
| `bae_systems_suppliers` | 2 |
| **Total** | **26** |

Ficheiros de entrada (standardized):  
`audit_reports_main_pipeline/recovery_d1_fornecedores_final/standardized/`

---

## 2. Apply (staging)

Fonte: `portais_estrategicos_recovery_d1_apply/load_portais_estrategicos_summary.json`

| Métrica | Valor |
|---------|--------|
| Modo | `apply` |
| `apply_status` | `applied` |
| Total lido | 26 |
| Inseridos | **25** |
| Atualizados | **1** |
| `upserted_total` | **26** |
| Erros de validação / mapa / apply | 0 |

Distribuição `portal_tipo` no lote: `documentation` 11, `supplier_resource` 7, `procurement` 3, `hub` 2, `registration` 2, `access_limited` 1.  
`validacao_status`: 24 `incompleto`, 2 `acesso_limitado`.  
Todos com `frontend_section=fornecedores`, `mostrar_no_radar=false`, `mostrar_em_fornecedores=true`.

---

## 3. Validação pós-carga e `vw_fornecedores_front`

Fonte: `portais_estrategicos_recovery_d1_validation/validate_portais_estrategicos_after_load.json`

| Verificação | Resultado |
|-------------|-----------|
| Links esperados (standardized) | 26 |
| Encontrados em `portal_estrategico` | **26** |
| Encontrados em `vw_fornecedores_front` | **26** |
| Em falta na tabela / na view | **nenhum** |
| Violações de regras por linha | **0** |
| Erro na query à view | **nulo** |
| `status` | **ok** |

Isto confirma que a view usada pelo front de fornecedores está alinhada com os dados carregados.

---

## 4. Por que estes itens foram movidos para `portal_estrategico`

- São **portais corporativos de fornecedores** (páginas de registo, procurement, hubs, documentação, recursos), não editais de fomento com o mesmo perfil semântico e de negócio que `public.edital`.
- O desenho em `fornecedores_investimentos_backend_design.json` fixa o objetivo: **separar** fornecedores/investimentos do **Radar de Fomento (editais fortes)**. A tabela `portal_estrategico` é o destino adequado para a futura área **«Fornecedores & Investimentos» / portais estratégicos**.
- A verificação em `recovery_d1_fornecedores_final.json` (`verificacao_recovery_d_fornecedores`) já tinha fechado o lote com 26 itens, routing coerente e checks de qualidade/mapping a zero antes da carga em staging.

---

## 5. Por que não entram no Radar de Fomento

- O Radar deve privilegiar **oportunidades de financiamento/concurso** acionáveis; estes URLs são **contexto de fornecedor** (programas, ética, CMMC, SBIR como conteúdo institucional, etc.).
- O relatório Recovery D.1 explicita **`mostrar_no_radar=false` em 26/26** e **`documentacao_com_mostrar_radar_true=0`**, para que documentação não suba como “edital forte”.
- Carga feita **apenas** em `portal_estrategico`; **não** houve inserção deste lote em `public.edital`, evitando duplicação semântica no pipeline de fomento.

---

## 6. Como `frontend_section=fornecedores` e `mostrar_no_radar=false` protegem o Radar

1. **`frontend_section=fornecedores`** — Encaminha listagens e APIs de produto para a **secção Fornecedores** (por exemplo consumo via `vw_fornecedores_front`), em vez de misturar com o feed genérico de editais/fomento.
2. **`mostrar_no_radar=false`** — É a **regra explícita de exclusão** do agregador “Radar”: qualquer query do Radar de Fomento deve respeitar esta flag (ou equivalente) para não incluir portais estratégicos.
3. **Em conjunto** — Mesmo que exista código legado pouco sensível a `tipo_oportunidade`, a combinação **secção dedicada + radar desligado** mantém o isolamento entre **fomento** e **fornecedores**.

O design canónico (`extras` / colunas espelhadas) está descrito em `fornecedores_investimentos_backend_design.json` (`frontend_section`, `mostrar_no_radar`, `mostrar_em_fornecedores`, `portal_tipo`, etc.).

---

## 7. Próximos passos para o frontend

1. **Consumir** `vw_fornecedores_front` (ou endpoint que a reproduza) na rota **«Fornecedores & Investimentos»**, sem reutilizar a listagem do Radar sem filtros.
2. **Contrato de UI** — Tratar `portal_tipo` (`registration`, `access_limited`, `documentation`, `supplier_resource`, `procurement`, `hub`) com affordances distintas de “edital”.
3. **Investimentos** — Quando existirem fontes com `mostrar_em_investimentos=true`, seguir a evolução prevista no design (`vw_investimentos_front`, ainda proposta).
4. **QA visual** — Rever em staging títulos longos, links externos e estados `acesso_limitado` para copy e ícones de “acesso restrito”.

---

## 8. Restrições confirmadas nesta consolidação

- Nenhum **novo** apply executado ao gerar este documento.  
- **Schema** e **opportunity_gate global** não foram alterados por esta tarefa.

---

## 9. JSON irmão

Métricas e campos estruturados:  
`audit_reports_main_pipeline/portais_estrategicos_recovery_d1_consolidado.json`
