# Notícias e Pesquisas Estratégicas — Mapeamento de fontes (Defesa / Aeroespacial / Tecnologia)

Documento de **classificação e roteamento** para a frente **Notícias** e **Pesquisas** do EditalFinder.  
**Não implementa crawlers** — apenas decisão de produto, prioridade e fronteiras com Editais, Radar e Concursos.

**Inventário backend (todas as frentes):** [`BACKEND_SOURCES_INVENTORY.md`](./BACKEND_SOURCES_INVENTORY.md) · [`BACKEND_SOURCES_INVENTORY.json`](./BACKEND_SOURCES_INVENTORY.json)

**Contexto relacionado:**

| Frente | Estado |
|--------|--------|
| Concursos & Seleções — sub-wave Militar/Aeroespacial | ITA (`fonte=ita`) e IME (`fonte=ime`) **implementados** — ver [CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md) |
| Módulo news/research (NASA, DARPA, IAEA, EurekAlert) | Pipeline em `config/news_research_sources.json` + `scripts/crawl_news_research_sources.py` — **fora do escopo desta lista**, mas mesma governança |

**Governança (herdada do módulo news/research):**

- **Janelas públicas (produto):** notícias **12 meses**, pesquisas/artigos **24 meses** — histórico mantido no banco; filtro nas views `vw_noticias_front` / `vw_pesquisas_front`. Detalhe: [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) §2–3.
- Itens de **notícia/pesquisa** não entram em `public.edital` sem revisão explícita.
- Chamadas com edital/BAA/RFI forte → fila **review_for_edital** / Radar, não feed de notícias.
- Sem varredura agressiva de site inteiro; apenas seeds declarados; respeitar robots e políticas de acesso.
- **Sem apply** até dry-run + auditoria por onda.

---

## Legenda de classificação

Cada fonte recebe uma ou mais etiquetas de **tipo de oportunidade de conteúdo**:

| Etiqueta | Significado |
|----------|-------------|
| **notícias** | Comunicados, matérias, releases, agenda institucional |
| **pesquisas** | Projetos, laboratórios, artigos, programas de P&D, relatórios técnicos |
| **oportunidades** | Fomento, chamadas, editais genéricos, procurement, bolsas abertas |
| **editais/chamadas** | Edital formal com prazo/inscrição (candidato a Radar/Editais após revisão) |
| **concursos/seleções** | Vestibular, processo seletivo, ingresso, formação militar |
| **fonte latente** | Útil no mapa estratégico; crawler **não** prioritário agora |
| **não recomendado** | Baixo sinal, marketing estático, risco legal/técnico, ou duplicado |

**Rotas do produto** (onde o item deve aparecer, em tese):

| Rota | Uso |
|------|-----|
| **Notícias** | Aba `/noticias` → `public.noticia` |
| **Pesquisas** | Aba `/pesquisas` → `public.pesquisa` |
| **Editais** | Módulo Editais / oportunidades com prazo |
| **Radar** | Fomento estratégico, match com perfil (quando classificado como oportunidade) |
| **Concursos & Seleções** | Aba `/concursos` → `public.concurso_selecao` |

---

## Categorias estratégicas (taxonomia transversal)

Usar uma ou mais tags por fonte (e depois por item, no crawler):

| Categoria | Exemplos de conteúdo esperado |
|-----------|------------------------------|
| **Defesa** | EB, DefesaNet, MCTI defesa, DARPA-like contexto BR |
| **Aeroespacial** | ITA, Lockheed aeronautics, F-35 (referência) |
| **Guerra eletrônica** | Lab. GE ITA |
| **Materiais avançados** | Projetos ITA, indústria de defesa |
| **Física aplicada** | PIBIC, projetos, CAPES |
| **Química aplicada** | Projetos, energia |
| **Computação/IA/Cyber** | Transformação digital MCTI, multidomínio |
| **Engenharia** | IME/ITA, SOFTEX, fornecedores LM |
| **Energia/Nuclear** | Fomento MCTI, IAEA (módulo já existente) |
| **Indústria estratégica** | SOFTEX, Lockheed suppliers, Brisa |
| **Formação militar/científica** | CAPES, PIBIC, pós ITA, concursos IME/ITA |

---

## Tabela por fonte (lista fornecida)

### 1. Portal do Exército Brasileiro

**Status piloto (2026-05-17):** `source_id=exercito_brasileiro` via listagem HTML Liferay (`/web/guest` + `/web/guest/noticiario-do-exercito`); detalhe `/web/noticias/w/{slug}`; dry-run em `audit_reports_news_research/exercito_brasileiro_dryrun/`; **sem apply**. Sem RSS útil; **10/10 na janela 12m** na última corrida.

| Campo | Valor |
|-------|--------|
| **URL** | https://www.eb.mil.br/web/guest |
| **Classificação** | **notícias** (primário); **oportunidades** (secundário — avisos/comunicados); **fonte latente** para editais formais (concursos IME têm portal próprio) |
| **Tema principal** | Notícias e comunicação institucional do Exército; contexto para IME/EB |
| **Categorias estratégicas** | Defesa, Formação militar/científica, Engenharia |
| **Prioridade** | **Alta** (BR, alinhamento IME/CFG) |
| **Dificuldade técnica** | **Média–alta** — Liferay, `.mil.br` (SSL como IME), possível fragmentação de seções |
| **Frequência provável** | Diária a semanal (notícias); editais esporádicos |
| **Tipo de conteúdo** | HTML institucional, listagens de notícias, PDFs pontuais |
| **Rota do produto** | **Notícias** (principal); Radar só se item for claramente chamada com prazo |
| **Notas** | Não duplicar processos CFG/CFrm/CG já cobertos em Concursos (`fonte=ime`). Crawler dedicado: hub de notícias EB, não vestibular. |

---

### 2. DefesaNet

**Status piloto (2026-05-17):** crawler via pipeline genérico (`config/news_research_sources.json` → `defesanet`); dry-run em `audit_reports_news_research/defesanet_dryrun/`; **sem apply**.

| Campo | Valor |
|-------|--------|
| **URL** | https://www.defesanet.com.br/ |
| **Classificação** | **notícias** |
| **Tema principal** | Agregador/editorial de defesa, geopolítica e indústria de defesa (BR) |
| **Categorias estratégicas** | Defesa, Aeroespacial, Indústria estratégica |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média** — listagem HTML; verificar robots e rate limit |
| **Frequência provável** | Diária |
| **Tipo de conteúdo** | Artigos, notícias curtas, links externos |
| **Rota do produto** | **Notícias** |
| **Notas** | Boa primeira wave: alto sinal, formato próximo de feed editorial. |

---

### 3. Lockheed Martin — F-35 News & Features

