# EditalFinder V2 — M2.3b: resultados

## P. Avaliação final

READY — exclusivamente para o escopo offline documentado da M2.3b.
Implementação, gates locais e revisão adversarial independente por um único
subagente read-only concluídos, sem bloqueador reproduzível. Isso não substitui
revisão técnica humana externa. Testes sintéticos não certificam oportunidades reais,
produção, autenticação, persistência, merge ou promoção.

## Inspeção inicial e baseline

Reverificados os arquivos reais, Git, contratos/normalizadores M1/M2, integração,
orçamento, testes existentes, decisões arquiteturais, revisão M2.3a.2 e resultados
M2.3a.2. O relatório histórico M23A1_RESULTADOS.md continua presente localmente,
respondendo à ressalva de empacotamento da revisão anterior.

Baseline ANTES de qualquer alteração: **1.517 passed in 7.82s**.
Não foi usada apenas a contagem histórica. Nenhuma implementação M2.3b preexistia.
Inventário inicial por SHA-256: 123 arquivos V2, ignorando ambientes/caches.
Exclusão SQL e alterações/untracked anteriores preservados, sem stash/reset/restore.

Ambiente realmente executado: Python **3.11.16**, Pydantic **2.14.1**, pytest **9.1.1**,
na .venv existente. Não há certificação de outras versões/serializadores.

## A–C. Arquitetura, regras e precondições

Novo `domain/integration_consistency.py`: função pura
`evaluate_consistency(candidate_input, normalized_results, validation_result)`.
Retorna tupla ordenada de IntegrationDiagnostic ou OperationalError de preflight.
Aplica prepare_context antes de inputs secundários; compara vinculação completa
entre candidato/claims/contextos e relatórios. Erros com ID estrangeiro não são
atribuídos ao candidato. Normalizadores, M1 e identidade não são reimplementados.

Funções explícitas locais agrupam regras temporais, geográficas, organizacionais,
financeiras e taxonômicas. Não há framework configurável, NLP, relógio, API ou
estado global mutável. A versão de regras é **m2.3b-consistency-v1**.

Precondições, provas exigidas, hipóteses semânticas, resultado, exceções e casos
não resolvidos de CADA regra estão descritos em:
`docs/v2/INTEGRATION_CONSISTENCY_M23B.md`.

Principais decisões conservadoras:

- Faixa financeira reversa: única contradição definitiva implementada, reutilizando
  financial_range_reversed para dois endpoints da MESMA expressão evidenciada,
  sob as declarações de formato/unidade/moeda fornecidas; não autentica essas
  declarações nem a fonte e não compara instrumentos independentes.
- Mínimo > máximo de proposta em moeda/unidade comparáveis: somente conflito
  potencial, pois não há vínculo tipado comum de instrumento/proposta/tranche.
  Usa testemunhas extremas determinísticas, não produtos cartesianos.
- Datas aparentemente conflitantes: potencial quando datas civis/UTC comparáveis;
  insuficiente quando timezone/precisão não permitem comparação. Papel igual não
  prova fase igual; abertura/fechamento não provam janela comum. Nenhuma regra
  temporal afirma contradição definitiva, precedência ou expiração.
- Híbrido grant/crédito: relação não verificada, não contradição. Não há soma,
  câmbio, inferência de principal, equity, taxa, garantia, carência ou valuation.
- Internacional + elegibilidade BR: informação insuficiente sobre exclusividade,
  não conflito. Preserva aviso anterior de geografia sem atribuir a ele autoridade
  para excluir brasileiros ou inferir elegibilidade de sede/origem/moeda.
- Identificadores organizacionais comparáveis divergentes: preserva testemunhas,
  mas não conclui identidade jurídica nem cardinalidade exclusiva. Vários funders,
  várias funções e nomes similares não são contradições.
- Código taxonômico conhecido em news/result não estabelece acionabilidade e não
  supera o M1. Investment/equity não ganham categorias canônicas inventadas.

## D. Diagnósticos

Estados: contradiction, potential_conflict, insufficient_information,
no_conflict_detected. Nenhum estado concede ACCEPTED/REJECTED ou promoção.
No-conflict significa apenas ausência de observação nas regras implementadas,
NÃO consistência global, ausência de alertas de domínio ou oportunidade validada.

Códigos estáveis emitidos:

- consistency_context_mismatch;
- consistency_domain_unavailable;
- consistency_claim_evidence_unavailable;
- consistency_temporal_stage_unverified;
- consistency_temporal_window_unverified;
- consistency_rectification_precedence_unverified;
- consistency_geographic_scope_relationship_unverified;
- consistency_organization_identity_unverified;
- consistency_financial_interpretation_unresolved;
- consistency_financial_range_contradiction;
- consistency_financial_bounds_scope_unverified;
- consistency_financial_bounds_not_comparable;
- consistency_taxonomy_unsupported;
- consistency_taxonomy_not_actionability;
- consistency_hybrid_relationship_unverified;
- consistency_credit_terms_unrepresented;
- consistency_no_conflict_detected.

## E. Evidências e proveniência

Novo DomainClaimReference: domínio/coleção + índice estrito. Referências temporais,
financeiras, geográficas, organizacionais, taxonômicas e assertions M1 não colidem.
Geographic_scope usa singleton explícito, índice 0. claim_indices legado não é usado.

Cada observação registra mensagem, código, versão, estado, domínios afetados,
referências qualificadas, IdentityEvidence e versões/políticas de normalização.
Catálogo solicitado não suportado continua identificado como tal, não aprovado.
Falha operacional não recebe versão normalizada inventada.

Estado/domínios/referências/versões/evidências/version são obrigatórios mesmo quando
vazios. Não há default de versão em diagnóstico recebido. Todos os metadados são
modelos congelados/tuplas, sem dicionário mutável. Evidência estrangeira/rejeitada
não é copiada para o diagnóstico. Material original continua no input integral.

Matches reutiliza PreparedContext.matches/matches_m22b. O engine nunca consulta
resultados de outros candidatos ou usa comparação de identidade como merge.

## F. Integração

Após normalizadores e M1 existentes, evaluate_integration chama evaluate_consistency
para preencher IntegratedCandidate.diagnostics. Preserva inputs, normalizações,
validation, ordenação, snapshots e identidade. OperationalError continua estrutural.

IntegrationReport.verify_outputs continua recomputando TODO o pipeline; sua lógica
de auditoria não foi enfraquecida. Nenhum metadado obrigatório do IntegrationAudit
foi removido ou convertido em default. promotable continua False.

## G. Arquivos criados/modificados

Criados:

- src/editalfinder_v2/domain/integration_consistency.py;
- tests/test_m23b_consistency.py;
- tests/test_m23b_boundaries.py;
- tests/benchmark_m23b_consistency.py;
- docs/v2/INTEGRATION_CONSISTENCY_M23B.md;
- docs/v2/M23B_BENCHMARK.json;
- EDITALFINDER_V2_M23B_RESULTADOS.md.

Modificados:

- src/editalfinder_v2/domain/integration.py — chamada do novo núcleo;
- src/editalfinder_v2/domain/integration_models.py — contrato de observações;
- src/editalfinder_v2/domain/integration_budget.py — SOMENTE docstring explicando
  cobertura pelas reservas existentes; algoritmo, limites e versão inalterados;
- tests/test_m23_core.py — duas adaptações intencionais de contrato abaixo.

Nenhum normalizador, policies.py, Validation Engine ou identity resolution alterado.

## H. RED/GREEN observado

Executado RED antes de cada comportamento implementado. Reproduções direcionadas
no novo test_m23b_consistency.py falharam por ausência do código esperado, depois
passaram para: resumo limitado, recusa de contexto estrangeiro, taxonomia de
investimento não suportada, prova de outro record, híbrido, faixa financeira
reversa, moeda desconhecida, limites min/max, prazos, janela, retificação, crédito,
domínio em falha operacional, acionabilidade, geografia e identidade organizacional.

Adversariais adicionais também tiveram RED/GREEN:

- temporal de outro candidato: zero diagnósticos de prova indisponível onde dois
  eram exigidos; depois dois, índices exatos e evidence vazio;
- OperationalError estrangeiro: era atribuído como domain_unavailable; depois
  context_mismatch sem provas/versões estrangeiras;
- remoção de cada um dos seis metadados recebidos nas três rotas: **18 falhas**
  DID NOT RAISE antes de exigir presença explícita; depois 18 aprovações;
- admissão direta: bloqueio sentinela comprovou construção de TemporalInput antes
  do preflight; depois OperationalError normalization_limits_exceeded antes dela.

Uma tentativa mecânica de refatoração por grupos produziu erro de indentação;
foi revertida imediatamente e os 163 testes então existentes passaram. A divisão
subsequente por funções locais foi aplicada com AST válido e gates verdes.
Não se preservou stub nem se apagou implementação anterior para fabricar RED.

Comandos representativos:

```sh
.venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_m23b_consistency.py::test_explicit_reversed_financial_range_has_a_single_scoped_contradiction --tb=short
.venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_m23b_boundaries.py -k received_consistency_metadata --tb=line
.venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_m23b_consistency.py tests/test_m23b_boundaries.py
```

