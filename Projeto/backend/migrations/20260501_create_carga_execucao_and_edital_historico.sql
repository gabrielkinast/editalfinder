-- ============================================================
-- Migration: cria tabelas de histórico de carga e de edital
-- Data: 2026-05-01
-- Segurança: apenas CREATE TABLE/INDEX IF NOT EXISTS
-- ============================================================

create extension if not exists pgcrypto;

create table if not exists public.carga_execucao (
  id_execucao uuid primary key default gen_random_uuid(),
  ambiente text not null,
  status text not null,
  data_inicio timestamptz default now(),
  data_fim timestamptz,
  duracao_segundos numeric,
  fontes_carregadas integer,
  fontes_excluidas integer,
  itens_processados integer,
  itens_inseridos integer,
  itens_atualizados integer,
  itens_ignorados integer,
  erros integer,
  fontes jsonb default '[]'::jsonb,
  fontes_excluidas_detalhe jsonb default '[]'::jsonb,
  blocked_sources_loaded jsonb default '[]'::jsonb,
  environment_guard jsonb default '{}'::jsonb,
  relatorio_json jsonb default '{}'::jsonb,
  criado_em timestamptz default now()
);

create index if not exists idx_carga_execucao_ambiente on public.carga_execucao (ambiente);
create index if not exists idx_carga_execucao_status on public.carga_execucao (status);
create index if not exists idx_carga_execucao_data_inicio_desc on public.carga_execucao (data_inicio desc);
create index if not exists idx_carga_execucao_erros on public.carga_execucao (erros);
create index if not exists idx_carga_execucao_itens_processados on public.carga_execucao (itens_processados);

create table if not exists public.edital_historico (
  id_historico uuid primary key default gen_random_uuid(),
  id_edital bigint references public.edital(id_edital) on delete cascade,
  tipo_evento text not null,
  campo text,
  valor_antigo text,
  valor_novo text,
  valor_antigo_json jsonb,
  valor_novo_json jsonb,
  fonte text,
  id_execucao uuid,
  metadata jsonb default '{}'::jsonb,
  criado_em timestamptz default now()
);

create index if not exists idx_edital_historico_id_edital on public.edital_historico (id_edital);
create index if not exists idx_edital_historico_tipo_evento on public.edital_historico (tipo_evento);
create index if not exists idx_edital_historico_criado_em_desc on public.edital_historico (criado_em desc);
create index if not exists idx_edital_historico_id_execucao on public.edital_historico (id_execucao);