| Campo | Valor |
|-------|--------|
| **URL hub** | https://www.f35.com/f35/news-and-features.html |
| **Feed JSON** | https://www.f35.com/content/lockheed-martin/data/feeds/f35feed.json (`data-path` no hub) |
| **`source_id`** | `f35_news` |
| **Classificação** | **notícias** — piloto internacional **implementado** (dry-run) |
| **Tema principal** | Notícias e features do programa F-35 (operações, produção, alianças, treinamento) |
| **Categorias estratégicas** | Aeroespacial, Defesa, Aviação militar, Indústria estratégica |
| **Prioridade** | **Média** (wave internacional defesa/aero) |
| **Dificuldade técnica** | **Média** — hub HTML é SPA (Algolia InstantSearch); **sem RSS**; listagem estável via JSON AEM |
| **Frequência provável** | Média (~80 itens/12m no feed; cap piloto `max_items=10`) |
| **Tipo de conteúdo** | News, Feature, 3rd Party Article (tags no feed) |
| **Rota do produto** | **Notícias** (`tipo_conteudo=noticia`, `public.noticia` após apply explícito) |
| **robots.txt** | https://www.f35.com/robots.txt — sem `Disallow` em `/f35/`; respeitar rate limit |
| **Copyright** | Resumo `Description` do feed + enrich opcional `og:description`; **sem** corpo integral |
| **Notas** | Index/marketing estático (`/f35/index.html`) continua fora do crawl; apenas URLs em `/f35/news-and-features/`. Dry-run: `audit_reports_news_research/f35_news_dryrun/` (10/10 válidos, 12m). **Sem apply** até decisão de produto. |

**Diagnóstico técnico (2026-05-18):**

| Aspeto | Resultado |
|--------|-----------|
| RSS | Não encontrado |
| Listagem | JSON estático `f35feed.json` (302 itens no arquivo; ~81 na janela 12m) |
| Hub HTML | SPA + Algolia (conteúdo carregado via feed JSON, não scrape do DOM) |
| `data_publicacao` | Campo `Date` (RFC822) |
| `imagem_url` | `Thumbnail Image` (absolutizado) |
| `autor` / `fonte` | F-35 / Lockheed Martin (metadado) |

---

### 4. Lockheed Martin — Newsroom (corporativo, filtro técnico)

| Campo | Valor |
|-------|--------|
| **URL hub** | https://www.lockheedmartin.com/en-us/news.html |
| **Feed JSON** | https://www.lockheedmartin.com/content/lockheed-martin/data/feeds/newsfeed.json |
| **`source_id`** | `lockheed_martin_news` |
| **Classificação** | **notícias** — piloto internacional **implementado** (dry-run, filtro forte) |
| **Tema principal** | Press releases e features com relevância defesa/aero/espaço/engenharia |
| **Categorias estratégicas** | Defesa, Aeroespacial, Espaço, Sensores/Radar, Guerra eletrônica, IA/Cyber, Materiais, Hipersônicos |
| **Prioridade** | **Média** (corporativo; lote controlado obrigatório) |
| **Dificuldade técnica** | **Média** — SPA Algolia + feed JSON; sem RSS |
| **Frequência provável** | Alta no feed (~380/12m); **max_items=10** no piloto |
| **Rota do produto** | **Notícias** após subset + apply explícito |
| **Rotas excluídas** | `/capabilities/`, `/suppliers/` → institucional/Radar; MDO/engineering procurement → não notícia automática |
| **Filtros** | `require_any_keyword` (defense, aerospace, missile, AI, …); `exclude_keywords` (investor, careers, philanthropy); Supplier/3rd Party/Statement → `review_candidates.json` |
| **Notas** | Dry-run `lockheed_martin_news_dryrun/` — 10/10 válidos; ~162 elegíveis técnicos/12m no feed. **Não apply** sem subset (como F-35 top 20). |

**Diagnóstico (2026-05-18):** feed total ~2756; 381 na janela 12m (bruto); 10 standardized após filtros. URLs: `news.lockheedmartin.com` e `/en-us/news/features|press`. robots: `Disallow` parcial em paths `/en-us/news/news-releases` — feed JSON ainda utilizável.

---

### 4b. U.S. Department of Defense / War.gov — News (oficial governamental)

| Campo | Valor |
|-------|--------|
| **URL hub** | https://www.war.gov/news/ |
| **RSS News Stories** | `https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945&max=100` (redireciona para war.gov) |
| **`source_id`** | `war_gov_news` |
| **`fonte` (exibição)** | U.S. Department of Defense / War.gov |
| **`fonte_recurso`** | `war_gov_news` |
| **Classificação** | **notícias** — fonte **oficial governamental** EUA (não jornalismo independente) |
| **Tema principal** | Defesa, tecnologia militar, IA/cyber, espaço, autonomia, indústria de defesa |
| **Prioridade** | **Alta** (complementa F-35, DARPA, LM com voz institucional DoD) |
| **Dificuldade técnica** | **Média** — hub/artigo HTML podem 403; RSS ArticleCS estável; resumo do feed |
| **Rota do produto** | **Notícias** (`tipo_conteudo=noticia`) após subset + apply explícito |
| **Seções hub** | News Stories → principal; Features → permitido se técnico; From the Services → filtro forte; Press Products / Speeches / Biographies / Publications / Live Events → descartados ou fase futura |
| **Filtros** | Positivos: defense tech, AI, cyber, space, drones, hypersonic, sensors, NATO/deterrence com conteúdo técnico; negativos: ceremony, speech, transcript, travels, media invitation, biography; procurement → review (não vira edital) |
| **Notas** | Dry-run `war_gov_news_dryrun/` — **30 raw → 8 standardized (8 válidos), 22 descartados**, 0 review (2026-05-20). **Sem apply.** Subset top 10–20 recomendado. |

**Diagnóstico técnico (2026-05-20):**

| Aspeto | Resultado |
|--------|-----------|
| Hub HTML | 403 em ambiente automatizado (opcional) |
| RSS | HTTP 200; ContentType=1 = News Stories (`/News/News-Stories/Article/…`) |
| Detalhe HTML | 403 possível; `resumo` via `description` RSS |
| `data_publicacao` | `pubDate` RSS |
| `imagem_url` | `enclosure` / media quando presente |
| robots.txt | https://www.war.gov/robots.txt — validar em staging |

---

### 5. Lockheed Martin — Multi-Domain Operations

