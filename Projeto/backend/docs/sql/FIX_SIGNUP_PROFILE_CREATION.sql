-- =============================================================================
-- FIX SIGNUP PROFILE CREATION — incremental (NÃO EXECUTAR sem revisão em staging)
-- Objetivo: evitar auth.users sem linha em public.usuario
-- Regras de negócio padrão novos utilizadores: Consultor, nivel_acesso 2, status Ativo
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Pré-requisitos (verificar manualmente antes de aplicar)
-- -----------------------------------------------------------------------------
-- 1) Coluna public.usuario.auth_user_id uuid UNIQUE (ou índice único parcial)
-- 2) public.usuario.nome_email único ou tratado no ON CONFLICT
-- 3) RLS em public.usuario ENABLE ROW LEVEL SECURITY

-- -----------------------------------------------------------------------------
-- OPÇÃO A — Trigger em auth.users (recomendado com confirmação de e-mail)
-- Cria perfil mesmo quando signUp não devolve session (cliente anon no browser).
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_nome text;
  v_email text;
BEGIN
  v_email := lower(trim(coalesce(NEW.email, '')));
  v_nome := trim(coalesce(NEW.raw_user_meta_data->>'nome', ''));
  IF v_nome = '' THEN
    v_nome := split_part(v_email, '@', 1);
  END IF;
  IF v_nome = '' THEN
    v_nome := 'Utilizador';
  END IF;

  INSERT INTO public.usuario (
    auth_user_id,
    nome,
    nome_email,
    tipo_usuario,
    nivel_acesso,
    status
  )
  VALUES (
    NEW.id,
    v_nome,
    v_email,
    'Consultor',
    2,
    'Ativo'
  )
  ON CONFLICT (auth_user_id) DO NOTHING;

  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.handle_new_auth_user() IS
  'Provisioning automático de public.usuario após INSERT em auth.users (signup Supabase).';

-- Ajustar nome do constraint UNIQUE se no projeto for outro (ex.: usuario_auth_user_id_key)
-- Se auth_user_id não tiver UNIQUE, criar antes:
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_auth_user_id_unique
--   ON public.usuario (auth_user_id) WHERE auth_user_id IS NOT NULL;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_auth_user();

-- -----------------------------------------------------------------------------
-- OPÇÃO B — Policy RLS para INSERT pelo próprio utilizador autenticado
-- Necessária se o frontend criar perfil após signUp COM session (sem trigger).
-- -----------------------------------------------------------------------------

-- ALTER TABLE public.usuario ENABLE ROW LEVEL SECURITY;

-- DROP POLICY IF EXISTS usuario_insert_own ON public.usuario;
-- CREATE POLICY usuario_insert_own
--   ON public.usuario
--   FOR INSERT
--   TO authenticated
--   WITH CHECK (auth.uid() = auth_user_id);

-- DROP POLICY IF EXISTS usuario_select_own ON public.usuario;
-- CREATE POLICY usuario_select_own
--   ON public.usuario
--   FOR SELECT
--   TO authenticated
--   USING (auth.uid() = auth_user_id);

-- -----------------------------------------------------------------------------
-- OPÇÃO C — Documentação frontend (já implementado)
-- - session null → não INSERT; mensagem confirmar e-mail
-- - ensureInternalProfileFromAuthUser no 1º login com JWT
-- -----------------------------------------------------------------------------

-- -----------------------------------------------------------------------------
-- SECÇÃO 4 — Backfill: auth.users sem public.usuario (executar manualmente)
-- -----------------------------------------------------------------------------
-- Pré-visualizar órfãos:
/*
SELECT
  u.id AS auth_id,
  u.email,
  u.created_at
FROM auth.users AS u
LEFT JOIN public.usuario AS p ON p.auth_user_id = u.id
WHERE p.id_usuario IS NULL
ORDER BY u.created_at DESC;
*/

-- Inserir perfis ausentes (idempotente via NOT EXISTS / ON CONFLICT):
/*
INSERT INTO public.usuario (
  auth_user_id,
  nome,
  nome_email,
  tipo_usuario,
  nivel_acesso,
  status
)
SELECT
  u.id,
  coalesce(
    nullif(trim(u.raw_user_meta_data->>'nome'), ''),
    split_part(lower(trim(u.email)), '@', 1),
    'Utilizador'
  ),
  lower(trim(u.email)),
  'Consultor',
  2,
  'Ativo'
FROM auth.users AS u
LEFT JOIN public.usuario AS p ON p.auth_user_id = u.id
WHERE p.id_usuario IS NULL
  AND u.email IS NOT NULL
ON CONFLICT (auth_user_id) DO NOTHING;
*/

-- -----------------------------------------------------------------------------
-- ROLLBACK (comentado — aplicar manualmente se necessário reverter trigger)
-- -----------------------------------------------------------------------------
-- DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
-- DROP FUNCTION IF EXISTS public.handle_new_auth_user();
-- DROP POLICY IF EXISTS usuario_insert_own ON public.usuario;
