# Validação da migration candidata 000001 — EditalFinder V2

## Status

Este roteiro acompanha `supabase/migrations/20260717_000001_editalfinder_v2_initial_schema.sql`. A migration é **candidata e não foi executada** local ou remotamente nesta tarefa.

Fonte de verdade usada:

- `docs/v2/DECISIONS_V1.md`;
- `docs/v2/SCHEMA_DESIGN_V1.md`;
- `docs/v2/DATA_CONTRACT.md`;
- `docs/v2/GEOGRAPHY_CONTRACT.md`;
- `docs/v2/SOURCE_SCOPE.md`;
- decisões fechadas fornecidas para a migration 000001.

## Divergências documentais resolvidas nesta migration

Os documentos V1 não foram alterados. As decisões fechadas desta migration prevalecem nos pontos abaixo:

1. `DATA_CONTRACT.md` ainda descreve confiança categórica em trechos antigos; a migration usa `numeric(5,4)` entre 0 e 1, conforme decisão posterior aprovada.
2. `GEOGRAPHY_CONTRACT.md` exemplifica confiança como `alta`, `media` e `baixa`; localizações inferidas usam confiança numérica na migration.
3. `qualidade_dado` e `qualidade_detalhes` aparecem como proposta no desenho, mas foram deliberadamente excluídos até existir contrato de cálculo.
4. O schema JSON interno de `proveniencia` continua parcialmente aberto. A migration fixa apenas o envelope V1 obrigatório: `schema_version = 1` e `campos` como objeto.
5. O documento geográfico mais antigo ainda menciona localização principal como questão aberta; a migration segue a decisão V1 posterior de relação 1:N.

## Pré-requisitos

- Projeto Supabase/PostgreSQL de staging vazio para os objetos V2.
- PostgreSQL com `gen_random_uuid()` disponível. Em versões atuais do PostgreSQL ela é nativa; confirmar com consulta read-only antes da aplicação.
- Linguagem `plpgsql` disponível para a função de `atualizado_em`.
- Versão PostgreSQL compatível com view `security_invoker`.
- Roles Supabase `anon` e `authenticated` existentes, pois a migration revoga privilégios explicitamente dessas roles.
- Nenhum objeto homônimo em `public`, especialmente as 12 tabelas, a função e a view.
- Backup ou projeto descartável, apesar de a primeira aplicação ser destinada a staging vazio.
- Revisão humana das constraints, índices, política de cascatas e contrato da view.
- Execução futura por ferramenta de migration com permissão suficiente; não executar manualmente parcialmente.

Consultas read-only de pré-requisito:

```sql
select current_setting('server_version_num')::integer as server_version_num;

select to_regprocedure('gen_random_uuid()') as gen_random_uuid_disponivel;

select lanname
from pg_language
where lanname = 'plpgsql';

select rolname
from pg_roles
where rolname in ('anon', 'authenticated', 'service_role')
order by rolname;

select n.nspname as schema_name, c.relname, c.relkind
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relname in (
    'fonte', 'organizacao', 'tipo_oportunidade', 'tipo_recurso', 'area',
    'execucao_coleta', 'item_coletado', 'item_oportunidade', 'oportunidade',
    'oportunidade_identificador', 'oportunidade_localizacao',
    'oportunidade_area', 'vw_oportunidades_front_v2'
  )
order by c.relname;
```

No staging vazio, a última consulta deve retornar zero linhas antes da aplicação.

## Objetos esperados

### Relações e função

- 12 tabelas:
  - `fonte`;
  - `organizacao`;
  - `tipo_oportunidade`;
  - `tipo_recurso`;
  - `area`;
  - `execucao_coleta`;
  - `item_coletado`;
  - `oportunidade`;
  - `oportunidade_identificador`;
  - `oportunidade_localizacao`;
  - `item_oportunidade`;
  - `oportunidade_area`.
- 1 view: `vw_oportunidades_front_v2`.
- 1 função compartilhada: `set_atualizado_em()`.
- 6 triggers de atualização automática, somente nas entidades mutáveis aprovadas.
- 0 policies RLS.
- RLS habilitada nas 12 tabelas.
- 15 comandos `REVOKE`: 13 sobre relações e 2 sobre a função de trigger.
- Nenhum seed, usuário, favorito, cliente, Radar, Storage ou objeto legado.

### Contagem estática da migration candidata

