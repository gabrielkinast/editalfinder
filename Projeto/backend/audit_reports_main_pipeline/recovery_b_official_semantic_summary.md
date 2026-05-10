# Recovery B — auditoria semântica oficial (dry-run isolado)

## Entrada

- Pasta: `audit_reports_main_pipeline/recovery_b_official_dryrun_standardized/`
- Relatório detalhado: `audit_reports_main_pipeline/recovery_b_official_semantic/`

## Resumo

- Fontes: **3**
- Itens: **32**

## Top problemas (script `audit_semantic_classification.py`)

- `publico_alvo_sem_evidencia`: 10
- `tipo_oportunidade_generico`: 3
- `fonte_defesa_sem_defesa`: 2

## Critérios Recovery B (verificação cruzada)

| Critério | Resultado |
|---|---|
| `setor_estrategico` com mais de 3 valores (por item, standardized) | **0** |
| `setor_estrategico_excessivo` no script (>5) | **0** |
| Título ruído (lista canónica) | **0** |
| Login isolado (heurística) | **0** |
| Institucional genérico (BADESUL `/home`) | **0** |
| `validacao_status=suspeito` (standardized) | **0** |
| `publico_alvo_sem_evidencia` | **10** (documentado: aceitável para dry-run; refinável) |

Detalhe JSON: `recovery_b_official_semantic_summary.json`.
