# EditalFinder V2 — resultados M1.1a

## Escopo e diagnóstico

Leitura integral do parecer `EDITALFINDER_V2_M11_PARECER_INDEPENDENTE.md` e comparação com os contratos, validador, testes e documentação atuais. Trabalho estritamente offline. Sem crawler, M2, banco, rede, credenciais, alteração em Legacy, migrations ou Supabase. Nenhum commit ou staging.

Baseline executada no ambiente existente: Python 3.11.16, 274 testes aprovados em 0,34 s; Ruff check e mypy aprovados. Ruff format confirmou os dois arquivos apontados pelo parecer: `models.py` e `tests/test_integrity.py`.

Antes da correção da auditoria, a nova suíte produziu 26 falhas e 2 aprovações. Alterações isoladas de status temporal, data de referência, mensagem/código/campo/vínculos de diagnóstico, evidência do diagnóstico, atestado e metadado de snapshot eram aceitas com o envelope original. A mudança de REJECTED para REVIEW também era aceita quando ambas satisfaziam as invariantes estruturais. O teste de catálogo já era protegido.

Antes da indexação/limites, a suíte de escalabilidade produziu 4 falhas e 7 aprovações. Para 300 campos distintos, contabilizou 272.100 acessos a `FieldAssertion.field`; entradas acima dos novos limites ainda retornavam relatórios. Causas: varredura por campo ao agregar valores/conflitos, varredura por diagnóstico para evidências, busca linear de snapshot. Evidências repetidas no mesmo campo também amplificavam o tamanho da saída, o que indexação sozinha não resolve.

## Correção da integridade

`ValidationAudit` agora exige `report_digest` e identifica `audit_version=m1.1a-full-report-1` e `report_hash_version=pydantic-report-json-utf8-v1`.

Representação: SHA-256 dos bytes UTF-8 exatos de `ValidationReport.model_dump_json(exclude={"audit"})`. O relatório completo fora do envelope externo é coberto: candidato, snapshots completos, decisão, data de referência, status temporal, issues ordenadas com mensagens e vínculos de evidência, atestados e versões presentes no resultado. Não há hash circular. Catálogo, versões e resumos do envelope são comparados separadamente aos valores esperados.

Envelope recebido divergente causa ValidationError; não é substituído silenciosamente. Construção sem envelope calcula um novo, sem conceder autoridade. Envelopes antigos sem report_digest são recusados e precisam de reprocessamento explícito. O contrato interno continua schema_version=2; a versão SQL da proveniência não muda. Ruleset e regras semânticas não foram alterados.

Integridade não é autenticidade: substituir conteúdo e envelope continua possível. Não existe assinatura ou referência externa confiável nesta etapa. `promotable` permanece sempre falso, e `manual_review`/atestados não autenticam revisores.

## Desempenho e limites

Indexação única de valores/evidências por campo e snapshots por UUID. Preservadas a ordem global das afirmações/evidências, duplicatas, contexto de afirmações nulas, conflitos tipados, área N:N e a ordem/multiplicidade dos diagnósticos.

Política operacional `m1.1a-limits-1`, registrada no envelope:

- Até 1.200 afirmações por candidato.
- Até 2.400 ocorrências de evidência nas afirmações por candidato.
- Até 64 ocorrências de evidência por campo, somadas entre afirmações inclusive nulas/duplicadas.

Excedentes retornam `OperationalError(code="validation_limits_exceeded", stage="validation")`, sem decisão semântica, truncamento ou promoção. A checagem acontece antes de parsing/diagnósticos, sem restringir os DTOs ou relações do banco.

Benchmark controlado: mediana de 7 execuções, aquecimento fora da medição, construção do candidato fora da medição, mesma sessão Python e mesmos modelos atuais de auditoria completa nos dois motores. A baseline é uma cópia pré-indexação de validation.py; isto isola a indexação, não mede o custo adicional do digest completo contra a M1.1 original. Os 12 cenários exigiram igualdade integral dos relatórios.

| Cenário | Afirmações | Antes (ms) | Depois (ms) |
|---|---:|---:|---:|
| Campos distintos, None | 100 | 1,234 | 0,683 |
| Campos distintos, None | 300 | 6,963 | 1,886 |
| Campos distintos, None | 600 | 25,291 | 3,841 |
| Campos distintos, None | 1.200 | 92,556 | 7,740 |
| Campo repetido, None, sem evidência | 100 | 1,105 | 0,707 |
| Campo repetido, None, sem evidência | 300 | 6,139 | 1,907 |
| Campo repetido, None, sem evidência | 600 | 20,365 | 3,748 |
| Campo repetido, None, sem evidência | 1.200 | 74,476 | 7,685 |
| Campos distintos, valor/evidência inválidos | 100 | 3,910 | 2,875 |
| Campos distintos, valor/evidência inválidos | 300 | 18,653 | 9,041 |
| Campos distintos, valor/evidência inválidos | 600 | 56,887 | 17,659 |
| Campos distintos, valor/evidência inválidos | 1.200 | 191,616 | 36,896 |

