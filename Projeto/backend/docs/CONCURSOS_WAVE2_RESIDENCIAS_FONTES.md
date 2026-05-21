# Wave 2 — Residências e Programas de Formação (mapeamento de fontes)

Mapeamento para o módulo **Concursos & Seleções** (`public.concurso_selecao`), sem alterar `public.edital` ou Radar.  
Tipos suportados pelo loader: `residencia`, `programa_ingresso`, `bolsa_estudo`, etc.

**Piloto implementado:** [EmbarcaTech / Softex](./CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md) — decisão em [CONCURSOS_WAVE2_RESIDENCIAS_PILOT_DECISION.md](./CONCURSOS_WAVE2_RESIDENCIAS_PILOT_DECISION.md).

---

## Resumo executivo

| Prior. | Fonte | Recomendação | Piloto |
|:------:|-------|--------------|:------:|
| 1 | EmbarcaTech (Softex) | **Crawler** | **Sim** |
| 2 | BRISA / residência TIC UF | Crawler (latente) | Não |
| 3 | Softex editais / CI-Expert | Crawler | Não |
| 4 | IFs — RT regional | Crawler por edital | Não |
| 5 | CAPES / residência médica | Manual + wave saúde | Não |
| 6 | MCTI / CNPq / FINEP | Latente / API parcial | Não |
| 7 | MEC PROUNI/FIES/SISU | Não usar (ingresso) | Não |
| 8 | Residências saúde / multiprofissional | Wave dedicada | Não |
| 9 | Hospitais universitários | Manual / latente | Não |
| 10 | Residência pedagógica | Latente | Não |

---

## Tabela por fonte candidata

Colunas: **Recom.** = crawler | manual | API | latente | notícias (só Oportunidades, não `concurso_selecao`).

| Fonte | URL / base | Tipo | Prior. | Dific. | Campos | Edital | Inscrição / fim | Ruído | Recom. |
|-------|------------|------|:------:|:------:|--------|:------:|:---------------:|-------|--------|
| **Softex — EmbarcaTech** | [embarcatech.softex.br/inscricoes](https://embarcatech.softex.br/inscricoes/) | RT / TIC embarcados | **1** | Média | título, IF, bolsa, PDF, datas | Sim | Sim (IF) | Médio | **crawler** |
| **Softex — editais** | [softex.br/editais-e-chamadas](https://softex.br/editais-e-chamadas/) | RT, convênios | 2 | Média | PDF, órgão | Sim | Variável | Alto | crawler |
| **Softex — CI-Expert** | [ciexpert.irede.org.br](https://ciexpert.irede.org.br/) | RT microeletrônica | 2 | Alta | bolsa, vagas | Parcial | Sim | Médio | latente |
| **BRISA** | [brisabr.com.br](https://www.brisabr.com.br/) · [RESTIC](https://inscricoesrestic.brisabr.com.br/) | RT TIC | 2 | Alta | edital, bolsas | Sim | Sim* | Médio | latente |
| **BRISA-UFG / UECE** | residenciaemtic.inf.ufg.br, notícias UECE | RT TIC regional | 3 | Alta | idem | Sim | Sim | Médio | crawler |
| **Residência TIC/software** | EmbarcaTech, BRISA, IFs | Formação TIC | **1** | — | — | — | — | — | ver piloto |
| **Residência tecnológica (IFs)** | Portais IF estaduais/federais | RT | 2 | Média | edital IF | Sim | Sim | Médio | crawler |
| **MCTI** | [gov.br/mcti](https://www.gov.br/mcti/pt-br) | Chamamentos, inovação | 3 | Alta | edital | Sim | Sim | Alto | latente |
| **MEC** | [gov.br/mec](https://www.gov.br/mec/pt-br) | PROUNI, FIES, SISU | 3 | Alta | calendário | Às vezes | Sim | **Alto** | notícias |
| **CAPES** | [gov.br/capes](https://www.gov.br/capes/pt-br) | Res. médica, bolsas, pós | 3 | Alta | programa | Sim | Sim | Alto | latente |
| **CNPq** | [gov.br/cnpq](https://www.gov.br/cnpq/pt-br) | Chamadas pesquisa | 4 | Alta | edital | Sim | Sim | Alto | latente |
| **FINEP** | [gov.br/finep](https://www.gov.br/finep/pt-br) | Financiamento / inovação | 4 | Alta | edital chamada | Sim | Sim | Alto | latente |
| **Residência saúde** | Hospitais, SES, COREME | RT médica / multiprof. | 5 | Muito alta | CRM, especialidade | Sim | Sim | Muito alto | manual |
| **Residência multiprofissional** | Universidades, SUS | Saúde coletiva | 5 | Muito alta | edital | Sim | Sim | Muito alto | wave futura |
| **Hospitais universitários** | HC-FMUSP, HU-UF*, etc. | RT clínica | 5 | Alta | edital COREME | Sim | Sim | Alto | manual |
| **Universidades federais/estaduais** | Pró-reitorias, editais RT | RT / estágio | 3 | Média | por edital | Sim | Sim | Médio | crawler |
| **Programas estaduais formação** | SECTI, Softex estadual | RT / qualificação | 3 | Média | por UF | Sim | Sim | Médio | crawler |
| **Residência pedagógica** | Secretarias estaduais educação | Formação docente | 4 | Alta | edital | Sim | Sim | Médio | latente |
| **Formação profissional c/ edital** | Senai, Senac, IFs | Capacitação | 3 | Média | curso, vagas | Sim | Sim | Médio | crawler |

\* BRISA: portal de inscrição sem listagem pública (apenas login).

---

## Escolha do piloto (resumo)

**EmbarcaTech (Softex)** — residência tecnológica nacional (sistemas embarcados / IoT).

Motivos: hub oficial, editais por IF executor, bolsa e cronograma em HTML/PDF, alinhamento TIC, HTTP viável.  
Limitação: muitos ciclos 2024 encerrados → crawler latente até novo edital com datas futuras.

---

## Convenções `public.concurso_selecao` (Wave 2 Residências)

| Campo | Convenção |
|-------|-----------|
| `tipo_selecao` | `residencia` ou `programa_ingresso` (formação com ingresso) |
| `categoria` | `residencia_tecnologica` \| `residencia_saude` \| `residencia_multiprofissional` \| `programa_formacao` |
| `validacao_status` | `valido` iff `link_edital` + `data_fim_inscricao` |
| Bolsa/auxílio | `salario_min` / `salario_max` + `extras.valor_tipo` = `bolsa` ou `auxilio` |
| Notícia sem inscrição | Não gravar em `concurso_selecao` → candidata **Notícias/Oportunidades** |

---

## Diferencial do módulo

Residências e programas de formação ampliam o Edital Finder além de concursos públicos e vestibulares: mesma tabela, abas **Residências** e filtros por `tipo_selecao` / `categoria` na UI (`/concursos`).

---

## Artefatos

| Item | Caminho |
|------|---------|
| Decisão piloto | `docs/CONCURSOS_WAVE2_RESIDENCIAS_PILOT_DECISION.md` |
| Crawler piloto | `concursos/main_residencias_embarcatech.py` |
| Doc piloto | `docs/CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md` |
| Relatórios | `audit_reports_main_pipeline/concursos_wave2_residencias_embarcatech/` |
| Consolidado Wave 1 | `audit_reports_main_pipeline/concursos_wave1_consolidado.md` |
