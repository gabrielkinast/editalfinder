-- ============================================================
-- EditalFinder — 2026-05-05
-- Migration ADITIVA: alinhar public.edital ao payload real do loader
-- (map_to_db_schema + extras_to_filter_columns / _merge_db_row).
--
-- Segurança:
--   - Apenas ALTER TABLE ... ADD COLUMN IF NOT EXISTS
--   - CREATE INDEX IF NOT EXISTS
--   - Sem DROP TABLE/COLUMN, DELETE, TRUNCATE, recriação de tabela
--
-- Ordem sugerida no staging:
--   1) Este ficheiro
--   2) NOTIFY pgrst (incluído no fim)
--   3) migrations/20260505_recreate_edital_views_credito_staging.sql (opcional)
--   4) docs/sql/check_edital_payload_columns.sql
-- ============================================================

begin;

-- ---------------------------------------------------------------------------
-- Legado / núcleo (garantir presença em bases antigas)
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists titulo text;
alter table public.edital add column if not exists descricao text;
alter table public.edital add column if not exists link text;
alter table public.edital add column if not exists fonte_recurso text;
alter table public.edital add column if not exists data_publicacao date;
alter table public.edital add column if not exists prazo_envio date;
alter table public.edital add column if not exists situacao text;
alter table public.edital add column if not exists valor_maximo numeric;
alter table public.edital add column if not exists valor_minimo numeric;
alter table public.edital add column if not exists contrapartida text;
alter table public.edital add column if not exists elegibilidade text;
alter table public.edital add column if not exists contato text;
alter table public.edital add column if not exists link_inscricao text;
alter table public.edital add column if not exists ods text;
alter table public.edital add column if not exists regiao text;
alter table public.edital add column if not exists pdf_url text;
alter table public.edital add column if not exists objetivo text;
alter table public.edital add column if not exists publico_alvo text;
alter table public.edital add column if not exists temas text;
alter table public.edital add column if not exists score numeric;
alter table public.edital add column if not exists score_detalhado jsonb;
alter table public.edital add column if not exists justificativa text;
alter table public.edital add column if not exists recomendacao text;
alter table public.edital add column if not exists compatibilidade text;
alter table public.edital add column if not exists id_organizacao bigint;

-- ---------------------------------------------------------------------------
-- Pacote estendido (classificação, localização, metadados)
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists extras jsonb not null default '{}'::jsonb;
alter table public.edital add column if not exists programa text;
alter table public.edital add column if not exists acao text;
alter table public.edital add column if not exists tipo_recurso text;
alter table public.edital add column if not exists tipo_oportunidade text;
alter table public.edital add column if not exists natureza_recurso text;
alter table public.edital add column if not exists area text[];
alter table public.edital add column if not exists publico_alvo_arr text[];
alter table public.edital add column if not exists setor_economico text[];
alter table public.edital add column if not exists area_cientifica text[];
alter table public.edital add column if not exists area_tecnologica text[];
alter table public.edital add column if not exists setor_estrategico text[];
alter table public.edital add column if not exists tags text[];
alter table public.edital add column if not exists perfil_ideal text[];
alter table public.edital add column if not exists pais text;
alter table public.edital add column if not exists estado text;
alter table public.edital add column if not exists municipio text;
alter table public.edital add column if not exists uf text;
alter table public.edital add column if not exists cidade text;
alter table public.edital add column if not exists valor_total_texto text;
alter table public.edital add column if not exists valor_total numeric;
alter table public.edital add column if not exists valor_estimado numeric;
alter table public.edital add column if not exists moeda text;
alter table public.edital add column if not exists reembolsavel boolean;
alter table public.edital add column if not exists orgao_responsavel text;
alter table public.edital add column if not exists instituicao text;
alter table public.edital add column if not exists orgao_contratante text;
alter table public.edital add column if not exists orgao text;
alter table public.edital add column if not exists unidade_responsavel text;
alter table public.edital add column if not exists numero_edital text;
alter table public.edital add column if not exists numero_chamada text;
alter table public.edital add column if not exists codigo_oportunidade text;
alter table public.edital add column if not exists edital_numero text;
alter table public.edital add column if not exists chamada text;
alter table public.edital add column if not exists subprograma text;
alter table public.edital add column if not exists numero_processo text;
alter table public.edital add column if not exists url_detalhe text;
alter table public.edital add column if not exists url_listagem text;
alter table public.edital add column if not exists origem_portal text;
alter table public.edital add column if not exists classificacao_confianca text;
alter table public.edital add column if not exists ativo boolean default true;
alter table public.edital add column if not exists hash_deduplicacao text;
alter table public.edital add column if not exists ultima_coleta timestamptz;

