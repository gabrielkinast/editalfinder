# Lote 1 — `plataforma_industria`: diagnóstico e correções

**Escopo:** apenas esta fonte. **Não** alterado: `opportunity_gate` global, loader apply, Supabase, migrations, `source_readiness.json` / `readiness_for_loader.json`.

---

## 1. Diagnóstico inicial

| Métrica | Antes | Depois |
|--------|------:|-------:|
| Itens brutos | **1** (fallback índice) | **23** |
| Transformados | 0 (histórico) | **23** |
| Rejeitados | 1 (gate no índice) | **0** |
| `fallback_public_index` | Sim | **Não** |

**Bruto atual:** `plataforma_industria/outputs/plataforma_editais.json` — **23** URLs, todas com **`/categoria/`** da Plataforma Inovação (`portaldaindustria.com.br`), **sem** índice genérico.

**Natureza dos links:** páginas de **categoria / programa agregado** (várias chamadas/editais listados no corpo), **não** edital único, **não** notícia isolada, **não** menu/contato.

---

## 2. Paralelo com SENAI

- Mesmo **portal** e mesmo padrão **`.../plataforma-inovacao-para-industria/categoria/...`**.
- Reaproveitamento: **mesma calibração semântica** (`calibrate_portal_plataforma_inovacao_extras`) com metadado específico `extras.tipo_conteudo_plataforma_industria = categoria_plataforma_inovacao`.
- **Atenção:** URLs podem **coincidir** com as já coletadas pela fonte **senai** — convém **deduplicar por `link`** no loader ou na base.

---

## 3. Correções locais aplicadas

1. **`plataforma_industria/main_plataforma.py`:** `scrape_source` com `http_timeout`, filtros de URL, `link_path_min_depth`, exclusão de `/resultados` e `/edicoes`, keywords alargadas, **remoção do fallback** de índice.
2. **`CORE/transformer.py`:** sem `build_defense_extras` para `plataforma_industria`; **soft-continue** do gate partilhado com SENAI no portal; bloqueio explícito do **hub** sem `/categoria/`.
3. **`CORE/taxonomy_filtros.py`:** `calibrate_portal_plataforma_inovacao_extras(item, pipeline_source)` — `programa_agregado`, `tipo_recurso` de fomento industrial, `perfil_ideal` só com evidência.
4. **`scripts/audit_docs_pipeline.py`:** descoberta de `plataforma_editais.json` + robustez do MD quando há erro por fonte.

---

## 4. Evitado (verificação pós-pipeline)

- **Sem** `licitacao` / `supplier_portal` / `noticia_institucional` nos 23 itens standardized.
- **`tipo_oportunidade`:** `programa_agregado` ×23.
- **`tipo_conteudo_plataforma_industria`:** `categoria_plataforma_inovacao` ×23.

---

## 5–7. Artefactos gerados

| Etapa | Pasta / ficheiros |
|--------|---------------------|
| Retransformação (dry-run) | `audit_reports_blocked_sources/lote1_fix_plataforma_industria/` (`retransform_by_source.json`, `standardized/plataforma_industria_standardized.json`) |
| Auditoria semântica | `audit_reports_blocked_sources/lote1_fix_plataforma_industria_semantic/` |
| Auditoria documentos | `audit_reports_blocked_sources/lote1_fix_plataforma_industria_docs/` |

**Resumo semântico:** 23 itens, **0** flags semânticas agregadas.

**Resumo documentos:** preservação **0** perdas (`perdas_total: 0`); downloads PDF podem falhar no script de auditoria (ambiente), sem perda da lista de URLs no fluxo.

---

## 8. Readiness recomendada

**`ready_with_notes`** (não `ready` pleno): mesmo racional que **SENAI** — categorias agregadas, **23× `incompleto`**, qualidade média elevada mas granularidade de “um edital = um registo” não aplicável.

**`needs_manual_review`** se a política de produto **não** quiser duplicar categorias já cobertas por **senai**.

**Manter `blocked`** apenas se se decidir **não** expor categorias da plataforma como registos separados da fonte SENAI.

**Não** foi alterado `config/source_readiness.json` nesta tarefa.

---

Espelho JSON: `lote1_plataforma_industria_diagnostico.json`.
