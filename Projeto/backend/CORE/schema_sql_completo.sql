-- ============================================================
-- SCHEMA COMPLETO DO BANCO DE DADOS - EDITAL E TABELAS AUXILIARES
-- Execute este SQL no Supabase SQL Editor
-- ============================================================

-- ============================================================
-- 1) CRIAÇÃO DE TABELAS (Caso não existam)
-- ============================================================
create table if not exists public.edital (
  id_edital bigserial primary key,
  titulo text,
  descricao text,
  link text unique,
  fonte_recurso text,
  data_publicacao date,
  prazo_envio date,
  situacao text,
  valor_maximo double precision,
  valor_minimo double precision,
  contrapartida text,
  elegibilidade text,
  contato text,
  link_inscricao text,
  ods text,
  regiao text,
  score integer default 0,
  score_detalhado jsonb,
  justificativa text,
  recomendacao text,
  compatibilidade jsonb,
  pdf_url text,
  objetivo text,
  publico_alvo text,
  temas text,
  id_organizacao bigint,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

-- ============================================================
-- 2) GARANTIR QUE COLUNAS NOVAS EXISTAM (Caso a tabela já existisse antes)
-- ============================================================
do $$
begin
  -- valor_minimo
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'valor_minimo') then
    alter table public.edital add column valor_minimo double precision;
  end if;

  -- contrapartida
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'contrapartida') then
    alter table public.edital add column contrapartida text;
  end if;

  -- elegibilidade
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'elegibilidade') then
    alter table public.edital add column elegibilidade text;
  end if;

  -- contato
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'contato') then
    alter table public.edital add column contato text;
  end if;

  -- link_inscricao
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'link_inscricao') then
    alter table public.edital add column link_inscricao text;
  end if;

  -- ods
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'ods') then
    alter table public.edital add column ods text;
  end if;

  -- regiao
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'regiao') then
    alter table public.edital add column regiao text;
  end if;

  -- score
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'score') then
    alter table public.edital add column score integer default 0;
  end if;

  -- score_detalhado
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'score_detalhado') then
    alter table public.edital add column score_detalhado jsonb;
  end if;

  -- justificativa
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'justificativa') then
    alter table public.edital add column justificativa text;
  end if;

  -- recomendacao
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'recomendacao') then
    alter table public.edital add column recomendacao text;
  end if;

  -- compatibilidade
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'compatibilidade') then
    alter table public.edital add column compatibilidade jsonb;
  end if;

  -- valor_maximo
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'valor_maximo') then
    alter table public.edital add column valor_maximo double precision;
  end if;

  -- publico_alvo
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'publico_alvo') then
    alter table public.edital add column publico_alvo text;
  end if;

  -- temas
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'temas') then
    alter table public.edital add column temas text;
  end if;

  -- atualizado_em
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'atualizado_em') then
    alter table public.edital add column atualizado_em timestamptz not null default now();
  end if;
  
  -- id_organizacao (caso não exista por algum motivo)
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'id_organizacao') then
    alter table public.edital add column id_organizacao bigint;
  end if;

  raise notice 'Colunas validadas/adicionadas com sucesso!';
end $$;

-- ============================================================
-- 3) TABELAS AUXILIARES (Caso não existam)
-- ============================================================
create table if not exists public.edital_anexo (
  id_anexo bigserial primary key,
  id_edital bigint not null references public.edital(id_edital) on delete cascade,
  nome text,
  url text,
  tipo text,
  criado_em timestamptz not null default now()
);

create table if not exists public.edital_extra_campo (
  id_extra bigserial primary key,
  id_edital bigint not null references public.edital(id_edital) on delete cascade,
  chave text not null,
  valor text,
  tipo_dado text,
  ordem integer default 0,
  tamanho_valor integer,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

-- ============================================================
-- 4) ÍNDICES PARA PERFORMANCE (Executados APÓS as colunas existirem)
-- ============================================================
create index if not exists idx_edital_link on public.edital (link);
create index if not exists idx_edital_fonte on public.edital (fonte_recurso);
create index if not exists idx_edital_regiao on public.edital (regiao);
create index if not exists idx_edital_situacao on public.edital (situacao);
create index if not exists idx_edital_valor_max on public.edital (valor_maximo);
create index if not exists idx_edital_valor_min on public.edital (valor_minimo);
create index if not exists idx_edital_org on public.edital (id_organizacao);
create index if not exists idx_edital_anexo_edital on public.edital_anexo (id_edital);
create index if not exists idx_edital_extra_edital on public.edital_extra_campo (id_edital);
create index if not exists idx_edital_extra_chave on public.edital_extra_campo (chave);

-- ============================================================
-- 5) POLÍTICAS RLS (Row Level Security)
-- ============================================================
alter table public.edital enable row level security;
alter table public.edital_anexo enable row level security;
alter table public.edital_extra_campo enable row level security;

