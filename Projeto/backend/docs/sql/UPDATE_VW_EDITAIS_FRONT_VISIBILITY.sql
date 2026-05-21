-- =============================================================================
-- UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql
-- =============================================================================
-- Incremental: filtrar ruído na listagem pública sem apagar public.edital.
--
-- ANTES DE APLICAR EM PRODUÇÃO:
--   SELECT pg_get_viewdef('public.vw_editais_front'::regclass, true);
--   Confirmar colunas extras (crédito) do DDL vigente no cluster.
--
-- Ordem: DROP vw_editais_admin → CREATE vw_editais_front → CREATE vw_editais_admin
-- =============================================================================

BEGIN;

DROP VIEW IF EXISTS public.vw_editais_admin;
DROP VIEW IF EXISTS public.vw_editais_front;

CREATE OR REPLACE VIEW public.vw_editais_front AS
SELECT
  e.id_edital AS id,
  e.titulo,
  e.descricao,
  e.fonte_recurso,
  e.fonte_recurso AS fonte,
  e.link,
  e.pdf_url,
  e.prazo_envio,
  e.prazo_envio AS fim_inscricao,
  e.data_publicacao,
  e.tipo_oportunidade,
  e.tipo_recurso,
  e.natureza_recurso,
  e.reembolsavel,
  e.linha_credito,
  e.modalidade_financiamento,
  e.taxa_juros,
  e.prazo_carencia,
  e.prazo_amortizacao,
  e.contrapartida,
  e.garantias,
  e.valor_minimo,
  e.valor_maximo,
  e.perfil_ideal,
  e.publico_alvo_arr AS publico_alvo,
  e.area_cientifica,
  e.area_tecnologica,
  e.setor_estrategico,
  e.setor_economico,
  e.pais,
  e.regiao,
  e.uf,
  e.validacao_status,
  e.qualidade_dado,
  e.classificacao_confianca,
  e.ativo,
  e.situacao,
  e.extras,
  e.criado_em,
  e.atualizado_em
FROM public.edital e
WHERE COALESCE(e.ativo, TRUE) = TRUE
  -- Curadoria explícita (extras.curadoria_front.visibility)
  AND COALESCE(e.extras -> 'curadoria_front' ->> 'visibility', '') NOT IN (
    'hidden_institutional',
    'hidden_historical',
    'hidden_resultado',
    'hidden_invalid_link',
    'hidden_not_opportunity',
    'hidden_duplicate',
    'hidden_expired'
  )
  AND (
    -- A) Prazo futuro
    (e.prazo_envio IS NOT NULL AND e.prazo_envio >= CURRENT_DATE)
    -- B) Fluxo contínuo (metadado ou texto)
    OR COALESCE(e.extras ->> 'status_prazo', '') IN ('fluxo_continuo', 'fluxo continuo', 'continuous', 'rolling')
    OR COALESCE(e.situacao, '') ILIKE '%fluxo%continu%'
    OR COALESCE(e.situacao, '') ILIKE '%permanente%'
    -- C) Curadoria manual / visível explícita
    OR COALESCE(e.extras -> 'curadoria_front' ->> 'visibility', '') IN (
      'visible_current',
      'visible_continuous_flow',
      'visible_recent_strong_signal',
      'visible_manual_reviewed'
    )
    -- D) Recente + qualidade (sem prazo, sinal forte via curadoria ou qualidade)
    OR (
      e.data_publicacao IS NOT NULL
      AND e.data_publicacao >= (CURRENT_DATE - INTERVAL '12 months')
      AND COALESCE(e.qualidade_dado, 0) >= 60
      AND COALESCE(e.validacao_status, '') IN ('valido', 'incompleto')
    )
    -- E) Alta qualidade validada (fallback conservador)
    OR (
      COALESCE(e.validacao_status, '') = 'valido'
      AND COALESCE(e.qualidade_dado, 0) >= 80
      AND (
        e.prazo_envio IS NULL
        OR e.prazo_envio >= (CURRENT_DATE - INTERVAL '30 days')
      )
    )
    -- F) Revisão visível sob demanda (itens em revisão permanecem fora até curadoria positiva)
    -- (review_* não entram por padrão)
  );

COMMENT ON VIEW public.vw_editais_front IS
  'Listagem pública Editais: ativo + curadoria_front + recência/prazo/fluxo contínuo. Histórico permanece em public.edital.';

CREATE OR REPLACE VIEW public.vw_editais_admin AS
SELECT * FROM public.vw_editais_front;

COMMIT;

-- Validação sugerida (após apply manual):
-- SELECT fonte_recurso, COUNT(*) AS total
-- FROM public.vw_editais_front
-- GROUP BY fonte_recurso
-- ORDER BY total DESC;
