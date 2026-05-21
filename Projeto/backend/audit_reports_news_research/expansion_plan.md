# Plano de expansão — módulo news/research (EditalFinder)

**Inventário backend (todas as frentes):** [docs/BACKEND_SOURCES_INVENTORY.md](../docs/BACKEND_SOURCES_INVENTORY.md) · [BACKEND_SOURCES_INVENTORY.json](../docs/BACKEND_SOURCES_INVENTORY.json)

## Objetivo

Aumentar a cobertura de notícias e conteúdos de pesquisa **por ondas**, com **qualidade** e **fronteiras claras** em relação ao pipeline de editais.

**Mapeamento BR defesa/aero/estratégico:** [docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md](../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md) — pilotos **DefesaNet** (`defesanet_dryrun/`), **BRISA News** (`brisa_news_dryrun/`, latente por recência), **BRISA Artigos** (`brisa_artigos_dryrun/`, latente por recência), **Exército Brasileiro** (`exercito_brasileiro_dryrun/`, Liferay 12m), **SOFTEX Notícias** (`softex_noticias_dryrun/`, WordPress RSS 12m), **CAPES Notícias** (`capes_noticias_dryrun/`, gov.br/Plone RSS 12m), **ITA Projetos** / **LAB-GE** (`ita_*_dryrun/`, pesquisa institucional, sem apply por falta de data). **MCTI Fomento** — dry-run Radar v3 `mcti_fomento_dryrun_v3/` (5 prontos técnicos, 35 review); **`apply_status`: `não_recomendado`** (itens históricos/encerrados; apply não executado). Crawler + curadoria v3 mantidos; **próxima ação:** reexecutar `run_mcti_fomento_dryrun_v3.py` periodicamente e aplicar só se houver chamada ativa. [MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md](../docs/MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md).

**MCTI Notícias** — `mcti_noticias`; listagem HTML gov.br/Plone (RSS 404); filtro forte CT&I (descarte admin, review ambíguo); dry-run `mcti_noticias_dryrun/` (**30 raw → 22 standardized, 2 review, 6 descartados**, sem apply). Comando: `python scripts/news_research/run_mcti_noticias_dryrun.py`. **Não confundir** com MCTI Fomento (Radar).

**War.gov / U.S. DoD News** — `war_gov_news`; fonte **oficial governamental** EUA (`fonte` = U.S. Department of Defense / War.gov; não jornalismo independente); RSS ArticleCS ContentType=1 (News Stories); hub `war.gov/news` pode 403 — listagem via RSS; filtro forte defesa/tecnologia (22 descartados institucionais no piloto); dry-run `war_gov_news_dryrun/` (**30 raw → 8 standardized, 8 válidos, 0 review**, sem apply). Comando: `python scripts/news_research/run_war_gov_news_dryrun.py`. **Próximo:** subset top 10–20 + apply controlado.

**NATO News** — `nato_news`; fonte **oficial internacional** OTAN (`fonte` = NATO; `fonte_recurso=nato_news`); hub AEM SPA; listagem `sitemap.xml`; dry-run piloto `nato_news_dryrun/` (**30→26 std, 26 válidos, 4 review**); dry-run ampliado `nato_news_dryrun_100/` (**99 raw → 93 std, 26 válidos, 6 review** — enrich limitado a `page_enrich_max=30`); subset staging `nato_news_subset_top20/` (**20 would_upsert**, loader dry-run OK, **sem apply**). Comandos: `run_nato_news_dryrun.py`, `build_nato_news_subset_top20.py`.

**AFRL (Air Force Research Laboratory)** — `afrl_news` + diretorias **RA/RJ/RR** (`afrl_air_warfare_research`, `afrl_space_warfare_research`, `afrl_technology_transition`) + `afrl_mission_highlights`; highlights com **Read More** nas páginas de diretoria; **1 registro pesquisa/diretoria** com `extras.highlights`; highlights com data → `afrl_mission_highlights` → `public.noticia`; Akamai 403 → Wayback (News) + fixtures `fixtures/news_research/`; dry-run `afrl_strategic_dryrun/` (**12 news válidas**, **3 pesquisa institucional**, **2 highlights→notícia** com janela 24m no dry-run, **1 review**, sem apply). Comando: `python scripts/news_research/run_afrl_strategic_dryrun.py`.

**Expansão militar/técnico-científica (2026-05-20, rodada priorizada)** — fontes estáveis primeiro: `afrl_technology_areas` (live + enrich área), `arl_news` (filtro pesquisa aplicada), `arl_resources` (classificação BAA→review / PDF→documento / estático→`institucional_latente`); depois Wayback-first para `space_force_news`, `afnwc_news`, `afmc_news` e portais AFNWC. Módulo `military_af_research.py`; dry-run `military_research_expansion_dryrun/`. Comando: `python scripts/news_research/run_military_research_expansion_dryrun.py` (`DOD_AFMIL_WAYBACK_FALLBACK=1`).

**Subsets staging (2026-05-20, sem apply):** `python scripts/news_research/build_military_expansion_subsets_valido.py` → quatro pastas com `consolidado_subset.json` + loader dry-run:

| Subset | Loader `--source` | would_upsert | errors |
|--------|-------------------|-------------:|-------:|
| `afrl_technology_areas_subset_valido/` | `afrl_technology_areas` | pesquisa 12 | 0 |
| `arl_news_subset_valido/` | `arl_news` | notícia 12 | 0 |
| `arl_resources_subset_valido/` | `arl_resources` | pesquisa 18 (excl. 2 BAA) | 0 |
| `space_force_news_subset_valido/` | `space_force_news` | notícia 18 (12m) | 0 |

