# Diagnóstico SAM.gov — lote 2

**Data:** 2026-05-02  

## Respostas (checklist das 15 perguntas)

1. **O crawler roda?** Sim. `python sam_gov/main_sam_gov.py` executa sem erro; sem `SAM_GOV_API_KEY` imprime aviso e grava lista vazia (sem fallback de hub).
2. **Existe output bruto?** Sim: `sam_gov/outputs/sam_gov_editais.json` (pode ser `[]` se não houver chave ou se a API não devolver linhas após filtros).
3. **Quantos itens brutos?** Historicamente 2 (hub SAM + página DoD via fallback). Após a última execução documentada aqui: **0** (sem chave).
4. **Quantos transformam?** Com o bruto antigo: **0** (ver `audit_reports_retransform/readiness_rows.json`, `transformados: 0`). Com bruto vazio: **0**.
5. **Quantos rejeitados?** Com 2 itens antigos: **2**. Com bruto vazio: **0**.
6. **Motivos de rejeição?** Itens não eram notices (`/opp/<id>`), e sim páginas índice/institucionais; falta de evidência de oportunidade concreta compatível com o pipeline.
7. **Natureza dos links?** Hub `sam.gov/content/opportunities`, página genérica de programas `business.defense.gov/Programs/` — não são *notice details* da API.
8. **Método?** **API** GET Opportunities v2 (GSA), não RSS; o legado misturava HTML de portal.
9. **Paginação?** Sim na API (`offset`/`limit`), limitada pela política (`max_distinct_api_calls`, `max_items_output`).
10. **Filtros por data?** Sim: `postedFrom` / `postedTo` a partir de `posted_days_back`.
11. **NAICS / PSC / keywords?** NAICS/PSC entram no blob de texto do item; keywords positivas/negativas e agências na política JSON; queries de título e `ptype` opcionais no `main_sam_gov.py`.
12. **Documentos / anexos?** Mapeados a partir de `resourceLinks` quando presentes na resposta da API.
13. **Relevantes ou genéricos?** O bruto legado era **muito genérico**. O novo fluxo só grava notices que passam `passes_acceptance` e relevância mínima.
14. **Por que bloqueada?** `sam_gov` permanece em `blocked` em `config/source_readiness.json` por histórico de **0 transformados** com ruído de hub e risco ao loader (`gate_agressivo` nos relatórios antigos).
15. **Crawler, escopo, gate, taxonomia, duplicata, acesso, ruído?** Predominou **crawler/escopo legado + ruído**; **acesso** ao seed público está OK na auditoria de acesso; **taxonomia** foi estendida com `calibrate_sam_gov_extras`; **gate** global não foi alterado (conforme pedido).

## Política e código

- Escopo: `config/sam_gov_scope_policy.json`.
- Filtro e mapeamento API → item: `sam_gov/scope_policy.py`.
- Coleta: `sam_gov/main_sam_gov.py` (chave `SAM_GOV_API_KEY`, `SAM_API_KEY` ou `DATA_GOV_API_KEY`).
- Pós-transformação: `CORE/taxonomy_filtros.py` — `calibrate_sam_gov_extras`; heurística de defesa **não** sobrescreve `sam_gov` (`CORE/transformer.py`).
- `official_link_only`: SAM.gov **não** está na allowlist; comentário acrescentado em `CORE/official_link_only.py`.

## Pipeline local (esta sessão)

| Etapa | Pasta / ficheiro |
|--------|------------------|
| Retransformação dry-run | `audit_reports_blocked_sources/lote2_fix_sam_gov/` |
| Auditoria semântica | `audit_reports_blocked_sources/lote2_fix_sam_gov_semantic/` |
| Auditoria de documentos | `audit_reports_blocked_sources/lote2_fix_sam_gov_docs/` |
| Acesso | `audit_reports_access/` (regenerado com `--sources sam_gov`) |

## Readiness (recomendação apenas em relatório)

**`needs_manual_review`:** implementação alinhada ao escopo pedido, mas falta validação com **chave API** e amostra real de notices (≤25). Após validação manual, avaliar `ready_with_notes` se a amostra for estável, técnica e com baixo ruído. **Não** promover a `ready`/`ready_with_notes` só com base neste dry-run vazio.

Não foram executados: apply ao loader, Supabase, migrations, alteração ao opportunity gate global.
