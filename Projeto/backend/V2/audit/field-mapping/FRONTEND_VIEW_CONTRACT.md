# Contrato das views de editais

## View realmente solicitada pela listagem

**Fato:** `frontend/EditalFinder-React/src/config/env.js:53` define `VIEW_EDITAIS` a partir de `VITE_VIEW_EDITAIS`, com default `vw_editais_front`; `.env.example:35` repete esse valor. `dataService.getEditais` consulta essa variável com `select('*')`, paginação de 1.000 e ordem por `atualizado_em`, tentando `id_edital` se a ordem falhar (`services/dataService.js:99-148`). Se a view falhar **ou retornar zero linhas**, consulta diretamente `edital` (`:150-169`). Logo, a view consumida por default é `public.vw_editais_front`, mas o nome efetivo em runtime é configurável e **não confirmado** sem o ambiente.

## Definição local mais atual/reprodutível

`backend/database/schema_current.sql:517-577` incorpora o corpo da migração de views mais recente versionada (`backend/migrations/20260505_recreate_edital_views_credito_staging.sql:15-60`).

### `public.vw_editais_front`

- Fonte: somente `public.edital e`; sem JOIN (`schema_current.sql:532-574`).
- Colunas: `id`, `titulo`, `descricao`, `fonte_recurso`, `fonte`, `link`, `pdf_url`, `prazo_envio`, `fim_inscricao`, `data_publicacao`, `tipo_oportunidade`, `tipo_recurso`, `natureza_recurso`, `reembolsavel`, `linha_credito`, `modalidade_financiamento`, `taxa_juros`, `prazo_carencia`, `prazo_amortizacao`, `contrapartida`, `garantias`, `valor_minimo`, `valor_maximo`, `perfil_ideal`, `publico_alvo`, `area_cientifica`, `area_tecnologica`, `setor_estrategico`, `setor_economico`, `pais`, `regiao`, `uf`, `validacao_status`, `qualidade_dado`, `classificacao_confianca`, `ativo`, `situacao`, `extras`, `criado_em`, `atualizado_em`.
- Aliases/derivados: `id_edital AS id`; `fonte_recurso AS fonte` (mantém também o original); `prazo_envio AS fim_inscricao` (mantém original); `publico_alvo_arr AS publico_alvo`.
- WHERE/JOIN: nenhum nessa versão.

### `public.vw_editais_admin`

- Definição: `SELECT * FROM public.vw_editais_front`; sem campos adicionais (`schema_current.sql:576-577`).
- Não alimenta a listagem pública no código encontrado.

### `public.vw_editais_favoritos_front`

- O snapshot apenas registra sua exposição, sem DDL inline (`schema_current.sql:579-586`); colunas, JOINs e derivados são **não confirmados localmente**.
- É consultada por `favoritosService.fetchFavoritos` via nome configurável, filtrando `id_usuario` e descartando linhas com `ativo=false` (`frontend/EditalFinder-React/src/services/favoritosService.js:110-138`; config em `src/config/env.js:70-74`). Ela alimenta favoritos, não o catálogo-base.

## Definições divergentes de `vw_editais_front`

| Arquivo | Diferença relevante |
|---|---|
| `backend/migrations/20260430_add_edital_filter_columns.sql:59-114` | Versão inicial; `id_edital` sem alias e conjunto diferente de colunas. |
| `backend/CORE/schema_sql_completo.sql:313-366` | `id_edital`; omite `prazo_envio` original, `regiao`, `uf`, qualidade; inclui vários campos internacionais/processuais. |
| `backend/migrations/20260504_align_supabase_backend_contract.sql:524-558` | Versão intermediária. |
| `backend/migrations/20260504_recreate_front_views_staging.sql:33-70` | Recria front/admin para staging. |
| `backend/migrations/20260505_recreate_edital_views_credito_staging.sql:15-60` | Base do snapshot atual; inclui crédito, região, UF e qualidade. |
| `backend/docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql:18-110` | Script operacional/documental com filtros de ativo, curadoria, prazo, recência e qualidade. Aplicação remota não confirmada. |
| `backend/docs/sql/HOTFIX_VW_EDITAIS_FRONT_RELAX_VISIBILITY.sql:25-80` | Relaxa o WHERE para ativo + quatro flags `hidden_*`; aplicação remota não confirmada. |
| `backend/docs/sql/PROPOSAL_VW_EDITAIS_FRONT_*.sql` | Propostas, não tratar como aplicadas. |

## Conclusão probatória

- Consumidor efetivo no código: `dataService.getEditais` -> `VIEW_EDITAIS` -> default `vw_editais_front`.
- Contrato local mais atual: `schema_current.sql:532-574`.
- Definição efetivamente instalada, filtros SQL, security invoker e RLS da view: **não confirmados** sem Supabase remoto.
