# Lote 3 — relatório consolidado (3A Japão · 3B China)

**Gerado (UTC):** 2026-05-02T22:15:00Z  
**Formato estruturado:** `lote3_consolidado.json` (mesmo diretório).

Este documento consolida apenas **estado administrativo e técnico** das fontes do lote 3, **sem misturar** dados de Japão e China entre si. Não inclui execução de loader apply, alterações ao Supabase, migrations, gate global de oportunidade nem reescrita automática de `source_readiness.json`.

---

## 1. Resumo executivo

| Sub-lote | Situação |
|----------|-----------|
| **3A — Japão** | Quatro fontes instrumentadas com **calibrações locais**; crawlers terminaram com código **0**, mas **listagens falharam** ou não geraram itens úteis → **brutos efetivos = 0**, **retransformação 0 → 0**. Readiness: **revisão manual** (JST, JAEA) ou **bloqueio** (JAXA, e-Rad) até haver **coleta com dados reais** e rede estável. |
| **3B — China** | **Proteção de output** (`save_output_safely` / fluxos Asia) validada (preservação, `latest_error`, `failures.jsonl`, **exit 2** como preservação). **Curadoria** NSFC (28→9) e USTC (6→4); AVIC reduzida a **1** item; NORINCO/CNNC sem promoção. **Auditoria semântica** do conjunto curado: **`flags_totais` vazio**. **Dry-run loader** só para `china_nsfc` + `china_university_procurement`: **13** standardized, **13** would_upsert, **0** erros de mapeamento, **0** critical empty, **9/9** documentos e **3/3** PDFs preservados. |

**Fontes com readiness apto a considerar staging (duas):** `china_nsfc`, `china_university_procurement` (`ready_with_notes`).  
**Fontes pendentes (sete):** `japan_jst`, `japan_jaea`, `japan_jaxa`, `japan_e_rad`, `china_avic`, `china_norinco`, `china_cnnc`.

---

## 2. Lote 3A — Japão

Calibrações locais em `CORE/taxonomy_filtros.py` (e integração no `transformer`) **preparadas** para JST, JAEA, JAXA e e-Rad. No ciclo documentado, os crawlers **não** alimentaram brutos úteis (`*_editais.json` com **0** itens após falha de listagem/rede).

### Tabela por fonte (3A)

| Fonte | Estado (ciclo) | Brutos | Transformados | Rejeitados | Docs preservados | Problemas | Correções | Readiness recomendado |
|--------|----------------|--------|-----------------|------------|------------------|-----------|-----------|------------------------|
| **japan_jst** | Após crawl/retransform | 0 | 0 | 0 | N/A | Listagens HTTP falharam / bloqueio | Calibração local preparada | **needs_manual_review** |
| **japan_jaea** | Idem | 0 | 0 | 0 | N/A | Idem; histórico canónico com ruído quando houve dados antigos | Calibração JAEA preparada | **needs_manual_review** |
| **japan_jaxa** | Idem | 0 | 0 | 0 | N/A | Índice institucional / imprensa nos exemplos antigos | Calibração JAXA preparada | **blocked** |
| **japan_e_rad** | Idem | 0 | 0 | 0 | N/A | Página de procedimento vs grant; listagens falharam | Calibração e-Rad preparada | **blocked** |

### Observações — Japão

- **Reexecutar crawlers** em ambiente com **acesso HTTP estável**, respeitando robots e rate limits.
- **Não** promover readiness com JSON bruto **vazio** sem novo ciclo com dados reais.
- Em falhas de coleta, a política Asia alinha-se ao princípio de **não sobrescrever** ficheiros anteriores com dados com **`[]`** quando há preservação configurada (paridade conceitual com a China).

**Referência:** `audit_reports_blocked_sources/lote3a_japan_diagnostico.json` / `.md`.

---

## 3. Lote 3B — China

### Tabela por fonte (3B)

| Fonte | Antes (destaque) | Depois (destaque) | Brutos (curados / pres.) | Transformados | Rejeitados | Docs / PDF (dry-run 2 fontes) | Problemas | Correções | Readiness |
|--------|------------------|-------------------|---------------------------|---------------|------------|-------------------------------|-----------|-----------|-----------|
| **china_nsfc** | 28 brutos; ruído político/institucional | **9** curados | 9 | 9 | 0 | 5 docs, 2 PDF (por fonte) | Flags semânticas antes do fix | Curadoria + `calibrate_china_nsfc_extras` | **ready_with_notes** |
| **china_university_procurement** | 6 (USTC + falhas Tsinghua/PKU nos logs) | **4** curados | 4 | 4 | 0 | 4 docs, 1 PDF | Procurement vs fundos; nuclear sem evidência | Curadoria + `calibrate_china_university_procurement_extras` | **ready_with_notes** |
| **china_avic** | 15 mistos | **1** (recrutamento) | 1 | 1 | 0 | — | Predominância institucional | Curadoria + ramo recrutamento AVIC | **needs_manual_review** |
| **china_norinco** | Preservação exit 2 | Legado **1** item | 1 | — | — | — | Listagens EN / vazio pós-filtros | — neste fecho | **needs_manual_review** |
| **china_cnnc** | Falha total listagem | Preservado (exit 2) | 1 (legado) | — | — | — | Rede/bloqueio | `save_output_safely` | **blocked** |