-- Limpeza de políticas antigas
drop policy if exists "anon_all_edital" on public.edital;
drop policy if exists "Allow anon all on edital" on public.edital;
drop policy if exists "Allow anon insert on edital" on public.edital;
drop policy if exists "Allow anon select on edital" on public.edital;
drop policy if exists "anon_all_organizacao" on public.organizacao;
drop policy if exists "Allow anon all on organizacao" on public.organizacao;
drop policy if exists "anon_all_edital_anexo" on public.edital_anexo;
drop policy if exists "Allow anon all on edital_anexo" on public.edital_anexo;
drop policy if exists "anon_all_edital_extra_campo" on public.edital_extra_campo;
drop policy if exists "Allow anon all on edital_extra_campo" on public.edital_extra_campo;

-- Novas políticas
create policy "anon_all_edital" on public.edital for all to anon using (true) with check (true);
create policy "anon_all_organizacao" on public.organizacao for all to anon using (true) with check (true);
create policy "anon_all_edital_anexo" on public.edital_anexo for all to anon using (true) with check (true);
create policy "anon_all_edital_extra_campo" on public.edital_extra_campo for all to anon using (true) with check (true);

-- ============================================================
-- 6) ORGANIZAÇÃO PADRÃO (cria se não existir)
-- ============================================================
do $$
begin
  -- Tentativa de inserção robusta da organização padrão
  -- Tratando colunas NOT NULL comuns que possam existir (estado, site, cidade)
  begin
    insert into public.organizacao (id_organizacao, nome, tipo, país, estado, site, cidade)
    values (11, 'Organização Padrão', 'OUTRO', 'Brasil', 'N/A', 'N/A', 'N/A')
    on conflict (id_organizacao) do nothing;
  exception when undefined_column then
    begin
      insert into public.organizacao (id_organizacao, nome, tipo, país, estado, site)
      values (11, 'Organização Padrão', 'OUTRO', 'Brasil', 'N/A', 'N/A')
      on conflict (id_organizacao) do nothing;
    exception when undefined_column then
      begin
        insert into public.organizacao (id_organizacao, nome, tipo, país, estado)
        values (11, 'Organização Padrão', 'OUTRO', 'Brasil', 'N/A')
        on conflict (id_organizacao) do nothing;
      exception when undefined_column then
        insert into public.organizacao (id_organizacao, nome, tipo, país)
        values (11, 'Organização Padrão', 'OUTRO', 'Brasil')
        on conflict (id_organizacao) do nothing;
      end;
    end;
  end;
exception 
  when others then
    raise notice 'Erro ao criar organização padrão: %', SQLERRM;
end $$;

-- ============================================================
-- 7) PROPOSTA EditalFinder — filtros ricos + JSONB (NÃO DESTRUTIVO)
-- Objetivo: alinhar o banco ao modelo padronizado (extras + colunas
-- indexáveis). Revisar políticas RLS e aplicar em ambiente de teste antes
-- de produção. O loader (`CORE/loader.py`) grava estas colunas quando
-- EDITALFINDER_EXTENDED_SCHEMA=true e aplica merge com `extras`.
-- ============================================================

alter table public.edital add column if not exists extras jsonb not null default '{}'::jsonb;

alter table public.edital add column if not exists programa text;
alter table public.edital add column if not exists acao text;
alter table public.edital add column if not exists tipo_recurso text;
alter table public.edital add column if not exists tipo_oportunidade text;
alter table public.edital add column if not exists natureza_recurso text;

alter table public.edital add column if not exists area text[];
alter table public.edital add column if not exists publico_alvo_arr text[];
alter table public.edital add column if not exists setor_economico text[];
alter table public.edital add column if not exists area_cientifica text[];
alter table public.edital add column if not exists area_tecnologica text[];
alter table public.edital add column if not exists setor_estrategico text[];

alter table public.edital add column if not exists pais text;
alter table public.edital add column if not exists estado text;
alter table public.edital add column if not exists municipio text;

alter table public.edital add column if not exists valor_total_texto text;
alter table public.edital add column if not exists moeda text;
alter table public.edital add column if not exists reembolsavel boolean;

alter table public.edital add column if not exists orgao_responsavel text;
alter table public.edital add column if not exists instituicao text;
alter table public.edital add column if not exists orgao_contratante text;
alter table public.edital add column if not exists numero_edital text;
alter table public.edital add column if not exists numero_chamada text;
alter table public.edital add column if not exists codigo_oportunidade text;

alter table public.edital add column if not exists url_detalhe text;

alter table public.edital add column if not exists classificacao_confianca text;
alter table public.edital add column if not exists ativo boolean default true;
alter table public.edital add column if not exists hash_deduplicacao text;
alter table public.edital add column if not exists ultima_coleta timestamptz;

-- Processos / licitações / PNCP (além de codigo_oportunidade)
alter table public.edital add column if not exists numero_processo text;

-- Crédito / financiamento (BNDES, bancos regionais, etc.)
alter table public.edital add column if not exists taxa_juros text;
alter table public.edital add column if not exists carencia text;
alter table public.edital add column if not exists prazo_pagamento text;

