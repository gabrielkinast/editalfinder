# EDITALFINDER V2 — M2.3d — Resultados

## Decisão executiva

NOT READY. A higiene autorizada foi concluída sem mudança observável das fixtures; todos os gates passam. Entretanto, a auditoria reproduziu uma exceção não estruturada na fronteira de timestamps (M23D-F01) e aceitação de envelopes aninhados sem metadados históricos explícitos (M23D-F03). Nenhum desses achados foi corrigido durante a Fase B. M23D-F02 é uma lacuna não bloqueante do oráculo E2E, não uma falha semântica de produção demonstrada.

O escopo é composição offline com entradas já estruturadas. Não há certificação humana de segurança, avaliação de extração real, precisão/recall, persistência, autorização de promoção ou início de M3.

## A. Fase A — correção Ruff e equivalência

Arquivo autorizado: `tests/m23_fixtures.py`. A função interna `value` em `adapt_records` foi inspecionada: cria Evidence no DocumentUnit do registro, acrescenta FieldAssertion ao candidato e devolve SemanticValue com IdentityEvidence do mesmo candidato/fonte/execução.

Reproduzidos três B023 (`unit`, `assertions`, `cid`) e quatro E501; o formatador também recusava o arquivo. A alteração prende explicitamente os três valores por argumentos keyword-only com defaults locais (`bound_unit`, `bound_assertions`, `bound_cid`). Os demais deltas são exclusivamente Ruff format. Não houve alteração do payload sintético, da propriedade das evidências, do escopo dos registros ou das expectativas.

Antes de editar, um processo novo capturou entradas e resultados COMPLETOS: cinco casos M2.3, 26 semânticos M2.3c e sete operacionais = 38 casos. Depois, outro processo comparou igualdade estrutural de todos os pares input/result e igualdade byte a byte da serialização ordenada. Ambas passaram. O corpus de comparação tem 19.000.311 bytes, SHA-256 `77a8e20705293b2402c0d8d2477a3a04921914f5aab39f927492bf85fc4c1544`. Inclui o caso próximo ao limite e todos os OperationalError operacionais. A captura anterior é evidência de equivalência de higiene, NÃO um novo oráculo semântico circular.

O JSON de evidências conserva o fonte anterior do fixture, o diff completo, os recibos por caso, o comparador executável e seus hashes. A reprodução adicional do Ruff no fixture anterior congelado verificou que seu hash é idêntico ao capturado antes da correção. As saídas integrais anteriores do lint/formatação estão em `tree_verification`.

## B. Baseline, ambiente e congelamento

A suíte inicial voltou a passar com 1.810 testes; a baseline histórica não foi tomada como prova. Após a Fase A: 1.810 passaram em 14,04 s. Na Fase B, no snapshot: 1.810 passaram em 14,20 s. Nenhum teste de regressão foi removido, adicionado ou teve expectativas editadas. As sondagens adicionais foram scripts separados, fora de src/tests e fora do snapshot.

Ambiente efetivamente testado:

- Python 3.11.16, build Clang 22.1.3 (não o Python global 3.14).
- Pydantic 2.14.1 / pydantic_core 2.50.1.
- pytest 9.1.1; Ruff 0.17.1; mypy 2.4.0.
- Linux 7.0.0-38-generic, x86_64, glibc 2.43; 12 CPUs lógicas.
- Inventário integral das 16 distribuições instaladas em `frozen_manifest.packages`.

Snapshot: `/home/lorenzozm/.hermes/cache/scratch/m23d-audit/frozen`. Copiados 136 arquivos: 28 fontes, 59 arquivos de testes (56 Python e três JSON), contratos, documentação e configuração. Arquivos e diretórios da cópia sem permissão de escrita; .venv é symlink para o ambiente existente, não um ambiente independente hermético. Sem cache pytest, Ruff ou mypy, sem bytecode novo. A relação ordenada path/hash está no JSON de evidências.

SHA-256 do manifesto congelado: `f8f0514ea6234d6443094438625e1d48dd43233b6cce0a2b46f97ce64745a4ec`.

Versões relevantes inspecionadas:

- Contrato schema 2; snapshot `sha256-utf8-v1` / contract `2`.
- M1: `m1.1-hardening-1`, `m1.1a-full-report-1`, `m1.1a-limits-1`, `pydantic-json-utf8-v2`, `pydantic-report-json-utf8-v1`.
- Identidade: `m2.1-identity-v1`, `m2.1-identity-limits-v1`, `identity-pydantic-json-utf8-v1`; `opaque-exact-v1`, `opaque-nfc-v1`, `url-conservative-v1`, `cycle-exact-v1`.
- Temporal/geografia: `temporal-conservative-v1`, `geography-conservative-v1`, `m2.2a-semantics-v1`, `m2.2a-normalization-limits-v1`.
- Financeiro/organizações/taxonomia: versões `*-conservative-v1`, `m2.2b-semantics-v1`, `m2.2b-normalization-limits-v1`.
- Catálogo `seeds-000002`; geografia `iso3166-1-iso-codes-4.20.1`.
- Integração `m2.3-integration-v1`, limites `m2.3-integration-limits-v1`, digest `integration-pydantic-json-utf8-v1`, orçamento `m2.3a.1-output-budget-v1`, consistência `m2.3b-consistency-v1`.

