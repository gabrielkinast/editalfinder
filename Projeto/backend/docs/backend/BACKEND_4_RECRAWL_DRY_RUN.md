# Backend 4 — Recoleta controlada e comparação com o banco

Recoleta das fontes problemáticas **sem** insert/update/upsert, com comparação opcional aos registros atuais em `public.edital`.

---

## Comandos

```bash
cd "d:\Computational_Physics\My Projects\edital"

# Uma fonte (rede ligada = crawl/API real)
python scripts/recrawl_sources_dry_run.py --source china --limit 50
python scripts/recrawl_sources_dry_run.py --source araucaria --limit 50
python scripts/recrawl_sources_dry_run.py --source grants --limit 50

# Todas + comparar com Supabase (.env.staging)
python scripts/recrawl_sources_dry_run.py --source all --limit 50 --from-db

# Offline (JSON em cache, sem HTTP)
python scripts/recrawl_sources_dry_run.py --source all --limit 50 --no-network

# China: simular HTML de detail com fixture
python scripts/recrawl_sources_dry_run.py --source china --limit 30 --no-network --offline-fixtures

# Só comparação (após recoleta)
python scripts/compare_recrawl_with_db.py --source all --from-db
```

---

## Saídas

`outputs/backend_4_recrawl_comparison/`

| Caminho | Conteúdo |
|---------|----------|
| `china/summary.md` | listagem, detail HTTP, deadlines, bloqueios |
| `china/raw_sample.json` | itens brutos |
| `china/parsed_sample.json` | diagnóstico por item |
| `china/enriched_sample.json` | após parsers + `enrich_opportunity_record` |
| `araucaria/` | PDF, texto extraído, prazos |
| `grants/` | close_date, forecast, legado |
| `summary/comparison_summary.md` | diff vs BD (`--from-db`) |
| `*/matched_diff.json` | matched com ganho de prazo |
| `*/unmatched_new.json` / `unmatched_db.json` | só recoleta / só BD |

---

## O que cada relatório significa

### China
- **details_obtained / details_attempted** — taxa de sucesso no HTML de detalhe.
- **block_403** — provável bloqueio regional/WAF.
- **offline-fixtures** — valida o parser com HTML sintético (não prova crawl real).
- Se bloqueio > 50%: recomenda proxy/região antes de backfill.

### Araucária
- **pdf_text_extracted** — PDF baixado e lido (sem OCR).
- **deadline_requires_pdf** — prazo provavelmente só no PDF e texto ainda ausente.
- Ganho real exige propagar `pdf_texto_extraido` no crawler → transformer.

### Grants
- **with_close_date** — oportunidades com prazo de submissão na API.
- **forecasted** / **posted_only_no_close** — sem prazo estruturado (esperado).
- **legacy_view_url** — registros antigos; recoleta Simpler corrige links.

### Comparação BD
- **deadline_gain_estimate** = prazos novos em matched + novos itens com prazo.
- **deadlines_gained_on_matched** — BD sem `prazo_envio`, recoleta com prazo.

---

## Garantias (sem banco)

- Não chama `loader`, `upsert_routed_item`, `inserir_ou_atualizar_edital`.
- Não executa SQL nem migration.
- `EDITALFINDER_ENABLE_BACKEND_ENRICHMENT` não é alterado.

---

## Avançar para Backend 5?

| Condição | Ação |
|----------|------|
| China detail > 30% OK | staging: re-crawl + transform + load com relatório |
| Araucária PDF texto > 40% | backfill `prazo_envio` a partir de extras |
| Grants close_date estável | backfill ISO + atualizar links Simpler |
| Bloqueio China persistente | proxy ou despriorizar fonte no dashboard |

---

## Testes

```bash
python -m pytest tests/test_deadline_normalizer.py tests/test_opportunity_classifier.py tests/test_opportunity_enricher.py tests/test_source_deadline_parsers.py tests/test_recrawl_dry_run.py -q
```
