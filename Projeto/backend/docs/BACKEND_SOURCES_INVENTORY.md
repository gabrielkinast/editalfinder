# Inventário de fontes do backend — EditalFinder

Documento central de referência para **quais fontes existem**, **qual pipeline as alimenta**, **status operacional** e **onde ficam os artefatos**. Gerado por leitura de código, configs e relatórios de auditoria — **sem** execução de crawlers ou apply.

**Versão estruturada (máquina):** [`BACKEND_SOURCES_INVENTORY.json`](./BACKEND_SOURCES_INVENTORY.json) (`generated_at` no JSON).

**Visibilidade aba Editais (ruído global):** auditoria `scripts/audit_editais_visibility_noise.py` — política [`EDITAIS_VISIBILITY_AND_NOISE_POLICY.md`](./EDITAIS_VISIBILITY_AND_NOISE_POLICY.md). Não confundir com status `ready` do loader: uma fonte pode estar “aplicada” e ainda gerar ruído na view até curadoria/SQL da view.

---

## Resumo executivo

| Métrica | Valor (inventário atual) |
|---------|--------------------------|
| **Fontes mapeadas** | **157** |
| **aplicada** | 60 (majoritariamente editais `ready` + concursos wave1/wave2 com staging) |
| **pronta_para_apply** | 43 (editais `ready_with_notes` + pilotos notícias BR/internacional com dry-run limpo) |
| **implementada_latente** | 8 |
| **precisa_melhoria** | 17 |
| **nao_recomendado** | 12 |
| **descoberta** | 1 (`pci_concursos`) |

**Por módulo (contagem aproximada):**

| Módulo | Fontes no inventário | Destaque |
|--------|---------------------:|----------|
| Editais / Radar (legado) | ~102 (`config/source_readiness.json`) | 54 `ready` + 36 `ready_with_notes` + 8 review + 10 blocked |
| Concursos & Seleções | 19 | 33 upserts wave1 staging + Avança SP wave2; várias latentes |
| Notícias / Pesquisas | 24 (`config/news_research_sources.json`) | BR pilotos + DARPA + NATO + War.gov + AFRL + expansão militar (AFMC/AFNWC/Space Force/ARL/tech areas); ondas NASA/IAEA/EurekAlert |
| Radar dedicado (MCTI) | 1 | **`apply_status`: não_recomendado** (lote histórico) |

**Melhores fontes operacionais hoje**

- **Concursos:** Quadrix, Legalle, Objetiva, Fundatec (subset), Avança SP (wave2 apply).
- **Notícias:** DefesaNet, SOFTEX, CAPES, Exército Brasileiro, MCTI Notícias (dry-run com curadoria CT&I; apply pendente de decisão de produto).
- **Editais (legado):** dezenas em `ready` (finep, fapesp, grants_gov, …) — ver JSON; apply via `load_ready_sources.py` quando staging autorizado.
- **Radar MCTI:** infraestrutura v3 pronta; **não aplicar** lote atual.

---

## 1. Visão geral

O backend separa **tipos de oportunidade** em módulos com tabelas e loaders distintos:

| Módulo produto | Tabela base | View front típica | Loader / crawl |
|----------------|-------------|-------------------|----------------|
| Editais / Radar fomento | `public.edital` | `vw_editais_front` | `<fonte>/main_*.py` → `retransform` → `load_ready_sources.py` |
| Notícias | `public.noticia` | `vw_noticias_front` | `crawl_news_research_sources.py` → `load_news_research_sources.py` |
| Pesquisas | `public.pesquisa` | `vw_pesquisas_front` | idem |
| Concursos & Seleções | `public.concurso_selecao` | `vw_concursos_front` | `concursos/main_*` → `load_concursos_selecao.py` |
| Portais estratégicos | `public.portal_estrategico` | (fornecedores/investimentos) | `load_portais_estrategicos.py` |
| MCTI Fomento (radar dedicado) | *(futuro `public.edital`)* | — | `scripts/radar/run_mcti_fomento_dryrun_v3.py` |

