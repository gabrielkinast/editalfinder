# Schema consolidado — EditalFinder

Este diretório contém um snapshot SQL consolidado e **não destrutivo** do schema principal do backend.

Arquivo principal:

- `docs/sql/schema_consolidado_editalfinder.sql`

## Relação com as migrations (staging / dev)

- **`docs/sql/schema_consolidado_editalfinder.sql`** é a **fotografia ideal** do schema (referência para alinhar código e novos ambientes). Não substitui o histórico de migrations nem deve ser aplicado “cego” em bases já populadas sem planeamento.
- **`migrations/20260504_add_missing_columns_for_consolidated_schema.sql`** é a migration **aditiva**: apenas `ALTER TABLE … ADD COLUMN IF NOT EXISTS` e `CREATE INDEX IF NOT EXISTS` sobre tabelas já existentes. **Não contém views**, para evitar o erro PostgreSQL `42P16: cannot drop columns from view` ao tentar `CREATE OR REPLACE VIEW` com lista de colunas diferente da view atual.
- **`migrations/20260504_recreate_front_views_staging.sql`** recria as views do frontend em **staging/dev** com `DROP VIEW IF EXISTS` seguido de `CREATE VIEW` (definição alinhada ao consolidado). **Não apaga dados** nas tabelas base; pode, no entanto, **quebrar clientes antigos** que dependiam de colunas já não expostas pela view.
- **Produção:** alterar ou recriar views deve ser feito com mais cuidado (compatibilidade com o frontend em produção, ordem de deploy, eventual período em que convivem duas versões da API, etc.).

## O que o SQL cria

- Extensão necessária:
  - `pgcrypto`
- Tabela principal:
  - `public.edital`
- Tabelas de roteamento de conteúdo:
  - `public.pesquisa`
  - `public.noticia`
- Tabelas auxiliares:
  - `public.edital_anexo`
  - `public.edital_extra_campo`
  - `public.carga_execucao`
  - `public.edital_historico`
- Views:
  - `public.vw_editais_front`
  - `public.vw_editais_admin`
- Índices de busca/performance:
  - btree por `link`, status e campos de filtro
  - GIN para `extras` e arrays (`area_*`, `setor_estrategico`, `tags`)

## Ordem lógica interna

1. Extensão
2. Tabelas base (`edital`, `noticia`, `pesquisa`)
3. Tabelas auxiliares
4. Índices
5. Views
6. Comentários
7. Seção de referência RLS (comentada)

## Como backend e frontend usam isso

- Backend (`CORE/loader.py`):
  - escreve principalmente em `public.edital`
  - roteia conteúdo para `public.pesquisa` e `public.noticia` via `upsert_routed_item`
  - persiste anexos em `public.edital_anexo`
  - persiste extras em `public.edital_extra_campo`
  - registra execução em `public.carga_execucao`
  - registra mudanças em `public.edital_historico`
- Frontend:
  - consulta principal via `public.vw_editais_front`
  - compatibilidade legada preservada: `vw_editais_front` expõe
    - canônicos: `fonte_recurso`, `prazo_envio`
    - aliases legados: `fonte`, `fim_inscricao`

## Cuidados antes de rodar

- Executar em **desenvolvimento/staging** primeiro.
- Revisar políticas RLS antes de ativar em produção.
- Não contém migração de dados legados (somente estrutura).
- Não contém chaves, URLs sensíveis ou dados reais.

## Divergências e observações importantes

- O projeto tem evolução histórica de schema (ex.: colunas legadas e novas convivendo).
- Este consolidado prioriza compatibilidade com o código atual (`loader.py` + migrations recentes).
- Alguns campos foram incluídos como colunas opcionais para reduzir quebra entre ambientes com versões diferentes.
- Em especial para `public.pesquisa`, campos de classificação como `setor_estrategico`, `area_cientifica`, `area_tecnologica` e `tags` estão como `text[]` para evitar erro de *malformed array literal*.
- Índice dedicado em `codigo_oportunidade` foi incluído em `edital` (e também em `pesquisa`/`noticia` para busca e manutenção de desempenho em consultas por código).

## Não faz

- Não executa `DROP TABLE`
- Não executa `DELETE`
- Não executa `TRUNCATE`
- Não aplica migrations automaticamente
- Não roda loader apply

