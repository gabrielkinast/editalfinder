# PNCP — `ready_with_notes` e dry-run do loader

**Data (loader):** 2026-05-01T23:30:06Z  
**Execução:** `99da75e8-ae3b-4147-918e-7bfae94f6bba`  
**Modo:** dry-run (sem apply)

## 1. Readiness (`config/source_readiness.json`)

- **Removido** de `blocked`.
- **Incluído** em `ready_with_notes`, na posição entre `nuclep` e `pncp_defesa`.

O loader continua a ler `audit_reports_retransform/readiness_for_loader.json` e pode reescrever o JSON de readiness; o estado atual está alinhado com PNCP em `ready_with_notes`.

## 2. Comando executado

```text
python scripts/retransform_all.py --sources pncp --dry-run --output-dir audit_reports_blocked_sources/pncp_calibration/retransform
python scripts/load_ready_sources.py --dry-run --sources pncp --exclude-blocked --input-dir audit_reports_blocked_sources/pncp_calibration/retransform/standardized
```

Entrada do loader: `audit_reports_blocked_sources/pncp_calibration/retransform/standardized/pncp_standardized.json`.

## 3. Correção no pipeline (antes do dry-run final)

Em `CORE/transformer.py`, para `source_name == "pncp"`, **não** se aplica mais `build_defense_extras` (heurísticas de defesa). Caso contrário, `infer_opportunity_type` classificava tudo como `supplier_portal` por menção a “fornecedor”, antes da classificação de compra pública.

Após retransform só PNCP, `extras.tipo_oportunidade` ficou **`compra_publica` em 31/31** itens.

## 4. Resultado do dry-run (métricas agregadas)

| Métrica | Valor |
|--------|------:|
| Itens standardized | 31 |
| `would_upsert` | 31 |
| `would_ignore` | 0 |
| Erros de mapeamento | 0 |
| `critical_empty` | 0 |
| Itens com documentos (entrada) | 16 |
| Documentos preservados no payload | 16 |
| Documentos perdidos | 0 |
| Itens com `pdf_url` na entrada | 0 |
| `validacao_status` preservado (itens) | 31 |
| `qualidade_dado` preservado (itens) | 31 |

Detalhe por fonte: `audit_reports_loader_ready/load_ready_by_source.json` (fonte `pncp`, mesmos números).

## 5. Verificações pedidas

| Verificação | Situação |
|-------------|----------|
| Itens standardized | 31 |
| `would_upsert` | 31 |
| Erros de mapeamento | 0 |
| Documentos preservados | 16/16 |
| Links oficiais em `extras` | 17 itens com lista `links_oficiais` não vazia |
| `pdf_url` indevido | Entrada 0 PDFs; nada preenchido indevidamente |
| `tipo_oportunidade` | `compra_publica` em todos (após skip de defense para PNCP) |
| `tipo_recurso` | `Contratacao Publica` em todos |
| `perfil_ideal` | Presente em 31 (valor típico: `['fornecedor', 'empresa']`) |
| `validacao_status` | 17 `incompleto`, 13 `valido`, 1 `suspeito` |
| `qualidade_dado` | Presente em 31 (escores variados) |

Campos semânticos presentes no payload: contadores de `tipo_oportunidade`, `tipo_recurso`, `perfil_ideal`, `validacao_status`, `qualidade_dado` batem entrada ↔ payload ↔ preservação (31 em cada, no summary).

## 6. Apply

- **Não** foi executado apply.
- `environment_guard` do summary: `block_reason: missing_staging_flag` (comportamento esperado sem flag explícita de staging para apply).

## 7. Recomendação para staging

- **Tecnicamente:** o dry-run está consistente (31 upserts, sem perda de documentos, sem erros de mapeamento, tipo de oportunidade coerente após o fix do transformer).
- **Operacional:** há **17** registros com `validacao_status: incompleto` e **1** `suspeito`; convém revisar se isso é aceitável para negócio antes do primeiro apply em staging.
- **Próximo passo:** quando for aplicar, usar o fluxo já previsto no projeto (flag de staging / guard do loader), **sem** alterar `opportunity_gate` global, conforme combinado.

Arquivo JSON espelho: `audit_reports_blocked_sources/pncp_ready_with_notes_loader_dryrun.json`.
