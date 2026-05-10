-- ============================================================
-- STAGING / DEV — recriar views de editais com campos de crédito
--
-- Pré-requisito:
--   migrations/20260505_add_missing_edital_columns_from_loader_payload.sql
--
-- Apenas DROP/CREATE VIEW em public; não altera dados em tabelas base.
-- ============================================================

begin;

drop view if exists public.vw_editais_admin;
drop view if exists public.vw_editais_front;

create view public.vw_editais_front as
select
  e.id_edital as id,
  e.titulo,
  e.descricao,
  e.fonte_recurso,
  e.fonte_recurso as fonte,
  e.link,
  e.pdf_url,
  e.prazo_envio,
  e.prazo_envio as fim_inscricao,
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
  e.publico_alvo_arr as publico_alvo,
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
from public.edital e;

create view public.vw_editais_admin as
select * from public.vw_editais_front;

commit;