| Campo | Valor |
|-------|--------|
| **URL** | https://www.lockheedmartin.com/en-us/capabilities/multi-domain-operations.html |
| **Classificação** | **fonte latente**; **não recomendado** para notícias recorrentes |
| **Tema principal** | Capacidades corporativas (MDO, C4ISR, cyber) — página de capability |
| **Categorias estratégicas** | Defesa, Computação/IA/Cyber, Aeroespacial |
| **Prioridade** | **Baixa** |
| **Dificuldade técnica** | **Baixa** (página única) / **alta** se expandir site |
| **Frequência provável** | Muito baixa |
| **Tipo de conteúdo** | HTML estático, links para outras capabilities |
| **Rota do produto** | **Pesquisas** (apenas se virar seed de PDF/whitepaper linkado); caso contrário nenhuma |
| **Notas** | Útil para taxonomia e curadoria humana, não para crawl de notícias. |

---

### 6. Lockheed Martin — Aeronautics Engineering (Suppliers)

| Campo | Valor |
|-------|--------|
| **URL** | https://www.lockheedmartin.com/en-us/suppliers/business-area-procurement/aeronautics/engineering.html |
| **Classificação** | **oportunidades** (procurement B2B); **fonte latente** |
| **Tema principal** | Informação a fornecedores / engenharia aeronáutica (EUA) |
| **Categorias estratégicas** | Aeroespacial, Indústria estratégica, Engenharia |
| **Prioridade** | **Média** (nicho exportador/fornecedor) |
| **Dificuldade técnica** | **Alta** — site corporativo EN, possível anti-bot, conteúdo não estruturado como edital BR |
| **Frequência provável** | Baixa a média (avisos de procurement) |
| **Tipo de conteúdo** | Páginas de supplier, PDFs, links para portais de compras |
| **Rota do produto** | **Radar** ou **Portais** (fornecedores) numa frente futura; **não** Notícias |
| **Notas** | Fronteira com módulo Fornecedores/Investimentos; não misturar com CAPES/PIBIC. |

---

### 6. ITA — Laboratório de Guerra Eletrônica

| Campo | Valor |
|-------|--------|
| **URL** | http://www.ita.br/laboratorios/guerraeletronica |
| **Classificação** | **pesquisas**; **notícias** (eventos pontuais); **fonte latente** |
| **Tema principal** | Linhas de pesquisa, equipe e produção em guerra eletrônica |
| **Categorias estratégicas** | Guerra eletrônica, Defesa, Engenharia, Computação/IA/Cyber |
| **Prioridade** | **Média–alta** (diferencial estratégico ITA) |
| **Dificuldade técnica** | **Média** — Drupal/ITA; mistura HTTP/HTTPS |
| **Frequência provável** | Baixa a média |
| **Tipo de conteúdo** | Páginas de lab, publicações, possíveis notícias locais |
| **Rota do produto** | **Pesquisas** |
| **Notas** | Complementa `ita.br/projetos`; não confundir com vestibular (`vestibular.ita.br` → Concursos). |

---

### 7. ITA — Projetos

| Campo | Valor |
|-------|--------|
| **URL** | http://www.ita.br/projetos |
| **Classificação** | **pesquisas** |
| **Tema principal** | Projetos de pesquisa e inovação no ITA |
| **Categorias estratégicas** | Engenharia, Aeroespacial, Física aplicada, Materiais avançados, Defesa |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média** |
| **Frequência provável** | Mensal |
| **Tipo de conteúdo** | Listagens de projetos, descrições, links |
| **Rota do produto** | **Pesquisas** |
| **Notas** | Candidato forte à **1ª wave Pesquisas**. |

---

### 8. ITA — PIBIC

| Campo | Valor |
|-------|--------|
| **URL** | http://www.ita.br/pibic |
| **Classificação** | **oportunidades**; **concursos/seleções** (bolsa); **pesquisas** |
| **Tema principal** | Programa Institucional de Bolsas de Iniciação Científica |
| **Categorias estratégicas** | Formação militar/científica, Física aplicada, Engenharia |
| **Prioridade** | **Média** |
| **Dificuldade técnica** | **Média** |
| **Frequência provável** | Anual (ciclos) + notícias de abertura |
| **Tipo de conteúdo** | Editais de bolsa, cronogramas, PDFs |
| **Rota do produto** | **Concursos & Seleções** (`bolsa_estudo`) se houver prazo; senão **Pesquisas** ou **Radar** |
| **Notas** | Já mapeado em [CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md) como latente para concursos. Para esta frente: priorizar **oportunidade/bolsa** com datas, não duplicar notícia genérica. |

---

### 9. ITA — Pós-graduação EMU

| Campo | Valor |
|-------|--------|
| **URL** | http://www.ita.br/posgrad/emu |
| **Classificação** | **pesquisas**; **concursos/seleções** (processo seletivo mestrado/doutorado); **fonte latente** |
| **Tema principal** | Programa de pós-graduação (EMU) — pesquisa aplicada |
| **Categorias estratégicas** | Engenharia, Aeroespacial, Formação militar/científica |
| **Prioridade** | **Média** |
| **Dificuldade técnica** | **Média** |
| **Frequência provável** | Anual / semestral (seleção) |
| **Tipo de conteúdo** | Programas, linhas de pesquisa, editais de seleção |
| **Rota do produto** | **Pesquisas** + **Concursos** quando houver edital de seleção com prazo |
| **Notas** | Alinhar com `ita.br/posgrad` (hub) num único crawler ITA-pós futuro. |

---

### 10. ITA — Extensão

| Campo | Valor |
|-------|--------|
| **URL** | http://www.ita.br/extensao |
| **Classificação** | **pesquisas** (secundário); **notícias**; **fonte latente** |
| **Tema principal** | Cursos e ações de extensão tecnológica |
| **Categorias estratégicas** | Formação militar/científica, Engenharia, Indústria estratégica |
| **Prioridade** | **Baixa–média** |
| **Dificuldade técnica** | **Média** |
| **Frequência provável** | Mensal |
| **Tipo de conteúdo** | Cursos, eventos, notícias de extensão |
| **Rota do produto** | **Notícias** ou **Pesquisas** (eventos formativos); raramente Editais |
| **Notas** | Wave 2+; sinal mais fraco que projetos/PIBIC para estratégia defesa. |

---

### 11. SOFTEX — Notícias

**Status piloto (2026-05-17):** `source_id=softex_noticias` via RSS `https://softex.br/feed/`; dry-run em `audit_reports_news_research/softex_noticias_dryrun/`; **sem apply**. Feed global WordPress (~20 itens no feed; `max_items=10`); **10/10 na janela 12m** na última corrida.

| Campo | Valor |
|-------|--------|
| **URL** | https://softex.br/noticias/ |
| **Classificação** | **notícias** |
| **Tema principal** | Exportação de software e tecnologia brasileira; ecossistema TI |
| **Categorias estratégicas** | Indústria estratégica, Computação/IA/Cyber, Engenharia |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média** — WordPress/CMS comum |
| **Frequência provável** | Semanal |
| **Tipo de conteúdo** | Notícias, programas SOFTEX |
| **Rota do produto** | **Notícias** |
| **Notas** | Boa diversificação além de defesa pura; complementa Brisa/CAPES. |

