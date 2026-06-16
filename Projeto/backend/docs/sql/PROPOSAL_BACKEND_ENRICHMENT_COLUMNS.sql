-- =============================================================================
-- PROPOSTA Backend 6 — colunas de enriquecimento na tabela public.edital
-- NÃO APLICAR automaticamente. Revisar após dry-run Backend 6 aprovado.
-- =============================================================================

-- Exemplo documental (não executar em produção sem migration controlada):

/*
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_data date NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_raw text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_status text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_confidence text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_source_field text NULL;

ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS tipo_registro text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS kind_confidence text NULL;

ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS modalidade_normalizada text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS modalidade_label text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS modalidade_confidence text NULL;

ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS escopo_geografico text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS escopo_confidence text NULL;

ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS fonte_normalizada text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS pais_origem text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS source_scope text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS fundo_origem text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS programa_fundo text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS source_notes jsonb DEFAULT '[]'::jsonb;

ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS area_tematica_normalizada text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS area_tematica_label text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS area_tematica_confidence text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS area_tematica_secondary jsonb DEFAULT '[]'::jsonb;

ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS qualidade_flags jsonb DEFAULT '[]'::jsonb;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS backend_enrichment jsonb DEFAULT '{}'::jsonb;

COMMENT ON COLUMN public.edital.area_tematica_label IS
  'Rótulo humano de área temática (Backend 6). Frontend deve preferir este campo a fallback genérico.';

COMMENT ON COLUMN public.edital.backend_enrichment IS
  'Pacote completo de enriquecimento (versão, reasons, campos auxiliares) gerado por CORE/opportunity_enricher.';

COMMENT ON COLUMN public.edital.fundo_origem IS
  'Fundo/programa de origem do recurso (ex.: FNDCT). Distinto de fonte_normalizada (agência operadora, ex.: FINEP).';
*/

-- Backend 9 — ruído, validade, quality (dry-run antes de backfill):
/*
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS noise_score numeric NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS is_noise boolean NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS noise_type text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS is_actionable_opportunity boolean NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS actionability_score numeric NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS validade_status text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS validade_data date NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS validade_confidence text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS validade_source text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS quality_score integer NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS quality_level text NULL;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS quality_flags jsonb DEFAULT '[]'::jsonb;
ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS review_reasons jsonb DEFAULT '[]'::jsonb;

COMMENT ON COLUMN public.edital.validade_status IS
  'aberto|vencendo_7|vencendo_30|encerrado|sem_prazo|nao_aplicavel|prazo_invalido|desconhecido (Backend 9)';
COMMENT ON COLUMN public.edital.is_actionable_opportunity IS
  'True se o registro é oportunidade principal acionável (não resultado/retificação/notícia).';
*/

-- Backend 8: revisar dry-run FINEP/FNDCT antes de backfill:
--   python scripts/dry_run_finep_fndct_normalization.py --from-db

-- Backfill sugerido (job Python, não SQL em massa cego):
--   python scripts/dry_run_backend_backfill_payload.py --from-db
--   revisar outputs/backend_backfill_payload_dry_run/risky_updates_review.json
--   aplicar UPDATE controlado por lote após aprovação
