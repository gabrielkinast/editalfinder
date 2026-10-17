-- EditalFinder V2 — candidate initial schema.
-- This migration is intentionally seed-free and must be reviewed before execution.

begin;

create table public.fonte (
    id uuid primary key default gen_random_uuid(),
    codigo text not null,
    nome text not null,
    url_base text,
    status_integracao text not null,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint fonte_codigo_unique unique (codigo),
    constraint fonte_codigo_formato_check check (codigo ~ '^[a-z0-9]+(?:_[a-z0-9]+)*$'),
    constraint fonte_nome_nao_vazio_check check (btrim(nome) <> ''),
    constraint fonte_url_base_check check (url_base is null or url_base ~* '^https?://'),
    constraint fonte_status_integracao_check check (
        status_integracao in (
            'mvp_habilitada', 'piloto', 'futura', 'arquivada',
            'bloqueada', 'removida_v2'
        )
    )
);

create table public.organizacao (
    id uuid primary key default gen_random_uuid(),
    codigo text,
    nome_canonico text not null,
    pais_codigo text,
    site_oficial text,
    ativo_administrativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint organizacao_codigo_unique unique (codigo),
    constraint organizacao_codigo_formato_check check (
        codigo is null or codigo ~ '^[a-z0-9]+(?:_[a-z0-9]+)*$'
    ),
    constraint organizacao_nome_nao_vazio_check check (btrim(nome_canonico) <> ''),
    constraint organizacao_pais_codigo_check check (
        pais_codigo is null or pais_codigo ~ '^[A-Z]{2}$'
    ),
    constraint organizacao_site_oficial_check check (
        site_oficial is null or site_oficial ~* '^https?://'
    )
);

create table public.tipo_oportunidade (
    id uuid primary key default gen_random_uuid(),
    codigo text not null,
    nome text not null,
    descricao text,
    ativo boolean not null default true,
    ordem_exibicao integer,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint tipo_oportunidade_codigo_unique unique (codigo),
    constraint tipo_oportunidade_codigo_formato_check check (
        codigo ~ '^[a-z0-9]+(?:_[a-z0-9]+)*$'
    ),
    constraint tipo_oportunidade_nome_nao_vazio_check check (btrim(nome) <> ''),
    constraint tipo_oportunidade_ordem_check check (
        ordem_exibicao is null or ordem_exibicao >= 0
    )
);

create table public.tipo_recurso (
    id uuid primary key default gen_random_uuid(),
    codigo text not null,
    nome text not null,
    descricao text,
    ativo boolean not null default true,
    ordem_exibicao integer,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint tipo_recurso_codigo_unique unique (codigo),
    constraint tipo_recurso_codigo_formato_check check (
        codigo ~ '^[a-z0-9]+(?:_[a-z0-9]+)*$'
    ),
    constraint tipo_recurso_nome_nao_vazio_check check (btrim(nome) <> ''),
    constraint tipo_recurso_ordem_check check (
        ordem_exibicao is null or ordem_exibicao >= 0
    )
);

create table public.area (
    id uuid primary key default gen_random_uuid(),
    codigo text not null,
    nome text not null,
    descricao text,
    ativo boolean not null default true,
    ordem_exibicao integer,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint area_codigo_unique unique (codigo),
    constraint area_codigo_formato_check check (
        codigo ~ '^[a-z0-9]+(?:_[a-z0-9]+)*$'
    ),
    constraint area_nome_nao_vazio_check check (btrim(nome) <> ''),
    constraint area_ordem_check check (ordem_exibicao is null or ordem_exibicao >= 0)
);

create table public.execucao_coleta (
    id uuid primary key default gen_random_uuid(),
    fonte_id uuid not null,
    iniciado_em timestamptz not null default now(),
    finalizado_em timestamptz,
    status text not null default 'iniciada',
    versao_coletor text not null,
    parametros jsonb,
    metricas jsonb,
    erro_resumo text,
    criado_em timestamptz not null default now(),
    constraint execucao_coleta_fonte_fk foreign key (fonte_id)
        references public.fonte (id) on delete restrict,
    constraint execucao_coleta_status_check check (
        status in ('iniciada', 'sucesso', 'parcial', 'falha', 'cancelada')
    ),
    constraint execucao_coleta_versao_nao_vazia_check check (btrim(versao_coletor) <> ''),
    constraint execucao_coleta_parametros_objeto_check check (
        parametros is null or jsonb_typeof(parametros) = 'object'
    ),
    constraint execucao_coleta_metricas_objeto_check check (
        metricas is null or jsonb_typeof(metricas) = 'object'
    ),
    constraint execucao_coleta_periodo_check check (
        finalizado_em is null or finalizado_em >= iniciado_em
    ),
    constraint execucao_coleta_estado_temporal_check check (
        (status = 'iniciada' and finalizado_em is null)
        or (status <> 'iniciada' and finalizado_em is not null)
    )
);