---

### 12. Brisa BR — Artigos

**Status piloto (2026-05-17):** `source_id=brisa_artigos` via RSS `https://brisabr.com.br/artigos/feed/`; dry-run em `audit_reports_news_research/brisa_artigos_dryrun/`; **sem apply**. Feed ~8 itens; janela **24 meses** (não 12m de notícias). Permalinks WordPress na raiz do domínio (sem `/artigos/` no path).

| Campo | Valor |
|-------|--------|
| **URL** | https://brisabr.com.br/artigos/ |
| **Classificação** | **pesquisas** |
| **Tema principal** | Artigos técnicos (defesa, energia, materiais, inovação) |
| **Categorias estratégicas** | Defesa, Energia/Nuclear, Materiais avançados, Indústria estratégica |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média** |
| **Frequência provável** | Semanal a mensal |
| **Tipo de conteúdo** | Artigos longos, análise |
| **Rota do produto** | **Pesquisas** |
| **Notas** | Par com `/news/` — crawlers podem compartilhar domínio `brisabr.com.br`. |

---

### 13. Brisa BR — News

**Status piloto (2026-05-17):** `source_id=brisa_news` via RSS `https://brisabr.com.br/news/feed/`; dry-run em `audit_reports_news_research/brisa_news_dryrun/`; **sem apply**. Feed publica ~4 itens (volume baixo); `/artigos/` fora do escopo deste source.

| Campo | Valor |
|-------|--------|
| **URL** | https://brisabr.com.br/news/ |
| **Classificação** | **notícias** |
| **Tema principal** | Notícias de defesa, nuclear e tecnologia estratégica (BR) |
| **Categorias estratégicas** | Defesa, Energia/Nuclear, Aeroespacial |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média** |
| **Frequência provável** | Semanal |
| **Tipo de conteúdo** | Notícias curtas |
| **Rota do produto** | **Notícias** |
| **Notas** | Candidata **1ª wave Notícias** (junto com DefesaNet). |

---

### 14. CAPES — Notícias

**Status piloto (2026-05-17):** `source_id=capes_noticias` via RSS `https://www.gov.br/capes/pt-br/assuntos/noticias/rss.xml` (Plone: URL em `<guid>`); dry-run em `audit_reports_news_research/capes_noticias_dryrun/`; **sem apply**. Hub HTML espelha listagem; enrich `.documentPublished` + og:image; janela **12m**.

| Campo | Valor |
|-------|--------|
| **URL** | https://www.gov.br/capes/pt-br/assuntos/noticias |
| **Classificação** | **notícias**; **oportunidades** (secundário — quando notícia anuncia edital) |
| **Tema principal** | Notícias da CAPES (pós, cooperação, fomento à formação) |
| **Categorias estratégicas** | Educação, Ciência, Pós-graduação, Bolsas, Formação, Pesquisa, Internacionalização, Inovação (heurística no texto) |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média** — gov.br/Plone; RSS oficial; robots CAPES permissivo |
| **Frequência provável** | Diária a semanal |
| **Tipo de conteúdo** | Notícias gov.br; links para chamadas |
| **Rota do produto** | **Notícias** (`tipo_conteudo=noticia`); itens com edital embutido → revisão manual futura |
| **Notas** | Feed RSS ordenado por data desc no crawl; resumo RSS/lead sem `content:encoded` integral. |

---

### 15. MCTI — Transformação Digital / Fomento

**Status (2026-05-17):** dry-run Radar **v3** `mcti_fomento_dryrun_v3/` — 5 prontos técnicos, 35 review; **`apply_status`: `não_recomendado`** (itens históricos/encerrados). Infraestrutura crawler+curadoria **pronta**; reexecutar periodicamente. Plano: [MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md](MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md).

| Campo | Valor |
|-------|--------|
| **URL** | https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/fomento-1 |
| **Classificação** | **oportunidades**; **editais/chamadas** (via navegação MCTI, não feed único) |
| **Tema principal** | Hub de fomento (transformação digital, programas MCTI) |
| **Categorias estratégicas** | Computação/IA/Cyber, Indústria estratégica, Energia/Nuclear, Engenharia |
| **Prioridade** | **Alta** |
| **Dificuldade técnica** | **Média–alta** — gov.br/Plone; página hub estática; oportunidades em subpastas e repositório de editais |
| **Frequência provável** | Semanal (aberturas em programas ligados) |
| **Tipo de conteúdo** | Texto explicativo + PDFs + links para programas/editais/chamadas |
| **Rota do produto** | **Radar** / **Editais** (não Notícias); `review_for_edital` antes de `public.edital` |
| **Notas** | Diagnóstico: `run_mcti_fomento_diagnostic.py`. Dry-run v3: `run_mcti_fomento_dryrun_v3.py`. **Apply não recomendado** no lote atual. Não usar crawler de notícias. |
| **apply_status** | `não_recomendado` |
| **próxima_ação** | Reexecutar dry-run v3 periodicamente; apply só se houver chamada ativa |

---

## Fontes já cobertas em Concursos (não replicar em Notícias)

| Instituição | URL / `fonte` | Rota correta |
|-------------|---------------|--------------|
| ITA Vestibular | https://www.vestibular.ita.br/ — `ita` | **Concursos & Seleções** |
| IME CFG / CFrm / CG / CP | `ime.eb.mil.br` + `inscricoes.ime.eb.br` — `ime` | **Concursos & Seleções** |

Itens institucionais genéricos do EB (`eb.mil.br`) **complementam** IME em Notícias, não substituem concursos.

---

## Matriz resumo (classificação × rota)

| Fonte | notícias | pesquisas | oportun. | editais | concursos | latente | não rec. | Rota principal |
|-------|:--------:|:---------:|:--------:|:-------:|:---------:|:-------:|:--------:|----------------|
| EB `eb.mil.br` | ● | | ○ | ○ | | | | Notícias (piloto `exercito_brasileiro`) |
| DefesaNet | ● | | | | | | | Notícias |
| F-35 News & Features | ● | | | | | | | Notícias (`f35_news`) |
| LM Newsroom | ● | | | | | | | Notícias (`lockheed_martin_news`, lote controlado) |
| War.gov / U.S. DoD News | ● | | | | | | | Notícias (`war_gov_news`, oficial governamental) |
| LM MDO | | ○ | | | | ● | ○ | — (capability estática) |
| LM Suppliers | | | ● | | | ● | | Radar (futuro) |
| ITA GE | ○ | ● | | | | ● | | Pesquisas |
| ITA Projetos | | ● | | | | | | Pesquisas |
| ITA PIBIC | ○ | ● | ● | ○ | ● | | | Concursos / Pesquisas |
| ITA EMU | | ● | | | ● | ● | | Pesquisas / Concursos |
| ITA Extensão | ● | ○ | | | | ● | | Latente |
| SOFTEX notícias | ● | | | | | | | Notícias (piloto `softex_noticias`) |
| CAPES notícias | ● | | | | | | | Notícias (piloto `capes_noticias`) |
| Brisa artigos | | ● | | | | | | Pesquisas (piloto `brisa_artigos`) |
| Brisa news | ● | | | | | | | Notícias |
| CAPES notícias | ● | | ○ | ○ | | | | Notícias |
| MCTI fomento | | | ● | ● | | | | Radar / Editais |
| MCTI notícias | ● | | ○ | ○ | | | | Notícias (`mcti_noticias`) |

