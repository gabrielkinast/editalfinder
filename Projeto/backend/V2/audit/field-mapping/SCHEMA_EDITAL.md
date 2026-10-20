# Schema local de `public.edital`

## Fonte adotada

**Fato:** a evidência local mais recente e mais próxima do banco é `backend/database/schema_current.sql:1-5`, datada de 2026-06-03 e descrita como resultado de introspecção read-only do OpenAPI/PostgREST. Ela declara `public.edital` com 107 colunas em `:12-123`. Este documento a usa como contrato local principal, mas o estado remoto atual é **não confirmado**.

Nullable abaixo significa apenas o que o DDL local declara: sem `NOT NULL` = sim. Não foram inferidas constraints remotas ausentes do arquivo.

## Colunas

| Coluna | Tipo | Nullable | Default/constraint local |
|---|---|---:|---|
| id_edital | bigserial | não | PK `edital_pkey` |
| acao | text | sim | — |
| access_reason | text | sim | — |
| access_status | text | sim | — |
| anexos | jsonb | sim | JSONB |
| area | text[] | sim | — |
| area_cientifica | text[] | sim | — |
| area_tecnologica | text[] | sim | — |
| ativo | boolean | sim | — |
| atualizado_em | timestamptz | não | `now()` |
| carencia | text | sim | — |
| chamada | text | sim | — |
| cidade | text | sim | — |
| classificacao_confianca | text | sim | — |
| codigo_oportunidade | text | sim | — |
| compatibilidade | jsonb | sim | JSONB |
| contato | text | sim | — |
| content_type_detectado | text | sim | — |
| contrapartida | text | sim | — |
| criado_em | timestamptz | não | `now()` |
| data_abertura | date | sim | — |
| data_encerramento | date | sim | — |
| data_publicacao | date | sim | — |
| data_resultado | date | sim | — |
| descricao | text | sim | — |
| descricao_en | text | sim | — |
| descricao_original | text | sim | — |
| descricao_traduzida | text | sim | — |
| documentos | jsonb | sim | JSONB |
| edital_numero | text | sim | — |
| elegibilidade | text | sim | — |
| estado | text | sim | — |
| extraction_mode | text | sim | — |
| extras | jsonb | não | `'{}'::jsonb` |
| finalidade_financiamento | text | sim | — |
| fonte_recurso | text | sim | — |
| garantias | text | sim | — |
| hash_deduplicacao | text | sim | — |
| id_organizacao | bigint | sim | FK não declarada nesta evidência |
| idioma_original | text | sim | — |
| instituicao | text | sim | — |
| justificativa | text | sim | — |
| limite_financiavel | text | sim | — |
| linha_credito | text | sim | — |
| link | text | não | UNIQUE `edital_link_key` |
| link_inscricao | text | sim | — |
| modalidade_financiamento | text | sim | — |
| moeda | text | sim | — |
| motivo_rejeicao | text | sim | — |
| municipio | text | sim | — |
| natureza_recurso | text | sim | — |
| numero_chamada | text | sim | — |
| numero_edital | text | sim | — |
| numero_processo | text | sim | — |
| objetivo | text | sim | — |
| ods | text | sim | — |
| orgao | text | sim | — |
| orgao_contratante | text | sim | — |
| orgao_responsavel | text | sim | — |
| origem_portal | text | sim | — |
| pais | text | sim | — |
| pdf_resumo | text | sim | — |
| pdf_url | text | sim | — |
| percentual_financiavel | text | sim | — |
| perfil_ideal | text[] | sim | — |
| prazo_amortizacao | text | sim | — |
| prazo_carencia | text | sim | — |
| prazo_envio | date | sim | — |
| prazo_pagamento | text | sim | — |
| prazo_total | text | sim | — |
| programa | text | sim | — |
| publico_alvo | text | sim | — |
| publico_alvo_arr | text[] | sim | — |
| publico_beneficiario | text | sim | — |
| qualidade_dado | integer | sim | — |
| recomendacao | text | sim | — |
| reembolsavel | boolean | sim | — |
| regiao | text | sim | — |
| score | integer | sim | — |
| score_detalhado | jsonb | sim | JSONB |
| setor_economico | text[] | sim | — |
| setor_estrategico | text[] | sim | — |
| situacao | text | sim | — |
| subprograma | text | sim | — |
| suspeito | boolean | sim | — |
| tags | text[] | sim | — |
| taxa_juros | text | sim | — |
| temas | text | sim | — |
| tipo_oportunidade | text | sim | — |
| tipo_recurso | text | sim | — |
| titulo | text | sim | — |
| titulo_en | text | sim | — |
| titulo_original | text | sim | — |
| titulo_traduzido | text | sim | — |
| traducao_automatica | boolean | sim | — |
| uf | text | sim | — |
| ultima_coleta | timestamptz | sim | — |
| unidade_responsavel | text | sim | — |
| url_detalhe | text | sim | — |
| url_listagem | text | sim | — |
| validacao_status | text | sim | — |
| valor_estimado | numeric | sim | — |
| valor_maximo | double precision | sim | — |
| valor_minimo | double precision | sim | — |
| valor_total | numeric | sim | — |
| valor_total_texto | text | sim | — |
| warnings | text[] | sim | — |

## Chaves e constraints

- PK: `id_edital` (`backend/database/schema_current.sql:121`).
- UNIQUE e chave de conflito operacional: `link` (`:58,122`; loader em `backend/CORE/loader.py:943-959`).
- FKs saindo de `edital`: nenhuma declarada no snapshot. `id_organizacao` existe, mas sua FK é **não confirmada**.
- FKs entrando em `edital`: `edital_anexo.id_edital`, `edital_extra_campo.id_edital` e `edital_historico.id_edital`, todas com `ON DELETE CASCADE`, aparecem em `backend/database/schema_current.sql:233-258,422-439`.
- CHECK constraints: nenhuma declarada para `edital`; estado remoto **não confirmado**.
- JSONB: `anexos`, `compatibilidade`, `documentos`, `extras`, `score_detalhado`. Não há coluna `json` simples.

## Evidências e versões divergentes

- Principal: `backend/database/schema_current.sql:1-123` (107 colunas, `link NOT NULL`).
- Migrações cumulativas: `backend/migrations/20260504_align_supabase_backend_contract.sql:186-225` e `20260505_add_missing_edital_columns_from_loader_payload.sql:23-120`.
- `backend/CORE/schema_sql_completo.sql:9-36,238-310` é anterior/incompleto frente ao snapshot e declara menos campos; sua view também diverge.
- `frontend/EditalFinder-React/schema_sql_completo.sql:9-37` é ainda mais legado; inclui `status` e `estado` em sentido antigo e não representa as 107 colunas.
- `backend/docs/sql/schema_consolidado_editalfinder.sql:36-118` é documentação consolidada, não substitui a introspecção.
- Propostas em `backend/docs/sql/PROPOSAL_*.sql` são propostas, não evidência de aplicação.

Conclusão: o contrato local mais atual é o snapshot de 2026-06-03; schema remoto atual, FKs e constraints adicionais são **não confirmados**.
