# Onda A Brasil — `ready_with_notes` + dry-run do loader

**Data:** 2026-05-05  

## Promoção de readiness

| Fonte | Destino |
|--------|---------|
| `bnb` | `ready_with_notes` |
| `banco_da_amazonia` | `ready_with_notes` |
| `bdmg` | `ready_with_notes` |
| `desenvolve_sp` | **sem promoção** (continua `needs_manual_review` — não está em `fontes_prontas_para_loader`) |
| `agerio` | **sem promoção** (idem) |

### Diff resumido

1. **`config/source_readiness.json`**  
   - Inclusão de `banco_da_amazonia`, `bdmg`, `bnb` em `ready_with_notes` (lista ordenada).  
   - Garantia de que não figuram em `blocked`, `needs_manual_review` nem `reprocess_after_fix`.

2. **`audit_reports_retransform/readiness_for_loader.json`**  
   - Acréscimo das três fontes em `fontes_prontas_para_loader` (no bloco **pronto_com_observacoes**: posições após as 8 de `pronto_para_loader`).  
   - `status_distribution.pronto_com_observacoes`: **68 → 71**.  
   - `fontes_total`: **94 → 97**.  
   - `desenvolve_sp` e `agerio` **não** foram adicionados.

### Standardized copiados

Origem: `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix/standardized/`  

Destino: `audit_reports_retransform/standardized/`

- `bnb_standardized.json`  
- `banco_da_amazonia_standardized.json`  
- `bdmg_standardized.json`  

---

## Dry-run do loader

```bash
python scripts/load_ready_sources.py --dry-run --sources bnb,banco_da_amazonia,bdmg --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

Relatório completo gerado pelo script: `audit_reports_loader_ready/final_dry_run_before_staging.json`

### Métricas principais

| Métrica | Valor |
|---------|------:|
| `sources_selected` | **3** |
| `itens_standardized_total` | **77** |
| `would_upsert_total` | **77** |
| `would_ignore_total` | 0 |
| `mapping_errors_total` | **0** |
| `critical_empty_items_total` | **0** |
| `documentos_perdidos_no_payload_total` | **0** |
| `validacao_status_preserved_items_total` | 77 |
| `qualidade_dado_preserved_items_total` | 77 |
| `destination_counts_total` | `{ "edital": 77 }` |
| `canonical_skipped_total` | 0 |

*(77 = 24 BNB + 26 BASA + 27 BDMG, alinhado ao último standardized do lote.)*

### Verificações pedidas (checklist)

- **3 fontes** selecionadas; **77** itens com upsert simulado **>** 0.  
- **0** erros de mapping; **0** itens críticos vazios; **0** documentos perdidos no payload.  
- Amostra automatizada nos JSON copiados: **0** itens com `setor_estrategico` **> 3**; **0** `subvencao` sem evidência textual.  
- Campos `validacao_status` e `qualidade_dado` preservados em todos os itens (totais do relatório).  
- **Apply** não executado; **Supabase** não alterado pelo pedido; **`opportunity_gate` global** não modificado.

---

## Recomendação para staging

O dry-run está **consistente** com carga segura (mapping limpo, documentos preservados, destino `edital`).

Para **aplicar em staging** (quando a equipa aprovar), usar explicitamente `--apply --staging` com o mesmo filtro de fontes e caminhos — **não** foi executado nesta tarefa. Consultar `environment_guard` em `final_dry_run_before_staging.json` antes do primeiro apply (credenciais / flag de staging).
