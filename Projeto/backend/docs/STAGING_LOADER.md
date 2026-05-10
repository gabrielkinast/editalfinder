# Loader controlado em staging/local

Este guia descreve como executar o carregamento controlado **somente** em ambiente seguro (`staging`/`local`).

## 1) Variáveis de ambiente necessárias

O projeto usa principalmente:

- `SUPABASE_URL`
- `SUPABASE_KEY` **ou** `SUPABASE_SERVICE_ROLE_KEY` **ou** `SUPABASE_ANON_KEY`
- `EDITALFINDER_ENV` (`staging` ou `local`) para proteção explícita de apply
- `EDITALFINDER_ALLOW_STAGING_APPLY` (`true` para liberar apply em staging/local)

Referências de leitura no código:

- `CORE/db.py`: carrega `.env` e cria cliente Supabase
- `scripts/load_ready_sources.py`: valida ambiente seguro antes de `--apply`

## 2) Arquivo de exemplo

Use `.env.staging.example` como base (sem chaves reais no repositório).

Exemplo mínimo:

```env
EDITALFINDER_ENV=staging
EDITALFINDER_ALLOW_STAGING_APPLY=true
SUPABASE_URL=https://<projeto-staging>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<chave>
```

## 3) Proteções obrigatórias do apply

`scripts/load_ready_sources.py --staging --apply` só segue quando:

- `--staging` foi informado; **e**
- `EDITALFINDER_ENV` é `staging`/`local`; **e**
- `SUPABASE_URL` existe; **e**
- `SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY` existe; **e**
- `EDITALFINDER_ALLOW_STAGING_APPLY=true`.

Se falhar, o script grava `apply_status=blocked_staging_env_not_confirmed`.

## 4) Fluxo recomendado

### Dry-run final (obrigatório)

```bash
python scripts/load_ready_sources.py --dry-run --exclude-blocked
```

Relatórios:

- `audit_reports_loader_ready/final_dry_run_before_staging.md`
- `audit_reports_loader_ready/final_dry_run_before_staging.json`

### Apply controlado em staging/local

```bash
python scripts/load_ready_sources.py --staging --apply --exclude-blocked
```

Relatórios:

- `audit_reports_loader_ready/staging_load_summary.md`
- `audit_reports_loader_ready/staging_load_summary.json`
- `audit_reports_loader_ready/staging_load_by_source.json`
- `audit_reports_loader_ready/staging_load_errors.json`
- `audit_reports_loader_ready/staging_load_payload_examples.json`

## 5) Validação pós-carga

Gerada automaticamente:

- `audit_reports_loader_ready/post_staging_validation.md`
- `audit_reports_loader_ready/post_staging_validation.json`

Checklist:

- contagem de registros processados/inseridos/atualizados
- preservação de `extras`/`extras.documentos`/`pdf_url`
- campos de filtros preservados
- fontes bloqueadas não carregadas
- erros e sinais de duplicidade para revisão

## 6) Garantia de não-produção

- Não executar `--apply` sem `--staging`.
- Manter `EDITALFINDER_ENV=staging` (ou `local`) no ambiente de execução.
- Manter `EDITALFINDER_ALLOW_STAGING_APPLY=false` por padrão e ligar para `true` somente na janela de carga.
