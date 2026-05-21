-- =============================================================================
-- EditalFinder — EXEMPLOS de políticas RLS (REFERÊNCIA / DISCUSSÃO)
-- =============================================================================
-- NÃO executar como migração cega. Ajustar a:
--   - nomes reais de colunas (ex.: auth_user_id após migração Supabase Auth);
--   - funções helper (ex.: app.current_user_id() se usar JWT custom);
--   - modelo de admin (claim JWT vs tabela de roles).
-- Validar sempre em staging antes de produção.
-- =============================================================================

-- --- Exemplo conceptual: após ligar usuario.auth_user_id a auth.users(id) ---

-- ALTER TABLE public.usuario ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY usuario_select_own_or_admin ON public.usuario
--   FOR SELECT
--   USING (
--     auth.uid() = auth_user_id
--     OR EXISTS (
--       SELECT 1 FROM public.usuario u
--       WHERE u.auth_user_id = auth.uid()
--         AND u.tipo_usuario = 'Administrador'
--     )
--   );

-- CREATE POLICY usuario_update_own ON public.usuario
--   FOR UPDATE
--   USING (auth.uid() = auth_user_id)
--   WITH CHECK (auth.uid() = auth_user_id);

-- --- Exemplo: cliente por dono (id_usuario inteiro da app) ---
-- Requer mapeamento estável auth.uid() -> id_usuario (tabela perfil ou claim).

-- ALTER TABLE public.cliente ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY cliente_select_owner ON public.cliente
--   FOR SELECT
--   USING (
--     id_usuario = (SELECT id_usuario FROM public.usuario WHERE auth_user_id = auth.uid() LIMIT 1)
--     OR EXISTS (SELECT 1 FROM public.usuario WHERE auth_user_id = auth.uid() AND tipo_usuario = 'Administrador')
--   );

-- CREATE POLICY cliente_insert_owner ON public.cliente
--   FOR INSERT
--   WITH CHECK (
--     id_usuario = (SELECT id_usuario FROM public.usuario WHERE auth_user_id = auth.uid() LIMIT 1)
--   );

-- CREATE POLICY cliente_update_owner ON public.cliente
--   FOR UPDATE
--   USING (id_usuario = (SELECT id_usuario FROM public.usuario WHERE auth_user_id = auth.uid() LIMIT 1));

-- --- Exemplo: edital_favorito ---

-- ALTER TABLE public.edital_favorito ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY edital_favorito_all_owner ON public.edital_favorito
--   FOR ALL
--   USING (id_usuario = (SELECT id_usuario FROM public.usuario WHERE auth_user_id = auth.uid() LIMIT 1))
--   WITH CHECK (id_usuario = (SELECT id_usuario FROM public.usuario WHERE auth_user_id = auth.uid() LIMIT 1));

-- =============================================================================
-- Fim dos exemplos. Remover comentários e testar incrementalmente no projeto.
-- =============================================================================
