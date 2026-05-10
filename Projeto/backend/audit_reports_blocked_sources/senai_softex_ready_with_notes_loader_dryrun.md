# SENAI e Softex — `ready_with_notes` e dry-run do loader

**Execução loader:** `215f7952-5b51-4dd8-92a5-4134c9bb75d0` — `2026-05-02T00:00:43Z` — modo **dry-run** (sem apply).

## 1. Readiness — diff / resumo

### `audit_reports_retransform/readiness_for_loader.json`

- **Removidos** de `fontes_bloqueadas_temporariamente`: `senai`, `softex`.
- **Acrescentados** ao fim de `fontes_prontas_para_loader`: `senai`, `softex`.
- **`status_distribution`:** `pronto_com_observacoes` **9 → 11**; `bloquear_temporariamente` **22 → 20**.

### `config/source_readiness.json`

Regenerado pelo `load_ready_sources` a partir do readiness acima:

- **`senai`** e **`softex`** em **`ready_with_notes`** (lista ordenada; aparecem junto de `mapa` … `wellcome`).
- **Já não** estão em **`blocked`** (lista bloqueada passa a terminar em `science_scraper`).

### Standardized servido ao loader

Foram copiados para `audit_reports_retransform/standardized/` (entrada por defeito do script):

- `senai_standardized.json`
- `softex_standardized.json`  

(origem: calibração em `audit_reports_blocked_sources/lote1_fix_senai_softex/standardized/`).

## 2. Comando

```text
python scripts/load_ready_sources.py --dry-run --sources senai,softex --exclude-blocked
```

## 3. Resultado do dry-run (agregado)

| Métrica | Valor |
|--------|------:|
| Itens standardized | **24** |
| `would_upsert` | **24** |
| `would_ignore` | **0** |
| Erros de mapeamento | **0** |
| `critical_empty` | **0** |
| Itens com docs (entrada) | **22** (todos SENAI) |
| Docs preservados | **22** |
| Docs perdidos | **0** |
| Itens com `pdf_url` na entrada | **22** (SENAI) |
| `pdf_url` preservados | **22** |
| `validacao_status` preservado | **24** |
| `qualidade_dado` preservado | **24** |

Detalhe por fonte: `audit_reports_loader_ready/load_ready_by_source.json`.

## 4. Verificações pedidas

| Verificação | SENAI (22) | Softex (2) |
|-------------|------------|-------------|
| Standardized / `would_upsert` | 22 / 22 | 2 / 2 |
| Mapeamento | 0 erros | 0 erros |
| Documentos | Preservados (22 com docs) | 0 docs no bruto; 0 perdas |
| `pdf_url` “inventado” | 22 com URL (links reais extraídos da página de categoria) | 0 |
| `tipo_oportunidade` | 18 `licitacao`, 4 `supplier_portal` (rever taxonomia vs “programa/chamada”) | 2 `noticia_institucional` |
| `tipo_recurso` | Subvenção (Não Reembolsável) ×22 | `fomento` ×2 |
| `perfil_ideal` | Vazio em todos no JSON analisado | Vazio |
| `validacao_status` | `incompleto` ×22 | `suspeito` ×2 |
| `qualidade_dado` | Preservada no loader | Preservada |
| Natureza SENAI | **100%** URLs com `/categoria/` — **oportunidades agregadas** por linha da Plataforma Inovação | — |
| Descrição Softex | — | **82–118** caracteres — **insuficiente** para classificação rica |

O resumo do loader não inclui `perfil_ideal` nos contadores `fields_*` porque está vazio nos itens atuais.

## 5. Apply e Supabase

- **Apply:** não executado (`apply_requested: false`, guard `missing_staging_flag`).
- **Supabase:** apenas leitura/diagnóstico habitual do script; sem migration nem carga aplicada.

## 6. Recomendação para staging

**Pode aplicar em staging** do ponto de vista do **dry-run** (24 upserts, sem erros de mapeamento, sem perda de documentos SENAI).

**Condições recomendadas antes do primeiro apply:**

1. Aceitar **SENAI** como registros de **categoria agregada** e rever ** `tipo_oportunidade`** (`licitacao` / `supplier_portal` vs programa/chamada).
2. **Softex:** tratar como **notícia/programa** com texto curto e `suspeito`; considerar enriquecer descrição no crawler.
3. Preencher ou aceitar **`perfil_ideal`** vazio até próximo ciclo de taxonomia.
4. Usar a **flag explícita de staging** prevista no projeto quando for rodar apply real.

JSON espelho: `audit_reports_blocked_sources/senai_softex_ready_with_notes_loader_dryrun.json`.
