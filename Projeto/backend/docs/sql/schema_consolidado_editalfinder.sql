-- ============================================================
-- Projeto: EditalFinder
-- Arquivo: schema_consolidado_editalfinder.sql
-- Data: 2026-05-04
-- Objetivo:
--   - Consolidar o schema principal do backend para documentação/compartilhamento
--   - Permitir criação de ambiente novo (dev/staging) de forma NÃO destrutiva
--
-- Segurança:
--   - Não contém dados reais
--   - Não contém credenciais/URLs sensíveis
--   - Não contém comandos destrutivos (DROP/DELETE/TRUNCATE)
--   - Não executa apply automático
--
-- Ordem recomendada de execução:
--   1) Extensões
--   2) Tabelas base (edital, noticia, pesquisa)
--   3) Tabelas auxiliares (edital_anexo, edital_extra_campo, carga_execucao, edital_historico)
--   4) Índices
--   5) Views
--   6) Comentários
--
-- Ambiente recomendado: desenvolvimento / staging
-- ============================================================

begin;

-- ============================================================
-- 1) Extensões
-- ============================================================
create extension if not exists pgcrypto;

-- ============================================================
-- 2) Tabela principal: public.edital
-- ============================================================
create table if not exists public.edital (
  id_edital bigserial primary key,
  titulo text,
  descricao text,
  fonte_recurso text,
  link text unique,
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
  taxa_juros text,
  carencia text,
  prazo_pagamento text,
  valor_novo text,
  valor_antigo text,
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
  atualizado_em timestamptz not null default now()
);

-- Colunas opcionais/additivas para compatibilidade com versões antigas/novas
alter table public.edital add column if not exists contrapartida text;
alter table public.edital add column if not exists elegibilidade text;
alter table public.edital add column if not exists numero_chamada text;
alter table public.edital add column if not exists titulo_original text;
alter table public.edital add column if not exists descricao_original text;
alter table public.edital add column if not exists titulo_traduzido text;
alter table public.edital add column if not exists descricao_traduzida text;
alter table public.edital add column if not exists url_detalhe text;
alter table public.edital add column if not exists reembolsavel boolean;
alter table public.edital add column if not exists pdf_resumo text;

