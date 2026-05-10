# IAEA Wave 1 — curadoria final (pré-apply)

- **Gerado:** `2026-05-05` (artefato local; **apply não executado**).
- **Fonte:** `iaea_news_publications` · **Onda:** `iaea_wave1`.
- **Contexto:** 45 standardized → 5 notícias + 14 pesquisas nos payloads; 2 review; 24 rejeitados; dry-run loader com `errors_count = 0`.

---

## 1. Review candidates (2)

### 1. Call for Applications: ICTP-IAEA Nuclear Stakeholder Engagement School

| Campo | Valor |
|--------|--------|
| **Link** | http://www.iaea.org/newscenter/news/call-for-applications-ictp-iaea-nuclear-stakeholder-engagement-school |
| **Motivo (pipeline)** | `iaea_oportunidade_acionavel_titulo_ou_url` |
| **Data** | 2026-04-07 |

- **Oportunidade acionável?** Sim (convite a candidaturas).
- **Pesquisa/publicação?** Não.
- **Notícia editorial?** Não no sentido de comunicado passivo; é chamada.
- **Manter fora do payload notícia/pesquisa?** Sim.
- **Mover para pesquisa / notícia?** Não.
- **Manter como review_for_edital futuro?** Sim — revisão humana; não carregar neste apply.

---

### 2. IAEA Symposium on International Safeguards 2026: Call for Papers and Student Competition

| Campo | Valor |
|--------|--------|
| **Link** | http://www.iaea.org/newscenter/news/iaea-symposium-on-international-safeguards-2026-call-for-papers-and-student-competition |
| **Motivo (pipeline)** | `iaea_oportunidade_acionavel_titulo_ou_url` |
| **Data** | 2026-04-09 |

- **Oportunidade acionável?** Sim (call for papers / competição).
- **Pesquisa/publicação?** Não como registo de publicação já existente no catálogo.
- **Notícia?** Não como único destino seguro neste módulo.
- **Manter fora dos payloads?** Sim.
- **Manter como review_for_edital futuro?** Sim.

---

## 2. Rejeitados (24) — resumo

| Motivo (pipeline) | Quantidade |
|--------------------|------------|
| `resumo_curto` | 23 |
| `descricao_curta` | 1 |

**Classificação curatorial (agregada):**

| Categoria | N |
|-----------|---|
| Resumo fraco / RSS sem corpo (notícia) | 23 |
| Descrição insuficiente (título curto em publicação) | 1 |
| Genérico (hub) | 0 |
| Ambíguo notícia vs pesquisa | 0 |
| Oportunidade não captada na rota review | 1 (ver nota) |
| Outro | 0 |

**Nota:** *Uranium Mine Challenge: Call for Student Submissions* foi rejeitado por `resumo_curto`, embora o título sugira oportunidade — **não reincluir automaticamente**; numa próxima iteração pode alinhar-se às mesmas frases que enviam itens para `review_for_edital`.

### Amostra (10 itens)

1. Chornobyl 40 Years: Improved International Cooperation — `resumo_curto` — multimédia.
2. How Nuclear Science Helps Tackle Food Waste — `resumo_curto` — notícia.
3. IAEA Rays of Hope… Sudan — `resumo_curto` — press release.
4. Update 348 – Ukraine — `resumo_curto` — press release.
5. Japan… ALPS Treated Water… — `resumo_curto` — press release.
6. New Research Project on… Crop Diseases — `resumo_curto` — notícia.
7. Six Ways the IAEA Supports Global Health… — `resumo_curto` — notícia.
8. Uranium Mine Challenge: Call for Student Submissions — `resumo_curto` — *oportunidade potencial*.
9. Strengthening Collaborative Water Resource Management in Africa — `resumo_curto` — notícia.
10. Food Safety and Control — `descricao_curta` — publicação com título curto.

**Reinclusão futura (sem automação):** a maioria dos 23 com `resumo_curto` é **conteúdo IAEA útil** após enriquecimento de página ou resumo manual; press releases Ucrânia e vídeos Chornobyl são **candidatos fortes** a uma segunda onda. Nada disto entra no apply atual.

---

## 3. Payload notícia (5) — confirmação

| # | Título (abrev.) | Data | Resumo ≥40 |
|---|-----------------|------|--------------|
| 1 | Ecuador and Panama… Cultural Heritage | 2026-04-08 | Sim |
| 2 | IAEA Delivers Report to Viet Nam… | 2026-04-22 | Sim |
| 3 | IAEA ZODIAC Week… | 2026-04-29 | Sim (`&nbsp;` residual possível) |
| 4 | Nuclear Techniques Help Liberia… | 2026-04-29 | Sim |
| 5 | Singapore Signs… CPF… | 2026-04-23 | Sim |

- **Link, `fonte`, `fonte_recurso`:** coerentes (`iaea_news_publications`).
- **`tipo_conteudo`:** `noticia` em todos.
- **Observação:** todos trazem `tipo_pesquisa: relatorio_tecnico` no JSON — **redundante** para notícia; cosmético; opcional remover numa refinagem antes do apply.

---

## 4. Payload pesquisa (14) — confirmação

- **`tipo_conteudo`:** `pesquisa` · **`tipo_pesquisa`:** `relatorio_tecnico` · **`data_publicacao`:** presente em todos (sem justificativa extra necessária).
- **`fonte_recurso`:** `iaea_news_publications` em todos.
- **Fallback de título:** as **14** entradas têm `extras.iaea_descricao_fallback_titulo: true` — `descricao`/`resumo` repetem o **título oficial** (feed sem descrição). Adequado como registo Wave 1 de catálogo; **recomenda-se** enriquecimento futuro (página / PDF) antes de considerar isto “conteúdo rico”.

Lista de links com fallback: ver array `links_com_iaea_descricao_fallback_titulo_true` em `iaea_wave1_curadoria.json`.

---

## 5. Recomendação final

| | |
|--|--|
| **`apto_apply_staging`** | **`true`** |
| **Escopo do apply** | Apenas **5** linhas em `public.noticia` + **14** em `public.pesquisa` conforme payloads atuais. |
| **Fora do apply** | **2** review candidates · **24** rejeitados. |
| **`public.edital`** | Nada deste fluxo. |
| **Gates globais** | Não alterados nesta curadoria. |

**Condições:** confirmar `errors_count == 0` no último `load_news_research_summary.json` após qualquer alteração aos JSON; manter apply **manual** e com guardas de staging já existentes no projeto.

**Paralelo JSON:** `audit_reports_news_research_loader/iaea_wave1_curadoria.json`.
