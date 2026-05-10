-- =============================================================================
-- PROPOSTA — NÃO EXECUTAR EM PRODUÇÃO ATÉ MIGRATION / REVIEW DBA
-- Recovery D / secção «Fornecedores & Investimentos»
-- Filtra editais ativos cuja navegação deve ir para o front de fornecedores
-- (extras.frontend_section ou tipos de portal supplier alinhados à Recovery D).
-- =============================================================================

create or replace view public.vw_fornecedores_front as
select
  id_edital,
  titulo,
  link,
  fonte,
  fonte_recurso,
  tipo_oportunidade,
  tipo_recurso,
  validacao_status,
  qualidade_dado,
  setor_estrategico,
  perfil_ideal,
  pais,
  estado,
  prazo_envio,
  ativo,
  extras
from public.edital
where ativo = true
  and (
    coalesce(extras->>'frontend_section', '') = 'fornecedores'
    or coalesce(extras->>'mostrar_em_fornecedores', 'false') = 'true'
    or tipo_oportunidade in (
      'oportunidade_fornecedor',
      'supplier_registration',
      'supplier_portal',
      'procurement_portal',
      'programa_agregado',
      'documentacao_fornecedor',
      'recurso_fornecedor'
    )
  );

-- Notas:
-- 1) extras->>'mostrar_em_fornecedores' assume serialização JSON booleana como string 'true'/'false';
--    ajustar se a coluna extras for tipada de outra forma no vosso cluster.
-- 2) Índice GIN em extras ou expressão gerada pode ser necessário para performance.

comment on view public.vw_fornecedores_front is
  'Proposta Recovery D: vista para UI «Fornecedores» — não aplicada automaticamente.';
