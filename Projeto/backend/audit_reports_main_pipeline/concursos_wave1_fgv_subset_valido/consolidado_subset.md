# FGV — subset válido (apply conservador em staging)

**Consolidado (UTC):** 2026-05-14T20:19:22Z  
**Critério:** `validacao_status = "valido"` no standardized FGV v2.

## Referência crawl FGV v2

| Métrica | Valor |
|--------|--------|
| URLs brutas (listagem) | 32 |
| Descartados | 29 |
| Standardized (original) | **3** |
| PDF attempts / download_ok / text_extracted | 3 / 3 / 3 |
| Loader dry-run v2 (original) | `errors_count` = **0**; `would_upsert_total` = 3 |
| Validação (original) | 1 `valido`, 2 `incompleto` |

**Artefacto original:** `audit_reports_main_pipeline/concursos_wave1_fgv/standardized/fgv_standardized.json`

## Subset válido

| Métrica | Valor |
|--------|--------|
| Total no subset | **1** |
| Ficheiro | `audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/standardized/fgv_standardized.json` |

### Item incluído

| Campo | Valor |
|--------|--------|
| **Título** | Concurso Público para a Prefeitura de Macaé |
| **data_inicio_inscricao** | 2026-03-30 |
| **data_fim_inscricao** | 2026-04-30 |
| **data_prova** | 2026-05-14 |
| **link_edital** | https://conhecimento.fgv.br/sites/default/files/concursos/minuta-edital-macae-saude-publicacao_0.pdf |
| **qualidade_dado** | alta |
| **validacao_status** | valido |

## Loader dry-run (subset)

| Campo | Valor |
|--------|--------|
| `total_items` | 1 |
| `would_upsert_total` | 1 |
| **`errors_count`** | **0** |

**Saída:** `audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/loader_dryrun/`

**Comando dry-run (reprodução):**

```bash
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/loader_dryrun --sources fgv
```

## Apply staging (não executado)

Conferir no site oficial FGV antes de qualquer escrita. Exige `EDITALFINDER_ENV=staging`, `EDITALFINDER_ALLOW_STAGING_APPLY=1` e flags `--apply-staging --staging`.

**PowerShell:**

```powershell
$env:EDITALFINDER_ENV="staging"; $env:EDITALFINDER_ALLOW_STAGING_APPLY="1"; python scripts/load_concursos_selecao.py --input-dir audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/loader_apply_staging --sources fgv --apply-staging --staging
```

**Bash:**

```bash
EDITALFINDER_ENV=staging EDITALFINDER_ALLOW_STAGING_APPLY=1 python scripts/load_concursos_selecao.py --input-dir audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fgv_subset_valido/loader_apply_staging --sources fgv --apply-staging --staging
```

**Nota:** este consolidado não executa apply; apenas documenta o comando para um apply conservador sobre o subset.