**Não misturar:** notícias/pesquisas **não** entram em `public.edital` sem `review_for_edital` explícito ([`expansion_plan.md`](../audit_reports_news_research/expansion_plan.md)).

---

## 2. Convenções de `source_id`

- **Concursos:** `fonte` no standardized = slug (`quadrix`, `comvest`, `ita_vestibular`, …).
- **News/research:** `id` em `config/news_research_sources.json` (`defesanet`, `nasa_news`, …); no banco costuma ser `fonte_recurso`.
- **Editais legado:** diretório na raiz do repo = `source_id` (`finep`, `fapesp`, `grants_gov`, …).
- **MCTI radar:** `mcti_fomento_transformacao_digital` (separado do `mcti` genérico em `source_readiness`).

---

## 3. Tabelas de destino

| Destino | Conteúdo | Retenção pública (views) |
|---------|----------|---------------------------|
| `public.edital` | Editais, chamadas, crédito, fomento tradicional | Sai da view após `prazo_envio` / fim inscrição; **linha permanece** |
| `public.noticia` | Notícias científicas / institucionais | **12 meses** em `vw_noticias_front` |
| `public.pesquisa` | Pesquisas, relatórios, projetos catalogados | **24 meses** em `vw_pesquisas_front` |
| `public.concurso_selecao` | Concursos, vestibulares, residências | View por datas inscrição/prova; **sem delete** por vencimento |
| `public.portal_estrategico` | Fornecedores, investimentos, hubs | Política própria do módulo |

Política completa: [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md).

---

## 4. Pipelines existentes

```text
EDITAIS (legado)
  <fonte>/main_<fonte>.py  →  <fonte>/outputs/*_editais.json
  scripts/retransform_all.py  →  audit_reports_retransform/standardized/
  scripts/load_ready_sources.py  →  public.edital (+ roteamento excepcional noticia/pesquisa)

NOTÍCIAS / PESQUISAS
  scripts/crawl_news_research_sources.py  →  audit_reports_news_research/
  scripts/build_*_payloads.py (ondas)  →  audit_reports_news_research_loader/
  scripts/load_news_research_sources.py  →  public.noticia | public.pesquisa

CONCURSOS
  concursos/main_<fonte>_concursos.py  →  audit_reports_main_pipeline/concursos_wave*/
  scripts/load_concursos_selecao.py  →  public.concurso_selecao

RADAR MCTI (dedicado)
  scripts/radar/run_mcti_fomento_dryrun_v3.py  →  audit_reports_radar/mcti_fomento_dryrun_v3/

ORQUESTRAÇÃO
  main.py  (daily, apply-edital, apply-news, status, list-readiness)
```

Configs chave: `config/source_readiness.json`, `config/news_research_sources.json`, `config/pipeline_sources.json`.

---

## 5. Fontes por módulo

### A) Concursos & Seleções

