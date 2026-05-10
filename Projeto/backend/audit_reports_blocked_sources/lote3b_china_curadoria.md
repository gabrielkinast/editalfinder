# Curadoria local — lote 3B China

Gerado em (UTC): 2026-05-02T21:43:02Z (espelhado em `lote3b_china_curadoria.json`).

## Âmbito

- **Curados (bruto JSON):** `china_nsfc`, `china_avic`, `china_university_procurement` via `scripts/apply_lote3b_china_curadoria.py`.
- **Não alterados nesta tarefa:** `china_cnnc`, `china_norinco` (preservação / bloqueio já documentados).
- **Não executado:** loader apply, Supabase, migrations, gate global de oportunidade, atualização automática de `source_readiness.json`.

## Resumo quantitativo

| Fonte | Brutos antes | Brutos depois | Transformados (dry-run) |
|--------|--------------|---------------|---------------------------|
| china_nsfc | 28 | 9 | 9 |
| china_avic | 15 | 1 | 1 |
| china_university_procurement | 6 | 4 | 4 |

**Total bruto curado:** 14 itens → **14 transformados**, 0 rejeitados pelo pipeline neste dry-run (`retransform_summary.json`).

## china_nsfc

- **Removido:** notícias políticas / discursos, reuniões internas de avaliação, supervisão de fundos, fóruns “双清”, notícias de resultados científicos, páginas de sistema (`grants.nsfc` como registo isolado), índices genéricos em inglês e notícias “Funding & Support” sem conteúdo de edital.
- **Mantido com `tipo_oportunidade` explícito:** guias e referências com evidência (`grant`, `chamada_publica`, `funding_opportunity`); preservados `idioma_original`, `titulo_original`; `origem_portal` preenchido quando ausente (`NSFC (nsfc.gov.cn)`).
- **Auditoria semântica:** surgem ainda flags `oportunidade_fomento_sem_fomento` (4 ocorrências no conjunto curado) — revisão de taxonomia/perfil continua recomendada.

## china_avic

- **Removido:** hubs “新闻中心”, páginas institucionais duplicadas (.com / .com.cn), notícia fora de escopo (中储粮), secções genéricas “Military Aviation” em inglês.
- **Mantido:** um único registo — **recrutamento público campus 2026 (纪检监察)**; classificado como **oportunidade RH / `chamada_publica`**, não procurement nem defesa com evidência de objeto militar.
- **Leitura:** o sinal útil é fino; a fonte continua dependente de listagens melhores para oportunidades industriais/procurement.

## china_university_procurement

- **Removido:** página agregadora “科研类通知” (listagem), aviso de **segurança de laboratório** (sem concurso de fundos).
- **Mantido:** quatro avisos USTC alinhados a **fundos/chamadas** (国家重点研发计划 / 霍英东 / NSFC SDG / cooperação internacional); `tipo_oportunidade` ajustado para `grant` ou `funding_opportunity` com evidência no texto; removida sobre-classificação **nuclear** sem suporte textual; datas `1966-01-01` / `1991-01-01` (artefactos de parsing) limpas para `null` onde aplicável; `origem_portal` = `USTC (ustc.edu.cn)`; **documentos** existentes preservados nos registos.
- **Tsinghua / PKU:** continuam registadas como **falha parcial de acesso ou listagem** no crawler (fora do JSON curado).

## Pipelines executados

1. `python scripts/retransform_all.py --sources china_nsfc,china_avic,china_university_procurement --dry-run --output-dir audit_reports_blocked_sources/lote3b_china_curated`
2. `python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote3b_china_curated/standardized --output-dir audit_reports_blocked_sources/lote3b_china_curated_semantic`
3. `python scripts/audit_docs_pipeline.py --sources china_nsfc,china_avic,china_university_procurement --output-dir audit_reports_blocked_sources/lote3b_china_curated_docs`

## Recomendação final de readiness (manual)

| Fonte | Recomendação |
|--------|----------------|
| **china_nsfc** | **ready_with_notes** — conjunto alinhado a editais/guias; rever flags semânticas e evolução das páginas em inglês. |
| **china_avic** | **needs_manual_review** — um único item útil (RH); sem base para “ready” até haver listagens de procurement ou oportunidades com objeto explícito. |
| **china_university_procurement** | **ready_with_notes** — USTC limpo para o subconjunto curado; cobertura multi-campus incompleta. |
| **china_cnnc** | **blocked** — falha de listagem/rede; sem curadoria de bruto novo. |
| **china_norinco** | **needs_manual_review** — bruto legado fraco; sem mudança nesta tarefa. |

Detalhe estruturado (incl. `retransform_por_fonte` e resumo semântico): `audit_reports_blocked_sources/lote3b_china_curadoria.json`.
