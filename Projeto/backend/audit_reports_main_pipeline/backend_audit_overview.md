# Auditoria Backend EditalFinder

Gerado em 2026-05-09, em modo somente leitura. Não rodei apply, não acessei Supabase, não executei SQL, não rodei crawlers e não alterei schema ou código operacional. Esta auditoria só leu arquivos e relatórios locais, e gerou os artefatos solicitados.

## Resumo executivo

O backend está organizado em três fluxos: edital, notícia e pesquisa. O fluxo de edital parte de crawlers por fonte, grava outputs brutos em `<fonte>/outputs`, transforma para standardized, audita, passa por readiness e carrega em `public.edital`. O fluxo news/research é separado, gera payloads próprios e carrega em `public.noticia` e `public.pesquisa`. O `main.py` é hoje o orquestrador seguro do pipeline diário; `main_legacy_pipeline.py` continua existindo como pipeline monolítico legado e como mapa de crawlers.

O estado geral é bom para staging, mas ainda frágil para automação total. O maior risco operacional é `config/pipeline_sources.json` com `stable_apply_sources: []`: no código atual isso significa "não restringir", então todas as fontes `ready` + `ready_with_notes` entram no apply diário, exceto bloqueadas/review/reprocess/exclude. O segundo risco é que o último `main.py` registrou recomendação final `OK` mesmo com quatro steps em erro, incluindo uma validação pós-carga de EurekAlert.

## Mapa do backend

- Crawlers: diretórios de fonte na raiz, como `finep/`, `cnpq/`, `pncp/`, `bnb/`, `banco_da_amazonia/`, `bdmg/`, `eureka_network/`, `eic/`, `japan_*`, `china_*`.
- Outputs brutos: `<fonte>/outputs/*_editais.json` e `.csv`.
- Transformer legado: `CORE/transformer.py`, com saída em `CORE/transformer/*_standardized.json`.
- Standardized canônico para loader: `audit_reports_retransform/standardized/*_standardized.json`.
- Standardized diário do main: `audit_reports_main_pipeline/retransform_daily/standardized/*_standardized.json`.
- Loader edital: `scripts/load_ready_sources.py` usando `CORE/loader.py`.
- Loader notícia/pesquisa: `scripts/load_news_research_sources.py`.
- Auditorias edital: `scripts/audit_semantic_classification.py`, `scripts/audit_docs_pipeline.py`, `scripts/audit_source_access_methods.py`.
- Auditorias news/research: `scripts/audit_news_research_pipeline.py`, `scripts/validate_news_research_after_load.py`.
- Configs: `config/source_readiness.json`, `config/pipeline_sources.json`, `config/news_research_sources.json`.
- Schema/migrations: `migrations/*.sql`, `docs/sql/schema_consolidado_editalfinder.sql`, `docs/sql/check_edital_payload_columns.sql`.

Foram detectados 104 diretórios de fonte, 99 standardized canônicos em `audit_reports_retransform/standardized`, 87 standardized no último retransform diário, 5 raws news/research e 39 JSONs no diretório do loader news/research.

## Main.py

Subcomandos existentes: `status`, `list-readiness`, `daily`, `validate-staging`, `apply-edital`, `apply-news`, `clean-staging`.

Sem subcomando, `python main.py` apenas imprime ajuda e não executa nada. Isso está correto e seguro.

O `.env` é carregado no import, nesta ordem: `.env.staging`, `.env.local`, `.env`, `CORE/.env`, com `override=False`. O `main.py` bloqueia produção por `EDITALFINDER_ENV=production/prod` e exige guard de staging para apply: ambiente `staging` ou `local`, `SUPABASE_URL`, service key e `EDITALFINDER_ALLOW_STAGING_APPLY`.

`daily --dry-run` seleciona fontes elegíveis, opcionalmente roda crawlers, retransforma, audita, roda loader em dry-run, executa news/research em dry-run e grava `last_run_*`.

`daily --apply-staging` faz primeiro a fase dry-run/gates. Se passar e o ambiente for seguro, roda `load_ready_sources.py --apply --staging --test-db-before-apply` para editais, roda `load_news_research_sources.py --apply --staging --test-db-before-apply` por onda, e depois chama validações pós-carga.

