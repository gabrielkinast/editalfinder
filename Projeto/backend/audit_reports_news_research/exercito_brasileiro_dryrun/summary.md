# Exército Brasileiro — dry-run (Notícias Estratégicas)

- **Execução:** 2026-05-17T03:38:38Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `exercito_brasileiro` — Exército Brasileiro

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| Portal | https://www.eb.mil.br/web/guest |
| Noticiário | https://www.eb.mil.br/web/guest/noticiario-do-exercito |
| Detalhe | `https://www.eb.mil.br/web/noticias/w/{slug}` |
| RSS | Não identificado (listagem HTML Liferay) |
| robots.txt | User-agent: * / Disallow: (vazio) |
| CMS | Liferay |
| Data | div.dates — Publicado em DD/MM/AAAA (+ enrich) |
| Imagem | og:image no enrich |

## Resultados

- **Standardized:** 10
- **Na janela 12m:** 10
- **Enrich:** 10

- `tipo_conteudo=noticia`: **10**

- `valido`: **6**
- `incompleto`: **4**

## Warnings

- {'tipo': 'sem_rss', 'detalhe': 'Sem RSS útil; seeds guest + noticiario-do-exercito.'}

## Artefatos

- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\exercito_brasileiro_dryrun\standardized\exercito_brasileiro_standardized.json`
- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\exercito_brasileiro_dryrun\raw\exercito_brasileiro_raw.json`
