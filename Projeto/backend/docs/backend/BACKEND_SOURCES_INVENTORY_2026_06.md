# Inventário de fontes do backend — EditalFinder (2026-06)

**Patch:** BACKEND SOURCES INVENTORY 2026-06 — preparação para Backend 10.1  
**Gerado em:** 2026-06-05 (auditoria de código/configs + outputs Backend 10.1)  
**Versão estruturada:** [`../BACKEND_SOURCES_INVENTORY.json`](../BACKEND_SOURCES_INVENTORY.json)  
**Documento legado (histórico):** [`../BACKEND_SOURCES_INVENTORY.md`](../BACKEND_SOURCES_INVENTORY.md)

> **Escopo desta tarefa:** documentação e consolidação. **Não** foi executado apply, migration, alteração Supabase nem correção de crawlers/classificador.

---

## 1. Resumo executivo

| Métrica | Valor |
|---|--:|
| Fontes mapeadas | **159** |
| Aplicadas | **60** |
| Prontas para apply | **43** |
| Implementadas latentes | **8** |
| Precisam melhoria | **16** |
| Não recomendadas | **12** |
| Em descoberta | **1** |
| Dry-run OK (news, sem classificação fina) | **19** |
| Fontes com ruído alto (audit ≥5% e ≥3 reg.) | **7** |
| Fontes prioritárias Backend 10.1 (alta/média) | **~15** (ver §4) |
| Fontes candidatas a novo crawler (pós-10.1) | **~8 lacunas** (ver §7) |

### Contexto pós-Frontend 1.1 / Backend 10

- Frontend 1.1 estabilizado (EXE, links, feedback, PDF).
- Backend 10 introduziu `actionability_type`, `classification_bucket`, `is_noise`, `noise_type`, validade e quality em **dry-run/enricher**.
- Backend 10.1 **corrigiu semântica de ruído** em staging (1232 registros): `is_noise=true` caiu de ~930 para **25 (2,0%)**.
- Campos Backend 10.1 **ainda não persistidos** em `public.edital` — ver [`DATABASE_CURRENT_SCHEMA.md`](./DATABASE_CURRENT_SCHEMA.md).

### Problema principal identificado

Não é falta imediata de fontes, e sim **classificação + acionabilidade**:

1. **968 registros (78,6%)** em `desconhecido` — crawlers internacionais/asiáticos sem marcadores fortes.
2. **82** `oportunidade_sem_prazo` vs confusão histórica com `nao_aplicavel`.
3. **Portais úteis** (BNB, Eureka, CAPES) ainda em `public.edital` quando deveriam ser `portal_estrategico` ou non-actionable sem ruído duro.
4. **BDMG / QST / NSFC** com ruído residual alto no dry-run.
5. Chamadas reais (CNPq) **eram** classificadas como `resultado` no Backend 10 — **corrigido em 10.1** (regressão em `test_noise_classifier.py`).

**Conclusão:** retomar Backend 10.1 **antes** de expandir fontes.

---

## 2. Resumo por módulo

| Módulo | Fontes | Tabelas/views | Loader principal | Observação |
|---|---:|---|---|---|
| Editais / Radar (legado) | **107** | `public.edital` → `vw_editais_front` | `load_ready_sources.py` | `source_readiness.json`: 54 ready + 36 ready_with_notes + 8 review + 10 blocked |
| Concursos & Seleções | **19** | `public.concurso_selecao` → `vw_concursos_front` | `load_concursos_selecao.py` | Wave1/wave2; 7 aplicadas com subset válido |
| Notícias / Pesquisas | **32** | `public.noticia`, `public.pesquisa` | `load_news_research_sources.py` | Config `news_research_sources.json`; governança `no_edital_from_news_module` |
| Radar dedicado (MCTI Fomento) | **1** | `public.edital` (futuro) | `run_mcti_fomento_dryrun_v3.py` | **não_recomendado** — lote histórico |
| Portais estratégicos | *(subconjunto editais)* | `public.portal_estrategico` | `load_portais_estrategicos.py` | BNB/EIC/suppliers; não duplicar em edital |
| Outros / legado | — | — | `main.py` orquestração | `pipeline_sources.json` quase vazio (ondas news) |

**Contagem configs:**

| Config | Entradas |
|--------|--------:|
| `source_readiness.json` | 108 slugs (107 no inventário — `mcti` separado de notícias/radar) |
| `news_research_sources.json` | 32 |
| Concursos rastreados | 19 |
| Radar MCTI | 1 |

---

## 3. Resumo por status operacional