| Tipo | Quantidade | Observação |
|---|---:|---|
| Tabelas | 12 | `CREATE TABLE` |
| Views | 1 | View com `security_invoker` |
| Funções | 1 | Trigger compartilhado |
| Índices explícitos | 28 | Não inclui índices criados implicitamente por PK/UNIQUE |
| Índices esperados incluindo PK/UNIQUE | 45 | 28 explícitos + 12 PKs + 5 UNIQUEs; confirmar após aplicação |
| Constraints declaradas | 89 | 12 PKs, 13 FKs, 5 UNIQUEs e 59 CHECKs; 80 usam cláusula `CONSTRAINT` explícita e 9 PKs UUID são inline |
| Triggers | 6 | Um por entidade mutável |
| Policies | 0 | Nenhuma política para `anon` ou `authenticated` |
| Comandos `REVOKE` | 15 | 12 tabelas + 1 view + 2 revogações sobre a função compartilhada |

## Validação read-only após futura aplicação

### Tabelas, view e função

```sql
select table_name, table_type
from information_schema.tables
where table_schema = 'public'
  and table_name in (
    'fonte', 'organizacao', 'tipo_oportunidade', 'tipo_recurso', 'area',
    'execucao_coleta', 'item_coletado', 'item_oportunidade', 'oportunidade',
    'oportunidade_identificador', 'oportunidade_localizacao',
    'oportunidade_area'
  )
order by table_name;

select table_name
from information_schema.views
where table_schema = 'public'
  and table_name = 'vw_oportunidades_front_v2';

select p.proname, pg_get_function_identity_arguments(p.oid) as argumentos
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public'
  and p.proname = 'set_atualizado_em';
```

### Colunas e defaults críticos

```sql
select table_name, column_name, data_type, is_nullable, column_default
from information_schema.columns
where table_schema = 'public'
  and (
    (table_name = 'oportunidade' and column_name in (
      'id', 'url_oficial', 'prazo_submissao', 'motivo_sem_prazo',
      'confianca_classificacao', 'proveniencia', 'dados_extras'
    ))
    or (table_name = 'item_coletado' and column_name in (
      'id', 'payload_bruto', 'estado_processamento', 'processado_em'
    ))
    or (table_name = 'item_oportunidade' and column_name in (
      'item_coletado_id', 'oportunidade_id', 'papel', 'confianca'
    ))
  )
order by table_name, ordinal_position;
```

### Constraints e cascatas

```sql
select
  conrelid::regclass as tabela,
  conname,
  contype,
  pg_get_constraintdef(oid, true) as definicao
from pg_constraint
where connamespace = 'public'::regnamespace
  and conrelid <> 0
order by conrelid::regclass::text, conname;
```

Confirmar especialmente:

- organização, fonte e taxonomias com `ON DELETE RESTRICT`;
- `execucao_coleta → item_coletado` com `ON DELETE RESTRICT`;
- filhos próprios da oportunidade e ambas as FKs de `item_oportunidade` com `ON DELETE CASCADE`;
- PK composta nas três estruturas sem UUID próprio: `item_oportunidade`, `oportunidade_area` e `oportunidade_identificador`;
- PK do identificador composta por tipo, namespace, fonte e valor normalizado.

### Índices

```sql
select tablename, indexname, indexdef
from pg_indexes
where schemaname = 'public'
  and tablename in (
    'fonte', 'organizacao', 'tipo_oportunidade', 'tipo_recurso', 'area',
    'execucao_coleta', 'item_coletado', 'item_oportunidade', 'oportunidade',
    'oportunidade_identificador', 'oportunidade_localizacao',
    'oportunidade_area'
  )
order by tablename, indexname;
```

Não deve existir índice `pg_trgm`, GIN de busca textual ou UNIQUE direto em `oportunidade.url_oficial`.

### Triggers

```sql
select event_object_table, trigger_name, action_timing, event_manipulation
from information_schema.triggers
where trigger_schema = 'public'
order by event_object_table, trigger_name;
```

Devem existir exatamente seis triggers: `fonte`, `organizacao`, `tipo_oportunidade`, `tipo_recurso`, `area` e `oportunidade`.

### RLS e ausência de policies

