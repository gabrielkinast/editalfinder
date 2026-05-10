-- =============================================================================
-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
-- DANGER — RESET DESTRUTIVO DO SCHEMA EDITALFINDER (STAGING / DEV APENAS)
-- <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
-- <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
--
-- USAR SOMENTE EM STAGING / DESENVOLVIMENTO.
--
-- NÃO RODAR EM PRODUÇÃO. NÃO RODAR EM PRODUÇÃO. NÃO RODAR EM PRODUÇÃO.
--
-- ESTE SCRIPT:
--   - APAGA TODOS OS DADOS das tabelas operacionais do EditalFinder listadas
--     abaixo (DROP TABLE remove linhas).
--   - Recria tabelas, índices e views alinhadas ao contrato atual do backend
--     (ver docs/sql/schema_consolidado_editalfinder.sql e loaders em CORE/
--     e scripts/).
--
-- Não contém credenciais nem secrets.
-- Não é executado automaticamente pela aplicação (não chamar a partir de
-- main.py nem de pipelines implícitos).
--
-- Escopo LIMITADO (não tocar):
--   - auth.*, storage.*, perfis, utilizadores
--   - public.organizacao (e outras tabelas de negócio externas ao módulo)
--   - quaisquer objetos não listados explicitamente
--
-- Referência de modelagem: docs/sql/schema_consolidado_editalfinder.sql
-- Ajustes adicionais: scripts/load_news_research_sources.py (noticia/pesquisa)
--                     scripts/load_ready_sources.py (carga_execucao)
--                     CORE/loader.py (edital, anexos, extras, histórico)
--
-- Ordem:
--   1) BEGIN
--   2) DROP VIEW (admin → front → notícias → pesquisas)
--   3) DROP TABLE (dependentes primeiro)
--   4) CREATE EXTENSION pgcrypto
--   5) CREATE TABLE + constraints UNIQUE(link) onde aplicável
--   6) CREATE INDEX
--   7) CREATE VIEW
--   8) NOTIFY PostgREST para recarregar schema
--   9) COMMIT
--
-- Após rodar: reconfigurar RLS/políticas no Supabase se o projeto as usar
-- (este script não recria políticas).
-- =============================================================================

begin;

-- ---------------------------------------------------------------------------
-- 1) Views (dependências: admin → front)
-- ---------------------------------------------------------------------------
drop view if exists public.vw_editais_admin;
drop view if exists public.vw_editais_front;
drop view if exists public.vw_noticias_front;
drop view if exists public.vw_pesquisas_front;

-- ---------------------------------------------------------------------------
-- 2) Tabelas (filhas antes das bases)
-- ---------------------------------------------------------------------------
drop table if exists public.edital_historico cascade;
drop table if exists public.edital_extra_campo cascade;
drop table if exists public.edital_anexo cascade;
drop table if exists public.carga_execucao cascade;
drop table if exists public.edital cascade;
drop table if exists public.noticia cascade;
drop table if exists public.pesquisa cascade;

-- ---------------------------------------------------------------------------
-- 3) Extensão (gen_random_uuid)
-- ---------------------------------------------------------------------------
create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- 4) public.edital — núcleo do loader (id_edital bigserial)
-- ---------------------------------------------------------------------------
create table public.edital (
  id_edital bigserial primary key,
  titulo text,
  descricao text,
  fonte_recurso text,
  link text not null,
  hash_deduplicacao text,
  pdf_url text,
  prazo_envio date,
  data_publicacao date,
  data_encerramento date,
  orgao text,
  orgao_responsavel text,
  orgao_contratante text,
  instituicao text,
  pais text,
  regiao text,
  estado text,
  municipio text,
  uf text,
  cidade text,
  tipo_oportunidade text,
  tipo_recurso text,
  natureza_recurso text,
  perfil_ideal text[],
  publico_alvo text,
  publico_alvo_arr text[],
  area text[],
  area_cientifica text[],
  area_tecnologica text[],
  setor_estrategico text[],
  setor_economico text[],
  validacao_status text,
  qualidade_dado integer,
  classificacao_confianca text,
  ativo boolean default true,
  situacao text,
  codigo_oportunidade text,
  numero_chamada text,
  numero_edital text,
  numero_processo text,
  valor_estimado numeric,
  valor_maximo double precision,
  valor_minimo double precision,
  valor_total_texto text,
  moeda text,
  idioma_original varchar(32),
  origem_portal text,
  programa text,
  acao text,
  objetivo text,
  temas text,
  extras jsonb not null default '{}'::jsonb,
  score integer default 0,
  score_detalhado jsonb,
  justificativa text,
  recomendacao text,
  compatibilidade jsonb,
  contato text,
  link_inscricao text,
  ods text,
  id_organizacao bigint,
  ultima_coleta timestamptz,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  constraint edital_link_key unique (link)
);

