# Lote 4 — dry-run combinado do loader (fontes prontas)

**Data:** 2026-05-03  
**Fontes:** `apex`, `faperg`, `amazul`, `ambev`  
**Modo:** `--dry-run` apenas (sem `--apply`).

## Comando executado

```text
python scripts/load_ready_sources.py --dry-run --sources apex,faperg,amazul,ambev --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

**Saída do script:** `audit_reports_loader_ready/` (`load_ready_summary.json`, `load_ready_by_source.json`, …).  
**ID de execução (run atual):** `994cf6ee-67f8-4874-a1a1-c124e6105028`.

---

## Totais agregados

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 4 |
| Itens standardized (total) | **31** |
| `would_upsert_total` | **31** |
| `would_ignore_total` | 0 |
| `mapping_errors_total` | **0** |
| `critical_empty_items_total` | **0** |
| `docs_input_items_total` | 20 |
| `docs_preserved_items_total` | **20** |
| `documentos_perdidos_no_payload_total` | **0** |
| `pdf_input_items_total` | 20 |
| `pdf_preserved_items_total` | **20** |
| `validacao_status_preserved_items_total` | **31** |
| `qualidade_dado_preserved_items_total` | **31** |
| Docs não-PDF (std / payload) | 2 / 2 |
| `perda_documentos_nao_pdf_total` | **0** |

---

## Por fonte (`load_ready_by_source.json`)

| Fonte | Itens | would_upsert | mapping_errors | critical_empty | docs_preserv. | pdf_preserv. |
|-------|------:|-------------:|-----------------:|---------------:|--------------:|-------------:|
| amazul | 19 | 19 | 0 | 0 | 19 | 19 |
| ambev | 7 | 7 | 0 | 0 | 0 | 0 |
| apex | 3 | 3 | 0 | 0 | 0 | 0 |
| faperg | 2 | 2 | 0 | 0 | 1 | 1 |

---

## Verificações pedidas (tarefa 7)

| Verificação | Resultado |
|---------------|------------|
| Total standardized | **31** (= 19+7+3+2) |
| `would_upsert` | **31** |
| `mapping_errors` | **0** |
| `critical_empty` | **0** |
| Documentos preservados | **20** preservados; **0** perdidos no payload |
| `pdf_url` preservado | **20** itens com PDF na entrada preservados no agregado (19 Amazul + 1 FAPERGS) |
| `validacao_status` | Preservado em **31**/31 |
| `qualidade_dado` | Preservado em **31**/31 |
| Apex **não** voltou para licitação | `apex_standardized.json`: apenas **`apoio_internacionalizacao`** em `tipo_recurso` |
| Amazul **não** Prêmio/Subvenção/Reembolsável | Grep no standardized: **sem** essas strings em `tipo_recurso` |
| Ambev **não** marketing genérico | URLs **100accelerator**; **`tipo_conteudo_ambev`** = **`open_innovation_aceleracao`** |
| Faperg preservou PDF | Um item com **`pdf_url`** fapergs.rs.gov.br; **`pdf_preserved_items`** = **1** |

---

## Apply staging — **não executado** (recomendado)

PowerShell:

```powershell
$env:EDITALFINDER_ALLOW_STAGING_APPLY="true"
$env:EDITALFINDER_ENV="staging"
python scripts/load_ready_sources.py --apply --staging --sources apex,faperg,amazul,ambev --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json --test-db-before-apply
```

## Validação pós-apply — **não executada** (recomendado)

```powershell
python scripts/validate_database_after_load.py --staging --source apex
python scripts/validate_database_after_load.py --staging --source faperg
python scripts/validate_database_after_load.py --staging --source amazul
python scripts/validate_database_after_load.py --staging --source ambev
```

---

## JSON

`audit_reports_blocked_sources/lote4_ready_sources_loader_dryrun.json`
