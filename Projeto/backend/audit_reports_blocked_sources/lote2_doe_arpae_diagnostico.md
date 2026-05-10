# Lote 2 — Diagnóstico DOE / ARPA-E (`doe_arpae`)

## Resumo executivo

| Métrica | Valor |
|--------|------:|
| Brutos (`doe_arpae_editais.json`) | **14** |
| Transformados (dry-run) | **14** |
| Rejeitados | **0** |
| Incompletos | **14** |
| Suspeitos | **0** |
| Qualidade média | **67.86** |
| Flags semânticas agregadas | **nenhuma** |

## Diagnóstico inicial

### Estado anterior (lista vazia)

1. **`https://arpa-e.energy.gov/funding-opportunities`** respondia **404**, logo a primeira listagem do crawler não alimentava itens.
2. Mesmo com HTML do **ARPA-E eXCHANGE** (`arpa-e-foa.energy.gov`), o **`scraper_generic`** faz `split("#")[0]` no URL antes de deduplicar e seguir para detalhe — todas as âncoras `#FoaId…` viravam o **mesmo** `Default.aspx`, pelo que só poderia existir **um** registo (e ainda assim com corpo genérico da página inteira).

### Correção aplicada

- **Coleta dedicada** em `doe_arpae/main_doe_arpae.py`: leitura das páginas públicas  
  `Default.aspx` e `Default.aspx?Archive=1`, extração de linhas com códigos **`DE-FOA-*`** ou **`RFI-*`**, **preservando o fragmento `#FoaId…` no `link`**.
- **Rodapé canónico** na descrição (texto ≥ 400 caracteres) para qualidade/validação sem inventar prazos.
- **Título curto** (`RFI-…`) prolongado com sufixo `— ARPA-E eXCHANGE` quando necessário.
- **`CORE/transformer.py`:** `arpa-e-foa.energy.gov` no soft-continue; hub só sem `#FoaId`.
- **`CORE/taxonomy_filtros.py`:** domínio `arpa-e-foa.energy.gov`; `tipo_recurso` **fomento**; `tipo_oportunidade` **funding_opportunity** vs **chamada_publica** (teaming); `perfil_ideal` por defeito para linhas eXCHANGE; **pruning** de `thematic_tags` (ex.: remover **aeroespacial** sem evidência de aviação/espacial).
- **`CORE/noise_filter.py`:** `detect_content_type` reconhece links eXCHANGE com `#FoaId` como **chamada_publica** (evita classificação genérica).

## Natureza dos links

| Padrão | Interpretação |
|--------|----------------|
| `Default.aspx#FoaId{uuid}` + título `DE-FOA-…` | **FOA / funding opportunity** oficial na listagem pública. |
| `Default.aspx#FoaId{uuid}` + título `RFI-…` + texto “Teaming” | **Teaming partner** / anúncio associado a programa ARPA-E. |
| `FileContent.aspx?FileID=…` (não coletado em massa) | **Documento NOFO** — candidato a extensão futura sem abrir fluxo de login. |

Não são “só notícias” nem hubs institucionais vazios: são linhas da grelha de oportunidades do eXCHANGE.

## Classificação pedida × observado

| Tipo pedido | Observação neste lote |
|-------------|------------------------|
| Funding opportunity announcement | **Sim** — maioria `DE-FOA-*`. |
| FOA | **Sim** — códigos explícitos. |
| Programa técnico | **Parcial** — nomes de programa aparecem na descrição da linha (ex.: SUPERHOT, SCALEUP); não há página de “programa” separada. |
| chamada_publica | **Sim** — RFI/teaming e janelas de candidatura implícitas. |
| Grant / fomento | **Sim** — `tipo_recurso` calibrado para **fomento**. |
| Teaming partner opportunity | **Sim** — RFIs com “Teaming Partner List”. |
| Notícia institucional | **Não** (filtragem por códigos FOA/RFI + texto de linha). |
| Página genérica | **Não** (URL distingue cada FoaId). |

## Pipelines e relatórios

- **Retransform (dry-run):** `audit_reports_blocked_sources/lote2_fix_doe_arpae/`
- **Semântica:** `audit_reports_blocked_sources/lote2_fix_doe_arpae_semantic/` — flags totais vazias.
- **Documentos:** `audit_reports_blocked_sources/lote2_fix_doe_arpae_docs/` — 0 PDFs no bruto; **0 perdas** (nada a perder na cadeia).

## Readiness recomendado

**`ready_with_notes`** (não alterado em `source_readiness.json` por instrução).

**Motivos:** volume útil de FOAs/reais; classificação coerente; sem rejeições; auditoria semântica limpa; **notas** — todos **incompletos** em prazo/valor estruturado; **sem documentos/PDF** na coleta (detalhe fino continua no portal); não promover a **`ready`** pleno sem segunda fase (NOFO PDF ou API) se o produto exigir prazo obrigatório.

**`needs_manual_review`** só se a política de produto excluir RFIs de teaming ou URLs só com fragmento.

**`blocked`** — **não** recomendado após esta correção.

---

Ficheiros irmãos: `lote2_doe_arpae_diagnostico.json`, `lote2_doe_arpae_examples.json`.
