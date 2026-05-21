# Concursos & Seleções — Wave 1 (consolidado)

**Consolidado em:** 2026-05-16 (UTC)  
**Base:** artefatos em `audit_reports_main_pipeline/concursos_wave1_*` (crawler, standardized, loader dry-run e apply staging quando existente).  
**Nesta tarefa:** nenhum apply, alteração de código, Supabase ou frontend.

---

## Visão geral

| Métrica | Valor |
|---------|------:|
| Fontes avaliadas | **9** |
| Total standardized (soma por fonte) | **41** |
| Total `validacao_status = valido` | **22** |
| Total `incompleto` | **19** |
| Aplicados em staging (upserts) | **33** |
| Fontes latentes (0 standardized) | **2** (Cebraspe, AOCP) |
| Loader dry-run `errors_count` (todas) | **0** |

**Staging hoje:** PCI (12) + Fundatec subset (2) + Quadrix (10) + Legalle (5) + Objetiva (3) + IBFC (1) = **33** linhas upsertadas sem erros de loader nos relatórios analisados.

---

## Tabela por fonte

| Fonte | Tipo | Bruto | Standardized | Apply staging | errors | Válidos | Incompletos | Qualidade | Status | Recomendação |
|-------|------|------:|-------------:|--------------:|-------:|--------:|------------:|-----------|--------|--------------|
| **pci_concursos** | agregador | 24 | 12 | 12 | 0 | 0 | 12 | média | aplicada | Descoberta; não substitui edital oficial |
| **fundatec** | regional | 10 | 7 | 2* | 0 | 2 | 5 | média | aplicada | Apply só subset válido; melhorar taxa no crawl completo |
| **quadrix** | banca oficial | 10 | 10 | 10 | 0 | 10 | 0 | média | aplicada | Melhor rendimento; crawl periódico |
| **legalle** | banca oficial | 60 | 5 | 5 | 0 | 5 | 0 | média | aplicada | Alto descarte por recência; subset ativo forte |
| **objetiva** | banca oficial | 12 | 3 | 3 | 0 | 3 | 0 | média | aplicada | CMS selecao.net; volume baixo, apply limpo |
| **ibfc** | banca oficial | 10 | 1 | 1 | 0 | 1 | 0 | média | aplicada | Família Quadrix; quase tudo descartado |
| **fgv** | banca oficial | 32 | 3 | 0 | 0 | 1 | 2 | média | latente | 1 válido no subset; inscrição encerrada na ref.; sem apply |
| **cebraspe** | banca oficial | 12† | 0 | 0 | 0 | 0 | 0 | n/a | latente | API PAS; todas etapas encerradas |
| **aocp** | banca oficial | 1‡ | 0 | 0 | 0 | 0 | 0 | n/a | latente | 1 IN_PROGRESS descartado (resultado final) |

\* Apply via `concursos_wave1_fundatec_subset_valido`.  
† `total_bruto_api` Cebraspe PAS.  
‡ `total_bruto_lista_filtrada` IN_PROGRESS (lista API: 230).

---

## Classificação estratégica

### Boas para continuar rodando

- **quadrix** — 10/10 válidos, apply staging OK  
- **legalle** — 5/5 válidos no subset ativo  
- **objetiva** — 3/3 válidos, apply recente  
- **fundatec** — modo conservador (subset válido) comprovado em staging  

### Úteis como descoberta

- **pci_concursos** — volume e heurísticas de vagas/salário; 12 aplicados mas **0 válidos** (falta `data_fim_inscricao` típica de agregador)

### Latentes

- **cebraspe** — piloto PAS sem oportunidade ativa na corrida de referência  
- **aocp** — API pronta; filtro e descarte de não-oportunidade zeram o lote  
- **fgv** — crawler + PDF enrichment; apply adiado por recência / 1 item válido isolado  

### Precisam melhoria

- **pci** — extrair ou inferir datas de inscrição com mais rigor  
- **fundatec** — subir proporção de `valido` no crawl completo (7 → meta ≥4 válidos)  
- **ibfc** — volume ativo muito baixo (1 standardized)  
- **fgv** — priorizar certames «Em Andamento» e revalidar subset antes de apply  

---

## Totais e rendimento

| Fonte | Standardized | Válidos | Taxa válido |
|-------|-------------:|--------:|------------:|
| quadrix | 10 | 10 | 100% |
| legalle | 5 | 5 | 100% |
| objetiva | 3 | 3 | 100% |
| fundatec | 7 | 2 | 29% |
| fgv | 3 | 1 | 33% |
| pci | 12 | 0 | 0% |
| ibfc | 1 | 1 | 100% |
| cebraspe / aocp | 0 | 0 | — |

**Maior volume aplicado em staging:** Quadrix (10), PCI (12).  
**Melhor qualidade de validação entre bancas oficiais aplicadas:** Quadrix, Legalle, Objetiva (100% válidos no standardized gravado).

---

## Campos (41 itens standardized, agregado)

| Campo | Preenchidos | % |
|-------|------------:|--:|
| titulo, tipo_selecao, banca, link_edital | 41 | 100% |
| nivel_escolaridade | 37 | 90% |
| orgao | 35 | 85% |
| taxa_inscricao | 31 | 76% |
| numero_vagas | 29 | 71% |
| data_fim_inscricao | 22 | 54% |
| data_prova | 20 | 49% |
| cargo | 18 | 44% |
| salario_min / salario_max | 19 | 46% |
| estado / municipio | 13 | 32% |
| area | 0 | 0% |

**Fortes:** título, tipo, banca, PDF edital, nível, órgão.  
**Fracos:** área, geografia (UF/município), salários, datas de prova, cargo (depende da fonte).

---

## Próximas fontes (Wave 2 sugerida)

| Prioridade | Fonte | Tipo | Motivo |
|:----------:|-------|------|--------|
| 1 | **FCC** | banca oficial | HTML; complementa stack selecao.net |
| 2 | **Concursos no Brasil** | agregador | Segundo agregador; dedupe com PCI |
| 2 | **Vunesp / Vestibulares** | universidade | Expansão ingresso; stub no repo |
| 3 | **Residências / Formação** | residência | `tipo_selecao` + curadoria; wave dedicada |

---

## Documentação por fonte

| Fonte | Doc |
|-------|-----|
| PCI | `docs/CONCURSOS_WAVE1_CRAWLER_PILOT.md` |
| Fundatec | `docs/CONCURSOS_WAVE1_FUNDATEC_CRAWLER.md` |
| Quadrix | `docs/CONCURSOS_WAVE1_QUADRIX_CRAWLER.md` |
| IBFC | `docs/CONCURSOS_WAVE1_IBFC_CRAWLER.md` |
| Legalle | `docs/CONCURSOS_WAVE1_LEGALLE_CRAWLER.md` |
| Objetiva | `docs/CONCURSOS_WAVE1_OBJETIVA_CRAWLER.md` |
| FGV | `docs/CONCURSOS_WAVE1_FGV_CRAWLER.md` |
| Cebraspe | `docs/CONCURSOS_WAVE1_CEBRASPE_CRAWLER.md` |
| AOCP | `docs/CONCURSOS_WAVE1_AOCP_CRAWLER.md` |
| Catálogo | `docs/CONCURSOS_FONTES_WAVE1.md` |

JSON estruturado: [`concursos_wave1_consolidado.json`](./concursos_wave1_consolidado.json).
