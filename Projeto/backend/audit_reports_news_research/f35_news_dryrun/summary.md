# F-35 News & Features — dry-run (Notícias Estratégicas internacional)

- **Execução:** 2026-05-18T15:12:18Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `f35_news` — F-35 News & Features

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| Portal | https://www.f35.com |
| Hub | `https://www.f35.com/f35/news-and-features.html` |
| Feed JSON | `https://www.f35.com/content/lockheed-martin/data/feeds/f35feed.json` |
| RSS | não disponível (listagem via JSON AEM + Algolia no browser) |
| robots.txt | https://www.f35.com/robots.txt — Allow paths regionais; sem Disallow em /f35/ |
| CMS | Adobe AEM (Lockheed Martin F-35) |
| Listagem | JSON estático f35feed.json (data-path no hub); hub renderizado com Algolia InstantSearch |
| Data | campo Date (RFC822, ex. Wed, 13 May 2026 … MDT) |
| Imagem | Thumbnail Image no feed (absolutizada para f35.com) |
| Copyright | Apenas Description do feed; enrich opcional og:description; sem corpo integral |

## Classificação

- `tipo_conteudo`: noticia
- `fonte`: F-35
- `eixo_estrategico`: aeroespacial, defesa, aviação militar, indústria estratégica (heurística)

## Resultados

- **Standardized:** 10
- **Na janela 12m:** 10
- **Enrich páginas:** 0

### Validação

- `valido`: **10**

## Artefatos

- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\f35_news_dryrun\standardized\f35_news_standardized.json`
- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\f35_news_dryrun\standardized\exemplos.json`

Ver também [STRATEGIC_NEWS_RESEARCH_SOURCES.md](../../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md).
