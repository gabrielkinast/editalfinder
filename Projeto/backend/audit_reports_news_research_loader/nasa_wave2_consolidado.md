# NASA Wave 2 — consolidação (primeira carga validada notícia/pesquisa)

**Ambiente:** staging  
**Fonte lógica:** `nasa_news`  
**Onda:** `nasa_wave2`  
**Estado:** carga **validada** (notícia + pesquisa), **sem** encaminhamento para `public.edital`.

---

## Resumo numérico

| Métrica | Valor |
|--------|------:|
| Notícias (payload / alvo) | **78** |
| Pesquisas (payload / alvo) | **17** |
| `review_for_edital` (candidatos carregáveis) | **0** |
| Itens da Wave 2 em `public.edital` | **0** |

### Apply staging (registado em `load_news_research_summary.json`)

- **Data:** `2026-05-05T00:52:04Z`  
- **Modo:** `apply` — `apply_executado`: **true**, `apply_status`: **applied**  
- **Erros:** `errors_count` **0**, `skipped` **0**  
- **Review ignorado pelo loader:** `review_candidates_ignored` **0** (payload de review vazio)  
- **Notícia:** `inserted_noticia` **69**, `updated_noticia` **9** (total **78** alinhado a `would_upsert_noticia`)  
- **Pesquisa:** `inserted_pesquisa` **13**, `updated_pesquisa` **4** (total **17** alinhado a `would_upsert_pesquisa`)

---

## Fluxo executado

1. **Crawl / standardized** — expansão `nasa_news` → `audit_reports_news_research/standardized/nasa_news_standardized.json`.
2. **Build payloads Wave 2** — dedupe, roteamento, validação de contrato do loader:
   - `python scripts/build_nasa_wave2_payloads.py`
3. **Dry-run do loader** — sem escrita no Supabase, **0** erros de validação:
   - `python scripts/load_news_research_sources.py --dry-run --staging --wave nasa_wave2`
4. **Apply staging** — com guardas (`EDITALFINDER_ENV`, `EDITALFINDER_ALLOW_STAGING_APPLY`, `--test-db-before-apply`):
   - `python scripts/load_news_research_sources.py --apply --staging --test-db-before-apply --wave nasa_wave2`
5. **Validação pós-carga** — contagens por links do payload, campos, arrays, `extras`, **0** hits em `public.edital`, views com dados:
   - `python scripts/validate_news_research_after_load.py --staging --source nasa_news --wave nasa_wave2`

*(Nenhum novo apply foi executado na elaboração deste documento.)*

---

## Dry-run “limpo”

- Build Wave 2: **0** `review_candidates`, **0** `rejected_noise` no roteamento, **0** exclusões por validação (`nasa_wave2_dry_run.json`).  
- Loader em dry-run: **78** / **17** preparados para upsert, **0** erros (`load_news_research_summary.json` em modo dry-run anterior ao apply, ou equivalente documentado no fluxo).

---

## Validação pós-carga

Ficheiro: `nasa_wave2_post_load_validation.json` (gerado `2026-05-05T00:58:43Z`).

- **`ok`:** true  
- **78** notícias e **17** pesquisas encontradas em `public.noticia` / `public.pesquisa` pelos **links** dos payloads.  
- **Links únicos** e **sem overlap** entre notícia e pesquisa.  
- **`data_publicacao`**, **`resumo`** (notícia), **`descricao`** (pesquisa), **`extras`** como objeto, **arrays** não em formato string.  
- **`public.edital`:** **0** linhas com links da Wave 2.  
- **Views:** `vw_noticias_front` e `vw_pesquisas_front` devolveram dados na amostra.

---

## Artefactos principais

- `nasa_wave2_payload_noticia.json` / `nasa_wave2_payload_pesquisa.json`  
- `load_news_research_summary.json` (último apply documentado)  
- `nasa_wave2_post_load_validation.json` / `.md`  
- `nasa_wave2_dry_run.json` (build de payloads)  
- **`nasa_wave2_consolidado.json`** (máquina-legível, mesmo conteúdo estruturado)

---

## Próximos passos — Onda 3 (DARPA News)

- Fonte: **`darpa_news`** (RSS-only, plano em `expansion_plan.md`).  
- Repetir o padrão: **crawl** → **payloads** (ou script dedicado) → **dry-run loader** → **validação pós-carga** → **apply** só após aprovação explícita.  
- Manter **isolamento** do módulo: nada disto deve ir para `public.edital` automaticamente; `review_for_edital` continua fora do loader de notícia/pesquisa.

---

## Governança (reafirmação)

- Nenhum item desta onda foi para **`public.edital`**.  
- **`review_for_edital`** não é carregado por `load_news_research_sources.py` (apenas contabilizado / ignorado).  
- O módulo notícia/pesquisa permanece **separado** do pipeline de editais.
