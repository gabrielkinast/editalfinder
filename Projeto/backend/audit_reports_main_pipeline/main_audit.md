# Auditoria — orquestrador `main.py`

- **Objetivo:** um único ponto de entrada para `daily` (edital + notícia/pesquisa), validações, apply explícito em staging e limpeza segura.
- **Legado:** `main_legacy_pipeline.py` mantém o fluxo crawlers → `CORE/transformer.py` → `CORE/loader.py` sem readiness/news integrados.
- **Segurança:** `python main.py` só mostra ajuda; apply só com subcomando e `--apply-staging` onde aplicável; ambiente `production`/`prod` bloqueia guards de staging; sem operações DDL/DML destrutivas no orquestrador.
- **Daily `--apply-staging`:** primeiro dry-run completo (loaders sem `--apply`); se falhar, exit 1 sem apply; se passar, verifica env e só então aplica edital, depois news por onda, validações e opcionalmente `clean-staging --deactivate-removed`.
- **Relatórios:** `last_run_*` em `audit_reports_main_pipeline/` (ver `main_audit.json`).

Documentação operacional: `docs/DAILY_PIPELINE.md`.
