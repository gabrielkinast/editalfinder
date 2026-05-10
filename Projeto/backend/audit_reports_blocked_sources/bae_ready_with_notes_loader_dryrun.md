# BAE Systems suppliers — loader dry-run (`ready_with_notes`)

## Decisão

`bae_systems_suppliers` em **ready_with_notes** (não ready pleno), após curadoria BAE/HICX.

## Diff / resumo de readiness

### `config/source_readiness.json`

- **Removido** de `needs_manual_review`.
- **Incluído** em `ready_with_notes` (após `badesul`, entrada `bae_systems_suppliers`).

### `audit_reports_retransform/readiness_for_loader.json`

- **Contagens:** `pronto_com_observacoes` = **68**; `precisa_revisao_manual` = **5**.
- **Removido** de `fontes_para_revisao`.
- **Incluído** em **`fontes_prontas_para_loader`** (após `thales_suppliers`) — necessário para `--exclude-blocked` selecionar a fonte.

### Standardized

Origem: `audit_reports_blocked_sources/lote5_fix_bae/standardized/bae_systems_suppliers_standardized.json`  
Destino: `audit_reports_retransform/standardized/bae_systems_suppliers_standardized.json`

## Comando dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources bae_systems_suppliers --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Resultado do dry-run (run válido)

| Métrica | Valor |
|--------|-------|
| `id_execucao` | `eb82ebd9-197f-4ba4-9fb4-246d42885657` |
| `data_auditoria` | `2026-05-04T00:09:20Z` |
| `sources_selected` | 1 |
| `itens_standardized_total` | 3 |
| `would_upsert_total` | 3 |
| `would_ignore_total` | 0 |
| `mapping_errors_total` | 0 |
| `critical_empty_items_total` | 0 |
| `documentos_perdidos_no_payload_total` | 0 |
| `pdf_input_items_total` | 0 |
| `apply_requested` | false |

Relatório agregado: `audit_reports_loader_ready/load_ready_summary.json`.

**`official_link_only`:** o `load_ready_summary.json` não expõe `official_link_only_total`; no standardized há **1** item com `extras.extraction_mode == "official_link_only"` (stub `baesystems.com`). O quick audit em `audit_reports_blocked_sources/lote5_fix_bae/retransform_by_source.json` regista **`official_link_only_total`: 1**.

## Verificação (checklist)

| Critério | Estado |
|----------|--------|
| 3 itens | OK |
| `would_upsert` = 3 | OK |
| `mapping_errors` = 0 | OK |
| `critical_empty` = 0 | OK |
| `official_link_only` | 1 item (stub corporativo WAF) |
| `validacao_status` (nível do item) | `incompleto`, `acesso_limitado`, `acesso_limitado` |
| `tipo_oportunidade` | `supplier_portal` (cumpre supplier_portal / cadastro_fornecedor) |
| `tipo_recurso` | `oportunidade_fornecedor` |
| `perfil_ideal` | `fornecedor`, `empresa` |
| `origem_portal` | BAE Systems |
| `idioma_original` | en |
| `setor_estrategico` | `[]` nos três |
| Sem careers / news / investors | OK (URLs filtradas) |
| Sem PDFs inventados | OK (`pdf_url` vazio) |
| Sem documentos perdidos | OK (`documentos_perdidos_no_payload_total` = 0) |

## Escopo desta sessão

- Sem `--apply`.
- Sem alterações no Supabase.
- Sem alteração ao gate global.

## Recomendação para staging

O dry-run está **consistente** para carga: 3 upserts, sem erros de mapeamento nem perda de documentos. **Recomenda-se** apply em **staging** apenas quando a equipa quiser promover a fonte, com fluxo controlado (`environment_guard` / `has_allow_staging_apply`) e **revisão humana** (inclui 1 × `official_link_only` + nota WAF/Incapsula), coerente com **ready_with_notes**.
