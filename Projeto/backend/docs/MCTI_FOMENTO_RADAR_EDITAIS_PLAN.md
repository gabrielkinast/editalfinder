# MCTI Fomento — plano Radar / Editais

**Inventário backend (todas as frentes):** [`BACKEND_SOURCES_INVENTORY.md`](./BACKEND_SOURCES_INVENTORY.md) · [`BACKEND_SOURCES_INVENTORY.json`](./BACKEND_SOURCES_INVENTORY.json)

## Objetivo

Ingerir **oportunidades e editais/chamadas** do MCTI no produto **Radar / Editais**, sem `public.noticia`.

## Decisão de apply (2026-05-17)

| Campo | Valor |
|-------|--------|
| **apply_status** | `não_recomendado` |
| **apply_executed** | `false` |
| **motivo** | Os 5 itens classificados como `pronto_para_apply` na curadoria v3 são **históricos/encerrados** (editais e chamamentos de 2020–2024, muitos sem prazo ativo ou com processos já concluídos). Não representam oportunidades atuais para o produto. |
| **infraestrutura** | Crawler (`mcti_fomento_lib.py`), seeds, curadoria v3 e artefatos em `mcti_fomento_dryrun_v3/` **mantidos** — pipeline validado, pronto para reexecução. |
| **próxima_ação** | Reexecutar periodicamente `run_mcti_fomento_dryrun_v3.py` (ex.: mensal ou quando houver indício de nova chamada no portal MCTI). **Aplicar ao banco somente** se surgir item com chamada **ativa** (prazo futuro, inscrições abertas ou edital recente com sinal claro de abertura). |

A curadoria v3 cumpriu o papel de **filtro conservador**; o bloqueio ao apply é por **conteúdo latente no site**, não por falha técnica do crawler.

## Três níveis de curadoria (v3 — usar antes de apply)

| Nível | Artefato | Critério resumido |
|-------|----------|-------------------|
| **pronto_para_apply** | `standardized/mcti_fomento_standardized.json` | ≥2 sinais fortes + edital SEI ou PDF de edital principal (não ato de processo) |
| **review** | `review_candidates.json` | Comunicados, resultados, FAQ, edital antigo sem prazo, Lei TICs/PPI, retificação sem anexo |
| **institucional_latente** / **descartado_ruido** | `institucional_latente.json`, `descartados_ruido.json` | Menu gov.br, hubs de programa, PDF estudo/cartilha, fora allowlist |

### Sinais fortes (v3)

1. **texto_ou_url_forte** — edital, chamamento, chamada/seleção pública, portaria (em contexto de chamada), etc.
2. **pagina_ou_pdf_chamada** — `/editais/edital-*`, subpágina de chamamento (não hub), PDF com keyword de edital/chamamento
3. **prazo_ou_documento_oficial** — prazo extraído ou `link_edital` / PDF edital

**Pronto** exige **≥2 sinais** e **não** ser comunicado/resultado/parecer/relatório/despacho (vão para review).

**Lei das TICs / PPI:** sempre **review** (programa permanente, não chamada aberta).

## Pipeline (sem apply)

```text
python scripts/news_research/run_mcti_fomento_diagnostic.py
python scripts/radar/run_mcti_fomento_dryrun_v2.py    # allowlist/blocklist (exploração)
python scripts/radar/run_mcti_fomento_dryrun_v3.py    # conservador ← gate pré-apply
```

| Versão | Pasta | Uso |
|--------|-------|-----|
| v1 | `mcti_fomento_dryrun/` | Legado |
| v2 | `mcti_fomento_dryrun_v2/` | Filtro navegação; standardized amplo |
| v3 | `mcti_fomento_dryrun_v3/` | Gate pré-apply (referência); **apply não recomendado** na corrida atual |

## Comparação v2 → v3 (2026-05-17)

| Métrica | v2 | v3 |
|---------|---:|---:|
| Itens em `standardized` | 46 | **5** (só pronto) |
| Review | 39 | **35** |
| Prontos para apply | 8 | **5** |
| Institucional latente (registros) | — | 1173 |
| Descartados ruído | — | 687 |

Detalhe: `audit_reports_radar/mcti_fomento_dryrun_v3/comparacao_v2_v3.json`

### Os 5 prontos técnicos (última corrida — não aplicados)

Itens que passaram o gate v3, mas **não devem ir para apply** neste ciclo:

| Item | Observação |
|------|------------|
| Edital SEI nº 4/2021 | Histórico |
| Edital SEI nº 66/2024 | Publicado 2024; sem prazo extraído; validar manualmente se ainda relevante |
| PDF Edital Chamamento Oceano 31/2021 | Processo encerrado |
| Edital Chamamento Vacinas SEPEF 1/2021 e 2/2021 | COVID-19 / processos encerrados |

Edital 144/2020, portarias, comunicados e resultados → `review_candidates.json`.

*(Lista em `standardized/mcti_fomento_standardized.json` — uso: auditoria e diff em reexecuções futuras.)*

## Seeds

1. `fomento-1` (descoberta `#content-core`)
2. `/acesso-a-informacao/editais/`
3. Chamamento Oceano, Bolsa Científica, Chamamento Vacinas

## Código

- `scripts/radar/mcti_fomento_lib.py` — `evaluate_curation_v3`, `assign_nivel_v3`, `crawl_mcti_fomento_v3`
- `scripts/radar/run_mcti_fomento_dryrun_v3.py`

## Apply

**Status atual:** `não_recomendado` — não executar apply com o lote v3 existente.

Quando reexecutar o dry-run v3, considerar apply **apenas** se houver itens novos em `standardized/` com:

- prazo futuro extraído, ou
- menção explícita a inscrições abertas, ou
- edital SEI com data de publicação recente (janela a definir, ex. últimos 12 meses) **e** revisão humana.

Até lá: manter crawler/curadoria como infraestrutura; comparar `comparacao_v2_v3.json` entre corridas para detectar URLs novas.
