# Validação global pós-daily

- Gerado: `2026-05-10T08:02:47Z`
- Ambiente: `staging`
- OK geral: **True**
- Critical errors: **0**
- Warnings: **4**

## Contagens

- `edital`: total=1232, ativo_true=1226, ativo_false=6
- `noticia`: total=109, ativo_true=109, ativo_false=0
- `pesquisa`: total=47, ativo_true=47, ativo_false=0

## Problemas

- WARNING `edital` / `prazo_vencido_ativo_true`: 49
- WARNING `edital` / `credito_tipo_recurso_incoerente`: 4
- WARNING `edital` / `setor_estrategico_muito_amplo`: 47
- WARNING `edital` / `suspeito_ativo_true`: 47

## Exemplos por warning

| Problema | Fonte | Título | Link | Motivo |
|---|---|---|---|---|
| `edital.prazo_vencido_ativo_true` | BDMG | Trabalhe no BDMG e construa o futuro de Minas Gerais! | https://www.bdmg.mg.gov.br/concurso | prazo_envio vencido (2025-06-24) e ativo=true |
| `edital.prazo_vencido_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 02/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-022025 | prazo_envio vencido (2026-03-20) e ativo=true |
| `edital.prazo_vencido_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 07/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-072025 | prazo_envio vencido (2025-12-11) e ativo=true |
| `edital.prazo_vencido_ativo_true` | ANP | Edital de Chamada Pública | https://www.gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/prh-anp-programa-de-formacao-de-recursos-humanos/eixo-academico/... | prazo_envio vencido (2025-11-26) e ativo=true |
| `edital.prazo_vencido_ativo_true` | ANP | Consultas e Audiências Públicas | https://www.gov.br/anp/pt-br/assuntos/consultas-e-audiencias-publicas/consulta-audiencia-publica | prazo_envio vencido (2026-05-04) e ativo=true |
| `edital.prazo_vencido_ativo_true` | Apex Brasil | Exporta Mais Brasil - E-commerce 2026 | https://crm-apps.apexbrasil.com.br/orgbdeab873/inscricao-eventos/evento/exporta-mais-brasil-e-commerce-2026/9a606dbd-27e2-4239-... | prazo_envio vencido (2026-05-08) e ativo=true |
| `edital.prazo_vencido_ativo_true` | CNPQ | Chamada Nº 28/2025 - Apoio a Projetos de Cooperação CNPq-TUBITAK | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2025/chamada-no-28-2025/chamada-tubitak-lan-amento.pdf | prazo_envio vencido (2026-05-04) e ativo=true |
| `edital.prazo_vencido_ativo_true` | CNPQ | Chamada pública CNPq/MCTI/MEMP N° 05/2026 - Programa de Iniciação ao Empreendedorismo - PIEMP | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-05-2026/chamada-piemp-2026-1.pdf | prazo_envio vencido (2026-04-13) e ativo=true |
| `edital.prazo_vencido_ativo_true` | CNPQ | Chamada para Pesquisas Inovadoras em Vacinas CNPq/Decit/SCTIE/MS Nº 31/2025 | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2025/chamada-no-31-2025/chamada_publica_vacinas.pdf | prazo_envio vencido (2026-02-23) e ativo=true |
| `edital.prazo_vencido_ativo_true` | CNPQ | CHAMADA PÚBLICA CNPq/MPA Nº 03/2026 PROGRAMA JOVEM CIENTISTA DA PESCA ARTESANAL - INICIAÇÃO CIENTÍFICA JÚNI... | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-03-2026/sei_01300-000619_2026_40.pdf | prazo_envio vencido (2026-03-24) e ativo=true |
| `edital.credito_tipo_recurso_incoerente` | FAPEMIG | Guias passo a passo | https://fapemig.br/central-de-ajuda/guias-passo-a-passo/4908 | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| `edital.credito_tipo_recurso_incoerente` | FAPERGS | FAPERGS - Fundação de Amparo à pesquisa do Estado do RS | https://fapergs.rs.gov.br/sict-e-fapergs-lancam-edital-de-r-8-milhoes-para-fortalecer-ambientes-de-inovacao-no-rs | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| `edital.credito_tipo_recurso_incoerente` | IPEN | Internacionalização | https://www.gov.br/ipen/pt-br/pesquisa-e-desenvolvimento/internacionalizacao | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| `edital.credito_tipo_recurso_incoerente` | CNPQ | CNPq/CAPES/IRD Nº 27/2025 Programa de apoio ao Centro Franco-Brasileiro de Biodiversidade Amazônica | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2025/chamada-no-27-2025/sei_cnpq-2536880-chamada-p-blica.pdf | crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos |
| `edital.setor_estrategico_muito_amplo` | Ministério da Defesa | Projeto Soldado Cidadão | https://www.gov.br/defesa/pt-br/assuntos/programas-sociais/copy_of_projeto-soldado-cidadao | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | ANEEL | Sistemas de Armazenamento de Energia | https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/chamadas-de-projetos-de-pdi-estrategico... | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | AFWERX | Specific Topic | https://afwerx.com/divisions/sbir-sttr/specific-topic/ | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | Ministério da Defesa | Consulta Pública ao Inteiro Teor dos Processos de Licitações e Contratos | https://www.gov.br/defesa/pt-br/acesso-a-informacao/licitacoes-e-contratos-1/consulta-publica-ao-inteiro-teor-dos-processos-de-... | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | DoD SBIR/STTR | Participating Federal Agencies | https://www.sbir.gov/participating-agencies | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | DoD SBIR/STTR | Impact, Mission, and Goals | https://www.sbir.gov/impact | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | DoD SBIR/STTR | Portfolio | https://www.sbir.gov/awards | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | DoD SBIR/STTR | Data Resources | https://www.sbir.gov/api | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | DoD SBIR/STTR | Data Resources | https://www.sbir.gov/data-resources | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.setor_estrategico_muito_amplo` | DoD SBIR/STTR | Funding Opportunities | https://www.sbir.gov/topics | setor_estrategico contém 4 valores; limite recomendado é 3 |
| `edital.suspeito_ativo_true` | BASA | Renegociação de Dívidas | https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos/renegociacao-dividas | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | BAE Systems Suppliers | Login to your account | https://baesystems.hicx.net/bae/hicxesm-portal/app/index.html | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 05/2026 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-052026 | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | SENAI | Agenda.Tech (SENAI) 2026 Chamada: Mapeamento de Oportunidades e Tencologias para Powrshoring no Brasill \| ... | https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/categoria/agendatech/ | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | SENAI | Chamada Regional (SENAI) [SENAI/RJ] CONCURSO DE INOVAÇÃO PARA SOLUÇÕES EM EFICIÊNCIA ENERGÉTICA - (SENAI RJ... | https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/categoria/chamada-regional-senai/ | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 04/2024 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-042024-0 | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 02/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-022025 | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 03/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-032025 | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 06/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-062025 | validacao_status=suspeito e ativo=true |
| `edital.suspeito_ativo_true` | AMAZUL | Dispensa de Licitação por Valor 07/2025 | https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-072025 | validacao_status=suspeito e ativo=true |

