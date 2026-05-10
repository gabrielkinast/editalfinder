# EurekAlert Wave 1 — curadoria (política revisada)

**Data:** 2026-05-05 · **JSON:** `eurekalert_wave1_curadoria.json`

## Correção conceitual

- **Defesa biológica / agro** (“plant defense”, immunity, salicylic acid, etc.) **não** é automaticamente ruído: pode ir para `public.pesquisa` como **pesquisa científica**.
- **Não** classificar como defesa militar / dual-use **sem** evidência no texto.
- **“Defense” isolado** sem contexto bio nem militar → **`review_manual`** no build (não rejeição automática no crawl).

## Onde está implementado

| Camada | Ficheiro | O quê |
|--------|----------|--------|
| Crawl | `scripts/crawl_news_research_sources.py` | Sem exclusão automática por defense biológico. |
| Build | `scripts/build_eurekalert_wave1_payloads.py` | Taxonomia (`tipo_pesquisa_cientifica`, áreas), `extras.defense_semantica`, revisão `defense_contexto_insuficiente_review_manual`. |

## Os 3 itens (payload pesquisa)

### 1 — IA + sequências / ancestralidade

| Campo | Valor |
|--------|--------|
| Link | https://www.eurekalert.org/news-releases/1126804 |
| matched_keywords | artificial intelligence |
| Passou porque | Tema IA explícito + genómica. |
| Classificação | **pesquisa_util** |
| Taxonomia | `biologia` · `ia`, `computacao`, `biotecnologia` · `bioeconomia` · `defense_semantica: nao_aplicavel` |

---

### 2 — Plantas / crescimento e “defense”

| Campo | Valor |
|--------|--------|
| Link | https://www.eurekalert.org/news-releases/1126830 |
| matched_keywords | defense |
| Passou porque | Keyword “defense” em **contexto de imunidade vegetal / hormonas**, não militar. |
| Classificação | **pesquisa_util** (biológica/agro, não ruído semântico) |
| Taxonomia | `ciencias_agrarias` · `agrobiotecnologia`, `biotecnologia` · `agricultura`, `bioeconomia` · `defense_semantica: biologica_agro` |

**Sem** `setor_estrategico = defesa` militar.

---

### 3 — Aeronáutica / turbulência / mísseis

| Campo | Valor |
|--------|--------|
| Link | https://www.eurekalert.org/news-releases/1126833 |
| matched_keywords | aircraft, engineering |
| Passou porque | Engenharia aeronáutica; texto refere **mísseis** e aeronaves rápidas. |
| Classificação | **pesquisa_util** |
| Taxonomia | `engenharia` · `aeroespacial`, `engenharia`, `defesa` · `aeroespacial`, `defesa` · `defense_semantica: militar_dual_use` |

---

## Artefatos regenerados

- `eurekalert_wave1_payload_pesquisa.json` — **3** linhas, taxonomia nova.
- `eurekalert_wave1_rejected.json` — vazio.
- `eurekalert_wave1_dry_run.json` — regenerado pelo build.

## Recomendação

| Campo | Valor |
|--------|--------|
| **apply_staging_ok** | **true** (subir os 3 registos curados; sem apply automático aqui) |
| Fonte | Manter **experimental_wave** até mais ondas estáveis |

Dry-run loader: confirmar `errors_count == 0` em `load_news_research_summary.json`.