*Transformados/rejeitados agregados do dry-run loader referem-se apenas a **china_nsfc** + **china_university_procurement** (13 itens).*

---

## 4. Proteção de output (Asia / China)

| Mecanismo | Função |
|-----------|--------|
| **`crawler_output_safe.py`** | `save_output_safely`: ramos para itens > 0, vazio confirmado, falha de coleta, vazio sem confirmação. |
| **Backups** | Backup do `*_editais.json` anterior quando uma gravação bem-sucedida substitui conteúdo com dados. |
| **`latest_error.json`** | Registo JSON no `outputs/` da fonte com `failure_kind`, `listing_events`, `tipo_resultado`, etc. |
| **`failures.jsonl`** | Linhas JSONL em `audit_reports_crawler_failures/failures.jsonl` com `source_name` e `ts_utc`. |
| **Exit code 2** | Nos mains Asia: **preservação intencional** do ficheiro principal — **não** é crash. |

### Tipos de resultado (resumo)

- **`falha_de_coleta`:** rede/listagem ou `collection_failed` explícito.  
- **`coleta_vazia_pos_filtros`:** listagens OK mas zero itens após filtros/gate **no crawl**.  
- **`coleta_vazia_sem_confirmacao`:** vazio sem falha explícita nem `confirmed_no_items`.  
- **`confirmed_no_items`:** lista vazia **confirmada** com motivo explícito (`allow_empty` + razão).

---

## 5. Dry-run loader — China (duas fontes)

| Métrica | Valor |
|---------|--------|
| Fontes | `china_nsfc`, `china_university_procurement` |
| Standardized | **13** (9 + 4) |
| `would_upsert` | **13** |
| `mapping_errors` | **0** |
| `critical_empty_items` | **0** |
| Documentos | **9 / 9** preservados |
| PDFs | **3 / 3** preservados |
| Auditoria semântica (pós-cura + calibração) | **`flags_totais` vazio**; `oportunidade_fomento_sem_fomento`: **0** |

**Artefactos:** `audit_reports_loader_ready/load_ready_summary.json`, `china_ready_with_notes_loader_dryrun.md` / `.json`.

---

## 6. Comandos recomendados (não executados nesta entrega)

### Apply staging (PowerShell)

```powershell
$env:EDITALFINDER_ALLOW_STAGING_APPLY="true"
$env:EDITALFINDER_ENV="staging"
python scripts/load_ready_sources.py --apply --staging --sources china_nsfc,china_university_procurement --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json --test-db-before-apply
```

### Validação pós-apply

```bash
python scripts/validate_database_after_load.py --staging --source china_nsfc
python scripts/validate_database_after_load.py --staging --source china_university_procurement
```

---

## 7. Pode aplicar em staging?

| Área | Recomendação |
|------|----------------|
| **china_nsfc + china_university_procurement** | **Sim, condicional:** após aprovação humana, conferência de itens `incompletos` se relevante, e ambiente staging (`EDITALFINDER_ALLOW_STAGING_APPLY`, `EDITALFINDER_ENV`, teste DB) conforme política interna. |
| **Japão (3A)** | **Não**, até novo crawl com **bruto real** (`len(itens) > 0`) e retransformação validada. |
| **china_avic / china_norinco / china_cnnc** | **Não** para loader geral: AVIC/NORINCO em revisão manual; CNNC bloqueada. |

---

## 8. Próximos passos

1. Aplicar **china_nsfc** e **china_university_procurement** em **staging** se aceite o risco/QA.  
2. **Reexecutar** o lote **3A Japão** com melhor rede/acesso.  
3. **Revisão manual** **china_avic** e **china_norinco** (URLs, listagens, calibração).  
4. **Novas seeds / acesso** para **china_cnnc** quando viável.  
5. **Planear** o próximo lote de fontes asiáticas após fecho operacional do lote 3.

---

## 9. Listas finais

### Liberadas para consideração de staging (readiness)

- `china_nsfc`  
- `china_university_procurement`  

### Pendentes (sem staging neste consolidado)

- `japan_jst`, `japan_jaea`, `japan_jaxa`, `japan_e_rad`  
- `china_avic`, `china_norinco`, `china_cnnc`  

---

*Snapshot de `config/source_readiness.json` nesta geração: Japão (JST/JAEA → `needs_manual_review`; JAXA/e-Rad → `blocked`); China (NSFC/USTC → `ready_with_notes`; AVIC/NORINCO → `needs_manual_review`; CNNC → `blocked`). Nenhuma alteração automática foi feita ao gravar este relatório.*