create table public.item_coletado (
    id uuid primary key default gen_random_uuid(),
    execucao_coleta_id uuid not null,
    chave_origem text,
    url_coletada text,
    payload_bruto jsonb not null,
    hash_payload text not null,
    coletado_em timestamptz not null default now(),
    estado_processamento text not null default 'coletado',
    motivo_rejeicao text,
    erro_codigo text,
    erro_detalhes jsonb,
    processado_em timestamptz,
    versao_transformer text,
    constraint item_coletado_execucao_fk foreign key (execucao_coleta_id)
        references public.execucao_coleta (id) on delete restrict,
    constraint item_coletado_url_check check (
        url_coletada is null or url_coletada ~* '^https?://'
    ),
    constraint item_coletado_hash_nao_vazio_check check (btrim(hash_payload) <> ''),
    constraint item_coletado_estado_check check (
        estado_processamento in (
            'coletado', 'normalizado', 'aceito', 'rejeitado',
            'erro', 'quarentena', 'ignorado'
        )
    ),
    constraint item_coletado_rejeicao_check check (
        estado_processamento <> 'rejeitado'
        or (motivo_rejeicao is not null and btrim(motivo_rejeicao) <> '')
    ),
    constraint item_coletado_erro_check check (
        estado_processamento <> 'erro'
        or (erro_codigo is not null and btrim(erro_codigo) <> '')
    ),
    constraint item_coletado_erro_detalhes_objeto_check check (
        erro_detalhes is null or jsonb_typeof(erro_detalhes) = 'object'
    ),
    constraint item_coletado_processamento_temporal_check check (
        (estado_processamento = 'coletado' and processado_em is null)
        or (estado_processamento <> 'coletado' and processado_em is not null)
    )
);

create table public.oportunidade (
    id uuid primary key default gen_random_uuid(),
    fonte_id uuid not null,
    organizacao_responsavel_id uuid,
    organizacao_responsavel_texto text,
    tipo_oportunidade_id uuid,
    tipo_recurso_id uuid,
    titulo text not null,
    descricao text,
    url_oficial text not null,
    url_pdf text,
    programa text,
    data_publicacao date,
    data_abertura date,
    prazo_submissao date,
    motivo_sem_prazo text,
    data_resultado date,
    situacao_informada text,
    ativo_administrativo boolean not null default true,
    escopo_geografico text not null default 'nao_identificado',
    valor_minimo numeric(18,2),
    valor_maximo numeric(18,2),
    moeda text,
    confianca_classificacao numeric(5,4),
    proveniencia jsonb not null default '{"schema_version":1,"campos":{}}'::jsonb,
    hash_conteudo text,
    dados_extras jsonb not null default '{}'::jsonb,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now(),
    constraint oportunidade_fonte_fk foreign key (fonte_id)
        references public.fonte (id) on delete restrict,
    constraint oportunidade_organizacao_fk foreign key (organizacao_responsavel_id)
        references public.organizacao (id) on delete restrict,
    constraint oportunidade_tipo_oportunidade_fk foreign key (tipo_oportunidade_id)
        references public.tipo_oportunidade (id) on delete restrict,
    constraint oportunidade_tipo_recurso_fk foreign key (tipo_recurso_id)
        references public.tipo_recurso (id) on delete restrict,
    constraint oportunidade_titulo_nao_vazio_check check (btrim(titulo) <> ''),
    constraint oportunidade_url_oficial_check check (url_oficial ~* '^https?://'),
    constraint oportunidade_url_pdf_check check (url_pdf is null or url_pdf ~* '^https?://'),
    constraint oportunidade_motivo_sem_prazo_check check (
        motivo_sem_prazo is null
        or motivo_sem_prazo in (
            'nao_informado', 'a_definir', 'fluxo_continuo', 'nao_aplicavel'
        )
    ),
    constraint oportunidade_prazo_check check (
        (prazo_submissao is not null and motivo_sem_prazo is null)
        or (prazo_submissao is null and motivo_sem_prazo is not null)
    ),
    constraint oportunidade_escopo_geografico_check check (
        escopo_geografico in ('brasil', 'internacional', 'misto', 'nao_identificado')
    ),
    constraint oportunidade_valor_minimo_check check (
        valor_minimo is null or valor_minimo >= 0
    ),
    constraint oportunidade_valor_maximo_check check (
        valor_maximo is null or valor_maximo >= 0
    ),
    constraint oportunidade_faixa_valor_check check (
        valor_minimo is null or valor_maximo is null or valor_minimo <= valor_maximo
    ),
    constraint oportunidade_moeda_check check (
        moeda is null or moeda ~ '^[A-Z]{3}$'
    ),
    constraint oportunidade_valor_moeda_check check (
        (valor_minimo is null and valor_maximo is null)
        or moeda is not null
    ),
    constraint oportunidade_confianca_check check (
        confianca_classificacao is null
        or confianca_classificacao between 0 and 1
    ),
    constraint oportunidade_proveniencia_check check (
        jsonb_typeof(proveniencia) = 'object'
        and proveniencia ->> 'schema_version' = '1'
        and jsonb_typeof(proveniencia -> 'campos') = 'object'
    ),
    constraint oportunidade_dados_extras_check check (
        jsonb_typeof(dados_extras) = 'object'
    )
);

