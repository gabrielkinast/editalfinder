# Auditoria global — visibilidade Editais

- **Total analisado:** 1232
- **Visíveis:** 242
- **Revisão:** 504
- **Ocultos (candidatos):** 486
- **Regra:** `editais_visibility_v1`
- **Origem:** `supabase:edital source=all`

## Por visibility

- `review_missing_deadline`: 504
- `hidden_historical`: 198
- `visible_recent_strong_signal`: 190
- `hidden_institutional`: 109
- `hidden_duplicate`: 75
- `hidden_resultado`: 50
- `visible_current`: 48
- `hidden_expired`: 36
- `hidden_not_opportunity`: 18
- `visible_continuous_flow`: 4

## Hidden por motivo

- `hidden_historical`: 198
- `hidden_institutional`: 109
- `hidden_duplicate`: 75
- `hidden_resultado`: 50
- `hidden_expired`: 36
- `hidden_not_opportunity`: 18

## Fontes com maior ruído

- **China International Tendering (MOFCOM)**: 131/131 hidden (100.0%) — `precisa_melhoria_crawler`
- **EMBRAPII**: 21/21 hidden (100.0%) — `precisa_melhoria_crawler`
- **NUCLEP**: 20/20 hidden (100.0%) — `precisa_melhoria_crawler`
- **JETRO Government Procurement**: 11/11 hidden (100.0%) — `precisa_melhoria_crawler`
- **IARPA**: 8/8 hidden (100.0%) — `precisa_melhoria_crawler`
- **Ambev**: 7/7 hidden (100.0%) — `precisa_melhoria_crawler`
- **China Tendering & Bidding**: 6/6 hidden (100.0%) — `precisa_melhoria_crawler`
- **MCTI**: 3/3 hidden (100.0%) — `precisa_melhoria_crawler`
- **ANP**: 2/2 hidden (100.0%) — `precisa_melhoria_crawler`
- **China MOD (public)**: 2/2 hidden (100.0%) — `precisa_melhoria_crawler`
- **NATO DIANA**: 2/2 hidden (100.0%) — `precisa_melhoria_crawler`
- **Compras.gov Defesa**: 1/1 hidden (100.0%) — `precisa_melhoria_crawler`
- **IMPA**: 1/1 hidden (100.0%) — `precisa_melhoria_crawler`
- **MEXT**: 1/1 hidden (100.0%) — `precisa_melhoria_crawler`
- **DOE_ARPAE**: 13/14 hidden (92.9%) — `precisa_melhoria_crawler`

## Próximos passos

1. Revisar `hidden_candidates.json` e `review_candidates.json`.
2. Aplicar manualmente `sql_updates_sugeridos.sql` (extras.curadoria_front).
3. Aplicar `docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql` em staging.
4. Validar `SELECT fonte_recurso, COUNT(*) FROM public.vw_editais_front GROUP BY 1`.

**Não** apagar linhas de `public.edital`.