-- ---------------------------------------------------------------------------
-- 5) public.noticia — contrato load_news_research_sources (id uuid)
-- ---------------------------------------------------------------------------
create table public.noticia (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  resumo text,
  conteudo text,
  link text not null,
  fonte text,
  fonte_recurso text,
  data_publicacao date,
  prazo_envio date,
  autor text,
  pais text,
  regiao text,
  idioma text,
  idioma_original text,
  origem_portal text,
  tipo_conteudo text,
  content_type text not null default 'noticia',
  imagem_url text,
  area_cientifica text[],
  area_tecnologica text[],
  setor_estrategico text[],
  tags text[],
  perfil_ideal text[],
  publico_alvo text,
  qualidade_dado integer,
  validacao_status text default 'incompleto',
  codigo_oportunidade text,
  numero_chamada text,
  extras jsonb not null default '{}'::jsonb,
  ativo boolean not null default true,
  hash_deduplicacao text,
  ultima_coleta timestamptz,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  constraint noticia_link_key unique (link)
);

-- ---------------------------------------------------------------------------
-- 6) public.pesquisa — contrato load_news_research_sources (id uuid)
-- ---------------------------------------------------------------------------
create table public.pesquisa (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  resumo text,
  descricao text,
  link text not null,
  fonte text,
  fonte_recurso text,
  data_publicacao date,
  prazo_envio date,
  pais text,
  regiao text,
  idioma text,
  idioma_original text,
  origem_portal text,
  tipo_pesquisa text,
  tipo_oportunidade text,
  tipo_recurso text,
  area_cientifica text[],
  area_tecnologica text[],
  setor_estrategico text[],
  tags text[],
  perfil_ideal text[],
  publico_alvo text,
  documentos jsonb not null default '[]'::jsonb,
  pdf_url text,
  url_documento text,
  content_type text not null default 'pesquisa',
  qualidade_dado integer,
  validacao_status text default 'incompleto',
  codigo_oportunidade text,
  numero_chamada text,
  extras jsonb not null default '{}'::jsonb,
  ativo boolean not null default true,
  hash_deduplicacao text,
  ultima_coleta timestamptz,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  constraint pesquisa_link_key unique (link)
);

-- ---------------------------------------------------------------------------
-- 7) public.carga_execucao — id_execucao (insert em load_ready_sources)
-- ---------------------------------------------------------------------------
create table public.carga_execucao (
  id_execucao uuid primary key default gen_random_uuid(),
  ambiente text not null,
  staging_flag boolean,
  status text,
  apply_status text,
  data_inicio timestamptz default now(),
  data_fim timestamptz,
  duracao_segundos numeric,
  sources jsonb not null default '[]'::jsonb,
  fontes jsonb not null default '[]'::jsonb,
  sources_selected integer,
  sources_excluded integer,
  fontes_carregadas integer,
  fontes_excluidas integer,
  total_itens_processados integer,
  itens_processados integer,
  inseridos integer,
  itens_inseridos integer,
  atualizados integer,
  itens_atualizados integer,
  ignorados integer,
  itens_ignorados integer,
  erros integer,
  environment_safe boolean,
  environment_guard jsonb not null default '{}'::jsonb,
  summary jsonb not null default '{}'::jsonb,
  fontes_excluidas_detalhe jsonb not null default '[]'::jsonb,
  blocked_sources_loaded jsonb not null default '[]'::jsonb,
  relatorio_json jsonb not null default '{}'::jsonb,
  criado_em timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- 8) public.edital_anexo
