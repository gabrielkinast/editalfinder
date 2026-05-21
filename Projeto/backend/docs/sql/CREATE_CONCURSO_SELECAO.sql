-- =============================================================================
-- EditalFinder — Módulo Concursos & Seleções
-- =============================================================================
-- Tabela: public.concurso_selecao
-- Views: public.vw_concursos_front, public.vw_concursos_admin,
--         public.vw_vestibulares_front (opcional)
--
-- NÃO executar automaticamente. Revisar em staging antes de aplicar em
-- produção. Este script NÃO altera public.edital, Radar nem favoritos de
-- edital. NÃO modifica políticas RLS existentes noutras tabelas.
--
-- Ordem sugerida de execução: função trigger → tabela → índices → views.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1) Trigger: atualizar atualizado_em em UPDATE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.touch_concurso_selecao_atualizado_em()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  NEW.atualizado_em := now();
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.touch_concurso_selecao_atualizado_em() IS
  'BEFORE UPDATE em public.concurso_selecao: define atualizado_em = now().';

-- ---------------------------------------------------------------------------
-- 2) Tabela public.concurso_selecao
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.concurso_selecao (
  id_concurso           bigserial PRIMARY KEY,
  titulo                text NOT NULL,
  tipo_selecao          text NOT NULL,
  categoria             text NULL,
  orgao                 text NULL,
  instituicao           text NULL,
  banca                 text NULL,
  cargo                 text NULL,
  curso                 text NULL,
  area                  text NULL,
  nivel_escolaridade    text NULL,
  estado                text NULL,
  municipio             text NULL,
  regiao                text NULL,
  modalidade            text NULL,
  numero_vagas          integer NULL,
  salario_min           numeric NULL,
  salario_max           numeric NULL,
  taxa_inscricao        numeric NULL,
  data_publicacao       date NULL,
  data_inicio_inscricao date NULL,
  data_fim_inscricao    date NULL,
  data_prova            date NULL,
  status                text NOT NULL DEFAULT 'ativo',
  link                  text NOT NULL,
  link_edital           text NULL,
  fonte                 text NOT NULL,
  fonte_tipo            text NULL,
  validacao_status      text NOT NULL DEFAULT 'incompleto',
  qualidade_dado        text NULL,
  tags                  text[] NULL,
  extras                jsonb NOT NULL DEFAULT '{}'::jsonb,
  ativo                 boolean NOT NULL DEFAULT true,
  criado_em             timestamptz NOT NULL DEFAULT now(),
  atualizado_em         timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT concurso_selecao_tipo_selecao_chk CHECK (
    tipo_selecao IN (
      'concurso_publico',
      'processo_seletivo',
      'professor',
      'coordenador',
      'tecnico_administrativo',
      'estagio',
      'residencia',
      'vestibular',
      'bolsa_estudo',
      'programa_ingresso'
    )
  ),

  CONSTRAINT concurso_selecao_status_chk CHECK (
    status IN (
      'ativo',
      'inscricoes_abertas',
      'inscricoes_encerradas',
      'prova_proxima',
      'encerrado',
      'suspenso',
      'cancelado'
    )
  ),

  CONSTRAINT concurso_selecao_validacao_status_chk CHECK (
    validacao_status IN (
      'valido',
      'incompleto',
      'suspeito',
      'acesso_limitado'
    )
  ),

  CONSTRAINT concurso_selecao_fonte_tipo_chk CHECK (
    fonte_tipo IS NULL OR fonte_tipo IN (
      'banca',
      'agregador',
      'instituicao',
      'governo',
      'universidade',
      'vestibular',
      'outro'
    )
  )
);

DROP TRIGGER IF EXISTS trg_concurso_selecao_atualizado_em ON public.concurso_selecao;
CREATE TRIGGER trg_concurso_selecao_atualizado_em
  BEFORE UPDATE ON public.concurso_selecao
  FOR EACH ROW
  EXECUTE PROCEDURE public.touch_concurso_selecao_atualizado_em();

-- ---------------------------------------------------------------------------
-- 3) Unicidade e índices
-- ---------------------------------------------------------------------------
-- Dedupe natural: mesma fonte + mesmo link (evita colidir entre fontes que
-- republicam a mesma URL com metadados diferentes).

CREATE UNIQUE INDEX IF NOT EXISTS uq_concurso_selecao_fonte_link
  ON public.concurso_selecao (fonte, link);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_tipo_selecao
  ON public.concurso_selecao (tipo_selecao);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_estado
  ON public.concurso_selecao (estado);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_municipio
  ON public.concurso_selecao (municipio);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_banca
  ON public.concurso_selecao (banca);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_instituicao
  ON public.concurso_selecao (instituicao);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_data_fim_inscricao
  ON public.concurso_selecao (data_fim_inscricao);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_data_prova
  ON public.concurso_selecao (data_prova);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_status
  ON public.concurso_selecao (status);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_ativo
  ON public.concurso_selecao (ativo);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_tags_gin
  ON public.concurso_selecao USING gin (tags);

