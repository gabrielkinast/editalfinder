# Backend 3 — Mapa de prazos por fonte problemática

Auditoria e correção na **origem** (crawler/parser), sem UPDATE em massa no banco.

---

## A) China International Tendering / MOFCOM

| Item | Detalhe |
|------|---------|
| **Crawler** | `china_mofcom_tendering/main_china_mofcom_tendering.py` |
| **Motor** | `asia_source_common.scrape_asia_html_portal` |
| **Saída** | `china_mofcom_tendering/outputs/china_mofcom_tendering_editais.json` |
| **Transformer** | `transform_generic` → `CORE/transformer/china_mofcom_tendering_standardized.json` |
| **Fonte no banco** | `fonte_recurso` ≈ "China International Tendering (MOFCOM)" |

### Campos extraídos hoje

- `data_publicacao`: `parse_loose_date(body)` (quando há data no texto)
- `fim_inscricao`: **null** na listagem (padrão Asia)
- `extras.detail_fetch_failed`: frequente (403/bloqueio)
- PDF opcional no detail; texto limitado

### Onde o prazo aparece na fonte

- Páginas de detalhe em inglês/chinês: *bid closing date*, *tender closing*, *submission deadline*, 投标截止
- Listagens muitas vezes só título + link (sem prazo)
- URLs `BidResult` = resultado, não oportunidade aberta

### Problema detectado

- Detail fetch falha → corpo vazio → 0 prazo estruturado
- Publicação confundida com encerramento se não filtrar labels

### Correção Backend 3

- `CORE/source_deadline_parsers.py` → `enrich_china_crawler_item` no fim do item em `asia_source_common` (country=china / MOFCOM)
- Flags: `extras.deadline_missing_in_source=true` quando só há publicação
- Campos: `prazo_envio_raw`, `extras.deadline`, `extras.deadline_source_field`, `extras.deadline_normalizer`

---

## B) Fundação Araucária (FAPPR)

| Item | Detalhe |
|------|---------|
| **Crawler** | `fappr/main_fappr.py` + `fappr/extrair_informacoes_fappr.py` |
| **Listagem** | Programas Abertos / Programas 2025–2026 |
| **Saída** | `fappr/outputs/fappr_editais.json` |
| **fonte_recurso** | "Fundação Araucária" (`programa`: fundacao_araucaria) |

### Campos extraídos hoje

- `fim_inscricao`: às vezes no HTML (`até DD/MM/YYYY`); muitas vezes só no **PDF** do edital
- `extras.anexos`: PDFs/docx
- Transformer enriquece PDF → `pdf_texto_extraido` (prazo pode aparecer depois do transform)

### Onde o prazo aparece

- HTML: inscrições até, prazo de submissão, data limite
- PDF: corpo da chamada (não OCR nesta fase)

### Problema detectado

- Listagem rasa; prazo só no PDF → BD sem `prazo_envio`
- Fallback index (`fappr.pr.gov.br/`) sem prazo

### Correção Backend 3

- `parse_araucaria_deadlines` + `enrich_araucaria_crawler_item` em `main_fappr._enrich_item`
- Flag `extras.deadline_requires_pdf=true` quando há PDF e sem data no HTML
- Regex ampliadas: período de inscrições, encerramento, data limite

---

## C) Grants.gov / Simpler Grants

| Item | Detalhe |
|------|---------|
| **Entrada** | `grants_gov/main_grants_gov.py` → `main_simpler_grants_gov.py` |
| **API** | `grants_gov/simpler_grants_common.py` (`collect_opportunities`) |
| **Saída** | `grants_gov/outputs/grants_gov_editais.json` |
| **fonte_recurso** | "Grants.gov" |

### Campos API

- `close_date` / `post_date` (Simpler)
- Legacy search2: `closeDate`, `openDate`, `oppStatus`
- **Prazo correto:** close / application due — **não** `postedDate` / `archiveDate`

### Problema detectado

- JSON legado com `fim_inscricao` em MM/DD/YYYY sem ISO na BD
- Registros sem `close_date` na API (forecasted) → sem prazo

### Correção Backend 3

- `parse_grants_api_deadlines` + `enrich_grants_crawler_item` em `build_pipeline_item`
- `prazo_envio_raw`, `extras.grants_close_date`, `extras.deadline_source_field`
- `deadline_missing_in_source` quando só posted

---

## Transformer / loader (preservação)

`CORE/transformer.py` copia para `enrich_patch` / extras:

- `prazo_envio_raw`, `fim_inscricao_raw`
- `deadline`, `deadline_source`, `deadline_source_field`, `grants_close_date`

Loader continua mapeando só `fim_inscricao` → `prazo_envio` (schema legado).

---

## Scripts Backend 3

| Script | Saída |
|--------|-------|
| `scripts/audit_deadline_by_source_backend.py` | `outputs/audit_deadline_by_source_backend/` |
| `scripts/probe_source_deadlines.py` | `outputs/source_deadline_probes/<source>/` |
| `scripts/dry_run_source_deadline_improvements.py` | `outputs/source_deadline_improvements/` |

---

## Backend 4 — recoleta dry-run

Script: `scripts/recrawl_sources_dry_run.py` + `scripts/compare_recrawl_with_db.py`  
Doc: `docs/backend/BACKEND_4_RECRAWL_DRY_RUN.md`  
Saída: `outputs/backend_4_recrawl_comparison/`

Descoberta esperada: ganho na China depende de detail HTML; Araucária depende de texto PDF no crawl; Grants depende de `close_date` na API.

## Próximos passos (Backend 5 sugerido)

1. Staging: transform + load após recoleta com `comparison_summary.md` aprovado.
2. Proxy/região para China se taxa de bloqueio permanecer alta.
3. Backfill `prazo_envio` a partir de `extras.deadline_normalizer` após migration.
4. OCR/PDF pipeline para Araucária (fase separada).
