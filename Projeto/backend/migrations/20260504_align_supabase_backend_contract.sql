-- EditalFinder
-- Schema sync patch for Supabase <-> current backend contract
-- Safe goals:
--   - no DROP TABLE / DROP COLUMN / TRUNCATE
--   - create missing tables/columns/indexes
--   - coerce drifted array/json columns to the types the backend expects
--   - keep existing data whenever possible

begin;

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------------

create or replace function public.editalfinder_text_to_jsonb(v text)
returns jsonb
language plpgsql
immutable
as $$
begin
  if v is null or btrim(v) = '' then
    return '{}'::jsonb;
  end if;
  begin
    return v::jsonb;
  exception when others then
    return jsonb_build_object('legacy_text', v);
  end;
end;
$$;

create or replace function public.editalfinder_text_to_text_array(v text)
returns text[]
language plpgsql
immutable
as $$
declare
  trimmed text;
  parsed_json jsonb;
begin
  if v is null then
    return null;
  end if;

  trimmed := btrim(v);
  if trimmed = '' then
    return null;
  end if;

  if left(trimmed, 1) = '[' then
    begin
      parsed_json := trimmed::jsonb;
      return array(
        select btrim(x)
        from jsonb_array_elements_text(parsed_json) as t(x)
        where btrim(x) <> ''
      );
    exception when others then
      null;
    end;
  end if;

  if left(trimmed, 1) = '{' then
    begin
      return array(
        select btrim(x)
        from unnest(trimmed::text[]) as t(x)
        where btrim(x) <> ''
      );
    exception when others then
      null;
    end;
  end if;

  if strpos(trimmed, ',') > 0 then
    return array(
      select btrim(x)
      from unnest(string_to_array(trimmed, ',')) as t(x)
      where btrim(x) <> ''
    );
  end if;

  return array[trimmed];
end;
$$;

create or replace function public.editalfinder_jsonb_to_text_array(v jsonb)
returns text[]
language sql
immutable
as $$
  select case
    when v is null then null
    when jsonb_typeof(v) = 'array' then array(
      select btrim(x)
      from jsonb_array_elements_text(v) as t(x)
      where btrim(x) <> ''
    )
    when jsonb_typeof(v) = 'string' then
      case
        when btrim(trim(both '"' from v::text)) = '' then null
        else array[btrim(trim(both '"' from v::text))]
      end
    else array[btrim(v::text)]
  end
$$;

create or replace function public.editalfinder_touch_atualizado_em()
returns trigger
language plpgsql
as $$
begin
  new.atualizado_em = now();
  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- Core tables used by loader
-- ---------------------------------------------------------------------------

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

-- ---------------------------------------------------------------------------
-- public.edital - base + extended schema expected by CORE/loader.py
-- ---------------------------------------------------------------------------

alter table public.edital add column if not exists situacao text;
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
alter table public.edital add column if not exists numero_processo text;
alter table public.edital add column if not exists taxa_juros text;
alter table public.edital add column if not exists carencia text;
alter table public.edital add column if not exists prazo_pagamento text;
alter table public.edital add column if not exists titulo_original text;
alter table public.edital add column if not exists descricao_original text;
alter table public.edital add column if not exists titulo_traduzido text;
alter table public.edital add column if not exists descricao_traduzida text;
alter table public.edital add column if not exists idioma_original text;
alter table public.edital add column if not exists pdf_resumo text;

-- ---------------------------------------------------------------------------
-- public.noticia / public.pesquisa - exact contract used by map_to_content_schema
-- ---------------------------------------------------------------------------