create table public.oportunidade_identificador (
    tipo_identificador text not null,
    namespace text not null,
    fonte_id uuid not null,
    valor_normalizado text not null,
    oportunidade_id uuid not null,
    valor_original text,
    criado_em timestamptz not null default now(),
    constraint oportunidade_identificador_pk primary key (
        tipo_identificador, namespace, fonte_id, valor_normalizado
    ),
    constraint oportunidade_identificador_fonte_fk foreign key (fonte_id)
        references public.fonte (id) on delete restrict,
    constraint oportunidade_identificador_oportunidade_fk foreign key (oportunidade_id)
        references public.oportunidade (id) on delete cascade,
    constraint oportunidade_identificador_tipo_check check (
        tipo_identificador in (
            'url_canonica', 'identificador_oficial', 'identificador_fonte'
        )
    ),
    constraint oportunidade_identificador_namespace_check check (btrim(namespace) <> ''),
    constraint oportunidade_identificador_valor_check check (btrim(valor_normalizado) <> '')
);

create table public.oportunidade_localizacao (
    id uuid primary key default gen_random_uuid(),
    oportunidade_id uuid not null,
    papel_localizacao text not null,
    pais_codigo text,
    regiao_brasil text,
    estado_codigo text,
    municipio text,
    origem_inferencia text,
    confianca numeric(5,4),
    criado_em timestamptz not null default now(),
    constraint oportunidade_localizacao_oportunidade_fk foreign key (oportunidade_id)
        references public.oportunidade (id) on delete cascade,
    constraint oportunidade_localizacao_papel_check check (
        papel_localizacao in (
            'elegibilidade', 'execucao', 'beneficiarios', 'origem',
            'organizacao_responsavel', 'nao_especificado'
        )
    ),
    constraint oportunidade_localizacao_pais_check check (
        pais_codigo is null or pais_codigo ~ '^[A-Z]{2}$'
    ),
    constraint oportunidade_localizacao_regiao_check check (
        regiao_brasil is null
        or regiao_brasil in ('norte', 'nordeste', 'centro_oeste', 'sudeste', 'sul')
    ),
    constraint oportunidade_localizacao_estado_check check (
        estado_codigo is null
        or estado_codigo in (
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        )
    ),
    constraint oportunidade_localizacao_geografia_brasil_check check (
        (regiao_brasil is null and estado_codigo is null)
        or pais_codigo = 'BR'
    ),
    constraint oportunidade_localizacao_uf_regiao_check check (
        estado_codigo is null
        or regiao_brasil is null
        or (regiao_brasil = 'norte' and estado_codigo in ('AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'))
        or (regiao_brasil = 'nordeste' and estado_codigo in ('AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'))
        or (regiao_brasil = 'centro_oeste' and estado_codigo in ('DF', 'GO', 'MT', 'MS'))
        or (regiao_brasil = 'sudeste' and estado_codigo in ('ES', 'MG', 'RJ', 'SP'))
        or (regiao_brasil = 'sul' and estado_codigo in ('PR', 'RS', 'SC'))
    ),
    constraint oportunidade_localizacao_municipio_check check (
        municipio is null or btrim(municipio) <> ''
    ),
    constraint oportunidade_localizacao_confianca_check check (
        confianca is null or confianca between 0 and 1
    ),
    constraint oportunidade_localizacao_inferencia_check check (
        origem_inferencia is null or confianca is not null
    )
);

