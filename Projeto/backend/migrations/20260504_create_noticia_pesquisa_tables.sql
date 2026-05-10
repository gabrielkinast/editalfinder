-- EditalFinder: separa conteudos informativos de oportunidades acionaveis.
-- Objetivo: public.edital fica apenas com editais/oportunidades; noticias e
-- pesquisas passam a ter tabelas proprias.

begin;

create table if not exists public.noticia (
  id_noticia bigserial primary key,
  titulo text,
  resumo text,
  link text unique,
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
  link text unique,
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

create index if not exists idx_noticia_link on public.noticia (link);
create index if not exists idx_noticia_fonte on public.noticia (fonte);
create index if not exists idx_noticia_data_publicacao on public.noticia (data_publicacao desc);
create index if not exists idx_noticia_extras_gin on public.noticia using gin (extras);
create index if not exists idx_noticia_tags_gin on public.noticia using gin (tags);
create index if not exists idx_noticia_hash on public.noticia (hash_deduplicacao);

create index if not exists idx_pesquisa_link on public.pesquisa (link);
create index if not exists idx_pesquisa_fonte on public.pesquisa (fonte);
create index if not exists idx_pesquisa_data_publicacao on public.pesquisa (data_publicacao desc);
create index if not exists idx_pesquisa_extras_gin on public.pesquisa using gin (extras);
create index if not exists idx_pesquisa_tags_gin on public.pesquisa using gin (tags);
create index if not exists idx_pesquisa_hash on public.pesquisa (hash_deduplicacao);

alter table public.noticia enable row level security;
alter table public.pesquisa enable row level security;

drop policy if exists "anon_all_noticia" on public.noticia;
drop policy if exists "anon_all_pesquisa" on public.pesquisa;

create policy "anon_all_noticia" on public.noticia for all to anon using (true) with check (true);
create policy "anon_all_pesquisa" on public.pesquisa for all to anon using (true) with check (true);

create or replace view public.vw_noticias_front as
select
  id_noticia,
  titulo,
  resumo,
  link,
  fonte,
  data_publicacao,
  pais,
  orgao,
  setor_estrategico,
  area_cientifica,
  area_tecnologica,
  idioma,
  tags,
  url_documento,
  extras,
  atualizado_em
from public.noticia;

create or replace view public.vw_pesquisas_front as
select
  id_pesquisa,
  titulo,
  resumo,
  link,
  fonte,
  data_publicacao,
  pais,
  orgao,
  setor_estrategico,
  area_cientifica,
  area_tecnologica,
  idioma,
  tags,
  url_documento,
  extras,
  atualizado_em
from public.pesquisa;

commit;

