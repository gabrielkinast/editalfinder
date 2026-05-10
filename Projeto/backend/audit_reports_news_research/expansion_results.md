# Resultados da expansão news/research (dry-run, sem apply)

**Gerado:** 2026-05-05 (após atualização de `config/news_research_sources.json` e filtros opcionais no crawl).

## Comandos executados

1. `python scripts/crawl_news_research_sources.py`
2. `python scripts/audit_news_research_pipeline.py`
3. `python scripts/dry_run_news_research_loader.py`

**Apply:** não executado.

## Totais globais

| Métrica | Valor |
|--------|------:|
| Itens standardized (crawl) | 158 |
| Dry-run depois dedupe | 158 |
| Deduplicados (cross-fonte neste ciclo) | 0 |
| Simulado `public.noticia` | 127 |
| Simulado `public.pesquisa` | 30 |
| `review_for_edital` | 0 |
| `rejected_noise` | 1 |
| Sem `data_publicacao` (auditoria) | 17 |
| `missing_summary` (dry-run) | 42 |

## Por fonte — cobertura e “limpeza”

### `nasa_news` (status: **ready_for_wave**)

- **Crawl:** 95 itens (dedupe por link no crawl).
- **Auditoria:** 95 dentro de 12 meses; 0 sem data.
- **Dry-run:** 78 → notícia, 17 → pesquisa.
- **Leitura:** melhor candidata à **Onda 2** em staging após amostragem humana; volume alto com baixo ruído de data.

### `darpa_news` (status: **needs_cleanup**)

- **Crawl:** 10 itens (RSS apenas).
- **Auditoria:** 10 com data em 12 meses.
- **Dry-run:** 9 notícia, 1 pesquisa.
- **Leitura:** boa **segunda prioridade** pós-NASA: volume pequeno mas estável após remoção do hub HTML.

### `iaea_news_publications` (status: **active_candidate**)

- **Crawl:** 50 itens (feeds RSS oficiais).
- **Auditoria:** 35 em 12 meses; 15 sem data.
- **Dry-run:** 40 notícia, 10 pesquisa; **muitos** `missing_summary` (feed/publicação com descrição curta).
- **Leitura:** candidata à **Onda 4**, mas staging incremental só com filtro de qualidade (ex.: só `validacao_status=valido`) ou mais `page_enrich` — ver `expansion_plan.md`.

### `darpa_opportunities_research` (status: **active_candidate**)

- **Crawl:** 1 item no ciclo atual.
- **Dry-run:** 1 `rejected_noise` (não passou nos critérios de destino).
- **Leitura:** manter **separado** de notícias; quando o RSS tiver volume, usar **revisão manual** para BAA/RFI/RFP → `review_for_edital` (nunca rota automática para `public.edital`).

### `eurekalert_science_filtered` (status: **noisy**)

- **Crawl:** 2 itens (browse + filtros agressivos).
- **Auditoria:** 2 sem data; ruído temporal alto.
- **Leitura:** **não** priorizar staging até haver datas confiáveis ou feed alternativo alinhado à política do EurekAlert.

## Recomendação final

| Prioridade | Fonte | Ação sugerida |
|------------|--------|----------------|
| 1 | `nasa_news` | Pronta para **Onda 2** em staging (amostragem + apply controlado do loader). |
| 2 | `darpa_news` | Pronta para **lote pequeno** em staging após NASA. |
| 3 | `iaea_news_publications` | Staging **só** com subset de alta qualidade ou após melhorar resumo/data. |
| — | `darpa_opportunities_research` | Monitorar RSS; volume atual insuficiente para onda automática. |
| — | `eurekalert_science_filtered` | Manter em modo experimental (Onda 5). |

Ficheiro JSON detalhado: `expansion_results.json`.
