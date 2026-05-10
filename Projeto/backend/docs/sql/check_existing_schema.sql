-- ============================================================
-- EditalFinder — diagnóstico de colunas existentes (somente leitura)
-- Executar no SQL Editor do Supabase (staging) antes/depois da migration aditiva.
-- Não altera dados nem schema.
-- ============================================================

-- Colunas atuais: public.edital
select
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable,
  c.column_default
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'edital'
order by c.ordinal_position;

-- Colunas atuais: public.noticia
select
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable,
  c.column_default
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'noticia'
order by c.ordinal_position;

-- Colunas atuais: public.pesquisa
select
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable,
  c.column_default
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name = 'pesquisa'
order by c.ordinal_position;

-- Resumo: contagem de colunas por tabela alvo
select table_name, count(*) as column_count
from information_schema.columns
where table_schema = 'public'
  and table_name in (
    'edital',
    'noticia',
    'pesquisa',
    'edital_anexo',
    'edital_extra_campo',
    'carga_execucao',
    'edital_historico'
  )
group by table_name
order by table_name;
