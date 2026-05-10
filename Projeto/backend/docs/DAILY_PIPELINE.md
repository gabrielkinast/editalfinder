# Pipeline diário EditalFinder (`main.py`)

O orquestrador na raiz (`main.py`) coordena o fluxo **edi­tais/oportunidades** e **notícia/pesquisa** com dry-run por defeito em `daily` e **apply** apenas com `--apply-staging` e variáveis de ambiente corretas.

O pipeline monolítico antigo (crawlers + `CORE/transformer.py` + `CORE/loader.py`) permanece em `main_legacy_pipeline.py`.

## Dry-run manual (sem escrita no Supabase)

```powershell
cd <raiz-do-repo>
CORE\.venv\Scripts\python.exe main.py daily --dry-run --skip-crawl --skip-transform --skip-news --skip-edital-audits
```

`--skip-edital-audits` evita `audit_semantic_classification` sobre todo o diretório canónico (pode ser muito lento). Remova `--skip-news` / `--skip-edital` conforme quiser exercitar esses blocos.

## Apply em staging (manual)

```powershell
$env:EDITALFINDER_ENV = "staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY = "true"
cd <raiz-do-repo>
CORE\.venv\Scripts\python.exe main.py daily --apply-staging
```

**Nota:** no apply, o `main.py` invoca os loaders com `--test-db-before-apply` (exigência dos scripts).

Pré-requisitos adicionais: `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY` (carregados via `.env.staging`, `.env.local`, `.env`, `CORE/.env` — `override=False`).

## Só editais

Dry-run:

```powershell
CORE\.venv\Scripts\python.exe main.py apply-edital --sources bnb,banco_da_amazonia,bdmg --dry-run
```

Apply staging:

```powershell
$env:EDITALFINDER_ENV = "staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY = "true"
CORE\.venv\Scripts\python.exe main.py apply-edital --sources bnb,banco_da_amazonia,bdmg --apply-staging
```

## Só notícia/pesquisa (uma onda)

Dry-run:

```powershell
CORE\.venv\Scripts\python.exe main.py apply-news --source nasa_news --wave nasa_wave2 --dry-run
```

Apply staging:

```powershell
$env:EDITALFINDER_ENV = "staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY = "true"
CORE\.venv\Scripts\python.exe main.py apply-news --source nasa_news --wave nasa_wave2 --apply-staging
```

## Limpeza segura (sem DELETE)

Dry-run (Onda A crédito):

```powershell
CORE\.venv\Scripts\python.exe main.py clean-staging --group credito_onda_a --dry-run
```

Apply (exige `ALLOW_CREDITO_ONDA_A_DEACTIVATE=1` no script de desativação):

```powershell
$env:EDITALFINDER_ENV = "staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY = "true"
$env:ALLOW_CREDITO_ONDA_A_DEACTIVATE = "1"
CORE\.venv\Scripts\python.exe main.py clean-staging --group credito_onda_a --apply-staging
```

## Validação global pós-carga

Depois de um `daily --apply-staging`, rode a validação global. Ela faz apenas `SELECT`, valida `public.edital`, `public.noticia`, `public.pesquisa` e as views principais, e grava:

- `audit_reports_main_pipeline/post_daily_validation.json`
- `audit_reports_main_pipeline/post_daily_validation.md`

```powershell
CORE\.venv\Scripts\python.exe main.py validate-staging
```

## Detector geral de resíduos

O detector compara links ativos no banco staging com os payloads/standardized atuais. Ele não altera dados e grava:

- `audit_reports_main_pipeline/removed_items_candidates.json`
- `audit_reports_main_pipeline/removed_items_candidates.md`

```powershell
CORE\.venv\Scripts\python.exe main.py detect-residues
```

Exemplo restrito a fontes de crédito:

```powershell
CORE\.venv\Scripts\python.exe main.py detect-residues --table edital --sources bnb,banco_da_amazonia,bdmg
```

## Limpeza segura geral de resíduos

Dry-run (padrão, sem escrita):

```powershell
CORE\.venv\Scripts\python.exe main.py clean-staging --group removed_items
```

Apply seguro em staging:

```powershell
$env:EDITALFINDER_ENV="staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY="true"
$env:ALLOW_DEACTIVATE_REMOVED_ITEMS="1"

CORE\.venv\Scripts\python.exe main.py clean-staging --group removed_items --apply-staging --apply-deactivation
```

Esta limpeza geral nunca deleta registros. Ela apenas marca candidatos como `ativo=false` e preserva metadados de auditoria em `extras` quando a coluna existe. O frontend deve esconder `ativo=false` por padrão; os dados permanecem preservados para auditoria e eventual reversão. Produção exigiria política separada, revisão específica e guards próprios.

## Agendamento (Windows Task Scheduler, meio-dia)

| Campo | Valor |
|--------|--------|
| Programa | `C:\caminho\para\repo\CORE\.venv\Scripts\python.exe` |
| Argumentos | `main.py daily --apply-staging` |
| Iniciar em | Raiz do repositório |

**Recomendação:** agendar primeiro `daily --dry-run` durante alguns dias; só depois `--apply-staging`.

## Configuração opcional

- `config/pipeline_sources.json` — ondas ativas de news/research; `stable_apply_sources` para limitar fontes edital no daily (vazio = todas as elegíveis via readiness).
- `config/source_readiness.json` — curadoria operacional (ready / blocked / etc.).

## Relatórios

Por defeito em `audit_reports_main_pipeline/`:

- `last_run_summary.json` / `.md`
- `last_run_steps.json`
- `last_run_errors.json`
