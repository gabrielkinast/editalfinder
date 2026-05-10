# Recovery D.1 — Loader dry-run (QA)

- mapping_errors_total: **0**
- critical_empty_items_total: **0**
- itens standardized: **26**

## Verificação Recovery D.1

```json
{
  "itens_total": 26,
  "faq_help_support_url_heuristic": 0,
  "login_isolado_warnings": 0,
  "validacao_suspeito_top_level": 0,
  "setor_estrategico_gt3": 0,
  "titulo_generico_suppliers_sem_normalizacao": 0,
  "capabilities_na_colecao": 0,
  "gdls_lav_na_colecao": 0,
  "criterios_apply": {
    "sem_faq_help": true,
    "sem_login_isolado_forte": true,
    "sem_capabilities_fantasma": true,
    "sem_lav_produto": true,
    "suspeito_zero_ou_explicado": true,
    "mapping_loader_zero": true
  }
}
```

Ver também `load_ready_summary.md` na pasta do loader.
