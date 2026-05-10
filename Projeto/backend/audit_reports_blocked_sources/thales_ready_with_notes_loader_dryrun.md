# Thales suppliers — loader dry-run (`ready_with_notes`)

## Decisão

`thales_suppliers` em **ready_with_notes** (não ready pleno), após curadoria Thales.

## Diff / resumo de readiness

### `config/source_readiness.json`

- **Removido** de `needs_manual_review`.
- **Incluído** em `ready_with_notes` (a seguir de `rheinmetall_suppliers`, antes de `saude`).

### `audit_reports_retransform/readiness_for_loader.json`

- **Contagens:** `pronto_com_observacoes` 66 → 67; `precisa_revisao_manual` 7 → 6.
- **Removido** de `fontes_para_revisao`.
- **Incluído** em `fontes_prontas_para_loader` (necessário para `--exclude-blocked` selecionar a fonte).

### Standardized

Origem: `audit_reports_blocked_sources/lote5_fix_thales/standardized/thales_suppliers_standardized.json`  
Destino: `audit_reports_retransform/standardized/thales_suppliers_standardized.json`

## Comando dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources thales_suppliers --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Resultado do dry-run

| Métrica | Valor |
|--------|-------|
| `id_execucao` | `650eba1f-816e-43ce-9dc0-da67c0a93cf4` |
| `data_auditoria` | `2026-05-03T23:06:30Z` |
| `sources_selected` | 1 |
| `itens_standardized_total` | 4 |
| `would_upsert_total` | 4 |
| `would_ignore_total` | 0 |
| `mapping_errors_total` | 0 |
| `critical_empty_items_total` | 0 |
| `docs_input_items_total` | 3 |
| `docs_preserved_items_total` | 3 |
| `pdf_input_items_total` | 3 |
| `pdf_preserved_items_total` | 3 |
| `documentos_perdidos_no_payload_total` | 0 |
| `apply_requested` | false |

Relatório agregado: `audit_reports_loader_ready/load_ready_summary.json`.

## Verificação (checklist)

| Critério | Estado |
|----------|--------|
| 4 itens | OK |
| `would_upsert` = 4 | OK |
| `mapping_errors` = 0 | OK |
| `critical_empty` = 0 | OK |
| `tipo_oportunidade` | `supplier_portal` nos 4 (dentro do conjunto permitido) |
| `tipo_recurso` | `oportunidade_fornecedor` |
| `perfil_ideal` | `fornecedor`, `empresa` |
| `origem_portal` | Thales |
| `idioma_original` | en |
| `regiao` | Internacional |
| Documentos / PDFs | 3 itens com PDF; preservação 3/3 no dry-run |
| Sem careers / news / press / contact / investors | OK (URLs filtradas na colheita) |
| Setor defesa só por nome | Hub e PDFs “limpos” com `setor_estrategico` vazio onde não há evidência; entradas com texto de normas podem ter marcadores derivados do **conteúdo do PDF**, não do nome da empresa |

## Escopo explícito desta sessão

- Sem `--apply`.
- Sem alterações no Supabase.
- Sem alteração ao gate global.

## Recomendação para staging

O dry-run está **consistente** para carga: 4 upserts previstos, sem erros de mapeamento nem perda de documentos/PDF no agregado do loader. **Recomenda-se** apply em **staging** apenas quando a equipa quiser promover a fonte, com fluxo controlado (`environment_guard` / `has_allow_staging_apply` conforme política do projeto) e revisão humana, dado **ready_with_notes** e dependência de **manifesto + WAF/Incapsula** para validação periódica das URLs.