● = primário | ○ = secundário possível

---

## Recomendação — primeira wave (sem implementação)

Critérios: sinal alto, HTML/RSS viável, alinhamento estratégico BR + defesa/aero, baixa sobreposição com Concursos já implementados, aderência à governança news/research.

### Notícias (3 fontes)

| # | Fonte | `source_id` sugerido | Motivo |
|---|--------|----------------------|--------|
| 1 | **DefesaNet** | `defesanet` | Feed editorial defesa; atualização frequente; formato adequado a `public.noticia` — **piloto implementado** |
| 2 | **Brisa BR — News** | `brisa_news` | **Piloto implementado** — feed `/news/`; institucional/inovação BR |
| 3 | **Exército Brasileiro** (`eb.mil.br` — seção notícias) | `eb_mil_br_noticias` | Ancoragem institucional IME/EB; exige seed explícito (não home genérica) |

**Reserva wave 1b:** CAPES notícias (SOFTEX e EB já com piloto implementado).

### Pesquisas (2 fontes)

| # | Fonte | `source_id` sugerido | Motivo |
|---|--------|----------------------|--------|
| 1 | **ITA — Projetos** | `ita_projetos` | P&D direto; categorias engenharia/defesa |
| 2 | **Brisa BR — Artigos** | `brisa_artigos` | **Piloto implementado** — feed `/artigos/feed/`; aba Pesquisas |

**Reserva wave 1b:** ITA Guerra Eletrônica (refino temático) ou ITA PIBIC (se foco em bolsas → fronteira Concursos).

### Oportunidades / chamadas (1 fonte)

| # | Fonte | `source_id` sugerido | Motivo |
|---|--------|----------------------|--------|
| 1 | **MCTI — Fomento (Transformação Digital)** | `mcti_fomento_transformacao_digital` | Hub gov.br de programas; rota **Radar/Editais** com `review_for_edital` |

**Reserva:** CAPES notícias com filtro forte de “edital/chamada” (mais ruído que MCTI hub).

---

## Próximos passos (fora deste documento)

1. ~~DefesaNet em `config/news_research_sources.json`~~ — **feito** (`id=defesanet`).
2. ~~Dry-run DefesaNet~~ — **feito** (`python scripts/news_research/run_defesanet_dryrun.py`).
3. ~~Brisa News em config~~ — **feito** (`id=brisa_news`).
4. EB: registar em config e repetir dry-run.
5. Dry-run loader notícia/pesquisa (`scripts/dry_run_news_research_loader.py`); **não** apply.
6. Manter ITA/IME exclusivamente no pipeline `concursos/main_militar_aeroespacial_*.py`.

### Pilotos BR — artefatos

| Fonte | Dry-run |
|-------|---------|
| DefesaNet | `python scripts/news_research/run_defesanet_dryrun.py` |
| BRISA News | `python scripts/news_research/run_brisa_news_dryrun.py` |
| BRISA Artigos | `python scripts/news_research/run_brisa_artigos_dryrun.py` |
| Exército Brasileiro | `python scripts/news_research/run_exercito_brasileiro_dryrun.py` |
| SOFTEX Notícias | `python scripts/news_research/run_softex_noticias_dryrun.py` |
| CAPES Notícias | `python scripts/news_research/run_capes_noticias_dryrun.py` |
| DARPA estratégico | `python scripts/news_research/run_darpa_strategic_dryrun.py` |
| MCTI Notícias | `python scripts/news_research/run_mcti_noticias_dryrun.py` |
| War.gov / U.S. DoD News | `python scripts/news_research/run_war_gov_news_dryrun.py` |
| AFRL News + Mission Orgs | `python scripts/news_research/run_afrl_strategic_dryrun.py` |
| MCTI Fomento (diagnóstico) | `python scripts/news_research/run_mcti_fomento_diagnostic.py` |
| MCTI Fomento (Radar dry-run v3) | `python scripts/radar/run_mcti_fomento_dryrun_v3.py` |
| F-35 News & Features | `python scripts/news_research/run_f35_news_dryrun.py` |
| Lockheed Martin Newsroom | `python scripts/news_research/run_lockheed_martin_news_dryrun.py` |

### Piloto Lockheed Martin Newsroom — artefatos

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `lockheed_martin_news` |
| Crawler | `scripts/crawl_news_research_sources.py` (`lm_json_feed`) |
| Dry-run | `scripts/news_research/run_lockheed_martin_news_dryrun.py` |
| Relatórios | `audit_reports_news_research/lockheed_martin_news_dryrun/` |

### Piloto F-35 News — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `f35_news` |
| Crawler | `scripts/crawl_news_research_sources.py` (`method=json_feed`) |
| Dry-run | `scripts/news_research/run_f35_news_dryrun.py` |
| Relatórios | `audit_reports_news_research/f35_news_dryrun/summary.json` |

### Piloto DefesaNet — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `defesanet` |
| Crawler | `scripts/crawl_news_research_sources.py` (RSS) |
| Dry-run | `scripts/news_research/run_defesanet_dryrun.py` |
| Relatórios | `audit_reports_news_research/defesanet_dryrun/summary.json` |

### Piloto BRISA News — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `brisa_news` |
| Dry-run | `scripts/news_research/run_brisa_news_dryrun.py` |
| Relatórios | `audit_reports_news_research/brisa_news_dryrun/summary.json` |

**Última corrida:** 4 standardized, 4 `valido`, 0 erros; feed com volume limitado; maioria das datas fora da janela 12m (itens de 2024–2025) — ver `within_window_12m` no summary.

### Piloto BRISA Artigos — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `brisa_artigos` |
| Dry-run | `scripts/news_research/run_brisa_artigos_dryrun.py` |
| Relatórios | `audit_reports_news_research/brisa_artigos_dryrun/summary.json` |

**Última corrida:** 8 standardized, 7 `valido`, 1 `incompleto`; todos `tipo_conteudo=pesquisa`; `fonte=BRISA`; 0 na janela 24m (datas 2022–2024 vs corte rolling) — ver `within_window_24m` no summary.

