# EditalFinder V2 — M2.1: relatório de implementação

## Parecer

READY para o escopo offline M2.1. A revisão adversarial independente final reexecutou as três reproduções corrigidas, a suíte de 473 testes e probes adicionais, sem novos erros lógicos ou preocupações de segurança identificados. Isso não certifica persistência, produção, SSRF, autenticidade de publicadores ou orçamento global de transporte/memória.

Escopo: contratos, normalização e comparação determinística offline. Não é autorização de promoção, merge ou persistência. M2.2 não foi iniciado.

## Inspeção e arquitetura

A árvore Git foi inspecionada antes de escrever código. Baseline real: 325 testes aprovados em Python 3.11.16; README e núcleo estavam rastreados no commit existente 2b5a5b3. A exclusão de `BANCO DE DADOS/bancode Dados.sql` e o arquivo não rastreado `V2.tar.gz` já existiam e foram preservados. Nenhum stage ou commit foi realizado.

Foram lidos os contratos atuais e os documentos DECISIONS_V1, DATA_CONTRACT, SCHEMA_DESIGN_V1, MIGRATION_PLAN e MIGRATION_000001_VALIDATION. Inspecionadas a definição SQL V2 de oportunidade_identificador e a documentação SQL Legacy, sem executá-las. A autoridade e as divergências entre proposta, decisão aprovada e SQL concreto estão discriminadas em `docs/v2/IDENTITY_M21.md`.

A PK SQL existente é (tipo_identificador, namespace, fonte_id, valor_normalizado). Não inclui ciclo ou versão de normalização; original é nullable no SQL. A implementação preserva original obrigatoriamente no domínio, mas não inventa mapper, tabela, coluna ou constraint. A política de persistência de chaves reutilizadas em ciclos diferentes continua bloqueada para decisão posterior.

Foram separados fonte, execução, snapshot, documento/unidade estrutural, identificador externo, oportunidade e ciclo de publicação. claimed_document_id e claimed_opportunity_id são declarações, não identidades inferidas ou autenticadas. Documento não é hash; snapshot não é documento estável entre execuções; execução não é ciclo.

## Entregas

- Contratos imutáveis Pydantic V2 para namespace, identificador bruto/normalizado, ciclo, evidência, contexto, diagnóstico, conflito, envelope e relatório.
- Normalização opaca literal por padrão; NFC somente explícita. Nunca casefold, NFKC, trim, remoção de zeros ou pontuação.
- Canonicalização de URL HTTP(S) estritamente ASCII no esquema, com host/IDN conservador, portas, escapes, queries e fragments auditáveis.
- Queries preservam ordem, repetição, parâmetros de identidade e valores vazios. Tracking default preservado; remoção opt-in somente dos cinco nomes raw autorizados. Fragments não são descartados.
- Resolver puro com índices contextuais e decisões versionadas: exact_match, no_supported_match, conflict, insufficient_information, distinct_cycles.
- Provas isoladas por candidato/fonte/execução/snapshot/unidade/role/pointer/valor textual integral. Booleanos não comprovam strings. Mesmo UUID de snapshot com contexto contraditório bloqueia resolução.
- Detecção de divergências de identificador/documento, UUIDs de oportunidade incompatíveis, fonte incoerente e reuso de chaves entre ciclos.
- Auditoria completa de resultado sem hash circular e sem pretensão de autenticidade.
- Limites operacionais explícitos e erros sem decisão semântica.

URL igual, hash igual, título/descrição semelhantes, organização, país ou domínio não produzem match de oportunidade. Mesmo exact_match é comparação contextual entre dados fornecidos, não confiança editorial. promotable permanece False.

## Testes e revisão

TDD executado para contratos/decisões centrais, isolamento de evidência, normalização de ciclos, adversários URL e correções da revisão. O bootstrap inicialmente falhou por módulo ausente; depois os testes comportamentais demonstraram falhas reais contra o resolvedor inicialmente não implementado. Testes adicionais cobrem round-trip, versões, idempotência, determinismo, limites inclusivos e códigos negativos específicos.

A primeira revisão independente foi NOT READY e encontrou três defeitos que não foram ocultados pela suíte verde:

1. Identificador/ciclo textual podia ser comprovado por booleano no payload devido ao helper compartilhado de evidência.
2. Dois subjects podiam declarar bytes/metadados diferentes para o mesmo UUID de snapshot.
3. Regex case-insensitive Unicode reconhecia `httpſ` como esquema suportado; com porta ocorria KeyError.

Um contexto terceiro corrigiu somente esses achados, sem alterar o núcleo M1.1a. O novo arquivo de regressões tem 33 casos. Foram relatadas e exercitadas falhas RED específicas antes das correções; o agente principal reexecutou a suíte final após a correção. O reconhecimento ASCII do esquema não remove suporte Unicode de host/path. O helper booleano do Validation Engine não foi alterado.

A revisão independente final foi READY no escopo offline. O revisor executou a suíte completa (473 passed), as suítes específicas (148 passed) e relatou 7.515 assertions adicionais em probes de tipos, snapshots, ordem dos argumentos, round-trip, não promoção e combinações Unicode/URL. A confirmação de correção não depende apenas desse relato: o agente principal executou diretamente os 33 casos de regressão como parte da suíte completa e todos os gates. Nenhum código foi alterado após essa revisão final.

