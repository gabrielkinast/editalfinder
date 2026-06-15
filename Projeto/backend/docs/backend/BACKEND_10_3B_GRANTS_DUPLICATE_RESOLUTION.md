# BACKEND 10.3B — GRANTS.GOV DUPLICATE OPPORTUNITY RESOLUTION

## Contexto

O patch **10.3A** canonicalizou os links Grants.gov para o padrão público atual:

```
https://www.grants.gov/search-results-detail/<opportunity_id>
```

Resultado do apply real do 10.3A:

| Métrica | Valor |
|---------|-------|
| Candidatos | 278 |
| Links corrigidos | 181 |
| Duplicatas (UNIQUE `link`) | **97** |
| Deleções | **0** |

## O achado das 97 duplicatas

A mesma oportunidade Grants.gov existe em mais de uma linha no banco. Tipicamente:

- o registro **canônico** já tem o link `search-results-detail/<id>`;
- o registro **duplicado** ainda usa link legado (`simpler.grants.gov/opportunity/<id>`).

Ao canonicalizar o duplicado, colidiria com o canônico (`23505` / `edital_link_key`). O 10.3A **pula** essas colisões e lista em `outputs/grants_link_fix/duplicate_targets.json`.

## Por que NÃO deletar / NÃO mesclar / NÃO migration

- Preservar histórico e rastreabilidade.
- Sem mudança de schema, RLS ou frontend neste patch.
- Decisão de merge físico fica para patch futuro.
- Necessidade imediata: **ocultar duplicatas na curadoria/frontend**.

## Critério do registro canônico

Para cada `opportunity_id` com mais de um registro, o canônico é escolhido por `pick_canonical_record()` (ordem de preferência):

1. Link já canônico `search-results-detail/<id>`;
2. Melhor `prazo_envio` / deadline;
3. Maior score/relevância (se presente);
4. Maior completude (título, descrição, objetivo, link);
5. `atualizado_em` mais recente;
6. Menor `id_edital` (desempate estável).

No fluxo principal, o 10.3A já atribui `duplicate_of_id_edital` em `duplicate_targets.json`; o 10.3B valida e aplica o ocultamento.

## Formato `extras.curadoria_front`

Marcamos **somente o duplicado**:

```json
{
  "curadoria_front": {
    "hidden_duplicate": true,
    "visibility": "hidden_duplicate",
    "duplicate_of_id_edital": 1126,
    "duplicate_reason": "same_grants_opportunity_id",
    "duplicate_source": "grants_link_fix_10.3a",
    "resolved_by": "backend_10.3b",
    "resolved_at": "2026-06-09T00:00:00Z",
    "canonical_link": "https://www.grants.gov/search-results-detail/362201"
  }
}
```

- `visibility: hidden_duplicate` alinha com `vw_editais_front` e `editalVisibility.js` (filtro por `visibility`).
- `hidden_duplicate: true` alinha com `post_apply_consolidation` e auditoria 10.3B.
- Merge preserva todo `extras` e campos existentes em `curadoria_front`.
- **Não** altera `link`, prazo, título nem o registro canônico.

## Arquivos

| Arquivo | Função |
|---------|--------|
| `CORE/grants_duplicate_resolution.py` | Agrupamento, canônico, merge, apply |
| `scripts/dry_run_grants_duplicate_resolution.py` | Dry-run (sem writes) |
| `scripts/apply_grants_duplicate_resolution.py` | Apply controlado |
| `scripts/audit_grants_duplicate_resolution.py` | Post-audit read-only |
| `tests/test_grants_duplicate_resolution.py` | Testes unitários |
| `docs/backend/BACKEND_10_3B_GRANTS_DUPLICATE_RESOLUTION.md` | Este documento |

Alterado: `CORE/post_apply_consolidation.py` — métrica `hidden_duplicates`.

## Dry-run

```powershell
cd backend
python scripts/dry_run_grants_duplicate_resolution.py --input outputs/grants_link_fix/duplicate_targets.json --from-db --limit 3000
```

Saídas em `outputs/grants_duplicate_resolution/`:

| Arquivo | Conteúdo |
|---------|----------|
| `dry_run_summary.json` | Totais e stats |
| `groups.json` | Grupos por `opportunity_id` |
| `candidates_to_hide.json` | Candidatos com `curadoria_patch` |
| `already_hidden.json` | Já marcados |
| `invalid_duplicates.json` | Rejeitados |
| `canonical_records.json` | Canônicos distintos |
| `summary.md` | Resumo legível |

**Resultado validado (staging):**

| Métrica | Valor |
|---------|-------|
| duplicate_targets | 97 |
| candidates_to_hide | 97 |
| already_hidden | 0 |
| invalid_duplicates | 0 |
| grupos (opportunity_id) | 97 |
| canônicos visíveis | 97 |

## Apply controlado

Proteções:

- `EDITALFINDER_ALLOW_CONTROLLED_APPLY=1`
- `EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION=1`
- `--confirm` obrigatório
- lote > 100 exige `--confirm-large`
- atualiza **somente** `extras` do duplicado
- idempotente

```powershell
$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
$env:EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION="1"
python scripts/apply_grants_duplicate_resolution.py --input outputs/grants_duplicate_resolution/candidates_to_hide.json --confirm
Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
Remove-Item Env:EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION
```

**Apply executado (staging):** `ok=97`, `errors=0`, `already_hidden=0`.

Saídas: `apply_summary.json`, `updated_records.json`, `skipped_records.json`, `apply_log.json`.

## Post-audit

```powershell
python scripts/audit_grants_duplicate_resolution.py --from-db --limit 3000
```

Confirma: 1 visível por grupo, duplicatas com `hidden_duplicate`, canônico não oculto, sem deleção.

## Reversão

Atualizar manualmente `extras.curadoria_front` do duplicado removendo `hidden_duplicate`, `visibility` e campos `duplicate_*` — **sem DELETE**. Opcional: script de rollback em patch futuro.

## Frontend

`editalVisibility.js` filtra `visibility === 'hidden_duplicate'`. Com `visibility` no patch, duplicatas somem da view sem alteração de frontend neste patch.

Modo admin “mostrar ocultos” → **FRONTEND 10.3C** (recomendado).

## Testes

```powershell
python -m pytest tests/test_grants_duplicate_resolution.py -q
```

## Limitações

- Sem merge físico; duplicado permanece no banco, apenas oculto.
- Validação rica requer `--from-db` no dry-run.
- Grupos gerados a partir de `duplicate_targets` (10.3A), não re-scan completo do DB por padrão.

## Próximo patch

- **BACKEND 10.3C** — backfill `visibility: "hidden_duplicate"` nos duplicados ocultos pelo apply inicial (ver `BACKEND_10_3C_GRANTS_DUPLICATE_VISIBILITY_BACKFILL.md`).
- **FRONTEND 10.3C:** toggle admin para duplicatas ocultas; fallback `hidden_duplicate === true` em `isCuradoriaHidden()`.
