# Onda C — resumo final de preparo (dry-run controlado)

- **Quando:** `2026-05-10T03:14:26.064817+00:00`
- **Duração (s):** 16.97

## Confirmações

- apply_executado: **False**
- supabase_staging_tocado: **False**
- schema_alterado: **False**
- opportunity_gate_global_alterado: **False**

## Erros / avisos do script

```json
{
  "errors": [],
  "warnings": []
}
```

## Artefatos

- `audit_reports_main_pipeline/pre_dryrun_state_snapshot.md`
- `audit_reports_main_pipeline/pre_dryrun_state_snapshot.json`
- `audit_reports_credito/onda_c_pre_dryrun_file_check.md`
- `audit_reports_credito/onda_c_pre_dryrun_file_check.json`
- `audit_reports_credito/onda_c_pre_dryrun_pycompile.md`
- `audit_reports_credito/onda_c_pre_dryrun_pycompile.json`
- `audit_reports_credito/onda_c_readiness_for_dryrun.json`
- `audit_reports_credito/onda_c_dryrun_standardized/`
- `audit_reports_credito/onda_c_dryrun_standardized_copy.md`
- `audit_reports_credito/onda_c_dryrun_standardized_copy.json`
- `audit_reports_credito/onda_c_loader_dryrun.md`
- `audit_reports_credito/onda_c_loader_dryrun.json`
- `audit_reports_credito/onda_c_dryrun_semantic/`
- `audit_reports_credito/onda_c_dryrun_semantic_summary.md`
- `audit_reports_credito/onda_c_dryrun_semantic_summary.json`
- `audit_reports_credito/onda_c_apply_readiness_recommendation.md`
- `audit_reports_credito/onda_c_apply_readiness_recommendation.json`

## Nota backup loader

Se existia load_ready_summary.json global, foi guardado em load_ready_summary.backup_pre_onda_c_dryrun.json durante a captura e restaurado após copiar para onda_c_loader_dryrun.json.

## Script reprodutível

- `scripts/onda_c_controlled_dryrun_prepare.py` — gera novamente os artefatos acima (sem apply).

## Nota Supabase

O `load_ready_sources.py` em dry-run pode inicializar o cliente Supabase (deteção de tabelas opcionais / organização), mas não foi usado `--apply` nem `--staging`; nenhum upsert foi solicitado.