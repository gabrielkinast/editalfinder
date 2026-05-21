-- =============================================================================
-- RADAR CLIENTE CACHE — proposta de leitura rápida (NÃO EXECUTAR sem revisão)
-- Objetivo: pré-calcular matches por cliente; frontend lê view em vez de JS O(N)
-- Regras de score: devem ser replicadas no job que popula esta tabela (mesma versão)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Tabela de cache
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.radar_cliente_resultado (
    id              bigserial PRIMARY KEY,
    id_cliente      uuid NOT NULL,
    id_edital       uuid NOT NULL,
    score           numeric(5,2) NOT NULL,
    motivos_match   jsonb NOT NULL DEFAULT '[]'::jsonb,
    areas_match     text[] NOT NULL DEFAULT '{}',
    setores_match   text[] NOT NULL DEFAULT '{}',
    compatibilidade text,
    status          text,
    prazo           date,
    calculado_em    timestamptz NOT NULL DEFAULT now(),
    stale           boolean NOT NULL DEFAULT false,
    algorithm_version text NOT NULL DEFAULT 'radar-v1',
    CONSTRAINT radar_cliente_resultado_uniq UNIQUE (id_cliente, id_edital)
);

COMMENT ON TABLE public.radar_cliente_resultado IS
    'Cache de resultados do Radar por par cliente×edital. Populado por job/cron, não no clique do usuário.';

COMMENT ON COLUMN public.radar_cliente_resultado.stale IS
    'true quando cadastro do cliente ou edital mudou após calculado_em e o par precisa ser recalculado.';

COMMENT ON COLUMN public.radar_cliente_resultado.motivos_match IS
    'Espelho estruturado das razões exibidas no card (JSON), sem alterar regra de score na origem.';

-- -----------------------------------------------------------------------------
-- 2. Índices recomendados
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_cliente_score
    ON public.radar_cliente_resultado (id_cliente, score DESC);

CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_cliente_status
    ON public.radar_cliente_resultado (id_cliente, status);

CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_cliente_prazo
    ON public.radar_cliente_resultado (id_cliente, prazo);

CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_edital
    ON public.radar_cliente_resultado (id_edital);

CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_stale
    ON public.radar_cliente_resultado (id_cliente)
    WHERE stale = true;

-- GIN opcional se filtrar por motivos/arrays no SQL
-- CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_motivos_gin
--     ON public.radar_cliente_resultado USING gin (motivos_match);

-- CREATE INDEX IF NOT EXISTS idx_radar_cliente_resultado_areas_gin
--     ON public.radar_cliente_resultado USING gin (areas_match);

-- -----------------------------------------------------------------------------
-- 3. View de leitura para o frontend (joins mínimos)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW public.vw_radar_cliente_front AS
SELECT
    r.id_cliente,
    r.id_edital,
    r.score,
    r.motivos_match,
    r.areas_match,
    r.setores_match,
    r.compatibilidade,
    r.status,
    r.prazo,
    r.calculado_em,
    r.stale,
    e.titulo,
    e.orgao,
    e.area,
    e.tipo_recurso,
    e.link,
    e.data_limite,
    e.status AS edital_status
FROM public.radar_cliente_resultado r
INNER JOIN public.edital e ON e.id_edital = r.id_edital
WHERE r.stale = false;

COMMENT ON VIEW public.vw_radar_cliente_front IS
    'Leitura rápida Radar: filtrar por id_cliente, status, prazo, score. Join mínimo com edital.';

-- Exemplo de consulta esperada pelo frontend (futuro):
-- SELECT * FROM vw_radar_cliente_front
-- WHERE id_cliente = $1 AND score >= $2
-- ORDER BY score DESC
-- LIMIT 500;

-- -----------------------------------------------------------------------------
-- 4. Política de atualização (documentação — implementar no worker)
-- -----------------------------------------------------------------------------
-- a) Inserir/atualizar linhas após batch de scoring (mesma lógica do JS, versionada).
-- b) Marcar stale=true em linhas do cliente quando UPDATE em public.cliente.
-- c) Marcar stale=true em linhas do edital quando INSERT/UPDATE relevante em public.edital.
-- d) Job noturno: recalcular stale por cliente ativo.
-- e) Nunca recalcular no SELECT da view.

-- -----------------------------------------------------------------------------
-- 5. RLS (esboço — AJUSTAR conforme políticas existentes de cliente/edital)
-- -----------------------------------------------------------------------------
-- ALTER TABLE public.radar_cliente_resultado ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY radar_cache_select ON public.radar_cliente_resultado
--     FOR SELECT USING (
--         id_cliente IN (SELECT id_cliente FROM public.cliente WHERE ... ownership ...)
--     );

-- -----------------------------------------------------------------------------
-- 6. ROLLBACK (comentado — executar manualmente se necessário reverter)
-- -----------------------------------------------------------------------------
-- DROP VIEW IF EXISTS public.vw_radar_cliente_front;
-- DROP TABLE IF EXISTS public.radar_cliente_resultado CASCADE;