O inventário com declarações e linhas está preservado, evitando interpretar defaults de hoje como atestação histórica.

## C. Inventário arquitetural inspecionado

- `models.py`, `policies.py`, `safety.py`, `validation.py`: domínio M1, decisões, parsing JSON/Pointer, evidências, limites e auditoria.
- `identity_models.py`, `identity_normalization.py`, `identity_resolution.py`, `url_identity.py`: normalização versionada e comparação contextual, sem merge.
- `semantic_common.py`, `temporal_models.py`, `temporal_normalization.py`, `geography_models.py`, `geography_normalization.py`, `geography_catalog.py`: EvidenceIndex, papéis temporais/geográficos e catálogos offline.
- `m22b_common.py`, `financial_models.py`, `financial_parsing.py`, `financial_normalization.py`, `organization_models.py`, `organization_normalization.py`, `taxonomy_models.py`, `taxonomy_normalization.py`: verificações lexicais/contextuais e relatórios completos.
- `integration.py`, `integration_models.py`, `integration_budget.py`, `integration_consistency.py`: orquestrador real, recomputação completa, orçamento e regras entre domínios.
- README, contratos em `docs/v2`, relatórios/revisões M2.3b/M2.3c, dataset congelado e respectivos testes. Não se substituiu a inspeção do código por relatórios anteriores.

## D. Auditoria domínio a domínio

### M1 — decisões e confiança

`validate` não interpreta a ausência de erros como aprovação: exige evidência, escopo, identidade e diagnósticos. REVIEW mantém incerteza; REJECTED é reservado ao diagnóstico não contradito `non_opportunity`; ACCEPTED exige os invariantes estruturais de `instrument_verified`, mas a engine atual não dispõe de verificação de atestação humana. `ValidationReport.promotable` sempre retorna False.

Atribuir `method=manual_review` ou fornecer ReviewAttestation não confere autoridade. Testes de construção/serialização não encontraram promoção automática. A reconstrução completa de IntegrationReport reavalia a M1, ao contrário de tratar qualquer DTO standalone como autorização. Campos extras e números não finitos foram recusados com ValidationError. É preciso separar a fronteira Pydantic, os OperationalError de avaliação e decisões semânticas: M23D-F01 demonstra uma exceção que escapa dessa separação.

### Identidade

Namespace, tipo, política, valor original e ciclo são verificados explicitamente. URL compartilhada/documento compartilhado não determina identidade de oportunidade. Portas padrão/host têm normalização conservadora; fragmento, query de identidade, ordem e caracteres Unicode de path/query não são descartados arbitrariamente. Remoção de tracking é política explícita, não default. Políticas desconhecidas não viram aliases silenciosos. URLs são identificadores offline, não autorização SSRF/HTTP/DNS.

Os casos de ciclos distintos, namespaces distintos, IDs conflitantes, documentos múltiplos, portal reutilizado e snapshots contraditórios são cobertos pela suíte e sondagens. Comparações exatas não alteram candidatos nem combinam evidências; não existe autorização de merge. M23D-F03 inclui o envelope de identidade.

### Temporal

Papéis publicação, abertura, deadline preliminar/completo, resultado, contratação, execução e retificação permanecem distintos. Civil date não adquire hora. Timezone ausente e `-00:00` não adquirem instant_utc. Normalização temporal trata overflow UTC com `temporal_timezone_conversion_out_of_range`; a M1 não trata o mesmo limite no metadado de coleta/revisão (F01). Múltiplas etapas/retificações permanecem rastreáveis, sem precedência inventada. A reference_date é explícita, sem resultado dependente do relógio.

### Geografia

Country/UF/região e papéis são separados; UF brasileira exige BR explícito. Municípios permanecem `municipality_verified=False`. Elegibilidade não decorre de publisher, sede, execução, idioma, moeda ou domínio. Vários países elegíveis são preservados. As sondagens mudam publisher/role e demonstram a distinção entre normalização e elegibilidade; transplantes de evidência entre registros não geraram oportunidade promovível.

### Financeiro

Decimal preserva coeficiente/expoente; não há float como resultado monetário, conversão cambial ou comparação por magnitude entre moedas diferentes. Papéis orçamento, máximo/mínimo por proposta, bolsas, contrapartida e prêmio são distintos. Ranges e percentuais obedecem aos formatos/papéis aprovados, não geram inferência de quantidade de projetos.

Fronteira de confiança importante e deliberada: format/currency/unit são declarações do adaptador, não atributos autenticados pela evidência do valor. A mesma string `1.234`, BRL, é 1234 com `brazilian` e 1.234 com `us`; sem moeda não gera BRL por default (`financial_currency_missing`). Isso é interpretação lexical explícita, não verificação das condições da fonte. Juros, carência, amortização, garantia, principal de crédito e investimento não têm todos papéis/relacionamentos dedicados aprovados. Não se reaproveita award_amount como prova de aprovação ou contrato de financiamento. Nenhuma taxa, equity ou valuation foi inventada.

