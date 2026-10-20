# M2.2b — Normalização financeira, organizacional e taxonômica offline

## Autoridade, limites e arquitetura

Esta etapa não classifica acionabilidade, não substitui o Validation Engine M1 e não concede autorização de escrita. Os três subsistemas são independentes: não fazem conversão cambial, projeção SQL, resolução de oportunidades ou associação automática de organizações. Não consultam relógio, filesystem, rede, banco ou modelos de linguagem em runtime. Entradas são contratos imutáveis; saídas preservam cada claim e o contexto completo. `promotable` permanece False.

Autoridades: DECISIONS_V1, DATA_CONTRACT (proposta histórica), SCHEMA_DESIGN_V1, migrations 000001/000002 e respectivas validações (lidas apenas como texto), políticas M1 e contratos M2.1/M2.2a/M2.2a.1. Decisões posteriores prevalecem sobre propostas superadas. As migrations e os contratos anteriores não foram alterados.

O SQL só representa um mínimo/máximo monetário não negativo `numeric(18,2)` e moeda; não representa todos os papéis, faixas/precisões, percentuais ou despesas elegíveis desta etapa. Não há conversão automática para essas colunas. A tabela `organizacao` possui UUID, código editorial opcional e nome, mas não cadastro CNPJ nem tabela de identificadores organizacionais. Os identificadores M2.1 são de oportunidade, não certificados de entidade jurídica. DTOs novos preservam informações offline sem inventar migrations ou FKs. Catálogos taxonômicos continuam administráveis, não enums SQL novos.

## Fronteira comum M2.2b

`m22b_common.py` reutiliza `Contract`, `SemanticValue`, `IdentityEvidence`, `NormalizationContext`, `NormalizationDiagnostic`, `PreparedContext`, `prepare_context`, parsing e verificação de evidências existentes. Acrescenta somente as coleções de adaptador `financial_claims`, `organization_claims`, `taxonomy_claims`; não amplia a API dos normalizadores M2.2a.

Esquemas estruturais suportados:

- Escalar filho direto da unidade do candidato, chave igual ao papel: `/record/program_budget` ou `/record/area`.
- Componente filho direto com chave `<papel>.<componente>`, por exemplo `/record/funding.name`.
- Coleção de objetos rotulados: `/record/financial_claims/0/value`, `/record/organization_claims/0/name`, `/record/taxonomy_claims/0/value`, com `role` explícito e correspondente no mesmo objeto. O índice de coleção usa gramática ASCII sem zeros iniciais. Componentes organizacionais devem permanecer no mesmo objeto.

Exigem-se pertencimento prévio da prova à afirmação do candidato, candidato/fonte/execução/snapshot/unidade coerentes, papel correto, quote integral, nó JSON textual igual ao original e método/confiança aceitos pelo motor existente. Booleanos JSON não provam texto. Não basta uma palavra em notícia, prova de outra linha, fonte ou nome de domínio. Isso verifica vínculo com a estrutura fornecida, não autenticidade da fonte ou extração de PDF. Formato, unidade e namespace declarados pelo adaptador não são autenticação de autoridade jurídica/semântica.

`prepare_m22b` indexa o contexto uma vez por requisição e aplica o orçamento de claims/componentes e texto antes de normalizar. Limites: 1.200 claims e no máximo 1.200 valores componentes; 8.192 caracteres por valor e metadado textual; 1 Mi caracteres agregados. Reutiliza limites M2.2a/M1.1a: 1.200 afirmações, 2.400 ocorrências de evidência, 64 por campo, 32 snapshots, 8 MiB de payload UTF-8 agregado, 1.000 referências. O parser de payload mantém limites próprios. Excedentes retornam `OperationalError(code='normalization_limits_exceeded', stage='normalization')`, sem truncamento; snapshot duplicado e JSON inválido mantêm códigos estruturados existentes. Limites financeiros adicionais e semântica de catálogos são descritos abaixo. Esses limites não substituem orçamento futuro de transporte ou construção de DTOs já existentes em memória.

`M22BReport` e `M22BAudit` introduzem `policy_version='m2.2b-semantics-v1'` e `limits_version='m2.2b-normalization-limits-v1'`. O SHA-256 cobre os bytes UTF-8 exatos de `model_dump_json(exclude={'audit'})`, incluindo entrada, originais, provas, saídas, versões e diagnósticos ordenados. O envelope recebido divergente é rejeitado; ausência de envelope permite calcular um novo, sem autenticação. Hash não é assinatura. Não há JSON canônico universal nem certificação de versões de serializador não executadas. `model_construct` e `model_copy(update=...)` são escapes Pydantic sem validação e não substituem validação na fronteira.

## Decisões conservadoras