### Piloto Exército Brasileiro — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `exercito_brasileiro` |
| Dry-run | `scripts/news_research/run_exercito_brasileiro_dryrun.py` |
| Relatórios | `audit_reports_news_research/exercito_brasileiro_dryrun/summary.json` |

**Última corrida:** 10 standardized, 6–10 `valido` (resumo curto em og:description reduz qualidade), **10 na janela 12m**, `tipo_conteudo=noticia`, `fonte=Exército Brasileiro`.

### Piloto SOFTEX Notícias — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `softex_noticias` |
| Dry-run | `scripts/news_research/run_softex_noticias_dryrun.py` |
| Relatórios | `audit_reports_news_research/softex_noticias_dryrun/summary.json` |

**Última corrida:** 10 standardized, 10 `valido`, **10 na janela 12m**; `fonte=SOFTEX`; RSS `https://softex.br/feed/`.

### Piloto CAPES Notícias — artefatos (detalhe)

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `capes_noticias` |
| Dry-run | `scripts/news_research/run_capes_noticias_dryrun.py` |
| Relatórios | `audit_reports_news_research/capes_noticias_dryrun/summary.json` |

**Última corrida:** 10 standardized, 10 `valido`, **7 na janela 12m** (3 mais antigas mantidas no standardized); `fonte=CAPES`; RSS `https://www.gov.br/capes/pt-br/assuntos/noticias/rss.xml`; categorias heurísticas (Formação, Ciência, Bolsas, Pós-graduação, Inovação).

### MCTI Fomento — Radar / Editais (artefatos)

| Item | Caminho |
|------|---------|
| Plano | [MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md](MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md) |
| Diagnóstico | `scripts/news_research/run_mcti_fomento_diagnostic.py` → `audit_reports_news_research/mcti_fomento_diagnostic/` |
| Dry-run v3 | `run_mcti_fomento_dryrun_v3.py` → `mcti_fomento_dryrun_v3/` |
| Níveis v3 | `standardized/` = pronto técnico; `review_candidates.json`; `institucional_latente.json`; `descartados_ruido.json` |
| Código | `mcti_fomento_lib.py` (`assign_nivel_v3`, `crawl_mcti_fomento_v3`) |
| **apply_status** | `não_recomendado` — motivo: prontos v3 são editais/chamamentos **históricos** (2020–2024), não oportunidades atuais |
| **próxima_ação** | Reexecutar periodicamente; usar apply apenas se aparecer chamada **ativa** |

**Conclusão:** rota **Radar / Editais**; crawler e curadoria v3 **mantidos** como infraestrutura; **sem apply** no estado atual do portal MCTI.

### 16. DARPA — Notícias / Programas / Opportunities (internacional)

**Status (2026-05-20):** três `source_id` + subset programas v2; dry-run unificado `darpa_strategic_dryrun/`; subset apply `darpa_programs_research_subset_valido_v2/`; **sem apply** automático nesta tarefa.

| Rota | source_id | Destino | Seed / método |
|------|-----------|---------|----------------|
| Notícias | `darpa_news` | **`public.noticia` apenas** (nunca `public.pesquisa`) | RSS `https://www.darpa.mil/rss/news.xml` |
| Programas | `darpa_programs_research` | **`public.pesquisa` apenas** (`programa_pesquisa`, `tipo_recurso=programa_estrategico`, `tipo_oportunidade=pesquisa_estrategica`) | `sitemap.xml` → `/research/programs/{slug}` |
| Opportunities | `darpa_opportunities_research` | **review_for_edital** / Radar | RSS `opportunities.xml` — **não** auto `public.edital` nem `public.pesquisa` |

| Campo | Valor |
|-------|--------|
| **CMS** | Drupal (darpa.mil) |
| **robots.txt** | HTTP 200; Allow padrão Drupal |
| **Último dry-run** | 10 notícias válidas; 25 programas válidos (40 std); 9 opportunities → review |
| **Subset programas (v2)** | `audit_reports_news_research/darpa_programs_research_subset_valido_v2/` — loader: 25/25 `tipo_pesquisa`+`tipo_recurso`, `errors_count=0` |
| **Comando dry-run estratégico** | `python scripts/news_research/run_darpa_strategic_dryrun.py` |
| **Comando subset v2** | `python scripts/news_research/build_darpa_programs_research_subset_valido_v2.py` |
| **SQL corretivo pós-apply antigo** | `docs/sql/FIX_DARPA_PROGRAMS_RESEARCH_TYPES.sql` (manual, staging) |

**Notas:** loader corrigido (`load_news_research_sources.py`) — `fonte=DARPA`, `fonte_recurso=darpa_programs_research`; tipos em colunas + `extras`. Registos com `fonte_recurso=DARPA News` em `public.pesquisa` foram roteamento incorreto; desativar via SQL se duplicados em `public.noticia`.

---

### 17. MCTI — Notícias (CT&I)

**Status piloto (2026-05-18):** `source_id=mcti_noticias` via listagem HTML gov.br/Plone (sem RSS — `rss.xml`/`atom.xml` retornam 404); dry-run em `audit_reports_news_research/mcti_noticias_dryrun/`; **sem apply**. **Separado** de MCTI Fomento (§15, Radar/Editais).

| Campo | Valor |
|-------|--------|
| **URL** | https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias |
| **Classificação** | **notícias** estratégicas CT&I |
| **CMS** | gov.br / Plone |
| **Listagem** | Hub + `/noticias/YYYY`; artigos em `/noticias/YYYY/MM/slug` |
| **Enrich** | `.documentPublished`, `#content-core`, `og:description`, `og:image` |
| **Filtro** | Curadoria forte: eixos ciência/tecnologia/inovação/IA/espaço/fomento/etc.; descarte de agenda/cerimônia/posse/nota oficial; **review** se admin + técnico ambíguo |
| **extras** | `relevancia_mcti`, `motivos_relevancia`, `motivos_descarte`, `possivel_edital` (não roteia para Radar) |
| **Rota do produto** | **Notícias** (`tipo_conteudo=noticia`, `fonte=MCTI`, `fonte_recurso=mcti_noticias`) |
| **Última corrida dry-run** | 30 raw → 22 standardized, 2 review, 6 descartados; 7 válidos, 15 incompletos (resumo curto em cards) |

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `mcti_noticias` |
| Crawler | `scripts/crawl_news_research_sources.py` (`govbr_plone_listing`) |
| Dry-run | `python scripts/news_research/run_mcti_noticias_dryrun.py` |
| Relatórios | `audit_reports_news_research/mcti_noticias_dryrun/` (`summary.json`, `review_candidates.json`, `descartados_ruido.json`) |

---

### 18. War.gov / U.S. DoD — Notícias (oficial governamental)