CREATE INDEX IF NOT EXISTS idx_concurso_selecao_extras_gin
  ON public.concurso_selecao USING gin (extras jsonb_path_ops);

-- ---------------------------------------------------------------------------
-- 4) Views — front (público filtrado), admin (completo), vestibulares (opcional)
-- ---------------------------------------------------------------------------
-- Nota: dias_* e flags usam CURRENT_DATE (data da sessão do servidor).

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

CREATE OR REPLACE VIEW public.vw_concursos_admin AS
SELECT
  cs.*
FROM public.concurso_selecao cs;

CREATE OR REPLACE VIEW public.vw_vestibulares_front AS
SELECT f.*
FROM public.vw_concursos_front f
WHERE f.tipo_selecao IN ('vestibular', 'programa_ingresso', 'bolsa_estudo');

-- ---------------------------------------------------------------------------
-- 5) Comentários (módulo, tabela, colunas, views)
-- ---------------------------------------------------------------------------

COMMENT ON TABLE public.concurso_selecao IS
  'Módulo Concursos & Seleções: concursos públicos, processos seletivos, docência, '
  'técnicos, residências, vestibulares, bolsas de ingresso. Separado de public.edital '
  '(fomento/Radar).';

COMMENT ON COLUMN public.concurso_selecao.id_concurso IS 'Identificador interno (PK).';
COMMENT ON COLUMN public.concurso_selecao.titulo IS 'Título da oportunidade ou do edital de seleção.';
COMMENT ON COLUMN public.concurso_selecao.tipo_selecao IS
  'Taxonomia principal: concurso_publico, processo_seletivo, professor, etc.';
COMMENT ON COLUMN public.concurso_selecao.status IS
  'Estado operacional do certame (inscrições, prova, encerramento). Distinto da coluna ativo (publicação).';
COMMENT ON COLUMN public.concurso_selecao.ativo IS
  'Soft-delete / despublicação na aplicação. Falso remove da vw_concursos_front.';
COMMENT ON COLUMN public.concurso_selecao.validacao_status IS
  'Qualidade/curadoria: valido e incompleto na front; suspeito e acesso_limitado excluídos da view pública.';
COMMENT ON COLUMN public.concurso_selecao.extras IS
  'JSONB: metadados por crawler (ids externos, URLs raw, hashes de dedupe).';
COMMENT ON COLUMN public.concurso_selecao.tags IS 'Etiquetas livres para filtros e facetas.';
COMMENT ON COLUMN public.concurso_selecao.link IS 'URL canónica do anúncio; parte da unicidade com fonte.';
COMMENT ON COLUMN public.concurso_selecao.fonte IS 'Identificador da origem (ex.: pci_concursos, fuvest).';
COMMENT ON COLUMN public.concurso_selecao.fonte_tipo IS 'Classificação da origem: banca, agregador, governo, etc.';
COMMENT ON COLUMN public.concurso_selecao.link_edital IS 'URL direta do PDF ou página do edital, quando distinta de link.';
COMMENT ON COLUMN public.concurso_selecao.data_inicio_inscricao IS 'Início do período de inscrição (calendário).';
COMMENT ON COLUMN public.concurso_selecao.data_fim_inscricao IS 'Fim do período de inscrição; usado em dias_ate_fim_inscricao na view front.';
COMMENT ON COLUMN public.concurso_selecao.data_prova IS 'Data da prova ou etapa principal; usado em dias_ate_prova e prova_proxima.';
COMMENT ON COLUMN public.concurso_selecao.qualidade_dado IS 'Etiqueta opcional de qualidade (ex.: scraper confiante vs. parcial).';

COMMENT ON VIEW public.vw_concursos_front IS
  'Listagem pública: ativo=true; validacao_status em (valido, incompleto); exclui cancelado/suspenso; '
  'recência: fim inscrições ou prova ainda >= hoje, OU sem ambas as datas mas criado_em ou data_publicacao nos últimos 90 dias. '
  'Registos fora desta regra permanecem na tabela e em vw_concursos_admin.';
COMMENT ON VIEW public.vw_concursos_admin IS
  'Backoffice: todas as linhas e colunas, incl. extras e registos inativos ou com validação restrita.';
COMMENT ON VIEW public.vw_vestibulares_front IS
  'Subconjunto da front: vestibular, programa_ingresso, bolsa_estudo.';

-- =============================================================================
-- Fim do script. Próximos passos (outros ficheiros, não executar daqui):
-- - RLS em public.concurso_selecao + grants para anon/authenticated
-- - Tabelas concurso_favorito / alertas
-- - Loader e crawlers dedicados
-- =============================================================================
