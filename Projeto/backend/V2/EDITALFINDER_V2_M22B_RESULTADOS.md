# EditalFinder V2 — Resultados M2.2b

## Estado

**READY para o escopo offline M2.2b.** Implementação integrada, gates obrigatórios e revisão adversarial independente concluídos. Há um achado documental preexistente, não bloqueante, registrado na seção L. Sem autorização para produção, persistência, promoção ou M3.

## A. Decisões arquiteturais e baseline

Foram lidos README, resultados M2.2a.1, revisão final ChatGPT da M2.2a.1, contratos de domínio, decisões aprovadas, proposta DATA_CONTRACT, schema design, contratos M2.1/M2.2a e migrations/seeds/validações relevantes somente como texto. Nenhum SQL foi executado. Autoridade posterior de seeds/decisões prevalece sobre exemplos conceituais antigos; não se reabrem escolhas de UUID, taxonomias administráveis ou área N:N.

A árvore inicial já continha os oito módulos M2.2b, fixtures, testes parciais, README com referência M2.2b e documento de contrato parcial. Esse material foi preservado e completado; não se declara que toda a implementação ou todos os testes foram criados nesta execução. Estado inicial integral: **8 failed, 1228 passed in 3.92s**. Foram reproduzidos: JSON financeiro inválido escapando com InvalidOperation; conflito de identificadores organizacionais omitido; seis aceitações indevidas de relatório taxonômico contraditório.

A baseline anterior foi executada separadamente, excluindo somente testes M2.2b: **1075 passed in 4.49s**; após integração: **1075 passed in 3.78s**. São execuções reais, não aceitação do total histórico. Inicialmente Ruff tinha 24 erros e 11 arquivos fora do formato; mypy já passava em 24 módulos. Não se atribuem essas falhas preexistentes à correção nova.

Três núcleos puros e independentes permanecem em domain, sem I/O, framework de serviços, mapper ou dependência nova. `m22b_common.py` reutiliza contexto, evidências, contratos e limites antigos sem modificar M2.2a; acrescenta apenas suas próprias coleções de adaptador e envelope versionado. O normalizador valida evidência estrutural; o relatório recalcula resultados ao ser construído/validado, em vez de confiar apenas em hash recalculável. Nenhum resultado concede aprovação de oportunidade ou entidade jurídica.

Versões: `m2.2b-semantics-v1`, `m2.2b-normalization-limits-v1`; normalizadores `financial-conservative-v1`, `organization-conservative-v1`, `taxonomy-conservative-v1`; catálogo `seeds-000002`. `schema_version=2` permanece, sem alterar o envelope SQL versão 1.

## B. Contratos financeiros

API: `normalize_financial(FinancialInput) -> FinancialReport | OperationalError`.

`FinancialClaim` preserva papel, SemanticValue original/proveniência, formato declarado, moeda opcional e unidade. Papéis distintos: orçamento de programa; máximo/mínimo por proposta; bolsa individual/mensal; contrapartida; contribuição do candidato; percentual financiado; despesas elegíveis; prêmio; custo estimado. Não há soma, rateio ou transferência entre papéis.

Formatos explícitos `brazilian`, `us`, `decimal`, `scientific`; `unspecified` só aceita inteiro ASCII sem inferência de pontuação. Exemplos exercitados: R$1.500,50 → Decimal('1500.50')/BRL; BRL1500.50; US$25,000.00 → Decimal('25000.00')/USD; €2.500,00 → Decimal('2500.00')/EUR. Sem câmbio. `$` não implica USD; ausência/conflito/moeda não suportada preserva original, deixa amounts vazio e produz diagnóstico específico, sem publicar dinheiro sem moeda.

