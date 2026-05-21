# Wave 2 — Vestibulares / Ingresso (UFRGS — CV / COPERSE)

## Diagnóstico da estrutura pública

| Aspeto | Observação |
|--------|------------|
| **CV legado** | `www.ufrgs.br/cv/` — inacessível ou instável em clientes HTTP simples (testes 2026). |
| **Hub atual** | [vestibular.ufrgs.br](https://vestibular.ufrgs.br/) — WordPress, título «COPERSE». |
| **Conteúdo oficial** | [www.ufrgs.br/coperse/](https://www.ufrgs.br/coperse/) — vestibular, PSU, processos seletivos específicos. |
| **Ingresso geral** | [www.ufrgs.br/ingresso/](https://www.ufrgs.br/ingresso/) — FAQs + links para editais PDF. |
| **Editais / manuais** | PDF em `coperse/wp-content/uploads/...` (ex.: `EDITAL-CV-2026.pdf`, `Manual-do-Candidato`). |
| **Inscrição online** | `www1.ufrgs.br/vestibular/inscricao/{ano}` (portal; não usado como `link` principal). |
| **Paths legados** | `www.ufrgs.br/vestibular/cv20xx/` — **403** frequente; crawler usa só COPERSE. |
| **Tipo** | **HTML** WordPress + **PDF**; sem API JSON pública identificada. |
| **robots.txt** | `www.ufrgs.br` — regras para bots nomeados; fetch com User-Agent identificado. |

## Escolha da fonte vs alternativas

| Fonte | Status no piloto Wave 2 |
|-------|-------------------------|
| Vunesp | Bloqueada (403 / DNS) |
| Comvest | `Disallow: /` |
| UFSC Coperve | Implementada (wave2 anterior) |
| **UFRGS CV/COPERSE** | **Implementada neste piloto** |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_vestibulares_ufrgs.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/standardized/ufrgs_cv_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_vestibulares_ufrgs_crawler.py` |

> O loader usa `--sources ufrgs_cv` → ficheiro `{fonte}_standardized.json` = **`ufrgs_cv_standardized.json`**.

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_vestibulares_ufrgs.py --max-items 12 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/loader_dryrun --sources ufrgs_cv
python -m pytest tests/test_vestibulares_ufrgs_crawler.py -q
```

Opções: `--no-pdf` desativa download de PDF para enriquecer datas.

## Mapeamento de campos

| Campo | Valor / origem |
|--------|----------------|
| `fonte` | `ufrgs_cv` |
| `fonte_tipo` | `universidade` |
| `orgao` | `UFRGS` |
| `instituicao` | `Universidade Federal do Rio Grande do Sul` |
| `banca` | `CV/UFRGS — COPERSE` |
| `estado` / `municipio` | `RS` / `Porto Alegre` |
| `nivel_escolaridade` | `ensino_medio` |
| `tipo_selecao` | `vestibular` ou `programa_ingresso` |
| `link` | URL oficial COPERSE do processo |
| `link_edital` | PDF «Edital» / «Manual do Candidato» quando presente |
| Datas | HTML (`de 08 a 29 de setembro de 2025`, etc.) + `fgv_schedule_from_text` em PDF |

## Regras

- `valido` = `link_edital` + `data_fim_inscricao`.
- Descarte: recência, edições anteriores, aquisição de provas, inscrições encerradas sem período futuro.
- PDF: até 6 MB, sem OCR (`fgv_edital_dates`).

## Última corrida de referência (2026-05-16)

| Métrica | Valor |
|---------|------:|
| URLs candidatas (bruto) | **17** |
| Descartados | **10** |
| **Standardized** | **7** |
| `valido` | **0** |
| `incompleto` | **7** |
| Erros crawl | **0** |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **7** |

**Tipos:** 3 `vestibular`, 4 `programa_ingresso`.

**Descartes típicos:** CLN 2026/1 (fim inscrição set/2025), PSU/PSE encerrados, CV 2024 sem datas recentes.

### Campos preenchidos (7/7)

Título, tipo, órgão, instituição, banca, UF, município, nível, link, tags.

### Lacunas

`data_fim_inscricao`, `data_prova`, `taxa_inscricao`, `numero_vagas`, `curso` — Vestibular 2027 ainda sem edital/cronograma estruturado no HTML; processos ativos com datas foram filtrados por recência.

## Recomendação de apply em staging

**Não recomendado** neste momento: 0 registos `valido`. Manter fonte **implementada/latente** (como Coperve na Wave 2) até:

1. Publicação do edital Vestibular 2027 com cronograma no HTML ou PDF parseável.
2. Re-crawl quando houver processo com inscrições abertas (`data_fim_inscricao` futura + PDF).

**Apply não executado** neste piloto.

## Relação com o módulo

- Aba **Vestibulares** no frontend: `tipo_selecao` ∈ `vestibular`, `programa_ingresso`.
- Deduplicação global por `(fonte, link)` com `fonte=ufrgs_cv`.
