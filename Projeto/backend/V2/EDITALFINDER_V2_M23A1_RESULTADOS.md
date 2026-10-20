# EditalFinder V2 — M2.3a.1: Output & Memory Budget Hardening

## Conclusão

Correção operacional implementada e exercitada offline. Excedentes agora retornam
`OperationalError(code="integration_output_budget_exceeded", stage="integration")`
antes de construir os relatórios de normalização, validação ou identidade.
Nenhuma evidência é truncada; nenhum excedente é convertido em REJECTED.

A política é deliberadamente conservadora e pode recusar relatórios cujo JSON
real seria menor que 64 MiB. É um orçamento de admissão em unidades equivalentes
de bytes/custo, NÃO uma garantia de RSS máximo de 64 MiB. Limites de transporte,
processo e decodificação de entradas permanecem necessários. Não é certificação de
produção nem revisão independente da correção.

## Estado inicial e reprodução

O relatório `EDITALFINDER_V2_M23A_REVISAO_CHATGPT.md` foi lido integralmente.
A árvore inicial tinha 1.402 testes aprovados. Foram preservadas as modificações
preexistentes, inclusive README, arquivos não rastreados e a exclusão SQL externa
a V2. Nenhum reset, staging, commit, acesso a Supabase, Legacy, migrations ou rede.
Execução sequencial no agente principal, sem subagentes.

Antes da edição, foi congelada uma cópia de `src` no scratch para comparação
real entre implementações. A reprodução com `adapt_records([grant] * 32)` confirmou:

- um único snapshot compartilhado: 34.381 bytes;
- 256 ocorrências de `payload_json` no relatório;
- 14.355.403 bytes de JSON final.

Cada candidato repete o snapshot oito vezes: entrada do batch, entrada do candidato,
cinco entradas de normalização e M1. Cada comparação explícita acrescenta os snapshots
dos seus dois sujeitos. Compartilhamento de objetos Python não deduplica JSON.
A construção e a reconstrução também auditam e reavaliam relatórios aninhados.
Contar somente snapshots únicos não limita esse trabalho.

## Solução adotada

Foi mantida a estrutura completa dos DTOs. Um registro de snapshots por UUID,
embora preferível em uma evolução arquitetural, exigiria alterar contratos anteriores.
Não foi implementado nesta correção.

`integration_budget.py` introduz a política `m2.3a.1-output-budget-v1`:

- orçamento de admissão: 64 MiB;
- snapshots cobrados oito vezes por candidato, mais uma vez por lado de cada par;
- corpo sem snapshots cobrado 16 vezes, mais 16 vezes a maior quantidade de
  afirmações do mesmo campo, cobrindo a amplificação de evidências em diagnósticos M1;
- reserva de 64 KiB por resultado e para o envelope;
- strings cobradas por comprimento e pior escape UTF-8 padrão; UUID, datas,
  Decimal e envelope escalar M1 têm reservas compatíveis com sua forma JSON;
- contagem saturante: ao exceder, retorna apenas o sentinela teto+1;
- no máximo 100.000 visitas por travessia e profundidade 64;
- memoização evita reprocessamento, mas cada ocorrência continua sendo cobrada;
- ciclos, tipos desconhecidos e travessias excessivas falham de forma conservadora;
- não usa `model_dump`, `model_dump_json`, `json.dumps` ou buffers UTF-8 grandes
  para calcular a admissão.

A contagem de claims foi extraída para uma função compartilhada, sem alterar seu
significado. Para candidatos que necessariamente excedem o limite de claims de
`prepare_context`, é cobrada a entrada original e a falha operacional, não relatórios
que não serão produzidos; o teto é importado do componente existente.
Os limites anteriores e sua precedência continuam ativos. Não foram duplicadas
regras semânticas ou validações de normalização.

`integrate` verifica o orçamento antes dos componentes de domínio. Em excesso,
a entrada original permanece inalterada com o chamador; não há relatório parcial
nem redução do conteúdo para fazê-lo caber. OperationalError mantém seu contrato
anterior e não passa a carregar cópias das evidências. A retenção durável da entrada
continua sendo responsabilidade futura da camada de ingestão/persistência.

`IntegrationReport` verifica projeção e custo estrutural do envelope em um validador
`before`, impedindo a construção/auditoria dos DTOs aninhados excessivos. Construção
ou desserialização direta de um DTO excessivo gera ValidationError com o código
operacional na mensagem: construtores Pydantic não retornam a união OperationalError.
A API de orquestração continua retornando OperationalError. Nenhuma dessas rotas
produz rejeição semântica.

