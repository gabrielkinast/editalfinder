-- =============================================================================
-- FIX_EDITAL_FAVORITO_RLS.sql
-- Corrige RLS de public.edital_favorito: policies MVP usavam id_usuario = 1.
-- Aplicar manualmente em staging/produção após revisão.
-- Não altera schema nem apaga dados.
-- =============================================================================

BEGIN;

DROP POLICY IF EXISTS edital_favorito_select_mvp ON public.edital_favorito;
DROP POLICY IF EXISTS edital_favorito_insert_mvp ON public.edital_favorito;
DROP POLICY IF EXISTS edital_favorito_update_mvp ON public.edital_favorito;

DROP POLICY IF EXISTS edital_favorito_select_own ON public.edital_favorito;
DROP POLICY IF EXISTS edital_favorito_insert_own ON public.edital_favorito;
DROP POLICY IF EXISTS edital_favorito_update_own ON public.edital_favorito;

ALTER TABLE public.edital_favorito ENABLE ROW LEVEL SECURITY;

CREATE POLICY edital_favorito_select_own
ON public.edital_favorito
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1
    FROM public.usuario u
    WHERE u.id_usuario = edital_favorito.id_usuario
      AND u.auth_user_id = auth.uid()
  )
);

CREATE POLICY edital_favorito_insert_own
ON public.edital_favorito
FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1
    FROM public.usuario u
    WHERE u.id_usuario = edital_favorito.id_usuario
      AND u.auth_user_id = auth.uid()
  )
  AND (
    id_edital IS NOT NULL
    OR edital_link IS NOT NULL
  )
);

CREATE POLICY edital_favorito_update_own
ON public.edital_favorito
FOR UPDATE
TO authenticated
USING (
  EXISTS (
    SELECT 1
    FROM public.usuario u
    WHERE u.id_usuario = edital_favorito.id_usuario
      AND u.auth_user_id = auth.uid()
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1
    FROM public.usuario u
    WHERE u.id_usuario = edital_favorito.id_usuario
      AND u.auth_user_id = auth.uid()
  )
);

COMMENT ON TABLE public.edital_favorito IS
  'Favoritos de editais por utilizador (id_usuario BIGINT → public.usuario). '
  'RLS: auth.uid() via usuario.auth_user_id. Soft delete: ativo=false.';

COMMIT;

-- =============================================================================
-- Validação (comentado — executar após aplicar)
-- =============================================================================

-- Ver policies
-- SELECT
--   policyname,
--   roles,
--   cmd,
--   qual,
--   with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
--   AND tablename = 'edital_favorito'
-- ORDER BY policyname;

-- Ver favoritos recentes
-- SELECT
--   f.id_favorito,
--   f.id_usuario,
--   u.auth_user_id,
--   u.nome_email,
--   f.id_edital,
--   f.edital_titulo,
--   f.edital_link,
--   f.ativo,
--   f.criado_em,
--   f.atualizado_em
-- FROM public.edital_favorito f
-- JOIN public.usuario u
--   ON u.id_usuario = f.id_usuario
-- ORDER BY f.atualizado_em DESC
-- LIMIT 20;
