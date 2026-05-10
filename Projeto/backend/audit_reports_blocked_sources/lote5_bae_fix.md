# Lote 5 — correção `bae_systems_suppliers`

## Contexto

No lote 5, `bae_systems_suppliers` tinha **0 brutos**: `baesystems.com` devolve **403/Incapsula** a pedidos simples; o `scrape_html_portal` não via âncoras úteis. O **portal oficial HICX** (`baesystems.hicx.net`) responde com HTML completo em muitos ambientes.

## Alterações

| Ficheiro | Descrição |
|----------|-----------|
| `bae_systems_suppliers/bae_harvest.py` | Colheita direta das páginas HICX (`discovery-login`, `index`); texto com `BeautifulSoup`; stub **factual** para `.../responsible-supply-chain` quando o GET corporativo falha (sem inventar corpo). |
| `bae_systems_suppliers/main_bae_systems_suppliers.py` | Duas seeds corporativas + `merge_bae_items` após `scrape_html_portal`; `allowed_domains` inclui `hicx.net`. |
| `CORE/official_link_only.py` | Allowlist **`bae_systems_suppliers`** (`baesystems.com`, `hicx.net`); critério de oportunidade alargado **só para esta fonte** (supplier, registration, hicx, …); barreira técnica inclui `bae_baesystems_waf_stub` e métodos de manifest/curadoria já usados noutras fontes. |
| `CORE/taxonomy_filtros.py` | Ramo **`bae_systems_suppliers`**: `origem_portal` BAE Systems, `regiao` Internacional, `idioma_original` en, `curadoria_referencia` `lote5_bae_fix`, `validacao_status` por tipo de URL/método. |

**Não feito (pedido):** alterar `opportunity_gate` global; loader apply; Supabase; migrations; `source_readiness.json`.

## `official_link_only`

Um item (URL corporativa UK) usa **`extraction_mode: official_link_only`** com `access_reason` coerente com **WAF/403**, porque o conteúdo útil não foi obtido por HTML vivo e a entrada cumpre a allowlist local (link oficial, ação inferível por URL + nota factual).

## Comandos executados

```text
python bae_systems_suppliers/main_bae_systems_suppliers.py
python scripts/retransform_all.py --sources bae_systems_suppliers --dry-run --output-dir audit_reports_blocked_sources/lote5_fix_bae
python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote5_fix_bae/standardized --output-dir audit_reports_blocked_sources/lote5_fix_bae_semantic
python scripts/audit_docs_pipeline.py --sources bae_systems_suppliers --output-dir audit_reports_blocked_sources/lote5_fix_bae_docs
```

## Resultados

| Métrica | Valor |
|--------|-------|
| Itens brutos | 3 |
| Transformados | 3 |
| Rejeitados | 0 |
| `official_link_only` (quick audit) | 1 |
| PDFs / documentos | 0 (sem perdas na auditoria de docs) |

### Auditoria semântica

`audit_semantic_summary.json` reporta `publico_alvo_sem_evidencia` × 3; na prática `calibrate_corporate_supplier_sources_extras` preenche `publico_alvo` — tratar como **nota de auditoria** até alinhar a regra do script.

### Artefactos

- Diagnóstico: `lote5_bae_diagnostico.md`, `lote5_bae_diagnostico.json`, `lote5_bae_examples.json`
- Pipeline: `audit_reports_blocked_sources/lote5_fix_bae/`, `lote5_fix_bae_semantic/`, `lote5_fix_bae_docs/`

## Readiness recomendado (tarefa 10)

**`ready_with_notes`**

- Conteúdo útil e **oficial** (HICX + URL corporativa documentada).
- **WAF** na raiz corporativa e **1/3** em `official_link_only` → não é `ready` pleno.
- Não **`blocked`**: há ação concreta para fornecedor (registo + portal).
- **`needs_manual_review`**: opcional se a política interna exigir zero `official_link_only`; não é obrigatório dado allowlist explícita e link verificável.
- **`fora_de_escopo`:** não.

---

*Atualização de `config/source_readiness.json` fica à curadoria manual, conforme pedido.*