-- ============================================================
-- 3) Conteúdo roteado: public.noticia / public.pesquisa
-- (alinhado a map_to_content_schema + upsert por link)
-- ============================================================
create table if not exists public.noticia (
  id_noticia bigserial primary key,
  titulo text,
  resumo text,
  conteudo text,
  fonte text,
  fonte_recurso text,
  link text unique,
  data_publicacao date,
  prazo_envio date,
  autor text,
  pais text,
  regiao text,
  idioma text,
  idioma_original text,
  origem_portal text,
  orgao text,
  setor_estrategico text[],
  area_cientifica text[],
  area_tecnologica text[],
  tags text[],
  tipo_conteudo text,
  content_type text not null default 'noticia',
  url_documento text,
  imagem_url text,
  perfil_ideal text[],
  publico_alvo text,
  qualidade_dado integer,
  validacao_status text,
  codigo_oportunidade text,
  numero_chamada text,
  extras jsonb not null default '{}'::jsonb,
  hash_deduplicacao text,
  ultima_coleta timestamptz,
  ativo boolean default true,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create table if not exists public.pesquisa (
  id_pesquisa bigserial primary key,
  titulo text,
  resumo text,
  descricao text,
  fonte text,
  fonte_recurso text,
  link text unique,
  data_publicacao date,
  prazo_envio date,
  pais text,
  regiao text,
  idioma text,
  idioma_original text,
  origem_portal text,
  orgao text,
  setor_estrategico text[],
  area_cientifica text[],
  area_tecnologica text[],
  tags text[],
  perfil_ideal text[],
  publico_alvo text,
  tipo_oportunidade text,
  tipo_recurso text,
  content_type text not null default 'pesquisa',
  url_documento text,
  qualidade_dado integer,
  validacao_status text,
  codigo_oportunidade text,
  numero_chamada text,
  extras jsonb not null default '{}'::jsonb,
  hash_deduplicacao text,
  ultima_coleta timestamptz,
  ativo boolean default true,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

-- ============================================================
-- 4) Tabelas auxiliares
-- ============================================================
create table if not exists public.edital_anexo (
  id_anexo bigserial primary key,
  id_edital bigint not null references public.edital(id_edital) on delete cascade,
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

create table if not exists public.edital_extra_campo (
  id_extra bigserial primary key,
  id_edital bigint not null references public.edital(id_edital) on delete cascade,
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

create table if not exists public.carga_execucao (
  id_execucao uuid primary key default gen_random_uuid(),
  ambiente text not null,
  staging_flag boolean,
  status text,
  apply_status text,
  data_inicio timestamptz default now(),
  data_fim timestamptz,
  duracao_segundos numeric,
  sources jsonb default '[]'::jsonb,
  fontes jsonb default '[]'::jsonb,
  sources_selected integer,
  fontes_carregadas integer,
  sources_excluded integer,
  fontes_excluidas integer,
  fontes_excluidas_detalhe jsonb default '[]'::jsonb,
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
  blocked_sources_loaded jsonb default '[]'::jsonb,
  environment_guard jsonb default '{}'::jsonb,
  summary jsonb default '{}'::jsonb,
  relatorio_json jsonb default '{}'::jsonb,
  criado_em timestamptz default now()
);

create table if not exists public.edital_historico (
  id_historico uuid primary key default gen_random_uuid(),
  id_edital bigint references public.edital(id_edital) on delete cascade,
  id_execucao uuid references public.carga_execucao(id_execucao),
  tipo_evento text not null,
  campo text,
  valor_anterior text,
  valor_novo text,
  valor_antigo text,
  valor_antigo_json jsonb,
  valor_novo_json jsonb,
  diff jsonb,
  metadata jsonb default '{}'::jsonb,
  fonte text,
  criado_em timestamptz default now()
);

-- ============================================================
-- 5) Índices
-- ============================================================
create index if not exists idx_edital_link on public.edital (link);
create index if not exists idx_edital_fonte on public.edital (fonte_recurso);
create index if not exists idx_edital_tipo_oportunidade on public.edital (tipo_oportunidade);
create index if not exists idx_edital_tipo_recurso_col on public.edital (tipo_recurso);
create index if not exists idx_edital_validacao_status on public.edital (validacao_status);
create index if not exists idx_edital_qualidade_dado on public.edital (qualidade_dado);
create index if not exists idx_edital_prazo_envio on public.edital (prazo_envio);
create index if not exists idx_edital_ativo on public.edital (ativo);
create index if not exists idx_edital_hash_dedup on public.edital (hash_deduplicacao);
create index if not exists idx_edital_codigo_oportunidade on public.edital (codigo_oportunidade);
create index if not exists idx_edital_extras_gin on public.edital using gin (extras);
create index if not exists idx_edital_area_cientifica_gin on public.edital using gin (area_cientifica);
create index if not exists idx_edital_area_tecnologica_gin on public.edital using gin (area_tecnologica);
create index if not exists idx_edital_setor_estrategico_gin on public.edital using gin (setor_estrategico);

create index if not exists idx_pesquisa_link on public.pesquisa (link);
create index if not exists idx_pesquisa_codigo_oportunidade on public.pesquisa (codigo_oportunidade);
create index if not exists idx_pesquisa_extras_gin on public.pesquisa using gin (extras);
create index if not exists idx_pesquisa_tags_gin on public.pesquisa using gin (tags);

create index if not exists idx_noticia_link on public.noticia (link);
create index if not exists idx_noticia_codigo_oportunidade on public.noticia (codigo_oportunidade);
create index if not exists idx_noticia_extras_gin on public.noticia using gin (extras);
create index if not exists idx_noticia_tags_gin on public.noticia using gin (tags);

create index if not exists idx_edital_anexo_edital on public.edital_anexo (id_edital);
create index if not exists idx_edital_anexo_url on public.edital_anexo (url);
create index if not exists idx_edital_extra_edital on public.edital_extra_campo (id_edital);
create index if not exists idx_edital_extra_chave on public.edital_extra_campo (chave);
create index if not exists idx_carga_execucao_ambiente on public.carga_execucao (ambiente);
create index if not exists idx_carga_execucao_status on public.carga_execucao (status);
create index if not exists idx_carga_execucao_data_inicio_desc on public.carga_execucao (data_inicio desc);
create index if not exists idx_edital_historico_id_edital on public.edital_historico (id_edital);
create index if not exists idx_edital_historico_tipo_evento on public.edital_historico (tipo_evento);
create index if not exists idx_edital_historico_criado_em_desc on public.edital_historico (criado_em desc);
create index if not exists idx_edital_historico_id_execucao on public.edital_historico (id_execucao);

-- ============================================================
-- 6) Views
-- ============================================================
-- Compatibilidade legada:
-- - `fonte` e `fim_inscricao` são aliases históricos consumidos por clientes antigos.
-- - `fonte_recurso` e `prazo_envio` são os nomes canônicos atuais.
create or replace view public.vw_editais_front as
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

-- Variante opcional útil para administração (inclui inativos)
create or replace view public.vw_editais_admin as
select * from public.vw_editais_front;

-- ============================================================
-- 7) Comentários (documentação do schema)
-- ============================================================
comment on table public.edital is 'Tabela principal de oportunidades/editais normalizados pelo pipeline.';
comment on table public.pesquisa is 'Conteúdos roteados como pesquisa/fomento científico (não inseridos em edital).';
comment on table public.noticia is 'Conteúdos informativos/notícias roteados fora da tabela edital.';
comment on table public.edital_anexo is 'Anexos/documentos vinculados ao edital.';
comment on table public.edital_extra_campo is 'Metadados extras em formato chave/valor por edital.';
comment on table public.carga_execucao is 'Histórico de execuções de carga (dry-run/apply).';
comment on table public.edital_historico is 'Histórico de alterações de campos do edital.';

comment on column public.edital.extras is 'JSONB flexível com metadados de classificação, documentos e auditoria.';
comment on column public.edital.validacao_status is 'Status de validação do conteúdo (ex.: valido, incompleto, suspeito, acesso_limitado).';
comment on column public.edital.qualidade_dado is 'Score numérico de qualidade/completude do item.';
comment on column public.pesquisa.tags is 'Tags em text[] para filtros e busca.';
comment on column public.pesquisa.setor_estrategico is 'Setor estratégico em text[] (evita erro de array literal em upsert).';
comment on column public.noticia.content_type is 'Tipo lógico do conteúdo roteado para noticia.';
comment on view public.vw_editais_front is 'View de leitura para frontend com campos úteis e seguros de edital.';

-- ============================================================
-- 8) RLS / políticas (somente documentação; NÃO ativado por este script)
-- ============================================================
-- Exemplo (avaliar com segurança antes de ativar):
-- alter table public.edital enable row level security;
-- create policy "read_edital_authenticated" on public.edital
--   for select to authenticated
--   using (true);

commit;

