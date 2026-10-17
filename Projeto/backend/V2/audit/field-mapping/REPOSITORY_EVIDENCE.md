# Evidências consultadas

Esta lista registra arquivos efetivamente lidos ou pesquisados. Documentação/propostas foram comparadas com código e não tratadas automaticamente como verdade.

## Backend

- `backend/CORE/transformer.py` — fluxo, extrações, output, hash.
- `backend/CORE/data_cleaning.py` — aliases e limpeza.
- `backend/CORE/date_parser.py` — datas/prazos.
- `backend/CORE/deadline_normalizer.py` — segunda família de prazo.
- `backend/CORE/finance_parser.py` — valores.
- `backend/CORE/taxonomy_filtros.py` — área/tipos/calibradores/espelhos.
- `backend/CORE/opportunity_enricher.py` — enrichment opcional.
- `backend/CORE/validity_resolver.py` — validade.
- `backend/CORE/schema.py` — modelo-base pré-loader.
- `backend/CORE/loader.py` — persistência/upsert/expiração.
- `backend/CORE/merge_utils.py` — merge/sanitização.
- `backend/CORE/db.py` — seleção de ambiente (sem abrir secrets).

## SQL

- `backend/database/schema_current.sql` — snapshot principal de 2026-06-03.
- `backend/CORE/schema_sql_completo.sql` — versão divergente.
- `frontend/EditalFinder-React/schema_sql_completo.sql` — versão legada divergente.
- `backend/migrations/20260430_add_edital_filter_columns.sql`.
- `backend/migrations/20260504_align_supabase_backend_contract.sql`.
- `backend/migrations/20260504_recreate_front_views_staging.sql`.
- `backend/migrations/20260505_add_missing_edital_columns_from_loader_payload.sql`.
- `backend/migrations/20260505_recreate_edital_views_credito_staging.sql`.
- `backend/migrations/20260610_security_1_0b_edital_admin_write_policy.sql`.
- `backend/docs/sql/schema_consolidado_editalfinder.sql`.
- `backend/docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql`.
- `backend/docs/sql/HOTFIX_VW_EDITAIS_FRONT_RELAX_VISIBILITY.sql`.
- `backend/docs/sql/PROPOSAL_VW_EDITAIS_FRONT_BACKEND_1.sql`.
- `backend/docs/sql/PROPOSAL_VW_EDITAIS_FRONT_BACKEND_6.sql`.
- `backend/docs/sql/PROPOSAL_VW_EDITAIS_FRONT_WITH_SHADOW.sql`.
- `backend/docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql`.
- `backend/docs/sql/FIX_EDITAL_FAVORITO_RLS.sql`.

## Frontend

- `frontend/EditalFinder-React/src/config/env.js` e `.env.example` — nomes das views.
- `src/services/dataService.js` e `editaisService.js` — consulta/fallback.
- `src/services/favoritosService.js` e `src/hooks/useEditalFavorites.js`.
- `src/utils/edital/editalRowMapper.js`.
- `src/utils/edital/filtersEngine.js`.
- `src/utils/edital/search.js`, `noise.js`, `dates.js`, `editalFieldHelpers.js`, `editalStatusBadges.js`, `editalVisibility.js`.
- `src/utils/editais/editaisQueryFilters.js`, `editalDeadlineStatus.js`.
- `src/utils/dashboard/dashboardClassification.js` e utilitários de deadline.
- `src/components/dashboard/EditalCard.jsx`, `EditaisFiltersSidebar.jsx`.
- `src/pages/EditaisPage.jsx`, `EditalDetalhes.jsx`, `RadarFomento.jsx`.
- `src/types/edital.js`.
- `src/utils/debugRuntimeDataSource.js`, `debugDataCounts.js`.

## Testes

- `frontend/EditalFinder-React/src/utils/edital/editalDetailLookup.test.js`.
- `frontend/EditalFinder-React/src/utils/edital/editalStatusBadges.test.js`.
- `frontend/EditalFinder-React/src/utils/radarMatch.test.js`.
- `frontend/EditalFinder-React/src/utils/debugRuntimeDataSource.test.js`.
- `frontend/EditalFinder-React/tests/e2e/editais-filters.spec.js`.
- `frontend/EditalFinder-React/tests/e2e/editais-status-filter.spec.js`.
- `frontend/EditalFinder-React/tests/e2e/editais-detail.spec.js`.
- `frontend/EditalFinder-React/tests/e2e/editais-export.spec.js`.
- `frontend/EditalFinder-React/tests/e2e/grants-links.spec.js`.

## Documentação

- `docs/PROJECT_TECHNICAL_MAP.md`.
- `frontend/docs/FRONTEND_1_1B_ADMIN_FORM_ORGAO_RESPONSAVEL.md`.
- `frontend/EditalFinder-React/docs/FRONTEND_1_2A_VALIDITY_STATUS_BADGES.md`.
- `frontend/EditalFinder-React/docs/FRONTEND_1_2B_STATUS_FILTERS_EXPORT.md`.
- `frontend/EditalFinder-React/docs/BUG_DATA_COUNT_DIVERGENCE_WEB_VS_TAURI.md`.
- `frontend/EditalFinder-React/docs/SECURITY_1_0A_RLS_AUTH_ADMIN_AUDIT.md`.

## Amostras JSON

- Amostra empacotada: `backend/ambev/outputs/ambev_editais.json:88-102` e `backend/CORE/transformer/ambev_standardized.json:408-493`, ligada por URL exata.
- Estudos auxiliares lidos: `backend/fapesp/outputs/fapesp_editais.json`, `backend/CORE/transformer/fapesp_standardized.json`, `backend/fapergs/outputs/fapergs_editais.json`, `backend/CORE/transformer/fapergs_standardized.json`, `backend/japan_jsps/outputs/japan_jsps_editais.json`, `backend/CORE/transformer/japan_jsps_standardized.json`, `backend/abdi/outputs/abdi_editais.json`, `backend/CORE/transformer/abdi_standardized.json`.

## Comandos de leitura

Foram usados apenas comandos locais read-only para evidência: `pwd`, `find`, `rg --files`, `rg -n`, `sed -n`, `nl -ba`, `head`, `tail`, `wc`, `test`, `git status --short`, `git diff --stat`, `git diff -- <paths>` e pequenos scripts `python3` que somente abriram/parsearam JSON e imprimiram seleções. `mkdir -p audit/field-mapping` criou apenas a pasta autorizada. Não houve rede, crawler, instalação ou Supabase.
