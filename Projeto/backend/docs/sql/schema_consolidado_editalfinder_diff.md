# Diff de schema consolidado vs backend

Data: 2026-05-04  
Arquivos comparados:
- `docs/sql/schema_consolidado_editalfinder.sql`
- `CORE/schema_sql_completo.sql`
- `migrations/20260430_add_edital_filter_columns.sql`
- `migrations/20260501_create_carga_execucao_and_edital_historico.sql`
- `migrations/20260504_create_noticia_pesquisa_tables.sql`
- `CORE/loader.py` (`map_to_db_schema`, `map_to_content_schema`, `upsert_routed_item`)

## Conclusão geral

- O consolidado está **majoritariamente compatível** com o backend atual.
- Há divergências de nomenclatura e alguns campos “documentais” no SQL consolidado que não são usados pelo loader.
- A compatibilidade legada de `vw_editais_front` foi **ajustada** com aliases (`fonte`, `fim_inscricao`) sem remover os canônicos.

## 1) Campos usados no loader e ausentes no SQL consolidado

Nenhum campo crítico do payload de `map_to_db_schema()` ou `map_to_content_schema()` ficou ausente nas tabelas alvo:
- `public.edital`: cobre os campos retornados por `map_to_db_schema`.
- `public.pesquisa` e `public.noticia`: cobrem o payload de `map_to_content_schema`.

Observação:
- `save_detail_tables()` escreve `edital_anexo` com `nome`, `url`, `tipo`; esses campos existem.
- `save_detail_tables()` escreve `edital_extra_campo` com `chave`, `valor`, `tipo_dado`, `tamanho_valor`, `ordem`; esses campos existem.

## 2) Campos no SQL consolidado não usados diretamente pelo backend

### `public.edital`
- `data_encerramento`
- `orgao`
- `uf`
- `cidade`
- `valor_estimado`
- `origem_portal` (fica normalmente em `extras`)
- `valor_novo`, `valor_antigo`

### `public.pesquisa` / `public.noticia`
- `fonte_recurso`, `prazo_envio`, `origem_portal`, `perfil_ideal`, `publico_alvo`, `qualidade_dado`, `validacao_status`, `codigo_oportunidade`, `numero_chamada`, `ativo` (não são preenchidos por `map_to_content_schema` hoje; podem ser úteis para evolução).

### `public.carga_execucao`
- `staging_flag`, `apply_status`, `sources`, `sources_selected`, `sources_excluded`, `total_itens_processados`, `inseridos`, `atualizados`, `ignorados`, `environment_safe`, `summary` não são escritos pelo `db_record` atual (que grava o bloco legado compatível: `status`, `fontes*`, `itens_*`, `environment_guard`, `relatorio_json`).

## 3) Tipos incompatíveis (checagem)

### Corrigido / compatível
- `setor_estrategico`, `area_cientifica`, `area_tecnologica`, `tags` em `pesquisa/noticia` como `text[]`, compatível com `map_to_content_schema` após normalização para lista.
- `extras` em `jsonb` nas três tabelas principais (`edital`, `pesquisa`, `noticia`).
- Datas:
  - `data_publicacao`, `prazo_envio` como `date` (compatível com mapeamento).
  - `criado_em`, `atualizado_em`, `ultima_coleta` como `timestamptz`.

### Potencial atenção (não quebra atual)
- `perfil_ideal` em `edital` como `text[]`; backend pode também carregar esse valor em `extras`.
- `publico_alvo` em `edital` é `text` e `publico_alvo_arr` é `text[]`; hoje o mapeamento principal usa `publico_alvo` (texto).

## 4) Colunas de upsert (`on_conflict`)

- `edital`: `upsert(... on_conflict="link")` → `public.edital.link` é `unique` ✅
- `pesquisa`: `upsert(... on_conflict="link")` → `public.pesquisa.link` é `unique` ✅
- `noticia`: `upsert(... on_conflict="link")` → `public.noticia.link` é `unique` ✅

## 5) Índices/unique necessários

### Presentes e adequados
- Unique por `link` nas 3 tabelas de upsert.
- Índice em `hash_deduplicacao` em `edital` e `hash_deduplicacao` em `pesquisa/noticia`.
- GIN em `extras` e arrays relevantes.

### Lacuna moderada
- Índice para `codigo_oportunidade` foi adicionado no consolidado:
  - `idx_edital_codigo_oportunidade`
  - `idx_pesquisa_codigo_oportunidade`
  - `idx_noticia_codigo_oportunidade`

## 6) Compatibilidade tabelas vs mappers

### `public.edital` vs `map_to_db_schema`
- Compatível para escrita principal.

### `public.pesquisa` / `public.noticia` vs `map_to_content_schema`
- Compatível.
- Campos extras presentes no SQL não são usados agora, mas não atrapalham.

## 7) `vw_editais_front` vs frontend/backend esperado

### Status atual
`vw_editais_front` no consolidado expõe ambos:
- canônicos: `fonte_recurso`, `prazo_envio`
- legados: `fonte` (`fonte_recurso as fonte`) e `fim_inscricao` (`prazo_envio as fim_inscricao`)

Resultado:
- compatibilidade preservada para clientes novos e legados.

## 8) Divergências entre `schema_sql_completo` e consolidado

- O consolidado removeu a parte de políticas RLS ativas (mantém só seção comentada) — decisão segura para documentação.
- O consolidado adiciona colunas e tabelas “superset” para documentação e onboarding, além do necessário para run atual.

## 9) Pontos que exigem conferência manual

1. Se deseja manter `carga_execucao` estritamente no shape atual do `db_record` ou aceitar o superset documental.
2. Confirmar se índice de `codigo_oportunidade` em `noticia` continuará útil no volume projetado.

