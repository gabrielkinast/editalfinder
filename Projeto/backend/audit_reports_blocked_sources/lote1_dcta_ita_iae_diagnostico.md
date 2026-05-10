# Lote 1 — Diagnóstico DCTA / ITA / IAE (`dcta_ita_iae`)

## 1. Bruto atual

| Métrica | Valor |
|--------|------:|
| Itens em `dcta_ita_iae/outputs/dcta_ita_iae_editais.json` | **0** |
| CSV derivado | removido quando a lista ficou vazia |

O crawler **deixou de gravar** o fallback `fallback_public_index` na raiz `https://www.gov.br/dcta/pt-br` (página institucional, não oportunidade).

## 2. Histórico (antes deste lote)

| Métrica | Valor |
|--------|------:|
| Itens brutos | **1** |
| Transformados | **0** |
| Rejeitados | **1** |

- **Conteúdo:** título genérico «DCTA/ITA/IAE - Página de Oportunidades», link = raiz DCTA, `metodo_extracao: fallback_public_index`.
- **Tipo de link:** índice institucional / menu de entrada — **não** edital, licitação nem chamada concreta.
- **Motivo de rejeição no transform:** **opportunity_gate** (pontuação mínima / oportunidade não evidenciada). O módulo global do gate **não** foi alterado.

## 3. Classificação de tipos (URLs / conteúdo esperado nesta fonte)

| Tipo | Notas |
|------|--------|
| Edital académico | Mestrado/doutorado, stricto sensu, seleção de ingresso, bolsas. |
| Concurso / processo seletivo | Concurso público, vagas, provas — só se o projeto aceitar este tipo de oportunidade. |
| Chamada pública / fomento | Chamamento, P&D, linhas de pesquisa. |
| Licitação / compra pública | Pregão, licitação, UASG, modalidade, contratação. |
| Notícia / página genérica / contato | **Excluídos** no crawler (`avoid_keywords`, exclusões de URL, `link_path_min_depth`). |

## 4. Regra de escopo (resumo)

- **Entram:** licitações/compras; chamadas e editais com objeto; editais académicos reais.
- **Só com decisão de produto:** concursos / processos seletivos de emprego.
- **Não entram:** notícia pura; página institucional genérica; contacto/menu.

## 5. Alterações locais feitas

- **`dcta_ita_iae/main_dcta_ita_iae.py`:** listagens em `.../chamamentos-e-licitacoes` e `.../editais` por órgão; filtros de URL e profundidade; **sem** fallback; **sem** forçar `setor_estrategico` / `tipo_oportunidade` / áreas no config.
- **`CORE/transformer.py`:** `_dcta_ita_iae_hub_only` + `_dcta_ita_iae_soft_continue` (relax pontual só para `gov.br` DCTA/ITA/IAE com evidência, **não** em hubs); `dcta_ita_iae` fora de `build_defense_extras`.
- **`CORE/taxonomy_filtros.py`:** `calibrate_dcta_ita_iae_extras` — `tipo_oportunidade` com evidência; `setor_estrategico` defesa/aeroespacial só com contexto; `area_tecnologica` aeroespacial só com evidência; perfis fornecedor vs académico vs candidatos.

## 6. Retransformação e auditorias

- **Dry-run:** `audit_reports_blocked_sources/lote1_fix_dcta_ita_iae/` — ver `retransform_summary.json` (0 brutos / 0 transformados / 0 rejeitados).
- **Semântica:** `audit_reports_blocked_sources/lote1_fix_dcta_ita_iae_semantic/`.
- **Documentos:** `audit_reports_blocked_sources/lote1_fix_dcta_ita_iae_docs/`.

Com bruto vazio, as auditorias refletem **zero** itens (esperado).

## 7. Exemplos (`lote1_dcta_ita_iae_examples.json`)

Inclui descrição do **legado** (fallback) e **dois sintéticos** validados com `transform_generic` (licitação na ITA; edital académico no DCTA) — não estão guardados em `outputs/`.

## 8. Readiness recomendado

| Valor | **needs_manual_review** |
|--------|-------------------------|
| Manter **blocked** no loader | Sim, até haver brutos reais de qualidade após `python dcta_ita_iae/main_dcta_ita_iae.py`. |

**Não** recomendado `ready` / `ready_with_notes` sem dados no `standardized`.

**Não** foi atualizado `source_readiness.json` / `readiness_for_loader.json` nesta tarefa. **Não** foi executado loader apply nem migrations.

Detalhe em JSON: `lote1_dcta_ita_iae_diagnostico.json`.
