# Validação da migration 000002 — seeds mínimos do staging V2

## Status e escopo

Este roteiro acompanha `supabase/migrations/20260718_000002_editalfinder_v2_initial_seeds.sql`. A migration foi preparada para revisão e **não foi executada** nesta tarefa.

Ela insere dados de referência somente em `tipo_oportunidade`, `tipo_recurso`, `area` e `fonte`. Não altera schema, policies, grants ou Legacy e não cria organizações, oportunidades, execuções, itens coletados ou associações.

## Pré-requisitos

1. Migration 000001 aplicada com sucesso.
2. As quatro tabelas de destino devem conservar as colunas e constraints da 000001.
3. Staging sem dados dependentes para eventual rollback.
4. Revisão editorial de nomes, descrições, URLs e ordem antes da aplicação.

## Identidade e idempotência

- UUIDs são explícitos e estáveis: prefixos `100...`, `200...`, `300...` e `400...` distinguem as quatro tabelas.
- Cada bloco usa `ON CONFLICT (codigo) DO NOTHING`.
- Reaplicação não sobrescreve nome, descrição, ordem, ativação, URL ou status já curados.
- Código preexistente com outro UUID é preservado.
- UUID reservado associado a outro código causa erro de PK, em vez de ocultar a colisão.

## Tipo de oportunidade × tipo de recurso

`tipo_oportunidade` descreve **a forma do processo ou instrumento**: chamada, edital, concurso ou credenciamento. `tipo_recurso` descreve **o que ele oferece ou contrata**: financiamento, bolsa, crédito, apoio ou contratação.

As dimensões são independentes. Uma chamada pública pode oferecer financiamento não reembolsável; um edital pode resultar em contratação. “Bolsa” aparece nas duas tabelas com sentidos distintos: forma de seleção e natureza do benefício. Notícia, resultado, portal e página institucional não são oportunidades e não aparecem nos seeds.

## Contagens esperadas

| Tabela | Seeds |
|---|---:|
| `tipo_oportunidade` | 8 |
| `tipo_recurso` | 9 |
| `area` | 15 |
| `fonte` | 10 |
| **Total** | **42** |

São contagens do conjunto gerenciado. Registros editoriais adicionais podem elevar o total da tabela; a lista de códigos é a autoridade.

## Códigos inseridos

### `tipo_oportunidade`

`chamada_publica`, `edital`, `bolsa`, `premio`, `concurso`, `credenciamento`, `encomenda_tecnologica`, `outra`.

### `tipo_recurso`

`financiamento_nao_reembolsavel`, `financiamento_reembolsavel`, `bolsa`, `premio_financeiro`, `credito`, `apoio_nao_financeiro`, `contratacao`, `misto`, `nao_identificado`.

### `area`

`multidisciplinar`, `ciencias_exatas_e_da_terra`, `engenharias`, `ciencias_biologicas`, `ciencias_da_saude`, `ciencias_agrarias`, `ciencias_sociais_aplicadas`, `ciencias_humanas`, `linguistica_letras_e_artes`, `tecnologia_e_inovacao`, `energia`, `meio_ambiente`, `defesa_e_aeroespacial`, `materiais`, `computacao_e_dados`.

`multidisciplinar` possui a primeira ordem editorial, mas não é fallback automático. Exige evidência de integração entre áreas.

### `fonte`

`fapergs`, `fapesp`, `cnpq`, `finep`, `bndes`, `grants_gov`, `nsf`, `arpa_e`, `horizon_europe`, `erc`.

Todas entram como `piloto`; nenhuma recebe `mvp_habilitada` antes do gate de readiness.

## Consultas read-only

### Contagens do conjunto

```sql
select 'tipo_oportunidade' as tabela, count(*) from public.tipo_oportunidade
where codigo in ('chamada_publica','edital','bolsa','premio','concurso','credenciamento','encomenda_tecnologica','outra')
union all
select 'tipo_recurso', count(*) from public.tipo_recurso
where codigo in ('financiamento_nao_reembolsavel','financiamento_reembolsavel','bolsa','premio_financeiro','credito','apoio_nao_financeiro','contratacao','misto','nao_identificado')
union all
select 'area', count(*) from public.area
where codigo in ('multidisciplinar','ciencias_exatas_e_da_terra','engenharias','ciencias_biologicas','ciencias_da_saude','ciencias_agrarias','ciencias_sociais_aplicadas','ciencias_humanas','linguistica_letras_e_artes','tecnologia_e_inovacao','energia','meio_ambiente','defesa_e_aeroespacial','materiais','computacao_e_dados')
union all
select 'fonte', count(*) from public.fonte
where codigo in ('fapergs','fapesp','cnpq','finep','bndes','grants_gov','nsf','arpa_e','horizon_europe','erc')
order by tabela;
```

Esperado: `8`, `9`, `15` e `10`.

### Conteúdo, UUIDs e ordem

