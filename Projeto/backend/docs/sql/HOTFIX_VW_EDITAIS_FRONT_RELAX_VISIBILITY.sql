-- =============================================================================
-- HOTFIX_VW_EDITAIS_FRONT_RELAX_VISIBILITY.sql
-- =============================================================================
-- Urgência: a view ficou com ~312 linhas após UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql
-- porque filtros temporais/prazo/recência excluíram ~594 itens além da curadoria Step 1.
--
-- public.edital permanece com 1232 registros; Step 1 marcou 326 em curadoria_front.
-- Esperado na view após hotfix: ~906 (1232 - 326), não 312.
--
-- ANTES DE APLICAR — conferir definição vigente no cluster:
--   SELECT pg_get_viewdef('public.vw_editais_front'::regclass, true);
--
-- Este script usa a mesma lista de colunas de UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql
-- (inclui campos de crédito). Se pg_get_viewdef mostrar colunas diferentes,
-- ajuste o SELECT abaixo para coincidir com o cluster antes do COMMIT.
--
-- Não altera extras.curadoria_front. Não DELETE em public.edital.
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
  AND COALESCE(e.extras -> 'curadoria_front' ->> 'visibility', '') NOT IN (
    'hidden_institutional',
    'hidden_resultado',
    'hidden_duplicate',
    'hidden_invalid_link'
  );

COMMENT ON VIEW public.vw_editais_front IS
  'Hotfix conservador: a view oculta apenas ruídos seguros da curadoria Step 1. Histórico, itens sem prazo e itens em revisão continuam visíveis até revisão da Etapa 2.';

CREATE OR REPLACE VIEW public.vw_editais_admin AS
SELECT * FROM public.vw_editais_front;

COMMIT;

NOTIFY pgrst, 'reload schema';

-- =============================================================================
-- Validações (executar após o hotfix)
-- =============================================================================

-- SELECT COUNT(*) AS total_tabela_edital FROM public.edital;
-- Esperado: 1232 (ou total atual da base)

-- SELECT COUNT(*) AS total_view_editais FROM public.vw_editais_front;
-- Esperado: ~906 (ativos não ocultos pela Step 1)

-- SELECT
--   extras->'curadoria_front'->>'visibility' AS visibility,
--   COUNT(*) AS total
-- FROM public.edital
-- GROUP BY 1
-- ORDER BY total DESC NULLS LAST;

-- SELECT fonte_recurso, COUNT(*) AS total
-- FROM public.vw_editais_front
-- GROUP BY fonte_recurso
-- ORDER BY total DESC;

-- Ruídos Step 1 não devem reaparecer (amostra):
-- SELECT id_edital, titulo, fonte_recurso
-- FROM public.vw_editais_front
-- WHERE titulo ILIKE '%Código de Conduta%'
--    OR titulo ILIKE '%Página inicial%'
--    OR titulo ILIKE '%Resultado Final%'
--    OR titulo ILIKE '%Page Not Found%'
-- ORDER BY fonte_recurso, titulo;
