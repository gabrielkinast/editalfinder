# Auditoria news/research pipeline

- Itens avaliados: **152**
- Fontes: **5**
- Sem data_publicacao: **0**
- Duplicatas por link: **0**
- Conteúdo genérico: **0**

## Fontes com maior ruído

- `darpa_opportunities_research` total=1 sem_data=0 generic=0 noise_ratio=0.0
- `eurekalert_science_filtered` total=1 sem_data=0 generic=0 noise_ratio=0.0

## Recomendação de ativação inicial

- Ativar primeiro: darpa_news, iaea_news_publications, nasa_news
- Manter em teste: darpa_opportunities_research, eurekalert_science_filtered

## Próximos passos para integração com loader

- Adicionar job dedicado com --apply-content-routed para carregar apenas noticia/pesquisa em staging.
- Reforcar infer_content_type com features por fonte (NASA/DARPA/IAEA/EurekAlert).
- Criar whitelist de seeds por fonte e threshold minimo de data_publicacao para ativacao.