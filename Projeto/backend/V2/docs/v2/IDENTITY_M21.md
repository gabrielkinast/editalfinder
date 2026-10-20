# M2.1 — Identidade determinística offline

Status: contrato implementado para comparação offline; sujeito a revisão técnica. Não é autorização para merge, publicação, persistência ou M2.2.

## Autoridades e fronteira SQL

Foram inspecionados DECISIONS_V1.md, DATA_CONTRACT.md, SCHEMA_DESIGN_V1.md, MIGRATION_PLAN.md, MIGRATION_000001_VALIDATION.md e a definição SQL original da V2. A documentação histórica de decisões abertas não reabre escolhas posteriores aprovadas. O schema Legacy `backend/database/schema_current.sql` foi inspecionado em modo texto: `edital.id_edital` bigint e UNIQUE(link) não são contratos da V2.

Decisões aprovadas: UUIDs internos; fonte distinta de organização; identificadores externos com tipo/namespace/fonte/valor; N:N item–oportunidade; hash para conteúdo/auditoria, não identidade universal; ausência de fuzzy merge. A solicitação M2.1 restringe o antigo fluxo conceitual que começava pela URL: URL sozinha não estabelece identidade de oportunidade.

A migration imutável `20260717_000001_editalfinder_v2_initial_schema.sql:261–283` define `oportunidade_identificador`:

- tipo_identificador text NOT NULL; CHECK url_canonica, identificador_oficial, identificador_fonte.
- namespace text NOT NULL; CHECK btrim(namespace) <> ''.
- fonte_id uuid NOT NULL; FK fonte(id), ON DELETE RESTRICT.
- valor_normalizado text NOT NULL; CHECK btrim(valor_normalizado) <> ''.
- oportunidade_id uuid NOT NULL; FK oportunidade(id), ON DELETE CASCADE.
- valor_original text nullable.
- criado_em timestamptz NOT NULL DEFAULT now().
- PK (tipo_identificador, namespace, fonte_id, valor_normalizado).

Não há coluna de ciclo, versão de normalização ou evidência detalhada nessa chave. Não há UNIQUE direto em oportunidade.url_oficial. O domínio preserva original obrigatoriamente, embora SQL permita NULL. Nenhum mapper ou contrato novo de banco foi criado. Reuso de uma chave em ciclos distintos é diagnosticado, não contornado anexando ano ao valor/namespace. Isso bloqueia uma futura persistência ingênua: dois ciclos não podem ser gravados como donos diferentes da mesma PK sem decisão arquitetural e eventual migration futura separada.

## Sete identidades separadas

1. Fonte: candidate.source_id UUID e source_code; fonte não é organização nem hostname.
2. Execução: snapshot.execution_id UUID; não é ciclo de publicação.
3. Snapshot: RawSnapshot.id UUID e envelope dos bytes de payload_json; duas coletas podem ter o mesmo conteúdo.
4. Documento: DocumentUnit(snapshot_id, pointer) delimita uma unidade estrutural em um snapshot. claimed_document_id é uma declaração opcional de identidade documental estável fornecida pelo chamador, não inferida. Igualdade de UUID documental serve somente para apontar conflito potencial, não para provar uma oportunidade.
5. Identificador externo: ExternalIdentifier preserva original, tipo, namespace opaco, fonte, versão e proveniência. NormalizedIdentifier acrescenta valor normalizado, diagnóstico e transformações verificadas contra o original.
6. Oportunidade: claimed_opportunity_id é UUID declarado, nunca derivado de título, hash ou URL; não é capacidade de escrita.
7. Ciclo: PublicationCycle preserva rótulo original e normalizado idêntico, namespace próprio, versão cycle-exact-v1 e evidência. Não infere ano, período, programa pai ou continuidade a partir de datas, execução ou URL.

Os modelos herdam Contract imutável Pydantic V2, extra=forbid, schema_version=2. As políticas da M2.1 têm versões próprias; envelopes M1.1a não foram modificados.

## Normalização de identificadores

- opaque-exact-v1 é default para identificadores não URL: igualdade literal. Não altera maiúsculas, espaços, pontuação, zeros ou largura Unicode.
- opaque-nfc-v1 é opção explícita: somente equivalência canônica Unicode NFC; original preservado. Não aplica NFKC, remoção de acentos, transliteração ou casefold. A opção não constitui aprovação da semântica de um namespace real.
- url-conservative-v1 é obrigatório para tipo url_canonica e incompatível com os outros tipos.
- Valores vazios/brancos, caracteres de controle/formatação/surrogates e valores acima de 8.192 caracteres não geram chave utilizável. Tipos/versões desconhecidos são recusados no contrato.

