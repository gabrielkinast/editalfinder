-- EditalFinder — Current Database Schema
-- Generated from current database/migrations/backend usage
-- Date: 2026-06-03
-- Source: Supabase public schema (PostgREST OpenAPI introspection, read-only)
-- WARNING: Documentation/audit schema. Review before applying as migration.

-- Dialect: PostgreSQL 15+ (Supabase)
-- No INSERT/data.

create extension if not exists pgcrypto;

-- Table: public.edital (107 columns)
create table if not exists public.edital (
  id_edital bigserial not null,
  acao text,
  access_reason text,
  access_status text,
  anexos jsonb,
  area text[],
  area_cientifica text[],
  area_tecnologica text[],
  ativo boolean,
  atualizado_em timestamptz not null default now(),
  carencia text,
  chamada text,
  cidade text,
  classificacao_confianca text,
  codigo_oportunidade text,
  compatibilidade jsonb,
  contato text,
  content_type_detectado text,
  contrapartida text,
  criado_em timestamptz not null default now(),
  data_abertura date,
  data_encerramento date,
  data_publicacao date,
  data_resultado date,
  descricao text,
  descricao_en text,
  descricao_original text,
  descricao_traduzida text,
  documentos jsonb,
  edital_numero text,
  elegibilidade text,
  estado text,
  extraction_mode text,
  extras jsonb not null default '{}'::jsonb,
  finalidade_financiamento text,
  fonte_recurso text,
  garantias text,
  hash_deduplicacao text,
  id_organizacao bigint,
  idioma_original text,
  instituicao text,
  justificativa text,
  limite_financiavel text,
  linha_credito text,
  link text not null,
  link_inscricao text,
  modalidade_financiamento text,
  moeda text,
  motivo_rejeicao text,
  municipio text,
  natureza_recurso text,
  numero_chamada text,
  numero_edital text,
  numero_processo text,
  objetivo text,
  ods text,
  orgao text,
  orgao_contratante text,
  orgao_responsavel text,
  origem_portal text,
  pais text,
  pdf_resumo text,
  pdf_url text,
  percentual_financiavel text,
  perfil_ideal text[],
  prazo_amortizacao text,
  prazo_carencia text,
  prazo_envio date,
  prazo_pagamento text,
  prazo_total text,
  programa text,
  publico_alvo text,
  publico_alvo_arr text[],
  publico_beneficiario text,
  qualidade_dado integer,
  recomendacao text,
  reembolsavel boolean,
  regiao text,
  score integer,
  score_detalhado jsonb,
  setor_economico text[],
  setor_estrategico text[],
  situacao text,
  subprograma text,
  suspeito boolean,
  tags text[],
  taxa_juros text,
  temas text,
  tipo_oportunidade text,
  tipo_recurso text,
  titulo text,
  titulo_en text,
  titulo_original text,
  titulo_traduzido text,
  traducao_automatica boolean,
  uf text,
  ultima_coleta timestamptz,
  unidade_responsavel text,
  url_detalhe text,
  url_listagem text,
  validacao_status text,
  valor_estimado numeric,
  valor_maximo double precision,
  valor_minimo double precision,
  valor_total numeric,
  valor_total_texto text,
  warnings text[],
  constraint edital_pkey primary key (id_edital),
  constraint edital_link_key unique (link)
);

-- Table: public.noticia (34 columns)
create table if not exists public.noticia (
  id uuid not null,
  area_cientifica text[],
  area_tecnologica text[],
  ativo boolean not null default true,
  atualizado_em timestamptz not null default now(),
  autor text,
  codigo_oportunidade text,
  content_type text not null default 'noticia',
  conteudo text,
  criado_em timestamptz not null default now(),
  data_publicacao date,
  extras jsonb not null default '{}'::jsonb,
  fonte text,
  fonte_recurso text,
  hash_deduplicacao text,
  idioma text,
  idioma_original text,
  imagem_url text,
  link text not null,
  numero_chamada text,
  origem_portal text,
  pais text,
  perfil_ideal text[],
  prazo_envio date,
  publico_alvo text,
  qualidade_dado integer,
  regiao text,
  resumo text,
  setor_estrategico text[],
  tags text[],
  tipo_conteudo text,
  titulo text not null,
  ultima_coleta timestamptz,
  validacao_status text,
  constraint noticia_pkey primary key (id),
  constraint noticia_link_key unique (link)
);