Verificação diretamente executada pelo agente principal após as correções:

- pytest: 473 passed in 1.50s, sem skips/xfails. São 148 testes adicionais sobre a baseline observada.
- Ruff check src tests: All checks passed.
- Ruff format --check src tests: 26 files already formatted.
- mypy src: Success, 10 source files.
- git diff --check: limpo. Ressalva: Git não cobre arquivos novos não rastreados; verificação complementar direta dos 14 arquivos criados não encontrou whitespace no fim de linhas.
- Diff dos quatro módulos M1.1a, migrations, pyproject.toml e uv.lock: vazio.
- Índice Git: sem alterações staged.

Probe adicional diretamente executado, seed 2101: 10.000 avaliações URL com duas políticas, todas com preservação do original e round-trip JSON; 1.660 saídas normalizadas idempotentes, 7.776 recusas url_invalid e 564 url_ambiguous_idna. Mais 100 pares de identidade com decisão/códigos simétricos. A suíte persistente também inclui testes metamórficos seedados, sem nova dependência. Isso não é prova exaustiva de correção nem medição editorial.

## Benchmark final

Comando: `PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_identity.py`.

Condições: Linux x86_64, kernel 7.0.0-38-generic, glibc 2.43, Intel Core i7-1355U, 12 CPUs lógicas; Python 3.11.16, Pydantic 2.14.1. Máquina compartilhada com escala dinâmica de frequência; sem pinning de CPU, isolamento de carga ou perfil de pico de memória. Mediana de cinco chamadas após aquecimento. Construção dos inputs fora da medição; verificação das provas, normalização, construção do relatório e hash completo dentro dela. Igualdade/determinismo verificados fora do intervalo medido.

Cada tamanho é por subject: são dois subjects por comparação. Os cenários realmente suportados são duplicatas de uma chave e valores iguais declarados em namespaces sintéticos distintos. O segundo exercita muitas chaves indexadas, não um catálogo aprovado de autoridades reais nem extração de 10.000 IDs diferentes de um documento nativo.

| Identificadores por lado | Duplicatas (ms) | Namespaces distintos (ms) |
|---:|---:|---:|
| 100 | 6,065 | 7,112 |
| 1.000 | 60,447 | 72,415 |
| 10.000 | 993,459 | 1.130,269 |

Em 10.000 por lado, relatórios JSON mediram 32.911.411 e 55.024.819 bytes. Duplicatas mantiveram quatro testemunhas na decisão; namespaces distintos produziram 20.002. A busca evita produto cartesiano; serialização, validação de DTOs e hashing continuam proporcionais aos dados preservados, com ordenação de chaves O(K log K). Não se promete SLA, custo constante ou segurança global de transporte.

Amostras, mínimos/máximos, tamanhos e runtime estão em `docs/v2/M21_BENCHMARK.json`. As medições foram repetidas após as três correções. A primeira revisão também executou independentemente o harness, mas os números acima são da execução final do agente principal.

## Arquivos criados ou modificados

Relativos a backend/V2/:

Modificado:
- README.md — entrada M2.1 e referência ao contrato técnico.

Criados:
- src/editalfinder_v2/domain/identity_models.py
- src/editalfinder_v2/domain/identity_normalization.py
- src/editalfinder_v2/domain/identity_resolution.py
- src/editalfinder_v2/domain/url_identity.py
- tests/test_identity.py
- tests/test_identity_edges.py
- tests/test_identity_properties.py
- tests/test_identity_review_regressions.py
- tests/test_url_identity.py
- tests/test_url_identity_integrity.py
- tests/benchmark_identity.py
- docs/v2/IDENTITY_M21.md
- docs/v2/M21_BENCHMARK.json
- EDITALFINDER_V2_M21_RESULTADOS.md

Legacy, migrations existentes, Supabase, testes/núcleo M1.1a e dependências não foram modificados. Não houve rede, crawler, persistência, fuzzy merge, LLM no resolvedor, graph database, habilitação de promoção, stage ou commit.

## Pendências e consequências

- Registro/governança/autorização dos namespaces reais e interpretação por fonte: match é contextual, não certificação do publicador.
- Equivalência entre fontes/namespaces, aliases e identidade documental cross-snapshot: pode haver falsos negativos explícitos; não são resolvidos por heurística.
- Vocabulário/granularidade dos ciclos e chamadas recorrentes/contínuas: não inferidos de datas; ciclos ausentes/incomparáveis permanecem insuficientes.
- PK SQL sem ciclo/versão: persistência ingênua de URL/ID reutilizado é incompatível. Necessária decisão posterior, sem migration nesta milestone.
- Transporte/orçamento global de bytes/pico de memória: os maiores relatórios sintéticos excedem 55 MB; não expor como endpoint público sem gate específico.
- Autenticidade/assinatura, autorização de revisão e referência externa confiável do envelope: não implementadas. Hash não concede autoridade.
- Regras específicas de query/fragments/redirects/IDNA por fonte: equivalências não suportadas continuam distintas ou recusadas conservadoramente.
- Dados reais, precisão/recall, calibração e matriz Python 3.11–3.14 não foram certificados. Unicode/IDNA usam tabelas do runtime; reprocessamento deve fixar ambiente e versões, não assumir JSON canônico universal.

Encerrar M2.1 e aguardar revisão técnica humana. Nenhuma atividade M2.2 foi iniciada.