`NormalizedFinancialValue` contém claim, até dois endpoints Decimal exatos, moeda, expoentes de precisão, texto opcional e códigos. Strings Decimal são a representação JSON; Python exige Decimal finito, sem coerção int/float/bool/string. Preserva zeros finais e sinal de zero; não arredonda ou quantiza para duas casas. Faixas têm delimitadores explícitos ` to `, ` até ` ou ` .. ` e uma moeda aplicável aos dois endpoints; faixa inversa é diagnosticada, não reordenada. Negativos e percentual fora de 0–100 são preservados com diagnóstico, não clamps. `funding_percentage` usa pontos percentuais/unidade percent sem moeda; bolsa mensal exige per_month. Não há cálculo de total anual. Despesas elegíveis são somente texto rastreado, com diagnóstico explícito.

Strings inválidas JSON geram ValidationError, não exceção decimal escapada. Interpretação é comparada exatamente com o original, inclusive tupla Decimal, precisão e códigos; resultado não pode emparelhar claim diferente do interpretado. Relatório rejeita resultados/diagnósticos inconsistentes mesmo sem envelope anterior. Declarar formato/moeda/unidade não prova a verdade da interpretação do adaptador: essa fronteira é explícita, não autenticação da fonte.

## C. Contratos organizacionais

APIs: `normalize_organizations(context, claims) -> OrganizationNormalizationReport | OperationalError`; lexical isolada `normalize_organization_identifier(OrganizationIdentifier)`.

Papéis preservados: publishing, funding, managing, executing, partner, beneficiary, applicant. Site publicador não vira financiador. Cada OrganizationClaim conserva nome e identificadores; nome normalizado usa NFC e colapso de whitespace válido, sem casefold, remoção de acentos, NFKC ou expansão de sigla. Nome semelhante, sigla e domínio não produzem identidade nem merge.

Identificadores offline suportados: CNPJ numérico e institutional com namespace explicitamente fornecido. O schema organizacao possui UUID/código editorial/nome/país/site, mas não coluna CNPJ ou tabela desses identificadores. Nenhuma FK/tabela fictícia foi criada. Reutiliza IdentifierNamespace e políticas opacas M2.1, sem reaproveitar oportunidade_identificador como identidade de pessoa jurídica.

CNPJ: aceita 14 dígitos ASCII ou máscara exata; distingue syntax_status, checksum_status e existence_status. Checksum válido nunca prova existência; existence_status permanece unverified. Repetição de dígito/checksum inválido não gera chave. Alfanumérico fica unsupported com código específico. Institucional preserva literal ou NFC opt-in, incluindo zeros e namespace; não verifica autoridade cadastral.

Nome/identificadores de cada claim precisam vir de um único objeto/papel. Evidência inválida suprime todas as comparison_keys daquele claim, sem apagar o original ou falsificar identidade. Chave contextual: tipo, namespace, source UUID, política, valor normalizado. Compartilhamento é diagnóstico sem merge. Identificadores diferentes comparáveis produzem testemunhas de divergência; uma chave compartilhada não esconde conflito em outra. Não é uma decisão de identidade legal nem prova de que duas entidades reais sejam a mesma ou distintas.

`structured_diagnostics` obrigatório contém OrganizationDiagnostic com código/mensagem, claim_index, related_claim_index, identifier_index e evidências relacionadas; índices estritos não negativos. Strings de diagnóstico da implementação parcial foram mantidas por compatibilidade, mas não substituem os novos registros estruturados. Compartilhamento inclui ambos os índices/provas testemunhas; ausência de componente não inventa prova. Declaração global de identidade não verificada não é associada artificialmente a um claim. DTOs e relatório verificam derivados sem reparo silencioso; JSONs parciais antigos sem structured_diagnostics exigem regeneração explícita.

## D. Contratos taxonômicos

API: `normalize_taxonomy(TaxonomyInput) -> TaxonomyReport | OperationalError`.

