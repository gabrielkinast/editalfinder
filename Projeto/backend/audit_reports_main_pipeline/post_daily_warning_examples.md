# Exemplos acionáveis de warnings

- Gerado: `2026-05-10T08:02:47Z`
- Ambiente: `staging`

## Resumo por warning

| Problema | Severidade | Count | Top fontes |
|---|---:|---:|---|
| `edital.prazo_vencido_ativo_true` | warning | 49 | CNPQ=10, EMBRAPII=10, Grants.gov=9, IARPA=8, AMAZUL=7 |
| `edital.titulo_ruidoso_inativo` | info | 6 | BASA=1, BDMG=1, General Dynamics Suppliers=1, KAKENHI=1, NATO DIANA=1 |
| `edital.credito_tipo_recurso_incoerente` | warning | 4 | CNPQ=1, FAPEMIG=1, FAPERGS=1, IPEN=1 |
| `edital.setor_estrategico_muito_amplo` | warning | 47 | DoD SBIR/STTR=9, EIC=9, Eureka Network=5, DIU=3, European Defence Fund=3 |
| `edital.suspeito_ativo_true` | warning | 47 | AMAZUL=12, General Dynamics Suppliers=6, Apex Brasil=4, Petrobras=4, BASA=3 |

## Exemplos por warning

### `edital.prazo_vencido_ativo_true`

| Fonte | Título | Link | Motivo |
|---|---|---|---|
| BDMG | Trabalhe no BDMG e construa o futuro de Minas Gerais! | https://www.bdmg.mg.gov.br/concurso | prazo_envio vencido (2025-06-24) e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 02/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-022025 | prazo_envio vencido (2026-03-20) e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 07/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-072025 | prazo_envio vencido (2025-12-11) e ativo=true |
| ANP | Edital de Chamada Pública | https://www.gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/prh-anp-programa-de-formacao-de-recursos-humanos/eixo-academico/edital-de-... | prazo_envio vencido (2025-11-26) e ativo=true |
| ANP | Consultas e Audiências Públicas | https://www.gov.br/anp/pt-br/assuntos/consultas-e-audiencias-publicas/consulta-audiencia-publica | prazo_envio vencido (2026-05-04) e ativo=true |
| Apex Brasil | Exporta Mais Brasil - E-commerce 2026 | https://crm-apps.apexbrasil.com.br/orgbdeab873/inscricao-eventos/evento/exporta-mais-brasil-e-commerce-2026/9a606dbd-27e2-4239-9914-a7826... | prazo_envio vencido (2026-05-08) e ativo=true |
| CNPQ | Chamada Nº 28/2025 - Apoio a Projetos de Cooperação CNPq-TUBITAK | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2025/chamada-no-28-2025/chamada-tubitak-lan-amento.pdf | prazo_envio vencido (2026-05-04) e ativo=true |
| CNPQ | Chamada pública CNPq/MCTI/MEMP N° 05/2026 - Programa de Iniciação ao Empreendedorismo - PIEMP | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-05-2026/chamada-piemp-2026-1.pdf | prazo_envio vencido (2026-04-13) e ativo=true |
| CNPQ | Chamada para Pesquisas Inovadoras em Vacinas CNPq/Decit/SCTIE/MS Nº 31/2025 | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2025/chamada-no-31-2025/chamada_publica_vacinas.pdf | prazo_envio vencido (2026-02-23) e ativo=true |
| CNPQ | CHAMADA PÚBLICA CNPq/MPA Nº 03/2026 PROGRAMA JOVEM CIENTISTA DA PESCA ARTESANAL - INICIAÇÃO CIENTÍFICA JÚNIOR (ICJ) | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-03-2026/sei_01300-000619_2026_40.pdf | prazo_envio vencido (2026-03-24) e ativo=true |

### `edital.titulo_ruidoso_inativo`

| Fonte | Título | Link | Motivo |
|---|---|---|---|
| BASA | Conta PJ | https://www.bancoamazonia.com.br/empresas/conta-pj | título contém termo ruidoso: conta pj (ativo=false; histórico) |
| KAKENHI | 科研費FAQ | https://www.jsps.go.jp/j-grantsinaid/01_seido/05_faq/index.html | título contém termo ruidoso: faq (ativo=false; histórico) |
| BDMG | Entre em contato | https://www.bdmg.mg.gov.br/investimento | título contém termo ruidoso: entre em contato (ativo=false; histórico) |
| General Dynamics Suppliers | Supplier FAQs | https://www.gd.com/suppliers/supplier-faqs | título contém termo ruidoso: faq (ativo=false; histórico) |
| NATO DIANA | NATO DIANA — Programme FAQ (challenges, eligibility, portal) | https://www.diana.nato.int/faq.html | título contém termo ruidoso: faq (ativo=false; histórico) |
| NUCLEP | Quem Somos | https://www.nuclep.gov.br/quem-somos | título contém termo ruidoso: quem somos (ativo=false; histórico) |

