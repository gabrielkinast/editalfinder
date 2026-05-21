# Consolidado — Fundatec subset `validacao_status = valido`

**Filtro:** apenas registos com `link_edital` e `data_fim_inscricao` (regra v4 do crawler).  
**Apply:** não executado; Supabase sem escrita nesta etapa.

## Totais

| Métrica | Valor |
|--------|--------|
| Total original (standardized v4) | **7** |
| Total subset válido | **2** |
| Loader dry-run `total_items` | **2** |
| Loader `would_upsert_total` | **2** |
| Loader `errors_count` | **0** |

## Artefactos

| Ficheiro | Descrição |
|----------|-----------|
| `standardized/fundatec_standardized.json` | JSON filtrado (só `valido`) |
| `loader_dryrun/load_concursos_selecao_summary.json` | Resumo do dry-run |
| `consolidado_subset.json` | Este relatório em JSON |

## Títulos incluídos no subset

1. Prefeitura de Porto Alegre/RS abre inscrições para concursos públicos nas áreas de Farmácia e Medicina Veterinária - Fundatec  
2. Prefeitura de Morro Reuter/RS abre inscrições para Concurso Público - Fundatec  

## Campos principais (resumo)

| Campo | Porto Alegre | Morro Reuter |
|--------|----------------|--------------|
| `tipo_selecao` | concurso_publico | concurso_publico |
| `orgao` | Prefeitura de Porto Alegre | Prefeitura de Morro Reuter |
| `estado` / `municipio` | RS / Porto Alegre | RS / Morro Reuter |
| `nivel_escolaridade` | superior | medio |
| `numero_vagas` | null | null |
| `salario_min` / `salario_max` | 2755.73 / 2755.73 | 2092.6 / 5864.07 |
| `taxa_inscricao` | 211.44 | null |
| `qualidade_dado` | alta | alta |
| `status` | inscricoes_abertas | inscricoes_abertas |

## Datas

| Notícia | `data_publicacao` | `data_fim_inscricao` | `data_prova` |
|---------|-------------------|----------------------|--------------|
| Porto Alegre | 2026-04-17 | 2026-05-15 | 2026-07-05 |
| Morro Reuter | 2026-05-29 | 2026-05-29 | 2026-06-28 |

## Links de edital (portal Fundatec)

- **Porto Alegre:** `https://www.fundatec.org.br/portal/concursos/index_concursos.php?concurso=1090`  
- **Morro Reuter:** `https://www.fundatec.org.br/portal/concursos/index_concursos.php?concurso=1053`  

## Dry-run (reprodução)

```bash
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/loader_dryrun --sources fundatec
```

## Comando apply staging (referência — não executado)

Conferir no portal antes de aplicar.

**PowerShell:**

```powershell
$env:EDITALFINDER_ENV="staging"; $env:EDITALFINDER_ALLOW_STAGING_APPLY="1"; python scripts/load_concursos_selecao.py --input-dir audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/loader_apply_staging --sources fundatec --apply-staging --staging
```

**Bash:**

```bash
EDITALFINDER_ENV=staging EDITALFINDER_ALLOW_STAGING_APPLY=1 python scripts/load_concursos_selecao.py --input-dir audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/loader_apply_staging --sources fundatec --apply-staging --staging
```

Detalhe completo em `consolidado_subset.json` → `comando_apply_staging`.
