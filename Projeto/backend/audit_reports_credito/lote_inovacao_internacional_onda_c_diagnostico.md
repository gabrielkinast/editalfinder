# Lote Cr?dito/Fomento/Inova??o Internacional ? Onda C

Gerado: `2026-05-09T15:17:49Z`

## Seguran?a

- Apply executado: **n?o**
- Supabase staging tocado: **n?o** (loader dry-run executado com `SUPABASE_URL=http://127.0.0.1:9`)
- Schema/migrations alterados: **n?o**
- `opportunity_gate` global alterado: **n?o**

## Resumo

- Fontes: **6**
- Itens brutos: **50**
- Itens standardized: **48**
- Rejeitados no transform: **2**
- Loader dry-run would_upsert: **48**
- Mapping errors: **0**

## Por fonte

| Fonte | Raw | Standardized | Readiness recomendado | Observa??o |
|---|---:|---:|---|---|
| Innovate UK | 1 | 1 | `needs_manual_review` | Volume baixo (1 item) e depende de filtro por funder Innovate UK no detalhe; oficial e acionavel, mas ainda estreito. |
| UKRI Funding | 12 | 12 | `ready_with_notes` | 12 oportunidades oficiais UKRI; sem erros criticos, mas metade dos itens tem publico_alvo generico e muitos sem prazo extraido. |
| Eurostars | 2 | 2 | `needs_manual_review` | 2 itens oficiais; inclui hub Eurostars e uma call especifica. Bom escopo, mas volume baixo e hub deve ficar com observacao. |
| EIT | 16 | 16 | `ready_with_notes` | 16 itens oficiais EIT; mistura calls, procurement e oportunidades de KICs. Precisa curadoria leve para hubs e publico_alvo. |
| ESA STAR | 1 | 0 | `blocked` | Crawler encontra portal oficial, mas transformer rejeita esa-star Publication como login/autenticacao; 0 transformados. |
| ESA OSIP | 18 | 17 | `ready_with_notes` | 17 oportunidades/campaigns oficiais OSIP transformadas; 1 item rejeitado por login/autenticacao e alguns itens sem prazo. |

## URLs oficiais ?teis

### Innovate UK
- https://www.gov.uk/apply-funding-innovation
- https://apply-for-innovation-funding.service.gov.uk/competition/search
- https://www.ukri.org/opportunity/?lang=en-gb

### UKRI Funding
- https://www.ukri.org/opportunity/?lang=en-gb
- https://www.ukri.org/apply-for-funding/

### Eurostars
- https://www.eurekanetwork.org/programmes/eurostars/
- https://www.eurekanetwork.org/programmes-and-calls/eurostars/
- https://www.eurekanetwork.org/programmes-and-calls/eurostars/eurostars-call-for-projects-september-2026/

### EIT
- https://www.eit.europa.eu/our-activities/opportunities
- https://www.eit.europa.eu/opportunities
- https://www.eit.europa.eu/work-with-us/procurement/calls

### ESA STAR
- https://www.esa.int/About_Us/Business_with_ESA/How_to_do/Open_Invitations_to_Tender
- https://esastar-publication-ext.sso.esa.int

### ESA OSIP
- https://ideas.esa.int/core/servlet/hype/IMT?templateName=MenuItem&userAction=BrowseCurrentUser
- https://www.esa.int/Enabling_Support/Preparing_for_the_Future/Discovery_and_Preparation/The_Open_Space_Innovation_Platform_OSIP

## Exclus?es aplicadas

- about/contact/careers/news/blog/eventos sem inscri??o; login isolado; FAQ/resource library gen?rico; p?ginas de pol?tica/termos.

## Auditorias

- Sem?ntica: `48` itens, flags: `{'publico_alvo_sem_evidencia': 15, 'classificacao_muito_ampla': 1}`
- Docs: perdas PDF `0`, perdas n?o-PDF `0`, downloads falharam `14`
- Acesso: `{'ok_html_publico': 6}`

## Riscos e lacunas

- esa_star ficou bloqueado pelo gate como login/autenticacao; nao aplicar sem nova estrategia oficial/API.
- UKRI/Innovate UK ainda tem prazos ausentes em varios itens; melhorar parser de closing date em fase curta.
- EIT mistura calls/procurement/hubs; recomendar ready_with_notes com monitoramento.
- Dry-run loader foi executado com SUPABASE_URL local falso para nao tocar staging real.

## Pr?ximos passos recomendados

- Adicionar fontes ao config/source_readiness.json apenas depois de revisao humana.
- Melhorar extracao de prazo em UKRI/EIT/OSIP.
- Refinar publico_alvo para reduzir publico_alvo_sem_evidencia.
- Investigar ESA STAR por feed/export oficial ou endpoint publico antes de novo crawler.