# Wave 2 — FCC (Fundação Carlos Chagas)

Crawler piloto da banca **FCC** (`concursosfcc.com.br`) para `public.concurso_selecao`.

## Diagnóstico da estrutura pública

| Aspeto | Observação |
|--------|------------|
| **Listagem** | [concursoInscricaoAberta.html](https://www.concursosfcc.com.br/concursoInscricaoAberta.html) — `div.box5` com `.textoInstituicao2` e `.textoConcurso2` |
| **Detalhe** | `/concursos/{codigo}/index.html` (ex.: [sface125](https://www.concursosfcc.com.br/concursos/sface125/index.html)) |
| **Dados HTML** | Inscrições (`div.box3`), vencimento base, cargos, situação `#opcaoConcursos`, links/PDF em `div.campoLinkArquivo` |
| **PDF** | Via viewer Rybená (`?file=` URL do PDF); extração de texto **não** usada por defeito (`robots` bloqueia `*.pdf`) |
| **robots.txt** | `Disallow: /concursos/` e `Disallow: /*.pdf$` — listagem na raiz é permitida |

### robots.txt e modo de operação

| Modo | Comportamento |
|------|----------------|
| **Padrão** | Só listagem → registos `incompleto` (sem datas/edital) |
| **`--allow-detail-despite-robots`** | GET nas páginas de detalhe linkadas oficialmente na listagem; sleep ≥ 2 s |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_fcc_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_fcc/standardized/fcc_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_fcc_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_fcc_concursos.py --max-items 10 --sleep 2.0 --allow-detail-despite-robots
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_fcc/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_fcc/loader_dryrun --sources fcc
python -m pytest tests/test_fcc_crawler.py -q
```

## Mapeamento de campos

| Campo | Origem |
|--------|--------|
| `fonte` | `fcc` |
| `fonte_tipo` | `banca` |
| `banca` | `FCC` |
| `categoria` | `banca_fcc_concurso` |
| `tipo_selecao` | `infer_tipo_selecao_meta` (concurso vs certificação PLANEJAR, etc.) |
| `titulo` | `{instituição} — {cargo}` |
| `link` | URL detalhe `/concursos/{codigo}/index.html` |
| `link_edital` | PDF «Abertura de Inscrições» (URL direta via `file=`) |
| `data_*_inscricao` | Bloco «Período de inscrição para todos os candidatos» |
| `salario_min/max` | «Vencimento Base Inicial» |
| `taxa_inscricao` | «Valor da Inscrição» no box3 |
| `validacao_status` | `valido` iff `link_edital` + `data_fim_inscricao` |

## Regras

- Não inventar vagas, datas, salário ou taxa.
- Descartar processos encerrados (`recency_should_discard`, situação encerrada).
- Apply **não** executado nesta wave.

## Última corrida de referência (2026-05-17)

| Métrica | Valor |
|---------|------:|
| Listagem (candidatos) | **4** |
| Standardized | **4** |
| `valido` | **2** (SEFAZ CE, Câmara Presidente Prudente) |
| `incompleto` | **2** (exames PLANEJAR — edital sem `data_fim_inscricao` no HTML) |
| Loader dry-run | `errors_count` **0**, `would_upsert` **4** |
| pytest | **5** passed |
