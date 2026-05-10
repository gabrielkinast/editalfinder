# Lote 2 — Diagnóstico NATO DIANA (`nato_diana`)

## Resumo executivo

| Métrica | Valor |
|--------|------:|
| Brutos | **2** |
| Transformados | **2** |
| Rejeitados | **0** |
| Incompletos | **1** |
| Suspeitos | **0** |
| Qualidade média | **79.0** |
| Flags semânticas (após ajuste) | **nenhuma** |

## Diagnóstico inicial

### Problemas anteriores

1. **`fallback_public_index`** + item genérico em **`challenges.html`** (hub, não desafio concreto).
2. Entrada **NATO Innovation Fund (`nif.fund`)** misturada com a fonte DIANA (organização distinta).
3. **`diana.nato.int`** costuma responder **403 Cloudflare** a clientes HTTP simples, pelo que o scrape HTML falha sem contornar CAPTCHA/bot check.

### Correções aplicadas

- **`nato_diana/main_nato_diana.py`**
  - Listagens apenas **`diana.nato.int`** (`challenges.html`, `faq.html`).
  - Filtro do scrape: **não** guardar a página-índice `/challenges.html` como item detalhado vindo do HTML (o curated pode usar esse URL como referência oficial do desafio).
  - **Sem** `fallback_public_index`; se não houver itens scrapeados → **`curated_official_public_brief`** com texto alinhado à **FAQ pública** DIANA (desafio em destaque + FAQ programa), prazo **2026-05-05** para o desafio citado, código **`DIANA-WARFIGHTERS-2026`**.
  - **Removido NIF** do output desta fonte.
- **`CORE/taxonomy_filtros.py`** — `calibrate_nato_diana_extras`: `tipo_oportunidade`, `tipo_recurso`, `perfil_ideal`, `setor_estrategico` com contexto OTAN; **cibersegurança** só com lista forte (não usar “security” isolado); limpeza de `area_tecnologica` fraca em ciber.
- **`CORE/transformer.py`** — `_nato_diana_soft_continue` + categoria de gate local.
- **`CORE/noise_filter.py`** — `diana.nato.int` → tipo de conteúdo coerente (`chamada_publica` no detetor).
- **`scripts/audit_semantic_classification.py`** — isenção **`fonte_defesa_sem_defesa`** para `nato_diana` quando o texto traz marcadores **defence/defense/NATO/DIANA/military/allied/warfighter/dual_use** (evita falso positivo por léxico PT-only).

## Natureza dos links

| URL | Interpretação |
|-----|----------------|
| `…/challenges.html` | Portal oficial de **challenges** / candidaturas (item curado = desafio concreto + remissão ao portal). |
| `…/faq.html` | **Programa / FAQ** oficial (orientação; não é notícia solta). |

Não são “páginas genéricas” no sentido antigo (fallback único); são URLs canónicos OTAN com conteúdo editorial curado a partir de material público.

## Tipos pedidos × observado

| Tipo | Neste lote |
|------|------------|
| challenge | Sim (Warfighters). |
| programa | Sim (FAQ agregador). |
| accelerator | Apenas como **subtema** textual; sem URL dedicada scrapeada. |
| test_centre | Não evidenciado — **não inventado**. |
| dual_use / defence_innovation | Presente no texto / setor calibrado com contexto OTAN. |
| notícia / genérica | Evitado (sem fallback de índice). |

## Pipelines

- `audit_reports_blocked_sources/lote2_fix_nato_diana/`
- `…/lote2_fix_nato_diana_semantic/` — flags totais vazias após ajuste.
- `…/lote2_fix_nato_diana_docs/` — 0 PDFs; 0 perdas.

## Readiness recomendado

**`ready_with_notes`** (não atualizar `source_readiness.json` aqui).

**Motivos:** há transformados > 0; conteúdo alinhado a **challenges/programa** reais DIANA; classificação coerente; **sem** ciber indevida por regra fraca; semântica limpa.

**Notas obrigatórias:** poucos itens (**2**) enquanto o **Cloudflare** impedir scrape; brief curado deve ser **revisado/atualizado** quando novos desafios forem anunciados; segundo item **sem prazo** estruturado; **sem PDFs** na coleta.

**`needs_manual_review`** se a política de produto **não** aceitar entradas `curated_official_public_brief`.

**`ready` pleno** exigiria scrape ou feed estável sem bloqueio, mais densidade de oportunidades e documentos quando existirem.

---

Ficheiros: `lote2_nato_diana_diagnostico.json`, `lote2_nato_diana_examples.json`.
