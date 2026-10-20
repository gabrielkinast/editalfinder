# EditalFinder V2 — Resultados M2.2a

## Avaliação

READY exclusivamente para M2.2a offline, após correções e aprovação independente final. O revisor final executou 958 testes (3,09 s), as 51 regressões DTO isoladas (0,10 s), Ruff check/format e mypy, além de 2.964 verificações próprias; não encontrou problema de segurança, erro lógico ou sugestão pendente. A aprovação não abrange produção, autenticação, persistência, promoção ou integração automática ao validador M1. Aguarda revisão técnica do usuário antes de qualquer expansão.

A primeira revisão independente foi NOT READY: executou 907 testes e 88 probes, e reproduziu duas falhas nos DTOs públicos de saída (timezone desconhecido coexistindo com local aware/UTC; precisão fracionária sem limitar os dígitos do datetime). Um terceiro agente corrigiu exclusivamente `temporal_models.py`. O agente principal reexecutou os gates, as 51 regressões e probes após a correção; o código foi novamente congelado para a revisão final aprovada. Não se confunde correção ou aprovação dos gates com aprovação independente.

As duas tentativas de delegar a implementação temporal/geográfica falharam por HTTP 429, sem entregar código. O agente principal implementou ambas localmente. Essas tentativas NÃO são revisão nem aprovação independente. Não houve mudança de provider/configuração para contornar limites.

Não se autoriza produção, persistência, extração por fonte, crawling, merge, promoção ou M2.2b.

## Baseline e autoridades

Árvore Git inspecionada: README já modificado, arquivos M2.1 não rastreados e exclusão preexistente de `BANCO DE DADOS/bancode Dados.sql`. Nenhum deles foi restaurado, stageado ou commitado. Os módulos e artefatos M2.1 preexistentes foram preservados.

Baseline M1/M2.1 reexecutada: 473 testes aprovados em 2,14 s. A baseline não foi presumida a partir do relatório histórico. Parecer/resultados M1.1a, modelos e envelopes, `validation.py`, `safety.py`, policies, contratos/resolvedor M2.1 e documentação de identidade foram examinados. Contratos relevantes: GEOGRAPHY_CONTRACT.md, DATA_CONTRACT.md, DECISIONS_V1.md, OPEN_DECISIONS.md, SCHEMA_DESIGN_V1.md, SQL e validação da migration 000001, todos em modo texto. Não foi carregada configuração/credencial nem acessado Supabase.

A autoridade posterior permite municípios estrangeiros (US/Washington) e múltiplas localizações 1:N; não se reaplicou a proposta inicial de município exclusivamente brasileiro/localização única. Permanecem o país ISO alpha-2, UF somente com BR, macrorregião brasileira coerente, confiança numérica 0–1, civil date e timestamps operacionais UTC, identidade/proveniência separadas.

## Entrega

### Temporal

Dez papéis explícitos, não intercambiáveis: publicação; abertura; submissão; candidatura preliminar; candidatura completa; resultado; contratação; execução; validade administrativa; retificação.

Formatos versionados: ISO civil e timestamp de gramática estrita; D/M/AAAA brasileiro mediante formato explícito; datas por extenso em português mediante formato explícito. O modo não especificado não adivinha locale de datas com barras. Anos curtos, calendário não identificado/não suportado, datas inválidas e ambiguidade produzem diagnósticos específicos, sem sentinelas.

Datas civis permanecem date. Timestamps sem offset e -00:00 não ganham UTC. Offset explícito conhecido permite conversão determinística e preservação do horário local, offset original, precisão e casas fracionárias. Offsets malformados não são normalizados silenciosamente pelo parser Python. Overflow de UTC nos anos 1/9999 gera diagnóstico mantendo o horário declarado.

Prazos preliminar e completo coexistem. Prazos conflitantes não são escolhidos por ordem, confiança ou maior/menor data. Precisões/referenciais não comparáveis são diagnosticados separadamente. Retificações e prazos anterior/novo permanecem visíveis para revisão, sem associação/substituição automática. Prazo ausente nunca implica fluxo contínuo. Nenhum status temporal é calculado ou alterado pelo normalizador.

### Geografia

Preservados os seis papéis SQL, cada componente com prova e confiança próprias. País ISO é validado por membership de 249 códigos, não regex isolada; 27 UFs e cinco regiões seguem o contrato/migration. Catálogo factual extraído de iso-codes 4.20.1, com origem e SHA-256 do input de desenvolvimento documentados; runtime não lê dataset nem faz rede.

