# M2.3b — Consistência semântica offline

## Fronteira e API

`integration_consistency.evaluate_consistency(candidate_input, normalized_results,
validation_result) -> tuple[IntegrationDiagnostic, ...] | OperationalError`.

Função pura, sem relógio, rede, catálogos externos, normalização adicional ou
mudança de decisão M1. Consome relatórios já produzidos pelos componentes aprovados.
Não é uma segunda fronteira de autenticação de relatórios arbitrários: somente
`IntegrationReport` recomputa TODO o pipeline e verifica outputs e auditoria.
`model_construct`/`model_copy(update=...)` continuam escapes de código confiável.

A função aplica `prepare_context` ANTES de construir inputs auxiliares/índices.
Falhas operacionais de preflight retornam o OperationalError original, nunca
REJECTED nem um falso sucesso semântico. O orquestrador preserva esse slot.
Contextos/inputs de relatórios e IDs de erros devem coincidir com o candidato atual.
Um desacordo aborta as observações de relações, sem citar provas estrangeiras.

Os normalizadores existentes são a única autoridade de parsing/mapeamento lexical.
`PreparedContext.matches` e `matches_m22b` são reutilizados para citar provas locais.
Decisões, papéis, originais, normalizações e comparações de identidade não mudam.
Não há projeção de M2 em assertions M1, merge ou promoção.

## Contratos dos diagnósticos

`version=m2.3b-consistency-v1` versiona este conjunto explícito de regras. O código
estável identifica a regra/observação dentro dessa versão. Não há framework de
configuração, regras registráveis ou categorias financeiras novas.

São obrigatórios no diagnóstico recebido: code, message, domain, classification,
domains, claim_references, normalization_versions, evidence, version. Mesmo tuplas
vazias são explícitas; não há default de versão/estado/metadados. O schema_version
segue o contrato geral 2; claim_indices legado continua vazio e não é usado.

`DomainClaimReference(domain, claim_index)` referencia o input DESTE candidato:

- temporal: `CandidateIntegrationInput.temporal`;
- geography: `CandidateIntegrationInput.geography`;
- financial: `CandidateIntegrationInput.financial`;
- organizations: `CandidateIntegrationInput.organizations`;
- taxonomy: `CandidateIntegrationInput.taxonomy`;
- validation: `context.candidate.assertions`;
- geographic_scope: singleton `CandidateIntegrationInput.geographic_scope`, índice 0.

Índices de domínios distintos jamais são intercambiáveis. `domains` lista domínios
afetados, enquanto `domain=integration` identifica o produtor das observações.
`NormalizationVersionReference` registra versões dos relatórios efetivamente
consumidos, política e catálogo solicitado quando relevante. Um catálogo solicitado
mas não suportado não se torna aprovado por aparecer nessa referência. Domínio em
falha operacional não ganha uma normalização fictícia.

Modelos congelados e tuplas não introduzem metadata mutável. Provas continuam
IdentityEvidence, com candidato, fonte, execução, unidade e pointer originais.
Claims sem prova válida podem ser referenciados como NÃO avaliáveis, mas sua prova
rejeitada/estrangeira não entra em evidence. O input completo preserva o material
recebido, inclusive declarações que falharam.

## Estados

- contradiction: incompatibilidade no recorte explicitamente suportado por regra;
- potential_conflict: aparência incompatível, faltando vínculo/contexto necessário;
- insufficient_information: relação, interpretação ou classificação não estabelecida;
- no_conflict_detected: nenhuma observação específica foi produzida pelas regras
  implementadas; NÃO certifica consistência total, ausência de alertas nos relatórios
  de domínio, elegibilidade ou acionabilidade.

Contradição não significa REJECTED. Nenhum destes estados altera M1.

## Regras, na ordem de execução

Todas exigem preflight local bem-sucedido e inputs/relatórios vinculados ao candidato.
Fora das precondições, não há relação inferida. Exceções deixam a relação sem
resolução e/ou permanecem nos relatórios anteriores; não são tratadas por fallback.

### 1. Fronteira/contexto e disponibilidade

- `consistency_context_mismatch`: relatórios/erros atribuídos a outro input/candidato;
  insufficient_information global, sem claims/provas/versionamento estrangeiros.
- `consistency_domain_unavailable`: OperationalError de domínio ou M1 preservado
  em seu slot; insufficient_information daquele domínio, sem falsa versão normalizada.
- `consistency_claim_evidence_unavailable`: claim temporal/financeiro/taxonômico sem
  prova local aceita, inclusive valor temporal/financeiro ausente; insufficient_information,
  referência exata e nenhuma prova rejeitada copiada. Não infere valores do claim.