## I. Regressão e migrações explícitas

**174 testes novos aprovados** (5.29s na última rodada direcionada).
**1.691 testes totais aprovados em 12.61s**.
**1.517 casos anteriores aprovados em 7.96s**, excluindo explicitamente somente:
`tests/test_m23b_consistency.py` e `tests/test_m23b_boundaries.py`.

Não afirmar que todos os 1.517 permaneceram textualmente inalterados. A mudança
intencional de contrato exigiu duas adaptações em test_m23_core.py:

1. Caso que exigia diagnostics=() por regras adiadas agora exige o resumo limitado.
2. Payload falso de diagnóstico agora parte de uma estrutura completa válida,
   alterando código/mensagem/domain; assim os três parâmetros de rota ainda testam
   recomputação e não passam apenas por erro de campos obrigatórios ausentes.

São quatro execuções de casos afetadas (um teste e três rotas parametrizadas),
sem excluir, skipar ou xfailar nenhum.
Os outros testes anteriores, inclusive os 80 de metadados de auditoria, não mudaram.

Gates finais já executados:

```sh
.venv/bin/python -B -m pytest -p no:cacheprovider -q
.venv/bin/python -B -m pytest -p no:cacheprovider -q --ignore=tests/test_m23b_consistency.py --ignore=tests/test_m23b_boundaries.py
.venv/bin/ruff check --no-cache src tests
.venv/bin/ruff format --check --no-cache src tests
.venv/bin/ruff check --no-cache --extend-exclude m23_fixtures.py src tests
.venv/bin/ruff format --check --no-cache --extend-exclude m23_fixtures.py src tests
.venv/bin/mypy --no-incremental --cache-dir=/dev/null src
git diff --check
```

Ruff GLOBAL NÃO está verde: continuam as sete ocorrências preexistentes em
m23_fixtures.py — B023 em 70/73/77 e E501 em 147/166/172/178 — e sua formatação
pendente. Nenhuma correção não autorizada foi feita nesse arquivo.
Excluindo explicitamente somente ele: lint aprovado, 76 arquivos formatados.
Mypy aprovado em 28 arquivos src. git diff --check aprovado; arquivos não rastreados
são verificados adicionalmente por hashes/UTF-8/whitespace/newline/conflitos.

## J. Serialização/auditoria

As 72 combinações de adulteração de diagnósticos cobrem três rotas Pydantic,
com/sem envelope retido: omissão total/parcial, ordem, mensagem/código, estado,
domínio, domínio qualificado, índice, prova, versões e claim_indices legado.
Metadados ausentes têm 18 regressões adicionais. Há round-trip integral, igualdade
byte a byte entre repetições, digest SHA-256 do corpo completo e imutabilidade.

Os testes preservam Decimal sob contexto de precisão 2, timezone desconhecido,
datas civis sem cutoff e independência de dados em snapshots compartilhados.
Não se promete matriz de serializadores não executada.

## K. Orçamento e desempenho controlado

Mantidos **64 MiB**, política **m2.3a.1-output-budget-v1**, máximo 32 candidatos,
64 comparações solicitadas, 4.800 claims combinados e todos os limites anteriores.
A fórmula preexistente já cobra corpo/diagnósticos/auditorias e fan-out de campo;
nenhum coeficiente ou capacidade foi relaxado. A nova política de regras fica
explícita nos diagnósticos; não foi inventada mudança de versão do orçamento.

Não há produto cartesiano entre claims de domínios. Min/max usa índices por moeda/
unidade e testemunhas extremas, com ordem determinística. Observações de relações
não assumem instrumentos/fases/entidades por coincidência de valores.
Não há truncamento de evidências nem de diagnósticos; excesso retorna OperationalError.
O resumo no-conflict não é emitido quando um domínio falhou operacionalmente.

Benchmark em três processos novos SEQUENCIAIS por cenário, sem rede e sem GiB.
Entrada construída antes de iniciar medição; pico tracemalloc cobre integrar,
serializar e reconstruir JSON. Não é medição de teto de RSS nem SLA de produção.
Medianas e amostras completas: `docs/v2/M23B_BENCHMARK.json`.

