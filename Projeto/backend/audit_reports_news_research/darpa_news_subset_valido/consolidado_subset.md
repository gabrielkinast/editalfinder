# DARPA News — subset válido (staging)

- **Execução:** 2026-05-19T00:21:19Z
- **Origem:** `audit_reports_news_research/darpa_strategic_dryrun/standardized/darpa_news_standardized.json`
- **Subset:** `audit_reports_news_research/darpa_news_subset_valido/standardized/darpa_news_standardized.json`
- **Janela:** 12 meses (corte ≥ `2025-05-24`)

## Totais

| Original (dry-run estratégico) | 10 |
| **Subset escolhido** | **10** |
| Excluídos | 0 |

## Loader dry-run

- **would_upsert_noticia:** 10
- **errors_count:** 0
- **apply_status:** dry_run_only
- **apply:** não executado

## Eixos estratégicos

- `engenharia_avancada`: 3
- `materiais_avancados`: 2
- `quantum`: 2
- `autonomia`: 1
- `defesa`: 1
- `robotica`: 1

## Itens (título · data)

- **2026-05-06** — DARPA XRQ-73 demonstrates hybrid-electric flight
- **2026-04-28** — Rethinking robotics with physical intelligence
- **2026-04-13** — For quantum computing, different qubits are better together
- **2026-03-19** — DARPA-developed autonomous helicopter technology transitions to U.S. Army
- **2026-03-11** — Translate your bio-attribution research into national security impact
- **2026-03-04** — Quantum Benchmarking Initiative expands quest to separate hype from reality
- **2026-03-03** — DARPAâs new X-76: the speed of a jet, the freedom of a helicopter
- **2026-02-27** — Upgrading biomass waste into strategic materials
- **2026-02-25** — ROCkN enables GPS-free operations
- **2026-02-18** — Turning proteins into PROSE

## Apply staging (não executado)

```powershell
# NÃO EXECUTADO — apply staging (manual após validar .env.staging)
$env:EDITALFINDER_ENV='staging'
$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'
python scripts/load_news_research_sources.py `
  --apply --staging --test-db-before-apply `
  --source darpa_news `
  --input-dir audit_reports_news_research/darpa_news_subset_valido
```