### `edital.credito_tipo_recurso_incoerente`

| Fonte | Título | Link | Motivo |
|---|---|---|---|
| FAPEMIG | Guias passo a passo | https://fapemig.br/central-de-ajuda/guias-passo-a-passo/4908 | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| FAPERGS | FAPERGS - Fundação de Amparo à pesquisa do Estado do RS | https://fapergs.rs.gov.br/sict-e-fapergs-lancam-edital-de-r-8-milhoes-para-fortalecer-ambientes-de-inovacao-no-rs | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| IPEN | Internacionalização | https://www.gov.br/ipen/pt-br/pesquisa-e-desenvolvimento/internacionalizacao | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| CNPQ | CNPq/CAPES/IRD Nº 27/2025 Programa de apoio ao Centro Franco-Brasileiro de Biodiversidade Amazônica | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2025/chamada-no-27-2025/sei_cnpq-2536880-chamada-p-blica.pdf | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |

### `edital.setor_estrategico_muito_amplo`

| Fonte | Título | Link | Motivo |
|---|---|---|---|
| Ministério da Defesa | Projeto Soldado Cidadão | https://www.gov.br/defesa/pt-br/assuntos/programas-sociais/copy_of_projeto-soldado-cidadao | setor_estrategico contém 4 valores; limite recomendado é 3 |
| ANEEL | Sistemas de Armazenamento de Energia | https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/chamadas-de-projetos-de-pdi-estrategicos/sistemas... | setor_estrategico contém 4 valores; limite recomendado é 3 |
| AFWERX | Specific Topic | https://afwerx.com/divisions/sbir-sttr/specific-topic/ | setor_estrategico contém 4 valores; limite recomendado é 3 |
| Ministério da Defesa | Consulta Pública ao Inteiro Teor dos Processos de Licitações e Contratos | https://www.gov.br/defesa/pt-br/acesso-a-informacao/licitacoes-e-contratos-1/consulta-publica-ao-inteiro-teor-dos-processos-de-licitacoes... | setor_estrategico contém 4 valores; limite recomendado é 3 |
| DoD SBIR/STTR | Participating Federal Agencies | https://www.sbir.gov/participating-agencies | setor_estrategico contém 4 valores; limite recomendado é 3 |
| DoD SBIR/STTR | Impact, Mission, and Goals | https://www.sbir.gov/impact | setor_estrategico contém 4 valores; limite recomendado é 3 |
| DoD SBIR/STTR | Portfolio | https://www.sbir.gov/awards | setor_estrategico contém 4 valores; limite recomendado é 3 |
| DoD SBIR/STTR | Data Resources | https://www.sbir.gov/api | setor_estrategico contém 4 valores; limite recomendado é 3 |
| DoD SBIR/STTR | Data Resources | https://www.sbir.gov/data-resources | setor_estrategico contém 4 valores; limite recomendado é 3 |
| DoD SBIR/STTR | Funding Opportunities | https://www.sbir.gov/topics | setor_estrategico contém 4 valores; limite recomendado é 3 |

### `edital.suspeito_ativo_true`

| Fonte | Título | Link | Motivo |
|---|---|---|---|
| BASA | Renegociação de Dívidas | https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos/renegociacao-dividas | validacao_status=suspeito e ativo=true |
| BAE Systems Suppliers | Login to your account | https://baesystems.hicx.net/bae/hicxesm-portal/app/index.html | validacao_status=suspeito e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 05/2026 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-052026 | validacao_status=suspeito e ativo=true |
| SENAI | Agenda.Tech (SENAI) 2026 Chamada: Mapeamento de Oportunidades e Tencologias para Powrshoring no Brasill \| Resultado ... | https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/categoria/agendatech/ | validacao_status=suspeito e ativo=true |
| SENAI | Chamada Regional (SENAI) [SENAI/RJ] CONCURSO DE INOVAÇÃO PARA SOLUÇÕES EM EFICIÊNCIA ENERGÉTICA - (SENAI RJ/ENBPAR) -... | https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/categoria/chamada-regional-senai/ | validacao_status=suspeito e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 04/2024 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-042024-0 | validacao_status=suspeito e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 02/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-022025 | validacao_status=suspeito e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 03/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-032025 | validacao_status=suspeito e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 06/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-062025 | validacao_status=suspeito e ativo=true |
| AMAZUL | Dispensa de Licitação por Valor 07/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-072025 | validacao_status=suspeito e ativo=true |

