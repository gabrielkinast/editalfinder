# Reset do schema EditalFinder (staging / dev)

## Quando usar

Use este fluxo quando o **banco de staging ou desenvolvimento** estiver com schema **irrecuperável por migrations aditivas** (colunas em falta, tipos divergentes, views incompatíveis) e for aceitável **perder todos os dados** das tabelas operacionais do módulo EditalFinder nesse ambiente, recarregando depois via loaders.

**Não use em produção.** O script `migrations/DANGER_RESET_STAGING_SCHEMA.sql` faz `DROP TABLE` nas tabelas listadas no próprio ficheiro e **apaga linhas**.

## O que o reset faz

- Remove e recria **apenas** as views e tabelas do EditalFinder definidas nesse script (edital, notícia, pesquisa, anexos, extras, carga de execução, histórico).
- **Não** remove `public.organizacao`, auth, storage, perfis nem outras tabelas do projeto.
- **Não** contém secrets; não deve ser executado pela aplicação (`main.py` não deve invocá-lo).

## Ordem recomendada após decidir pelo reset

1. **Backup opcional** do staging (export SQL ou snapshot do projeto Supabase), se quiser histórico.
2. Executar manualmente no SQL Editor do Supabase (ou `psql`) o ficheiro  
   `migrations/DANGER_RESET_STAGING_SCHEMA.sql`  
   na base **staging/dev** correta.
3. Conferir tabelas e views (ver `docs/sql/check_reset_schema.sql`).
4. O script já executa `NOTIFY pgrst, 'reload schema';` no fim da transação. Se tiver aplicado DDL noutro sítio sem esse passo, execute o `NOTIFY` manualmente para o PostgREST atualizar o cache.
5. **RLS / políticas:** o reset não recria políticas Supabase. Se o projeto usava políticas em `noticia` / `pesquisa` / `edital`, volte a criá-las ou desative RLS em dev conforme a vossa política de segurança.
6. Correr os **applies** dos lotes prontos (`load_ready_sources` ou fluxo que usam) para repovoar `public.edital` e tabelas relacionadas.
7. Correr **`scripts/load_news_research_sources.py`** (NASA news/research ou payloads equivalentes) para repovoar `public.noticia` e `public.pesquisa`.
8. Validar no frontend e com consultas de verificação (incluindo `docs/sql/check_reset_schema.sql`).

## Contratos importantes

- **`public.edital`:** chave primária **`id_edital`** (`bigserial`), alinhada a `CORE/loader.py` (upsert por `link`).
- **`public.noticia` / `public.pesquisa`:** chave primária **`id`** (`uuid`, `gen_random_uuid()`), alinhada ao pedido de reset e às views `vw_*_front` que expõem `id`.
- **`public.carga_execucao`:** chave **`id_execucao`** (`uuid`), como em `scripts/load_ready_sources.py`.
- **`public.edital_historico`:** eventos gravados pelo loader usam **`valor_antigo` / `valor_novo`** (e não `valor_anterior`).

## Relação com o schema consolidado

O ficheiro `docs/sql/schema_consolidado_editalfinder.sql` continua a ser a **referência documental** do modelo ideal. O reset de staging **materializa** um subconjunto compatível com os loaders atuais, com ajustes explícitos (por exemplo `id` uuid em notícia/pesquisa, colunas extra em `carga_execucao` para o registo de execução).

## Produção

Em produção, **não** se deve usar este reset. Migrações incrementais, compatibilidade com o frontend e plano de dados exigem outro processo.
