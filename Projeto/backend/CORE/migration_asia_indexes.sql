-- ============================================================
-- MIGRATION: indices e view para a expansao Asia (Japao + China)
--
-- Esta migration e IDEMPOTENTE e NAO destrutiva. Pode rodar varias vezes.
--
-- O loader atual (CORE/loader.py) salva campos de `extras` na tabela
-- auxiliar `edital_extra_campo (id_edital, chave, valor)`. Para acelerar
-- queries por:
--   - regiao = 'asia'
--   - pais   = 'japao' | 'china'
--   - setor_estrategico
--   - idioma_original
--   - tipo_oportunidade
--   - nivel_sensibilidade
--
-- adicionamos indices parciais em `edital_extra_campo` e criamos uma view
-- helper `vw_edital_asia` que pivota essas chaves para queries mais simples.
--
-- Tambem (opcional) adicionamos uma coluna `extras_jsonb` em `edital` para
-- quem quiser persistir o dicionario inteiro de uma vez no futuro, com
-- indice GIN ja criado.
-- ============================================================

-- 1. Indices em edital_extra_campo
-- ----------------------------------------------------------------
-- Os indices abaixo sao parciais (so para chaves que nos interessam),
-- entao nao incham o banco mesmo com milhares de outras chaves.

create index if not exists idx_extra_regiao
    on public.edital_extra_campo (valor)
    where chave = 'regiao';

create index if not exists idx_extra_pais
    on public.edital_extra_campo (valor)
    where chave = 'pais';

create index if not exists idx_extra_setor_estrategico
    on public.edital_extra_campo (valor)
    where chave = 'setor_estrategico';

create index if not exists idx_extra_idioma_original
    on public.edital_extra_campo (valor)
    where chave = 'idioma_original';

create index if not exists idx_extra_tipo_oportunidade
    on public.edital_extra_campo (valor)
    where chave = 'tipo_oportunidade';

create index if not exists idx_extra_nivel_sensibilidade
    on public.edital_extra_campo (valor)
    where chave = 'nivel_sensibilidade';

create index if not exists idx_extra_orgao_responsavel
    on public.edital_extra_campo (valor)
    where chave = 'orgao_responsavel';

-- Indice composto chave+valor para busca exata e ordenacao por id_edital.
create index if not exists idx_extra_chave_valor
    on public.edital_extra_campo (chave, valor, id_edital);


-- 2. View consolidada vw_edital_asia
-- ----------------------------------------------------------------
-- Pivota as chaves de extras relevantes em colunas, restrita a registros
-- onde regiao='asia'. Inclui o link e a fonte para join rapido.

create or replace view public.vw_edital_asia as
with extras_pivot as (
    select
        e.id_edital,
        e.titulo,
        e.link,
        e.fonte_recurso,
        e.data_publicacao,
        e.prazo_envio,
        e.situacao,
        max(case when ec.chave = 'regiao' then ec.valor end)              as regiao,
        max(case when ec.chave = 'pais' then ec.valor end)                as pais,
        max(case when ec.chave = 'idioma_original' then ec.valor end)     as idioma_original,
        max(case when ec.chave = 'titulo_original' then ec.valor end)     as titulo_original,
        max(case when ec.chave = 'descricao_original' then ec.valor end)  as descricao_original,
        max(case when ec.chave = 'titulo_traduzido' then ec.valor end)    as titulo_traduzido,
        max(case when ec.chave = 'descricao_traduzida' then ec.valor end) as descricao_traduzida,
        max(case when ec.chave = 'setor_estrategico' then ec.valor end)   as setor_estrategico,
        max(case when ec.chave = 'tipo_oportunidade' then ec.valor end)   as tipo_oportunidade,
        max(case when ec.chave = 'orgao_responsavel' then ec.valor end)   as orgao_responsavel,
        max(case when ec.chave = 'instituicao' then ec.valor end)         as instituicao,
        max(case when ec.chave = 'orgao_contratante' then ec.valor end)   as orgao_contratante,
        max(case when ec.chave = 'nivel_sensibilidade' then ec.valor end) as nivel_sensibilidade,
        max(case when ec.chave = 'origem' then ec.valor end)              as origem,
        max(case when ec.chave = 'subtema' then ec.valor end)             as subtema,
        max(case when ec.chave = 'palavras_chave_detectadas' then ec.valor end) as palavras_chave_detectadas,
        max(case when ec.chave = 'necessita_traducao' then ec.valor end)  as necessita_traducao
    from public.edital e
    left join public.edital_extra_campo ec on ec.id_edital = e.id_edital
    group by e.id_edital
)
select * from extras_pivot
where regiao = 'asia';


-- 3. (Opcional) coluna jsonb na tabela edital + indice GIN
-- ----------------------------------------------------------------
-- Util quando quiser passar a salvar o dicionario inteiro num so campo.
-- Nada e obrigatorio; o loader atual continua funcionando sem mexer aqui.

do $$
begin
    if not exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'edital'
          and column_name = 'extras_jsonb'
    ) then
        alter table public.edital add column extras_jsonb jsonb default '{}'::jsonb;
    end if;
end $$;

create index if not exists idx_edital_extras_jsonb_gin
    on public.edital using gin (extras_jsonb);

create index if not exists idx_edital_extras_regiao_btree
    on public.edital ((extras_jsonb->>'regiao'));

create index if not exists idx_edital_extras_pais_btree
    on public.edital ((extras_jsonb->>'pais'));

create index if not exists idx_edital_extras_setor_btree
    on public.edital ((extras_jsonb->>'setor_estrategico'));


-- 4. Comentarios (documentacao no proprio banco)
-- ----------------------------------------------------------------
comment on view public.vw_edital_asia is
    'View consolidada: editais asiaticos (regiao=asia) com chaves de extras pivotadas. Origem: edital_extra_campo.';

comment on column public.edital.extras_jsonb is
    'Coluna jsonb opcional para persistir o dicionario completo de extras. Use junto com idx_edital_extras_jsonb_gin para queries rapidas.';