| source_id | Nome | Tipo | Pipeline | Artefatos | Destino | Status | Último resultado conhecido |
|-----------|------|------|----------|-----------|---------|--------|---------------------------|
| pci_concursos | PCI Concursos | agregador | `concursos/main_pci_concursos.py` | `concursos_wave1_pci` | `public.concurso_selecao` | **descoberta** | 12 std, 0 válidos, **12 apply** staging |
| quadrix | Quadrix | banca | `main_quadrix_concursos.py` | `concursos_wave1_quadrix` | idem | **aplicada** | 10 std, 10 válidos, 10 apply |
| legalle | Legalle | banca | `main_legalle_concursos.py` | `concursos_wave1_legalle` | idem | **aplicada** | 5/5 apply |
| objetiva | Objetiva | banca | `main_objetiva_concursos.py` | `concursos_wave1_objetiva` | idem | **aplicada** | 3/3 apply |
| fundatec | Fundatec | banca | `main_fundatec_concursos.py` | `concursos_wave1_fundatec` | idem | **aplicada** | 7 std, **2 válidos apply** (subset) |
| ibfc | IBFC | banca | `main_ibfc_concursos.py` | `concursos_wave1_ibfc` | idem | **aplicada** | 1 válido apply |
| avancasp | Avança SP | banca | `main_avancasp_concursos.py` | `concursos_wave2_avancasp` | idem | **aplicada** | 5/5 válidos, **5 apply** wave2 |
| fgv | FGV | banca | `main_fgv_concursos.py` | `concursos_wave1_fgv` | idem | **implementada_latente** | 3 std, 1 válido, sem apply |
| cebraspe | Cebraspe | banca | `main_cebraspe_concursos.py` | `concursos_wave1_cebraspe` | idem | **implementada_latente** | 0 std ativo (PAS encerrado) |
| aocp | AOCP | banca | `main_aocp_concursos.py` | `concursos_wave2_aocp` | idem | **implementada_latente** | 2 std, 1 válido |
| fcc | FCC | banca | `main_fcc_concursos.py` | `concursos_wave2_fcc` | idem | **nao_recomendado** | robots; 2/4 válidos |
| consulplan | Consulplan | banca | `main_consulplan_concursos.py` | `concursos_wave2_consulplan` | idem | **precisa_melhoria** | 0/10 válidos |
| fuvest | Fuvest | universidade | `main_fuvest_concursos.py` | `concursos_wave2_fuvest` | idem | **precisa_melhoria** | 0/2 válidos |
| comvest | Comvest | universidade | `main_vestibulares_comvest.py` | `concursos_wave2_comvest` | idem | **precisa_melhoria** | sem `data_fim_inscricao` |
| coperve | Coperve | universidade | `main_vestibulares_coperve.py` | `concursos_wave2_coperve` | idem | **implementada_latente** | 9 std, 0 válidos |
| ufrgs_cv | UFRGS/COPERSE | universidade | `main_vestibulares_ufrgs.py` | `concursos_wave2_ufrgs_cv` | idem | **implementada_latente** | 7 std, 0 válidos |
| ita_vestibular | ITA Vestibular | universidade | `main_militar_aeroespacial_ita.py` | `concursos_wave2_militar_aeroespacial_ita` | idem | **precisa_melhoria** | PDF escaneado |
| ime | IME | instituição militar | `main_militar_aeroespacial_ime.py` | `concursos_wave2_militar_aeroespacial_ime` | idem | **precisa_melhoria** | 5 std, datas PDF |
| embarcatech | EmbarcaTech | residência | `main_residencias_embarcatech.py` | `concursos_wave2_residencias_embarcatech` | idem | **precisa_melhoria** | 2 std, erros fetch |

Consolidado wave1: [`concursos_wave1_consolidado.json`](../audit_reports_main_pipeline/concursos_wave1_consolidado.json). Catálogo: [`CONCURSOS_FONTES_WAVE1.md`](./CONCURSOS_FONTES_WAVE1.md), [`CONCURSOS_WAVE2_FONTES_PRIORIZADAS.md`](./CONCURSOS_WAVE2_FONTES_PRIORIZADAS.md).

### B) Notícias / Pesquisas

