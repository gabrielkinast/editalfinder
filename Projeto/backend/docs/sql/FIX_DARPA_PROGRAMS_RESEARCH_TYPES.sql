-- FIX_DARPA_PROGRAMS_RESEARCH_TYPES.sql
-- Corrige tipos e roteamento de DARPA Programs em public.pesquisa após apply com loader antigo.
-- NÃO executar em produção sem revisão. Rodar em staging com BEGIN; … ROLLBACK; primeiro.

-- ---------------------------------------------------------------------------
-- 1) Pré-validação: programas DARPA e possíveis notícias em pesquisa
-- ---------------------------------------------------------------------------

-- Programas (URL canônica) com tipos NULL
SELECT
  id_pesquisa,
  titulo,
  link,
  fonte,
  fonte_recurso,
  tipo_recurso,
  tipo_oportunidade,
  extras ->> 'tipo_pesquisa' AS tipo_pesquisa_extras,
  validacao_status,
  ativo
FROM public.pesquisa
WHERE link ILIKE '%darpa.mil/research/programs/%'
ORDER BY data_publicacao DESC NULLS LAST;

-- Registos com fonte_recurso incorreto (notícia em pesquisa)
SELECT
  p.id_pesquisa,
  p.titulo,
  p.link,
  p.fonte,
  p.fonte_recurso,
  EXISTS (SELECT 1 FROM public.noticia n WHERE n.link = p.link) AS duplicado_em_noticia
FROM public.pesquisa p
WHERE lower(trim(coalesce(p.fonte_recurso, ''))) IN ('darpa news', 'darpa_news')
   OR (p.link ILIKE '%darpa.mil/news/%' AND coalesce(p.fonte_recurso, '') <> 'darpa_programs_research');

-- Contagem antes do fix
SELECT
  count(*) FILTER (WHERE link ILIKE '%darpa.mil/research/programs/%') AS programas_url,
  count(*) FILTER (
    WHERE link ILIKE '%darpa.mil/research/programs/%'
      AND tipo_recurso IS NULL
  ) AS programas_sem_tipo_recurso,
  count(*) FILTER (
    WHERE lower(trim(coalesce(fonte_recurso, ''))) IN ('darpa news', 'darpa_news')
  ) AS pesquisa_fonte_darpa_news
FROM public.pesquisa;

-- ---------------------------------------------------------------------------
-- 2) UPDATE: 25 programas — tipos + fonte + extras.tipo_pesquisa
-- ---------------------------------------------------------------------------

UPDATE public.pesquisa
SET
  fonte = 'DARPA',
  fonte_recurso = 'darpa_programs_research',
  tipo_recurso = 'programa_estrategico',
  tipo_oportunidade = 'pesquisa_estrategica',
  content_type = 'pesquisa',
  extras = coalesce(extras, '{}'::jsonb)
    || jsonb_build_object(
      'tipo_pesquisa', 'programa_pesquisa',
      'tipo_recurso', 'programa_estrategico',
      'tipo_oportunidade', 'pesquisa_estrategica',
      'routing_fix', 'darpa_programs_research_v2',
      'source_id', 'darpa_programs_research'
    ),
  atualizado_em = now()
WHERE link ILIKE '%darpa.mil/research/programs/%'
  AND (
    fonte_recurso IS DISTINCT FROM 'darpa_programs_research'
    OR tipo_recurso IS DISTINCT FROM 'programa_estrategico'
    OR tipo_oportunidade IS DISTINCT FROM 'pesquisa_estrategica'
    OR coalesce(extras ->> 'tipo_pesquisa', '') <> 'programa_pesquisa'
  );

-- ---------------------------------------------------------------------------
-- 3) Desativar DARPA News em public.pesquisa (duplicados em noticia)
-- ---------------------------------------------------------------------------

UPDATE public.pesquisa p
SET
  ativo = false,
  validacao_status = 'descartado_roteamento',
  extras = coalesce(p.extras, '{}'::jsonb)
    || jsonb_build_object(
      'routing_fix', 'darpa_news_nao_pesquisa',
      'motivo', 'noticia_roteada_incorretamente_para_pesquisa',
      'desativado_manual', true
    ),
  atualizado_em = now()
WHERE (
    lower(trim(coalesce(p.fonte_recurso, ''))) IN ('darpa news', 'darpa_news')
    OR p.link ILIKE '%darpa.mil/news/%'
  )
  AND p.ativo IS DISTINCT FROM false
  AND EXISTS (
    SELECT 1 FROM public.noticia n WHERE n.link = p.link
  );

-- Opcional: desativar DARPA News em pesquisa mesmo sem duplicado em noticia
-- UPDATE public.pesquisa p
-- SET ativo = false, validacao_status = 'descartado_roteamento', ...
-- WHERE lower(trim(coalesce(p.fonte_recurso, ''))) IN ('darpa news', 'darpa_news');

-- ---------------------------------------------------------------------------
-- 4) Pós-validação
-- ---------------------------------------------------------------------------

SELECT
  count(*) AS programas_total,
  count(*) FILTER (WHERE tipo_recurso = 'programa_estrategico') AS com_tipo_recurso,
  count(*) FILTER (WHERE tipo_oportunidade = 'pesquisa_estrategica') AS com_tipo_oportunidade,
  count(*) FILTER (WHERE extras ->> 'tipo_pesquisa' = 'programa_pesquisa') AS com_tipo_pesquisa_extras
FROM public.pesquisa
WHERE link ILIKE '%darpa.mil/research/programs/%'
  AND coalesce(ativo, true) = true;

SELECT id_pesquisa, titulo, link, fonte_recurso, tipo_recurso, tipo_oportunidade, extras ->> 'tipo_pesquisa'
FROM public.pesquisa
WHERE link ILIKE '%darpa.mil/research/programs/%'
  AND coalesce(ativo, true) = true
ORDER BY data_publicacao DESC NULLS LAST
LIMIT 30;

SELECT count(*) AS darpa_news_ainda_ativo_em_pesquisa
FROM public.pesquisa
WHERE coalesce(ativo, true) = true
  AND (
    lower(trim(coalesce(fonte_recurso, ''))) IN ('darpa news', 'darpa_news')
    OR link ILIKE '%darpa.mil/news/%'
  );