| Status | Quantidade | Significado | Próxima ação |
|---|---:|---|---|
| `aplicada` | 60 | Carga staging/documentada (54 editais `ready` + concursos apply) | Revalidar ruído pós-10.1 antes de novo apply |
| `pronta_para_apply` | 43 | Dry-run limpo; subset válido | Apply só após 10.1 persistido + decisão produto |
| `dryrun_ok` | 19 | News internacional/militar com payloads | Classificar pronta/latente; subset staging |
| `implementada_latente` | 8 | Crawler OK; sem oportunidade atual | Monitorar recrawl |
| `precisa_melhoria` | 16 | OCR, robots, WAF, incompletos | Corrigir crawler ou classificador |
| `nao_recomendado` | 12 | Bloqueio técnico, histórico, política | Manter blocked; MCTI radar sem apply |
| `descoberta` | 1 | Agregador (PCI) | Não tratar como fonte oficial |
| `desatualizada` | 0 | — | — |
| `desconhecida` | 0 | — | — |

### Mapeamento `source_readiness.json` → status inventário

| Bucket readiness | Qtd | Status canónico |
|------------------|----:|-----------------|
| `ready` | 54 | `aplicada` |
| `ready_with_notes` | 36 | `pronta_para_apply` |
| `needs_manual_review` | 8 | `precisa_melhoria` |
| `blocked` | 10 | `nao_recomendado` |

Fontes `blocked`: bid_lab, caf, china_cnnc, dcta_ita_iae, esa_star, japan_e_rad, japan_jaxa, marinha, sam_gov, science_scraper.

---

## 4. Fontes prioritárias para Backend 10.1

| Fonte | Módulo | Problema observado | Evidência | Ação recomendada |
|---|---|---|---|---|
| **bdmg** | editais | 28,9% ruído; portal_generico + notícia em edital | `noise_by_source.json` 11/38 | Corrigir classificador; mover hubs para `portal_estrategico` |
| **japan_qst** | editais | 100% ruído (5/5) | audit noise | Bloquear apply; revisar crawler ou excluir de edital |
| **bnb** | editais | 17× `portal_util` em edital | `source_actionability_breakdown.json` | Mover para `portal_estrategico` |
| **eureka_network** | editais | 10× `portal_util` | actionability breakdown | Mover módulo / portal |
| **cnpq** | editais | Falsos `resultado` no B10 | B10.1: 13 principal, 0 resultado falso | Manter; validar regressão |
| **bndes** | editais | 20 acionáveis; 20 sem prazo útil | `by_source.json` validity | Melhorar parser prazo; não inflar `nao_aplicavel` |
| **grants_gov** | editais | 119/127 `desconhecido` | actionability breakdown | Classificador EN + perfil fonte |
| **china_mofcom_tendering** | editais | 131 `desconhecido` | actionability breakdown | Perfil fonte asiática (10.1C) |
| **embrapii** | editais | 10 resultado + 10 acionáveis misturados | actionability breakdown | Separar resultado de chamada ativa |
| **china_nsfc** | editais | 13,3% ruído | noise_by_source | Revisar classificador |
| **dod_sbir_sttr** | editais | portal_util + ruído residual | noise + profiles | portal_util ≠ ruído; revisar perfil |
| **mcti** | editais | Confusão com `mcti_noticias` / radar | 2 módulos distintos | Separar: notícia → `noticia`; fomento → radar |
| **amazul** | editais | 20 acionáveis; 6 sem prazo | quality ranking + validity | Manter; enriquecer prazo (10.1D) |
| **fapesc / cnpq / embrapii** | editais | Alta qualidade, baixo ruído | `source_quality_ranking.json` | Candidatos apply pós-10.1 |
| **eurekalert_science_filtered** | notícias | experimental; WAF/medicina | config status | Precisa melhoria crawler; não misturar edital |

---

## 5. Fontes com ruído alto

Dry-run Backend **10.1** — `outputs/audit_noise_backend/` (1232 registros, **não recalculado nesta auditoria de inventário**).

| Fonte | Total analisado | Ruído provável | % ruído | Tipo dominante | Recomendação |
|---|---:|---:|---:|---|---|
| BDMG | 38 | 11 | 28,9% | portal_generico, noticia | Perfil fonte + mover portal |
| QST (japan_qst) | 5 | 5 | 100,0% | noticia/portal | Bloquear ou sair de edital |
| NSFC (china_nsfc) | 30 | 4 | 13,3% | noticia | Classificador + revisão manual |
| DoD SBIR/STTR | 15 | 2 | 13,3% | portal | portal_util, não ruído duro |
| NUCLEP | 20 | 1 | 5,0% | portal_generico | Revisar 1 caso |
| European Defence Fund | 18 | 1 | 5,6% | — | Monitorar |
| EIC | 14 | 1 | 7,1% | — | portal_util → portal_estrategico |