-- Table: public.pesquisa (37 columns)
create table if not exists public.pesquisa (
  id uuid not null,
  area_cientifica text[],
  area_tecnologica text[],
  ativo boolean not null default true,
  atualizado_em timestamptz not null default now(),
  codigo_oportunidade text,
  content_type text not null default 'pesquisa',
  criado_em timestamptz not null default now(),
  data_publicacao date,
  descricao text,
  documentos jsonb not null,
  extras jsonb not null default '{}'::jsonb,
  fonte text,
  fonte_recurso text,
  hash_deduplicacao text,
  idioma text,
  idioma_original text,
  link text not null,
  numero_chamada text,
  origem_portal text,
  pais text,
  pdf_url text,
  perfil_ideal text[],
  prazo_envio date,
  publico_alvo text,
  qualidade_dado integer,
  regiao text,
  resumo text,
  setor_estrategico text[],
  tags text[],
  tipo_oportunidade text,
  tipo_pesquisa text,
  tipo_recurso text,
  titulo text not null,
  ultima_coleta timestamptz,
  url_documento text,
  validacao_status text,
  constraint pesquisa_pkey primary key (id),
  constraint pesquisa_link_key unique (link)
);

-- Table: public.edital_anexo (13 columns)
create table if not exists public.edital_anexo (
  id_anexo uuid not null,
  atualizado_em timestamptz not null default now(),
  criado_em timestamptz not null default now(),
  extras jsonb not null default '{}'::jsonb,
  hash text,
  id_edital bigint not null,
  mime_type text,
  nome text,
  origem text,
  tamanho bigint,
  tipo text,
  titulo text,
  url text,
  constraint edital_anexo_pkey primary key (id_anexo)
);

-- Table: public.edital_extra_campo (11 columns)
create table if not exists public.edital_extra_campo (
  id_extra uuid not null,
  atualizado_em timestamptz not null default now(),
  chave text not null,
  criado_em timestamptz not null default now(),
  id_edital bigint not null,
  ordem integer,
  tamanho_valor integer,
  tipo_dado text,
  tipo_valor text,
  valor text,
  valor_json jsonb,
  constraint edital_extra_campo_pkey primary key (id_extra)
);

-- Table: public.carga_execucao (30 columns)
create table if not exists public.carga_execucao (
  id_execucao uuid not null,
  ambiente text not null,
  apply_status text,
  atualizados integer,
  blocked_sources_loaded jsonb not null,
  criado_em timestamptz not null default now(),
  data_fim timestamptz,
  data_inicio timestamptz,
  duracao_segundos numeric,
  environment_guard jsonb not null,
  environment_safe boolean,
  erros integer,
  fontes jsonb not null,
  fontes_carregadas integer,
  fontes_excluidas integer,
  fontes_excluidas_detalhe jsonb not null,
  ignorados integer,
  inseridos integer,
  itens_atualizados integer,
  itens_ignorados integer,
  itens_inseridos integer,
  itens_processados integer,
  relatorio_json jsonb not null,
  sources jsonb not null,
  sources_excluded integer,
  sources_selected integer,
  staging_flag boolean,
  status text,
  summary jsonb not null,
  total_itens_processados integer,
  constraint carga_execucao_pkey primary key (id_execucao)
);

-- Table: public.edital_historico (13 columns)
create table if not exists public.edital_historico (
  id_historico uuid not null,
  campo text,
  criado_em timestamptz not null default now(),
  diff jsonb,
  fonte text,
  id_edital bigint,
  id_execucao uuid,
  metadata jsonb not null,
  tipo_evento text not null,
  valor_antigo text,
  valor_antigo_json jsonb,
  valor_novo text,
  valor_novo_json jsonb,
  constraint edital_historico_pkey primary key (id_historico)
);

-- Table: public.cliente (30 columns)
create table if not exists public.cliente (
  id_cliente integer not null,
  area_inovacao text,
  capital_social numeric,
  cidade text,
  cnae_principal text,
  cnpj text,
  data_abertura date,
  descricao_projeto text,
  disponibilidade_contrapartida boolean,
  estado text,
  extras jsonb not null default '{}'::jsonb,
  faturamento_anual numeric,
  id_usuario bigint,
  interesse_temas text,
  interesse_valor_max numeric,
  interesse_valor_min numeric,
  natureza_juridica text,
  nivel_maturidade text,
  nome_empresa text,
  numero_funcionarios integer,
  pais text,
  porte_empresa text,
  possui_certidao_negativa boolean,
  razao_social text,
  regiao text,
  regular_fiscal boolean,
  regular_trabalhista boolean,
  setor text,
  status text,
  tem_projeto_inovacao boolean,
  constraint cliente_pkey primary key (id_cliente)
);

