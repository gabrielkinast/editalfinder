# Fornecedores & Investimentos — desenho backend (Recovery D)

## Objetivo

Os crawlers **general_dynamics_suppliers**, **lockheed_martin_suppliers** e **bae_systems_suppliers** produzem conteúdo de **portal de fornecedores**, **cadastro**, **hub** e **documentação** — não devem competir com o **Radar de Fomento** como edital forte.

## Extras canónicos (JSON `extras`)

| Chave | Valor típico |
|--------|----------------|
| `frontend_section` | `fornecedores` |
| `mostrar_no_radar` | `false` |
| `mostrar_em_fornecedores` | `true` |
| `mostrar_em_investimentos` | `false` |
| `portal_tipo` | `registration`, `hub`, `access_limited`, `documentation`, `supplier_resource`, `procurement` |
| `supplier_portal` | `true` |
| `recovery_d1_decisao_qa` / `motivo` / `acao_recomendada` | Rastreio QA D.1 |

## Tipos (`tipo_oportunidade` / `tipo_recurso`)

Lista canónica e constante `TIPO_OPORTUNIDADE_FORNECEDORES_INVESTIMENTOS` em `CORE/taxonomy_filtros.py`.

- **Destaque fornecedor:** `supplier_registration`, `supplier_portal`, `procurement_portal`, `programa_agregado`, `oportunidade_fornecedor`.
- **Documentação / apoio:** `documentacao_fornecedor` + `tipo_recurso` `recurso_fornecedor`.

## Qualidade

`CORE/item_quality.py` aplica teto de score para `documentacao_fornecedor` / `recovery_d_doc_supplier` e para hubs (`recovery_d1_hub_supplier`), para não inflar `qualidade_dado`.

## SQL (proposta)

Ficheiro: `docs/sql/VW_FORNECEDORES_FRONT_PROPOSTA.sql` — **não executado** nesta fase.

## Vista «Investimentos» (futuro)

Quando houver dados com `mostrar_em_investimentos` ou tipos `investment_portal` / `corporate_venture`, definir `public.vw_investimentos_front` de forma análoga. Ver `fornecedores_investimentos_backend_design.json`.
