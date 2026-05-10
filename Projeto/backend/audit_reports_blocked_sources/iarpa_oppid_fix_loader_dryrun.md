# IARPA — correção oppId / Grants.gov — dry-run do loader

Data: 2026-05-02

## Problema 1 — `source_readiness.json` não é mais sobrescrito por defeito

- **`load_ready_sources.py`** deixou de chamar `_save_source_readiness_config` em cada dry-run/apply.
- O slice calculado a partir de `readiness_for_loader.json` é gravado apenas em **`audit_reports_loader_ready/readiness_derived_slice.json`**.
- O resumo JSON inclui `readiness_config_write` (`written: false` por defeito) e `readiness_derived_slice_path`.
- **`--write-readiness-config`**: merge conservativo com o ficheiro em disco (`_merge_readiness_conservative`) e gravação explícita em `config/source_readiness.json`.
- Relatórios **`audit_reports_loader_ready/readiness_config_write_guard.{md,json}`** são atualizados no fim da execução.

### Verificação (execução deste lote)

- SHA-256 de `config/source_readiness.json` **inalterado** antes/depois do dry-run: `CC441738BEE545F2DF1223D785EF332021897C9ADFC5194B06814A4F7A9CBE50`.
- `badesul`, `nato_diana`, `horizon_europe`, `erc`, `doe_arpae`, `iarpa` continuam em **`ready_with_notes`**.

## Problema 2 — oppId e metadados Grants.gov no standardized

### Código

- **`transformer.py`**: merge do `build_defense_extras` com **`_extras_apply_patch_preserve_nonempty`** (não substituir valores úteis por strings vazias).
- **`_enrich_grants_gov_catalog_extras`**: extrai `oppId` da query string; preenche `grants_gov_opp_id`, `codigo_oportunidade`, `numero_chamada` (via regex na descrição se necessário), `grants_gov_status`, `agency`, `origem_portal`.
- **`iarpa/main_iarpa.py`**: `agency`, `grants_gov_opp_id`, `grants_gov_status`; `numero_chamada` só quando a API devolve número (sem inventar).

### Retransformação

- Pasta: `audit_reports_blocked_sources/lote2_fix_iarpa_oppid/`
- **8/8** itens com `codigo_oportunidade`, `numero_chamada`, `grants_gov_opp_id`, `agency`, `grants_gov_status` preenchidos (ex.: oppId `336190`, número `W911NF-22-S-0002`).

## Dry-run do loader (input novo)

```text
python scripts/load_ready_sources.py --dry-run --sources iarpa --exclude-blocked --input-dir audit_reports_blocked_sources/lote2_fix_iarpa_oppid/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

| Métrica | Valor |
|--------|------:|
| would_upsert | 8 |
| mapping_errors | 0 |
| critical_empty_items | 0 |
| readiness_config_write.written | false |

## Apply / Supabase / gate

- **Apply** não executado.
- **Gate** global não alterado.
- **Migrations** não aplicadas.