`apply-edital` isola o pipeline de edital e exige `--sources`. `apply-news` isola uma fonte/onda news/research. `validate-staging` chama `validate_database_after_load.py`. `clean-staging` hoje só aceita `credito_onda_a` e chama o script de desativação Onda A.

Flags relevantes: `--report-dir`, `--fail-fast`, `--continue-on-warning`, `--skip-crawl`, `--skip-transform`, `--sources`, `--skip-edital`, `--skip-news`, `--news-source`, `--skip-experimental-news`, `--update-canonical-standardized`, `--deactivate-removed`, `--skip-edital-audits`, `--filter-sources`, `--source`, `--wave`, `--group`.

Pontos frágeis:

- `stable_apply_sources: []` não significa "nenhuma fonte"; significa "todas as elegíveis".
- `last_run_errors.json` pode ficar vazio mesmo com steps em `status=error`.
- Com `--continue-on-warning`, falhas de crawler podem não bloquear apply.
- News/research experimental pode ser pulado com `--skip-experimental-news`, mas atualmente está ativo no config.
- O apply de news/research usa o summary do loader que é sobrescrito por onda, então o último `load_news_research_summary.json` não representa todas as ondas do diário.

## Pipeline de editais

Uma fonte vira standardized assim:

1. Crawler grava JSON bruto em `<fonte>/outputs`.
2. `CORE/transformer.py` ou `scripts/retransform_all.py` lê esse JSON.
3. O transformer normaliza datas, descrição, documentos, PDF, campos semânticos e extras.
4. `opportunity_gate.py`, `official_link_only.py` e calibrações em `taxonomy_filtros.py` reduzem ruído e enriquecem metadados.
5. A saída fica em `*_standardized.json`.

O standardized vira payload por `scripts/load_ready_sources.py`: ele normaliza com `CORE/schema.py`, decide destino com `CORE/loader.get_destination_table`, mapeia com `map_to_db_schema` para edital ou `map_to_content_schema` para notícia/pesquisa, valida campos críticos, e em apply chama upsert por `link`.

Readiness atual em `config/source_readiness.json`:

- `ready`: 54 fontes.
- `ready_with_notes`: 33 fontes.
- `needs_manual_review`: 6 fontes.
- `blocked`: 9 fontes.
- `reprocess_after_fix`: 0.
- elegíveis para daily hoje: 87 fontes.

Fontes recentemente adicionadas citadas no pedido:

- `bnb`: `ready_with_notes`.
- `banco_da_amazonia`: `ready_with_notes`.
- `bdmg`: `ready_with_notes`.
- `eureka_network`: `ready_with_notes`.
- `eic`: `ready_with_notes`.

O loader está preparado para campos extras de crédito quando `EDITALFINDER_EXTENDED_SCHEMA=true`. A migration `20260505_add_missing_edital_columns_from_loader_payload.sql` cobre campos como `taxa_juros`, `carencia`, `prazo_pagamento`, `prazo_carencia`, `prazo_amortizacao`, `linha_credito`, `modalidade_financiamento`, `garantias`, `reembolsavel` e outros.

O que pode quebrar:

- Se `EDITALFINDER_EXTENDED_SCHEMA` não estiver ativo, campos ricos podem ficar só em `extras` ou ser removidos do payload de upsert.
- `CORE/loader.save_detail_tables` usa `delete()` nas tabelas auxiliares `edital_anexo` e `edital_extra_campo` antes de reinserir detalhes. Não apaga `public.edital`, mas é uma exceção à política "nunca DELETE" se ela for interpretada globalmente.
- `content_routing.py` pode rotear itens de standardized para `noticia`/`pesquisa`; no último loader houve 60 notícia e 20 pesquisa vindas do fluxo de standardized.
- O schema consolidado é documentação e pode ficar defasado se o payload real evoluir mais rápido que as migrations/checks.

## Pipeline notícia/pesquisa

