# Wave 2 — Militar / Aeroespacial — Mapeamento de fontes (IME e ITA)

Sub-wave do módulo **Concursos & Seleções** para ingresso, formação e pesquisa em defesa/aeroespacial.

**Pilotos implementados:** [ITA Vestibular](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_ITA_CRAWLER.md) (`fonte=ita`), [IME](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_IME_CRAWLER.md) (`fonte=ime`).

---

## Resumo executivo

| Instituição | Piloto | Motivo |
|-------------|:------:|--------|
| **ITA** | **Sim** | `vestibular.ita.br` acessível; edital PDF + cronograma de provas no HTML |
| **IME** | **Sim** | SSL + Joomla; CFG/CFrm/CG/CP; PDFs escaneados → incompleto sem `data_fim` |

---

## IME — Instituto Militar de Engenharia

| URL | Tipo técnico | Classificação | Datas / edital | Crawler |
|-----|--------------|---------------|----------------|---------|
| [inscricoes.ime.eb.br](https://inscricoes.ime.eb.br/) | HTML (landing SPA/hash) | **concurso_selecao** (hub) | Links para processos; sem datas na home | **Futuro** — hub |
| [CFG inscrições](https://www.ime.eb.mil.br/vestibular-e-concursos/cfg-ensino-medio/inscricoes) | Joomla HTML | **concurso_selecao** | PDFs `CFG ATIVA/RESERVA 2026.pdf` | **Implementado** |
| [CFRM informações](https://www.ime.eb.mil.br/vestibular-e-concursos/cfrm/informacoes-cfrm) | Joomla HTML | **concurso_selecao** | `CFORM 2026.pdf` | **Implementado** |
| [CP-IME](https://www.ime.eb.mil.br/vestibular-e-concursos/cp-ime) | Joomla HTML | **programa_formacao** | Calendário 2026; 90 vagas HTML | **Implementado** |
| [CG informações](https://www.ime.eb.mil.br/vestibular-e-concursos/cg/informacoes-gerais-cg) | Joomla HTML | **concurso_selecao** | MIC EQA + calendário (legislação) | **Implementado** |

**Mapeamento `tipo_selecao` / `categoria` (IME):**

| Processo | `tipo_selecao` | `categoria` sugerida |
|----------|----------------|----------------------|
| CFG (Ensino Médio) | `vestibular` ou `programa_ingresso` | `militar_aeroespacial_ime_cfg` |
| CG (Oficiais AMAN) | `programa_ingresso` | `militar_aeroespacial_ime_cg` |
| CFrm (nível superior) | `programa_ingresso` | `militar_aeroespacial_ime_cfrm` |

**Notas:** certificado SSL do domínio `.mil.br` pode exigir contexto SSL explícito no crawler (como no piloto ITA). Não há `robots.txt` útil em todos os hosts.

---

## ITA — Instituto Tecnológico de Aeronáutica

| URL | Tipo técnico | Classificação | Datas / edital | Crawler |
|-----|--------------|---------------|----------------|---------|
| [vestibular.ita.br](https://www.vestibular.ita.br/) | Frameset HTML | **concurso_selecao** | `principal.htm` + `topo.htm` | **Piloto** |
| [ita.br/grad](http://www.ita.br/grad) | Drupal HTML | misto | Notícias de editais de transferência; resultados | Latente / notícias |
| [ita.br/posgrad](http://www.ita.br/posgrad) | Drupal HTML | **programa_ingresso** / pesquisas | Processos seletivos Mestrado/Doutorado | Latente |
| [ita.br/especializacao](http://www.ita.br/pt-br/especializacao) | Drupal HTML | **programa_ingresso** | Cursos lato sensu | Latente |
| [ita.br/pibic](http://www.ita.br/pibic) | Drupal HTML | **bolsa_estudo** | PAIC/PIBIC | Pesquisas (fora de concurso_selecao) |
| [ita.br/extensao](http://www.ita.br/extensao) | Drupal HTML | **programa_formacao** | Extensão | Latente / notícias |

**Piloto ITA:** `principal.htm` (Vestibular 2027, provas set/out 2026) + edital PDF em `instrucoes/edital_2026_retificado.pdf`.

---

## Decisão do piloto

**Fonte escolhida: ITA Vestibular** (`vestibular.ita.br`)

| Critério | ITA | IME |
|----------|-----|-----|
| Edital PDF oficial | Sim (topo) | Sim (CFG 2026 por processo) |
| Datas no HTML | Provas 1ª/2ª fase | Poucas na listagem |
| Complexidade | Frameset legado, 2 páginas | Hub + 3 processos + Joomla |
| Acesso HTTP | Estável | SSL `.mil.br` |

Crawler IME (`fonte=ime`): **5 registros** — CFG ATIVA, CFG RESERVA, CFrm, CG, CP/IME — ver [CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_IME_CRAWLER.md](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_IME_CRAWLER.md).

---

## Convenções `public.concurso_selecao`

| Tipo de página | `tipo_selecao` típico |
|----------------|------------------------|
| Vestibular ITA/IME | `vestibular` |
| Pós / especialização | `programa_ingresso` |
| PIBIC / PAIC | `bolsa_estudo` |
| Residência / formação técnica militar | `residencia` ou `programa_formacao` |

`fonte_tipo` para instituições: **`instituicao`** (não banca organizadora).

---

## Artefatos

| Item | Caminho |
|------|---------|
| Crawler ITA | `concursos/main_militar_aeroespacial_ita.py` |
| Crawler IME | `concursos/main_militar_aeroespacial_ime.py` |
| Relatórios ITA | `audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ita/` |
| Relatórios IME | `audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ime/` |