create table public.item_oportunidade (
    item_coletado_id uuid not null,
    oportunidade_id uuid not null,
    papel text not null,
    confianca numeric(5,4) not null,
    criado_em timestamptz not null default now(),
    constraint item_oportunidade_pk primary key (item_coletado_id, oportunidade_id),
    constraint item_oportunidade_item_fk foreign key (item_coletado_id)
        references public.item_coletado (id) on delete cascade,
    constraint item_oportunidade_oportunidade_fk foreign key (oportunidade_id)
        references public.oportunidade (id) on delete cascade,
    constraint item_oportunidade_papel_check check (
        papel in ('origem', 'evidencia', 'atualizacao', 'agregador')
    ),
    constraint item_oportunidade_confianca_check check (confianca between 0 and 1)
);

create table public.oportunidade_area (
    oportunidade_id uuid not null,
    area_id uuid not null,
    principal boolean not null default false,
    origem_classificacao text,
    confianca numeric(5,4),
    criado_em timestamptz not null default now(),
    constraint oportunidade_area_pk primary key (oportunidade_id, area_id),
    constraint oportunidade_area_oportunidade_fk foreign key (oportunidade_id)
        references public.oportunidade (id) on delete cascade,
    constraint oportunidade_area_area_fk foreign key (area_id)
        references public.area (id) on delete restrict,
    constraint oportunidade_area_confianca_check check (
        confianca is null or confianca between 0 and 1
    )
);

create index fonte_status_integracao_idx
    on public.fonte (status_integracao);

create index tipo_oportunidade_catalogo_idx
    on public.tipo_oportunidade (ativo, ordem_exibicao);

create index tipo_recurso_catalogo_idx
    on public.tipo_recurso (ativo, ordem_exibicao);

create index area_catalogo_idx
    on public.area (ativo, ordem_exibicao);

create index execucao_coleta_fonte_inicio_idx
    on public.execucao_coleta (fonte_id, iniciado_em desc);

create index execucao_coleta_status_idx
    on public.execucao_coleta (status);

create index execucao_coleta_inicio_idx
    on public.execucao_coleta (iniciado_em);

create unique index item_coletado_execucao_chave_origem_uidx
    on public.item_coletado (execucao_coleta_id, chave_origem)
    where chave_origem is not null;

create index item_coletado_hash_payload_idx
    on public.item_coletado (hash_payload);

create index item_coletado_estado_coletado_idx
    on public.item_coletado (estado_processamento, coletado_em);

create index item_coletado_processado_em_idx
    on public.item_coletado (processado_em)
    where processado_em is not null;

create index oportunidade_fonte_idx
    on public.oportunidade (fonte_id);

create index oportunidade_organizacao_idx
    on public.oportunidade (organizacao_responsavel_id);

create index oportunidade_tipo_oportunidade_idx
    on public.oportunidade (tipo_oportunidade_id);

create index oportunidade_tipo_recurso_idx
    on public.oportunidade (tipo_recurso_id);

create index oportunidade_ativo_prazo_idx
    on public.oportunidade (ativo_administrativo, prazo_submissao);

create index oportunidade_escopo_idx
    on public.oportunidade (escopo_geografico);

create index oportunidade_atualizado_em_idx
    on public.oportunidade (atualizado_em);

create index oportunidade_hash_conteudo_idx
    on public.oportunidade (hash_conteudo)
    where hash_conteudo is not null;

create index oportunidade_identificador_oportunidade_idx
    on public.oportunidade_identificador (oportunidade_id);

create index oportunidade_identificador_fonte_tipo_idx
    on public.oportunidade_identificador (fonte_id, tipo_identificador);

create index oportunidade_localizacao_oportunidade_idx
    on public.oportunidade_localizacao (oportunidade_id);

