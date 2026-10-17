# Backend V2 — Milestone 1.1a

Fundação offline: domínio puro, sem crawler, persistência, LLM, autenticação,
rede, banco ou imports Legacy. Não é um backend pronto para produção.

## Executar no ambiente existente

```sh
.venv/bin/python -B -m pytest -p no:cacheprovider -q
.venv/bin/ruff check --no-cache src tests
.venv/bin/ruff format --check --no-cache src tests
.venv/bin/mypy --no-incremental --cache-dir=/dev/null src
git diff --check
```

Python mínimo declarado: 3.11. A versão efetivamente testada consta no relatório
M1.1. Runtime: Pydantic V2; desenvolvimento: pytest, Ruff, mypy. Nenhuma nova
dependência é necessária. Não carregar .env, configurações remotas ou credenciais.

## API e mudança de segurança

`validate(candidate, snapshots, reference_date=..., errors=(), review_attestations=())`
retorna `ValidationReport | OperationalError`. Erros técnicos não possuem decisão
semântica. Cada chamada avalia um candidato; o conteúdo completo é preservado.

M1 confiava em `method="manual_review"`. M1.1 remove essa autoridade: o método
somente descreve extração. Não existe adaptador autenticado nesta etapa. Afirmações
de intenção produzem `trusted_review_required`, inclusive notícias e instrumentos
estruturalmente válidos. Assim, o motor atualmente não emite ACCEPTED nem REJECTED
com base nessas declarações. Isso é uma limitação conservadora intencional, não
classificação automática nem rejeição universal de oportunidades reais.

`ReviewAttestation` preserva identidade declarada do revisor, instante UTC,
identidade e digest do candidato, digests das evidências, versão de política,
decisão e proveniência. Mesmo uma declaração perfeitamente vinculada NÃO é
verificada pelo domínio: causa `untrusted_review_attestation` e REVIEW.
Não há booleano, segredo, versão arbitrária ou campo capaz de conceder autoridade.

Futuro adaptador confiável deverá verificar identidade, autorização, escopo,
assinatura/proveniência, expiração/revogação e vínculo aos bytes revisados, fora do
domínio puro. Sua interface e políticas ainda precisam de aprovação. Não foi criado
um verificador fictício. O atestado atual é um DTO não confiável, não essa interface.

`ValidationReport.promotable` sempre retorna False, inclusive em DTOs ACCEPTED.
Invariantes estruturais do relatório não autenticam sua origem. Um futuro serviço de
persistência deverá revalidar entradas e autorização em fronteira controlada; nunca
aceitar um relatório recebido como capacidade de escrita.

## Identidade estrutural e semântica

`DocumentUnit(snapshot_id, pointer)` identifica uma unidade estrutural no snapshot,
não uma oportunidade canônica. O candidato e cada evidência declaram a unidade.
Não há identidade inferida por URL, título, organização ou similaridade.

Para o recorte estruturado suportado, a evidência de um campo deve apontar para o
filho DIRETO de mesmo nome dentro da unidade: por exemplo, candidato em
`/records/0`, título em `/records/0/title`. O papel declarado deve coincidir com o
campo e com esse caminho real. O pointer também precisa resolver no JSON e seu
valor escalar corresponder ao valor afirmado. A igualdade de um record_id arbitrário
não é suficiente. Declarar a raiz ou `/records` como unidade não libera caminhos
descendentes. Contam a estrutura e o valor efetivo, não apenas os rótulos.

Essa verificação NÃO prova que uma fonte diz a verdade, nem que um transformer
preservou corretamente a semântica. Recebe-se JSON já sanitizado. Esquemas nativos
com nomes/estruturas diferentes, texto livre e múltiplas unidades exigem regras por
fonte aprovadas; não há normalização implícita neste recorte.

`CrossDocumentReference` registra origem, alvo, tipo e evidência de link, mas não
valida associação por si só. Qualquer referência produz
`cross_document_relationship_unverified`. Mesmo URL ou identificador externo igual
não autoriza juntar documentos. Resolver identidades, ciclos e retificações permanece
adiado. N:N entre itens e oportunidades continua permitido no modelo de banco.