Somente códigos exatos já presentes nos seeds e policies: oito tipos de oportunidade, nove de recurso, quinze áreas. Sem tabela arbitrária enviada pelo cliente, aliases, tradução, casefold, trim, inferência por substring ou fallback. Dimensão deve ser explícita; bolsa sem dimensão conserva ambiguidade entre opportunity_type/resource_type, sem código escolhido. Código único com dimensão ausente continua unresolved. Código desconhecido ou da dimensão errada: taxonomy_mapping_not_approved. Catálogo solicitado diferente: catalog_version_unsupported e nenhum mapeamento. Não finge suportar catálogo futuro.

NormalizedTaxonomy preserva claim, catálogo, canonical_code opcional, dimensão, mapping_rule exact-code-v1 quando justificável, status, dimensões candidatas e diagnósticos. No máximo três dimensões candidatas. Múltiplas áreas permanecem afirmações independentes; não escolhe área principal. Ausência da coleção: taxonomy_classifications_missing. Diagnósticos por claim estão em classifications[i].diagnostics; report.diagnostics contém os globais. Prova e claim_index são verificados; relatório verifica a ordem/quantidade e recomputa toda classificação contra input/contexto, inclusive sem audit.

Notícia mencionando edital e resultado mencionando bolsa não são mapeados por palavras. Mesmo código taxonômico explícito suportado em notícia só normaliza aquela afirmação: não prova acionabilidade, abertura de chamada nem ACCEPTED. Não houve mudança no motor M1, no contrato de revisão autenticada ou em promotable=False.

## E. Arquivos entregues e autoria

Preexistentes modificados nesta execução:

- src/editalfinder_v2/domain/financial_models.py
- src/editalfinder_v2/domain/financial_parsing.py
- src/editalfinder_v2/domain/organization_models.py
- src/editalfinder_v2/domain/organization_normalization.py
- src/editalfinder_v2/domain/taxonomy_models.py
- src/editalfinder_v2/domain/taxonomy_normalization.py (formatação; núcleo puro já existia)
- tests/test_financial_edges.py (formatação)
- tests/test_organization_identifiers.py (formatação)
- tests/test_organization_normalization.py (formatação/imports)
- tests/test_taxonomy_models.py (formatação/imports)
- tests/test_taxonomy_normalization.py (formatação)
- tests/test_taxonomy_evidence.py (formatação/imports)
- tests/test_taxonomy_integrity.py (formatação)
- docs/v2/SEMANTIC_NORMALIZATION_M22B.md (APIs/decisões/limites concretos e compatibilidade)

Criados nesta execução:

- tests/test_financial_adversarial.py
- tests/test_organization_adversarial.py
- tests/test_taxonomy_adversarial.py
- tests/test_m22b_boundary_adversarial.py
- EDITALFINDER_V2_M22B_RESULTADOS.md

Completam o subsistema, mas já existiam e não foram modificados nesta execução: m22b_common.py, financial_normalization.py, m22b_fixtures.py, test_m22b_common.py, test_financial_normalization.py, test_financial_parsing.py. README já referenciava M2.2b no início, e foi preservado. Todos continuam majoritariamente untracked; isso não é indicação de autoria desta execução. Não houve staging/commit.

## F. Regressões e TDD

A suíte dirigida final contém **273 casos M2.2b** sobre a baseline 1075; **112 casos foram acrescentados nesta execução**, além dos 161 casos parciais encontrados inicialmente. Não foram enfraquecidas expectativas antigas nem introduzidos skips/xfails. Cobertura de caracterização que já passava não é falsamente descrita como implementação nova.

RED→GREEN efetivamente observado pelos implementadores:

- Financeiro: reprodução da exceção JSON (1 RED); extremo fracionário scientific 1E-1250 (1 RED); faixa inteira com ` .. ` (1 RED/2 controles); interpretação de outro claim (1 RED); coerção de expoentes float/bool/string (3 RED). Suíte financeira integrada dos agentes: 77 aprovados.
- Organização: conflito comparável original (1 RED); campo estruturado ausente (1 RED); evidência da testemunha cruzada (1 RED/1 controle); índices inválidos (9 RED). Suíte organizacional dos agentes: 63 aprovados.
- Taxonomia: seis RED preexistentes; novas mutações de relatório (16 RED); diagnóstico standalone sem prova/índice coerente (15 RED). Suíte taxonômica: 88 aprovados.

