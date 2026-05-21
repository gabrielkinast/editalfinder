# Schema — Concursos & Seleções

Este documento descreve o modelo de dados do módulo **Concursos & Seleções**, alinhado ao plano em [`CONCURSOS_SELECOES_MODULE_PLAN.md`](./CONCURSOS_SELECOES_MODULE_PLAN.md). O DDL vive em [`sql/CREATE_CONCURSO_SELECAO.sql`](./sql/CREATE_CONCURSO_SELECAO.sql) (não executar automaticamente; aplicar manualmente em staging/produção quando a equipa decidir).

## Objetivo da tabela `public.concurso_selecao`

Armazenar oportunidades de **ingresso por seleção**: concursos públicos, processos seletivos para docência ou cargos técnico-administrativos, estágios, residências, vestibulares, bolsas/programas de ingresso, etc. Cada linha representa um certame ou anúncio agregável com datas, localização, remuneração (quando aplicável), links e metadados de proveniência.

## Diferença face a `public.edital`

| Aspeto | `public.edital` (Radar / fomento) | `public.concurso_selecao` |
|--------|-------------------------------------|---------------------------|
| Domínio | Editais de **fomento**, bolsas de pesquisa, chamadas científicas | **Seleção para vínculo ou ingresso** (emprego público, docência, vestibular, etc.) |
| Relação com o plano | Módulo existente; favoritos e RLS atuais | Módulo novo; **sem misturar** tabelas nem políticas com `edital` |
| Identificador | Convém manter convenções do projeto Radar | `id_concurso` (bigserial) próprio do módulo |

Não há FK obrigatória entre os dois módulos; eventual correlação futura seria opcional e documentada à parte.

## Campos principais

- **Identidade e título**: `id_concurso`, `titulo`, `tipo_selecao`, `categoria`.
- **Quem / onde**: `orgao`, `instituicao`, `banca`, `cargo`, `curso`, `area`, `nivel_escolaridade`, `estado`, `municipio`, `regiao`, `modalidade`.
- **Oferta**: `numero_vagas`, `salario_min`, `salario_max`, `taxa_inscricao`.
- **Calendário** (`date`): `data_publicacao`, `data_inicio_inscricao`, `data_fim_inscricao`, `data_prova`.
- **Estado do certame**: `status` (workflow) e `ativo` (publicação na app — soft-hide).
- **Proveniência e qualidade**: `link`, `link_edital`, `fonte`, `fonte_tipo`, `validacao_status`, `qualidade_dado`.
- **Flexível**: `tags` (`text[]`), `extras` (`jsonb`, default `{}`) para crawlers e dedupe.
- **Auditoria**: `criado_em`, `atualizado_em` (este último atualizado por trigger em `UPDATE`).

## `status` (workflow do certame)

Valores permitidos (CHECK na tabela):

- `ativo`
- `inscricoes_abertas`
- `inscricoes_encerradas`
- `prova_proxima`
- `encerrado`
- `suspenso`
- `cancelado`

Default na inserção: `ativo`. A coluna booleana **`ativo`** controla se o registo entra na listagem pública (`vw_concursos_front`); não confundir com `status`.

## `tipo_selecao`

Valores permitidos:

- `concurso_publico`
- `processo_seletivo`
- `professor`
- `coordenador`
- `tecnico_administrativo`
- `estagio`
- `residencia`
- `vestibular`
- `bolsa_estudo`
- `programa_ingresso`

## `validacao_status` e `fonte_tipo`

**`validacao_status`** (default `incompleto`): `valido`, `incompleto`, `suspeito`, `acesso_limitado`. A view pública inclui apenas `valido` e `incompleto` (exclui conteúdo suspeito ou com acesso limitado por defeito).

**`fonte_tipo`** (nullable): `banca`, `agregador`, `instituicao`, `governo`, `universidade`, `vestibular`, `outro`.

## Índices e unicidade

- **Unicidade**: índice único em `(fonte, link)` — dedupe por origem + URL canónica (mais robusto que só `link`).
- B-tree em `tipo_selecao`, `estado`, `municipio`, `banca`, `instituicao`, `data_fim_inscricao`, `data_prova`, `status`, `ativo`.
- **GIN** em `tags` e em `extras` (`jsonb_path_ops`).

## Views

### `public.vw_concursos_front`

- Filtro base: `ativo = true`, `validacao_status IN ('valido','incompleto')`, **`status` não pode ser `cancelado` nem `suspenso`**.
- **Recência (não apaga linhas na tabela):** só entram oportunidades ainda relevantes no calendário ou muito recentes sem datas:
  1. `data_fim_inscricao` **não nula** e `>= CURRENT_DATE`; **ou**
  2. `data_prova` **não nula** e `>= CURRENT_DATE`; **ou**
  3. **Sem** `data_fim_inscricao` e **sem** `data_prova`, **e** (`criado_em` nos últimos 90 dias **ou** `data_publicacao` nos últimos 90 dias em relação a `CURRENT_DATE`).
- Tudo o que falhar esta combinação **continua em `public.concurso_selecao`** e é visível em **`vw_concursos_admin`** (histórico, curadoria, reprocessamento).
- Colunas para listagens, filtros e cards; inclui `extras` para badges leves.
- Campos derivados (baseados em `CURRENT_DATE` na sessão do servidor):
  - **`dias_ate_fim_inscricao`**: `data_fim_inscricao - CURRENT_DATE` (inteiro; null se sem data).
  - **`dias_ate_prova`**: idem para `data_prova`.
  - **`inscricoes_abertas`**: `CURRENT_DATE` entre `data_inicio_inscricao` e `data_fim_inscricao` (false se datas incompletas).
  - **`prova_proxima`**: `data_prova` entre hoje e hoje + 30 dias (ajustável na view se o produto quiser outra janela).

DDL completo: [`sql/CREATE_CONCURSO_SELECAO.sql`](./sql/CREATE_CONCURSO_SELECAO.sql). Patch só das views: [`sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql`](./sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql).

### `public.vw_concursos_admin`

- Todas as linhas e todas as colunas da tabela base (inclui inativos, `suspeito`, `acesso_limitado`, `extras` completos).

### `public.vw_vestibulares_front` (opcional)

- `SELECT *` de `vw_concursos_front` onde `tipo_selecao IN ('vestibular','programa_ingresso','bolsa_estudo')` — herda automaticamente a mesma regra de recência e exclusões da front.

## Trigger

Função `public.touch_concurso_selecao_atualizado_em()` + trigger `BEFORE UPDATE` em `public.concurso_selecao` para definir `atualizado_em = now()`. Não reutiliza trigger de `edital` (módulo isolado).

## Próximos passos (fora deste DDL)

1. **RLS** dedicado a `public.concurso_selecao` e grants (`anon` / `authenticated`) — ficheiro separado, sem alterar RLS existente de outras tabelas.
2. **Favoritos / alertas** do módulo (tabelas próprias, sem tocar em favoritos de edital).
3. **Loaders e crawlers** que preencham `extras`, `validacao_status` e respeitem `(fonte, link)`.
4. **API e frontend** consumindo `vw_concursos_front` ou RPC com os mesmos filtros.
5. Ajustar a janela de **`prova_proxima`** (ex.: 7 vs 30 dias) se o UX o exigir.

---

*Última atualização: alinhado ao script `CREATE_CONCURSO_SELECAO.sql` na pasta `docs/sql/`.*