### Organizações

Publishing, funding, managing, executing, partner, beneficiary e applicant são papéis distintos. CNPJ tem sintaxe/checksum, mas existência permanece unverified. Nome normalizado e sigla não são identidade jurídica. Chaves contextuais exigem provas suportadas e namespace correto; não há merge por similaridade. A apresentação lexical pode permanecer quando as provas não sustentam chaves. F02 mostra que a projeção E2E não verifica integralmente esse resultado lexical; os testes especializados de organizações continuam existindo.

### Taxonomias

Somente códigos exatos/dimensões/catalog_version aprovados. Desconhecido/ambíguo preserva original e diagnóstico. VC/equity não vira crédito por envolver dinheiro; não existe fallback automático para `outra`. Uma classificação bolsa/edital não estabelece actionable/specific_instrument.

## E. Segurança de evidência e isolamento de identidade

EvidenceIndex cruza candidate_id, source_id, execution_id, snapshot, DocumentUnit, JSON Pointer, FieldAssertion e semantic_role. As verificações de coleções estruturadas também checam índice/componente/papel no registro. Pointer textual e hash não autenticam a instituição publicadora, nem permitem misturar registros do mesmo snapshot.

Nos cenários multirregistro e ataques da suíte, evidências de outro registro são recusadas ou geram diagnóstico, sem corromper candidatos independentes. Nenhum bypass cross-record confirmado. A mutação controlada de um pointer preservou a forma do input e foi rejeitada por isolamento/evidência, não por um campo Pydantic inventado. Identidade contextual permanece separada da autorização de promover/mesclar.

## F. Consistência entre domínios

Inspecionado `evaluate_consistency`: limita-se aos relatórios normalizados com contexto correspondente, referências domain-qualified e provas suportadas. Mantém ordem determinística e diferencia contradiction, potential_conflict, insufficient_information e no_conflict_detected. Códigos/evidence/claim references/version references são recomputados no IntegrationReport.

- Orçamento x proposta exige mesmo candidato e moeda comparável, sem converter currencies.
- Abertura após fechamento é contradição apenas na etapa comparável; multi-stage/retificação não escolhe deadline vencedor.
- Grant+credit não é contradição por si só; sem identidade de instrumento/tranche a conclusão é conservadora.
- Sede de organização/publisher não é elegibilidade; notícia/resultado com alegações de actionability gera diagnóstico, não promoção.
- Múltiplos financiadores, áreas e países não são considerados contradições automaticamente.

Permanece a limitação: falta contrato aprovado para identidade de instrumento/tranche e precedência de retificação. Não foi criado um identificador de relacionamento nem uma segunda engine.

## G. Serialização e integridade de hashes

As adulterações da suíte e das sondagens em montantes, papéis, evidência, taxonomia, comparações, diagnósticos, referências e digest foram executadas com envelope retido e sem envelope quando a avaliação local é permitida. IntegrationReport verifica saída completa por reprocessamento; retirar seu audit não transforma saída forjada em válida. Entrada alterada com nova avaliação local válida não é verificação histórica da entrada anterior.

O envelope superior exige algoritmo/versões explícitos, e o digest adulterado falha. Porém os envelopes aninhados antigos ainda restauram metadados omitidos por defaults: achado M23D-F03. Portanto não se afirma que TODOS os envelopes exigem a presença explícita de metadados históricos. SHA-256 demonstra integridade/recomputação local, não autenticidade da fonte, autoridade humana ou impossibilidade de modificar o próprio processo Python. `model_construct`/`model_copy` não são canais confiáveis de verificação; objetos são revalidados no boundary completo.

## H. Segurança de recursos e medições

Limites inspecionados: 32 candidatos por batch; 64 comparações explícitas; 4.800 claims de integração; 16 MiB de snapshots distintos no batch; orçamento de admissão 64 MiB. M1: 1.200 assertions, 2.400 evidências/candidato, 64 evidências/campo. Normalização: 1.200 claims, 32 snapshots, 8 MiB payload agregado e 1 Mi caracteres declarados. JSON: 2 MiB/payload, depth 64, 100.000 nodes, tokens numéricos até 256 caracteres e pointer até 4.096. Financeiro: até 256 dígitos de fonte e módulo do expoente até 1.000; limites próprios do wire Decimal são distintos. URLs até 8.192 caracteres/32.768 bytes. O inventário fonte contém os limites adicionais de identidade e strings.

Sondagens novas limitadas: 33 candidatos com UUIDs próprios; 65 comparações; 1.201 assertions; 1.201 temporal claims; 257 dígitos financeiros; JSON com 66 níveis; snapshot pouco acima de 2 MiB. Produziram OperationalError estruturado, no nível batch/candidato/domínio aplicável. Um limite financeiro local não deve ser confundido com falha batch: o IntegrationReport pode carregar FinancialReport=OperationalError preservando o restante. Snapshot grande foi recusado pelo orçamento antes do parsing profundo; não foi apresentado como evidência de qual guard de JSON executou.

