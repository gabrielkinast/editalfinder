-- ============================================================
-- MIGRAÇÃO: ADICIONAR CAMPOS DE PERFIL NA TABELA ORGANIZACAO
-- ============================================================

-- 1. Adicionar coluna para armazenar os perfis de interesse da organização
do $$
begin
  if not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'organizacao' and column_name = 'perfis_interesse') then
    alter table public.organizacao add column perfis_interesse jsonb default '[]'::jsonb;
  end if;
end $$;

-- 2. Migrar os perfis hardcoded para a Organização Padrão (ID 11)
-- Isso permite que o backend leia do banco e o front-end possa editar.
update public.organizacao
set perfis_interesse = '[
  {
    "nome": "Pesquisador",
    "keywords": ["bolsa", "doutorado", "mestrado", "pesquisa científica", "produtividade", "artigo", "pós-graduação"],
    "eligibility": ["pessoa física", "pesquisador", "doutor", "mestre", "estudante"]
  },
  {
    "nome": "Consultoria em Incentivos Fiscais",
    "keywords": ["lei do bem", "lei de informática", "incentivos fiscais", "benefícios fiscais", "p&d", "dedução"],
    "eligibility": ["empresa tributada pelo lucro real", "consultoria", "empresa de tecnologia"]
  },
  {
    "nome": "Consultoria em Captação de Recursos",
    "keywords": ["fomento", "subvenção", "financiamento", "captação", "elaboração de projetos", "propostas", "edital"],
    "eligibility": ["assessoria", "consultoria", "empresa", "ict", "ong"]
  },
  {
    "nome": "Consultoria em Inovação e Estratégia",
    "keywords": ["gestão da inovação", "open innovation", "inovação aberta", "ecossistema", "transformação digital"],
    "eligibility": ["grandes empresas", "corporate venture", "consultoria estratégica"]
  }
]'::jsonb
where id_organizacao = 11;

raise notice 'Tabela organizacao atualizada com perfis de interesse.';
