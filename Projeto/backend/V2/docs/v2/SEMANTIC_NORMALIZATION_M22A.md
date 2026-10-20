# M2.2a — Normalização semântica temporal e geográfica offline

## Fronteira e autoridade

Subsistema puro em Python 3.11+/Pydantic V2. Não lê relógio, filesystem, timezone local, banco ou rede; recebe contratos imutáveis, produz valores e diagnósticos determinísticos. Não extrai PDFs, não rastreia portais e não associa organizações, identidades ou documentos. Não há cálculo de status temporal, seleção de prazo canônico, decisão ACCEPTED, escrita ou promoção automática. `promotable` permanece False.

Autoridades consultadas: DECISIONS_V1.md (decisões aprovadas), DATA_CONTRACT.md e GEOGRAPHY_CONTRACT.md (propostas anteriores), SCHEMA_DESIGN_V1.md, OPEN_DECISIONS.md, migration 000001 e MIGRATION_000001_VALIDATION.md. Decisões posteriores não são reabertas por propostas antigas: UUID, confiança Decimal numérica 0–1, múltiplas localizações 1:N, país ISO alpha-2, UF somente com BR, região brasileira coerente com UF e ausência sem placeholders continuam válidos.

A proposta geográfica inicial dizia município exclusivamente brasileiro. A migration e sua validação posterior, seção “Casos geográficos válidos”, permitem explicitamente US/Washington sem UF/região brasileira. M2.2a preserva o texto estrangeiro, sem inventar código IBGE ou certificação municipal. OPEN_DECISIONS.md contém itens historicamente superados; a escolha 1:N já está aprovada em DECISIONS_V1 e implementada no SQL.

## API e contratos comuns

`semantic_common.py` fornece:

- `SemanticValue(original, provenance)`: literal original e `IdentityEvidence` reutilizado da M2.1 como vínculo de proveniência, não como declaração de igualdade de oportunidades.
- `NormalizationContext(candidate, snapshots)`: candidato e snapshots completos. Não resolve identidade nem junta candidatos.
- `NormalizationDiagnostic(code, message, claim_index, evidence)`: códigos específicos, índice de entrada e somente provas relacionadas.
- `NormalizationAudit`: SHA-256 integral, algoritmo, versão da representação e versão dos limites.
- `AuditedNormalizationReport`: contrato imutável, envelope integral e nenhuma capacidade de promoção.

Normalizadores recebem uma entrada tipada contendo contexto e valores explicitamente rotulados. Retêm a entrada inteira no relatório. Retificações e locais múltiplos não desaparecem por ordenação, deduplicação ou confiança.

APIs públicas:

- `normalize_temporal(TemporalInput(context, events)) -> TemporalReport | OperationalError`.
- Cada `TemporalClaim` contém `role`, `value: SemanticValue | None`, `format` e `calendar`. Resultado por evento em `NormalizedTemporalEvent`: `claim`, `civil_date`, `local_datetime`, `instant_utc`, `timezone`, `precision`, `fractional_digits`, `calendar_interpretation` e diagnósticos.
- `normalize_geography(GeographyInput(context, locations, scope)) -> GeographyReport | OperationalError`.
- Cada `GeographyLocationClaim` contém papel SQL e componentes opcionais `country_code`, `state_code`, `municipality`, `region`, cada um com prova própria. `NormalizedLocation` preserva o claim, valores, confiança por componente e `municipality_verified=False`; componentes de uma localização não podem vir de linhas estruturais diferentes.
- Confiança do escopo permanece em `report.input.scope.provenance.evidence.confidence`; não se fabrica confiança agregada, calibrada ou certificação de elegibilidade.

O construtor Pydantic usa argumentos nomeados; as assinaturas acima expressam os campos, não uma API posicional. Modelos não permitem extras e herdam `schema_version=2`, sem alterar proveniência SQL versão 1.

## Evidência estrutural e isolamento

