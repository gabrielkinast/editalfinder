-- =============================================================================
-- Incremental: public.vw_pesquisas_front — apenas registros ativos (+ recência 24m)
-- =============================================================================
-- Aplicar manualmente em staging/produção após revisão.
-- Não altera public.pesquisa; não apaga linhas (ativo=false permanecem como histórico).
--
-- Schema real: public.pesquisa.id (uuid), não id_pesquisa.
-- A view expõe p.id e p.id AS id_pesquisa para compatibilidade com o frontend.
--
-- Diagnóstico antes/depois:
--   SELECT pg_get_viewdef('public.vw_pesquisas_front'::regclass, true);
--
-- Problema corrigido: registros com ativo=false (ex.: DARPA News desativados após
-- roteamento incorreto) ainda apareciam na listagem pública.
-- =============================================================================

BEGIN;

DROP VIEW IF EXISTS public.vw_pesquisas_front;

CREATE VIEW public.vw_pesquisas_front AS
SELECT
  p.id,
  p.id AS id_pesquisa,
  p.titulo,
  p.descricao,
  p.resumo,
  p.link,
  p.data_publicacao,
  p.prazo_envio,
  p.prazo_envio AS fim_inscricao,
  p.fonte_recurso,
  COALESCE(p.fonte_recurso, p.fonte) AS fonte,
  p.fonte AS fonte_legado,
  p.tipo_pesquisa,
  p.tipo_oportunidade,
  p.tipo_recurso,
  p.area_cientifica,
  p.area_tecnologica,
  p.setor_estrategico,
  p.tags,
  p.perfil_ideal,
  p.publico_alvo,
  p.validacao_status,
  p.qualidade_dado,
  p.pdf_url,
  p.url_documento,
  p.documentos,
  p.pais,
  p.regiao,
  p.idioma,
  p.idioma_original,
  p.origem_portal,
  p.codigo_oportunidade,
  p.numero_chamada,
  p.content_type,
  p.extras,
  p.ativo,
  p.hash_deduplicacao,
  p.ultima_coleta,
  p.criado_em,
  p.atualizado_em
FROM public.pesquisa p
WHERE COALESCE(p.ativo, true) = true
  AND (
    p.data_publicacao IS NULL
    OR p.data_publicacao >= (CURRENT_DATE - INTERVAL '24 months')::date
  );

COMMENT ON VIEW public.vw_pesquisas_front IS
  'Listagem pública de pesquisas/artigos (aba Pesquisas). Chave primária: public.pesquisa.id (uuid), '
  'exposta também como id_pesquisa para compatibilidade legada. '
  'Inclui apenas registros com ativo=true (ativo NULL tratado como ativo). '
  'Registos com ativo=false permanecem em public.pesquisa como histórico e não aparecem aqui. '
  'Recência: data_publicacao nos últimos 24 meses ou data_publicacao ausente. '
  'Ver docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md §3.';

COMMIT;

-- Recarregar cache PostgREST (Supabase)
NOTIFY pgrst, 'reload schema';

-- =============================================================================
-- Validação (executar após COMMIT)
-- =============================================================================

-- Inativos na tabela (não devem aparecer na view):
-- SELECT id, titulo, fonte_recurso, ativo
-- FROM public.pesquisa
-- WHERE COALESCE(ativo, true) = false
--   AND (fonte_recurso ILIKE '%darpa%' OR fonte ILIKE '%darpa%');

-- SELECT id, id_pesquisa, titulo, fonte_recurso, ativo
-- FROM public.vw_pesquisas_front
-- WHERE fonte_recurso ILIKE '%darpa%' OR fonte ILIKE '%darpa%';

SELECT
  fonte_recurso,
  COUNT(*) AS total
FROM public.vw_pesquisas_front
WHERE fonte_recurso ILIKE '%darpa%'
   OR fonte ILIKE '%darpa%'
GROUP BY fonte_recurso
ORDER BY fonte_recurso;

-- Esperado:
--   darpa_programs_research | 25
--   (DARPA News / darpa_news não deve aparecer — ativo=false na tabela base)
