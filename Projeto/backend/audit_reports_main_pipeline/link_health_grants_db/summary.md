# Link health — grants

- **Origem:** `supabase:edital`
- **Auditado em:** 2026-05-20T21:16:35Z
- **Itens:** 4
- **URLs testadas:** 12
- **Itens com link essencial quebrado:** 0

## Status HTTP

- `ok`: 12

## Recomendações

- `manter`: 12

## Próximos passos

1. Revisar `broken_links.json` e `review_candidates.json`.
2. Aplicar manualmente trechos de `docs/sql/FIX_GRANTS_BROKEN_LINKS.sql` (extras.link_health).
3. Re-rodar crawler grants se oppId estiver desatualizado.

**Não** apagar linhas de edital automaticamente.