`hide_input_in_errors=True` evita materializar representações grandes ao formatar
o erro. Consumidores devem usar `errors(include_input=False)` em logs; isso não
altera as evidências da entrada.

## Evidências, auditoria e compatibilidade

M1, identidade M2.1 e normalizadores M2.2 não foram modificados. Papéis, alternativas,
proveniência e isolamento permanecem nos DTOs originais. Hashes e verificação por
recomputação não foram removidos ou enfraquecidos. Auditorias aninhadas permanecem
completas. A auditoria externa acrescenta somente `output_budget_version`, mantendo
a política anterior de limites, o algoritmo e o hash do corpo completo sem `audit`.

Os cinco cenários grant/credit/investment/mixed/ambiguous foram comparados com a
cópia congelada: igualdade integral de todos os campos e digests, excluindo apenas
o novo campo de política no envelope externo. O novo JSON aumenta 51 bytes nesses
cenários. Relatórios antigos abaixo do orçamento podem ser revalidados sob a nova
política; relatórios antigos excessivos são recusados. Não há migração silenciosa
de evidências nem declaração de que a política nova existia na execução histórica.

## Benchmark controlado antes/depois

Ambiente: Linux x86_64, Python 3.11.16, Pydantic 2.14.1. Mediana de três execuções
por cenário, cada uma em processo novo e sequencial, com tracemalloc ativo.
O benchmark não faz parte da coleta automática de pytest. Casos permitidos são
limitados a 1/4/16/32 candidatos e padding de 0/1.024 caracteres por registro.
Nenhuma carga de gigabytes foi construída.

Construção de fixtures e da entrada excluída dos picos tracemalloc. Picos de cada
etapa incluem objetos ainda vivos de etapas anteriores. RSS nos dados brutos é
pico de vida do processo Linux em KiB; tracemalloc não cobre todas as alocações
nativas. Tempos instrumentados não são SLA e não foram comparados ao hardware da
revisão independente.

### Integração

Bytes de snapshot, JSON e picos Python são valores absolutos. Padding é por registro.

| Candidatos | Padding | Snapshot | JSON antes | JSON depois | integrate antes s | depois s | Pico antes B | depois B | Resultado depois |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0 | 1087 | 147692 | 147743 | 0.0527 | 0.0799 | 719168 | 730348 | IntegrationReport |
| 4 | 0 | 4309 | 705887 | 705938 | 0.2118 | 0.3125 | 2801211 | 2811025 | IntegrationReport |
| 16 | 0 | 17197 | 4689467 | 163 | 1.8641 | 0.0434 | 16335478 | 139130 | OperationalError |
| 32 | 0 | 34381 | 14355403 | 163 | 6.7054 | 0.0394 | 47390688 | 126842 | OperationalError |
| 32 | 1024 | 68141 | 23047115 | 163 | 7.7336 | 0.0353 | 73465689 | 114426 | OperationalError |

Para 32 grants, o pico adicional rastreado da integração caiu 99,73% porque o batch
é recusado, não porque o mesmo relatório foi comprimido. Nos casos admitidos,
a multiplicidade permanece e o orçamento acrescenta custo de CPU. O caso com
32 candidatos vazios e snapshot pequeno continua admitido: não é um limite
artificialmente reduzido de quantidade de candidatos.

### Serialização e reconstrução do resultado emitido

Nas linhas recusadas, o objeto de 163 bytes é OperationalError. Seus tempos não
representam reconstrução do antigo IntegrationReport; a comparação desse mesmo
relatório histórico está separada abaixo.

| Candidatos | Padding | dump antes s | depois s | restore antes s | depois s | Pico restore antes B | depois B |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0.0030 | 0.0030 | 0.0406 | 0.103954 | 2003772 | 2102308 |
| 4 | 0 | 0.0121 | 0.0120 | 0.1903 | 0.441880 | 8116598 | 8181877 |
| 16 | 0 | 0.0599 | 0.0000 | 1.4639 | 0.000036 | 44541027 | 135162 |
| 32 | 0 | 0.1141 | 0.0000 | 4.8287 | 0.000038 | 122513636 | 122641 |
| 32 | 1024 | 0.1301 | 0.0000 | 5.5076 | 0.000035 | 183256301 | 110346 |

### Reconstrução do MESMO JSON histórico de 32 candidatos

Replay isolado do mesmo arquivo de 14355403 bytes, sem relatório anterior
vivo, três processos por implementação:

- antes: aceito, 4.9298 s; pico tracemalloc 106131729 bytes;
- depois: recusado antes dos DTOs aninhados, 0.4863 s;
  pico tracemalloc 77739717 bytes.

A decodificação do JSON acontece ANTES do validador `before`; esse custo permanece
e explica o pico relevante no replay. Não se afirma que a validação de um JSON já
excessivo tenha memória desprezível. O transporte deve limitar bytes antes de
`model_validate_json`. Formatar entradas completas de ValidationError também pode
amplificar memória; o benchmark final usa erros sem entradas.

Dados brutos, amostras e medianas: `docs/v2/M23A1_BENCHMARK.json`.

## Regressões e qualidade

35 casos novos em `tests/test_m23_output_budget.py`:

- cenário compartilhado recusado antes de normalizar e sem mutar a entrada;
- limites imediatamente abaixo/no teto/acima com orçamentos reduzidos;
- snapshots compartilhados por referência ou por objetos iguais;
- amplificação só de snapshot, fan-out de afirmações e pares explícitos;
- preservação dos cinco cenários e round-trip;
- bloqueio antecipado por constructor, model_validate e model_validate_json;
- envelope bruto excessivo mesmo quando declara uma entrada pequena;
- ausência de serialização no estimador;
- ciclos, profundidade, visitas e tipos desconhecidos;
- Unicode, escapes, UUID, datetime, Decimal e envelope escalar;
- estabilidade de custo Python→JSON e prevenção de reutilização de IDs temporários;
- auditoria versionada e erro sem representação da entrada.

Foram observados RED antes das correções do cenário principal, admissão antecipada
do DTO, versão da auditoria, formatação de erros e discrepâncias de custo de
transporte/memoização. GREEN reexecutado com as regressões existentes.

Resultados finais executados:

- pytest novo: 35 passed in 0.82s;
- regressão existente, excluindo somente test_m23_output_budget.py: 1.402 passed in 6.48s;
- pytest completo: 1.437 passed in 7.35s;
- mypy strict src: sem erros em 27 arquivos;
- Ruff check e format dos cinco arquivos Python desta correção: aprovados;
- Ruff src/tests sem excluir nada: NÃO totalmente verde por pendências anteriores
  em tests/m23_fixtures.py: B023 nas linhas 70/73/77 e E501 em 147/166/172/178;
  o mesmo arquivo também precisa de formatação. Seu hash inicial foi preservado;
- Ruff src/tests excluindo explicitamente apenas m23_fixtures.py: lint aprovado e
  71 arquivos formatados. Não foi mascarada a falha global ou alterada a fixture;
- git diff --check aprovado; nada staged ou commitado. Inventário por hashes e
  inspeção UTF-8/whitespace/newline/conflitos complementam Git para não rastreados.

Comandos de reprodução no diretório backend/V2:

```sh
.venv/bin/python -B -m pytest -p no:cacheprovider -q
.venv/bin/ruff check --no-cache src tests
.venv/bin/ruff format --check --no-cache src tests
.venv/bin/mypy --no-incremental --cache-dir=/dev/null src
git diff --check
PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_integration_budget.py --output /caminho/after.json
```

Para comparar antes/depois, executar o mesmo benchmark com PYTHONPATH apontando
primeiro para a cópia congelada de src. `--save-replay /caminho/legacy32.json`
guarda o cenário original de 32 candidatos; `--replay /caminho/legacy32.json`
mede sua reconstrução isolada. Os arquivos temporários usados nesta execução
ficam no scratch e não são artefatos duráveis; todas as medidas estão no JSON
versionável acima.

## Arquivos e limites restantes

Modificados somente integration.py e integration_models.py no domínio existente.
Criados integration_budget.py, test_m23_output_budget.py,
benchmark_integration_budget.py, este relatório e M23A1_BENCHMARK.json.
Os testes/fixtures de M2.3a e demais milestones foram preservados.

Ainda não há registro compartilhado de snapshots na saída, streaming de JSON,
limite de RSS de processo, política de transporte ou retenção durável da entrada.
O estimador deve ser revisto se DTOs/diagnósticos mudarem: suas margens não são uma
prova matemática para implementações futuras ou serializadores arbitrários.
A reavaliação completa dos relatórios admitidos continua, com custo adicional
medido acima. Limites conservadores podem exigir divisão explícita de batches,
nunca truncamento implícito.

Não foram implementados M2.3b, crawlers, promoção, merge, autenticação ou persistência.
Nenhuma autorização é concedida por auditorias ou pelo novo orçamento.

M2.3a.1 concluída; parada para revisão humana.