**Status piloto (2026-05-20):** `source_id=war_gov_news`; RSS ArticleCS ContentType=1 (News Stories); dry-run em `audit_reports_news_research/war_gov_news_dryrun/`; **sem apply**. Exibição neutra: **U.S. Department of Defense / War.gov** — não confundir com imprensa independente.

| Campo | Valor |
|-------|--------|
| **URL hub** | https://www.war.gov/news/ |
| **RSS** | `DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945` |
| **Classificação** | **notícias** estratégicas defesa/tecnologia (governo EUA) |
| **Filtro** | Positivos: defense/military tech, AI, cyber, space, drones, hypersonic, sensors, NATO/deterrence técnico; negativos: ceremony, speech, transcript, travels, media invitation; procurement → review |
| **extras** | `relevancia_war_gov`, `war_gov_section`, `motivos_relevancia`, `motivos_descarte`, `possivel_procurement` (não vira edital) |
| **Rota do produto** | **Notícias** (`tipo_conteudo=noticia`, `fonte_recurso=war_gov_news`) |
| **Última corrida dry-run** | 30 raw → 8 standardized (8 válidos), 22 descartados, 0 review |

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `war_gov_news` |
| Crawler | `scripts/crawl_news_research_sources.py` (`dod_articlecs_rss`) |
| Dry-run | `python scripts/news_research/run_war_gov_news_dryrun.py` |
| Relatórios | `audit_reports_news_research/war_gov_news_dryrun/` |

**Avaliação:** excelente para subset top 10–20 e apply controlado (alta taxa de ruído filtrado no feed bruto).

---

### 19. NATO — Notícias (oficial internacional)

**Status piloto (2026-05-20):** `source_id=nato_news`; hub AEM SPA + listagem via `sitemap.xml`; dry-run em `audit_reports_news_research/nato_news_dryrun/`; **sem apply**.