-- Table: public.usuario (8 columns)
create table if not exists public.usuario (
  id_usuario bigserial not null,
  auth_user_id uuid,
  nivel_acesso integer,
  nome text not null,
  nome_email text,
  senha text not null,
  status text,
  tipo_usuario text not null,
  constraint usuario_pkey primary key (id_usuario)
);

-- Table: public.edital_favorito (21 columns)
create table if not exists public.edital_favorito (
  id_favorito uuid not null,
  alerta_ativo boolean not null,
  alertar_com_dias integer not null,
  ativo boolean not null default true,
  atualizado_em timestamptz not null default now(),
  contexto text,
  criado_em timestamptz not null default now(),
  edital_fonte text,
  edital_link text,
  edital_titulo text,
  extras jsonb not null default '{}'::jsonb,
  id_edital bigint,
  id_usuario bigint,
  observacao text,
  origem text not null,
  prazo_envio date,
  proximo_alerta_em timestamptz,
  status_prazo text,
  ultimo_alerta_em timestamptz,
  visualizado boolean not null,
  visualizado_em timestamptz,
  constraint edital_favorito_pkey primary key (id_favorito)
);

-- Table: public.edital_feedback (13 columns)
create table if not exists public.edital_feedback (
  id_feedback uuid not null,
  atualizado_em timestamptz,
  comentario text,
  criado_em timestamptz,
  edital_link text,
  edital_titulo text,
  extras jsonb,
  fonte_recurso text,
  id_edital bigint,
  id_usuario bigint,
  prioridade text,
  status text not null,
  tipo_feedback text not null,
  constraint edital_feedback_pkey primary key (id_feedback)
);

-- Table: public.concurso_selecao (35 columns)
create table if not exists public.concurso_selecao (
  id_concurso bigserial not null,
  area text,
  ativo boolean not null default true,
  atualizado_em timestamptz not null default now(),
  banca text,
  cargo text,
  categoria text,
  criado_em timestamptz not null default now(),
  curso text,
  data_fim_inscricao date,
  data_inicio_inscricao date,
  data_prova date,
  data_publicacao date,
  estado text,
  extras jsonb not null default '{}'::jsonb,
  fonte text not null,
  fonte_tipo text,
  instituicao text,
  link text not null,
  link_edital text,
  modalidade text,
  municipio text,
  nivel_escolaridade text,
  numero_vagas integer,
  orgao text,
  qualidade_dado text,
  regiao text,
  salario_max numeric,
  salario_min numeric,
  status text not null,
  tags text[],
  taxa_inscricao numeric,
  tipo_selecao text not null,
  titulo text not null,
  validacao_status text not null,
  constraint concurso_selecao_pkey primary key (id_concurso),
  constraint concurso_selecao_fonte_link_key unique (fonte, link)
);

-- Table: public.portal_estrategico (44 columns)
create table if not exists public.portal_estrategico (
  id_portal uuid not null,
  acao_recomendada text,
  acesso_observacao text,
  acesso_tipo text,
  area_cientifica text[] not null,
  area_tecnologica text[] not null,
  ativo boolean not null default true,
  categoria text not null,
  created_at timestamptz not null default now(),
  data_captura timestamptz,
  data_publicacao date,
  decisao_qa text,
  descricao text,
  estado text,
  extras jsonb not null default '{}'::jsonb,
  fonte text,
  fonte_recurso text,
  frontend_section text not null,
  id_edital bigint,
  link text not null,
  mostrar_em_fornecedores boolean not null,
  mostrar_em_investimentos boolean not null,
  mostrar_em_procurement boolean not null,
  mostrar_no_radar boolean not null,
  motivo_qa text,
  origem_pipeline text,
  pais text,
  perfil_ideal text[] not null,
  portal_tipo text not null,
  prazo_envio date,
  publico_alvo text[] not null,
  qualidade_dado text not null,
  regiao text,
  requer_login boolean not null,
  resumo text,
  setor_economico text[] not null,
  setor_estrategico text[] not null,
  tags text[] not null,
  tipo_oportunidade text,
  tipo_recurso text,
  titulo text not null,
  updated_at timestamptz not null default now(),
  validacao_status text not null,
  wave text,
  constraint portal_estrategico_pkey primary key (id_portal),
  constraint portal_estrategico_link_key unique (link)
);