| source_id | Módulo | Tipo | Pipeline | Artefatos dry-run | Destino | Status | Válidos (dry-run) |
|-----------|--------|------|----------|-------------------|---------|--------|-------------------|
| defesanet | notícia | instituição | `crawl_news_research` + `run_defesanet_dryrun` | `defesanet_dryrun/` | `public.noticia` | **pronta_para_apply** | 10 |
| softex_noticias | notícia | instituição | idem | `softex_noticias_dryrun/` | idem | **pronta_para_apply** | 10 (10 em 12m) |
| capes_noticias | notícia | governo | idem | `capes_noticias_dryrun/` | idem | **pronta_para_apply** | 10 (7 em 12m) |
| exercito_brasileiro | notícia | governo | idem | `exercito_brasileiro_dryrun/` | idem | **pronta_para_apply** | 10 |
| brisa_news | notícia | instituição | idem | `brisa_news_dryrun/` | idem | **implementada_latente** | 4 (fora 12m) |
| brisa_artigos | pesquisa | instituição | idem | `brisa_artigos_dryrun/` | `public.pesquisa` | **implementada_latente** | 7 (fora 24m) |
| ita_projetos | pesquisa | universidade | idem | `ita_projetos_dryrun/` | idem | **precisa_melhoria** | 0 válidos (4 incompletos) |
| ita_lab_guerra_eletronica | pesquisa | portal institucional | idem | `ita_lab_guerra_eletronica_dryrun/` | idem | **implementada_latente** | 1 portal |
| nasa_news | notícia+pesquisa | internacional | crawl + `build_nasa_wave2_payloads` | `audit_reports_news_research_loader/` | noticia/pesquisa | **pronta_para_apply** | payloads wave2 |
| darpa_news | notícia | internacional | `run_darpa_strategic_dryrun.py` | `darpa_strategic_dryrun/` | `public.noticia` | **pronta_para_apply** | 10/10 válidas (RSS) |
| darpa_programs_research | pesquisa | internacional | crawl sitemap + `build_darpa_programs_research_subset_valido_v2.py` | `darpa_programs_research_subset_valido_v2/` | `public.pesquisa` | **pronta_para_apply** | subset v2: 25/25 tipos OK (loader dry-run); SQL corretivo `FIX_DARPA_PROGRAMS_RESEARCH_TYPES.sql` |
| darpa_opportunities_research | review/Radar | internacional | opportunities RSS | `darpa_strategic_dryrun/review_candidates.json` | **review_for_edital** only | **pronta_para_apply** | 9 review; sem auto-edital |
| iaea_news_publications | notícia+pesquisa | internacional | crawl + build | loader/ | noticia/pesquisa | **pronta_para_apply** | wave1 prep |
| eurekalert_science_filtered | notícia+pesquisa | internacional | crawl filtrado | loader/ | noticia/pesquisa | **precisa_melhoria** | experimental/noisy |
| f35_news | notícia | internacional | `crawl_news_research` json_feed | `f35_news_dryrun/` | `public.noticia` | **pronta_para_apply** | subset top20 preparado |
| lockheed_martin_news | notícia | internacional | `crawl_news_research` lm_json_feed | `lockheed_martin_news_dryrun/` | `public.noticia` | **pronta_para_apply** | filtro técnico forte; subset pendente |
| mcti_noticias | notícia | governo | `crawl_news_research` govbr_plone_listing | `mcti_noticias_dryrun/` | `public.noticia` | **pronta_para_apply** | 22 std (7 válidos); 2 review; 6 descartados; sem apply |
| war_gov_news | notícia | governo EUA | `crawl_news_research` dod_articlecs_rss | `war_gov_news_dryrun/` | `public.noticia` | **pronta_para_apply** | 8/8 válidos (max 30); filtro forte; subset top 10–20 recomendado; sem apply |
| nato_news | notícia | OTAN internacional | `crawl_news_research` nato_sitemap + `.model.json` | `nato_news_dryrun/` | `public.noticia` | **pronta_para_apply** | 26/26 válidos (max 30); 4 review; sem apply; subset top 10–20 recomendado |
| afrl_news | notícia | AFRL EUA | `afrl_news_listing_html` | `afrl_strategic_dryrun/` | `public.noticia` | **pronta_para_apply** | 12/12 válidos (Wayback); 1 review |
| afrl_air_warfare_research | pesquisa | AFRL RA | `afrl_directorate_highlights_html` | `afrl_strategic_dryrun/` | `public.pesquisa` | **latente** | 1 institucional + extras.highlights (~45 cards) |
| afrl_space_warfare_research | pesquisa | AFRL RJ | idem | idem | `public.pesquisa` | **latente** | Space Warfare Directorate |
| afrl_technology_transition | pesquisa | AFRL RR | idem | idem | `public.pesquisa` | **latente** | portal_estrategico; possivel_edital RR |
| afrl_mission_highlights | notícia | AFRL RA/RJ/RR | `afrl_mission_highlights` | `afrl_strategic_dryrun/` | `public.noticia` | **latente** | highlights com data 12m; dry-run 2 válidos (24m); fetch live RA/RJ/RR |
| afrl_technology_areas | pesquisa | AFRL tech catalog | `military_af_research` + `build_military_expansion_subsets_valido.py` | `afrl_technology_areas_subset_valido/` | `public.pesquisa` | **pronta_para_apply** | subset 12; loader dry-run would_upsert_pesquisa=12 |
| arl_news | notícia | ARL DEVCOM | idem | `arl_news_subset_valido/` | `public.noticia` | **pronta_para_apply** | subset 12 (12m); would_upsert_noticia=12; distinto de `afrl_news` |
| arl_resources | pesquisa | ARL resources | idem | `arl_resources_subset_valido/` | `public.pesquisa` | **pronta_para_apply** | subset 18 (2 BAA excluídos); would_upsert_pesquisa=18 |
| space_force_news | notícia | USSF | idem | `space_force_news_subset_valido/` | `public.noticia` | **pronta_para_apply** | subset 18 (12m); would_upsert_noticia=18 |
| afmc_news / afnwc_news | notícia | .af.mil | `military_research_expansion_dryrun/` | idem | `public.noticia` | **latente** | 0 válidos no dry-run 2026-05-20 |
| afnwc_innovation / afnwc_weapon_systems | pesquisa | AFNWC portais | idem | idem | `public.pesquisa` | **precisa_melhoria** | fora do lote staging |

