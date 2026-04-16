-- Políticas RLS para Supabase (executar no SQL Editor DEPOIS das tabelas existirem).
-- Ajusta nomes de schema/tabela se forem diferentes.
--
-- IMPORTANTE:
-- - Com RLS ON e SEM políticas: utilizadores anon/authenticated não conseguem ler
--   nem escrever até existirem políticas para esses papéis.
-- - Na Supabase, a chave service_role costuma IGNORAR RLS no API; mesmo assim
--   podes manter políticas explícitas para documentação ou ferramentas que não
--   usem bypass. Confirma na documentação do teu projeto qual chave o loader usa.
-- - Se o loader usar a chave anon, tens de criar políticas "to anon" (insert/update
--   só se fizer sentido para o teu modelo de segurança).
--
-- Recomendação: service_role só no servidor (.env nunca no frontend).

-- ---------------------------------------------------------------------------
-- 1) Ligar RLS nas tabelas
-- ---------------------------------------------------------------------------
alter table public.organizacao enable row level security;
alter table public.edital enable row level security;
alter table public.edital_anexo enable row level security;
alter table public.edital_extra_campo enable row level security;

-- ---------------------------------------------------------------------------
-- 2) Service role: acesso total (adequado ao loader / scripts na tua máquina)
--    O papel "service_role" já ignora RLS em muitos setups; se mesmo assim
--    precisares de políticas explícitas, usa blocos como estes.
-- ---------------------------------------------------------------------------

-- Organização
drop policy if exists "service_role_all_organizacao" on public.organizacao;
create policy "service_role_all_organizacao"
  on public.organizacao
  for all
  to service_role
  using (true)
  with check (true);

-- Edital
drop policy if exists "service_role_all_edital" on public.edital;
create policy "service_role_all_edital"
  on public.edital
  for all
  to service_role
  using (true)
  with check (true);

-- Anexos (se a tabela existir)
drop policy if exists "service_role_all_edital_anexo" on public.edital_anexo;
create policy "service_role_all_edital_anexo"
  on public.edital_anexo
  for all
  to service_role
  using (true)
  with check (true);

-- Extras JSON (se a tabela existir)
drop policy if exists "service_role_all_edital_extra" on public.edital_extra_campo;
create policy "service_role_all_edital_extra"
  on public.edital_extra_campo
  for all
  to service_role
  using (true)
  with check (true);

-- ---------------------------------------------------------------------------
-- 3) Opcional: leitura pública só para anon (ex.: app só lê editais)
--    Descomenta se quiseres que utilizadores autenticados ou anon leiam.
-- ---------------------------------------------------------------------------
-- drop policy if exists "anon_select_edital" on public.edital;
-- create policy "anon_select_edital"
--   on public.edital
--   for select
--   to anon
--   using (true);
