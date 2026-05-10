-- Migração proposta EditalFinder — colunas de filtro + extras JSONB + view
-- NÃO executar em produção sem revisão de RLS, backfill e atualização do loader.
-- Modo sugerido: aplicar primeiro em projeto Supabase de staging.
-- Conteúdo espelha a seção 7 de CORE/schema_sql_completo.sql.

begin;

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
  e.atualizado_em,
  e.extras
from public.edital e;

commit;

-- ---------------------------------------------------------------------------
-- BACKFILL (exemplo; rodar separadamente após validar tipos em extras legado)
-- dry-run: comentar o UPDATE e usar SELECT com as mesmas expressões.
--
-- update public.edital e
-- set
--   tipo_oportunidade = coalesce(e.tipo_oportunidade, e.extras->>'tipo_oportunidade'),
--   area = coalesce(e.area, array(select jsonb_array_elements_text(e.extras->'area'))),
--   ultima_coleta = coalesce(e.ultima_coleta, now())
-- where e.extras <> '{}'::jsonb;
-- ---------------------------------------------------------------------------