-- Internacional / tradução (Ásia e fontes bilíngues)
alter table public.edital add column if not exists titulo_original text;
alter table public.edital add column if not exists descricao_original text;
alter table public.edital add column if not exists titulo_traduzido text;
alter table public.edital add column if not exists descricao_traduzida text;
alter table public.edital add column if not exists idioma_original varchar(32);

-- Resumo textual do PDF (listagens sem abrir extras JSONB)
alter table public.edital add column if not exists pdf_resumo text;

comment on column public.edital.extras is 'Metadados ricos (documentos, cronograma, PDF, classificação); manter sincronizado com colunas de filtro quando possível.';
comment on column public.edital.area is 'Áreas temáticas para filtros do front (text[]); espelho ou suplemento a extras->area.';
comment on column public.edital.publico_alvo_arr is 'Público-alvo múltiplo; coluna separada da legada publico_alvo (text) para não quebrar clientes antigos.';

create index if not exists idx_edital_extras_gin on public.edital using gin (extras);
create index if not exists idx_edital_area_gin on public.edital using gin (area);
create index if not exists idx_edital_publico_alvo_arr_gin on public.edital using gin (publico_alvo_arr);
create index if not exists idx_edital_setor_economico_gin on public.edital using gin (setor_economico);
create index if not exists idx_edital_area_cientifica_gin on public.edital using gin (area_cientifica);
create index if not exists idx_edital_area_tecnologica_gin on public.edital using gin (area_tecnologica);
create index if not exists idx_edital_setor_estrategico_gin on public.edital using gin (setor_estrategico);
create index if not exists idx_edital_tipo_oportunidade on public.edital (tipo_oportunidade);
create index if not exists idx_edital_tipo_recurso_col on public.edital (tipo_recurso);
create index if not exists idx_edital_pais_estado on public.edital (pais, estado);
create index if not exists idx_edital_hash_dedup on public.edital (hash_deduplicacao);
create index if not exists idx_edital_ativo on public.edital (ativo);
create index if not exists idx_edital_ultima_coleta on public.edital (ultima_coleta desc);
create index if not exists idx_edital_numero_processo on public.edital (numero_processo) where numero_processo is not null;
create index if not exists idx_edital_idioma_original on public.edital (idioma_original) where idioma_original is not null;

-- View opcional para o front consumir colunas + resumo de extras sem JSON profundo
create or replace view public.vw_editais_front as
select
  e.id_edital,
  e.titulo,
  e.descricao,
  e.link,
  e.fonte_recurso as fonte,
  e.situacao,
  e.data_publicacao,
  e.prazo_envio as fim_inscricao,
  e.valor_maximo,
  e.valor_minimo,
  e.programa,
  e.acao,
  e.valor_total_texto,
  e.moeda,
  e.reembolsavel,
  e.tipo_recurso,
  e.tipo_oportunidade,
  e.natureza_recurso,
  e.area,
  e.publico_alvo_arr as publico_alvo,
  e.setor_economico,
  e.area_cientifica,
  e.area_tecnologica,
  e.setor_estrategico,
  e.pais,
  e.estado,
  e.municipio,
  e.orgao_responsavel,
  e.instituicao,
  e.orgao_contratante,
  e.numero_edital,
  e.numero_chamada,
  e.codigo_oportunidade,
  e.numero_processo,
  e.taxa_juros,
  e.carencia,
  e.prazo_pagamento,
  e.titulo_original,
  e.descricao_original,
  e.titulo_traduzido,
  e.descricao_traduzida,
  e.idioma_original,
  e.pdf_url,
  e.pdf_resumo,
  e.url_detalhe,
  e.classificacao_confianca,
  e.ativo,
  e.ultima_coleta,
  e.hash_deduplicacao,
  e.atualizado_em,
  e.extras
from public.edital e;

comment on view public.vw_editais_front is 'Camada de leitura para filtros; RLS da tabela base ainda se aplica em consultas diretas à edital.';

-- ============================================================
-- 7c) Histórico de execução de carga
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

-- ============================================================
-- 7d) Histórico de mudanças de edital
-- ============================================================
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

-- ============================================================
-- 7b) edital_extra_campo — metadados por fragmento (bases antigas)
-- ============================================================
do $$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'edital_extra_campo' and column_name = 'atualizado_em'
  ) then
    alter table public.edital_extra_campo add column atualizado_em timestamptz not null default now();
  end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'edital_extra_campo' and column_name = 'tipo_dado'
  ) then
    alter table public.edital_extra_campo add column tipo_dado text;
    comment on column public.edital_extra_campo.tipo_dado is 'Sugestão: json | text | number | boolean — preenchido pelo loader quando disponível.';
  end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'edital_extra_campo' and column_name = 'ordem'
  ) then
    alter table public.edital_extra_campo add column ordem integer default 0;
  end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'edital_extra_campo' and column_name = 'tamanho_valor'
  ) then
    alter table public.edital_extra_campo add column tamanho_valor integer;
    comment on column public.edital_extra_campo.tamanho_valor is 'Comprimento do campo valor (caracteres) para auditoria e limites de UI.';
  end if;
end $$;

create index if not exists idx_edital_extra_tipo on public.edital_extra_campo (tipo_dado) where tipo_dado is not null;
