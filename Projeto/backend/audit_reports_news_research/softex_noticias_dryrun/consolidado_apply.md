# SOFTEX Notícias — preparação apply staging

- **Execução:** 2026-05-17T04:20:27Z
- **Fonte:** `softex_noticias`
- **Apply executado:** não

## Totais

- **Standardized (crawler):** 10
- **Válidas no payload:** 10
- **would_upsert_noticia:** 10
- **errors_count:** 0
- **apply_status:** `dry_run_only`

## Dry-run loader

```text
C:\Program Files\Python312\python.exe D:\Computational_Physics\My Projects\edital\scripts\load_news_research_sources.py --dry-run --source softex_noticias --input-dir audit_reports_news_research/softex_noticias_dryrun
```

- Relatório: `audit_reports_news_research/softex_noticias_dryrun/load_news_research_summary.json`
- Payload: `audit_reports_news_research/softex_noticias_dryrun/softex_noticias_payload_noticia.json`

## Notícias no payload

### 1. Softex participa da inauguração do laboratório de IA do Instituto Atlântico

- **Data:** 2026-05-15
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, engenharia, industria, software, computacao_ia
- **Imagem:** sim
- **Link:** https://softex.br/softex-participa-da-inauguracao-do-laboratorio-de-ia-do-instituto-atlantico/

### 2. Inscrições abertas para o XChange 2026

- **Data:** 2026-05-14
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, engenharia, industria, software
- **Imagem:** sim
- **Link:** https://softex.br/inscricoes-abertas-para-o-xchange-2026/

### 3. Livro “Mulheres em Tecnologia” mostra em detalhes por que diversidade se tornou estratégica para emp

- **Data:** 2026-05-12
- **Categoria:** Softex Mulher
- **Eixos:** tecnologia, inovacao, industria, software
- **Imagem:** sim
- **Link:** https://softex.br/livro-mulheres-em-tecnologia-mostra-em-detalhes-por-que-diversidade-se-tornou-estrategica-para-empresas-e-governos/

### 4. Softex apoia edição 2026 do Energy Summit no Rio

- **Data:** 2026-05-12
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, engenharia, industria, software
- **Imagem:** sim
- **Link:** https://softex.br/softex-apoia-edicao-2026-do-energy-summit-no-rio/

### 5. Programa de conexão de startups com mercado canadense conta com o apoio do Brasil IT+

- **Data:** 2026-05-11
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, industria, software
- **Imagem:** sim
- **Link:** https://softex.br/programa-de-conexao-de-startups-com-mercado-canadense-conta-com-o-apoio-do-brasil-it/

### 6. EvoSystems detalha estratégia de expansão global no podcast Pelo Mundo com o Brasil IT+

- **Data:** 2026-05-11
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, engenharia, industria, software
- **Imagem:** sim
- **Link:** https://softex.br/evosystems-detalha-estrategia-de-expansao-global-no-podcast-pelo-mundo-com-o-brasil-it/

### 7. Brasil IT+ é destaque no Midsize Enterprise Summit Spring 2026

- **Data:** 2026-05-11
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, industria
- **Imagem:** sim
- **Link:** https://softex.br/brasil-it-e-destaque-no-midsize-enterprise-summit-spring-2026/

### 8. Softex defende estratégia nacional para autonomia tecnológica em painel do XI Congresso da ABIPTI

- **Data:** 2026-05-06
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, engenharia, industria, software
- **Imagem:** sim
- **Link:** https://softex.br/softex-defende-estrategia-nacional-para-autonomia-tecnologica-em-painel-do-xi-congresso-da-abipti/

### 9. FavEla empoder@ abre inscrições para apoiar mulheres empreendedoras em Manaus

- **Data:** 2026-04-30
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao
- **Link:** https://softex.br/favela-empoder-abre-inscricoes-para-apoiar-mulheres-empreendedoras-em-manaus/

### 10. Inscrições abertas para o Amazônia Geek, programa de formação de talentos em games

- **Data:** 2026-04-29
- **Categoria:** Notícias
- **Eixos:** tecnologia, inovacao, industria, software
- **Link:** https://softex.br/inscricoes-abertas-para-o-amazonia-geek-programa-de-formacao-de-talentos-em-games/

## Apply staging (não executado)

```powershell
# NÃO EXECUTADO — apply staging (executar manualmente após validar .env.staging)
$env:EDITALFINDER_ENV='staging'
$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'
python scripts/load_news_research_sources.py `
  --apply --staging --test-db-before-apply `
  --source softex_noticias `
  --input-dir audit_reports_news_research/softex_noticias_dryrun
```