Fora deste lote: `afnwc_innovation` (revisar), `afnwc_weapon_systems` (precisa_melhoria), `afmc_news` / `afnwc_news` (latentes). **Apply (quando autorizado):** apenas os quatro subsets acima; BAA permanecem fora de `public.pesquisa` automático.

**Consolidado frente militar (2026-05-20, staging aplicado):** `audit_reports_news_research/military_strategic_consolidado/consolidado_militar.json` · [consolidado_militar.md](military_strategic_consolidado/consolidado_militar.md)

| Tabela | Fontes aplicadas | Registros |
|--------|------------------|----------:|
| `public.noticia` | f35_news, lockheed_martin_news, darpa_news, war_gov_news, nato_news, afrl_news, arl_news, space_force_news | **132** |
| `public.pesquisa` | darpa_programs_research, afrl_technology_areas, arl_resources | **55** |
| **Total** | 11 fontes | **187** |

Latente/review: `darpa_opportunities_research`, diretorias AFRL, `afnwc_*`, `afmc_news`, BAA ARL — ver consolidado §6–7.

**Wave internacional defesa/aero (piloto 1):** **F-35 News & Features** — `f35_news`; feed `f35feed.json`; dry-run `f35_news_dryrun/` (**10/10 válidos**); subset top 20 em `f35_news_subset_top20/` (would_upsert=20, sem apply). **Lockheed Martin Newsroom** — `lockheed_martin_news`; feed `newsfeed.json` (~2756 itens; ~162 elegíveis técnicos/12m); filtros `require_any`/`exclude` + routing capabilities→rejeição; dry-run `lockheed_martin_news_dryrun/` (**10/10 válidos**, sem apply). Comandos: `run_f35_news_dryrun.py`, `run_lockheed_martin_news_dryrun.py`. **Lote controlado** obrigatório (fontes corporativas).

**Retenção / listagem pública:** [docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md](../docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md) — notícias 12m, pesquisas 24m no feed; crawl pode usar a mesma janela em `time_window_months` sem apagar linhas antigas na BD.

## O que não fazer (governança)

- Não enviar itens deste módulo para **`public.edital`**.
- Não promover **`review_for_edital`** automaticamente para edital.
- Não fazer **apply** sem **dry-run** e validação explícita.
- Não contornar **bloqueios** (robots, Cloudflare, políticas de fonte).
- Não fazer **scraping agressivo** nem varrer site inteiro: apenas `seed_urls` declarados e, no código atual, descoberta **limitada** de feeds RSS a partir de páginas hub.
- Não relaxar filtros de **data** e **resumo** (enriquecimento só a partir de HTML/RSS real).

## Onda 2 — NASA ampliada

- **Feeds oficiais** adicionais (verificados HTTP 200): notícias gerais, educação, aeronáutica, image of the day, *Technology*, *Earth*, *Missions*, *News releases*, *NASA Science* (`science.nasa.gov/feed/`).
- **Janela:** últimos **12 meses** (`time_window_months`).
- **Volume:** `max_items` com teto seguro (**95**) agregando todos os seeds; **dedupe por link** no crawl.
- **Qualidade:** manter parsing de data do RSS; `page_enrich_max` maior **só** na NASA para preencher resumo/data quando o feed vier pobre.

## Onda 3 — DARPA

- **`darpa_news`:** apenas `https://www.darpa.mil/rss/news.xml` (hub HTML removido).
- **`darpa_programs_research`:** catálogo via `sitemap.xml` → `/research/programs/{slug}` (hub SPA); `tipo_pesquisa=programa_pesquisa`; janela **24m** por `lastmod`.
- **`darpa_opportunities_research`:** `opportunities.xml`; links canônicos por âncora (RSS repete URL do hub); **sempre** `review_for_edital` — **não** `public.edital` automático.
- **Dry-run unificado:** `python scripts/news_research/run_darpa_strategic_dryrun.py` → `darpa_strategic_dryrun/` (2026-05-19: 10 notícias válidas, 25 programas válidos, 9 opportunities em review; **sem apply**).
- **Roteamento:** BAA/RFI/RFP → review/Radar; notícias técnicas → `public.noticia`; programas → `public.pesquisa`.

## Onda 4 — IAEA

- **Seeds corrigidos** para RSS estáveis: `https://www.iaea.org/feeds/topnews`, `/feeds/news`, `/feeds/publications` (evitar homepage sujeita a 403 Cloudflare em ambientes automatizados).
- **Temas:** nuclear, energia, segurança nuclear, aplicações nucleares.
- **Janelas:** 12 meses na config atual; **até 24 meses** para publicações técnicas pode ser uma **fase seguinte** (fonte duplicada filtrada ou parâmetro futuro no crawl).

## Onda 5 — EurekAlert filtrado

- **Volume baixo:** `max_items` **12** por execução.
- **Filtros no crawl:** `require_any_keyword` (aerospace, nuclear, quantum, …) e `exclude_keywords` para reduzir medicina genérica.
- **Status:** `noisy` até a taxa de ruído estabilizar; ajustar listas com base em `audit_summary.json`.

## Configuração

- Ficheiro: `config/news_research_sources.json`
- Campo **`status`** por fonte: `ready_for_wave` | `active_candidate` | `needs_cleanup` | `blocked_access` | `noisy`
- Bloco opcional **`governance`** documenta regras (não é consumido pelo loader legado).

## Pipeline (sem apply)

```text
python scripts/crawl_news_research_sources.py
python scripts/audit_news_research_pipeline.py
python scripts/dry_run_news_research_loader.py
```

Resultados agregados: `expansion_results.md` / `expansion_results.json` (gerados após esta configuração).