Benchmark: três processos novos sequenciais por caso; perf_counter e tracemalloc. Construção dos inputs excluída; tracing cobre integrar/dump/revalidação. Sem threshold de tempo/SLA. Nenhuma alocação intencional de gigabytes, RSS não medido. Medianas:

| Caso | Admissão (bytes) | JSON (bytes) | integrar (s) | serializar (s) | revalidar (s) | pico Python (bytes) | JSON/snapshot único |
|---|---:|---:|---:|---:|---:|---:|---:|
| M23C-A-001 | 7020928 | 166688 | 0.059564 | 0.002231 | 0.079846 | 2340412 | 140.192x |
| M23C-B-001 | 4567344 | 116689 | 0.041634 | 0.001625 | 0.055198 | 1647171 | 135.057x |
| M23C-C-001 | 4520240 | 115936 | 0.040574 | 0.001743 | 0.054149 | 1642604 | 139.850x |
| M23C-E-001 | 21705888 | 654467 | 0.195929 | 0.007714 | 0.283377 | 7438803 | 183.016x |
| near | 67108864 | 9969994 | 0.771168 | 0.014036 | 0.559727 | 71341556 | 32.715x |
| over | 67108865 | 163 | 0.004753 | 0.000020 | 0.000021 | 305808 | 0.001x |

A razão JSON/snapshot único é amplificação em relação apenas ao payload bruto compartilhado, NÃO à serialização completa do input. As razões JSON/admissão e pico Python/admissão estão no JSON de evidências. No caso near, o pico de alocação Python excede 64 MiB: isso NÃO viola o contrato de estimativa de admissão. Over cobra o valor saturado 67.108.865 e retorna `integration_output_budget_exceeded`, 163 bytes, sem truncamento silencioso. O caso near admite exatamente 67.108.864 e serializa 9.969.994 bytes. Construção Pydantic, transporte e memória total do processo continuam fora de um hard RSS ceiling.

## I. Avaliação do oráculo congelado M2.3c

Confirmados 26 casos semânticos, categorias A–I, 37 slots de candidatos e sete casos operacionais. Esperados são literais no manifesto, com referências contratuais; adaptador constrói entradas/proveniência e não captura golden outputs da implementação. A ordem histórica da autoria de cada esperado não é demonstrável somente pelo snapshot. Comparadores de ordenação e round-trip foram executados na suíte.

Sondagens controladas copiando registros, sem mudar expectativas congeladas:

- Deadline preliminar virou publicação: a nova avaliação continuou bem formada; o esperado temporal original detectou a corrupção.
- Troca de orçamento/máximo: o esperado financeiro detectou os montantes trocados, não um erro sintático.
- Elegibilidade reatribuída a execução: o esperado geográfico distinguiu o papel.
- Publishing reatribuído a managing: o esperado de papéis de organização detectou a alteração.
- Dimensão de taxonomia substituída: esperado detectou classificação diferente/não mapeada.
- Ciclo de publicação alterado: comparação deixou de sustentar o exact match original; o oráculo de identidade detectou a mudança.
- Evidência movida entre registros: falha ligada ao escopo/evidência, mantendo controles independentes.

Houve ainda injeção temporária em memória de comportamento incorreto de produção: parse financeiro passou a devolver orçamento 42, com seus verificadores locais reutilizando a função adulterada. A avaliação integrada foi construída e `check_candidate` detectou o valor errado. Isso é sensibilidade semântica, não corrupção do manifesto ou erro incidental de shape. Outra injeção revelou F02: nomes normalizados absurdos passaram no comparador E2E porque a projeção olha o nome original.

Os controles F continuam sendo de registros já estruturados como news/result/etc., não classificadores de páginas. Permanecer REVIEW/promotable=False não prova precisão de extração, nem disponibilidade atual. A checagem de M1 exige subconjunto dos códigos obrigatórios, permitindo códigos extras: limitação adicional do oráculo, não novo defeito comprovado de produção.

## J. Achados confirmados e classificação

### M23D-F01 — MEDIUM — bloqueador de robustez: OverflowError fora da fronteira estruturada

Referências: `src/editalfinder_v2/domain/models.py:76–79`, `RawSnapshot.utc_timestamp`; `models.py:260–263`, `ReviewAttestation.utc_review`.

Raiz: AwareDatetime aceita um datetime local no intervalo representável, mas `value.astimezone(UTC)` pode sair dos anos 1..9999. Os validators não capturam OverflowError e Pydantic não a converte em ValidationError. A normalização temporal já possui tratamento correspondente; os metadados M1 não.

Reprodução mínima (na raiz V2, PYTHONPATH=src):

