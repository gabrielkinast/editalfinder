# DefesaNet — dry-run (Notícias Estratégicas)

- **Execução:** 2026-05-17T01:55:27Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `defesanet` — DefesaNet

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| Portal | https://www.defesanet.com.br/ |
| RSS | `https://www.defesanet.com.br/?feed=rss2` |
| robots.txt | User-agent: * / Disallow: (vazio) — Yoast |
| CMS | WordPress |
| Listagem | RSS 2.0 (primário); seções no path (/terrestre, /vant, /naval, …) |
| Data | pubDate RSS + enrich meta/JSON-LD opcional |
| Autor | dc:creator no RSS (ex.: Ricardo Fan) |
| Imagem | og:image no enrich de página (budget limitado) |
| Copyright | Apenas resumo RSS/HTML meta; sem corpo integral do artigo |

## Resultados

- **Standardized:** 10
- **Na janela 12m:** 10
- **Enrich páginas:** 8
- **Descartados pós-enrich:** 0

### Validação

- `valido`: **10**

### Seções (path)

- `aviacao`: 2
- `terrestre`: 2
- `vant`: 2
- `ael`: 1
- `avibras-aeroco`: 1
- `defesa`: 1
- `seguranca`: 1

## Artefatos

- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\defesanet_dryrun\standardized\defesanet_standardized.json`
- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\defesanet_dryrun\standardized\exemplos.json`

Ver também [STRATEGIC_NEWS_RESEARCH_SOURCES.md](../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md).