```sql
select c.relname, c.relrowsecurity, c.relforcerowsecurity
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relname in (
    'fonte', 'organizacao', 'tipo_oportunidade', 'tipo_recurso', 'area',
    'execucao_coleta', 'item_coletado', 'item_oportunidade', 'oportunidade',
    'oportunidade_identificador', 'oportunidade_localizacao',
    'oportunidade_area'
  )
order by c.relname;

select schemaname, tablename, policyname, roles, cmd
from pg_policies
where schemaname = 'public'
  and tablename in (
    'fonte', 'organizacao', 'tipo_oportunidade', 'tipo_recurso', 'area',
    'execucao_coleta', 'item_coletado', 'item_oportunidade', 'oportunidade',
    'oportunidade_identificador', 'oportunidade_localizacao',
    'oportunidade_area'
  );

select grantee, table_name, privilege_type
from information_schema.role_table_grants
where table_schema = 'public'
  and grantee in ('anon', 'authenticated')
  and table_name in (
    'fonte', 'organizacao', 'tipo_oportunidade', 'tipo_recurso', 'area',
    'execucao_coleta', 'item_coletado', 'item_oportunidade', 'oportunidade',
    'oportunidade_identificador', 'oportunidade_localizacao',
    'oportunidade_area', 'vw_oportunidades_front_v2'
  );
```

Resultados esperados: `relrowsecurity = true` nas 12 tabelas; zero policies; zero grants para `anon` e `authenticated` nos objetos desta migration.

### Função de trigger e privilégios

```sql
select
  has_function_privilege('anon', 'public.set_atualizado_em()', 'EXECUTE')
    as anon_pode_executar,
  has_function_privilege('authenticated', 'public.set_atualizado_em()', 'EXECUTE')
    as authenticated_pode_executar;

select coalesce(
  bool_or(a.grantee = 0 and a.privilege_type = 'EXECUTE'),
  false
) as public_pode_executar
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
where n.nspname = 'public'
  and p.proname = 'set_atualizado_em'
  and pg_get_function_identity_arguments(p.oid) = '';
```

Os três resultados devem ser `false`. Essas revogações não impedem o uso da função pelos triggers/owner. O acesso operacional do `service_role` deve ser confirmado no teste específico do ambiente, sem criar concessão pública.

## Testes transacionais de constraints

Os exemplos desta seção **fazem escritas temporárias**. Executá-los somente em banco local descartável ou staging vazio autorizado, sempre dentro de transação revertida. Eles não foram executados nesta tarefa.

### Cenário válido mínimo

```sql
begin;

insert into public.fonte (id, codigo, nome, status_integracao)
values ('00000000-0000-4000-8000-000000000001', 'fonte_teste', 'Fonte Teste', 'piloto');

insert into public.execucao_coleta (
  id, fonte_id, status, versao_coletor
) values (
  '00000000-0000-4000-8000-000000000002',
  '00000000-0000-4000-8000-000000000001',
  'iniciada',
  'test-1'
);

insert into public.item_coletado (
  id, execucao_coleta_id, payload_bruto, hash_payload
) values (
  '00000000-0000-4000-8000-000000000003',
  '00000000-0000-4000-8000-000000000002',
  '{"titulo":"Teste"}'::jsonb,
  'hash-teste'
);

insert into public.oportunidade (
  id, fonte_id, titulo, url_oficial, motivo_sem_prazo,
  escopo_geografico, proveniencia
) values (
  '00000000-0000-4000-8000-000000000004',
  '00000000-0000-4000-8000-000000000001',
  'Oportunidade válida',
  'https://example.org/oportunidades/1',
  'nao_informado',
  'internacional',
  '{"schema_version":1,"campos":{}}'::jsonb
);

insert into public.item_oportunidade (
  item_coletado_id, oportunidade_id, papel, confianca
) values (
  '00000000-0000-4000-8000-000000000003',
  '00000000-0000-4000-8000-000000000004',
  'origem',
  0.9500
);

insert into public.oportunidade_localizacao (
  oportunidade_id, papel_localizacao, pais_codigo, municipio,
  regiao_brasil, estado_codigo
) values (
  '00000000-0000-4000-8000-000000000004',
  'elegibilidade',
  'US',
  'Washington',
  null,
  null
);

select id, titulo, status_temporal, dias_para_prazo, localizacoes, areas
from public.vw_oportunidades_front_v2
where id = '00000000-0000-4000-8000-000000000004';

rollback;
```

Resultado esperado na view: uma linha, `status_temporal = sem_prazo`, `dias_para_prazo = null`, uma localização estrangeira com `pais_codigo = US` e `municipio = Washington`, e array vazio de áreas.

### Casos geográficos válidos

| País | Município | Estado | Região brasileira | Motivo |
|---|---|---|---|---|
| `US` | `Washington` | `null` | `null` | Município estrangeiro é permitido; UF e região brasileira não se aplicam |
| `BR` | `null` | `RS` | `sul` | Correspondência oficial |
| `BR` | `null` | `SP` | `sudeste` | Correspondência oficial |
| `BR` | `null` | `RS` | `null` | Região pode permanecer ausente quando apenas a UF é conhecida |

