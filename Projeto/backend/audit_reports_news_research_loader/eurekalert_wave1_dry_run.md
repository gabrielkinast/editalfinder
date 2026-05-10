# EurekAlert Wave 1 — build de payloads (sem Supabase)

- Gerado: `2026-05-09T14:00:42Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized\eurekalert_science_filtered_standardized.json`
- Linhas entrada: **1**
- Após dedupe: **1** (removidos **0**)

## Resumo (entrada)

- `missing_summary` (entrada): **0**
- Sem data (entrada): **0**

## Payloads

- `eurekalert_wave1_payload_noticia.json`: **0**
- `eurekalert_wave1_payload_pesquisa.json`: **1**
- `eurekalert_wave1_review_candidates.json`: **0**
- `eurekalert_wave1_rejected.json`: **0**
- Excluídos qualidade: **0**
- Excluídos validação loader: **0**

## Apto para staging (heurístico)

- Volume útil (notícia+pesquisa) ≥ 1: **True**
- `readiness_apply_staging.ok`: **True** — ainda **sem apply** neste fluxo.

## Dry-run loader (sem apply)

```
python scripts/load_news_research_sources.py --dry-run --staging --source eurekalert_science_filtered --input-dir audit_reports_news_research_loader --wave eurekalert_wave1
```

Após correr o comando acima, ver `audit_reports_news_research_loader/load_news_research_summary.json` → campo `errors_count` (objetivo **0** antes de qualquer apply).
