# Histórico de carga e de edital

Esta etapa adiciona rastreabilidade sem alterar dados existentes.

## Estruturas novas (via migration)

- `public.carga_execucao`: histórico de execuções de carga.
- `public.edital_historico`: histórico de mudanças por edital.

Migration criada:

- `migrations/20260501_create_carga_execucao_and_edital_historico.sql`

## Comportamento no loader controlado

`scripts/load_ready_sources.py` agora:

- gera histórico local sempre em `audit_reports_loader_ready/load_execution_history.jsonl`;
- tenta gravar em `public.carga_execucao` se a tabela existir;
- não quebra a execução se a gravação de histórico falhar.

## Histórico de mudanças de edital (preparação)

Helpers adicionados em `CORE/loader.py`:

- `detect_field_changes(old_record, new_payload)`
- `build_history_events(old_record, new_payload)`
- `save_history_events(id_edital, events, id_execucao=None)`

Nesta etapa eles foram preparados, sem ativar deduplicação nem merges reais.

## Leitura rápida de execuções

Script:

- `scripts/list_load_executions.py`

Exemplos:

- `python scripts/list_load_executions.py --staging`
- `python scripts/list_load_executions.py --limit 10`