**Ruído global:** 25 registros `is_noise=true` (2,0%) — tipos: `noticia` (14), `portal` (11).

Para recalcular:

```bash
cd backend
python scripts/audit_noise_backend.py --from-db --limit 5000
```

---

## 6. Fontes com oportunidades reais

| Fonte | Oportunidades acionáveis | Sem prazo | Com prazo | Qualidade média | Recomendação |
|---|---:|---:|---:|---:|---|
| AMAZUL | 20 | 6 | 14 | 95,0 | Manter; 10.1D prazo |
| BNDES | 20 | 20 | 0 | — | Parser prazo urgente |
| CNPQ | 13 | 0 | 13 | 99,7 | Core BR; apply pós-10.1 |
| DOE_ARPAE | 11 | 11 | 0 | — | Enriquecer validade |
| EMBRAPII | 10 | 2 | 8 | 94,2 | Separar resultados históricos |
| FAPESC | 10 | 0 | 10 | 100,0 | Excelente; manter |
| Grants.gov | 8 | 5 | 3 | — | Classificar desconhecidos |
| BDMG | 7 | 7 | 0 | — | Corrigir ruído antes de apply |
| CONFAP | 5 | 2 | 3 | 92,8 | Manter |
| ERC | 5 | 5 | 0 | — | Prazo |

**Total staging:** 136 oportunidades acionáveis (11,0% do corpus analisado).

Fontes com **80 acionáveis sem validade útil** — ver `audit_validity_backend/summary.md`.

---

## 7. Fontes que precisam de mais editais (lacunas — candidatas futuras)

> **Não adicionar fontes nesta etapa.** Apenas mapear lacunas para Backend 10.1E.

| Lacuna | O que falta | Por que | Candidatas a pesquisar depois | Crawler vs classificador |
|--------|-------------|---------|------------------------------|--------------------------|
| Brasil — fomento/inovação | Volume ativo Finep/FAPESP já existe; falta **prazo estruturado** em várias | Parsers fracos | Simpler.Grants.gov já mapeado; reforçar BNDES/EMBRAPII | **Classificador + prazo** primeiro |
| Brasil — compras/licitações | PNCP/pncp_defesa em ready_with_notes | Pouco apply recente documentado | Compras.gov.br, licitações estaduais | Novo crawler **após** 10.1 |
| Brasil — pesquisa/ICT | CAPES editais vs notícias misturados | portal_util em edital | Separar CAPES edital vs `capes_noticias` | **Mover módulo** |
| Internacional — grants | Grants.gov 93% desconhecido | Marcadores EN fracos | NSF, UKRI (já em readiness), Horizon | **Classificador 10.1A/C** |
| Internacional — defesa/aero | News militar forte; editais SBIR mistos | portal vs oportunidade | DIU, AFRL opportunities (review) | Perfil fonte |
| Internacional — supplier | Lockheed/GD/BAE suppliers em edital | Deveria ser portal_estrategico | Já em `ready` | **Mover módulo** |
| Concursos | Vestibulares ITA/IME/Comvest incompletos | OCR/datas | Cebraspe quando ativo | Crawler |
| Notícias/Pesquisas | 32 fontes; apply produto pendente | Módulo separado OK | MCTI notícias, NATO, War.gov prontos | Apply notícias, não edital |

---

## 8. Fontes que devem sair do fluxo de editais

| Fonte | Motivo | Destino recomendado |
|---|---|---|
| bnb | 17× portal_util (atividades financiadas) | `portal_estrategico` |
| bdmg | portal_generico + notícia + 28,9% ruído | `portal_estrategico` + curadoria |
| eureka_network | Hub funding europeu | `portal_estrategico` |
| lockheed_martin_suppliers, general_dynamics_suppliers, bae_systems_suppliers, rheinmetall_suppliers, thales_suppliers | Supplier/procurement | `portal_estrategico` |
| japan_qst | 100% ruído no dry-run | `bloquear` ou pesquisa/notícia |
| mcti_noticias | Notícias gov.br CT&I | `noticia` (já em news module) |
| darpa_news, war_gov_news, nato_news, defesanet, … | Módulo news | `noticia` — **não** `edital` |
| darpa_opportunities_research | review_for_edital only | Manter review; não auto-apply edital |
| pci_concursos | Agregador | `descoberta` → `concurso_selecao` se validado |
| mcti_fomento_transformacao_digital | Lote histórico encerrado | Bloquear apply; radar dedicado |

