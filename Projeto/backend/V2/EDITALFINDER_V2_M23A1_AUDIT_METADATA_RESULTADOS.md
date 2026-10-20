# Correção dirigida — IntegrationAudit: metadados explícitos

## Escopo e conclusão

Lido integralmente `EDITALFINDER_V2_M23A1_REVISAO_INDEPENDENTE_CHATGPT.md`.
Corrigida a aceitação de envelopes de auditoria incompletos. Apenas
`src/editalfinder_v2/domain/integration_models.py` foi modificado no domínio.
Orquestração, orçamento, normalizadores, evidências e os testes anteriores
permanecem inalterados. Não foi iniciada M2.3b.

## Reprodução antes e depois

Antes: `audit={"report_digest": original.audit.report_digest}` foi aceito tanto
por IntegrationAudit.model_validate quanto por IntegrationReport.model_validate_json.
O envelope restaurado recebeu automaticamente schema_version, output_budget_version,
algorithm, hash_version e limits_version. O relatório restaurado era igual ao
original, embora esses cinco campos não tivessem sido recebidos.

Foi observado RED nos testes de remoção: 36 falhas por ausência de ValidationError,
com seis casos já aprovados porque report_digest já era obrigatório.

Depois: o mesmo envelope é rejeitado com cinco erros `missing`, um para cada
metadado ausente. Remover individualmente qualquer um dos seis campos também é
rejeitado nas três rotas: construção Python, model_validate e model_validate_json,
tanto no DTO isolado como dentro do relatório completo.

Campos explicitamente obrigatórios:

- schema_version = 2;
- report_digest;
- algorithm = sha256;
- hash_version = integration-pydantic-json-utf8-v1;
- limits_version = m2.3-integration-limits-v1;
- output_budget_version = m2.3a.1-output-budget-v1.

A geração local fornece todos os campos explicitamente. Não há defaults nesses
campos nem backfill de metadados do envelope recebido. O JSON Schema também declara
os seis campos obrigatórios. Um envelope completo continua sujeito à comparação
com a auditoria esperada e à recomputação de todos os outputs do relatório.

O digest do cenário grant permaneceu igual antes/depois:
`283b32e4d7a9c43e6740c2be659e48e7728f5e7f740f425cb7ad4dd9bfaa09c1`.
Não houve mudança no corpo, algoritmo de hash ou valores serializados de envelopes
completos gerados localmente.

## Reprocessamento histórico sem confusão de políticas

Procedimento explicitamente documentado e executado nos testes:
`docs/v2/INTEGRATION_AUDIT_REPROCESSING.md`.

A restauração estrita de envelope incompleto agora falha. Para uma NOVA avaliação,
o chamador preserva o arquivo original, extrai somente input e executa integrate
sob a política atual. O exemplo gera um recibo separado com:

- marcador `operation=reprocess_input_under_current_policy`;
- SHA-256 dos bytes UTF-8 originais;
- presença e conteúdo do envelope original, sem preencher campos ausentes;
- política utilizada na nova avaliação, inclusive em falha operacional;
- nova auditoria completa, quando um relatório é emitido;
- `original_policy_inferred=False` e `historical_outputs_verified=False`.

O exemplo não é um novo adaptador de transporte/persistência. É um procedimento
local com as APIs existentes, exercitado diretamente a partir do bloco Python da
documentação para evitar divergência com os testes. Não realiza I/O de arquivos
nem substitui o registro original. O recibo não é assinatura/autorização.

A ausência TOTAL de audit ou audit=None continua sendo uma rota de geração local
após recomputação, não uma afirmação sobre o envelope histórico. Para arquivos
históricos, usar o procedimento explícito com origem e verificação separadas,
nunca apagar um envelope para apresentar o resultado como o mesmo registro.

Política não declarada na origem permanece desconhecida. Versões antigas ou
incompatíveis não são convertidas. Reprocessar input não comprova decisões,
diagnósticos ou hashes dos outputs históricos. Um verificador de políticas
históricas e uma migração de schemas continuam fora de escopo.

## Testes e resultados reais

Ambiente de execução: a mesma .venv Python 3.11.16/Pydantic 2.14.1 do projeto.
Não foi executada uma nova matriz de versões.

Novos testes: `tests/test_m23_audit_metadata.py`, 80 casos parametrizados:

- remoção de cada campo obrigatório em audit isolado e relatório, nas três rotas;
- digest-only nas três rotas;
- envelopes completos preservados sem alterar sua serialização;
- campos explicitamente nulos rejeitados;
- ausência total de envelope e None preservando geração local;
- JSON Schema e model_fields_set confirmando presença explícita;
- reprocessamento de digest-only, pré-orçamento, política desconhecida,
  envelope ausente e envelope nulo sem modificar a origem;
- recusa operacional de 32 grants pelo orçamento de 64 MiB;
- recusa de schema de input incompatível, sem migração automática.

Resultados finais:

- baseline inicial: 1.437 passed in 7.10s;
- testes novos: 80 passed in 0.81s;
- todos os testes anteriores, excluindo somente o novo arquivo:
  1.437 passed in 7.09s;
- suíte completa: 1.517 passed in 7.66s;
- mypy strict src: sem erros em 27 arquivos;
- Ruff check e format do módulo alterado e do novo teste: aprovados;
- Ruff global src/tests: continuam sete ocorrências preexistentes em
  tests/m23_fixtures.py — B023 em 70/73/77; E501 em 147/166/172/178;
  o mesmo arquivo continua com formatação pendente. Ele não foi modificado;
- Ruff global excluindo explicitamente apenas m23_fixtures.py: lint aprovado
  e 72 arquivos formatados;
- git diff --check aprovado, nada staged ou commitado;
- inventário inicial/final por SHA-256 e verificações UTF-8, whitespace,
  newline final e marcadores de conflito complementam Git em arquivos não rastreados.

Comandos executados no diretório backend/V2:

```sh
.venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_m23_audit_metadata.py
.venv/bin/python -B -m pytest -p no:cacheprovider -q --ignore=tests/test_m23_audit_metadata.py
.venv/bin/python -B -m pytest -p no:cacheprovider -q
.venv/bin/ruff check --no-cache src tests
.venv/bin/ruff format --check --no-cache src tests
.venv/bin/ruff check --no-cache --extend-exclude m23_fixtures.py src tests
.venv/bin/ruff format --check --no-cache --extend-exclude m23_fixtures.py src tests
.venv/bin/mypy --no-incremental --cache-dir=/dev/null src
git diff --check
```

## Arquivos e restrições

Modificado:
- src/editalfinder_v2/domain/integration_models.py.

Criados:
- tests/test_m23_audit_metadata.py;
- docs/v2/INTEGRATION_AUDIT_REPROCESSING.md;
- EDITALFINDER_V2_M23A1_AUDIT_METADATA_RESULTADOS.md.

Preservados: integration.py, integration_budget.py, os 1.437 testes anteriores,
fixtures e demais componentes M1/M2. O orçamento continua em 64 MiB, conservador e
sem promessa de teto de RSS. O exemplo pressupõe limites próprios de transporte
antes de decodificar JSON. Modelos construídos/copiados por rotas Pydantic sem
validação continuam sendo escapes de código confiável, não um protocolo externo.

Nenhum acesso a Legacy, migrations ou Supabase. Nenhuma promoção, merge, crawler,
persistência, commit ou implementação de M2.3b. A correção está concluída e parada
para revisão humana, sem alegação de nova aprovação independente.
