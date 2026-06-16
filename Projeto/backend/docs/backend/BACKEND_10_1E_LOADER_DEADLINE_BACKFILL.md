# BACKEND 10.1E — Loader Deadline Backfill + Sem-Prazo Semantics

Complemento ao 10.1D: backfill testável de prazo por fonte + semântica explícita para oportunidades sem deadline.

**Sem apply. Sem migration. Sem alteração em Supabase.**

## Problema

O 10.1D melhorou extração em dry-run, mas:

- Muitos registros no banco **não têm** `closeDate`/`prazo_envio` persistido (Grants.gov: 79/127 sem prazo explicado).
- BNDES traz textos de **lançamento**, não edital/PDF com deadline.
- DOE_ARPAE depende de detalhe eXCHANGE/PDF.
- `sem_prazo` era tratado implicitamente como “falta de qualidade”, quando na verdade é **condição de validade**, não ruído.

## Princípio central

> **`sem_prazo` é condição de validade, não condição de ruído.**

| Classificação | Significado |
|---------------|-------------|
| `oportunidade_principal` | Chamada com prazo útil detectado |
| `oportunidade_sem_prazo` | Oportunidade real **sem** deadline — permanece no radar |
| `portal_util` | Hub/linha permanente — deadline não exigido |
| `desconhecido` | Evidência insuficiente — não é ruído duro |
| `noticia` / `portal_generico` | Podem ser ruído no fluxo edital |

**Proibido:** rebaixar oportunidade real por falta de prazo; promover portal só por data; usar `data_publicacao` como prazo.

## Arquivos

| Arquivo | Papel |
|---------|-------|
| `CORE/deadline_backfill.py` | `extract_source_deadline_fields`, `apply_deadline_backfill_in_memory`, `resolve_sem_prazo_context` |
| `CORE/validity_resolver.py` | `sem_prazo_kind`, `sem_prazo_reason`, `deadline_backfill_status` |
| `CORE/opportunity_enricher.py` | `--with-deadline-backfill`, versão `backend_10.1e`, sem rebaixar por falta de prazo |
| `scripts/dry_run_deadline_backfill.py` | Auditoria de backfill |
| `scripts/dry_run_quality_enrichment.py` | Flag `--with-deadline-backfill` |
| `tests/test_deadline_backfill.py` | 21 testes regressivos |

## Semântica `sem_prazo_kind`

| Valor | Quando |
|-------|--------|
| `continuous_program` | ERC/Eureka programa contínuo |
| `permanent_funding_line` | BNDES linha permanente |
| `portal_or_hub` | Eureka hub, portal útil |
| `missing_from_loader` | Fonte deveria ter prazo mas loader não persistiu |
| `source_has_no_deadline` | Call sem data na origem |
| `deadline_in_pdf_or_detail` | BNDES/DOE — prazo provável em PDF/portal |
| `deadline_tbd` | NOFO/Grants forecast/TBD |
| `deadline_explicitly_absent` | `closeDateExplanation: No closing date` |
| `not_applicable` | Portal/notícia/resultado |
| `unknown` | Sem evidência classificável |

Campos expostos no enricher: `sem_prazo_kind`, `sem_prazo_reason`, `deadline_backfill_status`, `validade_reason`, `prazo_fonte`.

## Fontes e campos mapeados

### Grants.gov

| Campo origem | Uso |
|--------------|-----|
| `closeDate`, `close_date`, `opportunityCloseDate`, `applicationDeadline` | → candidato `prazo_envio` |
| `closeDateExplanation` | `deadline_explicitly_absent` |
| `postedDate`, `posted_date` | Metadado — **nunca** prazo |
| `archiveDate` | Metadado — **nunca** prazo sozinho |

Extras patch: `grants_close_date`, `grants_close_date_explanation`, `grants_posted_date`, `grants_archive_date`, `deadline_source_field`.

### DOE_ARPAE

| Campo | Prioridade |
|-------|------------|
| `full_application_deadline` | 1 |
| `application_deadline` | 2 |
| `submission_deadline` | 3 |
| `concept_paper_deadline` | 7 (aceito se único) |
| Linha NOFO (duas datas) | Segunda data |
| NOFO + TBD | `deadline_tbd` |

Sem detalhe: `deadline_in_pdf_or_detail` + flag `recrawl_candidate`.

### BNDES

Aceita texto com: `inscrições até`, `prazo final`, `data limite`, `propostas até`, etc.

