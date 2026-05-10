# Lote Credito / Desenvolvimento — Onda B (Multilaterais e Inovacao Internacional)

**Data:** 2026-05-05 (UTC)  
**Fontes:** `bid_lab`, `caf`, `fonplata`, `eureka_network`, `eic`

## Escopo e separacao de destinos

| Destino | Criterio |
|--------|-----------|
| **public.edital** | Chamada aberta, aplicacao/submissao, programa com formulario, procurement formal, grant/call com mecanismo acionavel. |
| **public.noticia** | Anuncios, resultados, releases, eventos sem inscricao. |
| **public.pesquisa** | Relatorios, WP explicativos, paginas de programa sem call aberta, material institucional nao acionavel. |

**Proibicoes (lote):** nao misturar noticia com edital; nao salvar homepage generica como oportunidade; nao inventar prazo/valor; sem scraping agressivo ou bypass de WAF/login.

### Tipos de oportunidade (referencia)

`funding_opportunity`, `chamada_publica`, `call_for_proposals`, `innovation_programme`, `startup_programme`, `accelerator`, `grant`, `financiamento`, `credito`, `procurement`, `technical_cooperation`, `project_financing`, `programa_agregado`.

### Calibracao local

`CORE/taxonomy_filtros.py`: nucleo `_calibrate_multilateral_innovation_core` + `calibrate_*_extras` por fonte.  
`CORE/transformer.py`: `opportunity_gate_multilateral_onda_b_soft` (hosts oficiais, heuristica conservadora) — **sem** alterar `opportunity_gate` global.

---

## Diagnostico por fonte

### BID Lab (`bid_lab`)

| Item | Status |
|------|--------|
| Crawler | `bid_lab/main_bid_lab.py` → `bid_lab/outputs/bid_lab_editais.json` |
| Coleta | **0 itens** — Cloudflare 403 em `bidlab.org` |
| URLs uteis | `/en/call-for-proposals`, `/en/calls`, `/en/innovation`, `/en/venture`; espelho institucional BID em `iadb.org` |
| Excluir | news, blog, events, about, press sem call |
| Readiness | **blocked** — acesso automatizado barrado; considerar RSS/API/manual se existir canal oficial |

### CAF (`caf`)

| Item | Status |
|------|--------|
| Crawler | `caf/main_caf.py` → `caf/outputs/caf_editais.json` |
| Coleta | **0 itens** — resposta Incapsula em HTML leve; probes com falha TLS no ambiente |
| URLs uteis | `…/convocatorias/`, `…/actualidad/convocatorias/`, procurement |
| Excluir | sala de prensa, noticias, eventos sem inscricao |
| Readiness | **blocked** para crawler leve; **needs_manual_review** se houver curadoria de URLs estaveis exportadas manualmente |

### FONPLATA (`fonplata`)

| Item | Status |
|------|--------|
| Crawler | `fonplata/main_fonplata.py` → `fonplata/outputs/fonplata_editais.json` |
| Coleta | **7 brutos**, **5 transformados**, **2 rejeitados** pelo gate (relevancia baixa: roster consultores, RH) |
| URLs uteis | `/es/oportunidades`, adquisiciones, reclutamiento (filtrar emprego vs consultoria) |
| Excluir | “o que fazemos”, financiamento generico, contacto isolado |
| Readiness | **needs_manual_review** — volume baixo, mistura RH/roster/projetos; sem PDFs na amostra |

### Eureka Network (`eureka_network`)

| Item | Status |
|------|--------|
| Crawler | `eureka_network/main_eureka_network.py` |
| Coleta | **23 brutos**, **21 transformados**; **2** cortados (pagina tipo login: Eurostars hub, resource library) |
| URLs uteis | Open calls, programmes-and-calls, feed RSS, Eurostars/Globalstars/Network Projects |
| Excluir | biblioteca de recursos generica, noticia sem submissao |
| Readiness | **ready_with_notes** — chamadas reais; revisar hubs vs call especifica; PDFs parciais |

