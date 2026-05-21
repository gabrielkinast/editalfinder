# BRISA News — dry-run (Notícias Estratégicas)

- **Execução:** 2026-05-17T02:10:38Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `brisa_news` — BRISA

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| Listagem | https://brisabr.com.br/news/ |
| RSS | `https://brisabr.com.br/news/feed/` |
| robots.txt | Disallow: /wp-admin/ (resto permitido) |
| CMS | WordPress |
| Canal | RSS 2.0 seção News; HTML /news/ espelha os mesmos ~4 posts |
| Data | pubDate RSS + enrich meta opcional |
| Autor | dc:creator (ex.: Pamela Souza) |
| Imagem | og:image no enrich (budget limitado) |
| Copyright | Apenas resumo RSS/meta; sem corpo integral |
| Concursos | Secção /news/ apenas — /artigos/ excluído |

## Resultados

- **Standardized:** 4
- **Na janela 12m:** 0
- **Enrich páginas:** 4

### Validação

- `valido`: **4**

## Warnings

- {'tipo': 'volume_baixo_feed', 'detalhe': 'O feed /news/feed/ publica poucos itens (típico 4); não usar feed global sem filtro /news/.'}
- {'tipo': 'fora_janela_12m', 'count': 4, 'detalhe': 'Itens mantidos com data_publicacao; ver within_window no meta.'}

## Artefatos

- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\brisa_news_dryrun\standardized\brisa_news_standardized.json`
- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\brisa_news_dryrun\raw\brisa_news_raw.json`

Ver [STRATEGIC_NEWS_RESEARCH_SOURCES.md](../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md).