| Cenário | Resultado | Diagnósticos | Admissão bytes | Saída bytes | Integração s | Dump s | Replay s | Pico tracemalloc bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| grant | IntegrationReport | 1 | 6277808 | 149056 | 0.080136 | 0.003700 | 0.102346 | 2104075 |
| ambiguous | IntegrationReport | 5 | 9057072 | 161311 | 0.083635 | 0.003865 | 0.105588 | 2262905 |
| investment | IntegrationReport | 1 | 4183744 | 107080 | 0.053890 | 0.002061 | 0.070178 | 1530026 |
| diagnostic_24 | IntegrationReport | 24 | 63629232 | 572061 | 0.186793 | 0.010085 | 0.331953 | 8034709 |
| refused_32 | OperationalError | 0 | 67108865 | 163 | 0.051462 | 0.000028 | 0.000031 | 118602 |

Para refused_32, replay é validação do DTO OperationalError, NÃO reconstrução de
um relatório recusado. O ganho desse cenário é recusa antecipada, não compressão.
O caso de 24 diagnósticos foi admitido integralmente; wire_cost e bytes de saída
ficaram abaixo da projeção conservadora. Uma amostra não prova todos os formatos.

## L. Revisão independente

Um único revisor read-only foi despachado para snapshot congelado e separado:
`/home/lorenzozm/.hermes/cache/scratch/m23b-review-snapshot`.
Manifesto FROZEN_HASHES.json contém 97 arquivos. Nenhum subagente implementador foi
usado. O revisor não pode editar, acessar rede/banco/Legacy, stagear ou commitar.
Revisão concluída: **READY apenas para o escopo offline documentado**, sem
bloqueador reproduzível. O revisor registrou 1.691 passed in 12.80s e probes
adicionais de faixas reversas, falso positivo temporal, prova financeira de outro
record, referências qualificadas, forja por três rotas/instância adulterada,
investimento não mapeado, identidade sem merge, orçamento e preflight antecipado.
Não houve proposta de correção nem alteração da implementação após a revisão.

O manifesto foi recalculado pelo revisor antes/depois, com 97 arquivos e nenhum
mismatch. SHA-256 de FROZEN_HASHES.json:
`e3b643cc58bea10fff5c3ee462a1a46e2f1a6296cdf2a43915ca5d0c4336622f`.
O agente principal também verifica os hashes do snapshot e sua correspondência
com os arquivos atuais antes de encerrar. Os números do benchmark deste relatório
continuam sendo as medições locais acima, não os de fixtures alternativas do revisor.

Limites expressos pelo revisor: probes não exaustivos; nenhuma certificação de
dados reais, autenticação, vínculos de fase/instrumento/entidade ou prontidão de
produção. DTOs isolados e rotas Pydantic sem validação não autenticam resultados;
orçamento conservador não é teto de RSS nem limite de transporte.

Transcrito read-only da revisão:
`/home/lorenzozm/.hermes/cache/delegation/live/deleg_914c0926/task-0.log`.
Esta é revisão independente adicional por IA, não parecer humano externo nem
aprovação para publicação/persistência. Aguarda-se a revisão técnica do usuário.

## M–O. Limitações, investimentos e confiança

- Não há identidade de fase/janela/instrumento/proposta/tranche/entidade jurídica
  nos contratos atuais. Relações não suportadas não se tornam contradições certas.
- Não há validação semântica de texto livre ou documentos reais, extração de PDF,
  precedência entre documentos ou curadoria de fontes.
- Credit principal não existe em FinancialRole; expressões de origem ficam
  preservadas, sem interpretação como grant, orçamento, contrapartida ou equity.
- Seeds não representam venture capital/equity adequadamente. Não foram criadas
  categorias, aliases ou fallbacks; investimento não vira empréstimo. Custo estimado
  pode permanecer normalizado em seu papel sem inferir valuation/ownership.
- Não é verificador jurídico de organização, certificador de fonte, identidade
  do revisor, autorização ou assinatura. Checksum CNPJ não prova existência.
- DomainNormalizationResults e diagnósticos isolados não são capabilities de
  persistência. A fronteira avaliada é IntegrationReport com recomputação completa.
- JSON já foi decodificado antes de validators Pydantic: limites de transporte
  continuam necessários. 64 MiB é orçamento conservador, não teto de RSS.
- Relatórios antigos com diagnostics vazio exigem nova avaliação explícita do input
  para as regras M2.3b; não são atualizados como se fossem o mesmo registro original.
- O conjunto de regras deliberadamente não cobre toda oportunidade. Falsos positivos
  e recall em dados reais não foram medidos; testes verdes não provam correção geral.

Legacy, SQL/migrations e Supabase não foram tocados. Exclusão SQL anterior preservada.
Sem crawler, persistência, extração real, APIs, fuzzy merge, promoção, stage ou commit.
M2.3c e M3 não foram iniciados. O próximo gate é revisão técnica humana independente.
