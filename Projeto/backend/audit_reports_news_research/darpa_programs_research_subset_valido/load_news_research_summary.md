# Load news/research (notícia / pesquisa)

- Execução: `2026-05-20T01:45:46Z`
- Modo: **apply**
- Fonte: `darpa_programs_research`
- Wave: `—`
- Payload notícia: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\darpa_programs_research_subset_valido\darpa_programs_payload_noticia.json`
- Payload pesquisa: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\darpa_programs_research_subset_valido\standardized\darpa_programs_research_standardized.json`
- Review (auditoria, não carregado): `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\darpa_programs_research_subset_valido\darpa_programs_review_candidates.json`
- Diretório: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\darpa_programs_research_subset_valido`

## Métricas

- total_noticia (input): **0**
- total_pesquisa (input): **25**
- would_upsert_noticia: **0**
- would_upsert_pesquisa: **25**
- inserted_noticia / updated_noticia: **0** / **0**
- inserted_pesquisa / updated_pesquisa: **0** / **25**
- skipped: **0**
- errors: **0**
- review_candidates_ignored: **0**
- arrays_normalized_count: **25**

## Environment guard (mascarado)

```json
{
  "editalfinder_env": "staging",
  "has_supabase_url": true,
  "has_service_key": true,
  "has_anon_key": true,
  "has_allow_staging_apply": true,
  "url_host_masked": "dof***.co",
  "block_reason": ""
}
```

- environment_safe (para **apply**): **True**
- apply_status: `applied`

> Em `--dry-run`, não é obrigatório `environment_safe`; o bloco acima apenas documenta o ambiente atual.

## Apply staging (não executado por padrão)

Pré-requisitos no ambiente:

- `EDITALFINDER_ENV=staging` ou `local`
- `EDITALFINDER_ALLOW_STAGING_APPLY=true`
- `SUPABASE_URL` + chave de serviço (`SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY`)
- Flags: `--apply --staging --test-db-before-apply`

```text
# Exemplo (não executar até validar .env.staging):
# set EDITALFINDER_ENV=staging
# set EDITALFINDER_ALLOW_STAGING_APPLY=true
# CORE\.venv\Scripts\python.exe scripts\load_news_research_sources.py ^
#   --apply --staging --test-db-before-apply --wave nasa_wave2 ^
#   --input-dir audit_reports_news_research_loader
```