### EIC (`eic`)

| Item | Status |
|------|--------|
| Crawler | `eic/main_eic.py` |
| Coleta | **14 brutos**, **14 transformados**; forte alinhamento com funding oficial |
| URLs uteis | `eic-funding-opportunities`, Pathfinder/Transition/Accelerator, `calls-proposals`, sitemap |
| Excluir | news, webinars sem aplicacao, success stories |
| Readiness | **ready_with_notes** — distinguir programa agregador vs call com deadline; validar extracao de valores do PDF |

---

## Pipeline executado (dry-run)

```text
python bid_lab/main_bid_lab.py
python caf/main_caf.py
python fonplata/main_fonplata.py
python eureka_network/main_eureka_network.py
python eic/main_eic.py

python scripts/retransform_all.py --sources bid_lab,caf,fonplata,eureka_network,eic --dry-run --output-dir audit_reports_credito/lote_credito_multilateral_onda_b_fix
python scripts/audit_semantic_classification.py --input-dir audit_reports_credito/lote_credito_multilateral_onda_b_fix/standardized --output-dir audit_reports_credito/lote_credito_multilateral_onda_b_semantic
python scripts/audit_docs_pipeline.py --sources bid_lab,caf,fonplata,eureka_network,eic --output-dir audit_reports_credito/lote_credito_multilateral_onda_b_docs
python scripts/audit_source_access_methods.py --sources bid_lab,caf,fonplata,eureka_network,eic --output-dir audit_reports_credito/lote_credito_multilateral_onda_b_access
```

### Resumo numerico (retransform)

- Itens brutos total: **44**
- Transformados: **40**
- Rejeitados (gate): **4**
- Aviso: carregamento de perfis Supabase no transformer (coluna inexistente no ambiente) — **nao** foi executado apply.

### Auditoria semantica

Ver `audit_reports_credito/lote_credito_multilateral_onda_b_semantic/audit_semantic_summary.md` — poucos flags; 1 ocorrencia de classificacao muito ampla no conjunto.

### Auditoria de documentos

`audit_docs_pipeline` com `pdf_skip`/downloads: muitas falhas de download no ambiente de auditoria; preservacao estrutural de links PDF nos itens EIC/Eureka.

---

## Entregaveis gerados

| Artefato | Caminho |
|----------|---------|
| Diagnostico JSON | `audit_reports_credito/lote_credito_multilateral_onda_b_diagnostico.json` |
| Diagnostico MD | `audit_reports_credito/lote_credito_multilateral_onda_b_diagnostico.md` |
| Por fonte | `audit_reports_credito/lote_credito_multilateral_onda_b_by_source.json` |
| Exemplos | `audit_reports_credito/lote_credito_multilateral_onda_b_examples.json` |
| Retransform | `audit_reports_credito/lote_credito_multilateral_onda_b_fix/` |
| Semantica | `audit_reports_credito/lote_credito_multilateral_onda_b_semantic/` |
| Docs | `audit_reports_credito/lote_credito_multilateral_onda_b_docs/` |
| Acesso | `audit_reports_credito/lote_credito_multilateral_onda_b_access/` |

**Nao atualizado:** `config/source_readiness.json`.

---

## Ajuste aplicado nesta sessao

- `caf/main_caf.py`: removido exclusor de URL `/trabaja-con-nosotros` que descartava convocatorias legitimas nesse path; coleta continua **0** por WAF/Incapsula, nao por filtro de path.

## Proximos passos sugeridos

- BID Lab / CAF: definir entrada manual, parceria ou feed oficial; nao aumentar agressividade do scraper.
- Eureka: avaliar extensao do soft-continue para hubs `…/eurostars/` se o conteudo for publico sem login.
- FONPLATA: filtrar na origem URLs `reclutamiento` vs `adquisiciones` vs projetos.
- EIC: opcionalmente priorizar sitemap filtrado por `calls-proposals` para reduzir paginas agregadoras.
