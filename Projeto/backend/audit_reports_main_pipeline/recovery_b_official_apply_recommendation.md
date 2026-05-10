# Recovery B — recomendação oficial de apply

## Opção recomendada: **1 — Aplicar as três fontes em staging**

Após o dry-run isolado (`recovery_b_official_loader_dryrun_bundle` + `recovery_b_official_semantic`), os indicadores críticos estão dentro do esperado: **32** `would_upsert`, **0** erros de mapeamento, **0** itens críticos vazios, **0** documentos perdidos no payload, destino **`edital`** para todos, **0** `validacao_status=suspeito` no standardized e na amostra de payload, e **0** ocorrências de título ruído / login isolado / BADESUL `/home` nas verificações automáticas.

As flags semânticas restantes (`publico_alvo_sem_evidencia`, `tipo_oportunidade_generico`, `fonte_defesa_sem_defesa`) devem ser tratadas como **dívida de classificação**, não como bloqueio de carga, com melhorias em iterações seguintes.

## Não executado neste passo

- **Apply** não foi corrido (conforme pedido).
- Nenhuma alteração a `config/source_readiness.json` nem a `audit_reports_retransform/readiness_for_loader.json`.

## Próximo passo sugerido (operacional)

1. Confirmar deploy do código Recovery B no ambiente de staging.
2. Executar apply com `--staging` e política de readiness acordada pela equipa (o comando de exemplo está em `recovery_b_official_apply_recommendation.json`).
3. Validar com `validate_full_staging_after_daily.py`.

Detalhe: `recovery_b_official_apply_recommendation.json`.
