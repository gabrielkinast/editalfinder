# EditalFinder V2 — Resultados M2.2a.1

## Estado desta versão do relatório

**READY para o escopo offline da M2.2a.1.** Ambos os defeitos foram reproduzidos, corrigidos com regressões RED→GREEN e verificados. Gates locais e revisão adversarial independente concluídos, sem achados bloqueantes. Aguarda revisão técnica do usuário. Não autoriza produção, persistência, promoção ou M2.2b; esta última não foi iniciada.

## A. Baseline, escopo e causas

O relatório `EDITALFINDER_V2_M22A_REVISAO_INDEPENDENTE.md` foi lido integralmente antes de qualquer modificação. Foram examinados os cinco módulos solicitados, fixtures, testes temporais/geográficos e contratos de normalização, decisões aprovadas e validação da migration, exclusivamente como texto. Nenhuma migration foi executada.

Estado inicial: README já modificado, exclusão SQL preexistente `BANCO DE DADOS/bancode Dados.sql` e vários arquivos M2.1/M2.2a não rastreados. Já existia `tests/test_m22a1_temporal_contract.py` com 12 casos RED para offset conhecido sem UTC. O arquivo foi preservado e ampliado; não é apresentado como criação desta execução.

Primeira execução integral, antes das mudanças: **12 failed, 958 passed in 3.07s**. As 12 falhas eram exatamente os testes preexistentes M2.2a.1, todos por ausência de ValidationError. Excluindo somente esse arquivo, a baseline foi independentemente confirmada: **958 passed in 3.02s**. O número histórico não foi presumido.

1. Temporal: `NormalizedTemporalEvent.consistent_shape()` verificava UTC apenas dentro de `if self.instant_utc is not None`. Portanto um local aware com offset explícito conhecido podia omitir o instante sem diagnóstico, inclusive em um novo relatório auditado. O normalizador já fazia a conversão correta. A mesma lacuna permitia overflow sem diagnóstico no DTO público.
2. Geografia: o laço preservava todos os claims e diagnosticava componentes inválidos, mas não tinha regra para a ausência dos quatro componentes. Um claim somente com papel produzia um local inteiramente vazio, aparentemente sem problema próprio; `geo_scope_missing` não descrevia esse estado.

## B. Reprodução antes/depois

Reprodutor mínimo executado antes das correções:

    PYTHONPATH=src:tests .venv/bin/python -B /home/lorenzozm/.hermes/cache/scratch/m22a1_reproduce.py

Entrada temporal: claim `submission_deadline`, local `2026-05-10T12:30:00+03:00`, timezone `+03:00`, precisão `minute`, calendário `gregorian`, sem UTC.

Antes: `Temporal accepted: None ()`.
Depois: `Temporal rejected: Value error, UTC instant is required for a known representable offset`.
A representação válida exige UTC `2026-05-10T09:30:00+00:00`; o DTO não o inventa. Foram exercitados construtor, `model_validate` e `model_validate_json`.

Entrada geográfica: `GeographyLocationClaim(role="elegibilidade")`, sem componentes nem escopo.

Antes: local preservado com quatro componentes nulos e `diagnostics=[]`; diagnóstico do relatório somente `('geo_scope_missing', None)`.
Depois: mesmo claim/papel/nulos preservados; diagnóstico local `geo_location_empty`, `claim_index=0`, `evidence=[]`; relatório contém `[('geo_scope_missing', None), ('geo_location_empty', 0)]`.

O reprodutor é um artefato auxiliar de scratch, não uma dependência do produto. As reproduções duráveis estão nos testes.

## C. Correção e arquivos

Arquivos preexistentes alterados nesta execução:

- `src/editalfinder_v2/domain/temporal_models.py`: conversão determinística para verificar a representação; exige UTC correspondente e offset zero, não preenche campos. Overflow exige diagnóstico exato no evento e ausência de UTC; diagnóstico de overflow falso é rejeitado, inclusive em datas civis, timezone ausente/desconhecido e valores ausentes. Validações de precisão foram movidas antes da verificação UTC para preservar as regressões anteriores, sem enfraquecê-las.
- `src/editalfinder_v2/domain/geography_normalization.py`: se `component_values` estiver vazio, acrescenta diagnóstico estruturado ao local; o mecanismo existente o agrega ao relatório e ao envelope.
- `tests/test_m22a1_temporal_contract.py`: ampliado sem remover os 12 casos preexistentes.
- `docs/v2/SEMANTIC_NORMALIZATION_M22A.md`: adendo dirigido M2.2a.1, incluindo rejeições deliberadas e impacto em digests.

Arquivos criados:

- `tests/test_m22a1_geography_contract.py`.
- `EDITALFINDER_V2_M22A1_RESULTADOS.md` (este relatório).

Não houve alteração em `temporal_normalization.py`, `geography_models.py`, `semantic_common.py`, contratos/resolvedor M2.1 ou qualquer teste anterior fora do arquivo parcial M2.2a.1. Não houve mudança de dependências ou identificadores das políticas; trata-se de correção conservadora, não nova política de inferência.