## Warnings por fonte

- `AMAZUL`: total=19 (suspeito_ativo_true=12, prazo_vencido_ativo_true=7)
- `CNPQ`: total=11 (prazo_vencido_ativo_true=10, credito_tipo_recurso_incoerente=1)
- `EMBRAPII`: total=10 (prazo_vencido_ativo_true=10)
- `DoD SBIR/STTR`: total=9 (setor_estrategico_muito_amplo=9)
- `EIC`: total=9 (setor_estrategico_muito_amplo=9)
- `Grants.gov`: total=9 (prazo_vencido_ativo_true=9)
- `IARPA`: total=8 (prazo_vencido_ativo_true=8)
- `General Dynamics Suppliers`: total=6 (suspeito_ativo_true=6)
- `Apex Brasil`: total=5 (suspeito_ativo_true=4, prazo_vencido_ativo_true=1)
- `Eureka Network`: total=5 (setor_estrategico_muito_amplo=5)
- `Petrobras`: total=4 (suspeito_ativo_true=4)
- `BASA`: total=3 (suspeito_ativo_true=3)
- `DIU`: total=3 (setor_estrategico_muito_amplo=3)
- `European Defence Fund`: total=3 (setor_estrategico_muito_amplo=3)
- `IPEN`: total=3 (setor_estrategico_muito_amplo=2, credito_tipo_recurso_incoerente=1)
- `Lockheed Martin Suppliers`: total=3 (suspeito_ativo_true=3)
- `Ministério da Defesa`: total=3 (setor_estrategico_muito_amplo=3)
- `Mitsubishi Heavy Industries (Suppliers)`: total=3 (setor_estrategico_muito_amplo=3)
- `SENAI`: total=3 (suspeito_ativo_true=2, setor_estrategico_muito_amplo=1)
- `AFWERX`: total=2 (setor_estrategico_muito_amplo=2)
- `ANEEL`: total=2 (setor_estrategico_muito_amplo=2)
- `ANP`: total=2 (prazo_vencido_ativo_true=2)
- `BADESUL`: total=2 (suspeito_ativo_true=2)
- `BAE Systems Suppliers`: total=2 (suspeito_ativo_true=2)
- `EIT`: total=2 (suspeito_ativo_true=2)
- `Rheinmetall Suppliers`: total=2 (suspeito_ativo_true=2)
- `Softex`: total=2 (suspeito_ativo_true=2)
- `BDMG`: total=1 (prazo_vencido_ativo_true=1)
- `CNEN`: total=1 (setor_estrategico_muito_amplo=1)
- `CONFAP`: total=1 (setor_estrategico_muito_amplo=1)
- `DARPA Opportunities`: total=1 (setor_estrategico_muito_amplo=1)
- `ELETRONUCLEAR`: total=1 (setor_estrategico_muito_amplo=1)
- `ESA OSIP`: total=1 (suspeito_ativo_true=1)
- `FAPEMIG`: total=1 (credito_tipo_recurso_incoerente=1)
- `FAPERGS`: total=1 (credito_tipo_recurso_incoerente=1)
- `Ministério da Saúde`: total=1 (setor_estrategico_muito_amplo=1)
- `NATO DIANA`: total=1 (prazo_vencido_ativo_true=1)
- `Thales Suppliers`: total=1 (suspeito_ativo_true=1)
- `UKRI Funding`: total=1 (suspeito_ativo_true=1)

## Views

- `vw_editais_front`: ok=True accessible=True sample=5
- `vw_editais_admin`: ok=True accessible=True sample=5
- `vw_noticias_front`: ok=True accessible=True sample=5
- `vw_pesquisas_front`: ok=True accessible=True sample=5

## Recomendações

- Usar warnings para priorizar limpeza, ajustes de classificação e filtros de frontend.
- Frontend deve ocultar ativo=false por padrão e expor badges para acesso limitado/fonte experimental.