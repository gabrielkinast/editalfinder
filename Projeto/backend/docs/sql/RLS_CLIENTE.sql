-- =============================================================================
-- EditalFinder — RLS em public.cliente (Supabase Auth)
-- =============================================================================
-- Pré-requisitos:
--   - public.usuario.auth_user_id preenchido e UNIQUE para utilizadores reais;
--   - JWT de sessão presente nos pedidos PostgREST (utilizador com sessão);
--   - Coluna cliente.id_usuario referencia o dono (inteiro da app).
--
-- NÃO executar em produção sem validar em staging.
-- O script NÃO é aplicado automaticamente pelo repositório.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1) Funções auxiliares (SECURITY DEFINER)
-- ---------------------------------------------------------------------------
-- Porquê DEFINER: as policies em `cliente` avaliam estas funções no contexto
-- do invocador (`authenticated`). Sem SELECT em `public.usuario` para esse
-- role, INVOKER falha (permission denied / erro PostgREST). Com DEFINER,
-- a leitura de `usuario` usa os privilégios do dono da função (p.ex. postgres).
-- `auth.uid()` continua a ser o UUID do JWT do utilizador da sessão (Supabase).

CREATE OR REPLACE FUNCTION public.current_app_user_id()
RETURNS bigint
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT u.id_usuario::bigint
  FROM public.usuario AS u
  WHERE u.auth_user_id = auth.uid()
    AND u.status = 'Ativo'
  LIMIT 1;
$$;

COMMENT ON FUNCTION public.current_app_user_id() IS
  'Retorna id_usuario da linha public.usuario com auth_user_id = auth.uid() e status Ativo.';

CREATE OR REPLACE FUNCTION public.current_app_user_is_admin()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.usuario AS u
    WHERE u.auth_user_id = auth.uid()
      AND u.status = 'Ativo'
      AND u.tipo_usuario IN ('Administrador', 'Admin')
  );
$$;

COMMENT ON FUNCTION public.current_app_user_is_admin() IS
  'True se o utilizador autenticado for Administrador ou Admin (status Ativo).';

-- ---------------------------------------------------------------------------
-- 2) RLS
-- ---------------------------------------------------------------------------

ALTER TABLE public.cliente ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 3) Policies (role authenticated — pedidos com JWT de utilizador logado)
-- ---------------------------------------------------------------------------

DROP POLICY IF EXISTS cliente_select_admin_or_owner ON public.cliente;
CREATE POLICY cliente_select_admin_or_owner
  ON public.cliente
  FOR SELECT
  TO authenticated
  USING (
    public.current_app_user_is_admin()
    OR id_usuario = public.current_app_user_id()
  );

DROP POLICY IF EXISTS cliente_insert_admin_or_owner ON public.cliente;
CREATE POLICY cliente_insert_admin_or_owner
  ON public.cliente
  FOR INSERT
  TO authenticated
  WITH CHECK (
    public.current_app_user_is_admin()
    OR (
      id_usuario IS NOT NULL
      AND id_usuario = public.current_app_user_id()
    )
  );

DROP POLICY IF EXISTS cliente_update_admin_or_owner ON public.cliente;
CREATE POLICY cliente_update_admin_or_owner
  ON public.cliente
  FOR UPDATE
  TO authenticated
  USING (
    public.current_app_user_is_admin()
    OR id_usuario = public.current_app_user_id()
  )
  WITH CHECK (
    public.current_app_user_is_admin()
    OR (
      id_usuario = public.current_app_user_id()
      AND public.current_app_user_id() IS NOT NULL
    )
  );

DROP POLICY IF EXISTS cliente_delete_admin_or_owner ON public.cliente;
CREATE POLICY cliente_delete_admin_or_owner
  ON public.cliente
  FOR DELETE
  TO authenticated
  USING (
    public.current_app_user_is_admin()
    OR id_usuario = public.current_app_user_id()
  );

-- ---------------------------------------------------------------------------
-- 4) Grants — authenticated; reduzir superfície para anon
-- ---------------------------------------------------------------------------
-- Nota: o cliente Supabase usa a chave "anon" no header, mas com JWT válido
-- o PostgREST assume o role "authenticated" nas queries.
-- Pedidos sem JWT continuam como "anon" e ficam sem acesso a cliente se
-- revogar privilégios a anon conforme abaixo.

REVOKE ALL ON TABLE public.cliente FROM PUBLIC;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.cliente TO authenticated;

-- anon: sem leitura/escrita direta em cliente (RLS não substitui falta de GRANT)
REVOKE ALL ON TABLE public.cliente FROM anon;

-- Se id_cliente for SERIAL/BIGSERIAL, conceda uso da sequência (ajuste o nome se necessário):
-- GRANT USAGE, SELECT ON SEQUENCE public.cliente_id_cliente_seq TO authenticated;

REVOKE ALL ON FUNCTION public.current_app_user_id() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.current_app_user_is_admin() FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.current_app_user_id() TO authenticated;
GRANT EXECUTE ON FUNCTION public.current_app_user_is_admin() TO authenticated;

-- Opcional: permitir a postgres/service_role via privilégios herdados; service_role
-- no Supabase ignora RLS e mantém bypass para jobs administrativos.

-- =============================================================================
-- ROLLBACK (referência — descomentar e executar manualmente se precisar reverter)
-- =============================================================================
/*
-- Policies
DROP POLICY IF EXISTS cliente_select_admin_or_owner ON public.cliente;
DROP POLICY IF EXISTS cliente_insert_admin_or_owner ON public.cliente;
DROP POLICY IF EXISTS cliente_update_admin_or_owner ON public.cliente;
DROP POLICY IF EXISTS cliente_delete_admin_or_owner ON public.cliente;

-- RLS
ALTER TABLE public.cliente DISABLE ROW LEVEL SECURITY;

-- Funções
DROP FUNCTION IF EXISTS public.current_app_user_id();
DROP FUNCTION IF EXISTS public.current_app_user_is_admin();

-- Repor grants genéricos (ajuste ao modelo anterior do seu projecto)
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.cliente TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.cliente TO authenticated;
GRANT ALL ON TABLE public.cliente TO PUBLIC;
*/
