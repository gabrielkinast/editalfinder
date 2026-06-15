# BACKEND 10.2C — Controlled DOE_ARPAE Detail Recrawl + Deadline Apply

## Objetivo

Replicar o padrão do Grants.gov (10.2B) para **DOE_ARPAE**:

1. Recrawl/listagem eXCHANGE + enriquecimento de deadlines do texto disponível.
2. Dry-run before/after com candidatos a update.
3. Apply controlado somente com flags explícitas.
4. Auditoria pós-ingest documentada.

**Nenhum apply automático** neste patch.

## Por que DOE_ARPAE depois de Grants.gov

- Grants.gov já validou o fluxo (151 updates, 0 erros).
- DOE_ARPAE tem prazos em campos estruturados e linhas NOFO, mas muitos registros chegam sem `fim_inscricao`.
- O backfill (`deadline_backfill.py`) já implementa prioridade DOE — falta recrawl + apply controlado.

## Mapeamento atual

| Item | Local |
|------|-------|
| Crawler listagem | `doe_arpae/main_doe_arpae.py` → `collect_arpa_e_exchange_foas()` |
| Standardized JSON | `CORE/transformer/doe_arpae_standardized.json` |
| Backfill handler | `CORE/deadline_backfill.py` → `_backfill_doe_arpae()` |
| URLs | `arpa-e-foa.energy.gov/Default.aspx#FoaId...` |

Sem scraping agressivo de detalhe/PDF neste patch.

## Prioridade de deadline

1. `full_application_deadline`
2. `application_deadline`
3. `submission_deadline`
4. `response_deadline`
5. `concept_paper_deadline` (se único)
6. NOFO com duas datas → segunda data (full application)
7. Rejeita: posted/publication/issued/release date, TBD sem data concreta

## Feature flags

| Flag | Default | Efeito |
|------|---------|--------|
| `EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1` | OFF | Backfill em memória |
| `EDITALFINDER_ALLOW_CONTROLLED_APPLY=1` | OFF | Escrita no banco |

## Recrawl

```bash
cd backend
python scripts/recrawl_doe_arpae.py --limit 200 --output outputs/recrawl/doe_arpae/doe_arpae_recrawl.json
python scripts/recrawl_doe_arpae.py --limit 50 --no-network
```

## Dry-run before/after

```bash
python scripts/dry_run_doe_arpae_deadline_apply.py \
  --input outputs/recrawl/doe_arpae/doe_arpae_recrawl.json

python scripts/dry_run_doe_arpae_deadline_apply.py \
  --input outputs/recrawl/doe_arpae/doe_arpae_recrawl.json \
  --compare-db
```

Saídas: `outputs/doe_arpae_deadline_apply/`

## Apply controlado

**Bash:**

```bash
EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1 \
EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 \
python scripts/apply_doe_arpae_deadline_backfill.py \
  --input outputs/doe_arpae_deadline_apply/candidates_to_update.json
```

**PowerShell:**

```powershell
$env:EDITALFINDER_ENABLE_DEADLINE_BACKFILL="1"
$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
python scripts/apply_doe_arpae_deadline_backfill.py `
  --input outputs/doe_arpae_deadline_apply/candidates_to_update.json
Remove-Item Env:EDITALFINDER_ENABLE_DEADLINE_BACKFILL
Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
```

Proteções:

- Aborta sem flags.
- Somente DOE_ARPAE.
- Lote > 100 exige `--confirm-large`.
- Dry-run recente obrigatório.
- Não sobrescreve prazo válido.
- Log em `apply_log.json`.

## Critérios para apply

1. Recrawl + dry-run revisados.
2. `candidates_to_update.json` validado.
3. Flags ativas.
4. Staging com backup acordado.

## Auditoria pós-ingest

```bash
python scripts/audit_validity_backend.py --from-db --source doe_arpae --limit 1000
python scripts/audit_noise_backend.py --from-db --source doe_arpae --limit 1000
python scripts/dry_run_quality_enrichment.py --from-db --source doe_arpae --limit 1000 --with-deadline-backfill
```

## Limitações

- Sem fetch agressivo de detalhe eXCHANGE/PDF.
- Prazos dependem de texto na listagem ou fixture.
- `sem_prazo` não é ruído.
- Sem migration/schema/frontend.

## Próximo patch recomendado

**BACKEND 10.2D** — BNDES controlled recrawl (PDF/edital) ou OCR leve BNDES.

## Confirmação

- Nenhum apply automático neste patch.
- Nenhuma migration criada.
- Nenhuma alteração de schema Supabase.