create index oportunidade_localizacao_pais_estado_idx
    on public.oportunidade_localizacao (pais_codigo, estado_codigo);

create index oportunidade_localizacao_regiao_idx
    on public.oportunidade_localizacao (regiao_brasil);

create index oportunidade_localizacao_papel_pais_idx
    on public.oportunidade_localizacao (papel_localizacao, pais_codigo);

create index item_oportunidade_oportunidade_item_idx
    on public.item_oportunidade (oportunidade_id, item_coletado_id);

create index oportunidade_area_area_idx
    on public.oportunidade_area (area_id);

create unique index oportunidade_area_principal_uidx
    on public.oportunidade_area (oportunidade_id)
    where principal;

create function public.set_atualizado_em()
returns trigger
language plpgsql
set search_path = pg_catalog, public
as $$
begin
    new.atualizado_em = now();
    return new;
end;
$$;

revoke all on function public.set_atualizado_em() from public;
revoke all on function public.set_atualizado_em()
    from anon, authenticated;

create trigger fonte_set_atualizado_em
before update on public.fonte
for each row execute function public.set_atualizado_em();

create trigger organizacao_set_atualizado_em
before update on public.organizacao
for each row execute function public.set_atualizado_em();

create trigger tipo_oportunidade_set_atualizado_em
before update on public.tipo_oportunidade
for each row execute function public.set_atualizado_em();

create trigger tipo_recurso_set_atualizado_em
before update on public.tipo_recurso
for each row execute function public.set_atualizado_em();

create trigger area_set_atualizado_em
before update on public.area
for each row execute function public.set_atualizado_em();

create trigger oportunidade_set_atualizado_em
before update on public.oportunidade
for each row execute function public.set_atualizado_em();

alter table public.fonte enable row level security;
alter table public.organizacao enable row level security;
alter table public.tipo_oportunidade enable row level security;
alter table public.tipo_recurso enable row level security;
alter table public.area enable row level security;
alter table public.execucao_coleta enable row level security;
alter table public.item_coletado enable row level security;
alter table public.oportunidade enable row level security;
alter table public.oportunidade_identificador enable row level security;
alter table public.oportunidade_localizacao enable row level security;
alter table public.item_oportunidade enable row level security;
alter table public.oportunidade_area enable row level security;

create view public.vw_oportunidades_front_v2
with (security_invoker = true)
as
select
    o.id,
    o.titulo,
    o.descricao,
    o.url_oficial,
    o.url_pdf,
    o.fonte_id,
    f.codigo as fonte_codigo,
    f.nome as fonte_nome,
    o.organizacao_responsavel_id,
    org.nome_canonico as organizacao_responsavel_nome,
    o.organizacao_responsavel_texto,
    top.codigo as tipo_oportunidade_codigo,
    top.nome as tipo_oportunidade_nome,
    tr.codigo as tipo_recurso_codigo,
    tr.nome as tipo_recurso_nome,
    o.programa,
    o.data_publicacao,
    o.data_abertura,
    o.prazo_submissao,
    o.motivo_sem_prazo,
    o.data_resultado,
    o.situacao_informada,
    o.ativo_administrativo,
    case
        when not o.ativo_administrativo then 'inativa'
        when o.prazo_submissao < current_date then 'encerrada'
        when o.prazo_submissao = current_date then 'vence_hoje'
        when o.prazo_submissao > current_date then 'aberta'
        when o.prazo_submissao is null and o.motivo_sem_prazo is not null then 'sem_prazo'
        else 'nao_determinada'
    end as status_temporal,
    case
        when o.prazo_submissao is not null
            then o.prazo_submissao - current_date
        else null
    end as dias_para_prazo,
    o.escopo_geografico,
    coalesce(loc.localizacoes, '[]'::jsonb) as localizacoes,
    coalesce(ar.areas, '[]'::jsonb) as areas,
    o.valor_minimo,
    o.valor_maximo,
    o.moeda,
    o.confianca_classificacao,
    o.atualizado_em
