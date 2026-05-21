# Link health — grants

- **Origem:** `supabase:edital`
- **Auditado em:** 2026-05-20T22:23:11Z
- **Itens:** 100
- **URLs testadas:** 308
- **Itens com link essencial quebrado:** 94

## Status HTTP

- `broken_spa_not_found`: 279
- `ok`: 15
- `broken_404`: 8
- `suspicious`: 6

## Recomendações

- `marcar_link_quebrado`: 279
- `manter`: 15
- `ocultar_botao_pdf`: 8
- `corrigir_url`: 6

## Próximos passos

1. Revisar `broken_links.json` e `review_candidates.json`.
2. Aplicar manualmente trechos de `docs/sql/FIX_GRANTS_BROKEN_LINKS.sql` (extras.link_health).
3. Re-rodar crawler grants se oppId estiver desatualizado.

**Não** apagar linhas de edital automaticamente.