### Casos inválidos que devem falhar

Executar cada caso isoladamente após preparar as FKs necessárias e sempre reverter a transação:

| Caso inválido | Exemplo | Constraint esperada |
|---|---|---|
| Confiança maior que 1 | `item_oportunidade.confianca = 1.0001` | `item_oportunidade_confianca_check` |
| Confiança negativa | `oportunidade.confianca_classificacao = -0.0001` | `oportunidade_confianca_check` |
| Prazo com motivo | prazo preenchido e `motivo_sem_prazo = nao_informado` | `oportunidade_prazo_check` |
| Prazo ausente sem motivo | ambos nulos | `oportunidade_prazo_check` |
| País minúsculo | `pais_codigo = br` | check de país da tabela correspondente |
| Moeda curta | `moeda = BR` | `oportunidade_moeda_check` |
| UF estrangeira | país `US` e estado `RS` | `oportunidade_localizacao_geografia_brasil_check` |
| Região brasileira em país estrangeiro | país `JP` e região `sudeste` | `oportunidade_localizacao_geografia_brasil_check` |
| UF/região incoerentes | estado `RS` e região `sudeste` | `oportunidade_localizacao_uf_regiao_check` |
| UF/região incoerentes | estado `SP` e região `sul` | `oportunidade_localizacao_uf_regiao_check` |
| Estado não UF | `estado_codigo = ZZ` | `oportunidade_localizacao_estado_check` |
| Papel de localização livre | `papel_localizacao = sede` | `oportunidade_localizacao_papel_check` |
| Papel item–oportunidade livre | `papel = principal` | `item_oportunidade_papel_check` |
| Estado de item desconhecido | `estado_processamento = pendente` | `item_coletado_estado_check` |
| Rejeição sem motivo | estado `rejeitado`, motivo nulo | `item_coletado_rejeicao_check` |
| Erro sem código | estado `erro`, código nulo | `item_coletado_erro_check` |
| Proveniência sem envelope | `proveniencia = {}` | `oportunidade_proveniencia_check` |
| Segunda área principal | duas áreas `principal = true` na mesma oportunidade | `oportunidade_area_principal_uidx` |
| URL oficial duplicada | duas oportunidades com a mesma URL | deve ser aceita em `oportunidade`; a colisão deve ocorrer somente ao repetir a mesma identidade composta em `oportunidade_identificador` |

## Teste futuro de RLS

Após a aplicação autorizada, usar uma sessão descartável sem credenciais privilegiadas. Como a migration revoga grants e não cria policies, consultas como `anon` e `authenticated` devem falhar por falta de privilégio; não devem retornar catálogo.

Exemplo administrativo para inspeção controlada:

```sql
begin;
set local role anon;
select * from public.vw_oportunidades_front_v2 limit 1;
rollback;
```

Resultado esperado: erro de permissão. Repetir com `authenticated`. Não criar policy apenas para fazer o teste passar.

O teste do pipeline com service role deve ocorrer separadamente, em ambiente server-side autorizado, e confirmar escrita nas tabelas internas sem expor a chave ao cliente.

### Grants futuros para a view

Nenhuma concessão pública é feita nesta migration. Como `vw_oportunidades_front_v2` usa `security_invoker`, qualquer abertura futura deve desenhar conjuntamente:

- o grant de `SELECT` na view;
- os grants necessários nas relações subjacentes;
- as policies RLS dessas relações;
- os papéis consumidores e testes positivos/negativos.

Conceder `SELECT` somente na view pode não ser suficiente: o invocador precisa atravessar permissões e RLS das relações usadas pela view. Não alterar `security_invoker` como atalho para contornar esse desenho.

## Imutabilidade do payload bruto

`item_coletado.payload_bruto` é imutável **por contrato do pipeline**: depois da coleta, correções devem produzir novo item/reprocessamento rastreável, sem reescrever a evidência original. A migration 000001 não impõe essa imutabilidade por constraint, trigger ou policy. Portanto, service role e owners continuam tecnicamente capazes de atualizar a coluna; impedir ou auditar isso no banco exige decisão posterior.

## Teste futuro da view

Com massa transacional descartável, validar:

1. exatamente uma linha por oportunidade, mesmo com duas áreas e duas localizações;
2. arrays `areas` e `localizacoes` sem duplicação cartesiana;
3. ordenação determinística dos arrays;
4. `inativa` tem precedência sobre todos os estados temporais;
5. prazo anterior à data da sessão produz `encerrada`;
6. prazo igual à data da sessão produz `vence_hoje`;
7. prazo futuro produz `aberta` e diferença inteira correta em `dias_para_prazo`;
8. prazo nulo com motivo controlado produz `sem_prazo`;
9. texto de `situacao_informada` permanece independente de `status_temporal`;
10. oportunidade sem organização canônica preserva `organizacao_responsavel_texto` e retorna nome canônico nulo;
11. payload bruto, erros, proveniência detalhada e vínculos `item_oportunidade` não aparecem na view.

Consulta read-only de forma da view:

```sql
select column_name, data_type, ordinal_position
from information_schema.columns
where table_schema = 'public'
  and table_name = 'vw_oportunidades_front_v2'
order by ordinal_position;
```

## Procedimento de rollback para staging vazio

Aplicar somente se a migration tiver sido executada em staging vazio, não houver dados a preservar e houver autorização explícita. O rollback é destrutivo.

Ordem conceitual:

1. iniciar uma transação;
2. remover `vw_oportunidades_front_v2`;
3. remover tabelas de associação e filhas: `item_oportunidade`, `oportunidade_area`, `oportunidade_localizacao`, `oportunidade_identificador`;
4. remover `item_coletado`;
5. remover `oportunidade`;
6. remover `execucao_coleta`;
7. remover taxonomias e entidades de referência: `area`, `tipo_recurso`, `tipo_oportunidade`, `organizacao`, `fonte`;
8. remover `set_atualizado_em()` depois das tabelas/triggers;
9. confirmar que não restaram objetos V2;
10. concluir a transação.

Não usar `CASCADE` indiscriminadamente. Antes de qualquer rollback, listar dependências com consultas de catálogo e confirmar que o staging continua vazio. Uma migration reversa formal deve ser criada se o objeto já tiver consumidores ou dados.

## Riscos

1. `gen_random_uuid()` ou `security_invoker` podem variar conforme a versão PostgreSQL disponível.
2. A PK contextual de identificadores inclui `fonte_id`; a mesma identidade republicada por fontes distintas não colide automaticamente.
3. Regex de país e moeda valida formato, não a existência real no catálogo ISO; tabelas ISO foram adiadas.
4. A constraint de prazo obriga motivo em toda oportunidade sem prazo, aumentando rejeições/quarentena para dados incompletos.
5. `date` não preserva horário/fuso de deadlines que tenham corte intradiário.
6. `proveniencia` valida apenas o envelope, não cada evidência interna.
7. Confianças numéricas ainda exigem calibração por classificador e versão para serem comparáveis.
8. Revogar privilégios não substitui testes de RLS, grants e comportamento da view no ambiente real.
9. Índices foram escolhidos pelo contrato, não por planos de execução com volume real.
10. A view usa `CURRENT_DATE`, portanto o resultado depende da timezone da sessão/banco; a regra operacional definitiva ainda precisa ser fechada.
11. A regra de uma única área principal é intencional, mas pode precisar mudar se o produto admitir empates.
12. A relação N:N exige idempotência do pipeline para evitar oportunidades duplicadas em páginas agregadoras.
13. Município permanece texto livre e pode existir para países estrangeiros; homônimos e variações linguísticas exigirão normalização futura.
14. A coerência UF/região é codificada em CHECK e precisará ser revisada se a divisão regional oficial mudar.
15. A imutabilidade de `payload_bruto` depende do comportamento do pipeline, pois não é garantida pela migration 000001.
16. Grants futuros na view `security_invoker` sem policies e privilégios coerentes nas relações subjacentes podem falhar ou abrir acesso além do pretendido.

## Itens deliberadamente adiados

- `qualidade_dado` e `qualidade_detalhes`;
- policies para `anon` e `authenticated`;
- grants públicos;
- usuários, profiles, favoritos e clientes;
- Radar;
- programa como entidade;
- `oportunidade_evento`;
- Supabase Storage e documentos grandes;
- busca textual, `pg_trgm` e similaridade;
- histórico/versionamento canônico completo;
- tabelas ISO de países e moedas;
- município canônico/código IBGE;
- taxonomia inicial e todos os seeds;
- fontes japonesas e chinesas;
- importação ou limpeza do legado;
- políticas definitivas de retenção de payload bruto;
- policies e testes operacionais de service role.