| Campo | Valor |
|-------|--------|
| **URL hub** | https://www.nato.int/en/news-and-events/articles/news |
| **URL legado** | https://www.nato.int/cps/en/natohq/news.htm (redireciona ao hub) |
| **Listagem** | `https://www.nato.int/sitemap.xml` → artigos `/en/news-and-events/articles/news/YYYY/MM/DD/slug` |
| **RSS** | Não disponível para bots (candidatos testados 404/timeout) |
| **Detalhe** | AEM `.model.json` (`title`, `description`) + `og:image`; sem corpo integral |
| **robots.txt** | HTTP 200; `Sitemap: https://www.nato.int/sitemap.xml`; `Disallow: */newsletter/*` |
| **Classificação** | **news** → `public.noticia`; speeches/statements → review/descarte; publications/reports → pesquisa futura; nato-stories fora do path `news/` |
| **Filtro** | Positivos: defense, deterrence, NATO, cyber, space, innovation, AI, drones, missile defense, EW, interoperability, industry, Ukraine (defesa/tecnologia); negativos: ceremony, speech, protocol visit, transcript, agenda, commemoration |
| **extras** | `relevancia_nato`, `nato_section`, `motivos_relevancia`, `motivos_descarte`, `listing_method=nato_sitemap_aem` |
| **Rota do produto** | **Notícias** (`tipo_conteudo=noticia`, `fonte=NATO`, `fonte_recurso=nato_news`) |
| **Última corrida dry-run** | 30 raw → 26 standardized (26 válidos), 4 review, 0 descartados pós-filtro |

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` → `nato_news` |
| Crawler | `scripts/crawl_news_research_sources.py` (`nato_sitemap` + enrich `.model.json`) |
| Dry-run | `python scripts/news_research/run_nato_news_dryrun.py` |
| Relatórios | `audit_reports_news_research/nato_news_dryrun/` |

**Avaliação:** excelente para subset top 10–20 e apply controlado (alta densidade de sinal técnico/estratégico na janela 12m).

---

### 20. AFRL — News + Diretorias RA/RJ/RR + Highlights (oficial EUA)

**Status piloto (2026-05-20):** `afrl_news`, diretorias `afrl_air_warfare_research` / `afrl_space_warfare_research` / `afrl_technology_transition`, `afrl_mission_highlights`; dry-run `afrl_strategic_dryrun/`; **sem apply**.

| Campo | Valor |
|-------|--------|
| **URL News** | https://www.afrl.af.mil/News/ |
| **Diretorias** | https://www.afrl.af.mil/RA/ (Air Warfare), https://www.afrl.af.mil/RJ/ (Space Warfare), https://www.afrl.af.mil/RR/ (Technology Transition) |
| **Highlights** | Secção *Directorate Highlights* — cards com link **Read More** → `/News/Article-Display/Article/{id}/slug` |
| **Listagem notícias** | HTML `article.article-listing-item` + paginação `?Page=N` |
| **RSS** | Sem feed AFRL útil (ArticleCS Site scan); listagem HTML |
| **Akamai** | Hub/diretorias **403** em datacenters; dry-run: Wayback (News) + `fixtures/news_research/afrl_{RA,RJ,RR}_directorate.html` |
| **Roteamento** | **news** (`afrl_news`, `afrl_mission_highlights` com data 12m) → `public.noticia`; **1 pesquisa/diretoria** com `extras.highlights` (todos os cards); highlight sem data → só em `extras.highlights`; SBIR/AFWERX/SpaceWERX → `review_for_edital` |
| **Última corrida dry-run** | News **12 válidos**; **3** registros institucionais (45+12+12 highlights em extras); **2** highlights → notícia (janela 24m no dry-run; config produção 12m); **1** review |

| `source_id` | Destino |
|-------------|---------|
| `afrl_news` | `public.noticia` |
| `afrl_air_warfare_research` | `public.pesquisa` (Air Warfare Directorate) |
| `afrl_space_warfare_research` | `public.pesquisa` (Space Warfare Directorate) |
| `afrl_technology_transition` | `public.pesquisa` (Technology Transition Office; `portal_estrategico`) |
| `afrl_mission_highlights` | `public.noticia` (highlights com data + filtro técnico) |

| Item | Caminho |
|------|---------|
| Config | `config/news_research_sources.json` |
| Crawler | `scripts/crawl_news_research_sources.py` |
| Fixtures | `fixtures/news_research/afrl_RA_directorate.html` (+ RJ, RR) |
| Dry-run | `python scripts/news_research/run_afrl_strategic_dryrun.py` |
| Relatórios | `audit_reports_news_research/afrl_strategic_dryrun/` |

**Avaliação:** **apply controlado** para `afrl_news`; diretorias **latente** (incompleto sem data — esperado); highlights como notícia dependem de recência (12m) e fetch live das páginas RA/RJ/RR.

---

### 21. Expansão militar/técnico-científica (AFMC, AFNWC, Space Force, ARL, AFRL tech areas)

**Status piloto (2026-05-20, prioridade probe):** oito `source_id` em `config/news_research_sources.json`; crawler `scripts/news_research/military_af_research.py`; dry-run `military_research_expansion_dryrun/`; **sem apply**.

**Ordem de prioridade (probe):** (1) `afrl_technology_areas` + `arl_news` + `arl_resources` — HTTP 200; (2) portais AFNWC Wayback; (3) notícias AFMC/AFNWC/Space Force — hubs `/News/` 403 live, **Wayback-first** + ArticleCS; RSS `Site=1` **não** usado.

| Campo | Valor |
|-------|--------|
| **Notícias (.af.mil / spaceforce)** | AFMC, AFNWC, Space Force — padrão DoD **Article-Display** + paginação `?Page=N`; hubs **403** (Akamai); listagem via **Wayback** (`DOD_AFMIL_WAYBACK_FALLBACK=1`) |
| **ARL News** | `arl.devcom.army.mil/media-center/` + `/news/` — **HTTP 200**; links `/news/{slug}/` (não ArticleCS) |
| **AFRL Technology Areas** | https://afresearchlab.com/technology/ — **HTTP 200**; ~15 áreas → `public.pesquisa` (`area_tecnologica`) |
| **AFNWC portais** | `/Innovation/`, `/Weapon-Systems/` → `public.pesquisa` (`portal_estrategico` / `sistema_estrategico`); Weapon-Systems hub instável (403) |
| **ARL Resources** | `/resources/`, BAA, CRAs — `public.pesquisa`; **BAA** → `review_candidates.json` (`destino_sugerido=Radar/Editais`) |
| **Oportunidades** | SBIR/BAA/solicitation **nunca** `public.edital` automático |

| `source_id` | Destino | Dry-run (2026-05-20) |
|-------------|---------|----------------------|
| `afrl_technology_areas` | `public.pesquisa` | **12 válidos** (live + enrich) → apply_controlado |
| `arl_news` | `public.noticia` | **12 válidos** (filtro pesquisa aplicada) → apply_controlado |
| `arl_resources` | `public.pesquisa` / review | **20 válidos**; **2** BAA → Radar |
| `space_force_news` | `public.noticia` | **18 válidos** (Wayback-first; 30 raw) → apply_controlado |
| `afnwc_innovation` | `public.pesquisa` | **4 válidos** (portal Wayback) |
| `afnwc_weapon_systems` | `public.pesquisa` | **1** hub (Weapon-Systems 403) → precisa_melhoria |
| `afmc_news` | `public.noticia` | **latente** — Wayback OK mas datas/enrich; filtro técnico AFMC |
| `afnwc_news` | `public.noticia` | **latente** — Wayback falhou no lote |

| Item | Caminho |
|------|---------|
| Módulo | `scripts/news_research/military_af_research.py` |
| Config | `config/news_research_sources.json` |
| Dry-run | `python scripts/news_research/run_military_research_expansion_dryrun.py` |
| Relatórios | `audit_reports_news_research/military_research_expansion_dryrun/` |
| Subsets staging (2026-05-20) | `python scripts/news_research/build_military_expansion_subsets_valido.py` — **sem apply** |

**Subsets apply staging (loader dry-run, sem apply):**

| Subset | Destino | Itens | `would_upsert` | `errors_count` | Pasta |
|--------|---------|------:|---------------:|---------------:|-------|
| `afrl_technology_areas_subset_valido` | `public.pesquisa` | 12 | pesquisa **12** | 0 | `audit_reports_news_research/afrl_technology_areas_subset_valido/` |
| `arl_news_subset_valido` | `public.noticia` | 12 | notícia **12** | 0 | `audit_reports_news_research/arl_news_subset_valido/` |
| `arl_resources_subset_valido` | `public.pesquisa` | 18 | pesquisa **18** | 0 | `audit_reports_news_research/arl_resources_subset_valido/` |
| `space_force_news_subset_valido` | `public.noticia` | 18 | notícia **18** | 0 | `audit_reports_news_research/space_force_news_subset_valido/` |

Filtros dos subsets: `validacao_status=valido`; notícias com **janela 12 meses**; `arl_resources` exclui **BAA** / `possivel_edital` / `review_for_edital` (2 itens); **sem** `review_candidates.json`; **sem** fontes latentes (`afmc_news`, `afnwc_news`, `afnwc_innovation`, `afnwc_weapon_systems`).

Loader por subset: `python scripts/load_news_research_sources.py --dry-run --source <source_id> --input-dir audit_reports_news_research/<subset_dir>/`

**Nota:** `afrl_news` (af.mil) permanece fonte separada já aplicada no banco; não duplicar com esta onda. `arl_news` é ARL (`arl.devcom.army.mil`), distinto de `afrl_news`.

---

### 22. Consolidado da frente militar/técnico-científica (aplicado em staging)

**Status (2026-05-20):** lote internacional defesa/aero/espaço **aplicado** em `public.noticia` e `public.pesquisa` (staging); consolidado único da frente.

| Métrica | Valor |
|---------|------:|
| Fontes aplicadas | **11** |
| Registros totais | **187** (132 notícias + 55 pesquisas) |
| Review/latente | DARPA opportunities, BAA ARL, AFMC/AFNWC news, diretorias AFRL |

| `public.noticia` | Registros |
|------------------|----------:|
| f35_news, lockheed_martin_news, darpa_news, war_gov_news, nato_news, afrl_news, arl_news, space_force_news | **132** |

| `public.pesquisa` | Registros |
|-------------------|----------:|
| darpa_programs_research, afrl_technology_areas, arl_resources | **55** |

| Item | Caminho |
|------|---------|
| Consolidado | `audit_reports_news_research/military_strategic_consolidado/consolidado_militar.json` |
| Relatório | `audit_reports_news_research/military_strategic_consolidado/consolidado_militar.md` |

**Produto:** fontes **oficiais/corporativas** — não jornalismo independente; roteamento notícia/pesquisa/review documentado no consolidado. SQL de validação na §11 do `.md`.

---

## Referências

| Documento | Conteúdo |
|-----------|----------|
| [CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md) | IME/ITA concursos |
| [audit_reports_news_research/expansion_plan.md](../audit_reports_news_research/expansion_plan.md) | Ondas NASA/DARPA/IAEA/EurekAlert |
| [military_strategic_consolidado/consolidado_militar.md](../audit_reports_news_research/military_strategic_consolidado/consolidado_militar.md) | Consolidado frente militar aplicada (187 reg.) |
| `config/news_research_sources.json` | Config técnica atual do módulo |
| `scripts/crawl_news_research_sources.py` | Crawler genérico (quando implementar BR) |

*Documento criado em 2026-05-17. Sem crawlers, sem alteração de schema/frontend/Supabase.*
