# Wave 2 — Residências / Formação — Decisão do piloto

**Data:** 2026-05-16  
**Módulo:** Concursos & Seleções (`public.concurso_selecao`)  
**Apply:** não executado nesta wave

---

## Objetivo

Escolher a primeira fonte piloto de **residências** e **programas de formação** com crawler, standardized JSON e dry-run do loader — sem alterar schema, frontend, `public.edital` ou Radar.

---

## Critérios de seleção

| Critério | Peso |
|----------|------|
| Alinhamento residência tecnológica / TIC / software | Alto |
| Página oficial + hub com links para editais | Alto |
| `data_fim_inscricao` e PDF possíveis no HTML/PDF | Alto |
| Baixo ruído (não misturar com notícias genéricas) | Alto |
| HTTP estável + robots permissivo | Médio |
| Oportunidade ativa ou futura | Médio |

---

## Candidatas avaliadas

| Fonte | Prós | Contras | Decisão |
|-------|------|---------|---------|
| **EmbarcaTech (Softex)** | Hub nacional RT embarcados/IoT; IFs com editais PDF; bolsa em HTML; programa claro | Ciclos 2024 encerrados; agregador multi-IF; muitos descartes por recência | **Piloto** |
| **BRISA (RESTIC)** | Residência TIC alinhada; editais por UF | Portal inscrição só login; DNS instável (UFG); alta fragmentação | Latente |
| **CI-Expert (Softex)** | RT microeletrônica | Landing mínima; detalhe em terceiros | Latente |
| **CAPES** | Residência médica estruturada | Ruído pós-graduação/bolsas; não é RT/TIC | Notícias / wave saúde |
| **MCTI / CNPq / FINEP** | Chamamentos com edital | Escopo pesquisa/inovação; não residência profissional típica | Latente / manual |
| **MEC (PROUNI/FIES/SISU)** | Datas nacionais | Não é residência (`tipo_selecao` diferente) | Fora do escopo residências |
| **Residências saúde / multiprofissional** | Volume alto | Curadoria e ruído muito altos | Wave dedicada futura |

---

## Fonte escolhida

**EmbarcaTech — Programa Softex de residência tecnológica**

| Item | Valor |
|------|--------|
| `fonte` | `embarcatech` |
| Hub | https://embarcatech.softex.br/inscricoes/ |
| Crawler | `concursos/main_residencias_embarcatech.py` |
| `tipo_selecao` | `residencia` |
| `categoria` | `residencia_tecnologica` |
| Artefatos | `audit_reports_main_pipeline/concursos_wave2_residencias_embarcatech/` |

---

## Resultado esperado do piloto

- Fonte **implementada** no pipeline (crawler + loader dry-run).
- Maioria dos itens **`incompleto`** ou **descartados** enquanto não houver ciclo com inscrições futuras + PDF — comportamento correto.
- **0 apply** até existir registo `valido` (`link_edital` + `data_fim_inscricao`).

---

## Próximo piloto sugerido

1. **BRISA** — listagem pública por campus/UF quando RESTIC expuser editais sem login.
2. **Softex editais gerais** — filtrar só chamadas com «residência tecnológica».
3. **CAPES** — subset residência médica (wave saúde, `categoria=residencia_saude`).

Ver [CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md](./CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md) e [CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md](./CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md).
