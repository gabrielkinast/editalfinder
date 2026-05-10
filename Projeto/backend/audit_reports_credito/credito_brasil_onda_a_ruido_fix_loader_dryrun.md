# Dry-run loader — Crédito Brasil Onda A (pós limpeza de ruído)

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources bnb,banco_da_amazonia,bdmg --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Fontes

`bnb`, `banco_da_amazonia`, `bdmg` (standardized canônicos copiados para `audit_reports_retransform/standardized/`).

## Resumo agregado (só estas três fontes)

| Métrica | Valor |
|--------|------:|
| Itens standardized | 68 |
| Would upsert | 68 |
| Would ignore | 0 |
| Erros de mapeamento | 0 |

## Por fonte

| Fonte | Itens | Would upsert | Mapping errors |
|-------|------:|-------------:|---------------:|
| banco_da_amazonia | 26 | 26 | 0 |
| bdmg | 18 | 18 | 0 |
| bnb | 24 | 24 | 0 |

## Artefatos gerados pelo loader

- `audit_reports_loader_ready/load_ready_summary.json`
- `audit_reports_loader_ready/load_ready_by_source.json`

## Próximo passo (fora do âmbito desta tarefa)

Reaplicar em staging **após** validação humana do relatório de links removidos; **não** executar `--apply` até essa revisão.

Versão estruturada: `credito_brasil_onda_a_ruido_fix_loader_dryrun.json`.
