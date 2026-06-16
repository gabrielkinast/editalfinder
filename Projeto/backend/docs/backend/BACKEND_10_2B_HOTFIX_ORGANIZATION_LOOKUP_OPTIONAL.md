# BACKEND 10.2B-HOTFIX — Organization Lookup Optional in Loader

## Problema

Durante o apply controlado Grants.gov (10.2B), o loader consultava `public.organizacao` em cada `map_to_db_schema` via `get_default_org_id()`.

No staging atual, a tabela **não está exposta** no PostgREST:

```
PGRST205 — Could not find the table 'public.organizacao' in the schema cache
```

Isso podia bloquear upsert/apply mesmo quando o edital tinha `orgao_responsavel` textual suficiente.

## Causa

- `get_default_org_id()` chamava `supabase.table("organizacao")` repetidamente.
- Em falha, retornava fallback fixo `id_organizacao = 11` sem desativar lookup.
- Organização estruturada era tratada como parte obrigatória do fluxo.

## Decisão de produto

- **Organização estruturada é opcional.**
- **`id_organizacao` é opcional** — omitido do payload quando indisponível.
- **`orgao_responsavel` textual** é o fallback (`agency`, `fonte`, etc.).
- Ausência de `public.organizacao` → **warning uma vez** + continuar.

## Implementação (`CORE/loader.py`)

| Helper | Função |
|--------|--------|
| `is_missing_organization_table_error(exc)` | Detecta PGRST205 (code, message, schema cache) |
| `disable_organization_lookup_for_session()` | `_ORGANIZATION_LOOKUP_AVAILABLE = False` |
| `resolve_orgao_responsavel_text()` | Fallback textual |
| `get_default_org_id()` | Retorna `None` se tabela ausente; não reconsulta |

Estado de sessão:

- `None` — ainda não sondado
- `True` — lookup OK (pode retornar id ou `None` se tabela vazia)
- `False` — tabela ausente; pular lookup

Payload seguro (`_strip_payload`):

- Remove `id_organizacao` quando `None`
- Remove `organizacao`, `organizacao_responsavel`, `organization`, `org`

## Testes

```bash
cd backend
python -m pytest tests/test_loader_organization_optional.py \
  tests/test_grants_controlled_apply.py \
  tests/test_loader_deadline_wiring.py \
  tests/test_deadline_backfill.py \
  tests/test_validity_resolver.py \
  tests/test_noise_classifier.py -q
```

## Retestar apply Grants.gov

```bash
# Deve abortar por flag, NÃO por organização:
python scripts/apply_grants_deadline_backfill.py \
  --input outputs/grants_deadline_apply/candidates_to_update.json

# Apply real (somente quando desejado):
EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1 \
EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 \
python scripts/apply_grants_deadline_backfill.py \
  --input outputs/grants_deadline_apply/candidates_to_update.json
```

## Confirmação

- Nenhuma migration criada.
- Nenhum schema Supabase alterado.
- Nenhum apply automático neste hotfix.
- Frontend não alterado.