```sql
select id, codigo, nome, descricao, ativo, ordem_exibicao
from public.tipo_oportunidade
where id::text like '10000000-0000-4000-8000-%'
order by ordem_exibicao;

select id, codigo, nome, descricao, ativo, ordem_exibicao
from public.tipo_recurso
where id::text like '20000000-0000-4000-8000-%'
order by ordem_exibicao;

select id, codigo, nome, descricao, ativo, ordem_exibicao
from public.area
where id::text like '30000000-0000-4000-8000-%'
order by ordem_exibicao;

select id, codigo, nome, url_base, status_integracao
from public.fonte
where id::text like '40000000-0000-4000-8000-%'
order by codigo;
```

Confirmar taxonomias ativas, fontes em `piloto` e `multidisciplinar` com a menor ordem de área.

### Verificação de códigos ausentes

```sql
with esperados(tabela, codigos) as (
  values
    ('tipo_oportunidade', array['chamada_publica','edital','bolsa','premio','concurso','credenciamento','encomenda_tecnologica','outra']),
    ('tipo_recurso', array['financiamento_nao_reembolsavel','financiamento_reembolsavel','bolsa','premio_financeiro','credito','apoio_nao_financeiro','contratacao','misto','nao_identificado']),
    ('area', array['multidisciplinar','ciencias_exatas_e_da_terra','engenharias','ciencias_biologicas','ciencias_da_saude','ciencias_agrarias','ciencias_sociais_aplicadas','ciencias_humanas','linguistica_letras_e_artes','tecnologia_e_inovacao','energia','meio_ambiente','defesa_e_aeroespacial','materiais','computacao_e_dados']),
    ('fonte', array['fapergs','fapesp','cnpq','finep','bndes','grants_gov','nsf','arpa_e','horizon_europe','erc'])
), lista as (
  select tabela, unnest(codigos) as codigo from esperados
), existentes as (
  select 'tipo_oportunidade' as tabela, codigo from public.tipo_oportunidade
  union all select 'tipo_recurso', codigo from public.tipo_recurso
  union all select 'area', codigo from public.area
  union all select 'fonte', codigo from public.fonte
)
select l.tabela, l.codigo
from lista l left join existentes e using (tabela, codigo)
where e.codigo is null
order by l.tabela, l.codigo;
```

Esperado: zero linhas.

## Ausência de fontes japonesas e chinesas

```sql
select id, codigo, nome, status_integracao
from public.fonte
where lower(codigo) in ('jsps','kakenhi','nedo','riken','atla','mofcom','nsfc')
   or lower(nome) ~ '(japan|japão|china|chinese|japanese)';
```

Esperado no staging inicial: zero linhas. A garantia principal da migration é sua allowlist estática de dez fontes.

## Teste futuro de idempotência

Não executado nesta tarefa. Em ambiente descartável e dentro de uma única transação revertida:

1. aplicar o corpo da migration;
2. registrar contagens e conteúdo dos 42 códigos;
3. editar nome/descrição/ordem de um seed e status de uma fonte;
4. reaplicar o corpo;
5. confirmar contagens `8`, `9`, `15`, `10` e preservação da curadoria;
6. fazer rollback.

Como o sistema de migrations não reaplica versões registradas, testar uma cópia do corpo sem manipular o histórico de migrations compartilhado.

## Confirmação de ausência de oportunidades

```sql
select count(*) as oportunidades from public.oportunidade;
```

Em staging previamente vazio, o resultado continua `0`. A inspeção estática deve encontrar `INSERT` somente nas quatro tabelas autorizadas.

## Rollback para staging sem dependências

Rollback é destrutivo e não foi executado. Somente com autorização:

1. confirmar ausência de oportunidades, execuções, itens e associações dependentes;
2. iniciar transação;
3. excluir de `fonte`, `area`, `tipo_recurso` e `tipo_oportunidade` somente os códigos listados acima, nessa ordem;
4. confirmar remoção exata de 42 registros;
5. concluir a transação após revisão.

Não truncar tabelas nem excluir por prefixo UUID. Havendo dependência ou curadoria, criar migration compensatória revisada.

## Riscos

1. `chamada_publica` e `edital` podem se sobrepor; o transformer precisa de critérios explícitos.
2. `bolsa` existe nas duas dimensões e pode ser mapeada para a tabela errada.
3. `outra` exige classificação consciente e não aceita conteúdo inválido.
4. `nao_identificado` existe apenas em tipo de recurso.
5. Áreas amplas podem ser insuficientes futuramente; granularidade prematura também aumenta inconsistência.
6. A primeira posição de `multidisciplinar` pode induzir uso incorreto como default.
7. Áreas temáticas podem coexistir e devem usar a relação N:N com evidência.
8. URLs base podem mudar; a migration não verifica rede.
9. Status `piloto` não afirma readiness do crawler.
10. `DO NOTHING` preserva curadoria, mas diferenças em registros preexistentes exigem revisão read-only.
11. Colisão de UUID com código diferente interrompe a migration deliberadamente.
12. Busca textual por nomes JP/CN é auxiliar; a allowlist é a verificação principal.

