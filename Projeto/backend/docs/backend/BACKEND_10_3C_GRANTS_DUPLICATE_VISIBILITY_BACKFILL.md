# BACKEND 10.3C — GRANTS DUPLICATE VISIBILITY BACKFILL

## Problema

O **10.3B** ocultou 97 duplicatas Grants.gov via `extras.curadoria_front.hidden_duplicate`.
O formato final exige **ambos**:

| Campo | Valor |
|-------|-------|
| `hidden_duplicate` | `true` (boolean) |
| `visibility` | `"hidden_duplicate"` (string) |

Registros aplicados **antes** do ajuste final do patch podem ter só o boolean, sem `visibility`.
Sem `visibility`, `vw_editais_front` e `editalVisibility.js` podem **não** filtrar o registro.

## Diferença entre os campos

| Campo | Consumidor |
|-------|------------|
| `hidden_duplicate: true` | `post_apply_consolidation`, auditoria 10.3B |
| `visibility: "hidden_duplicate"` | `vw_editais_front` SQL, `isCuradoriaHidden()` no frontend |

O backfill 10.3C alinha os dois **sem alterar** `duplicate_of_id_edital`, `canonical_link` nem demais metadados.

## Por que é necessário

- Apply staging do 10.3B pode ter gravado só `hidden_duplicate` antes do campo `visibility` no `build_curadoria_patch`.
- E2E passou, mas duplicatas podem ainda aparecer na view até o backfill.
- Processo idempotente — seguro rodar após deploy do patch 10.3B atualizado.

## Arquivos

| Arquivo | Função |
|---------|--------|
| `CORE/grants_duplicate_visibility_backfill.py` | Classificação, dry-run, apply, auditoria |
| `scripts/dry_run_grants_duplicate_visibility_backfill.py` | Dry-run |
| `scripts/apply_grants_duplicate_visibility_backfill.py` | Apply controlado |
| `tests/test_grants_duplicate_visibility_backfill.py` | 11 testes |
| `scripts/audit_grants_duplicate_resolution.py` | Atualizado com checks 10.3C |

## Dry-run

```powershell
cd backend
python scripts/dry_run_grants_duplicate_visibility_backfill.py --from-db --limit 3000
```

Ou com IDs do apply 10.3B:

```powershell
python scripts/dry_run_grants_duplicate_visibility_backfill.py --input outputs/grants_duplicate_resolution/updated_records.json --from-db --limit 3000
```

Saídas em `outputs/grants_duplicate_visibility_backfill/`:

- `dry_run_summary.json`
- `candidates_to_update.json`
- `already_ok.json`
- `anomalies.json`
- `summary.md`

### Simulação offline (estado pré-backfill)

Com 97 registros simulados (só `hidden_duplicate`, sem `visibility`):

| Métrica | Valor |
|---------|-------|
| Analisados | 97 |
| Já OK | 0 |
| Candidatos | **97** |
| Precisam `visibility` | **97** |
| Anomalias | 0 |

## Apply controlado

```powershell
$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
$env:EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL="1"
python scripts/apply_grants_duplicate_visibility_backfill.py --confirm
Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
Remove-Item Env:EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL
```

Proteções:

- `--confirm` obrigatório
- duas env flags
- atualiza **somente** `extras`
- merge preserva `curadoria_front` existente
- não altera canônicos visíveis
- idempotente

Saídas: `apply_summary.json`, `updated_records.json`, `skipped_records.json`, `anomalies.json`.

## Post-audit

```powershell
python scripts/audit_grants_duplicate_resolution.py --from-db --limit 3000
```

Confirma:

1. `hidden_duplicate = true`
2. `visibility = "hidden_duplicate"`
3. `duplicate_of_id_edital` presente
4. `duplicate_reason` e `canonical_link` presentes
5. nenhum canônico referenciado está oculto
6. contagem total estável

## Rollback

Remover manualmente de `extras.curadoria_front` apenas os campos adicionados pelo backfill (`visibility`, `visibility_backfill_by`) — **sem DELETE**. Opcional: manter `hidden_duplicate` se ainda desejado ocultar via boolean.

## Limitações

- Não corrige anomalias sem `duplicate_of_id_edital` automaticamente.
- Não altera registros que não estão marcados como ocultos.
- Requer acesso Supabase para apply real (`--from-db`).

## Próximo patch

- **FRONTEND 10.3C** (opcional): `isCuradoriaHidden()` também checar `hidden_duplicate === true` como fallback.
- Re-rodar E2E após apply staging do backfill.

## Referências

- `BACKEND_10_3B_GRANTS_DUPLICATE_RESOLUTION.md`
- `frontend/.../src/utils/edital/editalVisibility.js`
