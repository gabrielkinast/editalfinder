-- =============================================================================
-- PROPOSTA Backend 6 — view vw_editais_front com campos legados + enriquecidos
-- NÃO APLICAR automaticamente. Compatível com frontend atual (campos novos opcionais).
-- =============================================================================

/*
CREATE OR REPLACE VIEW public.vw_editais_front AS
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

  -- Campos novos (opcionais — NULL até migration/backfill)
  e.prazo_data,
  e.prazo_raw,
  e.prazo_status,
  e.prazo_confidence,
  e.prazo_source_field,
  e.tipo_registro,
  e.kind_confidence,
  e.modalidade_normalizada,
  e.modalidade_label,
  e.modalidade_confidence,
  e.escopo_geografico,
  e.escopo_confidence,
  COALESCE(e.fonte_normalizada, e.fonte_recurso) AS fonte_normalizada,
  COALESCE(e.pais_origem, e.pais) AS pais_origem,
  e.source_scope,
  e.area_tematica_normalizada,
  e.area_tematica_label,
  e.area_tematica_confidence,
  COALESCE(e.area_tematica_secondary, '[]'::jsonb) AS area_tematica_secondary,
  COALESCE(e.qualidade_flags, '[]'::jsonb) AS qualidade_flags,
  COALESCE(e.backend_enrichment, '{}'::jsonb) AS backend_enrichment,

  -- Compatibilidade Backend 1 (flags derivadas de prazo_status quando existir)
  (e.prazo_status IN ('vencendo_7', 'vencendo_30', 'prazo_confortavel')) AS is_aberto,
  (e.prazo_status = 'vencendo_7') AS is_vencendo_7,
  (e.prazo_status IN ('vencendo_7', 'vencendo_30')) AS is_vencendo_30,

  e.ativo,
  e.situacao,
  e.criado_em,
  e.atualizado_em
FROM public.edital e
WHERE e.ativo IS DISTINCT FROM false;
*/

-- Fase intermediária (sem ALTER TABLE): expor via extras.backend_enrichment
--   (e.extras->'backend_enrichment'->>'area_tematica_label') AS area_tematica_label
-- até colunas dedicadas existirem.

COMMENT ON VIEW public.vw_editais_front IS
  'Proposta Backend 6: ver PROPOSAL_VW_EDITAIS_FRONT_BACKEND_6.sql — não aplicada.';
