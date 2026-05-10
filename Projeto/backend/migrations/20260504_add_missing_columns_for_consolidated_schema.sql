-- ============================================================
-- EditalFinder — migration ADITIVA (2026-05-04)
-- Alinha tabelas já existentes ao schema consolidado (docs/sql/schema_consolidado_editalfinder.sql)
-- quando CREATE TABLE IF NOT EXISTS não criou colunas novas.
--
-- Segurança:
--   - Sem DROP TABLE / DROP COLUMN
--   - Sem DELETE / TRUNCATE
--   - Sem views neste ficheiro (ver migrations/20260504_recreate_front_views_staging.sql)
--   - Apenas ADD COLUMN IF NOT EXISTS e CREATE INDEX IF NOT EXISTS
--
-- Ordem: colunas → índices
-- Ambiente: staging / dev (revisar antes de produção)
-- ============================================================

begin;

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- public.edital — colunas usadas pelo loader e pela view vw_editais_front
-- (inclui campos de filtros já previstos em 20260430_add_edital_filter_columns.sql)
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists situacao text;
alter table public.edital add column if not exists extras jsonb not null default '{}'::jsonb;
alter table public.edital add column if not exists tipo_oportunidade text;
alter table public.edital add column if not exists tipo_recurso text;
alter table public.edital add column if not exists setor_economico text[];
alter table public.edital add column if not exists publico_alvo_arr text[];
alter table public.edital add column if not exists area_cientifica text[];
alter table public.edital add column if not exists area_tecnologica text[];
alter table public.edital add column if not exists setor_estrategico text[];

alter table public.edital add column if not exists validacao_status text default 'incompleto';
alter table public.edital add column if not exists qualidade_dado integer;
alter table public.edital add column if not exists classificacao_confianca text;
alter table public.edital add column if not exists ativo boolean default true;
alter table public.edital add column if not exists uf text;
alter table public.edital add column if not exists regiao text;
alter table public.edital add column if not exists cidade text;
alter table public.edital add column if not exists data_encerramento date;
alter table public.edital add column if not exists hash_deduplicacao text;
alter table public.edital add column if not exists idioma_original varchar(32);
alter table public.edital add column if not exists origem_portal text;
alter table public.edital add column if not exists codigo_oportunidade text;
alter table public.edital add column if not exists numero_processo text;
alter table public.edital add column if not exists valor_estimado numeric;
alter table public.edital add column if not exists pdf_resumo text;
alter table public.edital add column if not exists objetivo text;
alter table public.edital add column if not exists perfil_ideal text[];
alter table public.edital add column if not exists ultima_coleta timestamptz;

-- ---------------------------------------------------------------------------
-- public.noticia — alinhar a map_to_content_schema / loader news-research
-- (tabela inicial em 20260504_create_noticia_pesquisa_tables.sql era mínima)
-- ---------------------------------------------------------------------------
alter table public.noticia add column if not exists conteudo text;
alter table public.noticia add column if not exists fonte_recurso text;
alter table public.noticia add column if not exists prazo_envio date;
alter table public.noticia add column if not exists autor text;
alter table public.noticia add column if not exists regiao text;
alter table public.noticia add column if not exists idioma_original text;
alter table public.noticia add column if not exists origem_portal text;
alter table public.noticia add column if not exists tipo_conteudo text;
alter table public.noticia add column if not exists imagem_url text;
alter table public.noticia add column if not exists perfil_ideal text[];
alter table public.noticia add column if not exists publico_alvo text;
alter table public.noticia add column if not exists qualidade_dado integer;
alter table public.noticia add column if not exists validacao_status text default 'incompleto';
alter table public.noticia add column if not exists codigo_oportunidade text;
alter table public.noticia add column if not exists numero_chamada text;
alter table public.noticia add column if not exists ativo boolean default true;

