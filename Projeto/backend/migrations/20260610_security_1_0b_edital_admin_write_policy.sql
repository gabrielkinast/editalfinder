-- =============================================================================
-- SECURITY 1.0B — RLS Edital Admin Write + Select Policy Alignment
-- =============================================================================
-- Objetivo: permitir INSERT/UPDATE/SELECT manual em public.edital apenas para
--           utilizadores autenticados reconhecidos como admin pelo banco.
-- Hotfix SELECT: edital_admin_select — necessário para .insert().select().single()
--                e listagem Cadastros → Editais (FRONTEND 1.1I).
--
-- ⚠️  NÃO APLICAR AUTOMATICAMENTE — executar manualmente no Supabase SQL Editor
--     após confirmar estado do cluster (ver docs/SECURITY_1_0B_*.md).
--
-- Pré-requisitos (confirmar com queries manuais antes do apply):
--   1. public.usuario com auth_user_id ligado a auth.users
--   2. Funções current_app_user_* existentes ou criadas abaixo
--   3. Policies existentes de leitura (anon/service_role) preservadas
--   4. Ambiente: staging primeiro, depois produção
--
-- NÃO cria: política de remoção, policy permissiva ampla, escrita anon.
-- NÃO adiciona: created_by / id_usuario em public.edital.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1) Funções auxiliares (idempotente — alinha com RLS_CLIENTE.sql + frontend)
-- ---------------------------------------------------------------------------
-- SECURITY DEFINER + search_path fixo: evita recursão RLS em public.usuario.
-- auth.uid() continua a ser o UUID do JWT da sessão.

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
  'SECURITY 1.0B: id_usuario ativo para auth.uid() (espelha RLS_CLIENTE.sql).';

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
      AND (
        u.tipo_usuario IN ('Administrador', 'Admin')
        OR u.nivel_acesso = 1
      )
  );
$$;

COMMENT ON FUNCTION public.current_app_user_is_admin() IS
  'SECURITY 1.0B: admin se tipo Administrador/Admin OU nivel_acesso=1 e status Ativo.';

-- ---------------------------------------------------------------------------
-- 2) RLS em public.edital (idempotente)
-- ---------------------------------------------------------------------------

ALTER TABLE public.edital ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 3) Policies — authenticated + admin apenas (SELECT / INSERT / UPDATE)
-- ---------------------------------------------------------------------------
-- Não altera SELECT anon existente (anon_select, service_role_all, etc.).
-- Não remove policies legadas — apenas adiciona políticas nomeadas.

DROP POLICY IF EXISTS edital_admin_select ON public.edital;
CREATE POLICY edital_admin_select
  ON public.edital
  FOR SELECT
  TO authenticated
  USING (public.current_app_user_is_admin());

DROP POLICY IF EXISTS edital_admin_insert ON public.edital;
CREATE POLICY edital_admin_insert
  ON public.edital
  FOR INSERT
  TO authenticated
  WITH CHECK (public.current_app_user_is_admin());

DROP POLICY IF EXISTS edital_admin_update ON public.edital;
CREATE POLICY edital_admin_update
  ON public.edital
  FOR UPDATE
  TO authenticated
  USING (public.current_app_user_is_admin())
  WITH CHECK (public.current_app_user_is_admin());

-- ---------------------------------------------------------------------------
-- 4) Grants — authenticated precisa de SELECT/INSERT/UPDATE (RLS filtra)
-- ---------------------------------------------------------------------------
-- service_role mantém bypass RLS para loader/backend.
-- anon: sem INSERT/UPDATE (não ampliar superfície). SELECT anon via policies legadas.

GRANT SELECT, INSERT, UPDATE ON TABLE public.edital TO authenticated;

REVOKE INSERT, UPDATE ON TABLE public.edital FROM anon;

REVOKE ALL ON FUNCTION public.current_app_user_id() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.current_app_user_is_admin() FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.current_app_user_id() TO authenticated;
GRANT EXECUTE ON FUNCTION public.current_app_user_is_admin() TO authenticated;

COMMIT;

-- =============================================================================
-- ROLLBACK (referência — executar manualmente se precisar reverter)
-- =============================================================================
/*
BEGIN;

DROP POLICY IF EXISTS edital_admin_select ON public.edital;
DROP POLICY IF EXISTS edital_admin_insert ON public.edital;
DROP POLICY IF EXISTS edital_admin_update ON public.edital;

REVOKE SELECT, INSERT, UPDATE ON TABLE public.edital FROM authenticated;

-- Opcional: repor função exactamente como RLS_CLIENTE.sql (sem nivel_acesso=1):
-- CREATE OR REPLACE FUNCTION public.current_app_user_is_admin() ...

COMMIT;
*/

-- =============================================================================
-- Pós-apply: validar
-- =============================================================================
-- SELECT policyname, cmd, roles FROM pg_policies
-- WHERE schemaname = 'public' AND tablename = 'edital' ORDER BY policyname;
