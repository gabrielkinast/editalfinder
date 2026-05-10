# AMAZUL — correção `tipo_recurso` (calibração local) + loader dry-run

**Data:** 2026-05-03  

## Problema

Seis itens tinham `tipo_recurso` atípico (**Prêmio / Concurso**, **Subvenção**, **Reembolsável**) por ruído de texto/PDF DOU agregado, apesar de `tipo_oportunidade` = `licitacao` e de serem dispensas/compras públicas.

## Correção (`CORE/taxonomy_filtros.py` — `calibrate_amazul_extras`)

1. **`procurement_hit`:** evidência lexical alargada (fornecedor, contratada, objeto, ratificada, inexigibilidade, NUP, edital, …) mais **URL** sob `/acesso-a-informacao/licitacoes-e-contratos/` com slug de dispensa/pregão/contrato/UASG/NUP/edital.  
2. **Compra / licitação:** `item["tipo_recurso"]` passa a ser **sempre** `licitação` (não usa mais `item.get("tipo_recurso") or …`, que preservava o erro do transformer).  
3. **Concurso:** mantém-se só com marcadores explícitos e **sem** `procurement_hit`; `tipo_recurso` = `Seleção / emprego público`.  
4. **Fomento/chamada por texto:** não aplica o ramo “subven/fomento” quando `lk_licit_hub` (hub de licitações).  
5. **Nuclear:** condição de nuclear + compra usa `procurement_hit` em vez do tuplo antigo.

## Retransformação

```bash
python scripts/retransform_all.py --sources amazul --dry-run --output-dir audit_reports_blocked_sources/lote4_fix_amazul_tipo_recurso
```

**Resultado:** 19 standardized; `tipo_recurso` = **«licitação»** nos 19; `tipo_oportunidade` = **licitacao** nos 19; sem **Prêmio / Concurso**, **Subvenção** ou **Reembolsável**.

## Cópia para o input do loader

- `audit_reports_blocked_sources/lote4_fix_amazul_tipo_recurso/standardized/amazul_standardized.json`  
  → `audit_reports_retransform/standardized/amazul_standardized.json`

## Loader (dry-run)

```bash
python scripts/load_ready_sources.py --dry-run --sources amazul --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

| Verificação | Valor |
|-------------|------:|
| Itens standardized | 19 |
| would_upsert | 19 |
| mapping_errors | 0 |
| critical_empty_items | 0 |
| documentos preservados (itens) | 19 / 19 |
| pdf_url preservado (itens) | 19 / 19 |
| documentos perdidos no payload | 0 |

`tipo_oportunidade` permanece **licitacao** em todos os itens; `tipo_recurso` homogeneizado em **licitação**; gate global, Supabase e apply **não** foram alterados.

## JSON

Detalhe estruturado: `amazul_tipo_recurso_fix_loader_dryrun.json`.