create table if not exists public.noticia (
  id_noticia bigserial primary key,
  titulo text,
  resumo text,
  link text,
  fonte text,
  data_publicacao date,
  pais text,
  orgao text,
  setor_estrategico text[],
  area_cientifica text[],
  area_tecnologica text[],
  idioma text,
  tags text[],
  url_documento text,
  content_type text not null default 'noticia',
  extras jsonb not null default '{}'::jsonb,
  hash_deduplicacao text,
  ultima_coleta timestamptz,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create table if not exists public.pesquisa (
  id_pesquisa bigserial primary key,
  titulo text,
  resumo text,
  link text,
  fonte text,
  data_publicacao date,
  pais text,
  orgao text,
  setor_estrategico text[],
  area_cientifica text[],
  area_tecnologica text[],
  idioma text,
  tags text[],
  url_documento text,
  content_type text not null default 'pesquisa',
  extras jsonb not null default '{}'::jsonb,
  hash_deduplicacao text,
  ultima_coleta timestamptz,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

alter table public.noticia add column if not exists titulo text;
alter table public.noticia add column if not exists resumo text;
alter table public.noticia add column if not exists link text;
alter table public.noticia add column if not exists fonte text;
alter table public.noticia add column if not exists data_publicacao date;
alter table public.noticia add column if not exists pais text;
alter table public.noticia add column if not exists orgao text;
alter table public.noticia add column if not exists setor_estrategico text[];
alter table public.noticia add column if not exists area_cientifica text[];
alter table public.noticia add column if not exists area_tecnologica text[];
alter table public.noticia add column if not exists idioma text;
alter table public.noticia add column if not exists tags text[];
alter table public.noticia add column if not exists url_documento text;
alter table public.noticia add column if not exists content_type text;
alter table public.noticia add column if not exists extras jsonb not null default '{}'::jsonb;
alter table public.noticia add column if not exists hash_deduplicacao text;
alter table public.noticia add column if not exists ultima_coleta timestamptz;
alter table public.noticia add column if not exists criado_em timestamptz not null default now();
alter table public.noticia add column if not exists atualizado_em timestamptz not null default now();

alter table public.pesquisa add column if not exists titulo text;
alter table public.pesquisa add column if not exists resumo text;
alter table public.pesquisa add column if not exists link text;
alter table public.pesquisa add column if not exists fonte text;
alter table public.pesquisa add column if not exists data_publicacao date;
alter table public.pesquisa add column if not exists pais text;
alter table public.pesquisa add column if not exists orgao text;
alter table public.pesquisa add column if not exists setor_estrategico text[];
alter table public.pesquisa add column if not exists area_cientifica text[];
alter table public.pesquisa add column if not exists area_tecnologica text[];
alter table public.pesquisa add column if not exists idioma text;
alter table public.pesquisa add column if not exists tags text[];
alter table public.pesquisa add column if not exists url_documento text;
alter table public.pesquisa add column if not exists content_type text;
alter table public.pesquisa add column if not exists extras jsonb not null default '{}'::jsonb;
alter table public.pesquisa add column if not exists hash_deduplicacao text;
alter table public.pesquisa add column if not exists ultima_coleta timestamptz;
alter table public.pesquisa add column if not exists criado_em timestamptz not null default now();
alter table public.pesquisa add column if not exists atualizado_em timestamptz not null default now();

-- ---------------------------------------------------------------------------
-- Coerce drifted column types to what the backend expects
-- ---------------------------------------------------------------------------

do $$
declare
  rec record;
  v_data_type text;
  v_udt_name text;
begin
  for rec in
    select *
    from (
      values
        ('edital',   'area'),
        ('edital',   'publico_alvo_arr'),
        ('edital',   'setor_economico'),
        ('edital',   'area_cientifica'),
        ('edital',   'area_tecnologica'),
        ('edital',   'setor_estrategico'),
        ('noticia',  'setor_estrategico'),
        ('noticia',  'area_cientifica'),
        ('noticia',  'area_tecnologica'),
        ('noticia',  'tags'),
        ('pesquisa', 'setor_estrategico'),
        ('pesquisa', 'area_cientifica'),
        ('pesquisa', 'area_tecnologica'),
        ('pesquisa', 'tags')
    ) as t(table_name, column_name)
  loop
    select c.data_type, c.udt_name
      into v_data_type, v_udt_name
    from information_schema.columns c
    where c.table_schema = 'public'
      and c.table_name = rec.table_name
      and c.column_name = rec.column_name;

    if v_udt_name is null then
      continue;
    end if;

    if v_udt_name <> '_text' then
      if v_data_type = 'jsonb' then
        execute format(
          'alter table public.%I alter column %I type text[] using public.editalfinder_jsonb_to_text_array(%I)',
          rec.table_name,
          rec.column_name,
          rec.column_name
        );
      else
        execute format(
          'alter table public.%I alter column %I type text[] using public.editalfinder_text_to_text_array(%I::text)',
          rec.table_name,
          rec.column_name,
          rec.column_name
        );
      end if;
    end if;
  end loop;
end $$;

do $$
declare
  rec record;
  v_data_type text;
begin
  for rec in
    select *
    from (
      values
        ('edital', 'extras'),
        ('noticia', 'extras'),
        ('pesquisa', 'extras')
    ) as t(table_name, column_name)
  loop
    select c.data_type
      into v_data_type
    from information_schema.columns c
    where c.table_schema = 'public'
      and c.table_name = rec.table_name
      and c.column_name = rec.column_name;

    if v_data_type is null then
      continue;
    end if;

    if v_data_type <> 'jsonb' then
      execute format(
        'alter table public.%I alter column %I type jsonb using public.editalfinder_text_to_jsonb(%I::text)',
        rec.table_name,
        rec.column_name,
        rec.column_name
      );
    end if;

    execute format(
      'alter table public.%I alter column %I set default ''{}''::jsonb',
      rec.table_name,
      rec.column_name
    );
  end loop;
end $$;

update public.noticia
set content_type = 'noticia'
where content_type is null or btrim(content_type) = '';

update public.pesquisa
set content_type = 'pesquisa'
where content_type is null or btrim(content_type) = '';

alter table public.noticia alter column content_type set default 'noticia';
alter table public.pesquisa alter column content_type set default 'pesquisa';

-- ---------------------------------------------------------------------------
-- Indexes required for upsert / filtering
-- ---------------------------------------------------------------------------

create index if not exists idx_edital_link on public.edital (link);
create index if not exists idx_edital_fonte on public.edital (fonte_recurso);
create index if not exists idx_edital_anexo_edital on public.edital_anexo (id_edital);
create index if not exists idx_edital_extra_edital on public.edital_extra_campo (id_edital);
create index if not exists idx_edital_extra_chave on public.edital_extra_campo (chave);
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
create index if not exists idx_edital_numero_processo on public.edital (numero_processo);

create index if not exists idx_carga_execucao_ambiente on public.carga_execucao (ambiente);
create index if not exists idx_carga_execucao_status on public.carga_execucao (status);
create index if not exists idx_carga_execucao_data_inicio_desc on public.carga_execucao (data_inicio desc);
create index if not exists idx_edital_historico_id_edital on public.edital_historico (id_edital);
create index if not exists idx_edital_historico_tipo_evento on public.edital_historico (tipo_evento);
create index if not exists idx_edital_historico_criado_em_desc on public.edital_historico (criado_em desc);
create index if not exists idx_edital_historico_id_execucao on public.edital_historico (id_execucao);

create index if not exists idx_noticia_fonte on public.noticia (fonte);
create index if not exists idx_noticia_data_publicacao on public.noticia (data_publicacao desc);
create index if not exists idx_noticia_hash on public.noticia (hash_deduplicacao);
create index if not exists idx_noticia_extras_gin on public.noticia using gin (extras);
create index if not exists idx_noticia_tags_gin on public.noticia using gin (tags);
create index if not exists idx_noticia_area_cientifica_gin on public.noticia using gin (area_cientifica);
create index if not exists idx_noticia_area_tecnologica_gin on public.noticia using gin (area_tecnologica);
create index if not exists idx_noticia_setor_estrategico_gin on public.noticia using gin (setor_estrategico);

create index if not exists idx_pesquisa_fonte on public.pesquisa (fonte);
create index if not exists idx_pesquisa_data_publicacao on public.pesquisa (data_publicacao desc);
create index if not exists idx_pesquisa_hash on public.pesquisa (hash_deduplicacao);
create index if not exists idx_pesquisa_extras_gin on public.pesquisa using gin (extras);
create index if not exists idx_pesquisa_tags_gin on public.pesquisa using gin (tags);
create index if not exists idx_pesquisa_area_cientifica_gin on public.pesquisa using gin (area_cientifica);
create index if not exists idx_pesquisa_area_tecnologica_gin on public.pesquisa using gin (area_tecnologica);
create index if not exists idx_pesquisa_setor_estrategico_gin on public.pesquisa using gin (setor_estrategico);

do $$
begin
  begin
    create unique index if not exists uq_noticia_link on public.noticia (link);
  exception when others then
    raise notice 'uq_noticia_link not created: %', sqlerrm;
  end;
  begin
    create unique index if not exists uq_pesquisa_link on public.pesquisa (link);
  exception when others then
    raise notice 'uq_pesquisa_link not created: %', sqlerrm;
  end;
end $$;

-- ---------------------------------------------------------------------------
-- Touch triggers for atualizado_em
-- ---------------------------------------------------------------------------

drop trigger if exists trg_edital_touch_atualizado_em on public.edital;
create trigger trg_edital_touch_atualizado_em
before update on public.edital
for each row execute function public.editalfinder_touch_atualizado_em();

drop trigger if exists trg_noticia_touch_atualizado_em on public.noticia;
create trigger trg_noticia_touch_atualizado_em
before update on public.noticia
for each row execute function public.editalfinder_touch_atualizado_em();

drop trigger if exists trg_pesquisa_touch_atualizado_em on public.pesquisa;
create trigger trg_pesquisa_touch_atualizado_em
before update on public.pesquisa
for each row execute function public.editalfinder_touch_atualizado_em();

drop trigger if exists trg_edital_extra_campo_touch_atualizado_em on public.edital_extra_campo;
create trigger trg_edital_extra_campo_touch_atualizado_em
before update on public.edital_extra_campo
for each row execute function public.editalfinder_touch_atualizado_em();

-- ---------------------------------------------------------------------------
-- Front views
-- ---------------------------------------------------------------------------

drop view if exists public.vw_editais_front;
create view public.vw_editais_front as
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
  e.tipo_recurso,
  e.tipo_oportunidade,
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
  e.pdf_url,
  e.url_detalhe,
  e.classificacao_confianca,
  e.ativo,
  e.hash_deduplicacao,
  e.ultima_coleta,
  e.atualizado_em,
  e.extras
from public.edital e;

drop view if exists public.vw_noticias_front;
create view public.vw_noticias_front as
select
  n.id_noticia,
  n.titulo,
  n.resumo,
  n.link,
  n.fonte,
  n.data_publicacao,
  n.pais,
  n.orgao,
  n.setor_estrategico,
  n.area_cientifica,
  n.area_tecnologica,
  n.idioma,
  n.tags,
  n.url_documento,
  n.content_type,
  n.hash_deduplicacao,
  n.ultima_coleta,
  n.atualizado_em,
  n.extras
from public.noticia n;

drop view if exists public.vw_pesquisas_front;
create view public.vw_pesquisas_front as
select
  p.id_pesquisa,
  p.titulo,
  p.resumo,
  p.link,
  p.fonte,
  p.data_publicacao,
  p.pais,
  p.orgao,
  p.setor_estrategico,
  p.area_cientifica,
  p.area_tecnologica,
  p.idioma,
  p.tags,
  p.url_documento,
  p.content_type,
  p.hash_deduplicacao,
  p.ultima_coleta,
  p.atualizado_em,
  p.extras
from public.pesquisa p;

commit;
