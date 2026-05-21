# Exército Brasileiro — subset válido (consolidado)

- **Execução:** 2026-05-17T04:05:28Z
- **Origem:** `audit_reports_news_research/exercito_brasileiro_dryrun/standardized/exercito_brasileiro_standardized.json`
- **Subset:** `audit_reports_news_research/exercito_brasileiro_subset_valido/standardized/exercito_brasileiro_standardized.json`

## Totais

- **Original:** 10
- **Válido (incluído):** 6
- **Incompleto (excluído):** 4

## Itens incluídos

### 1. Programa Forças Blindadas atualiza frota de veículos de combate do Exército Brasileiro Operacionalid

- **Data:** 2026-05-12
- **Categoria:** Noticiário do Exército
- **Eixos:** defesa, engenharia, tecnologia_militar
- **Imagem:** `https://www.eb.mil.br/documents/42281/0/capa%20%2848%29.jpg/3a5a2343-76db-eb6f-31b4-548d58…`
- **Link:** https://www.eb.mil.br/web/noticias/w/programa-forcas-blindadas-atualiza-frota-de-veiculos-de-combate-do-exercito-brasileiro

### 2. Exército consolida alinhamento operacional da capacidade de Defesa Química, Biológica, Radiológica e

- **Data:** 2026-05-15
- **Categoria:** Noticiário do Exército
- **Eixos:** defesa, tecnologia_militar, formacao_militar_cientifica, computacao_cyber
- **Imagem:** `https://www.eb.mil.br/documents/42281/0/CAPA%203.jpg/fd12216a-4859-172b-292f-0897715f09db?…`
- **Link:** https://www.eb.mil.br/web/noticias/w/exercito-consolida-alinhamento-operacional-da-capacidade-de-defesa-quimica-biologica-radiologica-e-nuclear

### 3. Evento destaca capacidades das tropas de Infantaria do Exército Operacionalidade

- **Data:** 2026-05-13
- **Categoria:** Noticiário do Exército
- **Eixos:** defesa, tecnologia_militar, aeroespacial
- **Imagem:** `https://www.eb.mil.br/documents/42281/0/CAPA%201%20%284%29.jpg/cde9ea66-4b21-06ca-c2ac-23c…`
- **Link:** https://www.eb.mil.br/web/noticias/w/evento-destaca-capacidades-das-tropas-de-infantaria-do-exercito

### 4. Diplomacia militar Cadetes da Academia Militar representam o Brasil em competição militar internacio

- **Data:** 2026-05-15
- **Categoria:** Noticiário do Exército
- **Eixos:** defesa, tecnologia_militar, formacao_militar_cientifica
- **Imagem:** `https://www.eb.mil.br/documents/42281/0/cadets%20competicoers%20internacionais%206.jpg/816…`
- **Link:** https://www.eb.mil.br/web/noticias/w/cadetes-da-academia-militar-representam-o-brasil-em-competicao-militar-internacional

### 5. EBlog Novo artigo

- **Data:** 2026-05-15
- **Categoria:** Noticiário do Exército
- **Eixos:** defesa, tecnologia_militar
- **Imagem:** `https://www.eb.mil.br/documents/42953/1140680/card%20EBLOG%20NOVO%20PORTAL%20-%20Copia%20%…`
- **Link:** https://www.eb.mil.br/web/noticias/w/novo-artigo-do-eblog

### 6. Forças militares e civis aperfeiçoam prontidão para emergências climáticas em Santa Catarina

- **Data:** 2026-05-12
- **Categoria:** Noticiário do Exército
- **Eixos:** defesa, tecnologia_militar
- **Imagem:** `https://www.eb.mil.br/documents/42281/0/_COM5797A%20%281%29.jpg/32925009-5edd-8cb9-6cd5-ff…`
- **Link:** https://www.eb.mil.br/web/noticias/w/forcas-militares-e-civis-aperfeicoam-prontidao-para-emergencias-climaticas-em-santa-catarina

## Incompletos (excluídos do subset)

- **Concurso para sargentos de carreira: últimos dias de inscrição Integração com a **
  - Data: 2026-05-04
  - Motivo: resumo_curto_ou_rotulo_editorial (26 chars)
  - Resumo: Integração com a sociedade

- **Atuação da Força Terrestre na Faixa de Fronteira impõe mais de R$ 600 milhões de**
  - Data: 2026-05-06
  - Motivo: resumo_curto_ou_rotulo_editorial (37 chars)
  - Resumo: Operacionalidade - Faixa de Fronteira

- **Solenidade retrata evolução da Cavalaria do Exército e atrai milhares de pessoas**
  - Data: 2026-05-11
  - Motivo: resumo_curto_ou_rotulo_editorial (26 chars)
  - Resumo: Integração com a sociedade

- **Prática de Orientação nos Colégios Militares desenvolve valências que vão além d**
  - Data: 2026-05-15
  - Motivo: resumo_curto_ou_rotulo_editorial (26 chars)
  - Resumo: Integração com a sociedade

## Dry-run roteador (`dry_run_news_research_loader`)

- **Comando:** `C:\Program Files\Python312\python.exe D:\Computational_Physics\My Projects\edital\scripts\dry_run_news_research_loader.py --input-dir D:\Computational_Physics\My Projects\edital\audit_reports_news_research\exercito_brasileiro_subset_valido\standardized --output-dir D:\Computational_Physics\My Projects\edital\audit_reports_news_research\exercito_brasileiro_subset_valido\loader_dryrun`
- **Simulado public.noticia:** 6

## Dry-run carga (`load_news_research_sources`)

- **Comando:** `C:\Program Files\Python312\python.exe D:\Computational_Physics\My Projects\edital\scripts\load_news_research_sources.py --dry-run --source exercito_brasileiro --noticia-payload audit_reports_news_research/exercito_brasileiro_subset_valido/exercito_brasileiro_subset_valido_payload_noticia.json --input-dir audit_reports_news_research/exercito_brasileiro_subset_valido`
- **would_upsert_noticia:** 6
- **errors_count:** 0
- **Relatório:** `audit_reports_news_research/exercito_brasileiro_subset_valido/load_news_research_summary.json`

## Apply staging (não executado)

```powershell
# NÃO EXECUTADO — apply staging futuro (após validar .env.staging)
$env:EDITALFINDER_ENV='staging'
$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'
python scripts/load_news_research_sources.py `
  --apply --staging --test-db-before-apply `
  --source exercito_brasileiro `
  --noticia-payload audit_reports_news_research/exercito_brasileiro_subset_valido/exercito_brasileiro_subset_valido_payload_noticia.json `
  --input-dir audit_reports_news_research/exercito_brasileiro_subset_valido
```
