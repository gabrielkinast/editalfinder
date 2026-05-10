# EurekAlert — diagnóstico Wave 1

## Seeds / URLs usados

- `https://www.eurekalert.org/news-releases/browse`

## Contagens (crawl + filtros)

- Itens extraídos do feed/listing (antes do filtro temático, incl. duplicados de link contados no loop): **12**
- Passaram require_any + exclude (e limites IAEA N/A): **3**
- Rejeitados `require_any_keyword` (nenhum termo forte no blob): **7**
- Rejeitados `exclude_keywords`: **2** (heurística medicina/saúde genérica: **1**)

## Standardized (após crawl)

- Itens no ficheiro standardized: **3** (`raw_total` no meta: **3**)
- Sem `data_publicacao`: **0**

## Tipo de conteúdo (standardized)

- `pesquisa`: **3**

## Termos fortes (matches no filtro; top 30)

- `aircraft`: **1**
- `engineering`: **1**
- `defense`: **1**
- `artificial intelligence`: **1**

## Volume

- Passaram filtro temático (≤ max_items **30**): **3** → heurística aceitável: **True**
- Build local (`eurekalert_wave1_dry_run.json`): notícias **0**, pesquisas **3**

---

Gerado por `scripts/generate_eurekalert_wave1_diagnostico.py`.