Sem país/escopo BR por default; nenhuma inferência por domínio ou sede da organização. Escopo tem prova própria e conserva `nao_identificado` se ausente/inválido. Elegibilidade, execução, beneficiários, origem e sede não viram aliases. Múltiplos países/locais permanecem; componentes de linhas diferentes não podem compor uma localização fictícia. Conflitos de país–UF, país–região, UF–região e escopo–elegibilidade geram códigos explícitos, com originais preservados.

Municípios brasileiros e estrangeiros são texto declarado não certificado. Sem registry/IBGE, `municipality_verified=False` e `geo_municipality_unverified`; não há fuzzy, geocoding ou identificação municipal inventada. UF não inventa BR e não preenche região ausente.

### Evidência e auditoria

Reutilizados IdentityEvidence, Contract, Confidence, OpportunityCandidate, RawSnapshot, OperationalError, parser/pointers seguros, helper de evidências e limites M1.1a. Não foi copiado o resolvedor de identidade nem alterado seu comportamento.

Fronteira compartilhada indexa contexto/afirmações uma vez e exige literal textual, candidato/fonte/execução/unidade corretos, quote integral, método/confiança permitidos, pertencimento à afirmação e papel estrutural comprovado. Aceita apenas filho direto de mesmo nome ou coleções offline com role explícito no objeto; não é extrator de PDF nem política de fonte nativa.

Relatórios preservam input completo, eventos/locais, diagnósticos e versões. Envelope integral SHA-256 de UTF-8 `model_dump_json(exclude={'audit'})`; envelope recebido divergente é rejeitado. Retificações e contextos não são omitidos do hash. Integridade não é autenticidade; recalcular hash não concede autoridade. Normalizadores não possuem decisão ACCEPTED e `promotable=False`.

Limites operacionais explicitados: 1.200 claims/afirmações, 2.400 evidências, 64 por campo, 32 snapshots, 8 MiB agregados de payload, 1 Mi caracteres de valores e 1.000 referências. Cada JSON conserva os limites do parser M1.1a. Excedentes recusados sem truncar. Isso não certifica orçamento completo de transporte, construção de DTOs e metadados.

## TDD e testes

Ciclos RED→GREEN observados antes das implementações relevantes:

- Fronteira compartilhada: stub reproduziu 4 falhas; binding válido, snapshot duplicado e orçamento foram implementados; 20 testes iniciais passaram.
- Geografia: default BR incorreto falhou; códigos/locais ausentes produziram 14 falhas na etapa seguinte; conflitos/municípios produziram falhas antes da correção; escopo e combinação entre linhas produziram 13 falhas antes da implementação.
- Temporal: data ISO ausente falhou antes do parser; formatos/calendários/evidência produziram 22 falhas; timestamps/offsets/overflow produziram 8 falhas; conflitos/retificação/comparabilidade produziram 3 falhas antes da implementação.
- Pós-revisão: novo `test_temporal_review_regressions.py` com 51 casos; RED confirmado de 42 falhas e 9 controles válidos antes da correção, cobrindo construtor, validação Python e JSON, timezone desconhecido, offset/local incoerentes, UTC não zero/divergente e dígitos fracionários. A mutação de UTC no teste de auditoria foi ajustada para alterar o par local/UTC coerentemente e continuar isolando o envelope retido, sem depender da nova rejeição de forma.
- Invariantes de DTO: 12 casos inicialmente aceitos indevidamente falharam antes dos validadores de forma temporal/geográfica.

Correção do harness: método sintético não permitido foi trocado por `structured_field`; evidência vazia é rejeitada pelo contrato base, e há teste próprio da fronteira. Mutação de auditoria geográfica usa formas canônicas válidas para não passar apenas pela rejeição de outra invariante.

Cobertura inclui 249 países parametrizados, produto cartesiano UF/região, datas de fronteira em sete anos e 12 meses nos três formatos, seis precisões fracionárias, offsets com mudança de dia, múltiplas etapas, evidência de publicação relabelada, sede versus elegibilidade, unidades/provas estrangeiras, JSON não textual, contexto conflitante, ordem de conflitos, determinismo, idempotência de valores canônicos, imutabilidade, round-trips e mutações com envelope retido em Python/JSON. Casos negativos verificam códigos específicos. Não há skips/xfails usados para acomodar regressões.

## Comandos executados e resultados locais

Diretório: `/home/lorenzozm/PROJETOS/editalfinder/Projeto/backend/V2`.

Ambiente efetivamente exercitado: Python 3.11.16, Pydantic 2.14.1, Ruff 0.17.1 e mypy 2.4.0. Nenhuma dependência adicionada.