## D. TDD e cobertura

Ciclos executados, antes do código correspondente:

- Temporal: **26 failed, 27 passed in 0.19s**; falhas específicas por UTC omitido, overflow sem diagnóstico e diagnóstico de overflow falso. Após correção: **53 passed in 0.12s** e suíte integral **1011 passed in 3.05s**.
- Geografia: **36 failed, 9 passed in 0.30s**, com comparação exata dos diagnósticos/índices ausentes; após correção **45 passed in 0.14s** e suíte integral **1056 passed in 3.25s**.
- Adversarial temporal adicional: diagnóstico de overflow em representação sem conversão conhecida produziu **12 failed, 53 deselected in 0.10s**, antes de acrescentar a rejeição específica. Os casos posteriormente passaram.

A suíte dirigida final contém **117 casos**. Desses, 12 já existiam como regressões parciais no início. Nenhuma expectativa de teste anterior foi modificada para acomodar a correção; nenhum skip/xfail foi introduzido.

Temporal: offsets positivo/negativo/zero e Z; UTC ausente, divergente ou não zero; matching UTC; naive sem zona e `-00:00`; data civil; ambos os limites de ano; diagnóstico correto/incorreto; três entradas Pydantic; round-trip de DTO/relatório; omissão de UTC rejeitada dentro de relatório; determinismo e envelope retido com mutação de papel.

Testes adversariais duráveis percorrem **11.516 combinações**: todos os offsets de minuto de -23:59 a +23:59 em quatro horários nos extremos dos anos 1/9999. A expectativa usa subtração do offset no horário naive, separadamente da conversão `astimezone` usada na implementação. Verificam representabilidade, rejeição da omissão de UTC, preservação local/zona, diagnóstico e JSON round-trip.

Geografia: seis papéis, escopo ausente e quatro escopos válidos; país isolado; BR+UF, BR+região, país estrangeiro+município não certificado; UF isolada sem BR inventado; componentes fornecidos porém não resolvidos sem falso `geo_location_empty`; valores/provas originais; um local vazio em cada posição entre locais válidos; vários vazios com índices distintos; round-trip e mutações de diagnóstico/papel/índice com envelope retido.

## E. Ambiente e resultados exatos

Diretório de execução: `/home/lorenzozm/PROJETOS/editalfinder/Projeto/backend/V2/`.
Ambiente efetivamente executado da `.venv`: **Python 3.11.16**, **Pydantic 2.14.1**, **Ruff 0.17.1**, **mypy 2.4.0**. Nenhuma instalação. Nenhuma alegação de compatibilidade executada com outras versões.

- `.venv/bin/python -B -m pytest -p no:cacheprovider -q`
  Resultado final local após retorno independente e nova execução de todos os gates: **1075 passed in 3.77s** (execução anterior: **1075 passed in 3.80s**).
- `.venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_m22a1_temporal_contract.py tests/test_m22a1_geography_contract.py`
  **117 passed in 0.79s**.
- `.venv/bin/python -B -m pytest -p no:cacheprovider -q --ignore=tests/test_m22a1_temporal_contract.py --ignore=tests/test_m22a1_geography_contract.py`
  Baseline original novamente confirmada após correções: **958 passed in 3.17s**.
- `.venv/bin/ruff check --no-cache src tests`
  **All checks passed!**
- `.venv/bin/ruff format --check --no-cache src tests`
  **42 files already formatted**.
- `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src`
  **Success: no issues found in 16 source files**.
- `git diff --check`
  Exit **0**, sem saída. Não cobre arquivos não rastreados.

Primeiro lint identificou importação desordenada e UTC inicialmente sem uso no arquivo parcial temporal; primeira checagem de formato identificou os dois arquivos de regressão. Foram organizados/formatados somente esses arquivos, e todos os gates acima foram reexecutados. Não foi alterado o restante do projeto para satisfazer ferramentas.

Varredura complementar dos cinco arquivos de código/teste/contrato tocados: UTF-8 válido, LF/final newline, nenhum NUL, whitespace final ou marcador de conflito. Comparação SHA-256 com snapshot prévio de **5.606 arquivos preexistentes** (excluindo caches/ambientes/dependências): somente os quatro arquivos preexistentes declarados nesta seção mudaram. Varredura dos dois módulos de produção modificados não encontrou padrões de chamadas perigosas/I-O. A exclusão SQL e README continuam no estado preexistente; índice Git permanece sem staging.

## F. Serialização, auditoria e compatibilidade

Os testes recalculam SHA-256 dos bytes UTF-8 de `model_dump_json(exclude={"audit"})` e comparam com o digest. DTOs e relatórios corretos sobrevivem a validação Python e JSON; alteração de papel temporal, diagnóstico geográfico, índice ou papel geográfico com envelope anterior gera `ValidationError` especificamente por divergência de auditoria, não apenas por forma inválida.

