# Concursos & Seleções — Catálogo de fontes (wave 1)

**Inventário backend (todas as frentes):** [`BACKEND_SOURCES_INVENTORY.md`](./BACKEND_SOURCES_INVENTORY.md) · [`BACKEND_SOURCES_INVENTORY.json`](./BACKEND_SOURCES_INVENTORY.json)

**Wave 1 (piloto completo):** 9 fontes avaliadas — PCI, Fundatec, Quadrix, IBFC, Legalle, Objetiva, FGV, Cebraspe (PAS), AOCP. Consolidado: [`audit_reports_main_pipeline/concursos_wave1_consolidado.md`](../audit_reports_main_pipeline/concursos_wave1_consolidado.md) e [`.json`](../audit_reports_main_pipeline/concursos_wave1_consolidado.json).

| Status | Fontes |
|--------|--------|
| **Aplicadas em staging** (33 upserts) | `pci_concursos` (12), `fundatec` subset (2), `quadrix` (10), `legalle` (5), `objetiva` (3), `ibfc` (1) |
| **Latentes** (0 standardized ativo) | `cebraspe`, `aocp` |
| **Latente com crawl** | `fgv` (3 standardized, 1 válido; apply não executado) |

Docs por piloto: `docs/CONCURSOS_WAVE1_*_CRAWLER.md` (ver tabela no consolidado).

Catálogo inicial para priorização de crawlers **sem** misturar com `public.edital` ou Radar. Cada fonte inclui tipo (`fonte_tipo` alinhado à BD), prioridade (1 = mais cedo), dificuldade (baixa/média/alta), campos típicos, ruído esperado e modo de coleta sugerido.

**Princípios:** respeitar `robots.txt`, intervalo entre pedidos, não inventar campos, `validacao_status = incompleto` quando faltar dado crítico, e nunca ignorar bloqueios (`403`, `Disallow`).

---

## 1. Concursos / bancas

| Nome | Tipo | Prioridade | Dificuldade | Campos esperados | Risco de ruído | Coleta sugerida |
|------|------|------------|-------------|------------------|----------------|-----------------|
| **Vunesp** | banca | 1 | média | título, banca, datas inscrição/prova, taxa, link oficial | Médio (WAF/403 a bots simples) | HTML + respeitar UA; RSS se existir |
| **Cebraspe** | banca | 2 | alta (site) / média (PAS API) | ⏸ wave1 latente (0 standardized) | Médio | `main_cebraspe_concursos.py` — API PAS |
| **FGV Conhecimento** | banca | 2 | média | ⏸ wave1: 3 std, 1 válido; sem apply | Baixo | `main_fgv_concursos.py` + PDF |
| **FCC** (Carlos Chagas) | banca | 2 | média | — (Wave 2 sugerida) | Médio | HTML + PDF |
| **Quadrix** | banca | **2** (wave2) | média | ✅ wave1 apply; `concursos.quadrix.org.br` + paginação | Médio | `main_quadrix_concursos.py` |
| **Legalle** | banca | 3 | média | ✅ 5 válidos, apply staging | Médio | `main_legalle_concursos.py` |
| **Objetiva** | banca | 3 | média | ✅ 3 válidos, apply staging | Médio | `main_objetiva_concursos.py` |
| **IBFC** | banca | 3 | média | ✅ 1 válido, apply staging | Médio | `main_ibfc_concursos.py` |
| **Instituto AOCP** | banca | 3 | média | ⏸ latente (API; 0 std) | Médio | `main_aocp_concursos.py` |
| **Fundatec** | banca | 3 | média | ✅ subset 2 válidos apply | Médio | `main_fundatec_concursos.py` |
| **PCI Concursos** | agregador | 1 | média | ✅ 12 apply; 0 válidos | **Alto** | `main_pci_concursos.py` |

---

## 2. Vestibulares / ingresso

| Nome | Tipo | Prioridade | Dificuldade | Campos esperados | Risco de ruído | Coleta sugerida |
|------|------|------------|-------------|------------------|----------------|-----------------|
| **Vunesp Vestibulares** | universidade | 2 | média | curso, prova, taxa | Médio | HTML (mesmo domínio base Vunesp) |
| **Fuvest** | universidade | 1 | baixa | datas, provas, carreiras | Baixo | HTML + calendário oficial |
| **Comvest (Unicamp)** | universidade | **1** (wave2) | média | vestibular 2027, vagas olímpicas | Baixo | `main_vestibulares_comvest.py` — URLs fixas |
| **UFRGS (processo seletivo)** | universidade | 3 | média | inscrição, prova | Médio | HTML |
| **UFSC Coperve** | universidade | 3 | média | cronograma | Médio | HTML |
| **UFPR Núcleo de Concursos** | universidade | 3 | média | taxas, etapas | Médio | HTML |
| **SISU / MEC** | governo | 1 | alta | períodos nacionais, notas | Médio (API oficial preferível) | **API** MEC/INEP quando disponível |
| **PROUNI / MEC** | governo | 2 | alta | janelas nacionais | Médio | API ou CSV oficial |
| **FIES / MEC** | governo | 2 | alta | contratação, janelas | Médio | API/manual |
| **ENEM / INEP** | governo | 1 | média | datas prova, resultados | Baixo | API INEP / dados abertos |

