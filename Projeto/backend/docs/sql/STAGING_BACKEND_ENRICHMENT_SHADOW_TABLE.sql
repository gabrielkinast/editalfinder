-- =============================================================================
-- STAGING Backend 7 — tabela sombra de enriquecimento
-- NÃO APLICAR em produção. Usar apenas em ambiente staging para validação.
--
-- A tabela sombra NÃO substitui public.edital.
-- Serve para comparar payload enriquecido antes de migration/backfill real.
-- =============================================================================

-- Pré-requisito: public.edital com coluna id_edital (PK).

CREATE TABLE IF NOT EXISTS public.editais_backend_enrichment_shadow (
  id_edital bigint PRIMARY KEY REFERENCES public.edital(id_edital) ON DELETE CASCADE,

  prazo_data date NULL,
  prazo_raw text NULL,
  prazo_status text NULL,
  prazo_confidence text NULL,
  prazo_source_field text NULL,

  tipo_registro text NULL,
  kind_confidence text NULL,

  modalidade_normalizada text NULL,
  modalidade_label text NULL,
  modalidade_confidence text NULL,

  escopo_geografico text NULL,
  escopo_confidence text NULL,

  fonte_normalizada text NULL,
  pais_origem text NULL,
  source_scope text NULL,

  area_tematica_normalizada text NULL,
  area_tematica_label text NULL,
  area_tematica_confidence text NULL,
  area_tematica_secondary jsonb NOT NULL DEFAULT '[]'::jsonb,

  qualidade_flags jsonb NOT NULL DEFAULT '[]'::jsonb,
  backend_enrichment jsonb NOT NULL DEFAULT '{}'::jsonb,
  enrichment_version text NULL,

  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_shadow_enrichment_version
  ON public.editais_backend_enrichment_shadow (enrichment_version);

CREATE INDEX IF NOT EXISTS idx_shadow_prazo_status
  ON public.editais_backend_enrichment_shadow (prazo_status);

CREATE INDEX IF NOT EXISTS idx_shadow_tipo_registro
  ON public.editais_backend_enrichment_shadow (tipo_registro);

CREATE INDEX IF NOT EXISTS idx_shadow_area_tematica
  ON public.editais_backend_enrichment_shadow (area_tematica_normalizada);

COMMENT ON TABLE public.editais_backend_enrichment_shadow IS
  'Staging Backend 7: enriquecimento derivado de CORE/opportunity_enricher para validação antes de backfill em public.edital.';

-- Trigger opcional para updated_at
CREATE OR REPLACE FUNCTION public.touch_shadow_enrichment_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_shadow_enrichment_updated_at ON public.editais_backend_enrichment_shadow;
CREATE TRIGGER trg_shadow_enrichment_updated_at
  BEFORE UPDATE ON public.editais_backend_enrichment_shadow
  FOR EACH ROW
  EXECUTE FUNCTION public.touch_shadow_enrichment_updated_at();

-- Popular via script (não SQL em massa):
--   python scripts/generate_backend_enrichment_shadow_payload.py --from-db --limit 5000
--   EDITALFINDER_ALLOW_SHADOW_WRITE=true python scripts/generate_backend_enrichment_shadow_payload.py --from-db --write-shadow