**Consolidado frente militar (staging aplicado):** [military_strategic_consolidado/consolidado_militar.md](../audit_reports_news_research/military_strategic_consolidado/consolidado_militar.md) — **11 fontes**, **187 registros** (132 notícias + 55 pesquisas); SQL validação no consolidado.

Mapa estratégico BR: [`STRATEGIC_NEWS_RESEARCH_SOURCES.md`](./STRATEGIC_NEWS_RESEARCH_SOURCES.md). Config: `config/news_research_sources.json`.

### C) Radar / Editais dedicados

| source_id | Nome | Pipeline | Artefatos | Destino | Status |
|-----------|------|----------|-----------|---------|--------|
| mcti_fomento_transformacao_digital | MCTI Fomento | `run_mcti_fomento_dryrun_v3.py` | `audit_reports_radar/mcti_fomento_dryrun_v3/` | `public.edital` (futuro) | **nao_recomendado** |

- **`apply_status`:** `não_recomendado`
- **Motivo:** 5 itens `pronto_para_apply` técnicos são chamamentos/editais **históricos** (2020–2024), sem oportunidade ativa.
- **Próxima ação:** reexecutar v3 periodicamente; apply só se surgir chamada ativa.
- Plano: [`MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md`](./MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md)

### D) Editais / Radar (legado — 102 fontes em `source_readiness.json`)

Não repetidas linha a linha aqui — ver **`BACKEND_SOURCES_INVENTORY.json`** (`module: editais_radar`).

| Bucket `source_readiness.json` | Qtd | Status canónico inventário |
|-----------------------------|----:|----------------------------|
| `ready` | 54 | **aplicada** (carga staging documentada no fluxo legado) |
| `ready_with_notes` | 36 | **pronta_para_apply** |
| `needs_manual_review` | 8 | **precisa_melhoria** |
| `blocked` | 10 | **nao_recomendado** |
| `reprocess_after_fix` | 0 | — |

Exemplos `ready`: finep, fapesp, fapesp, grants_gov, embrapii, cnen, darpa_opportunities, european_defence_fund, …  

### Grants.gov → Simpler.Grants.gov (2026)

| Item | Valor |
|------|--------|
| `source_id` | `grants_gov` (exibido: **Grants.gov**) |
| Crawler | `grants_gov/main_simpler_grants_gov.py` (`main_grants_gov.py` delega) |
| Link canônico | `https://simpler.grants.gov/opportunity/{legacy_id\|uuid}` |
| API | `POST https://api.simpler.grants.gov/v1/opportunities/search` (env `SIMPLER_GRANTS_API_KEY`; 60 req/min) |
| Fallback sem chave | `api.grants.gov/v1/api/search2` + links Simpler |
| Legado | `view-opportunity.html?oppId=` — não usar como link principal |
| Dry-run | `python scripts/grants_simpler_dryrun.py` → `audit_reports_main_pipeline/grants_simpler_dryrun/` |
| Migração DB | `python scripts/audit_grants_legacy_to_simpler.py` → `audit_reports_main_pipeline/grants_simpler_migration/` |
| Política links | [`EDITAIS_LINK_HEALTH_POLICY.md`](./EDITAIS_LINK_HEALTH_POLICY.md) § Grants Simpler |
Exemplos `blocked`: *(ver JSON)*  
Nota: `mcti` em readiness ≠ `mcti_fomento_transformacao_digital` (radar dedicado).

