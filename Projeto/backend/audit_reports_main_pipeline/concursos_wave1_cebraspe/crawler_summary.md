# Crawler piloto — Cebraspe (API PAS)

- **Fonte:** `cebraspe`
- **API:** `https://apis.cebraspe.org.br/cebraspe/pas/subprogramas`
- **Coleta (UTC):** ver `crawler_summary.json` → `collected_at_utc`
- **as_of_date:** ver `crawler_summary.json` — data usada para encerrados / `recency_should_discard` (default: hoje)
- **Itens brutos (API):** 12 subprogramas PAS (amostra típica)
- **Descartados / Standardized:** ver JSON (com `as_of_date` = hoje pode ser 12 descartados e 0 standardized se todos encerrados)
- **Ficheiro:** `standardized/cebraspe_standardized.json`

## Nota

As rotas web `www.cebraspe.org.br/concursos/*` são **SPA**; o piloto usa **apenas** o JSON público referenciado pelo front (`apis.cebraspe.org.br`).

## Parâmetro opcional

```bash
python concursos/main_cebraspe_concursos.py --max-items 20 --sleep 1.5 --as-of-date 2025-09-01
```

## Próximo passo

```bash
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_cebraspe/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_cebraspe/loader_dryrun --sources cebraspe
```

Documentação: `docs/CONCURSOS_WAVE1_CEBRASPE_CRAWLER.md`.