---

## 9. Relação com Backend 10.1

Backend 10.1 deve corrigir **classificação antes de expandir fontes**.

### Prioridades (ordem)

1. **10.1A — Actionability Priority Fix** — chamadas reais não viram `resultado`; oportunidade forte primeiro ([`BACKEND_10_1_ACTIONABILITY_PRIORITY_FIX.md`](./BACKEND_10_1_ACTIONABILITY_PRIORITY_FIX.md)).
2. **10.1B — Noise Semantics Fix** — `is_noise` só para portal_generico/noticia/sem_oportunidade; `portal_util`, `resultado`, `documento_auxiliar`, `evento` **fora** do ruído duro.
3. **10.1C — Source-level Noise Profiles** — BDMG, BNB, fontes asiáticas, NSFC, MOFCOM.
4. **10.1D — Validity/Prazo Enrichment** — 80 acionáveis sem prazo (BNDES, DOE_ARPAE, …).
5. **10.1E — New Sources Gap Analysis** — só se cobertura acionável continuar baixa **após** 10.1A–D.

### Métricas de referência (dry-run 1232 reg.)

| Métrica | Backend 10 | Backend 10.1 |
|---------|----------:|-------------:|
| Acionáveis | 175 | **136** |
| Ruído `is_noise` | ~930 | **25 (2,0%)** |
| `oportunidade_principal` | 43 | **54** |
| `oportunidade_sem_prazo` | 132 | **82** |
| `desconhecido` | — | **968 (78,6%)** |

Ver também [`BACKEND_10_NOISE_CALIBRATION.md`](./BACKEND_10_NOISE_CALIBRATION.md).

---

## 10. Comandos recomendados de auditoria

**Documentar apenas — não executar apply nesta tarefa.**

```bash
cd backend

# Inventário JSON (regenerar a partir de configs)
python scripts/build_backend_sources_inventory.py

# Ruído e acionabilidade (Backend 10.1)
python scripts/audit_noise_backend.py --from-db --limit 5000

# Validade e prazos
python scripts/audit_validity_backend.py --from-db --limit 5000

# Enriquecimento dry-run (sem persistir)
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000

# Readiness editais
python main.py list-readiness

# Testes regressão classificador
python -m pytest tests/test_noise_classifier.py tests/test_validity_resolver.py -q
```

**Não existe** `generate_backend_sources_inventory.py` — usar `scripts/build_backend_sources_inventory.py`.

---

## 11. Próximo plano recomendado

| Patch | Escopo |
|-------|--------|
| **BACKEND 10.1A** | Actionability priority — CNPq/BNDES/EMBRAPII regressão |
| **BACKEND 10.1B** | Noise semantics — `is_noise` estreito; buckets corretos |
| **BACKEND 10.1C** | Perfis por fonte — BDMG, BNB, China, suppliers |
| **BACKEND 10.1D** | Validity/prazo — BNDES, DOE_ARPAE, Grants.gov |
| **BACKEND 10.1E** | Gap analysis novas fontes — **somente após** A–D |

### Decisão estratégica

| Pergunta | Resposta |
|----------|----------|
| Adicionar fontes novas agora? | **Não** — corrigir ruído/acionabilidade primeiro |
| Próximo patch? | **BACKEND 10.1A** (actionability priority + testes) |
| Apply de staging? | Suspender até 10.1 persistido e nova auditoria |

---

## 12. Changelog

| Data | Alteração |
|------|-----------|
| 2026-05-20 | Inventário 157 fontes (pré-Backend 10.1 métricas) |
| 2026-06-05 | Inventário 159 fontes; integração outputs Backend 10.1; preparação retomada 10.1 |

---

## Validação

**Consultado:**

- `config/source_readiness.json`, `pipeline_sources.json`, `news_research_sources.json`
- `scripts/audit_noise_backend.py`, `audit_validity_backend.py`, `dry_run_quality_enrichment.py`
- `outputs/audit_noise_backend/*`, `outputs/audit_validity_backend/*`, `outputs/backend_9_quality_dry_run/*`
- `docs/backend/BACKEND_10_NOISE_CALIBRATION.md`, `BACKEND_10_1_ACTIONABILITY_PRIORITY_FIX.md`
- `docs/PROJECT_TECHNICAL_MAP.md` (se existir no repo)

**Não executado:** apply, migration, crawlers, Supabase, frontend.