---

## 3. Residências / formação (Wave 2 — diferencial do módulo)

Residências e programas de formação usam o mesmo `public.concurso_selecao` que concursos e vestibulares, com `tipo_selecao = residencia` e `categoria` específica — aba **Residências** em `/concursos`.

| Grupo | Tipo | Prioridade | Status |
|--------|------|------------|--------|
| **EmbarcaTech (Softex)** | RT / TIC | **1** | Piloto: `main_residencias_embarcatech.py` — ver [CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md](./CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md) |
| Residência TIC / BRISA | residência / governo | 2 | Latente — [CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md](./CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md) |
| Softex editais / CI-Expert | agregador | 2 | Mapeado; crawler futuro |
| MEC / MCTI / CAPES / CNPq / FINEP | governo | 3–4 | Latente / manual |
| Residências saúde / multiprofissional / hospitais | instituição | 5 | Wave futura — curadoria |
| Residência pedagógica / formação profissional | formação | 4 | Latente |

---

## Wave 2 — URLs priorizadas (2026)

Catálogo detalhado: [CONCURSOS_WAVE2_FONTES_PRIORIZADAS.md](./CONCURSOS_WAVE2_FONTES_PRIORIZADAS.md).

| Prioridade | Fonte | URLs principais | Crawler |
|:----------:|-------|-----------------|---------|
| **Alta** | Comvest 2027 | `…/ingresso-2027/vestibular-2027/`, `…/vagas-olimpicas-2027/` | `main_vestibulares_comvest.py` |
| **Alta** | Fuvest | `fuvest.br/vestibular-da-usp`, `/concursos/` | `main_fuvest_concursos.py` |
| **Alta** | AOCP | `institutoaocp.org.br/…/inscricoes-abertas` + API `link.institutoaocp.org.br` | `main_aocp_concursos.py` (API atualizada) |
| **Alta** | Quadrix | `concursos.quadrix.org.br/index/abertos/` + pg=2,3 | `main_quadrix_concursos.py` (paginação) |
| **Alta** | FCC | `concursosfcc.com.br/concursoInscricaoAberta.html` | `main_fcc_concursos.py` — ver [CONCURSOS_WAVE2_FCC_CRAWLER.md](./CONCURSOS_WAVE2_FCC_CRAWLER.md) |
| **Alta** | Avança SP | `avancasp.org.br/index/abertos/` | `main_avancasp_concursos.py` — ver [CONCURSOS_WAVE2_AVANCASP_CRAWLER.md](./CONCURSOS_WAVE2_AVANCASP_CRAWLER.md) |
| **Alta** | Consulplan | `institutoconsulplan.org.br/concursosNovo.aspx` | `main_consulplan_concursos.py` — ver [CONCURSOS_WAVE2_CONSULPLAN_CRAWLER.md](./CONCURSOS_WAVE2_CONSULPLAN_CRAWLER.md) |
| **Estratégica** | ITA Vestibular | `vestibular.ita.br` | `main_militar_aeroespacial_ita.py` — [militar/aeroespacial](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md) |
| **Média** | UFRGS/COPERSE | `ufrgs.br/coperse/concurso-vestibular/`, `sobre-o-vestibular-2/` | `main_vestibulares_ufrgs.py` (latente) |
| **Média** | Cebraspe | `cebraspe.org.br/concursos/` | `main_cebraspe_concursos.py` (latente) |
| **Média** | Fuvest residência/pós | `/residencia/`, `/pos-graduacao/` | pendente |
| Vestibulares latentes | Coperve UFSC | `coperve.ufsc.br` | `main_vestibulares_coperve.py` |

Filtros frontend (futuro): [CONCURSOS_FILTROS_EXPANSAO.md](./CONCURSOS_FILTROS_EXPANSAO.md).

---

## Próximos passos (pós-consolidado Wave 1)

1. ~~Piloto wave1 (9 fontes)~~ — ver consolidado.
2. **Manter crawls periódicos:** Quadrix, Legalle, Objetiva, Fundatec (subset).
3. **Latentes wave1:** Cebraspe (PAS), FGV (certames «Em Andamento»). **AOCP:** reativar com API `link.institutoaocp.org.br`.
4. **Wave 2 em curso:** Comvest, Fuvest, vestibulares (Coperve/UFRGS latentes), Residências (EmbarcaTech piloto).
5. CI: dry-run loader após cada coleta (`errors_count` = 0). **Apply não executado** na wave 2 até validação.
6. Decisões históricas: `docs/CONCURSOS_WAVE1_PILOT_DECISION.md`, `docs/CONCURSOS_WAVE1_CRAWLER_PILOT.md`.
