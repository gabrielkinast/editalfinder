# BACKEND 10.2A — Loader Ingest Wiring for Deadline Backfill

Conecta `deadline_backfill` ao pipeline de ingest (`CORE/loader.py`) com feature flag e auditoria before/after.

**Sem apply. Sem migration. Sem alteração de schema Supabase.**

## Problema

O 10.1E provou heurísticas em dry-run, mas o banco ainda carece de `prazo_envio`/`extras.closeDate` porque o loader não aplicava backfill no upsert.

| Fonte | Gap |
|-------|-----|
| Grants.gov | `closeDate` na API, mas JSON legado sem `fim_inscricao` |
| BNDES | Notícias de lançamento; prazo em PDF/edital |
| DOE_ARPAE | Deadlines no texto NOFO, não em coluna |

## Diferença 10.1E vs 10.2A

| | 10.1E | 10.2A |
|---|-------|-------|
| Escopo | Dry-run / enricher | **Loader pré-upsert** |
| Persistência | Não | Payload pronto para upsert (flag ON) |
| Ponto de integração | `enrich_opportunity_record` | `upsert_routed_item`, `load_standardized_json` |

## Feature flag

```python
ENABLE_LOADER_DEADLINE_BACKFILL = False  # default seguro

# Ativar:
EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1
```

Função: `deadline_backfill_enabled()` / `apply_deadline_backfill_to_payload(payload, enabled=...)`

- **OFF** → payload inalterado (mesma referência)
- **ON** → `prazo_envio` + `fim_inscricao` + `extras_patch` quando confiável

## Integração loader

```python
# CORE/loader.py
item_normalizado = _apply_loader_deadline_backfill(item_normalizado)
```

Chamado em:
- `upsert_routed_item()` — antes de `map_to_db_schema`
- `load_standardized_json()` — após `normalizar()`

`map_to_db_schema` agora usa: `prazo_envio = fim_inscricao or prazo_envio`

## Campos gravados no payload (flag ON)

| Campo | Quando |
|-------|--------|
| `fim_inscricao` | Deadline confiável encontrado |
| `prazo_envio` | Espelho para loader/DB |
| `extras.grants_close_date` | Grants.gov closeDate |
| `extras.closeDate` / `close_date` | Preservação API |
| `extras.deadline_source_field` | Campo origem |
| `extras.sem_prazo_kind` | Sem prazo explicado |
| `extras.sem_prazo_reason` | Diagnóstico |
| `extras.loader_deadline_backfill` | Metadados wiring 10.2A |
| `extras.deadline_detail_url` | BNDES link edital/PDF |
| `extras.possible_deadline_document_url` | BNDES PDF detectado |

## Campos preservados em extras (nunca apagados)

- `postedDate` / `posted_date` — metadado, **não** prazo
- `archiveDate` / `archive_date` — metadado, **não** prazo sozinho
- `closeDateExplanation` — diagnóstico `deadline_explicitly_absent`
- Campos customizados existentes — merge, não wipe

## Fontes integradas

1. **Grants.gov** — crawler `simpler_grants_common` agora grava `closeDate`+`postedDate` em extras; transformer copia `close_date`→`fim_inscricao`
2. **DOE_ARPAE** — prioridade `full_application_deadline` > `concept_paper_deadline`; NOFO dupla data
3. **BNDES** — marcadores PT; PDF/detail URLs; `permanent_funding_line`
4. **Eureka** — deadline textual; hub → `portal_or_hub`
5. **ERC** — deadline textual; `continuous_program`
6. **AMAZUL** — preserva `prazo_envio` existente

## Dry-run wiring

```bash
python scripts/dry_run_loader_deadline_wiring.py --source grants_gov --limit 200
python scripts/dry_run_loader_deadline_wiring.py --source bndes --limit 200
python scripts/dry_run_loader_deadline_wiring.py --source doe_arpae --limit 200
```

Saídas: `outputs/loader_deadline_wiring/{fonte}/`

### Resultados (standardized JSON)

| Fonte | Registros | Alterados | new_deadline | explained |
|-------|-----------|-----------|--------------|-----------|
| grants_gov | 73 | 73 | 0* | 14 missing_from_loader |
| bndes | 19 | 19 | 0 | 16 pdf/detail |
| doe_arpae | 14 | 14 | **4** | 10 tbd/pdf |

\* JSON legado sem `closeDate` em extras — wiring pronto; ganho real após recrawl Simpler API.

### Exemplo before/after (DOE_ARPAE)

```json
{
  "before": { "fim_inscricao": null },
  "after": { "fim_inscricao": "2025-03-04", "prazo_envio": "2025-03-04" },
  "prazo_envio_after": "2025-03-04",
  "deadline_reason": "DOE NOFO data única"
}
```

### Exemplo Grants.gov (flag ON, closeDate sintético em teste)

```json
{
  "extras": { "closeDate": "2026-09-30" },
  "fim_inscricao": "2026-09-30",
  "extras.deadline_source_field": "closeDate"
}
```

## Auditorias (estáveis pós-10.2A)

| Métrica | Valor |
|---------|-------|
| `oportunidade_principal` | 65 |
| `oportunidade_sem_prazo` | 121 |
| `sem_prazo` | 120 |
| `is_noise` | 32 |

Ruído inalterado — `sem_prazo` continua não sendo ruído.

## Testes

```bash
python -m pytest tests/test_loader_deadline_wiring.py tests/test_deadline_backfill.py -q
# 104 passed (suite completa)
```

## Limitações

- Flag **desligada por default** — produção não muda até ativação explícita
- Grants.gov standardized JSON legado sem closeDate — recrawl necessário
- BNDES sem OCR/PDF neste patch
- DOE sem scraping agressivo eXCHANGE
- `replacement_candidate` não aplica automaticamente (só registra)

## Próximo patch

**BACKEND 10.2B — Controlled apply + recrawl Grants.gov:** recrawl Simpler API com flag ON, apply limitado a Grants.gov/BNDES/DOE, auditoria pós-ingest.

## Confirmação

- Nenhum apply executado neste patch
- Nenhuma migration
- Nenhuma coluna nova em `public.edital`
- Schema Supabase inalterado