```python
from uuid import UUID
from editalfinder_v2.domain.models import RawSnapshot
RawSnapshot(
    id=UUID(int=1), source_id=UUID(int=3), source_code="fapergs",
    execution_id=UUID(int=2),
    collected_at="0001-01-01T00:00:00+23:59",
    collector_version="synthetic-audit", url="https://example.org/",
    payload_json="{}",
)
# OverflowError: date value out of range
```

O reproduzidor completo exercitou dois timestamps extremos e quatro rotas: RawSnapshot Python/JSON, IntegrationInput JSON e ReviewAttestation JSON. Oito OverflowError reproduzidos. Oito controles com datas adjacentes dentro do range UTC foram aceitos. Os casos de ReviewAttestation são DTOs sintéticos sem confiança; não representam aprovação autenticada.

Impacto: um pequeno input pode abortar a construção do input integrado com exceção inesperada em vez de rejeição estruturada. Não foi demonstrado crash remoto, persistência, promoção, execução arbitrária ou contaminação de evidência. Bloqueia esta auditoria final por sua exigência de erros estruturados e fronteiras explícitas. Proposta para autorização separada: guard localizado dos dois validators, rejeição ValueError/ValidationError e regressões de ambos os extremos/rotas. NÃO aplicado.

### M23D-F02 — MEDIUM — não bloqueante: projeção E2E não observa normalized_name/classification

Referências: `tests/test_m23c_pipeline.py:38–40`, `projection`, e `tests/test_m23c_pipeline.py:44–78`, `check_candidate`; fonte injetada apenas em memória: `organization_normalization._organization_values` e `integration.evaluate_consistency`.

A projeção verifica o papel e `o.claim.name.original`, não `o.normalized_name`. Sob patch temporário que devolve `NOME NORMALIZADO CORROMPIDO`, o relatório integrado é construído e o check_candidate do cenário A passa. Não houve edição de fonte ou teste. Outros testes unitários de organizações protegem normalização; não se conclui que a suíte completa é cega ou que produção está errada.

A revisão independente também inverteu classification dos diagnósticos de consistência mantendo os códigos. O teste E2E completo do cenário A passou, inclusive com replay determinístico usando a função incorreta. Assim, não basta que o digest/replay confirmem uma execução internamente consistente: o oráculo precisa observar a classificação semântica correta. Ambas as lacunas foram reproduzidas pelo responsável principal sem mudar os esperados.

Consequência: a afirmação de que o manifesto M2.3c sozinho valida integralmente a normalização organizacional ou a classificação da consistência seria excessiva. Recomenda-se, em trabalho posterior autorizado, esperado literal de normalized_name/chaves/identificadores/classification e testes de mutação que provem sensibilidade. Não alterar o manifesto durante esta auditoria.

### M23D-F03 — MEDIUM — bloqueador do requisito histórico de metadados explícitos

Referências: `models.py:46–51` (SnapshotAudit), `models.py:266–280` (ValidationAudit), `semantic_common.py:50–56` (NormalizationAudit), `m22b_common.py:105–111` (NormalizationAudit M2.2b), `identity_models.py:105–109` (IdentityAudit). Contrastam com IntegrationAudit, `integration_models.py:142–150`, que exige presença explícita.

Reprodução: gerar IntegrationReport para M23C-I-005; manter seu audit e todos os digests; apagar somente `/identity_results/0/audit/hash_version` do JSON; reconstruir via `IntegrationReport.model_validate_json`. O objeto é aceito, o default `identity-pydantic-json-utf8-v1` é reintroduzido e o relatório final é igual ao original com o MESMO audit superior.

Varredura limitada de omissões representativas em todos os tipos de envelopes: 30 omissões individuais; 24 aceitas com default restaurado e audit superior retido; seis rejeitadas (cinco metadados superiores e catalog_version de ValidationAudit). Todos os paths/valores estão no JSON de evidências. Os envelopes aninhados M1, snapshot, identidade, normalizações M2.2a/M2.2b aceitam omissões.

Distinção importante: isso segue os defaults dos contratos antigos e não demonstrou alteração de conclusões nem quebra de SHA-256. Contudo NÃO atende à exigência M2.3d de presença explícita e de não inferir versões ausentes durante verificação histórica. Não é avaliação local solicitada com `audit=None`: o envelope superior original foi retido. A correção requer decisão de compatibilidade e boundary histórico estrito, não remover defaults indiscriminadamente nesta auditoria. Nenhuma alteração aplicada. Este achado foi descoberto após o envio inicial ao revisor e não recebeu confirmação independente; ver seção O.

### M23D-F04 — LOW — não bloqueante: validação URL M1 aceita sintaxe recusada em M2.1

Descoberto pelo revisor independente e reproduzido pelo responsável principal. Referências: `safety.py:150–172`, `_valid_host`; `safety.py:175–209`, `valid_url`; `validation.py:266–271`.

`valid_url("https://example.org/path<bad>")` e `valid_url("http://0x7f000001/")` retornam True. Os mesmos valores em official_url do cenário M23C-A-001 atravessam integrate sem o diagnóstico M1 `invalid_official_url`. `normalize_url` de M2.1 devolve `url_invalid` para ambos. A primeira string contém delimitadores literais incompatíveis com a checagem de URL bem formada; a segunda é um host hexadecimal com interpretação ambígua em parsers.