-- ---------------------------------------------------------------------------
create table public.edital_anexo (
  id_anexo uuid primary key default gen_random_uuid(),
  id_edital bigint not null references public.edital (id_edital) on delete cascade,
  titulo text,
  nome text,
  url text,
  tipo text,
  mime_type text,
  tamanho bigint,
  hash text,
  origem text,
  extras jsonb not null default '{}'::jsonb,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- 9) public.edital_extra_campo
-- ---------------------------------------------------------------------------
create table public.edital_extra_campo (
  id_extra uuid primary key default gen_random_uuid(),
  id_edital bigint not null references public.edital (id_edital) on delete cascade,
  chave text not null,
  valor text,
  valor_json jsonb,
  tipo_valor text,
  tipo_dado text,
  ordem integer default 0,
  tamanho_valor integer,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- 10) public.edital_historico — alinhado a CORE/loader.save_history_events
-- ---------------------------------------------------------------------------
create table public.edital_historico (
  id_historico uuid primary key default gen_random_uuid(),
  id_edital bigint references public.edital (id_edital) on delete cascade,
  id_execucao uuid references public.carga_execucao (id_execucao) on delete set null,
  tipo_evento text not null,
  campo text,
  valor_antigo text,
  valor_novo text,
  valor_antigo_json jsonb,
  valor_novo_json jsonb,
  diff jsonb,
  metadata jsonb not null default '{}'::jsonb,
  fonte text,
  criado_em timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- 11) Índices — btree + GIN (link já coberto por UNIQUE em edital/noticia/pesquisa)
-- ---------------------------------------------------------------------------
create index idx_edital_fonte_recurso on public.edital (fonte_recurso);
create index idx_edital_data_publicacao on public.edital (data_publicacao desc);
create index idx_edital_prazo_envio on public.edital (prazo_envio);
create index idx_edital_validacao_status on public.edital (validacao_status);
create index idx_edital_codigo_oportunidade on public.edital (codigo_oportunidade);
create index idx_edital_extras_gin on public.edital using gin (extras);
create index idx_edital_area_cientifica_gin on public.edital using gin (area_cientifica);
create index idx_edital_area_tecnologica_gin on public.edital using gin (area_tecnologica);
create index idx_edital_setor_estrategico_gin on public.edital using gin (setor_estrategico);

create index idx_noticia_fonte_recurso on public.noticia (fonte_recurso);
create index idx_noticia_data_publicacao on public.noticia (data_publicacao desc);
create index idx_noticia_prazo_envio on public.noticia (prazo_envio);
create index idx_noticia_validacao_status on public.noticia (validacao_status);
create index idx_noticia_codigo_oportunidade on public.noticia (codigo_oportunidade);
create index idx_noticia_extras_gin on public.noticia using gin (extras);
create index idx_noticia_tags_gin on public.noticia using gin (tags);
create index idx_noticia_area_cientifica_gin on public.noticia using gin (area_cientifica);
create index idx_noticia_area_tecnologica_gin on public.noticia using gin (area_tecnologica);
create index idx_noticia_setor_estrategico_gin on public.noticia using gin (setor_estrategico);

create index idx_pesquisa_fonte_recurso on public.pesquisa (fonte_recurso);
create index idx_pesquisa_data_publicacao on public.pesquisa (data_publicacao desc);
create index idx_pesquisa_prazo_envio on public.pesquisa (prazo_envio);
create index idx_pesquisa_validacao_status on public.pesquisa (validacao_status);
create index idx_pesquisa_codigo_oportunidade on public.pesquisa (codigo_oportunidade);
create index idx_pesquisa_extras_gin on public.pesquisa using gin (extras);
create index idx_pesquisa_tags_gin on public.pesquisa using gin (tags);
create index idx_pesquisa_area_cientifica_gin on public.pesquisa using gin (area_cientifica);
create index idx_pesquisa_area_tecnologica_gin on public.pesquisa using gin (area_tecnologica);
create index idx_pesquisa_setor_estrategico_gin on public.pesquisa using gin (setor_estrategico);

