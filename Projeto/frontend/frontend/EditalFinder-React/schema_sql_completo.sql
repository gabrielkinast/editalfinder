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
  estado text,
  regiao text,
  score integer default 0,
  score_detalhado jsonb,
  justificativa text,
  recomendacao text,
  compatibilidade jsonb,
  pdf_url text,
  status text default 'Ativo',
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

  -- estado
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'edital' and column_name = 'estado') then
    alter table public.edital add column estado text;
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
  criado_em timestamptz not null default now()
);

-- ============================================================
-- 4) ÍNDICES PARA PERFORMANCE (Executados APÓS as colunas existirem)
-- ============================================================
create index if not exists idx_edital_link on public.edital (link);
create index if not exists idx_edital_fonte on public.edital (fonte_recurso);
create index if not exists idx_edital_estado on public.edital (estado);
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