-- ---------------------------------------------------------------------------
-- i18n / originais
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists titulo_original text;
alter table public.edital add column if not exists descricao_original text;
alter table public.edital add column if not exists titulo_traduzido text;
alter table public.edital add column if not exists descricao_traduzida text;
alter table public.edital add column if not exists titulo_en text;
alter table public.edital add column if not exists descricao_en text;
alter table public.edital add column if not exists idioma_original text;
alter table public.edital add column if not exists traducao_automatica boolean;

-- ---------------------------------------------------------------------------
-- Crédito / financiamento
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists garantias text;
alter table public.edital add column if not exists limite_financiavel text;
alter table public.edital add column if not exists percentual_financiavel text;
alter table public.edital add column if not exists taxa_juros text;
alter table public.edital add column if not exists carencia text;
alter table public.edital add column if not exists prazo_carencia text;
alter table public.edital add column if not exists prazo_pagamento text;
alter table public.edital add column if not exists prazo_amortizacao text;
alter table public.edital add column if not exists prazo_total text;
alter table public.edital add column if not exists publico_beneficiario text;
alter table public.edital add column if not exists finalidade_financiamento text;
alter table public.edital add column if not exists linha_credito text;
alter table public.edital add column if not exists modalidade_financiamento text;

-- ---------------------------------------------------------------------------
-- Datas de ciclo
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists data_abertura date;
alter table public.edital add column if not exists data_encerramento date;
alter table public.edital add column if not exists data_resultado date;

-- ---------------------------------------------------------------------------
-- PDF / documentos espelhados
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists pdf_resumo text;
alter table public.edital add column if not exists documentos jsonb;
alter table public.edital add column if not exists anexos jsonb;

-- ---------------------------------------------------------------------------
-- Qualidade / acesso / roteamento de conteúdo
-- ---------------------------------------------------------------------------
alter table public.edital add column if not exists validacao_status text default 'incompleto';
alter table public.edital add column if not exists qualidade_dado integer;
alter table public.edital add column if not exists warnings text[];
alter table public.edital add column if not exists suspeito boolean;
alter table public.edital add column if not exists motivo_rejeicao text;
alter table public.edital add column if not exists content_type_detectado text;
alter table public.edital add column if not exists extraction_mode text;
alter table public.edital add column if not exists access_status text;
alter table public.edital add column if not exists access_reason text;

-- ---------------------------------------------------------------------------
-- Índices auxiliares (consultas por filtro comum)
-- ---------------------------------------------------------------------------
create index if not exists idx_edital_validacao_status on public.edital (validacao_status);
create index if not exists idx_edital_origem_portal on public.edital (origem_portal);
create index if not exists idx_edital_linha_credito on public.edital (linha_credito);
create index if not exists idx_edital_reembolsavel on public.edital (reembolsavel);
create index if not exists idx_edital_natureza_recurso on public.edital (natureza_recurso);
create index if not exists idx_edital_documentos_gin on public.edital using gin (documentos);
create index if not exists idx_edital_anexos_gin on public.edital using gin (anexos);
create index if not exists idx_edital_tags_gin on public.edital using gin (tags);
create index if not exists idx_edital_perfil_ideal_gin on public.edital using gin (perfil_ideal);

commit;

notify pgrst, 'reload schema';
