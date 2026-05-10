# Dry-run — `--overwrite-fields setor_estrategico` (Recovery C)

Execução: `load_ready_sources.py` em modo dry-run com leitura à BD para comparar merge padrão vs substituição taxonómica.

## Verificações pedidas

| Critério | Resultado |
|----------|-----------|
| `sources_selected` | **2** (embrapii, nuclep) |
| `would_upsert_total` | **41** |
| `mapping_errors_total` | **0** |
| `overwritten_fields_count` | **38** (ver nota abaixo) |
| `taxonomy_overwrite_preview_errors_total` | **0** |

### Nota sobre 38 vs 41

`overwritten_fields_count` conta apenas linhas em que **já existe** registo na BD **e** o **conjunto** de valores de `setor_estrategico` após merge por união é **diferente** do conjunto após substituição pelo payload (comparação por multiconjunto ordenado). Três situações entre as 41 não incrementam o contador (por exemplo: link sem linha existente ainda, ou união já igual ao payload capped em termos de conjunto).

## Comando utilizado

```text
python scripts/load_ready_sources.py --dry-run --sources embrapii,nuclep --exclude-blocked \
  --input-dir audit_reports_main_pipeline/recovery_c_setores/standardized \
  --readiness audit_reports_retransform/readiness_for_loader.json \
  --overwrite-fields setor_estrategico \
  --output-dir audit_reports_main_pipeline/recovery_c_taxonomy_overwrite_dryrun
```

## Artefactos

- `load_ready_summary.md` / `load_ready_summary.json` — relatório completo do script.
- `recovery_c_taxonomy_overwrite_dryrun.json` — cópia do resumo JSON (alias).
- `recovery_c_taxonomy_overwrite_dryrun.md` — este ficheiro.

Nenhum `apply` foi executado; sem escritas Supabase a partir deste dry-run além de leituras (`fetch_edital_by_link`).
