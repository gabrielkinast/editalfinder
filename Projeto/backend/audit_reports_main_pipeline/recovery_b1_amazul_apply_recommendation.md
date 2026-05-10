# Recovery B.1 — recomendação de apply (AMAZUL)

## Recomendação

**Não executar apply neste passo** (conforme pedido). Após revisão humana do `recovery_b1_amazul_diagnostico` e do dry-run em `recovery_b1_amazul_loader_dryrun`, um **apply isolado `--sources amazul --staging`** pode alinhar staging aos novos campos (`reembolsavel`, `validacao_status`, setores truncados).

## Evidência do dry-run local

- 20 itens, **0** `mapping_errors`, **0** `critical_empty`, **0** documentos perdidos
- Destino **edital** para todos
- `amazul_standardized.json` sem `validacao_status=suspeito` na saída deste pipeline

## Próximo passo operacional

1. Curadoria rápida dos exemplos do diagnóstico (staging atual vs novo JSON).
2. Apply `--staging` apenas AMAZUL com readiness acordado pela equipa.
3. `validate_full_staging_after_daily.py --staging` e verificar queda em `credito_tipo_recurso_incoerente` e `suspeito_ativo_true` para AMAZUL.

Detalhe: `recovery_b1_amazul_apply_recommendation.json`.