create index idx_edital_anexo_edital on public.edital_anexo (id_edital);
create index idx_edital_anexo_url on public.edital_anexo (url);
create index idx_edital_extra_edital on public.edital_extra_campo (id_edital);
create index idx_edital_extra_chave on public.edital_extra_campo (chave);
create index idx_carga_execucao_ambiente on public.carga_execucao (ambiente);
create index idx_carga_execucao_status on public.carga_execucao (status);
create index idx_carga_execucao_data_inicio_desc on public.carga_execucao (data_inicio desc);
create index idx_edital_historico_id_edital on public.edital_historico (id_edital);
create index idx_edital_historico_tipo_evento on public.edital_historico (tipo_evento);
create index idx_edital_historico_criado_em_desc on public.edital_historico (criado_em desc);
create index idx_edital_historico_id_execucao on public.edital_historico (id_execucao);

-- ---------------------------------------------------------------------------
-- 12) Views
-- ---------------------------------------------------------------------------
create view public.vw_editais_front as
select
  e.id_edital as id,
  e.titulo,
  e.descricao,
  e.fonte_recurso,
  e.fonte_recurso as fonte,
  e.link,
  e.pdf_url,
  e.prazo_envio,
  e.prazo_envio as fim_inscricao,
  e.data_publicacao,
  e.tipo_oportunidade,
  e.tipo_recurso,
  e.perfil_ideal,
  e.publico_alvo_arr as publico_alvo,
  e.area_cientifica,
  e.area_tecnologica,
  e.setor_estrategico,
  e.setor_economico,
  e.pais,
  e.regiao,
  e.uf,
  e.validacao_status,
  e.qualidade_dado,
  e.classificacao_confianca,
  e.ativo,
  e.situacao,
  e.extras,
  e.criado_em,
  e.atualizado_em
from public.edital e;

create view public.vw_editais_admin as
select * from public.vw_editais_front;

create view public.vw_noticias_front as
select
  n.id,
  n.titulo,
  n.resumo,
  n.conteudo,
  n.link,
  n.data_publicacao,
  n.prazo_envio,
  n.prazo_envio as fim_inscricao,
  n.fonte_recurso,
  coalesce(n.fonte_recurso, n.fonte) as fonte,
  n.fonte as fonte_legado,
  n.tipo_conteudo,
  n.content_type,
  n.area_cientifica,
  n.area_tecnologica,
  n.setor_estrategico,
  n.tags,
  n.validacao_status,
  n.qualidade_dado,
  n.extras,
  n.pais,
  n.regiao,
  n.idioma,
  n.idioma_original,
  n.origem_portal,
  n.ativo,
  n.criado_em,
  n.atualizado_em
from public.noticia n;

create view public.vw_pesquisas_front as
select
  p.id,
  p.titulo,
  p.descricao,
  p.resumo,
  p.link,
  p.data_publicacao,
  p.prazo_envio,
  p.prazo_envio as fim_inscricao,
  p.fonte_recurso,
  coalesce(p.fonte_recurso, p.fonte) as fonte,
  p.fonte as fonte_legado,
  p.tipo_pesquisa,
  p.area_cientifica,
  p.area_tecnologica,
  p.setor_estrategico,
  p.tags,
  p.validacao_status,
  p.qualidade_dado,
  p.pdf_url,
  p.url_documento,
  p.documentos,
  p.extras,
  p.tipo_oportunidade,
  p.tipo_recurso,
  p.pais,
  p.regiao,
  p.idioma,
  p.idioma_original,
  p.origem_portal,
  p.ativo,
  p.criado_em,
  p.atualizado_em
from public.pesquisa p;

-- ---------------------------------------------------------------------------
-- 13) PostgREST / Supabase API: pedir reload do cache de schema
-- ---------------------------------------------------------------------------
notify pgrst, 'reload schema';

commit;
