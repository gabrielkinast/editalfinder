# BRISA Artigos — dry-run (Pesquisas/Artigos Estratégicos)

- **Execução:** 2026-05-17T02:27:41Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `brisa_artigos` — BRISA
- **Destino:** public.pesquisa (via vw_pesquisas_front, após apply futuro)

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| Listagem | https://brisabr.com.br/artigos/ |
| RSS | `https://brisabr.com.br/artigos/feed/` |
| robots.txt | Disallow: /wp-admin/ (resto permitido) |
| CMS | WordPress |
| Canal | RSS 2.0 categoria Artigos; HTML /artigos/ espelha ~8 posts |
| Permalink | Slugs na raiz (ex. /desenvolvimento_software_customizado/) — não exige /artigos/ no path |
| Data | pubDate RSS + enrich meta opcional |
| Autor | dc:creator (ex.: Pamela Souza, Maicol Peixe) |
| Imagem | og:image no enrich (budget limitado) |
| Copyright | Apenas resumo RSS/meta; sem corpo integral |
| Notícias | Exclui URLs /news/; não mistura com brisa_news |

## Resultados

- **Standardized:** 8
- **Na janela 24m:** 0
- **Enrich páginas:** 8
- **Descartados pós-enrich:** 0

### tipo_conteudo

- `pesquisa`: **8**

### Validação

- `valido`: **7**
- `incompleto`: **1**

## Warnings

- {'tipo': 'fora_janela_24m', 'count': 8, 'detalhe': 'Itens mantidos no standardized; view pública usa 24 meses.'}

## Artefatos

- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\brisa_artigos_dryrun\standardized\brisa_artigos_standardized.json`
- `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\brisa_artigos_dryrun\raw\brisa_artigos_raw.json`

Ver [STRATEGIC_NEWS_RESEARCH_SOURCES.md](../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md) e [DATA_RETENTION_AND_EXPIRATION_POLICY.md](../docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md).
