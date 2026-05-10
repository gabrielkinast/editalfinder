# DARPA News — build de payloads (Onda 3, conservador)

- Gerado: `2026-05-09T14:00:40Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized\darpa_news_standardized.json`
- Linhas entrada: **10**
- Após dedupe: **10** (removidos **0**)

## Payloads

- `darpa_news_wave1_payload_noticia.json`: **8**
- `darpa_news_wave1_payload_pesquisa.json`: **2**
- `darpa_news_wave1_review_candidates.json`: **0** (não carregados pelo loader)
- `rejected_noise`: **0**
- Excluídos qualidade DARPA: **0**
- Excluídos validação loader: **0**

## Apto apply staging (heurístico)

- **True** — ver `readiness_apply_staging` em `darpa_news_wave1_dry_run.json`.

## Dry-run loader (sem apply)

```
python scripts/load_news_research_sources.py --dry-run --staging --source darpa_news --input-dir audit_reports_news_research_loader --wave darpa_news_wave1
```
