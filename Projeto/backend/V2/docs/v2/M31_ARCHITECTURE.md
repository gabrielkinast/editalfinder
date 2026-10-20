# M3.1 — proposta pré-implementação e protocolo experimental

## Inspeção e autoridade

Baseline executado antes da edição: 2095 passed in 20.40s; CLI M3.0 válido 28/33; hashes de 28 originais e 28 visões conferidos. Inventário inicial de conteúdo preservado em scratch e posteriormente arquivado no pacote M3.1. Árvore suja preexistente, inclusive exclusão SQL, não será limpa.

Lidos resultados/revisões M3.0, README/protocolo/preparação, manifesto/anotações/cobertura e contratos DATA_CONTRACT, SOURCE_SCOPE, IDENTITY_M21, INTEGRATION_CONSISTENCY_M23B, INTEGRATION_AUDIT_REPROCESSING. Inspecionados dataset_m30, models, validation, integration, integration_models, modelos temporal/financial/geography/organization/taxonomy/semantic_common e fixtures M23/testes M30. DATA_CONTRACT e SOURCE_SCOPE são propostas históricas; decisões posteriores e implementação aprovada prevalecem. M31_PREPARATION exigia referência humana aprovada para avaliação certificada: a autorização atual permite apenas comparação exploratória com rótulos provisórios, não satisfaz nem contorna essa exigência.

## Escopo mínimo e componentes

- Pacote extraction_m31 separado do domínio; Pydantic V2 congelado, extra=forbid, tuplas, versão própria. Não herdar tipos de decisão M1.
- Leitor local bounded: projeção explícita de metadados não rotulados; raw/ e text/ apenas; hashes separados; assinatura/tipo; texto UTF-8; limites de bytes/nós/profundidade/segmentos. Falhas por documento são operacionais, nunca negativas.
- HTMLParser stdlib reproduz a derivação passiva e adiciona locadores de blocos/ancestralidade; rejeita divergência com visão congelada, não a reescreve. Sem execução, rede ou leitura de anexos. PDF usa visão congelada com páginas físicas por formfeed; nenhuma renumeração ou nova renderização.
- Segmentação por blocos/paragraphs e cabeçalhos; chamadas repetidas separam unidades; transações e descrições de instrumentos não são fundidas pela página inteira. Fallback conservador por parágrafo/página, abstendo quando necessário. Limites causam falha explícita, não truncamento silencioso.
- Regras contextuais determinísticas PT-BR: múltiplos indícios locais (instrumento + acesso, público/condições), sinais, anúncios explicitamente futuros, negócio concluído, abstention. Sem identificação de documentos, respostas ou IDs de referência nas regras.
- Campos são expressões literais com papéis e testemunhas locais: dinheiro com papel financeiro, datas com papel e incerteza, descrições organizacionais/público/local explicitamente declaradas. Não normalizar para SQL, converter moeda ou inferir identidades.
- Verificador de evidência separado verifica ownership run/documento/hash/segmento, limites, quote e páginas; isso não prova entailment. JSON canônico determinístico separado de timings.
- Pipeline de inferência não importa dataset_m30 nem lê anotações/cobertura; CLI só lê manifesto e arquivos raw/text declarados. Avaliador separado só lê referências depois de congelar/hash das previsões.

## Split pré-ajuste

Não existe holdout independente honesto neste piloto: os 33 rótulos e casos especiais já foram expostos em M3.0 e na especificação. Todos os 28 documentos pertencem ao desenvolvimento; reserved_evaluation=[]; nenhuma alegação de teste cego. Um grupo conservador contém instituições e famílias conectadas: listagens CNPq ligadas aos detalhes/PDF e notícias MCTI; Finep/MCTI; fundos BNDES/Finep e Criatec; linhas BRDE/BNDES. Este agrupamento deliberadamente amplo impede separar parentes como se fossem independentes. IDs só constarão do manifesto de split/eval, nunca de regras. Um holdout futuro exige documentos não expostos e referências humanas independentes, não reaquisição nesta milestone.

## Ponte M1/M2 — desenhada, não implementada automaticamente

IntegrationInput exige CandidateIntegrationInput.context (NormalizationContext, OpportunityCandidate, snapshots), referência civil explícita; roles financeiros existentes não incluem principal de crédito/ticket equity. RawSnapshot exige UUID de fonte/executação, collected_at e JSON sanitizado. Não há configuração autorizada de UUIDs/namespaces reais, mapping source-specific aprovado ou autoridade de revisão. Nem dataset IDs, URL ou hash podem preencher essas identidades.

Ponte futura deverá receber contexto autorizado explicitamente; construir um objeto estruturado por segmento com campos escalares, DocumentUnit real, pointers RFC6901 diretos e FieldAssertions; manter mapa separado para offsets/hash HTTP/PDF. Hash JSON sanitizado jamais substitui hash original. Não copiar diagnóstico de descoberta para actionable/specific_instrument, não inventar ciclos/namespaces. Sem aprovação desses contextos, esta milestone mantém saídas separadas e registra bridge=not_implemented_context_authorization_missing. Não criar um validador concorrente ao M1.

## Correções após revisão técnica v1

A revisão independente v1 foi FAIL: a chamada final podia atravessar o fim do contêiner, e o verificador aceitava limites de segmento recebidos sem reconstruí-los. Ambos foram reproduzidos em testes RED e corrigidos no método `m31-deterministic-v2`: blocos HTML retêm ancestralidade estrutural local; agrupamento termina na saída do contêiner da chamada; verificação reexecuta a segmentação e exige IDs/limites/ordem/completude idênticos, com testemunhas contidas nos blocos da unidade reconstruída. Isso prova isolamento estrutural, não segmentação semântica perfeita dentro de um contêiner ambíguo. Continua proibido emprestar evidência entre unidades.

A leitura de previsões agora aplica limite durante o read; valores `mi`/`bi` são preservados literalmente, sem conversão. A CLI usa imports relativos internos para manter o gate histórico. `run-v1` preserva a execução anterior; `run-v2` é a execução corrigida. Não houve segunda revisão independente da versão final: correções verificadas pelo agente principal, pendentes de revisão externa.

## Dependências e critérios

Somente stdlib e Pydantic já instalado. Sem ML/LLM, rede, novo crawler ou instalação. Testes TDD em slices, sintéticos adversariais separados de casos reais. Gates completos, execução 28/28 ou falhas explícitas, avaliação de sobreposição/discordâncias/abstenções (não precisão/recall), timings por estágio, tamanho e memória observada. Revisão AI sequencial após congelamento; nenhuma aprovação humana implícita. Parar M3.1; não iniciar M3.2.
