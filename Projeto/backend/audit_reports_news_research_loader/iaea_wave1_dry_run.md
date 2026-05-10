# IAEA Wave 1 — build de payloads (sem Supabase)

- Gerado: `2026-05-09T14:00:41Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized\iaea_news_publications_standardized.json`
- Linhas entrada: **45**
- Após dedupe: **45** (removidos **0**)

## Resumo (entrada)

- `missing_summary` (entrada): **26**
- Sem data (entrada): **0**

## Payloads

- `iaea_wave1_payload_noticia.json`: **5**
- `iaea_wave1_payload_pesquisa.json`: **14**
- `iaea_wave1_review_candidates.json`: **2** (não carregados como notícia/pesquisa)
- `iaea_wave1_rejected.json`: **24**
- Excluídos qualidade: **24**
- Excluídos validação loader: **0**

## Apto para staging (heurístico)

- Volume útil (notícia+pesquisa) ≥ 1: **True**
- `readiness_apply_staging.ok`: **True** — ainda **sem apply** neste fluxo.

## Dry-run loader (sem apply)

```
python scripts/load_news_research_sources.py --dry-run --staging --source iaea_news_publications --input-dir audit_reports_news_research_loader --wave iaea_wave1
```

Após correr o comando acima, ver `audit_reports_news_research_loader/load_news_research_summary.json` → campo `errors_count` (objetivo **0** antes de qualquer apply).
