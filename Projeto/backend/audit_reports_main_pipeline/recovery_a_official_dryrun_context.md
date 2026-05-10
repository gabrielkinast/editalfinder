# Recovery A — contexto do dry-run oficial

## Artefatos lidos (fase Recovery A)

- `recovery_a_summary.json` / `recovery_a_summary.md`
- `recovery_a_by_source.json` / `recovery_a_by_source.md`
- `recovery_a_examples.json` / `recovery_a_examples.md`
- `recovery_a_apply_recommendation.json` / `recovery_a_apply_recommendation.md`
- `recovery_a_basa.json` / `recovery_a_basa.md`
- `recovery_a_dod_sbir.json` / `recovery_a_dod_sbir.md`
- `recovery_a_esa_star.json` / `recovery_a_esa_star.md`

## Confirmação (objetivo deste dry-run)

| Fonte | Incluir no dry-run oficial |
|--------|----------------------------|
| **banco_da_amazonia** | Sim — linhas reais de crédito/financiamento |
| **dod_sbir_sttr** | Sim — apenas topics/solicitations oficiais; ruído (Success Stories, News, Events, API, hubs) removido |
| **esa_star** | **Não** — continua **blocked** (SSO/login ou ausência de fonte pública suficiente) |

## Restrições

- Sem apply, sem escrita Supabase, sem alterar schema, sem alterar `opportunity_gate` global, sem promover readiness oficial.

## Artefatos gerados neste dry-run oficial

- Readiness temporário: `recovery_a_readiness_official_dryrun.json`
- Standardized isolado: `recovery_a_official_dryrun_standardized/`
- Loader: `recovery_a_official_loader_dryrun.json`, `recovery_a_official_loader_dryrun.md`, pasta `recovery_a_official_loader_dryrun_bundle/`
- Semântica: `recovery_a_official_semantic/`, resumo `recovery_a_official_semantic_summary.json` / `.md`
- Recomendação apply: `recovery_a_official_apply_recommendation.json` / `.md`

Espelho JSON: `recovery_a_official_dryrun_context.json`.
