

CREATE TABLE public.cliente (
  id_cliente integer NOT NULL DEFAULT nextval('cliente_id_cliente_seq'::regclass),
  nome_empresa character varying,
  razao_social character varying,
  cnpj character varying,
  data_abertura date,
  natureza_juridica character varying,
  porte_empresa character varying,
  setor character varying,
  cnae_principal character varying,
  pais character varying,
  estado character varying,
  cidade character varying,
  regiao character varying,
  faturamento_anual numeric,
  numero_funcionarios integer,
  capital_social numeric,
  area_inovacao character varying,
  tem_projeto_inovacao boolean,
  descricao_projeto text,
  nivel_maturidade character varying,
  possui_certidao_negativa boolean,
  regular_fiscal boolean,
  regular_trabalhista boolean,
  interesse_temas character varying,
  interesse_valor_min numeric,
  interesse_valor_max numeric,
  disponibilidade_contrapartida boolean,
  status text,
  CONSTRAINT cliente_pkey PRIMARY KEY (id_cliente)
);
CREATE TABLE public.consultor (
  id_consultor bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  id_usuario bigint NOT NULL,
  empresa character varying NOT NULL,
  especialidade character varying NOT NULL,
  telefone bigint NOT NULL,
  status text,
  CONSTRAINT consultor_pkey PRIMARY KEY (id_consultor, id_usuario),
  CONSTRAINT consultor_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario)
);
CREATE TABLE public.documento (
  id_documento bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  id_edital bigint NOT NULL,
  nome character varying NOT NULL,
  tipo character varying NOT NULL,
  url character varying NOT NULL,
  status text,
  CONSTRAINT documento_pkey PRIMARY KEY (id_documento, id_edital),
  CONSTRAINT documento_id_edital_fkey FOREIGN KEY (id_edital) REFERENCES public.edital(id_edital)
);
CREATE TABLE public.edital (
  id_edital bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  titulo character varying,
  descricao character varying,
  objetivo character varying,
  temas character varying,
  publico_alvo character varying,
  fonte_recurso character varying,
  valor_maximo double precision,
  data_publicacao date,
  prazo_envio date,
  situacao character varying,
  pdf_url character varying,
  link character varying,
  id_organizacao bigint NOT NULL,
  id_modificacao uuid,
  status text,
  estado character varying,
  CONSTRAINT edital_pkey PRIMARY KEY (id_edital, id_organizacao),
  CONSTRAINT edital_id_organizacao_fkey FOREIGN KEY (id_organizacao) REFERENCES public.organizacao(id_organizacao)
);
CREATE TABLE public.organizacao (
  id_organizacao bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  nome character varying NOT NULL,
  tipo character varying NOT NULL,
  país character varying NOT NULL,
  estado character varying NOT NULL,
  site character varying NOT NULL,
  status text,
  CONSTRAINT organizacao_pkey PRIMARY KEY (id_organizacao)
);
CREATE TABLE public.usuario (
  id_usuario bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  nome character varying NOT NULL,
  nome_email text,
  senha character varying NOT NULL,
  tipo_usuario text NOT NULL,
  nivel_acesso integer,
  status text,
  CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario)
);