A coleta é feita por `scripts/crawl_news_research_sources.py`, lendo `config/news_research_sources.json`. O desenho evita full-site crawl, usa RSS/listing, janela temporal, limite de itens, filtros de keywords e enriquecimento controlado de páginas.

Os payloads são gerados por builders específicos:

- NASA: `build_nasa_wave2_payloads.py`.
- DARPA News: `build_darpa_news_wave_payloads.py`.
- IAEA: `build_iaea_wave1_payloads.py`.
- EurekAlert: `build_eurekalert_wave1_payloads.py`.

O loader `load_news_research_sources.py` separa payloads de notícia e pesquisa em arquivos diferentes, valida campos mínimos e faz upsert por `link` em `public.noticia` e `public.pesquisa`. Ele não escreve em `public.edital`. Candidatos `review_for_edital` são carregados como JSON de auditoria e ignorados pelo loader. `rejected` é tratado na validação pós-carga quando existe.

Waves ativas em `config/pipeline_sources.json`:

- `nasa_news / nasa_wave2`.
- `darpa_news / darpa_news_wave1`.
- `iaea_news_publications / iaea_wave1`.
- `eurekalert_science_filtered / eurekalert_wave1` (experimental).

`darpa_opportunities_research` está em `config/news_research_sources.json` como candidato ativo/review, mas não aparece nas `active_waves` do main. Portanto não entra no apply automático do `daily`.

Validações pós-carga existentes checam unicidade de links, contagem esperada por payload, campos mínimos, arrays não serializados como string, nenhum overlap notícia/pesquisa, nenhum link de payload em `public.edital`, review/rejected não carregados indevidamente, e presença nas views `vw_noticias_front` e `vw_pesquisas_front`.

Falta uma validação global: hoje a validação é por onda e o summary do loader é sobrescrito. O diário precisa de uma camada agregadora que resuma todas as ondas, todas as tabelas e todas as views.

## Limpeza de resíduos

A limpeza atual está em `scripts/deactivate_removed_credito_onda_a_staging.py`. Ela lê `audit_reports_credito/credito_brasil_onda_a_removed_links.json`, faz dry-run por padrão, e só aplica com `--apply --staging` mais guards de ambiente. A ação é `ativo=false`; não há DELETE nesse script.

Guards exigidos: `EDITALFINDER_ENV` staging/local, URL Supabase, service key, `EDITALFINDER_ALLOW_STAGING_APPLY` e `ALLOW_CREDITO_ONDA_A_DEACTIVATE`.

Limitações e riscos:

- Está limitada à Onda A e o `main.py` chama apenas `banco_da_amazonia,bdmg`.
- O script filtra `.eq("fonte", t["fonte"])`, mas o loader canônico usa `fonte_recurso` em `public.edital`. Dependendo do schema real, isso pode gerar `no_matching_row`.
- A lista de resíduos é estática, derivada de relatório, não de comparação automática banco ativo vs payload atual.
- Não cobre resíduos de notícia, pesquisa nem outras ondas/fonte.

## Banco, schema e migrations

Schema esperado:

- `public.edital`: tabela principal de oportunidades, editais, chamadas, grants, crédito, financiamento, licitações, supplier portals e programas com inscrição/submissão.
- `public.noticia`: notícias, releases e atualizações institucionais/científicas.
- `public.pesquisa`: publicações, relatórios, documentos técnicos e conteúdo científico/técnico.

Migrations importantes encontradas:

- `20260430_add_edital_filter_columns.sql`.
- `20260501_create_carga_execucao_and_edital_historico.sql`.
- `20260504_create_noticia_pesquisa_tables.sql`.
- `20260504_add_missing_columns_for_consolidated_schema.sql`.
- `20260504_align_supabase_backend_contract.sql`.
- `20260504_recreate_front_views_staging.sql`.
- `20260505_add_missing_edital_columns_from_loader_payload.sql`.
- `20260505_recreate_edital_views_credito_staging.sql`.
- `DANGER_RESET_STAGING_SCHEMA.sql`.

Existe reset staging destrutivo documentado em `migrations/DANGER_RESET_STAGING_SCHEMA.sql` e `docs/sql/RESET_STAGING_README.md`. Ele contém DROP de tabelas e deve ficar fora de qualquer automação diária.

