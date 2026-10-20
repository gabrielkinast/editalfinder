# EditalFinder V2 — M2.3d.1: UTC Boundary & Nested Audit Metadata Hardening

## A. Causa-raiz e escopo

Correção exclusivamente dos bloqueadores M23D-F01 e M23D-F03. Revisados integralmente os relatórios M23D_RESULTADOS, M23D_REVISAO_CHATGPT e o JSON M23D_AUDIT_EVIDENCE; inspecionados os contratos, binders, integração, documentação e testes antes das alterações. Baseline atual executada antes de editar: 1.810 testes aprovados. Não se tratou essa contagem histórica como prova suficiente.

F01: `RawSnapshot.utc_timestamp` e `ReviewAttestation.utc_review` chamavam `astimezone(UTC)` sem tratar overflow representacional. Mesmo uma string ISO válida e aware pode exigir ano UTC fora de 1–9999. `OverflowError` não é convertido automaticamente por Pydantic em ValidationError. Agora somente essa exceção esperada é capturada e encadeada em `ValueError("UTC timestamp is outside the representable datetime range")`. O erro estruturado conserva a localização do campo. Não há clamp, fallback, timestamp inventado, captura genérica ou alteração da normalização temporal M2.2a.1. `AwareDatetime` permanece.

F03: defaults em cinco DTOs de auditoria, incluindo `schema_version` herdado de Contract, completavam envelopes recebidos antes do binder verificar igualdade/digest. A representação reconstruída voltava a coincidir com o original, escondendo a omissão. TODOS os campos desses DTOs passaram a ser obrigatórios; os binders locais fornecem explicitamente as mesmas constantes anteriores. `IntegrationAudit` já era estrito e foi incluído na matriz de testes sem mudança de sua política.

A inspeção também verificou que policy_version/normalization_version e outras versões estão no CORPO de vários relatórios, não no próprio audit DTO. Uma regressão adicional demonstrou que omiti-las com audit retido tinha o mesmo efeito. Um before-validator em Contract, restrito a tipos com campo audit e envelope não nulo, exige suas propriedades existentes terminadas em `_version` explicitamente. Não foram inventados campos de política em envelopes que não os têm. Essa extensão é parte do F03 solicitado (versões de políticas), não redesenho da integração.

Inventário completo, conferido contra os campos reais e `is_required()`; 43 campos no conjunto dos seis tipos:

- `SnapshotAudit`: `schema_version`, `snapshot_id`, `payload_digest`, `algorithm`, `hash_version`, `representation`, `contract_version`.
- `ValidationAudit`: `schema_version`, `audit_version`, `validation_limits_version`, `report_digest`, `report_hash_version`, `contract_version`, `candidate_id`, `candidate_digest`, `evidence_digests`, `snapshots`, `catalog_version`, `ruleset_version`, `rule_versions`, `algorithm`, `hash_version`.
- `IdentityAudit`: `schema_version`, `report_digest`, `algorithm`, `hash_version`, `limits_version`.
- `NormalizationAudit`: `schema_version`, `report_digest`, `algorithm`, `hash_version`, `limits_version`.
- `M22BAudit`: `schema_version`, `report_digest`, `algorithm`, `hash_version`, `limits_version`.
- `IntegrationAudit`: `schema_version`, `output_budget_version`, `report_digest`, `algorithm`, `hash_version`, `limits_version`.

As referências a snapshots dentro de ValidationAudit também são SnapshotAudit e recebem a mesma exigência. Temporal/geografia compartilham NormalizationAudit; financeiro/organizações/taxonomia compartilham M22BAudit. Não se assumiu que todos os envelopes têm os mesmos campos.

## B. Arquivos alterados

Fontes preexistentes, exclusivamente:
- `src/editalfinder_v2/domain/models.py`: dois validators UTC; SnapshotAudit, ValidationAudit e binders; guarda de versões de corpos com audit recebido.
- `src/editalfinder_v2/domain/identity_models.py`: IdentityAudit e binder.
- `src/editalfinder_v2/domain/semantic_common.py`: NormalizationAudit e binder M2.2a.
- `src/editalfinder_v2/domain/m22b_common.py`: M22BAudit e binder M2.2b.

Documentação relacionada preexistente: `docs/v2/INTEGRATION_AUDIT_REPROCESSING.md`, apenas seção adicional explicitando presença de metadados e separação entre verificação histórica e nova avaliação.

Novos: `tests/test_m23d1_utc_boundaries.py`, `tests/test_m23d1_audit_metadata.py`, este relatório e `docs/v2/M23D1_HARDENING_EVIDENCE.json`.

