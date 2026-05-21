# Wave 2 — Fontes priorizadas (Concursos & Seleções)

Catálogo de URLs confirmadas manualmente para **vestibulares**, **bancas latentes** e **melhorias Wave 1**. Não altera schema, `public.edital` nem Radar.

**Princípios:** respeitar `robots.txt`, intervalo entre pedidos, não inventar campos, **apply não executado** até validação em staging.

---

## Prioridade alta

| Fonte | URL | Tipo | Crawler / notas |
|-------|-----|------|-----------------|
| **Comvest — Vestibular 2027** | https://www.comvest.unicamp.br/ingresso-2027/vestibular-2027/ | `vestibular` | `main_vestibulares_comvest.py` — seed fixo |
| **Comvest — Vagas Olímpicas 2027** | https://www.comvest.unicamp.br/ingresso-2027/vagas-olimpicas-2027/ | `programa_ingresso` | idem |
| **Fuvest — Vestibular USP** | https://www.fuvest.br/vestibular-da-usp | `vestibular` | `main_fuvest_concursos.py` |
| **Fuvest — Concursos** | https://www.fuvest.br/concursos/ | misto | idem |
| **AOCP — Inscrições abertas** | https://www.institutoaocp.org.br/concursos/status/inscricoes-abertas | concurso | `main_aocp_concursos.py` — API `link.institutoaocp.org.br` |
| **Quadrix — Abertos** | https://concursos.quadrix.org.br/index/abertos/ | concurso | `main_quadrix_concursos.py` |
| **Quadrix — Paginação** | https://concursos.quadrix.org.br/index/1/?ord=&dir=&pg=2&q=&pp=10 | concurso | pg=2, pg=3 (limite conservador) |

---

## Prioridade média

| Fonte | URL | Tipo | Notas |
|-------|-----|------|--------|
| **UFRGS — Site** | https://www.ufrgs.br/site/ | hub | Contexto institucional |
| **UFRGS — COPERSE sobre** | https://www.ufrgs.br/coperse/sobre-o-vestibular-2/ | vestibular | `main_vestibulares_ufrgs.py` |
| **UFRGS — Concurso vestibular** | https://www.ufrgs.br/coperse/concurso-vestibular/ | vestibular | idem |
| **Cebraspe — Portal** | https://www.cebraspe.org.br/ | banca | Latente wave1 |
| **Cebraspe — Concursos** | https://www.cebraspe.org.br/concursos/ | banca | `main_cebraspe_concursos.py` (PAS API) |
| **Fuvest — Residência** | https://www.fuvest.br/residencia/ | `residencia` | Wave 2 residências / vestibulares |
| **Fuvest — Pós-graduação** | https://www.fuvest.br/pos-graduacao/ | `programa_ingresso` / pós | Wave 2 |

---

## Notícias / oportunidades (sem crawler de seleção direto)

| Fonte | URL | Uso |
|-------|-----|-----|
| Cebraspe notícias | (portal Cebraspe — secção notícias) | Radar futuro / curadoria |
| UFRGS notícias | via `www.ufrgs.br` | idem |
| **AOCP notícias** | https://noticias.institutoaocp.org.br/ | Oportunidades / contexto |
| **AOCP social** | https://social.institutoaocp.org.br/ | Comunicação |
| **AOCP — Novos** | https://www.institutoaocp.org.br/concursos/status/novos | Pré-inscrição (`NEW` na API) |

---

## AOCP — URLs complementares

| URL | Mapeamento API sugerido |
|-----|-------------------------|
| `/concursos/status/inscricoes-abertas` | `IN_PROGRESS` |
| `/concursos/status/novos` | `NEW` |
| `/concursos/status/em-andamento` | `IN_PROGRESS` + `SUBSCRIBE` |
| API primária | `https://link.institutoaocp.org.br/api/concursos` |
| API fallback | `https://link.aocp.com.br/api/concursos` |

---

## Comvest — mapeamento de campos (piloto)

| Campo | Valor |
|--------|--------|
| `fonte` | `comvest` |
| `fonte_tipo` | `universidade` |
| `orgao` | `Unicamp / Comvest` |
| `instituicao` | `Universidade Estadual de Campinas` |
| `banca` | `Comvest` |
| `estado` / `municipio` | `SP` / `Campinas` |
| `nivel_escolaridade` | `ensino_medio` |
| `validacao_status` | `valido` se `data_fim_inscricao` presente |

---

## Estado dos crawlers (2026-05-16)

| Fonte | Standardized | Válidos | Loader dry-run | Apply |
|-------|-------------:|--------:|----------------|-------|
| Coperve | latente | 0 | — | não |
| UFRGS/COPERSE | latente | 0 | — | não |
| **Comvest** | **2** | **0** (`incompleto`; sem `data_fim_inscricao` no site) | 2, `errors_count=0` | não |
| **AOCP** | **2** (NEW) | **1** | 2, `errors_count=0` | não |
| **Quadrix** | **11** | **11** | 11, `errors_count=0` | não |
| **Fuvest** | **2** | **0** | 2, `errors_count=0` | não |

**AOCP:** API primária `link.institutoaocp.org.br` (383 itens); `IN_PROGRESS` na lista muitas vezes com inscrição já encerrada — crawler prioriza `NEW` e não descarta `NEW`/`SUBSCRIBE` por recência.

Ver também: [CONCURSOS_FONTES_WAVE1.md](./CONCURSOS_FONTES_WAVE1.md), [CONCURSOS_FILTROS_EXPANSAO.md](./CONCURSOS_FILTROS_EXPANSAO.md).
