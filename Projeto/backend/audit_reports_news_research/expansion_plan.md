# Plano de expansão — módulo news/research (EditalFinder)

## Objetivo

Aumentar a cobertura de notícias e conteúdos de pesquisa **por ondas**, com **qualidade** e **fronteiras claras** em relação ao pipeline de editais.

## O que não fazer (governança)

- Não enviar itens deste módulo para **`public.edital`**.
- Não promover **`review_for_edital`** automaticamente para edital.
- Não fazer **apply** sem **dry-run** e validação explícita.
- Não contornar **bloqueios** (robots, Cloudflare, políticas de fonte).
- Não fazer **scraping agressivo** nem varrer site inteiro: apenas `seed_urls` declarados e, no código atual, descoberta **limitada** de feeds RSS a partir de páginas hub.
- Não relaxar filtros de **data** e **resumo** (enriquecimento só a partir de HTML/RSS real).

## Onda 2 — NASA ampliada

- **Feeds oficiais** adicionais (verificados HTTP 200): notícias gerais, educação, aeronáutica, image of the day, *Technology*, *Earth*, *Missions*, *News releases*, *NASA Science* (`science.nasa.gov/feed/`).
- **Janela:** últimos **12 meses** (`time_window_months`).
- **Volume:** `max_items` com teto seguro (**95**) agregando todos os seeds; **dedupe por link** no crawl.
- **Qualidade:** manter parsing de data do RSS; `page_enrich_max` maior **só** na NASA para preencher resumo/data quando o feed vier pobre.

## Onda 3 — DARPA

- **`darpa_news`:** limpar seeds — **apenas** `https://www.darpa.mil/rss/news.xml` (remover hub HTML que gerava ruído e datas fracas).
- **`darpa_opportunities_research`:** manter **separado**; apenas `opportunities.xml`.
- **Roteamento:** itens com solicitation / **BAA** / **RFI** / **RFP** fortes → **`review_for_edital`** no dry-run (`dry_run_news_research_loader.py`), **não** para `public.noticia`. Notícias técnicas reais → `public.noticia`. Programas/relatórios sem chamada aberta → `public.pesquisa` (heurística + revisão pontual).

## Onda 4 — IAEA

- **Seeds corrigidos** para RSS estáveis: `https://www.iaea.org/feeds/topnews`, `/feeds/news`, `/feeds/publications` (evitar homepage sujeita a 403 Cloudflare em ambientes automatizados).
- **Temas:** nuclear, energia, segurança nuclear, aplicações nucleares.
- **Janelas:** 12 meses na config atual; **até 24 meses** para publicações técnicas pode ser uma **fase seguinte** (fonte duplicada filtrada ou parâmetro futuro no crawl).

## Onda 5 — EurekAlert filtrado

- **Volume baixo:** `max_items` **12** por execução.
- **Filtros no crawl:** `require_any_keyword` (aerospace, nuclear, quantum, …) e `exclude_keywords` para reduzir medicina genérica.
- **Status:** `noisy` até a taxa de ruído estabilizar; ajustar listas com base em `audit_summary.json`.

## Configuração

- Ficheiro: `config/news_research_sources.json`
- Campo **`status`** por fonte: `ready_for_wave` | `active_candidate` | `needs_cleanup` | `blocked_access` | `noisy`
- Bloco opcional **`governance`** documenta regras (não é consumido pelo loader legado).

## Pipeline (sem apply)

```text
python scripts/crawl_news_research_sources.py
python scripts/audit_news_research_pipeline.py
python scripts/dry_run_news_research_loader.py
```

Resultados agregados: `expansion_results.md` / `expansion_results.json` (gerados após esta configuração).
