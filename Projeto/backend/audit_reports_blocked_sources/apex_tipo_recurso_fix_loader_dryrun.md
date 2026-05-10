# Apex — correção semântica `tipo_recurso` (Exporta Mais ≠ licitação)

**Data:** 2026-05-02  

**Objetivo:** itens **Exporta Mais** / inscrição CRM **não** herdarem `tipo_recurso` de licitação por heurística (causa raiz: marcadores genéricos com substring **`compra`**, que casava em **“compradores”** no texto).

## Alteração em código

**Ficheiro:** `CORE/taxonomy_filtros.py`

- Constantes novas: **`APEX_LICITACAO_EVIDENCIA`** (frases e termos estritos: licitação, pregão, compra pública, fornecedor, `compras.apexbrasil`, procurement, etc., **sem** `compra` isolado).
- **`APEX_PROGRAMA_EXPORTACAO`**: Exporta Mais, CRM `crm-apps.apexbrasil`, `inscricao-eventos`, internacionalização, exportação, compradores internacionais, etc.
- **`calibrate_apex_extras`**: ordem de decisão — (1) licitação só com `APEX_LICITACAO_EVIDENCIA`; (2) programa/exportação com sobrescrita se o recurso atual parecer licitação mas houver só sinais de programa; (3) `tipo_recurso` típico `apoio_internacionalizacao` / `promocao_exportacao` / `apoio`; `tipo_oportunidade` `programa`, `chamada_publica` ou `selecao_empresas` conforme texto.

**Não alterado:** gate global, FAPERGS (`calibrate_faperg_extras`), loader apply, Supabase, migrations.

## Retransform (só apex)

```text
python scripts/retransform_all.py --sources apex --dry-run --output-dir audit_reports_blocked_sources/lote4_fix_apex_tipo_recurso
```

- **3** brutos → **3** transformados, **0** rejeitados.

## Cópia do standardized

Origem → destino:

`audit_reports_blocked_sources/lote4_fix_apex_tipo_recurso/standardized/apex_standardized.json`  
→ `audit_reports_retransform/standardized/apex_standardized.json`

## Loader dry-run (só apex)

```text
python scripts/load_ready_sources.py --dry-run --sources apex --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

| Métrica | Valor |
|---------|--------|
| itens standardized | 3 |
| **would_upsert** | **3** |
| **mapping_errors** | **0** |
| **critical_empty_items** | **0** |

Detalhe por item (ver `audit_reports_loader_ready/load_ready_payload_examples.json`):

- `tipo_recurso` no payload: **`apoio_internacionalizacao`** nos três casos.
- `tipo_oportunidade`: **`programa`** (Casa e Design; Alimentos/NATURALTECH); **`selecao_empresas`** (E-commerce 2026 — texto com seleção/critérios).

## Confirmações pedidas

| Critério | Estado |
|----------|--------|
| 3 itens | Sim |
| 0 erros de mapeamento | Sim |
| 0 `critical_empty` | Sim |
| `tipo_recurso` ≠ licitação | Sim (`apoio_internacionalizacao`) |
| `tipo_oportunidade` coerente | Sim (programa / seleção) |
| Sem Menu / evento genérico / notícia institucional | Sim (títulos Exporta Mais) |
| Substring “licit” no `apex_standardized.json` copiado | **Não** (grep limpo) |

## JSON

`audit_reports_blocked_sources/apex_tipo_recurso_fix_loader_dryrun.json`

**Apply:** não executado.