Esta milestone introduz um recorte offline de estruturas normalizadas explicitamente rotuladas pelo adaptador. Ele não é uma política de extração por fonte e não flexibiliza o verificador M1 ou o resolvedor M2.1.

São suportados:

1. Escalares filhos diretos da unidade do candidato, com chave igual ao papel semântico: `/record/publication_date`, `/record/geographic_scope` ou `/record/elegibilidade.country_code`.
2. Eventos em `/record/temporal_events/0/value`, cujo objeto contém `role` textual, por exemplo `submission_deadline`.
3. Componentes em `/record/geographic_locations/0/country_code`, cujo objeto contém `role` textual, por exemplo `elegibilidade`.

Em todos os casos exigem-se: candidato, fonte UUID/código, execução e snapshot corretos; unidade exata do candidato; prova já pertencente à afirmação de mesmo papel/valor; nenhuma ambiguidade declarada; pointer válido; quote integral; nó JSON textual exatamente igual ao original; método permitido pelo motor existente e confiança positiva. O papel da evidência é o papel temporal ou `<papel_localizacao>.<componente>`. O papel do objeto da coleção também deve coincidir. Não basta renomear a evidência de publicação para prazo ou mover país da organização para elegibilidade. Booleanos JSON não são texto. Provas de unidades irmãs, pai agregador, execução ou candidato distintos não autorizam valores.

Valores distintos do mesmo papel não são apagados pelo índice de evidências: podem representar conflitos ou múltiplas localizações, que o normalizador deve tornar visíveis. Ambiguidade explicitamente marcada continua bloqueante. Referências interdocumentais são preservadas como contexto, mas não concedem acesso a outro snapshot/unidade. Retificação em documento distinto exige associação futura revisada; não se confia automaticamente em `CrossDocumentReference`.

Um JSON sanitizado pode mentir. O domínio prova consistência entre declaração, estrutura e bytes fornecidos, não a veracidade da fonte nem a correção de um extrator de PDF. DTOs construídos por `model_construct` ou modificados por `model_copy(update=...)` não substituem validação na fronteira; seus recursos Pydantic deliberadamente ignoram validadores. Relatórios recebidos não são autorização de escrita.

## Temporalidade

Papéis distintos: publicação, abertura de submissões, prazo de submissão, prazo preliminar, prazo de proposta completa, resultado, contratação, execução do projeto, validade administrativa e retificação. Um parser nunca decide o papel pela data, por sua ordem, por ser a maior/menor ou pela proximidade de uma palavra.

O formato de interpretação é explícito: ISO, brasileiro, texto português ou não especificado. Somente a gramática ISO suportada é autodeterminante quando `format='unspecified'`; valores com barras sem locale explícito permanecem ambíguos. Brasil: D/M/AAAA ou DD/MM/AAAA, sem adivinhar o século de anos com dois dígitos. Texto português: dia, mês por extenso no vocabulário fechado e ano de quatro dígitos. O calendário de política padrão é gregoriano proléptico; interpretações declaradas como não suportadas ou não especificadas são diagnosticadas. O original e a interpretação ficam na entrada preservada e no envelope. Calendário/formato são declarações do adaptador, não prova de que ele interpretou corretamente uma fonte nativa.

Data civil permanece `date`. Horário ausente não vira 00:00 nem 23:59:59. Timestamp sem offset preserva horário local, mas não gera UTC; offset desconhecido `-00:00` também não significa UTC. A conversão para UTC só é legítima quando o offset é explícito e conhecido. Não há resolução de fusos IANA, abreviações ambíguas ou horário de verão. Precisão lexical é preservada: `day`, `minute`, `second` ou `fractional_second` com `fractional_digits` de 1 a 6. O datetime serializado pode exibir segundos zero e seis casas por representação; isso não aumenta a precisão declarada da fonte. Mais de seis casas, segundos intercalares, 24:00 e offsets com minutos fora de 00–59 não são arredondados/normalizados silenciosamente. Falha de conversão UTC nos limites dos anos 1/9999 preserva o horário com diagnóstico, sem exceção ou invenção de instante.