Geografia de elegibilidade/aplicação, execução, beneficiários, sede e país de origem
não são intercambiáveis. Um valor em `/country_origin` não comprova
`geographic_scope`, mesmo com papel adulterado. Classificações opcionais e escopo
geográfico sem política de mapeamento aprovada recebem
`semantic_mapping_not_approved`. Dinheiro/moeda, organizações/FKs e geografia
detalhada continuam fora do motor: `unsupported_field`. Datas possuem papéis
estruturais distintos (submissão não é resultado). Nenhum campo opcional inválido é
silenciosamente promovido ou preenchido por fallback.

## Contratos e serialização

Contratos internos M1.1 usam `schema_version=2`. Isso NÃO altera a versão 1 do
futuro envelope canônico SQL de proveniência. Não existe mapper ou migration nova.
JSON M1 com versão explícita 1 é incompatível e deve ser reprocessado mediante
migração explícita futura; não realizar conversão silenciosa de dados armazenados.

`FieldAssertion.value` continua uma API Python escalar explícita: str, bool, date,
Decimal finito ou None. Números int/float e datetime não são convertidos em bool,
datas ou dinheiro. JSON emitido usa `{kind, data}` com tags text, boolean, date,
decimal e null. Tags preservam até tipos semanticamente inválidos: date em título
continua date e continua `invalid_field_value` depois do round-trip. Datas e
Decimais não são restaurados com base apenas no nome do campo. Uma string de data
continua string; um parser futuro deve produzir date explicitamente.

Nulos não sobrescrevem valores conhecidos. Conflitos não são resolvidos por ordem,
confiança ou maior prazo. Área permanece N:N; as regras semânticas de classificação
ainda não estão aprovadas. Ambiguidade exige REVIEW. Diagnósticos mantêm somente
as evidências dos campos relacionados; o contexto completo permanece no relatório.

## Hashes e auditoria

RawSnapshot.audit registra snapshot_id, payload_digest, algorithm=sha256,
hash_version=sha256-utf8-v1, contract_version=2 e representação
sanitized-json-text-utf8. São hasheados EXATAMENTE os bytes UTF-8 de payload_json,
sem reformatar/canonicalizar JSON. Espaços e ordem diferentes podem mudar o digest.
Não é hash dos bytes originais HTTP/PDF: eles não são recebidos neste contrato.
Se fornecido, o envelope deve corresponder à identidade e aos bytes; divergências
são rejeitadas na fronteira Pydantic. Na construção sem envelope ele é calculado.

ValidationReport.audit vincula candidato, digests das evidências, envelopes dos
snapshots, contrato, catálogo seeds-000002, ruleset e pares de regra/versão. Para
candidato/evidência: SHA-256 dos bytes UTF-8 EXATOS de model_dump_json() do contrato
2, hash_version=pydantic-json-utf8-v2; não é JSON canônico universal. A reprodutibilidade
entre versões de serializador não testadas não é prometida. O lockfile deve ser
usado no reprocessamento. Ordem de afirmações pode mudar o digest, não resolver
conflitos nem alterar a decisão.

M1.1a acrescenta `audit_version=m1.1a-full-report-1`, `report_digest` obrigatório e
`report_hash_version=pydantic-report-json-utf8-v1`. O digest completo é SHA-256 dos
bytes UTF-8 exatos de `report.model_dump_json(exclude={"audit"})`: inclui TODOS os
campos do relatório fora do próprio envelope, inclusive decisão, data de referência,
status temporal, diagnósticos ordenados com mensagens/campos/evidências, atestados,
candidato e snapshots completos (metadados e envelopes de snapshot incluídos).
O envelope externo não entra no seu próprio hash; catálogo e versões do envelope
são comparados separadamente aos valores esperados. O ruleset semântico permanece
`m1.1-hardening-1`; a correção não adiciona regras de classificação nem autorização.

Sem envelope, a construção calcula um novo. Com envelope retido, qualquer
divergência é rejeitada, não recalculada silenciosamente. Envelopes antigos M1.1
sem `report_digest` são recusados: reprocessamento explícito é necessário, não há
migração automática. `schema_version=2` e a proveniência canônica SQL não mudam.