O manifesto inicial inclui arquivos tracked e untracked, e a comparação SHA-256 confirmou que nenhum outro arquivo preexistente do projeto mudou. Nenhum teste/fixture anterior foi modificado ou enfraquecido. README e documentos anteriores, incluindo as revisões, foram preservados. Exclusão SQL preexistente preservada; índice Git sem staging. Legacy, migrações, dependências e configuração não foram alterados.

## C. Reproduções antes/depois e TDD

F01: limites `0001-01-01T00:00:00+23:59` e `9999-12-31T23:59:59-23:59` causavam OverflowError por construtor, model_validate e model_validate_json. Em integração, snapshot aninhado também escapava. Primeiro criados e executados testes sem alterar a implementação: 20 falharam com overflow e 42 controles passaram. Após a correção, 62 passaram. Agora há ValidationError estável, tipo `value_error`, mensagem explícita e localização correta; a repetição do mesmo input produz a mesma projeção de erros. Entradas naive continuam inválidas. Conversões representáveis e datas adjacentes mantêm o instante UTC correto.

F03: primeiro criados e executados testes de omissão de cada campo em envelopes e caminhos aninhados, incluindo o caso exato `identity_results[0].audit.hash_version` de M23C-I-005 com audit externo retido. RED: 50 falhas/29 controles passando. Antes, essa omissão era reconstruída; depois é `ValidationError` com campo ausente, antes de qualquer aceitação por digest externo. GREEN inicial: 79 testes. Nenhuma expectativa anterior foi relaxada.

Versões do corpo: teste adicional antes da guarda produziu 33 falhas por aceitação indevida. Após a guarda, a suíte F03 desse estágio passou com 112 testes. Acrescentados posteriormente controles já satisfeitos de null/extras, ausência de audit externo e preservação do arquivo original; não se apresenta esses controles como novos RED artificiais.

| Execução | Exit | Saída final literal |
|---|---:|---|
| F01_RED | 1 | 20 failed, 42 passed in 0.19s |
| F01_GREEN | 0 | 62 passed in 0.12s |
| F01_full_regressions | 0 | 1872 passed in 14.01s |
| F03_RED | 1 | 50 failed, 29 passed in 1.26s |
| F03_GREEN | 0 | 79 passed in 2.54s |
| F03_full_regressions | 0 | 1951 passed in 17.14s |
| F03_report_policy_RED | 1 | 33 failed, 79 deselected in 0.78s |
| F03_report_policy_GREEN | 0 | 112 passed in 3.39s |
| F03_report_policy_full_regressions | 0 | 1984 passed in 18.43s |
| old_regressions | 0 | 1810 passed in 14.40s |
| new_targeted | 0 | 190 passed in 3.66s |
| final_pytest | 0 | 2000 passed in 18.96s |
| final_ruff | 0 | All checks passed! |
| final_format | 0 | 86 files already formatted |
| final_mypy | 0 | Success: no issues found in 28 source files |
| final_diff | 0 | sem saída; aprovado |

Logs completos, comandos e erros RED estão no JSON de evidências. Os ciclos foram sequenciais: RED F01 → fix → GREEN → regressão completa; RED F03 → fix → GREEN → regressão completa; RED adicional de versões F03 → fix → GREEN → regressão completa. Ruff detectou problemas de importação/linha nos novos testes em execução intermediária; foram corrigidos apenas nesses arquivos e os gates globais finais passaram.

## D. Testes novos e cobertura efetiva

São 190 testes novos: 62 F01 e 128 F03, separados da baseline de 1.810. A contagem decorre da matriz de contratos/modos, não é objetivo de produto ou evidência de precisão.

F01 cobre ambos os DTOs, strings e datetime aware de Python, três APIs de construção, limites inferiores/superiores com offsets positivos e negativos, dias adjacentes válidos, UTC/horário ordinário, rejeição naive e snapshots aninhados em IntegrationInput. As expectativas UTC válidas são literais. Não é alegação sobre tzinfo customizado hostil que executa código Python arbitrário.

F03 enumera independentemente os campos obrigatórios de cada tipo e confronta essa enumeração com model_fields. Retira UM campo por tentativa em construtor, model_validate e JSON, sem regenerar o envelope externo. A matriz aninhada executa 216 omissões individuais entre os modos/caminhos definidos, além de omissões diretas nos seis DTOs. Inclui input.snapshots, contexto de candidato, validação M1, SnapshotAudit dentro da auditoria M1, identidade, temporal, geografia, financeiro, organizações, taxonomia e IntegrationAudit. Testa null/extras, adulteração de digests, versões do corpo, envelopes completos, reconstrução standalone, ausência de audit externo sem reparar audit interno incompleto, recomputação local e serialização determinística. Promotion permanece false.

Reprocessamento explícito: preserva bytes e hash do envelope recebido rejeitado, constrói nova avaliação apenas de cópia dos inputs e documenta que não é verificação do arquivo original. Para snapshot de input com audit parcial, IntegrationInput recusa até uma decisão explícita de retirar esse audit da cópia para nova avaliação. Não há fallback automático nem migração.