Prazos preliminar e completo coexistem e não são aliases. Valores conflitantes do mesmo papel permanecem no relatório; não há política de “última data vence”. Retificação tem papel próprio e exige revisão da relação de substituição: nenhuma data de retificação é promovida a prazo, e nenhum prazo anterior é removido automaticamente. Prazo ausente é desconhecido, nunca prova de fluxo contínuo.

## Geografia

Papéis SQL preservados: elegibilidade, execução, beneficiários, origem, organização responsável e não especificado. Origem pode registrar o país da fonte; isso não se transforma em elegibilidade ou escopo. Não se normaliza identidade de organização.

Códigos de país são validados contra catálogo ISO alpha-2 fechado, não somente regex. O catálogo factual de 249 códigos foi extraído em desenvolvimento de iso-codes 4.20.1 (pacote Debian 4.20.1-1); fonte e SHA-256 do JSON de desenvolvimento constam em `geography_catalog.py`. Não há consulta ou leitura desse arquivo no runtime. Uppercase ASCII conserva o significado e o original. Nomes livres e alpha-3 não viram códigos por fuzzy matching. UF usa as 27 siglas brasileiras; região usa as cinco macrorregiões aprovadas. UF não preenche país ausente; país estrangeiro não aceita UF/região brasileira. UF e região explícitas precisam ser coerentes. Não se deriva região ausente de UF enquanto essa política estiver aberta.

Município é texto declarado preservado, não localização resolvida. Sem cadastro/IBGE revisado, nem cidade brasileira nem estrangeira recebe certificação municipal ou coordenadas. Diagnóstico explicita a falta de verificação. Não se encontra município por similaridade textual.

Escopo exige prova própria; sem ela permanece `nao_identificado`, mesmo com fonte `.br`, país BR, UF válida ou sede brasileira. Múltiplos países e locais são mantidos sem escolher país principal. Escopo explicitamente brasileiro versus elegibilidade estrangeira, ou internacional versus elegibilidade brasileira, deve expor contradição. País de origem ou sede estrangeira não é contradição automática com elegibilidade brasileira. Uma lista parcial de países não prova completude ou inexistência de outros elegíveis.

## Auditoria, serialização e limites

Versão comum `m2.2a-semantics-v1`; limites `m2.2a-normalization-limits-v1`. O envelope vincula SHA-256 dos bytes UTF-8 exatos de `model_dump_json(exclude={'audit'})`, incluindo entradas, contexto, versões, valores normalizados, papéis, precisão e diagnósticos ordenados. O envelope recebido é comparado integralmente com o esperado; divergência é erro de validação, não recálculo silencioso. Sem envelope, um novo é calculado, sem autenticação. Hash não é assinatura. Não há dependência da ordem de chaves de um JSON canônico universal nem garantia entre versões de serializador não exercitadas.

Limites compartilhados: 1.200 claims, 1.200 afirmações por candidato, 2.400 ocorrências de evidência e 64 por campo (incluindo repetições/nulos, como M1.1a); 32 snapshots; 8 MiB agregados de payload UTF-8; 1 Mi caracteres dos valores de entrada; 1.000 referências. Cada payload mantém os limites de `safety.parse_payload` (2 MiB, profundidade/nós/números limitados). Excedentes produzem `OperationalError(normalization_limits_exceeded, stage='normalization')`, sem truncamento ou decisão. Snapshot duplicado e JSON inválido têm códigos próprios. Esses limites não são orçamento completo de transporte/metadados: DTOs já existem na chamada. Índices e parsing são feitos uma vez por contexto, não por claim.

Determinismo significa igualdade de DTOs/JSON completos para a mesma entrada validada. Round-trip não transforma tipo, papel ou confiança. Idempotência de valores canônicos é verificada no domínio normalizado suportado: data ISO permanece data ISO e código já canônico permanece o mesmo código. Não se passa um relatório arbitrário como entrada bruta ou se troca original/evidência para simular idempotência. Formatos de origem diferentes podem ter o mesmo valor civil sem possuir o mesmo histórico/audit digest.