## Resumo por fonte

| Fonte | Total | Principais warnings |
|---|---:|---|
| AMAZUL | 19 | suspeito_ativo_true=12, prazo_vencido_ativo_true=7 |
| CNPQ | 11 | prazo_vencido_ativo_true=10, credito_tipo_recurso_incoerente=1 |
| EMBRAPII | 10 | prazo_vencido_ativo_true=10 |
| DoD SBIR/STTR | 9 | setor_estrategico_muito_amplo=9 |
| EIC | 9 | setor_estrategico_muito_amplo=9 |
| Grants.gov | 9 | prazo_vencido_ativo_true=9 |
| IARPA | 8 | prazo_vencido_ativo_true=8 |
| General Dynamics Suppliers | 6 | suspeito_ativo_true=6 |
| Apex Brasil | 5 | suspeito_ativo_true=4, prazo_vencido_ativo_true=1 |
| Eureka Network | 5 | setor_estrategico_muito_amplo=5 |
| Petrobras | 4 | suspeito_ativo_true=4 |
| BASA | 3 | suspeito_ativo_true=3 |
| DIU | 3 | setor_estrategico_muito_amplo=3 |
| European Defence Fund | 3 | setor_estrategico_muito_amplo=3 |
| IPEN | 3 | setor_estrategico_muito_amplo=2, credito_tipo_recurso_incoerente=1 |
| Lockheed Martin Suppliers | 3 | suspeito_ativo_true=3 |
| Ministério da Defesa | 3 | setor_estrategico_muito_amplo=3 |
| Mitsubishi Heavy Industries (Suppliers) | 3 | setor_estrategico_muito_amplo=3 |
| SENAI | 3 | suspeito_ativo_true=2, setor_estrategico_muito_amplo=1 |
| AFWERX | 2 | setor_estrategico_muito_amplo=2 |
| ANEEL | 2 | setor_estrategico_muito_amplo=2 |
| ANP | 2 | prazo_vencido_ativo_true=2 |
| BADESUL | 2 | suspeito_ativo_true=2 |
| BAE Systems Suppliers | 2 | suspeito_ativo_true=2 |
| EIT | 2 | suspeito_ativo_true=2 |
| Rheinmetall Suppliers | 2 | suspeito_ativo_true=2 |
| Softex | 2 | suspeito_ativo_true=2 |
| BDMG | 1 | prazo_vencido_ativo_true=1 |
| CNEN | 1 | setor_estrategico_muito_amplo=1 |
| CONFAP | 1 | setor_estrategico_muito_amplo=1 |
| DARPA Opportunities | 1 | setor_estrategico_muito_amplo=1 |
| ELETRONUCLEAR | 1 | setor_estrategico_muito_amplo=1 |
| ESA OSIP | 1 | suspeito_ativo_true=1 |
| FAPEMIG | 1 | credito_tipo_recurso_incoerente=1 |
| FAPERGS | 1 | credito_tipo_recurso_incoerente=1 |
| Ministério da Saúde | 1 | setor_estrategico_muito_amplo=1 |
| NATO DIANA | 1 | prazo_vencido_ativo_true=1 |
| Thales Suppliers | 1 | suspeito_ativo_true=1 |
| UKRI Funding | 1 | suspeito_ativo_true=1 |

## Recomendações

- Priorizar problemas com maior total por fonte; eles indicam ajuste de crawler, transformer ou regra de curadoria.
- Para titulo_ruidoso_ativo_true e prazo_vencido_ativo_true, revisar desativação; titulo_ruidoso_inativo (severity info) conta histórico ativo=false.
- Para credito_tipo_recurso_incoerente, ajustar calibração de crédito por fonte antes de novo apply.
- Para setor_estrategico_muito_amplo, limitar taxonomia a evidências fortes ou mover excesso para extras.
- Para suspeito_ativo_true, revisar se o frontend deve ocultar ou badgear esses itens até curadoria.
- Fonte com maior volume de warnings: AMAZUL (19 ocorrências).