- `.venv/bin/python -B -m pytest -p no:cacheprovider -q`
  Última execução após revisão final: 958 passed in 3.10s; 485 testes adicionais sobre 473. A execução pós-correção anterior foi 958 passed in 3.01s; a pré-revisão foi 907 passed in 3.01s.
- `.venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_semantic_common.py tests/test_normalization_contracts.py tests/test_temporal_normalization.py tests/test_temporal_metamorphic.py tests/test_temporal_review_regressions.py tests/test_geography_normalization.py tests/test_geography_metamorphic.py`
  Resultado pós-correção: 485 passed in 1.80s. Subconjunto anterior sem o novo arquivo de regressões: 434 passed in 0.95s.
- `.venv/bin/ruff check --no-cache src tests`
  Resultado: All checks passed.
- `.venv/bin/ruff format --check --no-cache src tests`
  Resultado: 40 files already formatted.
- `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src`
  Resultado: Success: no issues found in 16 source files.
- `git diff --check`
  Resultado: exit 0. Complementado por varredura dos 14 novos arquivos Python, pois diff não cobre untracked: nenhum whitespace final.
- `PYTHONPATH=src:tests .venv/bin/python -B /home/lorenzozm/.hermes/cache/scratch/m22a_additional_probes.py`
  Resultado: 10.000 normalizações adicionais de strings sintéticas determinísticas (quatro formatos temporais e país), sem exceções inesperadas; determinismo e round-trips aprovados; quatro JSONs inválidos retornaram `normalization_invalid_snapshot_json`; guard de filesystem na chamada temporal aprovado. É probe do implementador, não revisão independente.
- `.venv/bin/python -B /home/lorenzozm/.hermes/cache/scratch/m22a_verify_scope.py`
  Resultado: 5.689 arquivos preexistentes comparados por SHA-256; somente README mudou. Nenhum achado na varredura AST dos seis módulos novos para imports de I/O e chamadas perigosas; sem staging; exclusão SQL preexistente preservada. Script e baseline ficam no scratch local, não são artefatos duráveis do produto.

A baseline de 473 foi novamente executada excluindo explicitamente os testes novos então existentes:
`.venv/bin/python -B -m pytest -p no:cacheprovider -q --ignore=tests/test_semantic_common.py --ignore=tests/test_temporal_normalization.py --ignore=tests/test_temporal_metamorphic.py --ignore=tests/test_geography_normalization.py --ignore=tests/test_geography_metamorphic.py`.

## Arquivos desta milestone

Modificado:

- README.md — entrada da milestone e link de contrato; conteúdo anterior preservado fora dos ajustes documentais relacionados.

Criados em src/editalfinder_v2/domain/:

- semantic_common.py
- temporal_models.py
- temporal_normalization.py
- geography_models.py
- geography_normalization.py
- geography_catalog.py

Criados em tests/:

- semantic_fixtures.py
- test_semantic_common.py
- test_normalization_contracts.py
- test_temporal_normalization.py
- test_temporal_metamorphic.py
- test_temporal_review_regressions.py
- test_geography_normalization.py
- test_geography_metamorphic.py

Documentação nova:

- docs/v2/SEMANTIC_NORMALIZATION_M22A.md
- EDITALFINDER_V2_M22A_RESULTADOS.md (este arquivo)

## Compatibilidade e pendências

Nenhum módulo M1.1a/M2.1, teste anterior, pyproject.toml, lockfile, Legacy ou migration foi modificado. Exclusão SQL preexistente permanece fora do escopo e sem staging. Sem Supabase, crawling, persistência, normalização financeira, resolução de organização/taxonomia, promoção ou commits.

O contrato SQL possui um único prazo civil e não representa todas as etapas, offsets, precisão, calendário e relações de retificação. O domínio offline conserva a informação; nenhuma tabela/migration/mapper ou JSONB de conveniência foi inventado. Novos eventos/locais não são automaticamente promovidos a afirmações aceitas pelo Validation Engine.

Pendências deliberadas: revisão técnica do usuário (a revisão independente final foi aprovada); políticas reais por fonte e conjunto ouro; associação autenticada de retificações entre documentos e precedência; projeção de múltiplas etapas na persistência futura; timezone/corte de prazo/status; cadastro IBGE e governança de países; política de região derivada; autorização/cadeia de custódia; orçamento de transporte; matriz Python 3.11–3.14. Apenas 3.11.16 foi executado. Não há alegação de precisão/recall com fontes reais.

M2.2b não foi iniciado. Aguardar revisão técnica antes de qualquer expansão.
