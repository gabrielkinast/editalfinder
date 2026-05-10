# Lote Crédito/Desenvolvimento — Onda A Brasil (Consolidado)

Data de consolidação: 2026-05-05

## Escopo

Fontes consideradas:
- `bnb`
- `banco_da_amazonia`
- `bdmg`
- `desenvolve_sp`
- `agerio`

## Diagnóstico

Com base em `audit_reports_credito/lote_credito_brasil_onda_a_diagnostico.json`:
- Brutos: **85**
- Transformados: **83**
- Rejeitados: **2**
- Readiness recomendado por fonte:
  - `bnb`: `ready_with_notes`
  - `banco_da_amazonia`: `ready_with_notes`
  - `bdmg`: `ready_with_notes`
  - `desenvolve_sp`: `needs_manual_review` (WAF/403)
  - `agerio`: `needs_manual_review` (baixo volume útil)

## Semantic Fix

Com base em `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix.json` e `.../semantic_fix_audit/audit_semantic_summary.json`:
- Auditoria semântica antes: 83 itens; flags: `setor_estrategico_excessivo=6`, `classificacao_muito_ampla=3`, `area_cientifica_sem_evidencia=1`.
- Auditoria semântica depois: 83 itens; **flags_totais vazio**.
- Ajustes aplicados: calibração local em `CORE/taxonomy_filtros.py` para crédito BR (`bnb`, `banco_da_amazonia`, `desenvolve_sp`, `bdmg`, `agerio`), sem alterar `opportunity_gate.py` global.

## Readiness

Com base em `audit_reports_credito/credito_brasil_onda_a_ready_with_notes_loader_dryrun.json`:
- Fontes promovidas para carga (`ready_with_notes`): **`bnb`, `banco_da_amazonia`, `bdmg`**.
- Fontes mantidas em revisão: **`desenvolve_sp`, `agerio`**.

## Dry-run do loader

Relatório canônico: `audit_reports_loader_ready/final_dry_run_before_staging.json`.

Métricas principais (3 fontes promovidas):
- `sources_selected`: **3**
- `itens_standardized_total`: **77**
- `would_upsert_total`: **77**
- `would_ignore_total`: **0**
- `mapping_errors_total`: **0**
- `critical_empty_items_total`: **0**
- `documentos_perdidos_no_payload_total`: **0**
- `validacao_status_preserved_items_total`: **77**
- `qualidade_dado_preserved_items_total`: **77**

## Migration de schema baseada no payload real

Contexto: no staging, houve falha por colunas ausentes em `public.edital` (ex.: `contrapartida`, `descricao_original`).

Entregas de schema:
- `migrations/20260505_add_missing_edital_columns_from_loader_payload.sql`
- `migrations/20260505_recreate_edital_views_credito_staging.sql`
- `docs/sql/check_edital_payload_columns.sql`
- `audit_reports_credito/credito_brasil_onda_a_schema_gap.{md,json}`

Resultado do gap (payload real do loader x migration):
- Chaves no payload (após strip): **64**
- Colunas na migration: **104**
- Payload sem cobertura na migration: **0**

## Apply em staging (realizado)

Com base em `audit_reports_loader_ready/load_ready_summary.json`:
- `apply_status`: `applied_to_staging`
- `environment_guard.block_reason`: vazio
- `apply_processed_total`: **77**
- `apply_inserted_total`: **77**
- `apply_updated_total`: **0**
- `apply_errors_total`: **0**

## Validações pós-carga

Com base em `audit_reports_loader_ready/post_staging_validation.json`:
- `executed`: **true**
- `apply_status`: `applied_to_staging`
- `records_processed`: **77**
- `records_inserted_or_updated`: **77**
- `blocked_sources_loaded`: **0**
- `critical_empty_check`: **0**
- Preservação documental:
  - `docs_input_items_total`: **21**
  - `docs_preserved_items_total`: **21**
  - `pdf_preserved_items_total`: **21**
- Pendente: `duplicates_check = pending_manual_sql_validation`.

## Fontes promovidas

- `bnb`
- `banco_da_amazonia`
- `bdmg`

## Fontes mantidas em revisão

- `desenvolve_sp` — bloqueio WAF/403 na coleta automática; depende de revisão/manual seed.
- `agerio` — volume útil baixo para promoção automática nesta onda.

## Conclusão

O Lote Crédito/Desenvolvimento — Onda A Brasil foi consolidado com correção semântica, readiness, dry-run, ajuste de schema e apply em staging concluído para as três fontes promovidas (`bnb`, `banco_da_amazonia`, `bdmg`), mantendo `desenvolve_sp` e `agerio` em revisão controlada.