Rejeita: `lançou, em`, `publicado em`, data isolada.

| Caso | `sem_prazo_kind` |
|------|------------------|
| Linha permanente | `permanent_funding_line` |
| Notícia + link PDF | `deadline_in_pdf_or_detail` |
| Chamada sem prazo no texto | `missing_from_loader` |

### Eureka / ERC / AMAZUL

- Eureka hub → `portal_or_hub`
- ERC programa → `continuous_program`
- AMAZUL: preserva `prazo_envio` existente

## Regras de backfill

- `preserved_existing` — `prazo_envio` válido não sobrescrito
- `new_deadline_found` — candidato novo (dry-run aplica em memória)
- `replacement_candidate` — `prazo_envio` inválido + novo confiável
- `no_deadline_explained` — sem prazo, mas com `sem_prazo_kind`
- `rejected_deadline` — data rejeitada (publicação etc.)
- `no_candidate` — `unknown`

## Métricas dry-run backfill (1232 registros)

| Métrica | Valor |
|---------|-------|
| Novos prazos candidatos | **12** |
| Prazos preservados | **116** |
| Prazos rejeitados | **0** |
| Sem prazo explicado | **143** |
| Sem prazo desconhecido | **961** |
| Candidatos recrawl/PDF | **35** |

### Por fonte (backfill)

| Fonte | preserved | new | explained |
|-------|-----------|-----|-----------|
| Grants.gov | 48 | 0 | 79 |
| BNDES | — | — | 32 |
| DOE_ARPAE | — | 4 | 10 |
| Eureka | — | 8 | 10 |
| AMAZUL | 14 | — | 6 |

> Grants.gov: 48 já têm `prazo_envio`; 79 sem `closeDate` no registro → `missing_from_loader` (backfill real exige recrawl API).

## Impacto enrichment (`--with-deadline-backfill`)

Comparado ao dry-run sem backfill (mesmo snapshot 1232):

| Métrica | Sem backfill | Com backfill |
|---------|--------------|--------------|
| `oportunidade_principal` | 66 | 66 |
| `oportunidade_sem_prazo` | 120 | 120 |
| `sem_prazo` (validade) | 120 | 120 |
| `is_noise` | 32 | 32 |
| `com_prazo_valido` (aberto+vencendo) | 20 | 20 |

Impacto limitado no snapshot atual: a maioria dos 12 candidatos novos são datas históricas (Eureka 2022) ou registros não-acionáveis. O ganho estrutural está na **semântica** e no pipeline pronto para loader.

## Exemplos

### Oportunidade real sem prazo preservada

- BNDES “Chamada Pública para Seleção de Fundos” → `oportunidade_sem_prazo`, `sem_prazo_kind=missing_from_loader`, `is_noise=false`
- ERC “Starting Grant” → `continuous_program`, permanece acionável ou hub conforme perfil

### Rejeições corretas

- BNDES “lançou, em 29.10.2025” → sem prazo, não inventa deadline
- Grants `postedDate` isolado → ignorado
- DOE NOFO `TBD` → `deadline_tbd`

### Novos candidatos (amostra)

- DOE `DE-FOA-0003551` → NOFO data única `2025-03-04`
- Eureka calls com `deadline` no texto (8 registros)

## Comandos

```bash
cd backend
python -m pytest tests/test_noise_classifier.py tests/test_validity_resolver.py tests/test_deadline_backfill.py -q
python scripts/dry_run_deadline_backfill.py --from-db --limit 5000
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000 --with-deadline-backfill
```

Saídas: `outputs/deadline_backfill/`, `outputs/backend_9_quality_dry_run_with_backfill/`.

## Limitações

- Backfill **não grava** em `public.edital` — apenas dry-run.
- Grants.gov: `extras` vazio no banco para muitos registros — loader precisa persistir `close_date` no ingest.
- BNDES: sem OCR/PDF neste patch.
- DOE: sem scraping agressivo do portal eXCHANGE.

## Próximo patch recomendado

**BACKEND 10.2 — Loader ingest wiring:** conectar `deadline_backfill` no pipeline Grants.gov/BNDES/DOE no momento do upsert (`prazo_envio` + extras), com feature flag e auditoria pós-ingest.

## Confirmação

- Nenhum apply executado
- Nenhuma migration
- Nenhuma alteração em Supabase/schema `public.edital`