- Papéis financeiros não são aliases: orçamento de programa não preenche valor máximo por proposta, nem bolsa mensal vira bolsa total. Sem soma automática ou câmbio.
- Moeda ausente permanece ausente; convenção decimal deve ser explícita quando ambígua. Não há arredondamento silencioso.
- Nome normalizado é apresentação, não prova de identidade; siglas, semelhança ou domínio comum não autorizam merge. Validade de dígitos de CNPJ não prova existência real.
- Taxonomia só normaliza códigos exatos já aprovados em dimensão explícita. Não cria aliases, defaults amplos ou classificador por palavras. `bolsa` existe nas duas dimensões e não autoriza escolher uma sem contexto. Notícia ou resultado não se torna oportunidade por mencionar um código conhecido.
- Catálogo base `seeds-000002`: oito tipos de oportunidade, nove tipos de recurso, quinze áreas, reutilizados de `policies.py`. Atualização real de catálogo ou aprovação de aliases exige política/revisão futura, não tabela arbitrária enviada pelo chamador.

## API financeira

`normalize_financial(FinancialInput) -> FinancialReport | OperationalError`. Cada `FinancialClaim` declara `role`, `value` opcional, `format`, `currency` opcional e `unit`. Papéis fechados desta política: `program_budget`, `proposal_maximum`, `proposal_minimum`, `individual_scholarship`, `monthly_scholarship`, `counterpart_contribution`, `applicant_contribution`, `funding_percentage`, `eligible_expenses`, `award_amount`, `estimated_project_cost`. O papel é preservado e não inferido pelo número.

Formatos explícitos: `brazilian` (ponto de milhar/vírgula decimal), `us` (vírgula de milhar/ponto decimal), `decimal` (ponto decimal sem agrupamento), `scientific` (decimal com expoente opcional), `unspecified` (somente inteiro ASCII, sem adivinhar separadores). Formato desconhecido gera `financial_format_unknown`. Prefixos suportados: BRL/R$, USD/US$, EUR/€; moeda ISO explícita deve ser uma das três. `$` isolado não é USD. Prefixo e declaração conflitantes geram diagnóstico, não preferência silenciosa. Moeda ausente/desconhecida mantém a quantidade monetária não resolvida: original retido, amounts vazio e diagnóstico específico; não se publica quantidade monetária sem moeda nem se inventa default.

Faixas usam exclusivamente ` to `, ` até ` ou ` .. `, até dois endpoints, com uma moeda inicial válida para toda a faixa. Hífens, moeda repetida por endpoint e palavras de escala (`mil`, `milhões`) não são extraídos: permanecem originais com diagnóstico. O parser não transforma orçamento em máximo por proposta nem soma claims. `NormalizedFinancialValue.amounts` contém Decimals exatos; `exponents` registra os expoentes originais normalizados de cada endpoint. Sinal de zero e zeros finais são preservados. Não se quantiza para duas casas nem para precisão SQL.

Unidades monetárias aceitas: `amount`, `per_month`, `per_year`; `monthly_scholarship` exige `per_month`. Não se convertem períodos ou calculam totais. `funding_percentage` exige `percent`, sem moeda; valores são pontos percentuais, não frações. Negativos, percentuais fora de 0–100 e faixas reversas são preservados e diagnosticados, não corrigidos. Não existe semântica implícita para taxa de juros ou outro rate: requer política futura. `eligible_expenses` exige `text`, preserva texto com `financial_expenses_text_only`; não extrai somas ou itens de despesas.

Orçamento numérico de origem: 256 dígitos ASCII agregados na expressão, inclusive expoente e ambos endpoints; expoente explícito de magnitude até 1000. Excesso retorna erro operacional antes de emitir resultados parciais, mesmo se outra evidência falharia. A representação JSON pode precisar de até 260 dígitos lexicais e expoente até 1256 após formatação Decimal; isso não amplia o orçamento de origem nem autoriza coeficiente acima de 256 dígitos. Python exige Decimal finito explicitamente; JSON exige strings decimais, nunca números float/bool. Strings malformadas geram ValidationError; exponents exige inteiros estritos. Interpretação normalizada é recalculada contra o original e suas declarações; `FinancialClaimResult` não pode apontar para claim diferente do interpretado. O relatório revalida resultados, diagnósticos, ordem e vínculo estrutural completo, mesmo sem envelope recebido.

## API organizacional

`normalize_organizations(context, claims) -> OrganizationNormalizationReport | OperationalError`. Cada `OrganizationClaim` preserva `role`, `name` opcional e tupla de identificadores. Papéis: `publishing`, `funding`, `managing`, `executing`, `partner`, `beneficiary`, `applicant`; publicador e financiador não são aliases.

`NormalizedOrganization.normalized_name` faz somente NFC e colapso de whitespace em nome válido; não remove acentos, não aplica casefold/NFKC, não expande siglas. Controles Unicode, formato invisível ou nome só branco não produzem nome utilizável. Nome, sigla e domínio não geram chave de identidade. O nome original sempre permanece no claim, inclusive quando não normalizável.

`OrganizationIdentifier` suporta `cnpj` numérico e `institutional`, com `IdentifierNamespace` opaco explicitamente fornecido; reutiliza conceitos M2.1, nunca constrói identificador de oportunidade ou FK. Identificador institucional usa `opaque-exact-v1` ou NFC opt-in `opaque-nfc-v1`, preservando zeros, pontuação e espaços válidos. CNPJ aceita 14 dígitos ASCII ou máscara exata `NN.NNN.NNN/NNNN-NN`, valida sintaxe e dígitos separadamente; número repetido e checksum inválido não geram chave. CNPJ alfanumérico é explicitamente `unsupported`, não implementado por regra inventada. `existence_status` é sempre `unverified`; nenhum acesso cadastral é feito.