A integração permanece REVIEW e promotable=False. Nenhuma URL foi aberta, resolvida via DNS ou usada em HTTP: não é demonstração de SSRF. Recomenda-se harmonizar, em correção futura aprovada, a política sintática de M1 sem transformá-la em permissão de rede. Nenhuma correção nesta Fase B.

## K. Fronteiras de confiança remanescentes

1. Claims/declarações estruturadas do adaptador não equivalem à extração correta ou fonte autêntica.
2. Snapshot hash não prova publicação pela instituição; não houve acesso a fontes externas.
3. CNPJ checksum não prova existência; nome/acrônimo não prova identidade legal.
4. Manual_review/ReviewAttestation sem verificador confiável não autoriza ACCEPTED/promover.
5. Exact identity não autoriza merge, transferência de claims ou de evidências.
6. Formato numérico/moeda/unidade e outros parâmetros do adaptador não são autenticados pelo texto do montante.
7. Defaults/envelopes locais não substituem contexto e políticas históricas retidos (F03).
8. O limite 64 MiB não é teto de RSS, limite de HTTP ou quota de transporte. Nenhuma dessas camadas futuras foi implementada/auditada.

## L. Matriz de capacidade e lacunas reais

Legenda: SUPPORTED = contrato aprovado representa; PARTIALLY SUPPORTED = original preservado, interpretação canônica/relacionamento incompleto; UNSUPPORTED = não há representação dedicada aprovada; BLOCKED BY TRUST = requer fonte/identidade/autorização confiável. A classificação pode variar por subaspecto explicitamente listado.

| Conceito | Fomento | Crédito | Investimentos | Preparação/evidência necessária |
|---|---|---|---|---|
| Identidade de programa/ciclo, URL, fonte/registro | SUPPORTED | SUPPORTED | SUPPORTED | ID/namespace/ciclo e evidência contextual explícitos; identidade não é merge |
| Papéis orçamento/limites/ranges/moeda | SUPPORTED | PARTIALLY SUPPORTED | PARTIALLY SUPPORTED | Papéis genéricos aprovados; não confundir proposal_maximum com identidade de principal/investimento |
| Não reembolsável/reembolsável/crédito | SUPPORTED | SUPPORTED | PARTIALLY SUPPORTED | Códigos exatos aprovados; equity/VC preservado como desconhecido, nunca convertido em crédito |
| Identidade de instrumento/tranche e relação entre parcelas | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | Novo contrato relacional e provas; híbrido não é contradição por default |
| Juros/carência/amortização/repagamento detalhado | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | Futuro contrato com unidade, periodicidade, indexador e condições; não inferir de classificação reembolsável |
| Garantias e elegibilidade de crédito | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | Texto pode permanecer no snapshot; sem avaliação de risco/garantia estruturada aprovada |
| Equity, valuation, round, ownership | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | Preservação lexical/snapshot é PARTIALLY SUPPORTED; não há instrumento canônico aprovado |
| Applicant requirements detalhados | PARTIALLY SUPPORTED | PARTIALLY SUPPORTED | PARTIALLY SUPPORTED | Elegibilidade geográfica separada; critérios empresariais/científicos completos sem contrato de regras |
| Estágios de aplicação/datas/timezone | SUPPORTED | SUPPORTED | SUPPORTED | Papéis e precision explícitos; nenhuma disponibilidade inferida do relógio |
| Retificações e deadline vencedor | PARTIALLY SUPPORTED | PARTIALLY SUPPORTED | PARTIALLY SUPPORTED | Datas/rastreio suportados, precedência/efeito substitutivo requer aprovação |
| Organizações/papéis/IDs/CNPJ sintático | SUPPORTED | SUPPORTED | SUPPORTED | Prova contextual; existência/identidade jurídica BLOCKED BY TRUST |
| Elegibilidade country/UF versus execução/sede | SUPPORTED | SUPPORTED | SUPPORTED | Evidência específica por papel, sem default BR |
| Certificação de município | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | Texto preservado; catálogo/resolver certificado futuro |
| News/result versus offer já estruturado | SUPPORTED | SUPPORTED | SUPPORTED | Validar declarações/evidência, não classificar páginas automaticamente |
| Actionability real/autenticidade da fonte/aprovação | BLOCKED BY TRUST | BLOCKED BY TRUST | BLOCKED BY TRUST | Fonte autoritativa e mecanismo de revisão autenticada aprovado; promoção desabilitada |
| Extração de sites/PDFs/classificador real | UNSUPPORTED | UNSUPPORTED | UNSUPPORTED | Milestone futuro; nenhum crawler/parser novo foi executado |

FAPERGS/FINEP/CNPq, BNDES e fundos/VC são exemplos de futura cobertura, NÃO fontes validadas neste trabalho. Nenhum site foi consultado.