## E. Compatibilidade e limites do contrato

Preservados schema_version=2 e todas as versões/algoritmos/constantes existentes. Não foi introduzida política nova de hash. A representação serializada de relatórios completos não mudou.

Verificação empírica pré/pós em processos novos: 38 casos (cinco fixtures M2.3, 26 M2.3c, sete operacionais); inputs e resultados COMPLETOS byte a byte iguais. Relatórios arquivados completos pré-correção são lidos pela implementação corrigida, e seus inputs reavaliados produzem os mesmos resultados. Captura externa de 19.000.311 bytes, SHA-256 `77a8e20705293b2402c0d8d2477a3a04921914f5aab39f927492bf85fc4c1544`. Inclui controles operacionais com OperationalError. Isso demonstra compatibilidade dos casos capturados, não de todo possível registro externo.

Mudança intencional de aceitação/API: instanciar um audit DTO parcial contando com defaults deixou de ser permitido. Relatórios recebidos com audit não nulo e versões próprias ausentes também são recusados. JSON Schema passa a marcar todos os campos audit DTO como required. Não há migração automática nem invenção de versões históricas. Conserva-se a versão de schema como hardening da exigência já aprovada de metadados explícitos, não como definição de novos metadados ou recodificação de arquivos completos. Consumidores que construíam envelopes parciais precisam fornecê-los completos ou solicitar uma NOVA avaliação explicitamente, nunca alegar verificação histórica após preencher defaults.

Ausência/None de audit continua significando geração local, inclusive em níveis aninhados. Portanto, parsing de um objeto sem envelope não comprova completude histórica daquele envelope. A alteração exige conteúdo explícito DENTRO de envelopes retidos; não transforma DTOs em um verificador criptográfico autenticado de arquivos históricos nem remove o contrato de avaliação local aprovado. Os defaults de claims/inputs sem envelope próprio não foram redesenhados. model_construct/model_copy, mutação de internals e instâncias validadas confiadas em memória não são entrada JSON não confiável nem validação completa; não devem ser usados para verificar arquivos recebidos.

## F. Ambiente efetivamente executado

- Python do projeto: 3.11.16, Clang 22.1.3.
- Pydantic: 2.14.1; pydantic-core: 2.50.1.
- pytest: 9.1.1; Ruff: 0.17.1; mypy: 2.4.0.
- Linux x86_64, kernel 7.0.0-38-generic, glibc 2.43.

Usada exclusivamente a `.venv` existente do projeto. O Python global não é o runtime desses resultados. Inventário completo de pacotes no JSON de evidências. Nenhuma instalação.

## G. Regressão completa

Baseline antes de editar: 1.810 passando. Depois das correções, executada separadamente a mesma baseline excluindo SOMENTE os dois arquivos novos: 1.810 passaram em 14,40s. Novos testes: 190 passaram em 3,66s. Comando integral solicitado: 2.000 passaram em 18,96s. Nenhum skip/xfail novo, alteração nos testes antigos ou atualização de fixture/oráculo para acomodar o fix.

Os controles M2.2a.1, identidade, integrações, consistência, orçamento, provenance, reprocessamento e promoção existentes continuam passando. Sintéticos não estabelecem precisão/recall real, extração automática, SLA de produção ou certificação humana.

## H. Ruff, mypy, Git e arquivos untracked

Comandos finais executados da raiz V2, todos exit 0:

```
.venv/bin/python -B -m pytest -p no:cacheprovider -q
.venv/bin/ruff check --no-cache src tests
.venv/bin/ruff format --check --no-cache src tests
.venv/bin/mypy --no-incremental --cache-dir=/dev/null src
git diff --check
```

Ruff: All checks passed; format: 86 arquivos já formatados; mypy: nenhum problema em 28 fontes. Os gates globais incluem fontes/testes untracked preexistentes e os dois testes novos. O manifesto/comparação inicial não confunde arquivos untracked preexistentes com arquivos criados nesta etapa. Verificação adicional dos quatro novos arquivos untracked: `git diff --no-index --check -- /dev/null <arquivo>` sem diagnóstico de whitespace (exit 1 esperado porque o arquivo difere de /dev/null; não é falha de whitespace). A mesma verificação passou no documento relacionado após remover somente uma linha vazia final. O snapshot de revisão permaneceu imutável: 139 arquivos conferidos sem divergências; fontes/testes originais idênticos ao snapshot. A única diferença do original em relação ao snapshot é essa linha vazia documental, sem alteração de conteúdo ou código após a revisão. `git diff --cached --stat` vazio. A exclusão preexistente `BANCO DE DADOS/bancode Dados.sql` continua intocada; README continua com a alteração anterior e hash inicial preservado.

