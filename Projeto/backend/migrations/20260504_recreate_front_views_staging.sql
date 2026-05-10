-- ============================================================
-- AVISO — STAGING / DESENVOLVIMENTO
--
-- Este script:
--   - Recria apenas VIEWS (DROP VIEW IF EXISTS + CREATE VIEW).
--   - Não altera dados nas tabelas base (sem DELETE, TRUNCATE, UPDATE em massa).
--   - Não remove tabelas nem colunas de tabelas.
--
-- Risco: clientes ou frontend antigos que dependiam de colunas removidas ou
-- renomeadas na view podem deixar de funcionar até serem atualizados.
--
-- Pré-requisito: aplicar antes
--   migrations/20260504_add_missing_columns_for_consolidated_schema.sql
-- para garantir que as colunas referenciadas existem em public.edital,
-- public.noticia e public.pesquisa.
--
-- Ordem de aplicação sugerida:
--   1) migration aditiva (colunas + índices)
--   2) este ficheiro (views)
--
-- Em produção, mudanças em views costumam exigir coordenação com deploy do
-- frontend e janela de manutenção; em staging/dev esta abordagem é aceitável.
-- ============================================================

begin;

-- Dependência: vw_editais_admin faz SELECT * a partir de vw_editais_front.
drop view if exists public.vw_editais_admin;
drop view if exists public.vw_editais_front;

-- Compatibilidade legada (espelha docs/sql/schema_consolidado_editalfinder.sql):
--   fonte_recurso / prazo_envio = canónicos; fonte / fim_inscricao = aliases.
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

-- Notícias / pesquisas: recriar com colunas alinhadas ao schema após migration aditiva.
drop view if exists public.vw_noticias_front;
drop view if exists public.vw_pesquisas_front;

create view public.vw_noticias_front as
select
  n.id_noticia,
  n.titulo,
  n.resumo,
  n.conteudo,
  n.link,
  n.fonte_recurso,
  coalesce(n.fonte_recurso, n.fonte) as fonte,
  n.data_publicacao,
  n.prazo_envio,
  n.prazo_envio as fim_inscricao,
  n.pais,
  n.regiao,
  n.orgao,
  n.origem_portal,
  n.tipo_conteudo,
  n.content_type,
  n.idioma,
  n.idioma_original,
  n.autor,
  n.setor_estrategico,
  n.area_cientifica,
  n.area_tecnologica,
  n.perfil_ideal,
  n.publico_alvo,
  n.tags,
  n.url_documento,
  n.imagem_url,
  n.codigo_oportunidade,
  n.numero_chamada,
  n.qualidade_dado,
  n.validacao_status,
  n.ativo,
  n.extras,
  n.hash_deduplicacao,
  n.ultima_coleta,
  n.criado_em,
  n.atualizado_em
from public.noticia n;

create view public.vw_pesquisas_front as
select
  p.id_pesquisa,
  p.titulo,
  p.resumo,
  p.descricao,
  p.link,
  p.fonte_recurso,
  coalesce(p.fonte_recurso, p.fonte) as fonte,
  p.data_publicacao,
  p.prazo_envio,
  p.prazo_envio as fim_inscricao,
  p.pais,
  p.regiao,
  p.orgao,
  p.origem_portal,
  p.tipo_oportunidade,
  p.tipo_recurso,
  p.tipo_pesquisa,
  p.idioma,
  p.idioma_original,
  p.setor_estrategico,
  p.area_cientifica,
  p.area_tecnologica,
  p.perfil_ideal,
  p.publico_alvo,
  p.tags,
  p.url_documento,
  p.pdf_url,
  p.codigo_oportunidade,
  p.numero_chamada,
  p.qualidade_dado,
  p.validacao_status,
  p.ativo,
  p.content_type,
  p.extras,
  p.hash_deduplicacao,
  p.ultima_coleta,
  p.criado_em,
  p.atualizado_em
from public.pesquisa p;

commit;