O diagnóstico de local vazio preserva input completo e papel através do claim original, com índice da posição no input, sem preencher país, UF, região, município ou confiança. Não existe prova de componente em claim sem componentes: `evidence=()` é intencional, não se toma prova de escopo ou da organização. Escopo sem locais usa `geo_locations_missing`; escopo presente não torna um claim vazio substantivo. Componente fornecido e inválido continua usando seus diagnósticos próprios, não é redefinido como ausente.

M1/M1.1/M1.1a: limites operacionais, imutabilidade, validação/evidências e erros estruturados permanecem; suíte original aprovada. M2.1: nenhum contrato, normalizador ou resolvedor de identidade alterado. M2.2a: papéis, proveniência, precisão, catálogos, ausência explícita e determinismo preservados. `promotable=False` permanece sem caminho de aprovação automática.

O contrato de saída temporal é deliberadamente mais estrito: DTO antigo inconsistente é rejeitado, não reparado. Relatório geográfico reprocessado com local vazio passa a ter diagnóstico/digest novos. O validador de envelopes não migra nem reescreve relatórios históricos silenciosamente. Versões conservadoras existentes foram mantidas e o impacto foi documentado no adendo.

## G. Segurança, limitações e exclusões

Todo trabalho de domínio e verificação foi offline. Sem Legacy, banco/migrations, Supabase, crawlers, persistência, promoção, staging ou commit. A exclusão SQL preexistente não foi restaurada nem ampliada. Não foi iniciada M2.2b.

Limitações preservadas: `model_construct`/`model_copy(update=...)` ignoram validadores por projeto do Pydantic e não substituem validação de fronteira; digest não é assinatura/autorização; não há migração de arquivos auditados históricos nem prova de autenticidade da fonte; não há catálogo municipal, inferência de IANA/DST ou status temporal; somente o ambiente local acima foi executado. Geografia vazia é diagnóstico do normalizador, não redesign global dos DTOs geográficos. A lista de códigos diagnósticos não autentica a fonte; o validador temporal verifica a condição de overflow, não autoria de diagnóstico.

## H. Revisão independente e decisão

Revisão concluída por subagente em contexto isolado (`deleg_361dd00b`, modelo reportado pelo runtime: gpt-6-astra), somente leitura. Parecer: **READY para o escopo offline, sem achados bloqueantes ou regressões**. Trata-se de contexto independente dentro desta ferramenta, não auditoria humana nem certificação de matriz de ambientes.

Resultados efetivamente reportados pelo revisor, com `PYTHONDONTWRITEBYTECODE=1`:

- `.venv/bin/python -B -m pytest -q -p no:cacheprovider`: **1075 passed in 3.69s**.
- Mesmo comando excluindo os dois arquivos M2.2a.1: **958 passed in 3.77s**.
- `.venv/bin/python -B -m ruff check --no-cache src tests`: aprovado.
- `.venv/bin/python -B -m mypy --cache-dir=/home/lorenzozm/.hermes/cache/scratch/m22a1-independent-mypy src`: nenhum problema em 16 arquivos. Este comando do revisor não substitui o gate local obrigatório `--no-incremental --cache-dir=/dev/null`, também aprovado.
- Ambiente do revisor: Python **3.11.16**, Pydantic **2.14.1**, pytest **9.1.1**; mesmo ambiente local, sem certificação multiversão.

O revisor exerceu construtor, validação Python/JSON, UTC e offsets desconhecidos, overflow nos limites de ano, necessidade de diagnóstico no próprio evento (diagnóstico apenas no relatório não basta), geografia vazia/escopo separado, serialização/auditoria e não promoção. Probes próprios percorreram todos os offsets de minuto em quatro horários extremos com precisão fracionária, nas três rotas: **8.634 casos de overflow**, **25.914 representáveis**, mais controles de timezone, relatórios e geografia. Saída: **34.599 aceitações esperadas**, **69.135 rejeições esperadas**, **15 relatórios geográficos**.

O agente principal leu o script independente e reexecutou:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests .venv/bin/python -B /home/lorenzozm/.hermes/cache/scratch/m22a1_independent_probe.py

Resultado confirmado: `{"accepted_expected": 34599, "geography_reports": 15, "overflow_cases": 8634, "rejected_expected": 69135, "representable_cases": 25914}` e `PASS independent probes; no network or database operations`. Em seguida, reexecutou os cinco gates obrigatórios com sucesso, incluindo a suíte integral de **1075 passed in 3.77s**.

Artefatos de revisão ficam em scratch, não são dependências do projeto. O revisor não modificou arquivos do projeto; comparação com a baseline confirma somente as alterações declaradas. Nenhuma limitação de rate limit/provider impediu esta revisão.

Decisão final: **READY — M2.2a.1, exclusivamente no domínio offline solicitado**. Ambos os defeitos corrigidos; baseline preservada; serialização, auditoria, Ruff, formato, mypy e checks de integridade aprovados. Nenhum requisito de aceitação conhecido pendente. Aguardar revisão técnica do usuário; parar nesta milestone, sem M2.2b.