from public.oportunidade o
join public.fonte f on f.id = o.fonte_id
left join public.organizacao org on org.id = o.organizacao_responsavel_id
left join public.tipo_oportunidade top on top.id = o.tipo_oportunidade_id
left join public.tipo_recurso tr on tr.id = o.tipo_recurso_id
left join lateral (
    select jsonb_agg(
        jsonb_build_object(
            'papel_localizacao', ol.papel_localizacao,
            'pais_codigo', ol.pais_codigo,
            'regiao_brasil', ol.regiao_brasil,
            'estado_codigo', ol.estado_codigo,
            'municipio', ol.municipio,
            'confianca', ol.confianca
        )
        order by
            ol.papel_localizacao,
            ol.pais_codigo nulls last,
            ol.estado_codigo nulls last,
            ol.municipio nulls last,
            ol.id
    ) as localizacoes
    from public.oportunidade_localizacao ol
    where ol.oportunidade_id = o.id
) loc on true
left join lateral (
    select jsonb_agg(
        jsonb_build_object(
            'codigo', a.codigo,
            'nome', a.nome,
            'principal', oa.principal,
            'confianca', oa.confianca
        )
        order by oa.principal desc, a.ordem_exibicao nulls last, a.codigo
    ) as areas
    from public.oportunidade_area oa
    join public.area a on a.id = oa.area_id
    where oa.oportunidade_id = o.id
) ar on true;

revoke all on table public.fonte from anon, authenticated;
revoke all on table public.organizacao from anon, authenticated;
revoke all on table public.tipo_oportunidade from anon, authenticated;
revoke all on table public.tipo_recurso from anon, authenticated;
revoke all on table public.area from anon, authenticated;
revoke all on table public.execucao_coleta from anon, authenticated;
revoke all on table public.item_coletado from anon, authenticated;
revoke all on table public.oportunidade from anon, authenticated;
revoke all on table public.oportunidade_identificador from anon, authenticated;
revoke all on table public.oportunidade_localizacao from anon, authenticated;
revoke all on table public.item_oportunidade from anon, authenticated;
revoke all on table public.oportunidade_area from anon, authenticated;
revoke all on table public.vw_oportunidades_front_v2 from anon, authenticated;

comment on table public.fonte is
    'Fonte de coleta do pipeline V2; não representa automaticamente a organização responsável.';
comment on column public.fonte.status_integracao is
    'Estado operacional controlado da integração no portfólio V2.';
comment on table public.item_coletado is
    'Fronteira auditável que preserva o payload bruto coletado antes da canonicalização.';
comment on column public.item_coletado.payload_bruto is
    'Payload bruto JSONB sanitizado; não deve conter credenciais ou dados pessoais desnecessários.';
comment on column public.item_coletado.estado_processamento is
    'Estado controlado do processamento do item pelo pipeline V2.';
comment on table public.item_oportunidade is
    'Relação N:N auditável entre itens coletados e oportunidades canônicas.';
comment on column public.item_oportunidade.confianca is
    'Confiança numérica da associação, na escala inclusiva de 0 a 1.';
comment on table public.oportunidade is
    'Registro canônico de uma oportunidade no EditalFinder V2.';
comment on column public.oportunidade.organizacao_responsavel_id is
    'FK nullable preenchida somente por associação determinística; nunca possui organização default.';
comment on column public.oportunidade.organizacao_responsavel_texto is
    'Texto original da organização responsável, preservado independentemente da FK canônica.';
comment on column public.oportunidade.url_oficial is
    'URL oficial obrigatória; não é UNIQUE diretamente. Identidade fica em oportunidade_identificador.';
comment on column public.oportunidade.prazo_submissao is
    'Data civil do último dia de submissão; não é timestamp operacional.';
comment on column public.oportunidade.situacao_informada is
    'Situação declarada pela fonte, distinta do status temporal derivado na view.';
comment on column public.oportunidade.ativo_administrativo is
    'Controle editorial persistido; não muda automaticamente com o vencimento do prazo.';
comment on column public.oportunidade.proveniencia is
    'Documento JSONB versionado com origem, método, confiança e item de evidência de campos inferidos.';
comment on table public.oportunidade_identificador is
    'Identidade determinística por tipo, namespace, fonte e valor normalizado.';
comment on table public.oportunidade_localizacao is
    'Localização 1:N cujo papel semântico é distinto do escopo geográfico da oportunidade.';
comment on column public.oportunidade_localizacao.regiao_brasil is
    'Macrorregião brasileira opcional; nunca recebe rótulos de escopo como Nacional ou Internacional.';
comment on view public.vw_oportunidades_front_v2 is
    'Contrato de leitura V2, sem concessão pública nesta migration; deriva status e agrega relações independentemente.';

commit;