O agente principal encontrou e testou mais duas fronteiras antes de corrigir:

- Decimal com 255 dígitos e e9 / 253 dígitos e999 normalizava, mas o JSON da mantissa/expoente crescia e era rejeitado pelo orçamento lexical de origem: **2 failed, 1 passed**. Separou orçamento wire limitado (260 dígitos) de origem (256); coeficiente e reinterpretação exata continuam vinculados. **23 testes adversariais financeiros passaram** após a correção.
- Diagnóstico de chave organizacional compartilhada não indicava os claims/provas: **1 failed** com índices (None, None). Agora usa índice de primeira testemunha e evidências exatas, sem busca quadrática. Incluído na suíte integral verde.

Controles adicionais da fronteira comum: **41 passed**, incluindo coleções novas sem ampliar matcher antigo, filho direto, pai/irmão com literal igual, quote sem papel estrutural, prova sem pertencimento, ambiguidade, source/execution/candidate/snapshot incorretos, JSON não textual e limites de claims/componentes/metadados. Nenhuma correção de produção compartilhada foi necessária.

## G. Verificação adversarial e gates

Ambiente executado: **Python 3.11.16 / Pydantic 2.14.1 / pytest 9.1.1 / Ruff 0.17.1 / mypy 2.4.0**. Sem instalação de dependências. Não há alegação de certificação de outra versão.

Comandos obrigatórios no diretório V2:

- `.venv/bin/python -B -m pytest -p no:cacheprovider -q`: **1348 passed in 4.46s** na implementação integrada congelada para revisão.
- `.venv/bin/ruff check --no-cache src tests`: **All checks passed!**
- `.venv/bin/ruff format --check --no-cache src tests`: **65 files already formatted**.
- `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src`: **Success: no issues found in 24 source files**.
- `git diff --check`: exit **0**, sem saída; complementado por verificação dos arquivos novos/tocados porque diff não cobre untracked.

Execução dirigida de todos os arquivos test_financial*, test_organization*, test_taxonomy*, test_m22b*: **273 passed in 0.77s**. Execução da baseline excluindo esses mesmos arquivos: **1075 passed in 3.78s**. O estado inicial de 8 falhas e os ciclos RED foram registrados antes das correções; os 1348 finais não são uma alegação de autoria de todos os testes.

## H. Serialização e auditoria

Os relatórios preservam input/contexto completos, claims em ordem, originais, papéis, evidências, versões, valores normalizados e diagnósticos. M22BAudit usa SHA-256 dos bytes UTF-8 exatos de model_dump_json(exclude={'audit'}), algoritmo/hash_version/limits_version explícitos. Envelope retido divergente gera ValidationError, não recálculo silencioso. Sem audit calcula envelope novo, mas os três relatórios ainda rejeitam derivações incompatíveis com suas entradas.

Testes exercitam construtor, model_validate, model_validate_json, round-trips, mudanças de tipo/escalar/precisão, troca de papéis e provas, omissão/duplicação/reordenação de resultados e adulteração de diagnósticos/índices/envelopes. Hash não autentica autor/fonte e model_construct/model_copy(update=...) continuam escapes Pydantic não validados; não substituem validação de fronteira.

## I. Desempenho e recursos

Limites compartilhados M2.2b: 1200 claims e até 1200 valores componentes; 8192 caracteres por valor/metadado; 1 Mi caracteres agregados. Preserva limites anteriores: 1200 afirmações, 2400 ocorrências de prova, 64 por campo, 32 snapshots, 8 MiB payload UTF-8, 1000 referências e limites próprios do parser. Financeiro limita 256 dígitos de origem/expoente 1000; taxonomia limita três dimensões candidatas. Excesso retorna OperationalError normalização sem truncamento, resultado parcial ou promoção.