## Compatibilidade e decisões pendentes

M1.1a e M2.1 não são modificados. Não há conversão automática dos novos eventos/localizações em `FieldAssertion` canônico aceito pelo Validation Engine. O motor antigo continua podendo diagnosticar campos novos como não suportados; normalização não substitui validação/autorização.

A migration 000001 contém um único `prazo_submissao date`, além de publicação, abertura e resultado civis. Não suporta múltiplas etapas, hora/offset/precisão, relações de retificação e todas as classes temporais desta milestone. O domínio offline preserva isso sem perder informação e sem fabricar uma nova tabela `oportunidade_evento` (adiada na baseline). O SQL tem localizações 1:N, mas não representa certificação municipal, catálogo/versionamento, papéis adicionais ou proveniência componente a componente nos mesmos campos deste DTO. Não há mapper nem JSONB de conveniência para contornar contratos.

Continuam abertos: timezone/corte de prazo e status temporal; política autenticada de retificação e precedência; projeção de múltiplas etapas no contrato persistido; semântica e catálogo real por fonte; cadastro municipal/IBGE; derivação/persistência de região; governança e atualização dos códigos ISO; autenticidade/cadeia de custódia; orçamento de transporte; integração/promoção revisada; conjunto ouro e matriz completa Python. Nenhum item aberto é resolvido por default oculto nesta milestone.

M2.2a encerra no domínio offline, com revisão independente final aprovada após correções das invariantes dos DTOs temporais (ver EDITALFINDER_V2_M22A_RESULTADOS.md). Aguarda revisão técnica do usuário. Não inicia M2.2b.

## Correção dirigida M2.2a.1

A revisão posterior `EDITALFINDER_V2_M22A_REVISAO_INDEPENDENTE.md` identificou duas lacunas adicionais; o parecer anterior acima é histórico, não aprovação desta correção.

No DTO público `NormalizedTemporalEvent`, offset explícito conhecido com datetime aware exige `instant_utc` presente, de offset zero e correspondente ao horário local sempre que a conversão for representável. O construtor não calcula campos ausentes nem repara inconsistências. Se a conversão UTC ultrapassa os anos Python 1–9999, preserva-se integralmente `local_datetime`, sem `instant_utc`, somente com diagnóstico local `temporal_timezone_conversion_out_of_range`. O código é obrigatório nesse estado e rejeitado fora dele; um diagnóstico geral do relatório não substitui o diagnóstico do evento. Ausência de timezone e `-00:00` continuam exigindo horário naive e nenhum instante UTC. Data civil não ganha horário.

Uma localização é vazia quando os quatro componentes do claim (`country_code`, `state_code`, `region`, `municipality`) são todos ausentes, não quando um componente fornecido falhou em normalizar. Cada claim vazio recebe `geo_location_empty` no local e no relatório, com seu `claim_index`. O claim completo, papel e entrada permanecem no envelope auditado. Sem componentes não há prova componente a componente; `evidence=()` não inventa prova nem usa a prova de escopo, da fonte ou de outra localização. Escopo é uma afirmação separada: sua presença não preenche o local vazio, e escopo sem qualquer claim de localização continua usando `geo_locations_missing`, não `geo_location_empty`. UF sem país continua diagnosticada por conflito, nunca inventa BR; país isolado e município estrangeiro acompanhado de país permanecem suportados.

São ajustes de validação e diagnóstico da política conservadora existente, sem nova arquitetura, inferência, projeção persistida, promoção ou mudança dos identificadores de versão. JSONs temporais antigos inconsistentes passam a ser rejeitados deliberadamente. Relatórios geográficos reprocessados com claims vazios terão diagnóstico e digest diferentes; envelopes históricos não são silenciosamente reescritos. Limitações de auditoria e APIs Pydantic que ignoram validação permanecem as documentadas acima. Resultados e escopo efetivamente verificados constam em `EDITALFINDER_V2_M22A1_RESULTADOS.md`.