---

## 6. Fontes aplicadas (staging documentado)

| Módulo | Fontes | Evidência |
|--------|--------|-----------|
| Concursos wave1 | pci (12), fundatec (2), quadrix (10), legalle (5), objetiva (3), ibfc (1) | `concursos_wave1_consolidado.json` → 33 upserts |
| Concursos wave2 | avancasp (5) | `concursos_wave2_avancasp/loader_apply_staging/` |
| Editais | 54+ em `ready` | `load_ready_sources.py` quando `apply-staging` autorizado |
| Notícias | Ondas NASA/DARPA/IAEA/EurekAlert | payloads em `audit_reports_news_research_loader/` (apply via `main.py apply-news`) |
| MCTI Fomento | — | **apply não executado** |

---

## 7. Fontes prontas para apply

- **Notícias BR (dry-run):** defesanet, softex_noticias, capes_noticias, exercito_brasileiro.
- **Editais:** 36 `ready_with_notes` + parte dos `ready` já aplicados.
- **Internacional news:** nasa_wave2, iaea_wave1, darpa payloads (com gates em `main.py`).
- **Concursos:** subset ativo (quadrix, legalle, …) após re-crawl — revalidar antes de novo apply.

---

## 8. Fontes latentes

- **Concursos:** cebraspe, aocp (volume baixo), fgv, coperve, ufrgs_cv, comvest, fuvest.
- **Notícias:** brisa_news, brisa_artigos (recência fora da janela).
- **Pesquisa:** ita_lab_guerra_eletronica (portal estático).
- **MCTI:** site gov.br com arquivo histórico dominante.

---

## 9. Fontes não recomendadas para apply

- **mcti_fomento_transformacao_digital** — lote v3 histórico/encerrado.
- **fcc** — `robots.txt` / rota bloqueada para crawl automático sem revisão.
- **pci_concursos** — agregador (útil como **descoberta**, não fonte oficial).
- Fontes em `blocked` em `source_readiness.json` (10).

---

## 10. Fontes que precisam melhoria

- ita_projetos, ita/ime vestibulares (datas/OCR), consulplan, eurekalert, darpa_news (cleanup), embarcatech.
- Editais em `needs_manual_review` (8).

---

## 11. Onde ficam os artefatos

| Padrão | Exemplo |
|--------|---------|
| Crawl edital bruto | `finep/outputs/finep_editais.json` |
| Standardized edital | `audit_reports_retransform/standardized/finep_standardized.json` |
| Concursos | `audit_reports_main_pipeline/concursos_wave1_quadrix/` (`crawler_summary.json`, `standardized/`, `loader_dryrun/`, `loader_apply_staging/`) |
| News dry-run | `audit_reports_news_research/defesanet_dryrun/` |
| News payloads | `audit_reports_news_research_loader/nasa_wave2_payload_noticia.json` |
| MCTI radar v3 | `audit_reports_radar/mcti_fomento_dryrun_v3/` (`standardized/`, `review_candidates.json`, `institucional_latente.json`, `descartados_ruido.json`) |
| Daily run | `audit_reports_main_pipeline/last_run_summary.json` |

---

## 12. Comandos principais

```bash
# Inventário readiness editais
python main.py list-readiness

# Concursos (exemplo)
python concursos/main_quadrix_concursos.py
python scripts/load_concursos_selecao.py --input audit_reports_main_pipeline/concursos_wave1_quadrix/standardized/quadrix_standardized.json

# Notícias (exemplo)
python scripts/crawl_news_research_sources.py --source defesanet
python scripts/news_research/run_defesanet_dryrun.py
python scripts/load_news_research_sources.py --source defesanet --staging  # apply só com flags

# MCTI radar (sem apply)
python scripts/radar/run_mcti_fomento_dryrun_v3.py

# Orquestração (dry-run diário)
python main.py daily --skip-apply
```

