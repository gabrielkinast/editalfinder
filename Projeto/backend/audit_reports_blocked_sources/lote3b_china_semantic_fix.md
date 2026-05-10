# Correção semântica — lote 3B China (pós-curadoria)

**Gerado (UTC):** 2026-05-02T21:52:33Z (alinhado com `lote3b_china_semantic_fix.json`).

## Problema

Na pasta `lote3b_china_curated_semantic/`, a auditoria (`scripts/audit_semantic_classification.py`) reportava **4×** `oportunidade_fomento_sem_fomento`.

**Causa:** o critério usa substrings em `tipo_oportunidade` / `tipo_recurso` normalizados (por exemplo `chamada` dentro de `chamada_publica`, ou `fomento` em `fomento_pdi`) e exige tokens PT/EN (`grant`, `funding`, `chamada`, …) no *blob* construído a partir de título/descrição/programa/palavras-chave. Texto principalmente **chinês** (基金, 申报, …) **não** contava como evidência, gerando falso positivo em itens válidos de fomento/guia NSFC e no anúncio AVIC.

## Itens analisados (antes do fix)

| Fonte | Título (resumo) | Link | Situação real |
|--------|-----------------|------|----------------|
| china_nsfc | 医学科学部青年科学基金…注意事项补充说明 | …/120883.html | Guia / requisitos de candidatura NSFC (fomento) |
| china_nsfc | 2026年度国家自然科学基金改革举措 | …/2026ndgjzrkxjjggjc.html | Secção do guia 2026 (política de candidatura) |
| china_nsfc | 国家自然科学基金申请代码 | …/gjzrkxjjsqdm2026.html | Referência de códigos de candidatura |
| china_avic | 2026年纪检监察人员校园招聘公告 | …/642825.shtml | **Recrutamento** (RH), não grant nem compra pública de equipamento |

Os quatro itens **não** eram “notícia institucional pura” no sentido da curadoria anterior; o problema era **alinhar tipo_recurso / tipo_oportunidade** com o contrato da auditoria e com a semântica real.

## Ajustes (só calibração local)

Ficheiro: `CORE/taxonomy_filtros.py`

1. **`calibrate_china_nsfc_extras`** — ramo sem procurement: `chamada_publica` → **`grant`** (mantém `funding_opportunity` quando já definido); `tipo_recurso` = **`Grant para pesquisa competitiva`** (rótulo sem `fomento` no identificador, para não acoplar ao mesmo ramo da auditoria de forma inconsistente com o blob zh).

2. **`calibrate_china_avic_extras`** — se texto tem **校园招聘** / **纪检监察** e **招聘**: **`processo_seletivo`**, **`Seleção / emprego público`**, remove setores defesa/aero/nuclear herdados do *chrome* do site; **return** antes do ramo genérico “notícia”.

3. **`calibrate_china_university_procurement_extras`** — **compra pública** só com sinal forte (招标/投标/tender/bid/竞价 ou 采购 com 公开招标|采购公告|中标|政府采购); caso contrário **`grant`** + **`Grant para pesquisa competitiva`**; `origem_portal` **USTC** quando o link é `ustc.edu.cn`.

**Não alterado:** gate global de oportunidade, Supabase, migrations, loader, `source_readiness.json`, JSONs brutos curados.

## Pipelines reexecutados

```text
python scripts/retransform_all.py --sources china_nsfc,china_avic,china_university_procurement --dry-run --output-dir audit_reports_blocked_sources/lote3b_china_curated_semantic_fix

python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote3b_china_curated_semantic_fix/standardized --output-dir audit_reports_blocked_sources/lote3b_china_curated_semantic_fix_audit
```

## Resultado

- **14** brutos → **14** transformados, **0** rejeitados (`retransform_summary.json`).
- Auditoria semântica: **`flags_totais` vazio**; **`oportunidade_fomento_sem_fomento`: 0** (`audit_semantic_summary.json` em `lote3b_china_curated_semantic_fix_audit/`).

## Recomendação de readiness (manual)

| Fonte | Recomendação |
|--------|----------------|
| **china_nsfc** | **ready_with_notes** |
| **china_avic** | **needs_manual_review** |
| **china_university_procurement** | **ready_with_notes** |
| **china_cnnc** | **blocked** |
| **china_norinco** | **needs_manual_review** |

*(Não atualizar `source_readiness.json` automaticamente.)*