-- ---------------------------------------------------------------------------
-- public.pesquisa
-- ---------------------------------------------------------------------------
alter table public.pesquisa add column if not exists descricao text;
alter table public.pesquisa add column if not exists fonte_recurso text;
alter table public.pesquisa add column if not exists prazo_envio date;
alter table public.pesquisa add column if not exists regiao text;
alter table public.pesquisa add column if not exists idioma_original text;
alter table public.pesquisa add column if not exists origem_portal text;
alter table public.pesquisa add column if not exists tipo_oportunidade text;
alter table public.pesquisa add column if not exists tipo_recurso text;
alter table public.pesquisa add column if not exists perfil_ideal text[];
alter table public.pesquisa add column if not exists publico_alvo text;
alter table public.pesquisa add column if not exists qualidade_dado integer;
alter table public.pesquisa add column if not exists validacao_status text default 'incompleto';
alter table public.pesquisa add column if not exists codigo_oportunidade text;
alter table public.pesquisa add column if not exists numero_chamada text;
alter table public.pesquisa add column if not exists ativo boolean default true;
alter table public.pesquisa add column if not exists tipo_pesquisa text;
alter table public.pesquisa add column if not exists pdf_url text;

-- ---------------------------------------------------------------------------
-- public.edital_anexo
-- ---------------------------------------------------------------------------
alter table public.edital_anexo add column if not exists titulo text;
alter table public.edital_anexo add column if not exists mime_type text;
alter table public.edital_anexo add column if not exists tamanho bigint;
alter table public.edital_anexo add column if not exists hash text;
alter table public.edital_anexo add column if not exists origem text;
alter table public.edital_anexo add column if not exists extras jsonb not null default '{}'::jsonb;
alter table public.edital_anexo add column if not exists atualizado_em timestamptz not null default now();

-- ---------------------------------------------------------------------------
-- public.edital_extra_campo
-- ---------------------------------------------------------------------------
alter table public.edital_extra_campo add column if not exists valor_json jsonb;
alter table public.edital_extra_campo add column if not exists tipo_valor text;

-- ---------------------------------------------------------------------------
-- public.carga_execucao — campos adicionais do consolidado (loader / relatórios)
-- ---------------------------------------------------------------------------
alter table public.carga_execucao add column if not exists staging_flag boolean;
alter table public.carga_execucao add column if not exists apply_status text;
alter table public.carga_execucao add column if not exists sources jsonb default '[]'::jsonb;
alter table public.carga_execucao add column if not exists sources_selected integer;
alter table public.carga_execucao add column if not exists sources_excluded integer;
alter table public.carga_execucao add column if not exists total_itens_processados integer;
alter table public.carga_execucao add column if not exists inseridos integer;
alter table public.carga_execucao add column if not exists atualizados integer;
alter table public.carga_execucao add column if not exists ignorados integer;
alter table public.carga_execucao add column if not exists environment_safe boolean;
alter table public.carga_execucao add column if not exists summary jsonb default '{}'::jsonb;

-- ---------------------------------------------------------------------------
-- public.edital_historico
-- ---------------------------------------------------------------------------
alter table public.edital_historico add column if not exists valor_anterior text;
alter table public.edital_historico add column if not exists diff jsonb;

-- ---------------------------------------------------------------------------
-- Índices (após colunas)
-- ---------------------------------------------------------------------------
create index if not exists idx_edital_validacao_status on public.edital (validacao_status);
create index if not exists idx_edital_qualidade_dado on public.edital (qualidade_dado);
create index if not exists idx_edital_codigo_oportunidade on public.edital (codigo_oportunidade);

create index if not exists idx_noticia_codigo_oportunidade on public.noticia (codigo_oportunidade);
create index if not exists idx_noticia_validacao_status on public.noticia (validacao_status);
create index if not exists idx_noticia_data_publicacao on public.noticia (data_publicacao);
create index if not exists idx_noticia_fonte_recurso on public.noticia (fonte_recurso);

create index if not exists idx_pesquisa_codigo_oportunidade on public.pesquisa (codigo_oportunidade);
create index if not exists idx_pesquisa_validacao_status on public.pesquisa (validacao_status);
create index if not exists idx_pesquisa_data_publicacao on public.pesquisa (data_publicacao);

create index if not exists idx_noticia_area_cientifica_gin on public.noticia using gin (area_cientifica);
create index if not exists idx_noticia_area_tecnologica_gin on public.noticia using gin (area_tecnologica);
create index if not exists idx_noticia_setor_estrategico_gin on public.noticia using gin (setor_estrategico);

create index if not exists idx_pesquisa_area_cientifica_gin on public.pesquisa using gin (area_cientifica);
create index if not exists idx_pesquisa_area_tecnologica_gin on public.pesquisa using gin (area_tecnologica);
create index if not exists idx_pesquisa_setor_estrategico_gin on public.pesquisa using gin (setor_estrategico);

commit;