---

## 13. Próximas fontes recomendadas

1. **Concursos:** reativar Cebraspe/AOCP quando houver edital ativo; melhorar Comvest/Fuvest (datas).
2. **Notícias BR:** apply piloto DefesaNet/SOFTEX/CAPES após decisão de produto.
3. **MCTI:** monitoramento periódico v3 (sem apply do arquivo atual).
4. **Editais:** promover `ready_with_notes` com retransform + validação staging.
5. **Residências / EmbarcaTech:** estabilizar crawl após erros HTTP.

---

## Regras especiais (governança)

- **Não deletar** fisicamente itens expirados nas tabelas base; views públicas filtram recência.
- **Notícias:** janela pública **12 meses**; **pesquisas:** **24 meses**.
- **Concursos:** saem da `vw_concursos_front` quando inscrição/prova deixam de ser relevantes; registo permanece.
- **MCTI Fomento:** **não aplicar** lote v3 atual (`apply_status = não_recomendado`); reexecutar periodicamente.
- **FCC:** atenção a `robots.txt`; não usar modo completo bloqueado sem revisão humana.
- **ITA/IME (concursos):** estratégicos; PDFs escaneados dificultam `data_fim_inscricao`.
- **BRISA News/Artigos:** latentes por recência no feed.
- **PCI / agregadores:** marcar como **descoberta**, não fonte oficial perfeita.
- **DARPA opportunities:** `review_for_edital` no dry-run, não carga automática em `public.edital`.

---

## Status canónico (referência)

| Status | Significado |
|--------|-------------|
| `aplicada` | Apply staging ou carga documentada |
| `pronta_para_apply` | Dry-run limpo; subset válido; apply pendente |
| `implementada_latente` | Crawler OK; sem oportunidade atual aplicável |
| `precisa_melhoria` | Ruído, incompletos, OCR, robots, cleanup |
| `nao_recomendado` | Política, dados antigos, bloqueio técnico |
| `descoberta` | Agregador útil; qualidade/link oficial incertos |

---

## Validação desta documentação

**Artefatos lidos (amostra representativa):**

- `config/source_readiness.json`, `config/news_research_sources.json`, `config/pipeline_sources.json`
- `scripts/load_news_research_sources.py`, `scripts/load_concursos_selecao.py`, `scripts/radar/*`
- `audit_reports_main_pipeline/concursos_wave1_consolidado.json`
- `audit_reports_news_research/*/summary.json` (pilotos BR)
- `audit_reports_radar/mcti_fomento_dryrun_v3/summary.json`
- `docs/CONCURSOS_FONTES_WAVE1.md`, `docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md`, `docs/MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md`
- `docs/FRONTEND_BACKEND_CONTEXT.md`, `docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md`
- `audit_reports_main_pipeline/backend_audit_overview.json`

**Arquivos criados/alterados:**

- `docs/BACKEND_SOURCES_INVENTORY.md` (este ficheiro)
- `docs/BACKEND_SOURCES_INVENTORY.json`
- Links adicionados em: `FRONTEND_BACKEND_CONTEXT.md`, `CONCURSOS_FONTES_WAVE1.md`, `STRATEGIC_NEWS_RESEARCH_SOURCES.md`, `expansion_plan.md`, `MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md`
- `scripts/build_backend_sources_inventory.py` (gerador opcional do JSON; não executar em CI sem necessidade)

**Status inferido vs incerto:**

- **Inferido com evidência:** concursos wave1/wave2 listados, pilotos BR notícias, MCTI v3, buckets `source_readiness`.
- **Incerto / depende do ambiente:** quais fontes `ready` têm apply **recente** em staging/produção (requer consulta Supabase — **não feita** nesta tarefa).
- **Incerto:** volume exacto de upsert por fonte edital internacional sem correlacionar cada `loader_apply` report.

**Não executado:** crawlers, apply, build, testes, alterações Supabase/schema/frontend.