-- -----------------------------------------------------------------------------
-- Foreign keys
-- -----------------------------------------------------------------------------
alter table public.edital_anexo
  add constraint edital_anexo_id_edital_fkey
  foreign key (id_edital) references public.edital (id_edital) on delete cascade;

alter table public.edital_extra_campo
  add constraint edital_extra_campo_id_edital_fkey
  foreign key (id_edital) references public.edital (id_edital) on delete cascade;

alter table public.edital_historico
  add constraint edital_historico_id_edital_fkey
  foreign key (id_edital) references public.edital (id_edital) on delete cascade;

alter table public.edital_historico
  add constraint edital_historico_id_execucao_fkey
  foreign key (id_execucao) references public.carga_execucao (id_execucao) on delete set null;

-- -----------------------------------------------------------------------------
-- Indexes (from migrations; safe IF NOT EXISTS)
-- -----------------------------------------------------------------------------
create unique index if not exists edital_link_key on public.edital (link);
create index if not exists idx_edital_fonte_recurso on public.edital (fonte_recurso);
create index if not exists idx_edital_data_publicacao on public.edital (data_publicacao desc);
create index if not exists idx_edital_prazo_envio on public.edital (prazo_envio);
create index if not exists idx_edital_validacao_status on public.edital (validacao_status);
create index if not exists idx_edital_origem_portal on public.edital (origem_portal);
create index if not exists idx_edital_extras_gin on public.edital using gin (extras);
create index if not exists idx_edital_tags_gin on public.edital using gin (tags);
create index if not exists idx_edital_perfil_ideal_gin on public.edital using gin (perfil_ideal);
create index if not exists idx_noticia_link on public.noticia (link);
create index if not exists idx_pesquisa_link on public.pesquisa (link);
create index if not exists idx_edital_anexo_edital on public.edital_anexo (id_edital);
create index if not exists idx_edital_extra_edital on public.edital_extra_campo (id_edital);
create index if not exists idx_carga_execucao_data_inicio_desc on public.carga_execucao (data_inicio desc);
create index if not exists idx_edital_historico_id_edital on public.edital_historico (id_edital);

-- -----------------------------------------------------------------------------
-- Views: editais (latest migration body)
-- -----------------------------------------------------------------------------
-- ============================================================
-- STAGING / DEV — recriar views de editais com campos de crédito
--
-- Pré-requisito:
--   migrations/20260505_add_missing_edital_columns_from_loader_payload.sql
--
-- Apenas DROP/CREATE VIEW em public; não altera dados em tabelas base.
-- ============================================================


drop view if exists public.vw_editais_admin;
drop view if exists public.vw_editais_front;

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
  e.natureza_recurso,
  e.reembolsavel,
  e.linha_credito,
  e.modalidade_financiamento,
  e.taxa_juros,
  e.prazo_carencia,
  e.prazo_amortizacao,
  e.contrapartida,
  e.garantias,
  e.valor_minimo,
  e.valor_maximo,
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

-- -----------------------------------------------------------------------------
-- Other views exposed by PostgREST (definitions in migrations/docs; not inlined)
-- -----------------------------------------------------------------------------
-- vw_noticias_front, vw_pesquisas_front
-- vw_concursos_front, vw_concursos_admin, vw_vestibulares_front
-- vw_fornecedores_front, vw_investimentos_front
-- vw_editais_favoritos_front
-- vw_portais_estrategicos_admin
--
-- RPC: current_app_user_id, current_app_user_is_admin
-- Helpers: editalfinder_text_to_jsonb, editalfinder_text_to_text_array, editalfinder_jsonb_to_text_array
--
-- Tables documented in SQL proposals but NOT in staging PostgREST cache (2026-06):
--   public.organizacao  — frontend admin still references; backend loader optional id_organizacao
--   public.app_feedback — see docs/sql/CREATE_APP_FEEDBACK.sql
--   public.edital_backend_enrichment_shadow — see docs/sql/STAGING_BACKEND_ENRICHMENT_SHADOW_TABLE.sql
--
-- Backend 9–10.1 enrichment (actionability_type, is_noise, validade_status, quality_score):
--   computed in Python (CORE/opportunity_enricher.py); NOT persisted on public.edital in staging.