Índice de contexto é preparado por avaliação; validação pública do relatório deliberadamente repete a avaliação. Não se promete uma única avaliação na chamada completa. Busca de identificadores e evidências usa índices; organização mantém até duas representações distintas por classe comparável e testemunhas limitadas, não pares O(N²). Custos de strings/JSON/hash e volume de evidências preservadas continuam materiais.

Benchmark auxiliar real:

    PYTHONPATH=src:tests .venv/bin/python -B /home/lorenzozm/.hermes/cache/scratch/m22b_benchmark.py

Três repetições por cenário, mediana em segundos; input construído fora da medida, uma prova contextual reutilizada, não 1200 evidências distintas:

| Claims | Financeiro | Organização | Taxonomia |
|---:|---:|---:|---:|
| 1 | 0.000408 | 0.000295 | 0.000170 |
| 64 | 0.009161 | 0.011370 | 0.004910 |
| 256 | 0.038378 | 0.047433 | 0.019670 |
| 1200 | 0.193666 | 0.260368 | 0.098062 |

Para 1200 claims, serialize+validate_json: 0.241372 / 0.412312 / 0.182234 s; saídas UTF-8: 2823199 / 4644152 / 1815195 bytes, respectivamente. Determinismo e round-trip foram assertados em todos os cenários. Guardas bloqueando builtins.open/socket.socket durante as normalizações passaram. São observações sintéticas locais, não SLA, prova formal de isolamento ou benchmark de fontes reais. Scripts auxiliares ficam em scratch, não são dependências do produto.

## J. Compatibilidade e preservação de escopo

Nenhum contrato/módulo/teste da baseline M1, M1.1, M1.1a, M2.1, M2.2a e M2.2a.1 foi modificado. Baseline 1075 reexecutada e aprovada. Resolver de identidade, fronteira antiga de normalização, políticas e catálogos antigos permanecem. Nenhum caminho novo ACCEPTED, promotable=True, persistência ou mapper foi criado.

Comparação SHA-256 com snapshot inicial de **5629 arquivos preexistentes** (excluindo ambientes/dependências/caches): somente os **14 arquivos preexistentes** listados na seção E mudaram, mais os **cinco novos** declarados. Todos os 19 passaram UTF-8, LF/final newline, ausência de NUL, whitespace final e marcadores de conflito. Módulos/testes anteriores, Legacy, SQL e README permaneceram hash-idênticos ao início. Varredura AST dos oito módulos de produção não encontrou imports de bibliotecas de rede/banco/processo/filesystem; guardas runtime sintéticas também passaram. Exclusão preexistente de BANCO DE DADOS/bancode Dados.sql e alterações alheias do working tree foram preservadas. Sem Legacy, migrations novas/modificadas, Supabase, crawlers, rede, staging ou commits. M3 não foi iniciado.

## K. Limitações e decisões ainda abertas

- Sem parsing de milhões/mil, moeda por endpoint, faixas por hífen, juros/rates não especificados, rateio, câmbio ou extrapolação de bolsa mensal.
- Só BRL/USD/EUR; moeda ausente fica não resolvida, não vira zero ou quantidade monetária sem moeda.
- Numeric(18,2) SQL não representa todos os papéis/precisões/negativos/percentuais; nenhuma projeção persistida é prometida.
- CNPJ apenas numérico, nunca existência; namespace/autenticidade legal/aliases de nomes reais exigem governança futura. Institucional é identificador opaco declarado.
- Comparação organizacional emite testemunhas de divergência limitadas, não lista exaustiva de pares ou resolução jurídica/transitiva.
- Catálogo fixo seeds-000002, sem aliases ou política source-specific para texto natural. Código exato não autentica acionabilidade nem verdade do item.
- Inputs já tipados existem antes dos limites de runtime; não se certifica orçamento de transporte/memória extremo, credenciais, cadeia de custódia, conjunto ouro ou precisão/recall em fontes reais.
- Auditoria não é assinatura, APIs Pydantic unchecked não são validação. Regeneração explícita é necessária para relatórios parciais antigos incompatíveis; não há migração silenciosa.
- Somente o ambiente acima foi executado. Não se reivindica matriz Python/Pydantic.