Um hash recalculável detecta divergência contra um envelope retido, não autentica
a fonte nem impede que alguém substitua payload E envelope. Identidade do snapshot
é UUID; identidade canônica da oportunidade é separada. Não há assinatura ou cadeia
de custódia durável implementada.

## Custo e limites do Validation Engine

Valores conhecidos e evidências são indexados uma vez por campo, e snapshots por
UUID. A seleção de evidências mantém ordem original, duplicatas e contexto nulo.
Não há varredura integral das afirmações para cada campo ou diagnóstico. O custo
ainda depende do tamanho de entrada/saída e da resolução de JSON Pointer; não há
promessa de tempo constante nem SLA para documentos reais.

Política operacional `validation_limits_version=m1.1a-limits-1`, registrada no
envelope: até 1.200 afirmações, 2.400 ocorrências de evidência por candidato e 64
ocorrências de evidência por campo (somadas entre todas as afirmações, incluindo
nulas e duplicatas). Exceder qualquer limite retorna `OperationalError` com
`code=validation_limits_exceeded`, `stage=validation`, sem decisão semântica,
truncamento ou promoção. A checagem precede parsing e geração de diagnósticos,
mas não substitui futuros limites de transporte/deserialização. Não restringe
os DTOs de candidato ou introduz limites nas relações N:N do schema aprovado.

Benchmark sintético offline (mediana de 7 execuções por cenário):
`PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_validation.py`.
`--baseline /caminho/validation.py` compara uma cópia pré-indexação, usando os
mesmos modelos atuais, e exige igualdade integral dos relatórios. Testes de
regressão usam contagem determinística de acessos, não limites frágeis de tempo.

## Parsing e URLs

`safety.py` concentra resolução limitada de JSON Pointer RFC 6901, parsing JSON
seguro e validação HTTP(S) local. Limites concretos, comportamento de Unicode,
números e testes estão documentados no módulo e no relatório M1.1. Entradas fora
dos limites não são truncadas nem transformadas em valores plausíveis. JSON inválido,
não finito, com chaves duplicadas ou acima dos limites produz OperationalError;
evidência não resolúvel produz diagnóstico e REVIEW. Sem captura genérica de Exception.

URLs são verificadas sem rede. IDN e IPv6 válidos são permitidos; credenciais,
controles, whitespace e autoridades malformadas não. Validade sintática não garante
oficialidade, existência, autenticidade, acessibilidade ou segurança contra SSRF.
Não há cliente HTTP nesta milestone; política de acesso remoto é trabalho futuro.

## Compatibilidade e limitações

Autoridades: docs/v2/DECISIONS_V1.md, DATA_CONTRACT.md, GEOGRAPHY_CONTRACT.md,
SCHEMA_DESIGN_V1.md e validações das migrations 000001/000002. Decisões aprovadas e
validações posteriores prevalecem sobre propostas antigas (confiança categórica,
localização única, exemplos taxonômicos antigos). UUID, UTC, date civil, ausência
sem placeholders, fonte distinta de organização, N:N e hashes não identitários são
preservados. Migrations e Legacy não são alterados.

Prazo ausente exige motivo explícito; não inferir fluxo contínuo. Prazo histórico
verificável pode indicar encerrada mesmo enquanto intenção aguarda revisão; nunca
indica aberta por prazo futuro. Isto não modifica a view SQL nem resolve sua política
de timezone/corte. Campos detalhados de normalização, crawlers e persistência são M2
ou posteriores e não foram iniciados.

Há conflito explícito entre preservar as antigas expectativas de ACCEPTED/promotable
por manual_review e remover essa autoridade. Os cenários antigos são mantidos, com
expectativas de segurança revistas e diagnósticos específicos, sem skips/xfails.
Não afirmar que os 77 testes originais passam INALTERADOS: consultar o relatório.

Fixtures são sintéticas. Testes verdes não medem precisão/recall de oportunidades
reais, calibração ou qualidade editorial. Conjunto ouro e políticas por fonte,
revisão humana autenticada, relações entre documentos, catálogo evolutivo,
persistência e envelope canônico de proveniência continuam pendentes.

Sem commit automático. Não restaurar nem stagear a exclusão preexistente de
`BANCO DE DADOS/bancode Dados.sql`.