API lexical isolada: `normalize_organization_identifier(OrganizationIdentifier)`. Ela não atesta contexto/evidência. No relatório, todos os componentes de um claim devem pertencer ao mesmo objeto e papel; falha suprime todas as `comparison_keys` daquele claim. Nome lexical preservado não é nome juridicamente certificado. Chaves contextuais são `(kind, namespace literal, source UUID, normalization policy, normalized value)`. Compartilhamento gera somente `contextual_identifier_shared_not_merge`, com índices e provas dos dois claims testemunhas. Diferenças em identificadores comparáveis geram testemunhas `organization_comparable_identifier_conflict`; nem igualdade nem diferença decidem identidade jurídica, e uma chave compartilhada não esconde divergência em outra.

Diagnósticos strings preexistentes permanecem em `diagnostics` por compatibilidade. Campo obrigatório `structured_diagnostics` contém `OrganizationDiagnostic`, com código, mensagem, claim_index, related_claim_index, identifier_index e provas exatas quando aplicáveis. Índices são inteiros estritos não negativos. Declaração global `organization_identity_unverified` não corresponde a um claim individual. Ausência de componente não inventa prova; flags de sintaxe/checksum não autenticam entidade. Relatório revalida todos os campos derivados, inclusive diagnósticos estruturados, sem reparar outputs recebidos. Relatórios parciais antigos sem o novo campo exigem regeneração explícita.

Detecção de conflitos armazena até duas representações distintas por classe comparável e emite testemunhas limitadas, não todos os pares de organizações. Não implementa união transitiva, fuzzy, merge ou cadastro. Índices preservam ordem das testemunhas. A saída não promete enumerar exaustivamente todas as divergências possíveis.

## API taxonômica

`normalize_taxonomy(TaxonomyInput) -> TaxonomyReport | OperationalError`. Claims exigem dimensão/papel explícito (`opportunity_type`, `resource_type`, `area`) e valor com proveniência; `unspecified` representa ausência de dimensão, não permissão de escolhê-la. `catalog_version` solicitado é preservado; somente `seeds-000002` é suportado. Versão diferente gera `catalog_version_unsupported` sem mapeamento. Não há catálogo arbitrário enviado pelo chamador.

São aceitos somente os 8/9/15 códigos exatos do catálogo em `policies.py`, verificados contra os seeds SQL; sem trim/casefold, aliases, traduções ou substrings. Regra `exact-code-v1`, código, dimensão, catálogo e `status` são preservados. Código desconhecido ou de outra dimensão gera `taxonomy_mapping_not_approved`; `bolsa` sem dimensão gera `taxonomy_mapping_ambiguous` com dimensões candidatas ordenadas, mas nenhum código canônico; código único sem dimensão ainda gera `taxonomy_dimension_missing`. No máximo três dimensões candidatas, nunca mapeamento múltiplo automático. Várias áreas são claims independentes, sem seleção de área principal ou fallback multidisciplinar. A ausência de claims gera `taxonomy_classifications_missing`.

Os diagnósticos por classificação ficam em `classifications[i].diagnostics`, com claim_index e prova do claim; `report.diagnostics` é reservado a diagnósticos globais. Consumidores devem examinar ambos. DTO normalizado verifica consistência lexical/catálogo; o relatório verifica contexto, evidência e toda a saída ordenada, mesmo com envelope ausente. Omissão, duplicação ou reordenação de resultados e falsos diagnósticos são rejeitados.

Notícias e resultados com prosa sobre edital/bolsa não são classificados por palavra isolada. Mesmo um código explícito suportado em uma notícia só normaliza aquela afirmação taxonômica: não transforma o item em oportunidade, não avalia prazo/acionabilidade, não chama ACCEPTED e não substitui o motor M1.

## Verificação e limitações

Os contratos anteriores M1–M2.2a.1, SQL/migrations e resolvedor M2.1 permanecem inalterados. A semântica de formato, moeda, unidade e namespace é declaração do adaptador; prova literal/estrutural não autentica essas interpretações. Sem extração real, governança de catálogo dinâmico, aliases aprovados, verificação cadastral, projeção SQL, câmbio, parsing de palavras de escala ou autoridade de escrita.

Observações de desempenho usam contexto/provas sintéticos e não garantem SLA. Validação de relatórios recalcula resultados em tempo linear no volume de claims/componentes, além dos custos de parsing/hash/serialização e tamanho das strings; isso custa mais que um parser isolado, mas preserva a fronteira pública. Sem produto cartesiano de identificadores. Os testes/gates, autoria dos arquivos parciais encontrados no início, revisão independente e decisão final estão em `EDITALFINDER_V2_M22B_RESULTADOS.md`. Nenhum item desta etapa autoriza M3.