## I. Revisão independente

Parecer independente: **READY**, `blockers: []`, estritamente para a correção direcionada M2.3d.1 F01/F03. Uma única revisão READ-ONLY (`deleg_9ae3f06b`), sem subagentes de implementação ou correções paralelas; duração 142,23s, 14 chamadas. O revisor executou a suíte completa: **2.000 passaram em 18,77s**, Ruff lint/format global e mypy aprovados (86 arquivos formatados; 28 fontes sem erros).

Reproduziu os defeitos originais contra a implementação corrigida e percorreu recursivamente TODAS as ocorrências de audit em dois relatórios representativos (M23C-A-001 e M23C-I-005), incluindo SnapshotAudit dentro de ValidationAudit. Omitiu um campo por tentativa, nos três modos: **1.077 omissões de campos de audit** e **354 omissões de versões de corpos auditados**, todas recusadas. Testou ainda dois arquivos históricos rejeitados, duas novas avaliações preservando o arquivo original, quatro avaliações locais com audit externo ausente/None, 12 overflows UTC estruturados de strings, oito de datetime Python, 12 aninhados, seis rejeições naive e oito conversões adjacentes exatas. Não houve escape de OverflowError, restauração de metadados recebidos ou promoção habilitada nos casos exercitados.

Compatibilidade independente adicional: comparou os bytes completos de inputs/resultados de **31 casos** (26 M23C + cinco M23), executados nas fontes congeladas anterior e corrigida; 5.161.460 bytes em cada corpus, SHA-256 `6616f74a7349cc3d7463472c229afc0fbe15a7f6f849ceea35e830a521d68602`, igualdade integral. Esta comparação independente NÃO abrange os sete operacionais adicionais da comparação própria de 38 casos; os escopos permanecem separados.

Integridade: snapshot externo de 139 arquivos, manifest SHA-256 `f35bb34217c881e53600cdba077aa843c0babff679b70f18b1343a47343f0e87`, intacto antes/depois; nenhuma divergência ou modificação de arquivos do projeto pelo revisor. Scripts/resultados foram criados somente em scratch. O responsável principal conferiu os hashes, a igualdade dos corpora independentes e **reexecutou o script independente no projeto original**, obtendo PASS e as mesmas contagens. SHA-256 do script: `3ebcf25e2c4a4b5a81eed6cd7333a3155056664f39b914e6d1194fd0216fb321`. Script, resultados, inventário de omissões e recibos estão preservados no JSON de evidências; os corpora completos externos continuam nos caminhos nele indicados.

Aprovação independente de IA não equivale a certificação humana, autorização de produção, autenticação de revisão ou aprovação de M3. F02/F04 e o significado de audit ausente/None permanecem explicitamente registrados como riscos/limites, não foram silenciados.

## J. Riscos restantes e itens deliberadamente adiados

- M23D-F02 permanece: oráculo E2E não observa completamente normalized_name/classification. Não houve alteração desse oráculo ou alegação de cobertura semântica universal.
- M23D-F04 permanece: divergência M1/M2.1 em certos URLs malformados. Não houve alteração de validação URL.
- Audit/digest local não prova autenticidade de fonte, autoria histórica, autorização humana ou revisão autenticada. Nenhum bypass de promoção foi demonstrado; isso não é certificação de segurança.
- Envelope ausente/None é operação de avaliação local, não evidência histórica completa; a API não adivinha a intenção do chamador. Guardas não substituem política explícita do consumidor ao carregar arquivos.
- Escopo continua offline com entradas estruturadas; não foram executados crawlers, PDFs, aquisição, persistência, Supabase, promoção/merge, novas taxonomias, migração de arquivos ou M3.
- Tempos de testes são medições desta máquina, não SLA ou prova contra todo ataque de recurso.

## K. Avaliação

**READY — M2.3d.1, exclusivamente no escopo direcionado de hardening offline F01/F03.** Ambos os bloqueadores foram eliminados nos reproduzidores e matrizes próprios e independentes; nenhuma nova regressão ou bypass foi identificado na revisão realizada. Baseline de 1.810 preservada, 190 testes direcionados aprovados, total de 2.000; Ruff global, formatação, mypy e Git verdes. Relatórios completos e digests preservados nos corpora comparados. Revisão independente READY incorporada, sem blockers.

Compatibilidade intencionalmente mais estrita para envelopes incompletos documentada; nenhum arquivo histórico foi migrado ou recebeu versões inventadas. Não é sign-off universal de produção ou solução de F02/F04. Sem staging, commits, alterações SQL, novas dependências, rede, persistência, promoção/merge ou início de M3. M2.3d.1 encerrada; aguarda-se revisão técnica externa e autorização expressa para qualquer etapa posterior.
