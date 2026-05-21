# CAPES Notícias — dry-run (Notícias Estratégicas)

- **Execução:** 2026-05-17T05:36:14Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `capes_noticias` — CAPES Notícias
- **Destino:** public.noticia (via vw_noticias_front, após apply futuro)

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| url_listagem | https://www.gov.br/capes/pt-br/assuntos/noticias |
| rss_seed | https://www.gov.br/capes/pt-br/assuntos/noticias/rss.xml |
| rss_alternativas | https://www.gov.br/capes/pt-br/assuntos/noticias/RSS, https://www.gov.br/capes/pt-br/assuntos/noticias/atom.xml |
| robots_gov_br | User-agent * — sem Disallow global relevante a /capes/ |
| robots_capes | User-agent * — Disallow: (vazio) |
| cms | gov.br / Plone (Zope) |
| listagem | HTML hub + RSS; feed ordenado pubDate desc no crawl |
| detalhe | Slug /assuntos/noticias/{slug}; data em .documentPublished (DD/MM/AAAA) |
| link_rss | Plone: <guid> como URL canônica quando <link> vazio |
| imagem | og:image no enrich |
| autor | documentByLine quando disponível |
| copyright | Resumo RSS ou 1º parágrafo; sem content:encoded integral |
| nao_editais | Notícias sobre editais permanecem tipo_conteudo=noticia |

## Resultados

- **Standardized:** 10
- **Na janela 12m:** 7
- **Enrich páginas:** 8

### Categorias estratégicas

- **Formação:** 2
- **Ciência:** 4
- **Pós-graduação:** 1
- **Inovação:** 1
- **Bolsas:** 2

### Validação

- `valido`: **10**

## Itens

### 1. CAPES e CNPq debatem equidade de gênero

- **Data:** 2026-02-12
- **Categoria:** Formação
- **Eixos:** ciencia_tecnologia, formacao_cientifica
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/capes-e-cnpq-debatem-equidade-de-genero

### 2. Projeto aproxima meninas e mulheres da área de transição energética

- **Data:** 2026-02-11
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/projeto-aproxima-meninas-e-mulheres-da-area-de-transicao-energetica

### 3. Censo da Pós-Graduação registra 70% de participação

- **Data:** 2026-02-03
- **Categoria:** Pós-graduação
- **Eixos:** ciencia_tecnologia, pos_graduacao
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/censo-da-pos-graduacao-registra-70-de-participacao

### 4. CAPES realiza sete treinamentos em fevereiro

- **Data:** 2026-01-30
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/capes-realiza-sete-treinamentos-em-fevereiro

### 5. CAPES atualiza regras para repasses de recursos financeiros

- **Data:** 2026-01-28
- **Categoria:** Inovação
- **Eixos:** ciencia_tecnologia, inovacao, engenharia
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/capes-atualiza-regras-para-repasses-de-recursos-financeiros

### 6. Sobre o Qualis Periódicos na Avaliação Quadrienal 2021-2024

- **Data:** 2026-01-20
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/sobre-o-qualis-periodicos-na-avaliacao-quadrienal-2021-2024

### 7. Divulgados inscritos de chamada para pesquisas na Alemanha

- **Data:** 2025-12-29
- **Categoria:** Bolsas
- **Eixos:** ciencia_tecnologia, bolsas_fomento
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/divulgados-inscritos-de-chamada-para-pesquisas-na-alemanha

### 8. Instituições de todas as regiões do país aderiram ao GoPG

- **Data:** 2025-05-08
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Imagem:** sim
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/instituicoes-de-todas-as-regioes-do-pais-aderiram-ao-gopg

### 9. MEC institui Comitê de Governança do Mais Professores

- **Data:** 2025-04-29
- **Categoria:** Formação
- **Eixos:** ciencia_tecnologia, formacao_cientifica
- **Imagem:** não
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/mec-institui-comite-de-governanca-do-mais-professores

### 10. Aberta seleção para mestrado profissional em roteiro nos EUA

- **Data:** 2025-02-28
- **Categoria:** Bolsas
- **Eixos:** ciencia_tecnologia, bolsas_fomento
- **Imagem:** não
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/aberta-selecao-para-mestrado-profissional-em-roteiro-nos-eua

## Warnings

- {'tipo': 'fora_janela_12m', 'count': 3, 'detalhe': 'Itens no standardized; view pública filtra 12 meses.'}