### 2. Temporalidade

- `consistency_temporal_stage_unverified`: reutiliza avisos de prazos divergentes
  do normalizador temporal e cita TODOS os eventos aceitos daquele aviso. Datas
  civis entre si ou instantes UTC entre si: potential_conflict. Mistura de precisões,
  timezone desconhecido/ausente ou instante irrepresentável: insufficient_information.
  O papel igual NÃO identifica etapa igual. Não há contradição temporal definitiva.
- `consistency_temporal_window_unverified`: exatamente uma abertura e um deadline
  genérico, ambos com prova local, sem claims de fases preliminar/completa. Ordem
  aparentemente reversa em datas civis comparáveis ou instantes UTC comparáveis:
  potential_conflict, pois falta identidade da janela. Valores não comparáveis:
  insufficient_information. Ordem normal não gera aviso, mas não prova janela comum.
- `consistency_rectification_precedence_unverified`: retificação com prova local;
  insufficient_information, com referências ordenadas a ela e a todos os deadlines
  locais. Não escolhe maior prazo, precedência, alvo nem substituição. Mesmo com
  só uma retificação não há alvo inventado.

Exceções intencionais: várias fases/janelas, documentos independentes, cutoffs e
vínculos de retificação exigem contratos futuros. O TemporalClaim atual não tem
stage_id/window_id. Não interpretar objeto de coleção como identidade de fase.
Datas M2 não passam a alimentar status temporal M1; nenhuma expiração é inventada.

### 3. Geografia

- `consistency_geographic_scope_relationship_unverified`: aviso geo_scope_conflict
  existente, scope literal e país de elegibilidade verificados. Cita scope singleton
  e localização específica. Resultado insufficient_information, NÃO conflito:
  escopo genérico não estabelece exclusividade de elegibilidade. Internacional
  pode incluir brasileiros; a semântica do aviso anterior permanece preservada.

Origem, organização, publicação, execução e beneficiários não viram elegibilidade.
Sem prova adequada, não comparar. Não há lookup municipal, default BR, inferência
por idioma/moeda/domínio ou restrição derivada de sede.

### 4. Organizações

- `consistency_organization_identity_unverified`: reutiliza somente testemunhas
  organization_comparable_identifier_conflict do relatório aprovado. Índices e
  provas exatos dos dois claims; insufficient_information. Comparabilidade de
  identificador não demonstra que ambos declaram a mesma entidade jurídica ou
  cardinalidade exclusiva. Múltiplos financiadores continuam legítimos.

Não há nova regra de identidade, CNPJ/namespace/cadastro ou comparação de nomes.
Compartilhamento de chave, sigla ou papel não autoriza merge. Checksum não prova
existência. Contradição definitiva entre identidades exigiria vínculo de entidade
verificado e cardinalidade aprovados, inexistentes nos inputs atuais.

### 5. Finanças

- `consistency_financial_interpretation_unresolved`: valor ausente ou interpretação
  normalizada com limitações/códigos, exceto texto de despesas suportado e faixa
  reversa tratada abaixo. insufficient_information; não faz parsing próprio.
- `consistency_financial_range_contradiction`: UMA expressão com prova local,
  interpretação normalizada e código financial_range_reversed do normalizador.
  contradiction DA FAIXA DECLARADA sob formato/unidade/moeda fornecidos; não afirma
  veracidade da fonte ou autenticação dessas declarações. Usa os dois endpoints
  da mesma expressão, não inventa relação entre dois instrumentos/claims.
- `consistency_financial_bounds_scope_unverified`: proposta mínima/máxima com um
  Decimal cada, sem códigos de limitação, mesma moeda conhecida e mesma unidade.
  Usa maior mínimo e menor máximo como testemunhas de uma condição existencial,
  sem produto cartesiano. Se mínimo > máximo: potential_conflict, nunca contradiction,
  pois falta identidade comum de instrumento/proposta/tranche. Não enumera todos
  os pares. Empates preservam a primeira testemunha na ordem de entrada.
- `consistency_financial_bounds_not_comparable`: há mínimos/máximos resolvidos,
  mas classes de moeda/unidade não têm correspondência. Cita representantes
  não pareados, insufficient_information. Não compara magnitude nem converte.

Orçamento, teto por proposta, bolsa mensal/individual, contrapartida, contribuição,
percentual, prêmio e custo estimado permanecem distintos. Valores negativos ou
percentuais fora do suporte continuam com seus avisos anteriores, sem inventar
nova contradição entre domínios. Não há soma, subtração, divisão, câmbio, valuation,
equity, principal de crédito, juros ou parcelas derivados de outros papéis.

