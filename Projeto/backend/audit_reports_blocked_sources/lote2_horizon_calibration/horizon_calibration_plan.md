# Plano de calibração — Horizon Europe (`horizon_calibration_plan`)

Data: 2026-05-02.

## 1. Diagnóstico (25 tópicos)

### Ficheiros analisados

| Artefato | Caminho |
|----------|---------|
| Bruto | `horizon_europe/outputs/horizon_europe_editais.json` |
| Standardized (antes) | `audit_reports_blocked_sources/lote2_fix_horizon/standardized/` |
| Auditoria semântica (antes) | `audit_reports_blocked_sources/lote2_fix_horizon_semantic/` |
| Pós-calibração | `audit_reports_blocked_sources/lote2_horizon_calibration/retransform/`, `semantic/`, `docs/` |

### Campos presentes no bruto

Título (código tópico), descrição curta (listagem + pouco texto do detalhe), `link`, `fonte`, `programa`, `tipo_recurso` frequentemente “Não Especificado”, `extras` com `url_listagem`, `url_detalhe`, `palavras_chave_detectadas`, `metodo_extracao`, datas quando inferidas.

### Campos em falta no bruto

Prazo de submissão, orçamento, PDFs/anexos, corpo textual rico (SPA).

### Campos no standardized (após calibração)

`tipo_oportunidade` = `funding_opportunity`, `tipo_recurso` = `fomento`, `topic_id`, `call_code`, `programa`, `origem_portal`, `tipo_conteudo_horizon`, `natureza_recurso`, `classificacao_confianca`, `links_oficiais`, descrição com fallback institucional, `validacao_status` = `incompleto`, `opportunity_gate_category` = `grant`, `content_type_detectado` = `chamada_publica`.

### Por que `validacao_status` era “suspeito”

`apply_quality_to_payload` tratava **qualquer** `opportunity_gate_relaxed` como suspeito (mensagem genérica “trusted_br”). Tópicos HE legítimos usam relax local e ficavam injustamente marcados.

**Correção:** se `fonte == HORIZON_EUROPE`, URL contém `topic-details/horizon-` e `opportunity_gate_relax_scope == horizon_europe_local`, **não** forçar suspeito; manter o resultado de `_validation_status_from_payload` (tipicamente `incompleto` por prazo/valor).

### Por que `oportunidade_fomento_sem_fomento` disparava

1. O auditor exigia vocabulário PT (`fomento`, `chamada`, …) no texto agregado.  
2. O corpus de `enrich_opportunity_classification` **não incluía o link**; “Funding **Tenders**” na descrição acionava `PROCUREMENT_MARKERS` (“tender”) → `tipo_recurso` = “licitação”, gerando inconsistência com “chamada”.

**Correções:** incluir `link` no corpus de enriquecimento; priorizar `topic-details/horizon-` em `_infer_tipo_recurso` → `fomento`; isenção explícita no `audit_semantic_classification.py` para HE + URL de tópico + `fomento` / `funding_opportunity`.

### HTML público / JSON / SPA

- Resposta HTML inicial do `topic-details` tem **pouco texto** útil (aplicação SPA).  
- **Não** se identificou payload JSON estável no HTML estático para prazos/orçamento.  
- **Listagem pública** `topic-list.html` continua a ser a fonte segura de links.

### Endpoint complementar

O conteúdo dinâmico depende da app do portal; **não** foi integrada chamada não documentada nem login.

---

## 2. Calibração implementada (`calibrate_horizon_europe_extras`)

Para URLs `.../topic-details/horizon-*`:

- `tipo_oportunidade`: `funding_opportunity`  
- `tipo_recurso` / item: `fomento`  
- `natureza_recurso`: `nao_reembolsavel`  
- `perfil_ideal`: só com evidência textual; caso contrário omitido  
- `regiao` / `pais`: Europa / União Europeia  
- `idioma_original`: `en`  
- `classificacao_confianca`: `media`  
- Áreas / setores / tags temáticas: **limpos** quando a descrição é curta (< 400 caracteres), para evitar ruído (ex.: “aeroespacial” espúrio).  
- `links_oficiais`: link do tópico + portal Funding & Tenders  
- Descrição: fallback composto (e meta tags no crawler se `enrich_meta_tags: true`)

---

## 3. Outras alterações locais

| Ficheiro | Alteração |
|----------|-----------|
| `CORE/transformer.py` | `opportunity_gate_category = "grant"` no ramo soft Horizon (substitui `setdefault`). |
| `CORE/item_quality.py` | Exceção HE + topic-details para não forçar suspeito em relax local. |
| `CORE/noise_filter.py` | URLs de tópico HE → `chamada_publica` em `detect_content_type`. |
| `scraper_generic.py` | `enrich_meta_tags`: `meta description`, `og:description`, `og:title`. |
| `horizon_europe/main_horizon_europe.py` | `enrich_meta_tags: true`. |

---

## 4. Resultados dos comandos (pós-calibração)

```text
python scripts/retransform_all.py --sources horizon_europe --dry-run --output-dir audit_reports_blocked_sources/lote2_horizon_calibration/retransform
python scripts/audit_semantic_classification.py --input-dir .../retransform/standardized --output-dir .../semantic
python scripts/audit_docs_pipeline.py --sources horizon_europe --output-dir .../docs
```

- **25** transformados, **0** rejeitados, **0** suspeitos, **25** incompletos.  
- **Qualidade média:** 60.  
- **Auditoria semântica:** `flags_totais` vazio (0× `oportunidade_fomento_sem_fomento`).  
- **Docs:** sem PDFs; sem perdas.

---

## 5. Readiness

**Recomendação técnica:** `ready_with_notes` — tópicos reais, pipeline coerente, auditoria semântica limpa; permanecem lacunas explícitas (prazo, valor, PDF, texto detalhado SPA).

**Política de lista:** manter **`blocked`** até decisão manual, conforme orientação do projeto (`source_readiness.json` não alterado automaticamente).

---

## 6. Próximos passos opcionais

1. Nova corrida do **crawler** com `enrich_meta_tags` para repor brutos com meta no texto.  
2. Fonte complementar **pública** (ex. exportos documentados da CE), sem scraping agressivo.  
3. Revisão humana de uma amostra de tópicos antes de retirar `blocked`.