## L. Revisão independente

Revisão concluída por agente separado em contexto novo, somente leitura, após congelar código/testes integrados. Os três agentes de implementação não são apresentados como revisores independentes. Veredito independente: **READY — M2.2b offline domain**, sem defeito bloqueante de correção/segurança.

O revisor executou suíte completa (**1348 passed in 4.45s**), Ruff lint, formatação de src/tests (**65 files already formatted**) e mypy (**24 source files**, cache somente em scratch). Executou **388 verificações independentes** além da suíte: precisão Decimal 2/contexto Emax/Emin restritivo e traps ativos; quantidades grandes e extremos wire; moedas/faixas/negativos/percentuais/Unicode; CNPJ, namespaces e conflito misto; provas exatas/índices e contaminação entre linhas; todos os códigos dos seeds; dimensão/catálogo/ambiguidade; construtor/Python/JSON, saída omitida, audit ausente/adulterado e limites 1200/1201. Nenhum projeto, SQL, Legacy, dependência ou estado Git foi modificado pelo revisor.

Scripts apenas em scratch, lidos integralmente antes da reexecução pelo agente principal:

- `/home/lorenzozm/.hermes/cache/scratch/m22b_independent_review.py`: reexecução confirmou **388 verificações, 0.2792 s**; smoke de 1200 claims vazios, construção e round-trip: financeiro **0.0830 s**, organizacional **0.1203 s**. Não se confundem com os cenários com prova da seção I.
- `/home/lorenzozm/.hermes/cache/scratch/m22b_review_catalog.py`: reexecução confirmou acordo exato SQL/policies de **8/9/15 códigos**, e scan dos oito módulos sem chamadas proibidas ou token ACCEPTED. Não executa SQL.

Achado não bloqueante, severidade baixa: `EDITALFINDER_V2_M22A_REVISAO_INDEPENDENTE.md:54`, exemplo Python em Markdown preexistente fora do formato Ruff. O comando mais amplo `.venv/bin/ruff format --check --no-cache .` foi reproduzido pelo agente principal: **exit 1, 1 file would be reformatted, 97 files already formatted**. Não é o gate obrigatório `src tests`, que está verde. Documento antigo preservado hash-idêntico, sem correção fora do escopo. Portanto não se declara que formatação de todo o repositório passou.

A suíte/gates obrigatórios foram reexecutados pelo agente principal após o retorno, sem mudança de código/teste: **1348 passed in 4.46s**, lint aprovado, 65 arquivos formatados, mypy 24 módulos e git diff --check exit 0. Limitações de conservadorismo documentadas não foram consideradas defeitos; hash não é autenticação. Revisão independente de agente não substitui revisão técnica humana.

## M. Avaliação final

**READY — M2.2b, estritamente para os três subsistemas offline entregues.** Baseline anterior preservada, 273 casos dirigidos M2.2b aprovados, 1348 testes totais verdes, gates obrigatórios aprovados, serialização/auditoria verificadas, limites e incertezas explícitos e revisão independente concluída sem bloqueantes. A ressalva documental preexistente da seção L não altera o gate de src/tests e foi preservada.

Nenhuma promoção automática, banco, extração, persistência, merge fuzzy ou M3 foi implementado. Não há staging/commits. Trabalho encerrado na M2.2b; aguardar revisão técnica humana antes de qualquer avanço.
