-- =============================================================================
-- PROPOSTA Backend 7 — view com LEFT JOIN na tabela sombra
-- NÃO APLICAR automaticamente. Validar em staging antes de produção.
-- =============================================================================

/*
CREATE OR REPLACE VIEW public.vw_editais_front_with_shadow AS
SELECT
  e.id_edital,
  -- Campos legados preservados
  e.titulo,
  e.descricao,
  e.link,
  e.fonte_recurso,
  e.fonte_recurso AS fonte,
  e.prazo_envio,
  e.prazo_envio AS prazo,
  e.prazo_envio AS fim_inscricao,
  e.area,
  e.setor,
  e.categoria,
  e.extras,
  e.ativo,
  e.situacao,
  e.criado_em,
  e.atualizado_em,

  -- Enriquecimento validado na tabela sombra (opcional)
  s.prazo_data,
  s.prazo_raw,
  s.prazo_status,
  s.prazo_confidence,
  s.prazo_source_field,
  s.tipo_registro,
  s.kind_confidence,
  s.modalidade_normalizada,
  s.modalidade_label,
  s.modalidade_confidence,
  s.escopo_geografico,
  s.escopo_confidence,
  COALESCE(s.fonte_normalizada, e.fonte_recurso) AS fonte_normalizada,
  COALESCE(s.fundo_origem, s.backend_enrichment->>'fundo_origem') AS fundo_origem,
  COALESCE(s.pais_origem, e.pais) AS pais_origem,
  s.source_scope,
  s.area_tematica_normalizada,
  s.area_tematica_label,
  s.area_tematica_confidence,
  COALESCE(s.area_tematica_secondary, '[]'::jsonb) AS area_tematica_secondary,
  COALESCE(s.qualidade_flags, '[]'::jsonb) AS qualidade_flags,
  COALESCE(s.backend_enrichment, '{}'::jsonb) AS backend_enrichment,
  s.enrichment_version,

  (s.prazo_status IN ('vencendo_7', 'vencendo_30', 'prazo_confortavel')) AS is_aberto,
  (s.prazo_status = 'vencendo_7') AS is_vencendo_7,
  (s.prazo_status IN ('vencendo_7', 'vencendo_30')) AS is_vencendo_30

FROM public.edital e
LEFT JOIN public.editais_backend_enrichment_shadow s
  ON s.id_edital = e.id_edital
WHERE e.ativo IS DISTINCT FROM false;
*/

COMMENT ON VIEW public.vw_editais_front_with_shadow IS
  'Proposta Backend 7: ver PROPOSAL_VW_EDITAIS_FRONT_WITH_SHADOW.sql — não aplicada.';
