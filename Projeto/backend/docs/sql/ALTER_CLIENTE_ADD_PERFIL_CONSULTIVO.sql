-- Opcional: coluna JSONB para perfil consultivo extenso (contato, fomento, documentação, diagnóstico).
-- Não executar automaticamente. Aplicar manualmente no Supabase/Postgres se `extras` ainda não existir em public.cliente.
--
-- O frontend grava em: extras.perfil_consultivo
-- Campos legados (cidade, estado, cnae_principal, faturamento_anual, etc.) continuam nas colunas existentes.

ALTER TABLE public.cliente
  ADD COLUMN IF NOT EXISTS extras jsonb NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN public.cliente.extras IS
  'Metadados flexíveis; perfil consultivo em extras.perfil_consultivo (Workspace do Consultor).';

-- Índice opcional para consultas futuras por chave (não obrigatório para o MVP):
-- CREATE INDEX IF NOT EXISTS idx_cliente_extras_perfil ON public.cliente USING gin ((extras -> 'perfil_consultivo'));