Normalização não autentica a origem. Um identificador sintaticamente válido não é automaticamente usado pelo resolvedor. O valor normalizado recebido é recalculado e comparado ao original e à política na fronteira Pydantic; não pode ser forjado mantendo o restante do DTO.

## URLs: política conservadora

API: normalize_url(value, tracking_policy='preserve-v1'). Resultado preserva original, normalized opcional, código, normalization_version, tracking_policy e sequência de transformações com before/after. Não faz rede, DNS, redirecionamento ou verificação de oficialidade.

Normalizações executadas: reconhecimento de esquema HTTP(S) estritamente ASCII, esquema e hostname em minúsculas; IDN com round-trip conservador; IPv6 válido; remoção de porta default de seu próprio esquema; portas alternativas preservadas; escapes percentuais com hex maiúsculo. HTTP e HTTPS continuam distintos. Não se faz resolução de dot-segments ou remoção de slash. Escapes de caracteres reservados não viram delimitadores. Caminhos e valores de query não passam por NFC/NFKC.

A implementação preserva ordem e multiplicidade da query, nomes/valores vazios e diferença entre '+' e '%20'. Não ordena parâmetros arbitrariamente. Preserva todos os fragments, inclusive SPA/hashbang e marcadores vazios, porque sua irrelevância não foi aprovada por fonte. Hostname com ponto final não perde esse ponto silenciosamente.

Tracking é opt-in: drop-known-tracking-v1 reconhece somente os nomes literais case-sensitive utm_source, utm_medium, utm_campaign, utm_term e utm_content. Não há remoção por prefixo utm_, percent-decoding do nome, remoção de id/edital/chamada ou de parâmetros arbitrários. O resolvedor usa preserve-v1; políticas diferentes de tracking não são misturadas implicitamente em chaves de identidade.

IDNA stdlib pode mapear caracteres de forma irreversível (por exemplo ß para ss). Esses casos são ambíguos e não devem colidir silenciosamente: retornam url_ambiguous_idna. Credenciais, controles (inclusive escapes C0/DEL/barra invertida), formatação Unicode invisível no sufixo, percent encoding inválido, host/porta inválidos e URLs fora do domínio HTTP(S) são recusados. Texto com surrogate isolado não pertence ao domínio UTF-8 de Contract: gera ValidationError na fronteira em vez de um DTO impossível de serializar. URLs malformadas em texto Unicode válido preservam o original e retornam diagnóstico estruturado. Limites e demais detalhes executados estão no módulo e nos testes. Isto não é uma política SSRF nem promessa de equivalência para todos os servidores.

Preservações deliberadas produzem falsos negativos, não são bugs: queries reordenadas, %7E versus ~, slash final, fragment, caminhos com dot-segments, esquema diferente e parâmetros desconhecidos podem continuar distintos. Idempotência vale para o valor normalizado no domínio suportado, não significa que históricos de originais diferentes sejam iguais.

## Evidência e resolução

API: resolve_identity(left: IdentitySubject, right: IdentitySubject) -> IdentityResolutionReport | OperationalError.

O resolvedor verifica cada prova contra o candidato e snapshot efetivamente fornecidos: candidate_id, source_id/código da fonte, execution_id, snapshot_id, unidade, papel semântico, pointer estrutural direto, quote integral e igualdade do escalar no payload. O nó JSON de identidade deve ser str: booleanos true/false não comprovam as strings "true"/"false". O suporte booleano do Validation Engine M1.1a permanece intacto. A evidência deve já pertencer à afirmação daquele candidato, sem ambiguidade ou valores tipados conflitantes. Não basta citar um trecho ou relabelar um título.

Recorte estrutural suportado: official_identifier, source_identifier, official_url e publication_cycle como filhos escalares diretos da unidade do candidato, com role igual ao campo. Não há parsing/extrator de documentos nativos ou interpretação semântica por fonte. Nomes diferentes/listas exigem um futuro adaptador explicitamente revisado. Declarações de namespace e UUIDs continuam não autenticadas. Os resultados exprimem relações condicionais entre os contextos e bytes fornecidos, não certificam a verdade do publicador.

Chave em memória: (tipo, namespace literal, fonte UUID, versão de normalização, valor normalizado). A versão adicional não é uma nova PK SQL.

Ruleset m2.1-identity-v1:

- exact_match / official_identifier_cycle_match: chave oficial contextual comum, mesma fonte coerente, ciclos explícitos iguais no mesmo namespace, provas válidas e ausência de conflito comparável. Suporta URLs/documentos diferentes para a mesma declaração de oportunidade/ciclo. Nunca promove ou faz merge.
- no_supported_match / source_scope_differs: não há política de equivalência entre fontes.
- no_supported_match / namespace_scope_differs: autoridades diferentes não são aliases por terem o mesmo valor.
- no_supported_match / normalization_policy_differs: versões não comparáveis não geram igualdade silenciosa.
- no_supported_match / official_identifiers_differ: nenhum identificador oficial contextual comum; não afirma que oportunidades reais sejam necessariamente distintas.
- insufficient_information / official_identifier_missing ou publication_cycle_missing: não infere identidade/ciclo a partir de URL ou identificador de item da fonte.
- insufficient_information / cycle_namespace_differs: rótulos de ciclos de autoridades diferentes não são comparáveis.
- insufficient_information / identity_evidence_invalid: prova não pertence ao valor/contexto/role declarado. Mantém entradas no relatório para diagnóstico.
- conflict / source_context_conflict: mesmo UUID de fonte declara códigos diferentes.
- conflict / document_identifier_conflict: registros aparentemente associados por documento, URL, identificador comum ou UUID de oportunidade declarado divergem em identificadores oficiais comparáveis.
- conflict / opportunity_claim_conflict: chave oficial e ciclo iguais declaram UUIDs de oportunidade incompatíveis.
- distinct_cycles / distinct_publication_cycles: rótulos explicitamente diferentes no mesmo escopo de ciclo. Reuso de chave/URL gera também conflito contextual_key_reused_across_cycles para expor a limitação SQL.
- url_is_not_opportunity_identity registra a URL comum apenas como localizador.

A ordem dos gates é conservadora: entrada operacional inválida ou prova inválida impede decisões posteriores; escopos de fonte/namespace não comparáveis não recebem match; ausência de informação obrigatória permanece explícita. Não se resolve conflito por ordem, confiança, título, organização, país, domínio ou hash. Não existe grafo/transitividade/union-find que faça um terceiro registro unir conflitos indiretamente.

## Auditoria e limites

IdentityResolutionReport retém ambos os subjects completos, identificadores normalizados, decisão, diagnósticos, conflitos e provas. IdentityAudit usa SHA-256 dos bytes UTF-8 exatos de model_dump_json(exclude={'audit'}), hash_version=identity-pydantic-json-utf8-v1. O envelope retido divergente é recusado. Sem envelope, um novo é calculado. Isso não autentica o relatório. promotable é sempre False.

Limites operacionais m2.1-identity-limits-v1 por subject: 10.000 identificadores, 10.002 afirmações, 30.000 evidências nas afirmações, 32 snapshots, 8 MiB agregados de payload UTF-8, 1 Mi caracteres agregados nos valores originais e 1.000 referências interdocumentais preservadas. Cada JSON continua sujeito aos limites M1.1a de safety.py. Excedentes retornam identity_limits_exceeded; snapshot duplicado/JSON inválido retornam identity_duplicate_snapshot_id / identity_invalid_snapshot_json. UUID de snapshot compartilhado entre os dois subjects com bytes ou metadados diferentes bloqueia a resolução como identity_snapshot_context_conflict; recapturas reais devem ter UUIDs de snapshot distintos. OperationalError não possui decisão semântica.

Esses limites não são orçamento completo de transporte/memória: DTOs já existem na chamada e metadados/atestados externos exigem orçamento na fronteira futura. Não alteram os limites menores do Validation Engine M1.1a. Um input de benchmark aceito pelo resolvedor pode exceder o orçamento do validador semântico; identidade não substitui validação nem a habilita.

Índices/set membership evitam produto cartesiano de identificadores; ordenar testemunhas usa O(K log K). Serialização/hash são proporcionais ao tamanho dos dados preservados, não O(1). Duplicatas são preservadas no relatório; só a busca usa primeira testemunha por chave. Nenhuma evidência é expandida para todas as combinações de identificadores.

## Decisões ainda não aprovadas

- Governança/autorização dos namespaces reais e semântica de oficialidade/acionabilidade por fonte.
- Equivalência cross-source, aliases de identificadores e equivalência cross-namespace.
- Vocabulário e granularidade dos ciclos reais, chamadas contínuas/recorrentes e relações pai/filho.
- Política de persistência para reuso de URL/identificador entre ciclos em conflito com a PK existente.
- Identidade documental estável entre snapshots e prova de associações N:N em documentos nativos.
- Autenticidade da revisão, autorização e referência externa do digest; não há assinatura/cadeia de custódia.
- Regras source-specific para fragments, ordenação de query, tracking adicional, redirects e equivalência de URLs.

Consequências: o motor pode deixar equivalências reais não resolvidas; não é um deduplicador de produção nem um mecanismo de escrita. Resolver essas questões exige revisão arquitetural/técnica separada, sem alterar migrations ou habilitar promoção nesta milestone. M2.2 não foi iniciado.
