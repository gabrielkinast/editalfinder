# Lote 1 — dry-run combinado (standardized actualizados)

**Input:** `audit_reports_retransform/standardized`  
**Comando:** `python scripts/load_ready_sources.py --dry-run --sources badesul,pncp,senai,softex,plataforma_industria,petrobras --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json`

**ID execução:** `a8e9a2d0-d98c-4c65-8914-4d0f683f5caf` (ver JSON).

---

## 1. Sincronização prévia da pasta `audit_reports_retransform/standardized`

| Ficheiro | Estado antes | Acção |
|----------|--------------|--------|
| `badesul_standardized.json` | 0 itens (lista vazia) | **Copiado** de `audit_reports_blocked_sources/lote1_fix_badesul_pncp/standardized/` (**7** itens) |
| `pncp_standardized.json` | 0 itens | **Copiado** de `audit_reports_blocked_sources/pncp_calibration/retransform/standardized/` (**31** itens) |
| `senai_standardized.json` | 22 itens | **Mantido** (alinhado às calibrações; mtime igual ao de `lote1_fix_senai_softex_semantic2`) |
| `softex_standardized.json` | 2 itens | **Mantido** |
| `plataforma_industria_standardized.json` | 23 itens | **Mantido** (mtime igual ao de `lote1_fix_plataforma_industria`) |
| `petrobras_standardized.json` | 4 itens | **Mantido** (4 itens; não usar `CORE/transformer` com 5) |

---

## 2. Totais por fonte (standardized / would_upsert)

| Fonte | itens_standardized | would_upsert | canonical_skipped |
|--------|-------------------:|-------------:|--------------------:|
| badesul | 7 | 7 | 0 |
| pncp | 31 | 31 | 0 |
| senai | 22 | 22 | 0 |
| softex | 2 | 2 | 0 |
| plataforma_industria | 23 | 1 | **22** |
| petrobras | 4 | 4 | 0 |
| **Total** | **89** | **67** | **22** |

Os **22** `canonical_skipped` são linhas do alias `plataforma_industria` cujo URL já foi reclamado pelo crawl canónico `senai` (`config/source_canonicalization.json`, grupo `plataforma_inovacao`).

---

## 3. Verificação global

| Critério | Valor |
|----------|------:|
| `itens_standardized_total` | **89** |
| `would_upsert_total` | **67** |
| `mapping_errors_total` | **0** |
| `critical_empty_items_total` | **0** |
| `docs_input_items_total` | **48** |
| `docs_preserved_items_total` | **48** |
| `documentos_perdidos_no_payload_total` | **0** |
| `pdf_input_items_total` | **25** |
| `pdf_preserved_items_total` | **25** |
| `validacao_status_preserved_items_total` | **67** (= would_upsert) |
| `qualidade_dado_preserved_items_total` | **67** (= would_upsert) |
| `canonical_skipped_total` | **22** |

---

## 4. JSON completo

`audit_reports_blocked_sources/lote1_ready_sources_loader_dryrun.json` — inclui `resumo_global`, `por_fonte`, `sincronizacao_ficheiros` e `verificacao`.

---

## 5. Apply staging (não executado)

Usar o mesmo `--input-dir audit_reports_retransform/standardized` no `load_ready_sources.py` quando for aplicar, para não voltar a `CORE/transformer` desactualizado.

```powershell
$env:EDITALFINDER_ALLOW_STAGING_APPLY = "1"
$env:EDITALFINDER_ENV = "staging"
python scripts/load_ready_sources.py --apply --staging --sources badesul,pncp,senai,softex,plataforma_industria,petrobras --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```
