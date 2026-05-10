# Rheinmetall suppliers — loader dry-run (`ready_with_notes`)

## Decisão

`rheinmetall_suppliers` em **ready_with_notes** (não ready pleno), aprovado na curadoria Rheinmetall.

## Diff / resumo de readiness

### `config/source_readiness.json`

- **Removido** de `needs_manual_review`.
- **Incluído** em `ready_with_notes` (após `pncp_defesa`, antes de `saude`).

### `audit_reports_retransform/readiness_for_loader.json`

- **Contagens:** `pronto_com_observacoes` = 66; `precisa_revisao_manual` = 7.
- **Removido** de `fontes_para_revisao`.
- **Incluído** em `fontes_prontas_para_loader` (necessário para `--exclude-blocked` selecionar a fonte).

### Artefato standardized

Origem: `audit_reports_blocked_sources/lote5_rheinmetall_curated/standardized/rheinmetall_suppliers_standardized.json`  
Destino: `audit_reports_retransform/standardized/rheinmetall_suppliers_standardized.json`

## Comando dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources rheinmetall_suppliers --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Resultado do dry-run

| Métrica | Valor |
|--------|-------|
| `id_execucao` | `d2db4edc-8fc2-4881-a7ab-2603017f11f4` |
| `data_auditoria` (summary) | `2026-05-03T18:55:10Z` |
| `sources_selected` | 1 |
| `itens_standardized_total` | 2 |
| `would_upsert_total` | 2 |
| `would_ignore_total` | 0 |
| `mapping_errors_total` | 0 |
| `critical_empty_items_total` | 0 |
| `apply_requested` | false |

Relatório completo: `audit_reports_loader_ready/load_ready_summary.json`.

## Verificação (checklist)

| Critério | Status |
|----------|--------|
| 2 itens | OK |
| `would_upsert` = 2 | OK |
| `mapping_errors` = 0 | OK |
| `critical_empty` = 0 | OK |
| `tipo_oportunidade` | `cadastro_fornecedor` + `supplier_portal` |
| `tipo_recurso` | `oportunidade_fornecedor` (ambos) |
| `perfil_ideal` | `fornecedor`, `empresa` (ambos) |
| `validacao_status` (nível do **item**) | `incompleto` / `acesso_limitado` |
| `origem_portal` | `Rheinmetall` (ambos) |
| `idioma_original` | `en` (ambos) |
| Setor defesa só por nome | `setor_estrategico` vazio |
| Página institucional vazia | Não — URLs concretas (become-a-supplier + Ivalua) |

**Nota:** Em `extras`, `validacao_status` permanece `suspeito` nos dois registros; o campo no **nível do item** (`validacao_status` fora de `extras`) reflete `incompleto` e `acesso_limitado`, alinhado à decisão de curadoria.

## Escopo explícito desta sessão

- Não foi executado `--apply`.
- Sem alterações no Supabase.
- Sem alteração ao gate global do projeto.

## Recomendação para staging

O dry-run está **limpo** para carga: dois upserts previstos, sem erros de mapeamento nem campos críticos vazios no agregado do loader. **Recomenda-se** aplicar em **staging** apenas quando a equipa quiser promover a fonte, com fluxo controlado (por exemplo `EDITALFINDER_ALLOW_STAGING_APPLY` / flags do ambiente conforme `environment_guard` no summary) e revisão humana pós-carga, dado o perfil `ready_with_notes` e o segundo item com descrição curta / portal com login.
