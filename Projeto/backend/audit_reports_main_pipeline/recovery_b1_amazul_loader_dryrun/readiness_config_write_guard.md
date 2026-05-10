# Readiness config — proteção contra escrita destrutiva

## Política

- O loader **lê** `readiness_for_loader.json` para calcular `allowed` / `blocked`, mas **não** sobrescreve `config/source_readiness.json` por defeito (dry-run e apply).
- O slice `pronto_para_loader` + `pronto_com_observacoes` é exportado apenas para **relatório derivado** (ver caminho em JSON).
- Com **`--write-readiness-config`**: merge **conservativo** (união + prioridade) e gravação explícita em `config/source_readiness.json`.

## Última execução (resumo)

- `readiness_config_write.written`: **False**
- `readiness_config_write.merge_mode`: `none`
- `readiness_config_write.path`: ``
- Relatório slice derivado: `D:\Computational_Physics\My Projects\edital\audit_reports_main_pipeline\recovery_b1_amazul_loader_dryrun\readiness_derived_slice.json`
