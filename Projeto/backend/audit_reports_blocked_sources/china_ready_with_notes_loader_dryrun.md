# Loader dry-run — China `ready_with_notes` (NSFC + USTC)

**Data (UTC):** 2026-05-02T22:00:15Z

## Diff / resumo de readiness

### `config/source_readiness.json`

| Fonte | Antes | Depois |
|--------|--------|--------|
| `china_nsfc` | `needs_manual_review` | **`ready_with_notes`** |
| `china_university_procurement` | `needs_manual_review` | **`ready_with_notes`** |
| `china_avic` | `blocked` | **`needs_manual_review`** |
| `china_norinco` | `blocked` | **`needs_manual_review`** |
| `china_cnnc` | `blocked` | **`blocked`** (inalterado) |

### `audit_reports_retransform/readiness_for_loader.json`

- `china_nsfc` e `china_university_procurement` incluídos no fim de **`fontes_prontas_para_loader`**; `pronto_com_observacoes`: **59 → 61**.
- `china_avic` e `china_norinco` retirados de **`fontes_bloqueadas_temporariamente`** e passados a **`fontes_para_revisao`**; `bloquear_temporariamente`: **18 → 16**; `precisa_revisao_manual`: **7 → 9**.
- Contador semântico `oportunidade_fomento_sem_fomento` no top20: **1 → 0** (alinhado ao lote já corrigido).

O slice derivado que o loader usa está em `audit_reports_loader_ready/readiness_derived_slice.json` (confirma `china_nsfc` e `china_university_procurement` em `ready_with_notes`).

## Standardized copiados

- `audit_reports_blocked_sources/lote3b_china_curated_semantic_fix/standardized/china_nsfc_standardized.json` → `audit_reports_retransform/standardized/china_nsfc_standardized.json`
- `…/china_university_procurement_standardized.json` → `audit_reports_retransform/standardized/china_university_procurement_standardized.json`

*(Apenas estas duas fontes; AVIC/NORINCO/CNNC não foram substituídos.)*

## Comando executado

```bash
python scripts/load_ready_sources.py --dry-run --sources china_nsfc,china_university_procurement --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

Saída de relatório: pasta **`audit_reports_loader_ready/`** (`load_ready_summary.json`, `load_ready_by_source.json`, `load_ready_payload_examples.json`, …).

## Resultado do dry-run

| Métrica | Valor |
|---------|--------|
| Fontes selecionadas | 2 |
| Itens standardized | **13** (9 NSFC + 4 USTC) |
| `would_upsert` | **13** |
| `would_ignore` | 0 |
| `mapping_errors` | **0** |
| `critical_empty_items` | **0** |
| Documentos (input → preservados) | 9 → **9** (0 perdidos) |
| PDF (input → preservados) | 3 → **3** |

### Por fonte

- **china_nsfc:** 9 standardized, 9 upserts, 5 docs preservados, 2 PDFs preservados.
- **china_university_procurement:** 4 standardized, 4 upserts, 4 docs, 1 PDF.

## Verificações pedidas (resumo)

- **`tipo_oportunidade` / `tipo_recurso`:** preenchidos em todos os itens (ex.: `grant` / `funding_opportunity` + `Grant para pesquisa competitiva`).
- **`idioma_original`, `titulo_original`, `origem_portal`:** presentes nos JSON standardized (ex.: `zh` + `NSFC (nsfc.gov.cn)`; USTC com portal USTC).
- **`validacao_status`, `qualidade_dado`:** contagem de preservação = número de itens.
- **Áreas:** maioria com `area` vazia; sem evidência neste relatório de “área excessiva” no sumário agregado.
- **Notícias políticas removidas na curadoria:** exemplos de payload não incluem entradas políticas/institucionais da triagem removida.

## Apply e staging

- **Não** foi executado `--apply`; **não** houve escrita no Supabase por este fluxo.
- O `environment_guard` do run indicou `has_allow_staging_apply: false` neste ambiente — antes de qualquer apply, alinhar política de staging documentada para o loader.

### Recomendação

**Sim, pode candidatar-se a apply em staging** depois de:

1. Aprovação explícita humana e revisão dos itens `validacao_status: incompleto` se isso for bloqueante para o vosso processo.
2. Configurar o ambiente para permitir apply de staging conforme `load_ready_sources.py` (ex.: flags e `.env` esperados).
3. Correr **sem** `--dry-run`, com `--staging` (e **não** usar apply em produção até critérios internos).

Detalhe estruturado: `china_ready_with_notes_loader_dryrun.json`.