## M. Preparação necessária antes de M3

- Autorizar correção localizada de F01 e decisão/compatibilidade histórica de F03; manter os reproduzidores e repetir regressões/gates.
- Fortalecer o oráculo organizacional (F02) e definir política para códigos M1 extras, sem usar resultados da implementação como esperados.
- Aprovar contratos de instrumentos/tranches, termos de crédito e equity/round/valuation antes de expandir taxonomia ou SQL.
- Definir proveniência/autenticidade da coleta, evidência por campo e governança de revisão humana antes de qualquer promoção/persistência.
- Planejar corpus real versionado e revisão rotulada por domínio para medir extração/classificação. Testes sintéticos não fornecem precision/recall real.
- Especificar limites de entrada/transporte/worker e reprocessamento histórico antes de expor endpoints; preservar versões, dependências e políticas reais.
- Só iniciar M3 mediante autorização explícita. Nenhuma dessas atividades foi implementada aqui.

## N. Saídas exatas dos gates

Sem --extend-exclude. Os gates Ruff incluem todo src/tests, inclusive `tests/m23_fixtures.py`. A saída completa anterior do Ruff (7 erros) e da formatação está preservada no JSON de evidências; a reprodução hash-verificada do fonte anterior tem caminhos do snapshot M2.3c, não é um novo lint do fixture corrigido.


### Fase A — árvore original após higiene

Comando: `.venv/bin/python -B -m pytest -p no:cacheprovider -q`

Saída exata (exit 0):

```text
........................................................................ [  3%]
........................................................................ [  7%]
........................................................................ [ 11%]
........................................................................ [ 15%]
........................................................................ [ 19%]
........................................................................ [ 23%]
........................................................................ [ 27%]
........................................................................ [ 31%]
........................................................................ [ 35%]
........................................................................ [ 39%]
........................................................................ [ 43%]
........................................................................ [ 47%]
........................................................................ [ 51%]
........................................................................ [ 55%]
........................................................................ [ 59%]
........................................................................ [ 63%]
........................................................................ [ 67%]
........................................................................ [ 71%]
........................................................................ [ 75%]
........................................................................ [ 79%]
........................................................................ [ 83%]
........................................................................ [ 87%]
........................................................................ [ 91%]
........................................................................ [ 95%]
........................................................................ [ 99%]
..........                                                               [100%]
1810 passed in 14.04s
```

Comando: `.venv/bin/ruff check --no-cache src tests`

Saída exata (exit 0):

```text
All checks passed!
```

Comando: `.venv/bin/ruff format --check --no-cache src tests`

Saída exata (exit 0):

```text
84 files already formatted
```

Comando: `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src`

Saída exata (exit 0):

```text
Success: no issues found in 28 source files
```

Comando: `git diff --check`

Saída exata (exit 0):

```text

```


### Fase B — snapshot congelado

Comando: `.venv/bin/python -B -m pytest -p no:cacheprovider -q`

Saída exata (exit 0):

```text
........................................................................ [  3%]
........................................................................ [  7%]
........................................................................ [ 11%]
........................................................................ [ 15%]
........................................................................ [ 19%]
........................................................................ [ 23%]
........................................................................ [ 27%]
........................................................................ [ 31%]
........................................................................ [ 35%]
........................................................................ [ 39%]
........................................................................ [ 43%]
........................................................................ [ 47%]
........................................................................ [ 51%]
........................................................................ [ 55%]
........................................................................ [ 59%]
........................................................................ [ 63%]
........................................................................ [ 67%]
........................................................................ [ 71%]
........................................................................ [ 75%]
........................................................................ [ 79%]
........................................................................ [ 83%]
........................................................................ [ 87%]
........................................................................ [ 91%]
........................................................................ [ 95%]
........................................................................ [ 99%]
..........                                                               [100%]
1810 passed in 14.20s
```

Comando: `.venv/bin/ruff check --no-cache src tests`

Saída exata (exit 0):

```text
All checks passed!
```

Comando: `.venv/bin/ruff format --check --no-cache src tests`

Saída exata (exit 0):

```text
84 files already formatted
```

Comando: `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src`

Saída exata (exit 0):

```text
Success: no issues found in 28 source files
```


## O. Revisão independente

Revisão independente AI read-only concluída: NOT READY. Um único revisor inspecionou o snapshot real, executou 1.810 testes (14,21 s), elaborou sondagens adicionais e não modificou fontes/testes/fixtures/configuração. O script independente foi lido e reexecutado pelo responsável principal com exit 0; seus achados adicionais e hashes foram reproduzidos. Não é certificação humana.

Convergência e achados adicionais:

- TIMESTAMP-OVERFLOW corresponde a M23D-F01: MEDIUM, bloqueador; quatro combinações JSON independentes propagaram OverflowError. Não se demonstrou exploração externa, DoS de serviço, promoção ou bypass de autenticação.
- M23C-ORACLE-BLIND-SPOTS corresponde a M23D-F02: MEDIUM, não bloqueante; além de normalized_name, a inversão de classifications mantendo os códigos passou no teste E2E completo. Dedicated tests podem detectar essas falhas; não se afirma cegueira da suíte completa.
- M1-URL-SYNTAX corresponde a M23D-F04: LOW, não bloqueante; duas URLs malformadas/ambíguas passam em M1 e são recusadas em M2.1. Ambos os candidatos continuam REVIEW/promotable=False.
- M23D-F03 é um achado adicional do responsável principal, confirmado por execução própria. O revisor já havia terminado quando foi tentado encaminhar esse novo reproduzidor; não se atribui confirmação independente a ele. NOT READY independe de F03, pois F01 já é bloqueador confirmado por ambos.

Sensibilidade independente: 26/26 casos semânticos detectaram mutação de código diagnóstico; 7/7 operacionais detectaram código de erro/contagem de candidatos incorretos, todos por AssertionError, sem contar falhas incidentais de validação. A sondagem de ValidationReport standalone confirmou que um DTO pode conter ACCEPTED autoconsistente sem autoridade; promotable=False e sua substituição no IntegrationReport completo foi rejeitada, mesmo com audit superior omitido.

Comandos/saídas reportados pelo revisor:

```text
PYTHONPATH=src:tests .venv/bin/python -B -m pytest -p no:cacheprovider -q
1810 passed in 14.21s

PYTHONPATH=src:tests .venv/bin/python -B /home/lorenzozm/.hermes/cache/scratch/m23d-review-probes-independent.py
Exit 0

.venv/bin/ruff check --no-cache .
All checks passed

.venv/bin/ruff format --check --no-cache src tests
84 files already formatted

PYTHONPATH=src:tests .venv/bin/python -B -m mypy --no-incremental --cache-dir=/dev/null src
Success: no issues found in 28 source files

.venv/bin/ruff format --check --no-cache .
Exit 1: 2 Markdown files would be reformatted; 120 files already formatted.
```

A última chamada é exploratória e MAIS AMPLA que o gate obrigatório src/tests. Os dois Markdown históricos são `EDITALFINDER_V2_M22A_REVISAO_INDEPENDENTE.md` e `EDITALFINDER_V2_M23A_REVISAO_CHATGPT.md`; não foram editados para ocultar a falha. Não se afirma formatação verde de todo o diretório incluindo documentação.

O revisor verificou 136 hashes antes/depois: manifesto `f8f0514ea6234d6443094438625e1d48dd43233b6cce0a2b46f97ce64745a4ec` em ambas as verificações, sem divergências. A reexecução principal voltou a verificar os mesmos hashes antes/depois. O único arquivo criado pelo revisor foi o script de sondagens no scratch, fora do snapshot; seu conteúdo e a reexecução estão preservados no JSON de evidências.

Transcript integral da revisão: `/home/lorenzozm/.hermes/cache/delegation/live/deleg_fd2189c7/task-0.log`. Limites declarados: inspeção e sondagens direcionadas não são verificação exaustiva do espaço de estados, nem evidência de extração/autenticidade/matriz de versões Python.

## P. Arquivos alterados/criados e preservação

Alterado exclusivamente na Fase A: `tests/m23_fixtures.py` (bindings explícitos e formatação).

Criados como artefatos da auditoria, fora da árvore congelada revisada:

- `EDITALFINDER_V2_M23D_RESULTADOS.md` (este relatório).
- `docs/v2/M23D_AUDIT_EVIDENCE.json` (ambiente, hashes, gates, scripts/reproduzidores, medições e recibos).

Nenhum src de produção, fixture JSON, expectativa de teste, configuração, Legacy, SQL/migração ou documento anterior foi alterado. README e a exclusão preexistente de `BANCO DE DADOS/bancode Dados.sql` permanecem mudanças anteriores, não deste milestone. A comparação com os hashes iniciais apontou somente o fixture autorizado; comparação da árvore revisada original contra o congelamento: zero divergências. Nenhum staging/commit. Arquivos untracked foram inventariados separadamente; `git diff` isoladamente não prova preservação de arquivos untracked.

Os scripts de auditoria foram executados de scratch e estão integralmente preservados no JSON (não dependem da sobrevivência do scratch). Para reexecutar um deles, extrair `scripts[nome.py]` em diretório de auditoria separado e usar `PYTHONPATH=src:tests .venv/bin/python -B caminho/script.py`; o script de recursos requer o benchmark JSON em seu caminho declarado, que pode ser ajustado SOMENTE na cópia do script. Isso não é alteração do pipeline congelado. O reproduzidor mínimo F01 acima não depende do scratch.

## Q. Avaliação final

NOT READY para encerrar M2.3d. Todos os gates de qualidade e as regressões passaram, mas isso não elimina os reproduzidores de F01/F03. Não se atribui prontidão de produção ou extração real. Não há bypass cross-record, merge ou promoção automática demonstrado; os bloqueadores são fronteiras de erro e verificação histórica explícita. Código/testes permanecem congelados; correções exigem autorização separada. M3 não foi iniciado.
