# Consolidação — lote 2 (readiness canónico alinhado)

**Data:** 2026-05-02  

## Causa do desfasamento

1. **`retransform_all.py` com `--sources`** gravava só as fontes filtradas em `audit_reports_retransform/retransform_by_source.json`, **apagando** as restantes entradas do relatório global. O `build_loader_readiness.py` lia contagens falsas (ex.: poucos brutos / 0 transformados para fontes que nem tinham sido reprocessadas).
2. **Corridas com `--output-dir` alternativo** geravam relatórios noutra pasta, deixando o canónico desactualizado.
3. O **readiness** nunca leu `standardized/` directamente: depende de `retransform_by_source.json` + risco + semântica + acesso.
4. **`iarpa`** era marcada `bloquear_temporariamente` por `crawler_fraco` + `access_http_403` **mesmo com 8 itens transformados** — a lógica tratava risco de rede como bloqueio absoluto.
5. **`sam_gov`**: linha antiga (2 brutos / 0 transformados) persistiu no ficheiro até se correr retransform só para `sam_gov` após o merge.

## Correcções feitas (código)

| Ficheiro | Alteração |
|----------|-----------|
| `scripts/retransform_all.py` | Com `--sources`, **merge** com `retransform_by_source.json` existente; idem para `standardized_old_vs_new.json`. |
| `scripts/build_loader_readiness.py` | Opções `--retransform-by-source`, `--old-vs-new`, `--risk-dir`, `--semantic-dir`, `--output-dir`. Não bloquear por `crawler_fraco` se `itens_transformados > 0`. `pronto_com_observacoes` se taxa de incompletos ≥ 85 %, ou `risco == gate_agressivo`, ou acesso limitado. `sam_gov` com `trf == 0` → bloqueio. |

## Fontes prontas (staging)

`horizon_europe`, `erc`, `doe_arpae`, `nato_diana`, `iarpa` — todas com `recomendacao_loader == pronto_com_observacoes` em `readiness_rows.json`.

## Pendente

- **`sam_gov`**: `bloquear_temporariamente` (sem transformados; API key pendente).

## Comandos executados (consolidação)

```text
python scripts/retransform_all.py --sources horizon_europe,erc,doe_arpae,nato_diana,iarpa --dry-run --output-dir audit_reports_retransform
python scripts/retransform_all.py --sources horizon_europe,erc,doe_arpae,nato_diana,iarpa --dry-run --output-dir audit_reports_retransform_lote2_ready
python scripts/retransform_all.py --sources sam_gov --dry-run --output-dir audit_reports_retransform
python scripts/build_loader_readiness.py
```

## Dry-run loader — readiness **canónico**

```text
python scripts/load_ready_sources.py --dry-run --sources horizon_europe,erc,doe_arpae,nato_diana,iarpa --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

**Resultado:** 5 fontes, 57 standardized, 57 would_upsert, 0 erros de mapeamento, 0 critical_empty, documentos/pdf/validacao/qualidade preservados como antes; **sam_gov não incluída**.

## Slice temporário

`audit_reports_blocked_sources/lote2_readiness_for_loader_apply_slice.json` → **DEPRECATED**; o canónico já cobre o caso.

## Restrições

Apply, migrations e gate global não foram alterados. Evitar assumir «sem Supabase»: o loader em dry-run pode ainda tentar append em `carga_execucao` se estiver configurado.