Há checks manuais: `docs/sql/check_edital_payload_columns.sql`, `check_existing_schema.sql` e `check_reset_schema.sql`. As views esperadas existem nos scripts: `vw_editais_front`, `vw_editais_admin`, `vw_noticias_front`, `vw_pesquisas_front`.

Risco de drift: médio/alto. O payload real do loader evolui em `CORE/loader.py` e `taxonomy_filtros.py`; o schema consolidado é documentação. A migration de 2026-05-05 alinha muita coisa, mas ainda é necessário check automatizado de contrato.

## Relatórios recentes

Último `main.py`:

- timestamp: `2026-05-09T01:11:26.095994+00:00`.
- modo: `apply-staging`.
- recomendação final: `OK`.
- steps: 199 totais, 195 success, 4 error.
- `last_run_errors.json`: lista vazia.

Erros nos steps:

- `crawl:bae_systems_suppliers`: `merge_bae_items()` recebeu argumento inesperado `allowed_domains`.
- `crawl:china_nsfc`: falha de rede/listagens, preservando saída antiga.
- `crawl:fapergs`: módulo `pypdf` ausente.
- `validate_news_research_after_load:eurekalert_science_filtered:eurekalert_wave1`: validação retornou `ok=false`.

Edital no último run:

- fontes processadas: 87.
- `would_upsert_total`: 1219.
- apply: 957 inserts, 128 updates.
- destination counts no loader: 1139 edital, 60 notícia, 20 pesquisa.
- mapping errors: 0.
- critical empty items: 0.
- documentos perdidos no payload: 0.

News/research rodou e houve apply por ondas no daily. O último arquivo `load_news_research_summary.json`, por ser sobrescrito, representa apenas `eurekalert_science_filtered/eurekalert_wave1`: apply executado, 0 notícia, 1 pesquisa, 0 erros.

Relatórios de crédito:

- `credito_brasil_onda_a_removed_links.json`: 22 links removidos no total, principalmente BDMG.
- `lote_credito_brasil_onda_a_ruido_fix.json`: BNB, Banco da Amazônia e BDMG recomendados como `ready_with_notes`; Agério e Desenvolve SP ainda aparecem como revisão no diagnóstico do lote.
- `credito_multilateral_onda_b_ready_with_notes_loader_dryrun.json`: dry-run sem apply; exemplos indicam EIC e Eureka Network com mapping/documents OK.

## Riscos e lacunas

- Apply diário amplo demais quando `stable_apply_sources` está vazio.
- Falhas de step não necessariamente contaminam `last_run_errors.json`.
- Validação global pós-carga ainda não existe.
- Detector geral de resíduos ainda não existe.
- Desativação segura é específica da Onda A e usa relatório estático.
- Views podem expor `ativo=false`, suspeitos ou prazo vencido sem política clara de frontend.
- News/research tem validações por onda, mas não relatório agregado.
- Schema consolidado pode ficar defasado em relação ao payload real.
- `delete()` em tabelas auxiliares do loader merece decisão explícita de política.

## Recomendações priorizadas

1. Validação global pós-carga para `public.edital`, `public.noticia`, `public.pesquisa` e views.
2. Detector geral de resíduos por fonte/tabela, comparando banco ativo contra payload atual.
3. Desativação segura geral com `ativo=false`, sem DELETE na linha principal, com guards por operação.
4. Controle mais estrito de `pipeline_sources.json`, evitando `stable_apply_sources: []` como "todas".
5. Relatório operacional diário único e confiável, com failures/warnings/apply/validações/resíduos.
6. Política de qualidade para frontend: esconder `ativo=false`, suspeitos e prazos vencidos; expor badges para `access_limited`, experimental e `ready_with_notes`.

## Próximos passos sugeridos

Começar pela validação global e pela correção da semântica de `stable_apply_sources`. Essas duas mudanças reduzem o risco antes de automatizar detector/desativação de resíduos. Depois, generalizar a limpeza segura a partir de um diff automático banco vs payload, e só então promover relatório diário como sinal operacional confiável.