### 6. Taxonomia e relação com finanças/M1

- `consistency_taxonomy_unsupported`: classificação local unknown/ambiguous;
  insufficient_information, preservando original, resultado e catálogo. Não há
  palavra-chave/NLP, alias nem fallback outra/misto/nao_identificado/multidisciplinar.
- `consistency_taxonomy_not_actionability`: pelo menos um código mapeado e
  content_kind textual news/result com prova direta aceita em assertion M1.
  Cita claims taxonômicos e assertions M1 qualificados separadamente;
  insufficient_information. Categoria conhecida não torna notícia/resultado
  acionável nem supera decisões/issues M1. Não classifica prosa por palavras.
- `consistency_hybrid_relationship_unverified`: classificações resource_type
  verificadas de financiamento_nao_reembolsavel e credito/financiamento_reembolsavel.
  insufficient_information sobre a relação; cita todas as classificações relacionadas.
  Híbrido não é contradição nem categoria nova. Valores não são ligados por inferência.
- `consistency_credit_terms_unrepresented`: resource_type credito ou
  financiamento_reembolsavel mapeado e verificado. insufficient_information:
  FinancialRole não representa principal de crédito/juros/garantia/carência/prazo.
  Não rebatiza orçamento, aporte ou prêmio como empréstimo. Expressões diretas
  credit_principal continuam preservadas no candidato M1, sem projeção financeira.

Investimento/equity/venture capital não têm categorias suficientes no seeds-000002.
Classificações não suportadas permanecem desconhecidas com original preservado.
Dados já suportados, como custo estimado em moeda explícita, podem ser normalizados
sem transformar equity em empréstimo ou inferir ownership/valuation.

### 7. Resumo limitado

- `consistency_no_conflict_detected`: somente na ausência de observações anteriores.
  Estado no_conflict_detected, sem prova/claim inventado, versões disponíveis registradas.
  Não agrega um selo de aprovação nem apaga diagnósticos dos normalizadores/M1.

## Recursos e integridade

Admissão de integration_budget continua em 64 MiB, com a MESMA fórmula e versão
m2.3a.1-output-budget-v1. Não foi aumentada nenhuma capacidade anterior.
O multiplicador de corpo 16, reserva de campo 16 * máximo de assertions de mesmo
campo e reserva fixa de 64 KiB já incluem outputs/diagnósticos/auditorias. As novas
provas temporais/taxonômicas aparecem em no máximo três observações adicionais por
claim; financeiras em uma. Repetições de scope e testemunhas organizacionais são
cobradas pelo fan-out de campo existente. Referências pequenas/versões/mensagens
cabem nas reservas conservadoras de corpo/fixo; não há snapshots nos diagnósticos.
Os testes controlam wire_cost e saída serializada contra a projeção, inclusive 24
observações admitidas perto do limite de admissão, sem alocar GiB.

Percursos de claims são lineares, salvo trabalho já existente nos normalizadores,
parsing/hash e comprimentos de strings. Avisos de deadlines têm no máximo três
papéis/grupos; os índices de limites monetários têm no máximo nove classes
moeda/unidade. Não há cartesiano entre domínios. Testemunhas limitadas representam
condições existenciais explicitamente documentadas; nunca truncamento de saída.

As observações inteiras entram no corpo do IntegrationReport e em seu digest.
Revalidação Python/JSON recompõe normalizadores, M1, observações e identidade na
ordem original. Omissão, reordenação ou adulteração é recusada mesmo sem audit.
Envelopes IntegrationAudit continuam exigindo seus seis campos explicitamente.
Relatórios antigos com diagnostics vazio precisam de reprocessamento explícito de
input sob a nova versão de consistência; não houve alteração/migração automática
dos registros originais. O caminho histórico de M2.3a.2 continua disponível, com o
novo resultado completo arquivado separadamente e suas versões por diagnóstico.

64 MiB é orçamento equivalente de trabalho/saída, NÃO teto de RSS. JSON é decodificado
antes de validators Pydantic; transporte deve impor seus próprios limites. Chamar a
função de observações diretamente não equivale a admitir um IntegrationReport nem
a autenticar um DTO recebido: a fronteira completa é integrate/IntegrationReport.

Sem conjunto ouro real, autenticação de fontes/revisores, políticas por fonte,
catálogo de investimento ampliado ou vínculos de fase/instrumento/entidade, não há
certificação semântica de oportunidades reais, autorização de publicar ou promoção.
