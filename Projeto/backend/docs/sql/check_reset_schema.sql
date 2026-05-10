-- =============================================================================
-- Verificação pós-reset (staging / dev) — apenas consultas (read-only)
-- Executar depois de migrations/DANGER_RESET_STAGING_SCHEMA.sql
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1) Colunas principais: public.edital
-- ---------------------------------------------------------------------------
select
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'edital'
order by c.ordinal_position;

-- ---------------------------------------------------------------------------
-- 2) Colunas principais: public.noticia
-- ---------------------------------------------------------------------------
select
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'noticia'
order by c.ordinal_position;

-- ---------------------------------------------------------------------------
-- 3) Colunas principais: public.pesquisa
-- ---------------------------------------------------------------------------
select
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'pesquisa'
order by c.ordinal_position;

-- ---------------------------------------------------------------------------
-- 4) Presença de colunas críticas (esperado: uma linha por chave, exists = t)
-- ---------------------------------------------------------------------------
select v.table_name, v.col, (c.column_name is not null) as col_present
from (
  values
    ('noticia', 'fonte_recurso'),
    ('noticia', 'idioma_original'),
    ('noticia', 'origem_portal'),
    ('pesquisa', 'descricao'),
    ('pesquisa', 'fonte_recurso'),
    ('pesquisa', 'validacao_status'),
    ('edital', 'fonte_recurso'),
    ('edital', 'validacao_status')
) as v(table_name, col)
left join information_schema.columns c
  on c.table_schema = 'public'
 and c.table_name = v.table_name
 and c.column_name = v.col
order by v.table_name, v.col;

-- ---------------------------------------------------------------------------
-- 5) UNIQUE em link (edital, noticia, pesquisa)
-- ---------------------------------------------------------------------------
select
  tc.table_name,
  tc.constraint_name,
  tc.constraint_type,
  string_agg(kcu.column_name, ', ' order by kcu.ordinal_position) as columns
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on tc.constraint_schema = kcu.constraint_schema
 and tc.constraint_name = kcu.constraint_name
 and tc.table_schema = kcu.table_schema
where tc.table_schema = 'public'
  and tc.table_name in ('edital', 'noticia', 'pesquisa')
  and tc.constraint_type in ('UNIQUE', 'PRIMARY KEY')
group by tc.table_name, tc.constraint_name, tc.constraint_type
order by tc.table_name, tc.constraint_type, tc.constraint_name;

-- ---------------------------------------------------------------------------
-- 6) Amostra das views (deve executar sem erro mesmo com 0 linhas)
-- ---------------------------------------------------------------------------
select 'vw_editais_front' as view_name, count(*) as n from public.vw_editais_front;
select * from public.vw_editais_front limit 5;

select 'vw_editais_admin' as view_name, count(*) as n from public.vw_editais_admin;
select * from public.vw_editais_admin limit 5;

select 'vw_noticias_front' as view_name, count(*) as n from public.vw_noticias_front;
select * from public.vw_noticias_front limit 5;

select 'vw_pesquisas_front' as view_name, count(*) as n from public.vw_pesquisas_front;
select * from public.vw_pesquisas_front limit 5;

-- ---------------------------------------------------------------------------
-- 7) Histórico: colunas usadas pelo loader (valor_antigo / valor_novo)
-- ---------------------------------------------------------------------------
select column_name
from information_schema.columns
where table_schema = 'public'
  and table_name = 'edital_historico'
  and column_name in ('valor_antigo', 'valor_novo', 'id_edital', 'id_execucao')
order by column_name;
