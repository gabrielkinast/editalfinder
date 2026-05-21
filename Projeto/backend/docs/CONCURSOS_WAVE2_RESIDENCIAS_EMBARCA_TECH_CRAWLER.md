# Wave 2 — Residências / Formação (EmbarcaTech — Softex)

## Diagnóstico da estrutura pública

| Aspeto | Observação |
|--------|------------|
| **Programa** | Residência tecnológica nacional em **sistemas embarcados / IoT**, coordenada pela **Softex**. |
| **Hub agregador** | [embarcatech.softex.br/inscricoes/](https://embarcatech.softex.br/inscricoes/) e [capacitacao-e-residencia](https://embarcatech.softex.br/capacitacao-e-residencia/) — links para IFs e parceiros. |
| **Detalhe por executora** | Páginas em domínios externos: IFRN (`ead.ifrn.edu.br`, `processoseletivo.ifrn.edu.br`), IFPI, IFCE, CEPEDI, Hardware BR. |
| **Editais** | PDF em portais IF (ex.: IFRN edital 24/2024) ou página `edital.html` (CEPEDI). |
| **Tipo** | **HTML** institucional + **PDF** opcional; sem API JSON pública. |
| **robots.txt** | Consultado em `embarcatech.softex.br`; URLs bloqueadas são ignoradas. |
| **BRISA / CAPES / MCTI** | Não usados neste piloto — ver [mapeamento](./CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md). |

## Escolha da fonte vs alternativas

| Fonte | Status no piloto Wave 2 |
|-------|-------------------------|
| **EmbarcaTech (Softex)** | **Implementada** (`fonte=embarcatech`) |
| BRISA (RESTIC) | Latente — portal de inscrição só login |
| CAPES / MCTI / CNPq | Latente — ruído e escopo amplo |
| Residências multiprofissionais saúde | Wave futura |

Decisão formal: [CONCURSOS_WAVE2_RESIDENCIAS_PILOT_DECISION.md](./CONCURSOS_WAVE2_RESIDENCIAS_PILOT_DECISION.md).

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_residencias_embarcatech.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_residencias_embarcatech/standardized/embarcatech_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_residencias_embarcatech_crawler.py` |

> O loader usa `--sources embarcatech` → ficheiro `{fonte}_standardized.json` = **`embarcatech_standardized.json`**.

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_residencias_embarcatech.py --max-items 10 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_residencias_embarcatech/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_residencias_embarcatech/loader_dryrun --sources embarcatech
python -m pytest tests/test_residencias_embarcatech_crawler.py -q
```

Opções: `--no-pdf` desativa download de PDF; `--listings` sobrescreve URLs do hub.

## Mapeamento de campos

| Campo | Valor / origem |
|--------|----------------|
| `fonte` | `embarcatech` |
| `fonte_tipo` | `governo` |
| `tipo_selecao` | `residencia` |
| `categoria` | `residencia_tecnologica` |
| `orgao` | `Softex — Programa EmbarcaTech` |
| `instituicao` | Inferida pelo host (IFRN, IFPI, IFCE, CEPEDI, Hardware BR) |
| `banca` | `Softex` |
| `area` | `TIC / Sistemas Embarcados` |
| `nivel_escolaridade` | `superior` |
| `curso` | Texto com «sistemas embarcados» / IoT |
| `link` | URL da página institucional do processo |
| `link_edital` | Primeiro PDF com «edital» no rótulo ou URL |
| Datas | Tabela HTML (`de DD/MM/AAAA a …`) + `fgv_schedule_from_text` em PDF |
| Bolsa | `parse_remuneracao_taxa_br` / regex «bolsa R$» (não inventar) |
| `extras.valor_tipo` | `bolsa` ou `auxilio` quando há `salario_min`/`max` |

## Regras

- `valido` = `link_edital` **e** `data_fim_inscricao`.
- `incompleto` se faltar `data_fim_inscricao` (mesmo com bolsa ou link da página).
- Não inventar vagas, datas ou bolsa.
- Descarte: `recency_should_discard` (inscrições encerradas antigas), páginas só marketing Softex, `robots_disallow`, resultado final sem edital/datas.
- PDF: até 6 MB, sem OCR (`concursos/fgv_edital_dates.py`).
- Sleep padrão **1,5 s** entre pedidos; User-Agent `EditalFinderConcursosBot/0.1`.

## Última corrida de referência (2026-05-16)

| Métrica | Valor |
|---------|------:|
| URLs candidatas (bruto) | **14** |
| Descartados | **10** |
| **Standardized** | **2** |
| `valido` | **0** |
| `incompleto` | **2** |
| Erros crawl | **2** (IFCE HTTP recusado; Hardware BR 404) |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **2** |
| pytest | **6** passed |

**Instituições mantidas:** CEPEDI (2 URLs — página institucional com bolsa R$ 3.100, sem PDF/datas no HTML).

**Descartes típicos:**

- IFRN edital 24/2024 — `data_fim_inscricao_passada_sem_prova_futura` (inscrições out/2024).
- IFPI inscrição — idem (ciclo encerrado).
- IFPI/IFCE/Hardware — sem datas nem indício recente no HTML.
- `processoseletivo.ifrn.edu.br` — `embarcatech_nao_oportunidade_ativa` (página genérica de processos).

### Campos preenchidos (2/2)

Título, tipo, categoria, órgão, instituição, banca, área, nível, bolsa, link, tags, `extras` de auditoria.

### Lacunas

`data_fim_inscricao`, `link_edital`, `estado`, `numero_vagas` — ciclo 2025/2026 ainda sem edital estruturado no hub; editais 2024 com datas completas são corretamente descartados por recência.

## Recomendação de apply em staging

**Não recomendado** neste momento: **0** registos `valido`. Manter fonte **implementada/latente** (padrão Coperve/UFRGS na Wave 2) até:

1. Novo ciclo com edital PDF e cronograma nas páginas IF ou hub Softex.
2. Re-crawl quando `data_fim_inscricao` for futura e `link_edital` estiver presente.

**Apply não executado** neste piloto.

## Relação com o módulo

- Filtro frontend residências/formação: `tipo_selecao` = `residencia` (e futuros `programa_ingresso` em outras fontes).
- Deduplicação global por `(fonte, link)` com `fonte=embarcatech`.
- Schema Supabase / `public.edital` / Radar: **não alterados** nesta wave.
