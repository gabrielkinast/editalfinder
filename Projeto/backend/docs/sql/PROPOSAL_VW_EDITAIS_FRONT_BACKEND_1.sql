-- =============================================================================
-- PROPOSTA Backend 1 — campos prontos na view vw_editais_front
-- NÃO APLICAR automaticamente. Revisar após auditoria e migration de colunas.
--
-- Pré-requisito sugerido (exemplo, não executar aqui):
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_status text;
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS prazo_confidence text;
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS escopo_geografico text;
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS modalidade_normalizada text;
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS modalidade_label text;
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS fonte_normalizada text;
--   ALTER TABLE public.edital ADD COLUMN IF NOT EXISTS tipo_registro text;
--   ... preenchidos por job ETL usando CORE/deadline_normalizer + opportunity_classifier
-- =============================================================================

-- Versão documental: expõe colunas legadas + novas (quando existirem na tabela).
-- Enquanto colunas novas não existem, usar apenas extras JSON gerado pelo job:

/*
create or replace view public.vw_editais_front as
select
  e.id_edital,
  e.titulo,
  e.descricao,
  e.fonte_recurso,
  coalesce(e.fonte_normalizada, e.fonte_recurso) as fonte_normalizada,
  e.fonte_recurso as fonte,
  e.link,
  e.pdf_url,
  e.prazo_envio,
  e.prazo_envio as fim_inscricao,
  e.prazo_envio as prazo,                    -- compat legado front
  e.data_publicacao,
  e.tipo_oportunidade,
  e.tipo_recurso,
  e.modalidade_normalizada,
  e.modalidade_label,
  e.escopo_geografico,
  e.pais as pais_origem,
  e.tipo_registro,
  e.prazo_status,
  e.prazo_confidence,
  (e.prazo_status in ('vencendo_7','vencendo_30','prazo_confortavel')) as is_aberto,
  (e.prazo_status = 'vencendo_7') as is_vencendo_7,
  (e.prazo_status in ('vencendo_7','vencendo_30')) as is_vencendo_30,
  e.natureza_recurso,
  e.reembolsavel,
  e.linha_credito,
  e.modalidade_financiamento,
  e.valor_minimo,
  e.valor_maximo,
  e.area,
  e.area_cientifica,
  e.area_tecnologica,
  e.setor_estrategico,
  e.validacao_status,
  e.qualidade_dado,
  e.classificacao_confianca,
  e.ativo,
  e.situacao,
  e.extras,
  e.extras->'curadoria_front' as curadoria_front,
  e.extras->'qualidade_flags' as qualidade_flags,
  e.criado_em,
  e.atualizado_em
from public.edital e
where e.ativo is distinct from false;
  -- filtros de visibilidade: manter política em docs/EDITAIS_VISIBILITY_AND_NOISE_POLICY.md
  -- e SQL em docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql
*/

-- Fase intermediária (somente extras, sem ALTER TABLE):
-- Job Python grava em extras.backend_1:
--   { prazo_data, prazo_status, prazo_confidence, modalidade_normalizada, escopo_geografico, ... }
-- View pode expor:
--   (e.extras->'backend_1'->>'prazo_status') as prazo_status
-- até colunas dedicadas existirem.

comment on view public.vw_editais_front is
  'Proposta Backend 1: ver PROPOSAL_VW_EDITAIS_FRONT_BACKEND_1.sql — não aplicada.';
