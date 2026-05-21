-- =============================================================================
-- Incremental: recência + exclusão cancelado/suspenso em vw_concursos_front
-- =============================================================================
-- Aplicar manualmente em staging/produção após revisão.
-- Não apaga dados em public.concurso_selecao; apenas redefine a view pública.
--
-- Ordem: remover view dependente → recriar front → recriar vestibulares.
-- =============================================================================

DROP VIEW IF EXISTS public.vw_vestibulares_front;

CREATE OR REPLACE VIEW public.vw_concursos_front AS
SELECT
  cs.id_concurso,
  cs.titulo,
  cs.tipo_selecao,
  cs.categoria,
  cs.orgao,
  cs.instituicao,
  cs.banca,
  cs.cargo,
  cs.curso,
  cs.area,
  cs.nivel_escolaridade,
  cs.estado,
  cs.municipio,
  cs.regiao,
  cs.modalidade,
  cs.numero_vagas,
  cs.salario_min,
  cs.salario_max,
  cs.taxa_inscricao,
  cs.data_publicacao,
  cs.data_inicio_inscricao,
  cs.data_fim_inscricao,
  cs.data_prova,
  cs.status,
  cs.link,
  cs.link_edital,
  cs.fonte,
  cs.fonte_tipo,
  cs.validacao_status,
  cs.qualidade_dado,
  cs.tags,
  cs.extras,
  cs.criado_em,
  cs.atualizado_em,
  CASE
    WHEN cs.data_fim_inscricao IS NOT NULL THEN (cs.data_fim_inscricao - CURRENT_DATE)::integer
    ELSE NULL
  END AS dias_ate_fim_inscricao,
  CASE
    WHEN cs.data_prova IS NOT NULL THEN (cs.data_prova - CURRENT_DATE)::integer
    ELSE NULL
  END AS dias_ate_prova,
  CASE
    WHEN cs.data_inicio_inscricao IS NOT NULL AND cs.data_fim_inscricao IS NOT NULL THEN
      CURRENT_DATE BETWEEN cs.data_inicio_inscricao AND cs.data_fim_inscricao
    ELSE false
  END AS inscricoes_abertas,
  CASE
    WHEN cs.data_prova IS NOT NULL THEN
      cs.data_prova >= CURRENT_DATE
      AND cs.data_prova <= (CURRENT_DATE + interval '30 days')::date
    ELSE false
  END AS prova_proxima
FROM public.concurso_selecao cs
WHERE cs.ativo = true
  AND cs.validacao_status IN ('valido', 'incompleto')
  AND cs.status NOT IN ('cancelado', 'suspenso')
  AND (
    (cs.data_fim_inscricao IS NOT NULL AND cs.data_fim_inscricao >= CURRENT_DATE)
    OR (cs.data_prova IS NOT NULL AND cs.data_prova >= CURRENT_DATE)
    OR (
      cs.data_fim_inscricao IS NULL
      AND cs.data_prova IS NULL
      AND (
        cs.criado_em >= (CURRENT_TIMESTAMP - interval '90 days')
        OR (
          cs.data_publicacao IS NOT NULL
          AND cs.data_publicacao >= (CURRENT_DATE - interval '90 days')
        )
      )
    )
  );

CREATE OR REPLACE VIEW public.vw_vestibulares_front AS
SELECT f.*
FROM public.vw_concursos_front f
WHERE f.tipo_selecao IN ('vestibular', 'programa_ingresso', 'bolsa_estudo');

COMMENT ON VIEW public.vw_concursos_front IS
  'Listagem pública: ativo=true; validacao_status em (valido, incompleto); exclui cancelado/suspenso; '
  'recência: fim inscrições ou prova ainda >= hoje, OU sem ambas as datas mas criado_em ou data_publicacao nos últimos 90 dias. '
  'Registos fora desta regra permanecem na tabela e em vw_concursos_admin.';

COMMENT ON VIEW public.vw_vestibulares_front IS
  'Subconjunto da front: vestibular, programa_ingresso, bolsa_estudo.';

-- =============================================================================
-- Fim
-- =============================================================================
