# BACKEND 10.2B — Controlled Recrawl + Apply for Grants.gov Deadlines

## Objetivo

Completar o ganho real do `deadline_backfill` para **Grants.gov** após o wiring do 10.2A:

1. Recrawl da Simpler API preservando `closeDate` e metadados.
2. Dry-run before/after com candidatos a update.
3. Apply controlado **somente Grants.gov**, **somente com flags explícitas**.
4. Auditoria pós-ingest documentada.

**Nenhum apply automático** foi executado neste patch.

## Por que Grants.gov primeiro

- O JSON standardized legado não contém `closeDate` em `extras`.
- A Simpler API já expõe `close_date`, `post_date`, `archive_date`, `close_date_explanation`.
- O crawler (`simpler_grants_common.py`) já mapeia esses campos para `extras`.
- BNDES/DOE ficam para patch seguinte (PDF/recrawl dedicado).

## Feature flags (duas travas)

| Flag | Default | Efeito |
|------|---------|--------|
| `EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1` | OFF | Permite alterar payload em memória (loader + dry-run) |
| `EDITALFINDER_ALLOW_CONTROLLED_APPLY=1` | OFF | Permite escrita no banco via `apply_grants_deadline_backfill.py` |

Sem `ALLOW_CONTROLLED_APPLY`, todo fluxo permanece dry-run.

## Recrawl Grants.gov

```bash
cd backend
python scripts/recrawl_grants_gov.py --limit 500 --output outputs/recrawl/grants_gov/grants_gov_recrawl.json
```

Offline (fixture, sem rede):

```bash
python scripts/recrawl_grants_gov.py --limit 50 --no-network
```

Campos preservados em `extras`:

- `closeDate` / `close_date` / `grants_close_date`
- `postedDate` / `posted_date`
- `archiveDate` / `archive_date`
- `closeDateExplanation`
- `opportunity_id`, `agency`, `link`

Regras:

- `closeDate` válido → `fim_inscricao` no item do crawler.
- `postedDate` / `archiveDate` → apenas `extras`, **nunca** prazo.
- `closeDateExplanation` com "No closing date" → `sem_prazo_kind`, não prazo.

## Dry-run before/after

```bash
python scripts/dry_run_grants_deadline_apply.py \
  --input outputs/recrawl/grants_gov/grants_gov_recrawl.json

# Opcional: comparar com Supabase (somente leitura)
python scripts/dry_run_grants_deadline_apply.py \
  --input outputs/recrawl/grants_gov/grants_gov_recrawl.json \
  --compare-db
```

Saídas em `outputs/grants_deadline_apply/`:

| Arquivo | Conteúdo |
|---------|----------|
| `summary.md` | Totais e contagens |
| `before_after.json` | Comparação por link |
| `candidates_to_update.json` | Candidatos a apply |
| `rejected.json` | Fonte inválida / rejeitados |
| `no_deadline.json` | Sem prazo ou explicado |

## Apply controlado

**Somente após dry-run recente** (relatório `summary.md` &lt; 72h).

```bash
EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1 \
EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 \
python scripts/apply_grants_deadline_backfill.py \
  --input outputs/grants_deadline_apply/candidates_to_update.json
```

Proteções:

- Aborta sem flags.
- Aborta se candidatos vazios.
- Aborta se fonte ≠ Grants.gov.
- Aborta se lote &gt; 200 sem `--confirm-large`.
- Não deleta registros.
- Não sobrescreve `prazo_envio` válido por data diferente/ menos confiável.
- Preserva `extras` existentes (merge).
- Log em `outputs/grants_deadline_apply/apply_log.json`.

## Critérios para rodar apply

1. Recrawl concluído com `with_closeDate` &gt; 0.
2. Dry-run gerado; revisar `candidates_to_update.json`.
3. Staging com backup ou janela de manutenção acordada.
4. Ambas as flags ativas no ambiente.
5. Revisar `rejected.json` e `no_deadline.json` antes do apply.

## Como reverter

- Apply faz upsert por `link` — não apaga linhas.
- Para reverter prazo de um registro: restaurar `prazo_envio` anterior via SQL/Supabase UI usando backup ou `before` em `before_after.json`.
- `extras` mesclados: campos novos podem permanecer; remover manualmente se necessário.

## Auditoria pós-ingest

```bash
python scripts/audit_validity_backend.py --from-db --source grants_gov --limit 1000
python scripts/audit_noise_backend.py --from-db --source grants_gov --limit 1000
python scripts/dry_run_quality_enrichment.py --from-db --source grants_gov --limit 1000 --with-deadline-backfill
```

Métricas a comparar:

- Grants.gov com / sem `prazo_envio`
- `oportunidade_principal` / `oportunidade_sem_prazo`
- `validade_status` (aberto, vencendo, encerrado, sem_prazo)
- `is_noise`
- `closeDate` preservado em `extras`

## Limitações

- Apply limitado a Grants.gov; BNDES/DOE não incluídos.
- Sem migration / schema alterado.
- Recrawl depende de `SIMPLER_GRANTS_API_KEY` (ou fallback legacy search2).
- Itens sem keywords de defesa são descartados em `build_pipeline_item` (comportamento existente).
- `sem_prazo` não é tratado como ruído.

## Próximo patch recomendado

**BACKEND 10.2C** — BNDES controlled recrawl + deadline em PDF/edital, ou DOE eXCHANGE detail recrawl, reutilizando o mesmo padrão de flags e dry-run.

## Confirmação

- Nenhum apply automático neste patch.
- Nenhuma migration criada.
- Nenhuma alteração de schema Supabase.
- Frontend não alterado.