Não tratar entradas recusadas pelo limite como validações aceleradas equivalentes. Evidência concentrada acima de 64 por campo agora é recusada, inclusive se todos os valores forem válidos. Isso limita amplificação, não deduplica/trunca dados.

Harness permanente: `PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_validation.py`. Para comparar com uma cópia anterior: acrescentar `--baseline /caminho/validation.py --repeats 7`. A cópia usada nesta execução está no scratch local, não é um artefato durável versionado. Medições são sintéticas locais, não SLA nem avaliação editorial.

## Verificações finais locais

- `.venv/bin/python -B -m pytest -p no:cacheprovider -q`: 325 passed in 0.46s (51 testes adicionais sobre a baseline).
- `.venv/bin/ruff check --no-cache src tests`: All checks passed.
- `.venv/bin/ruff format --check --no-cache src tests`: 15 files already formatted.
- `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src`: Success, 6 source files.
- `git diff --check`: aprovado, com a ressalva de que V2 inteira já estava untracked e este comando não valida arquivos não rastreados.
- Busca estática em src por shell=True, os.system, eval/exec, pickle e atribuições típicas de credenciais: nenhuma ocorrência.

Regressões incluem mutações isoladas em transporte Python/JSON, decisão sem depender de outra falha de invariante, round-trip, digest independente sem circularidade, reordenação de issues, envelope incompleto, ausência de autoridade após recálculo, contagem determinística de trabalho e fronteiras abaixo/no/acima dos três limites. Evidências de campos intercalados preservam ordem global; nulos e duplicatas contam para os limites.

## Arquivos alterados ou adicionados nesta execução

Todos os caminhos abaixo são relativos a backend/V2/:

- `src/editalfinder_v2/domain/models.py`: digest completo e versões do envelope; formatação apontada pelo parecer.
- `src/editalfinder_v2/domain/validation.py`: índices e checagens operacionais de tamanho.
- `src/editalfinder_v2/domain/policies.py`: constantes e versão da política de limites.
- `tests/test_integrity.py`: somente formatação preexistente apontada pelo parecer.
- `tests/test_report_audit.py`: novo, regressões de integridade.
- `tests/test_validation_scaling.py`: novo, regressões de custo, limites e ordem.
- `tests/benchmark_validation.py`: novo, harness offline.
- `README.md`: contrato do envelope, compatibilidade e limites.
- `EDITALFINDER_V2_M11A_RESULTADOS.md`: este relatório.

O parecer independente original foi preservado. pyproject.toml e uv.lock não foram modificados. A exclusão preexistente de `BANCO DE DADOS/bancode Dados.sql` permaneceu intacta, fora do escopo. V2 inteira já era não rastreada no início; não foi realizado git add nem commit.

## Revisão independente das alterações

Parecer de revisão somente leitura: aprovado, sem problemas de segurança ou erros lógicos identificados. O revisor relatou 39 testes específicos aprovados e 1.000 casos diferenciais determinísticos com igualdade integral contra o validador original. Essa execução é evidência relatada pelo revisor; a execução controlada diretamente pelo agente principal é a suíte completa e o benchmark de 12 cenários registrados acima.

As sugestões não bloqueantes foram atendidas na consolidação: teste de diagnóstico multicampo com evidências de papéis distintos e afirmações intercaladas, limite por campo distribuído entre afirmações nulas, e documentação explícita de que os limites não são orçamento global de bytes/snapshots/atestados. Os testes suplementares foram incluídos na execução final de 325 testes.

## Pendências deliberadas

- Referência externa confiável, autorização/autenticação do revisor, assinatura e cadeia de custódia durável.
- Política de acionabilidade e mapeamento semântico por fonte, relações interdocumentais e aprovação de promoção/persistência.
- Limites agregados de bytes, quantidade/tamanho total de snapshots, atestados e tamanho final do relatório na futura fronteira de transporte. Os limites desta etapa não garantem resistência geral a negação de serviço; DTOs ainda são construídos antes de validate().
- Matriz Python 3.11–3.14: somente 3.11.16 foi exercitado nesta execução.
- Dados reais/conjunto ouro e precisão/recall; testes e benchmarks são sintéticos.
- M2, crawlers, normalização e persistência continuam fora do escopo.
