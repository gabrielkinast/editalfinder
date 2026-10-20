# EditalFinder V2 — M3.1: extração offline de documentos reais

## A. Parecer final e alcance

**READY para o baseline experimental offline, com limitações semânticas e revisão externa da versão final pendente. Não pronto para produção ou publicação. M3.2 não iniciada.**

Há implementação reutilizável executada em documentos reais, saída separada e testemunhas verificáveis. O parecer não certifica acionabilidade, disponibilidade, precisão/recall, referência humana ou prontidão de fontes. O desempenho semântico é limitado; esta entrega é uma base de experimentação e análise de erros, não um extrator validado para uso autônomo.

Todos os 33 rótulos M3.0 permanecem `provisional`. A revisão independente originalmente solicitada da **M3.0 foi interrompida por HTTP 429 e não foi concluída**. As revisões ChatGPT existentes sustentavam preparação offline condicional, não verdade semântica. Nesta M3.1 foi realizada uma revisão técnica AI independente do código v1, com parecer **FAIL** e dois defeitos HIGH. Ambos foram reproduzidos e corrigidos pelo agente principal; o parecer não foi convertido em aprovação da versão final. Não houve segunda revisão independente; aguardar revisão externa.

## B. Inspeção inicial e preservação do estado

Antes de implementar: Git status inspecionado; árvore com alterações/arquivos não rastreados anteriores, incluindo exclusão SQL preexistente, preservada. Inventário SHA-256 de 267 arquivos preexistentes sem ambientes/caches em `data/m31/initial_inventory.json`. Nenhum arquivo desse inventário foi modificado. Não houve staging ou commit.

Baseline real: **2095 passed in 20.40s**; validador M3.0 aprovou 28 documentos/33 registros; os 28 hashes de originais e 28 hashes de texto conferiram. Evidência em `data/m31/baseline.json`.

Foram lidos `EDITALFINDER_V2_M30_RESULTADOS.md`, `EDITALFINDER_V2_M30_REVISAO_FINAL_CHATGPT.md`, README/protocolo/preparação M3.0, manifesto, anotações, cobertura e documentação DATA_CONTRACT, SOURCE_SCOPE, IDENTITY_M21, INTEGRATION_CONSISTENCY_M23B e INTEGRATION_AUDIT_REPROCESSING. Inspecionados `dataset_m30.py`, contratos Pydantic e validação M1, integração M2 e modelos dos normalizadores temporal, geográfico, financeiro, organizacional e taxonômico, com fixtures/testes existentes. Propostas históricas não reabrem decisões aprovadas.

M3.0 permanece `m3.0-pilot-v1` / `m3.0-annotation-v1`: 28 documentos, 26 HTML/2 PDF, 33 registros, 95 evidências. README, manifesto, anotações e todo o conteúdo inventariado de `data/m3` ficaram inalterados. A reprodução passiva das 28 visões também passou ao final. Não houve aquisição, alteração de corpus ou novo download.

## C. Arquitetura e dependências

Proposta pré-implementação e registro do split: `docs/v2/M31_ARCHITECTURE.md` e `data/m31/split.json`. Componentes em `src/editalfinder_v2/extraction_m31/`:

- `reader.py`: projeção de proveniência, leitura limitada, validação de bytes/hash/tipo, HTML passivo e blocos com ancestralidade; PDF usa texto congelado.
- `structure.py`: agrupamento de chamadas por cabeçalho e contêiner estrutural; fallback por bloco/nó textual. Não assume documento = oportunidade.
- `rules.py`: conjunções contextuais locais de instrumento/acesso/papel; campos literais, diagnósticos e abstenção.
- `models.py`: contratos imutáveis versionados próprios, sem reutilizar decisões do domínio.
- `pipeline.py`: composição e verificação externa das testemunhas contra unidades reconstruídas.
- `run.py`: inferência em lote, projeção anti-leakage, ID determinístico, tempos separados, falhas por documento.
- `evaluate.py`: comparação exploratória separada, sem aresta de importação a partir do motor de inferência.
- `__main__.py`: CLI explícita em duas etapas, criação exclusiva de artefatos, freeze e avaliação posterior.

Somente stdlib e Pydantic V2 já instalado. Nenhuma nova dependência, ML stack, chamada LLM externa, crawler, autenticação, banco, SQL, Legacy ou serviço. O conteúdo dos documentos nunca é executado como instrução.

## D. Contratos de entrada, segmentação e saída

Método final **`m31-deterministic-v2`**; schema de documento **`m31-extraction-v1`**; envelope **`m31-run-v1`**. O envelope v1 não significa algoritmo v1: as versões são explícitas e independentes. Schema exportado em `data/m31/run-v2/document_outcome.schema.json`.

`DocumentOutcome` separa processamento (`processed`/`operational_failure`), proveniência, segmentos e diagnósticos. Cada `Segment` possui ID local por posição, limites, descoberta provisória, modalidade, temporalidade, campos e testemunhas. Cada `ExtractedField` retém nome, expressão original, método, incerteza explícita e `traceable_not_semantically_certified`. Não há ID canônico de oportunidade. `promotable` só admite false.

`Witness` inclui run ID, documento, hashes original/texto, segmento, início/fim, página e quote literal. Tuplas/modelos congelados e `extra=forbid` evitam mutabilidade ordinária. Construções unchecked de código confiável, como `model_construct`/`model_copy`, não são fronteira de validação de entrada externa.

Limites explícitos em `run-v2/config.json`: 5 MiB por original, 1 MiB por visão textual, 30.000 nós de dados HTML, profundidade HTML 256, até 64 documentos, manifesto até 1 MiB, segmento até 20.000 caracteres, até 3.000 segmentos/documento, transporte de previsões até 32 MiB durante leitura. Excedentes recusam explicitamente; não se cortam evidências para caber. Não são um teto completo de RSS/processo para todo input adversarial. JSON decoding, serialização e manutenção dos resultados têm custos adicionais; não expor como serviço sem admissão de transporte/saída mais ampla.

Originais só podem ser lidos por caminhos contidos `raw/`; visões por `text/`. Não se seguem URLs ou anexos. HTML exige assinatura e reprodução byte a byte da derivação UTF-8 conhecida; encoding/método não suportado é falha. HTML malformado dentro dos limites usa o parser passivo tolerante, não DOM renderizado. PDF preserva páginas físicas 1-based via formfeed, incluindo páginas sem texto; sem OCR ou recuperação de layout. Não se sobrescreve texto mantendo offsets antigos.

## E. Métodos, incertezas e limites semânticos

As classes de descoberta são previsões: confirmado, anúncio futuro, sinal, não acionável e abstain. Não são ACCEPTED/REJECTED/REVIEW M1. Regras exigem contexto local, não score nem ocorrência isolada de banco/edital/startup/milhões. Confirmado também não equivale a janela aberta.

Crédito, subvenção/bolsa e fundos/equity são distinguidos por expressões contextuais; mistura ou ausência de contexto mantém modalidade indeterminada. Campos financeiros preservam papel e literal: orçamento, expressão por proposta, limite de crédito, receita mínima do tomador, estimativa de capital de fundo, expressão monetária não resolvida. Não há conversão FX, inferência de moeda faltante, normalização de ticket, juros ou valuation para contratos não aprovados. `mi`/`bi` são preservados literalmente, não multiplicados.

Datas numéricas suportadas têm papéis separados; intervalos de inscrição localizados permitem uma previsão conservadora em relação a **2026-10-19**, sem relógio implícito. Datas conflitantes não recebem precedência inventada. Não se transforma dia civil em horário/cutoff/timezone. No próprio dia de deadline, o baseline não presume janela aberta. Datas textuais extensas, tabelas quebradas e cronogramas multietapas podem ficar desconhecidos. Ausência de prazo não produz open/continuous; evento futuro não produz janela future.

Organizações, público e geografia são descrições originais com papel heurístico e testemunha, não entidades normalizadas. Fonte não é financiador, gestor não é startup elegível, sede/domínio/idioma/moeda não definem elegibilidade. Expressões de execução/local e de elegibilidade são campos distintos. Atribuição semântica errada ainda é possível e precisa de revisão humana: resolubilidade de quote não prova entailment.

## F. Proveniência, isolamento e anti-leakage

A inferência só consome whitelist de ID documental, URL original, tipo, caminhos, hashes, tamanho e método de derivação. Descarta categorias, category_evidence, datas anotadas e organização do manifesto antes de processar. Não abre records.json, REFERENCE_LABELS.md ou coverage.json. Há teste com abertura de arquivos guardada e teste que envenena categorias/datas/labels de manifesto sem alterar run ID ou previsões. O conhecimento prévio do desenvolvedor sobre o corpus continua uma limitação experimental; não é eliminado por essa separação de código.

IDs/valores esperados dos 28 documentos não estão nas regras. IDs dos casos só aparecem em testes de avaliação/relatórios e metadados. Não existem respostas por documento, joins de evidências entre documentos, fuzzy merge ou quota de 33 previsões.

O verificador externo reconstrói a segmentação a partir do input verificado e exige mesmos IDs, ordem, quantidade e limites. Verifica ownership documento/run/hash, valor literal dentro da quote, quote no texto congelado, testemunha no bloco da unidade reconstruída e página física PDF. Ampliar limites recebidos não autoriza emprestar evidência. Isto garante isolamento **estrutural do algoritmo**, não uma prova de que todo contêiner DOM corresponda a exatamente um instrumento semântico. Layout ambíguo/inline e referências internas continuam difíceis.

## G. Split, congelamento e execução real

Não há holdout independente honesto neste piloto: rótulos e casos já foram expostos na M3.0 e na solicitação. O split pré-ajuste registra todos os 28 documentos como desenvolvimento e `reserved_evaluation=[]`, com um grupo conservador de instituições/famílias conectadas. CNPq listagem/detalhes/PDF e notícias MCTI, Finep/BNDES/fundos, BRDE/BNDES e Criatec não foram separados artificialmente. Não afirmar generalização cega ou representatividade estatística.

Comandos reais, de `backend/V2`, com `PYTHONPATH=src` e `PYTHONDONTWRITEBYTECODE=1`:

    .venv/bin/python -B -m editalfinder_v2.extraction_m31 predict data/m3 data/m31/run-v2 --reference-date 2026-10-19
    .venv/bin/python -B -m editalfinder_v2.extraction_m31 evaluate data/m3 data/m31/run-v2

A avaliação é outra invocação, após gravação exclusiva de predictions.json e recibo SHA-256. Verifica o recibo, manifesto, versão, data, todos os outcomes na ordem do manifesto e as evidências antes de comparar referências. Não reescreve previsões. Novo experimento precisa de outro diretório. `run-v1` e gates inicialmente falhos foram preservados como histórico, não sobrescritos.

SHA-256 final de predictions.json: `c4c32df2850ac101b4389ae1d91c643f87d1bc129a45e7b96f8586c3fc9ee388`. Reexecução em outro processo/diretório scratch produziu bytes idênticos (`run-v2/reproducibility.json`). Timings não entram nas previsões determinísticas.

## H. Resultados reais por documento e desempenho

São segmentos passivos de análise, **não oportunidades únicas**. Campos podem existir em segmento abstido quando seu literal/papel é rastreável, mas a descoberta do instrumento não está suficientemente estabelecida.

28 outcomes processados; 0 falhas operacionais; 1649 segmentos, 332 campos e 1413 abstenções. Distribuição de descoberta: `{"abstain": 1413, "confirmed_opportunity": 11, "opportunity_signal": 206, "unrelated_or_non_actionable": 19}`.

| Documento | Segmentos | Campos | Leitura ms | Segmentação ms | Extração ms | Evidência ms | Total ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| M30-C01 | 165 | 16 | 5.220 | 0.190 | 5.489 | 0.325 | 11.226 |
| M30-C02 | 228 | 22 | 6.357 | 0.177 | 5.121 | 0.362 | 12.018 |
| M30-C03 | 194 | 34 | 5.678 | 0.157 | 6.533 | 0.286 | 12.655 |
| M30-C04 | 120 | 13 | 4.849 | 0.099 | 2.865 | 0.152 | 7.965 |
| M30-C05 | 35 | 8 | 3.181 | 0.034 | 0.847 | 0.056 | 4.118 |
| M30-C06 | 51 | 2 | 5.995 | 0.034 | 1.399 | 0.077 | 7.505 |
| M30-C07 | 42 | 5 | 5.599 | 0.034 | 1.531 | 0.064 | 7.227 |
| M30-C08 | 28 | 0 | 5.245 | 0.025 | 0.711 | 0.043 | 6.025 |
| M30-F01 | 16 | 34 | 10.879 | 0.059 | 1.811 | 0.146 | 12.895 |
| M30-F02 | 5 | 11 | 9.615 | 0.021 | 0.557 | 0.062 | 10.256 |
| M30-F03 | 5 | 3 | 9.280 | 0.017 | 0.192 | 0.033 | 9.521 |
| M30-F05 | 7 | 4 | 12.390 | 0.029 | 0.839 | 0.090 | 13.347 |
| M30-F06 | 7 | 8 | 12.518 | 0.031 | 1.071 | 0.074 | 13.695 |
| M30-F07 | 67 | 28 | 2.480 | 0.045 | 7.311 | 0.296 | 10.132 |
| M30-F08 | 5 | 9 | 9.885 | 0.026 | 0.474 | 0.054 | 10.439 |
| M30-I01 | 44 | 9 | 5.554 | 0.035 | 1.359 | 0.067 | 7.014 |
| M30-I02 | 21 | 2 | 3.107 | 0.025 | 0.600 | 0.040 | 3.772 |
| M30-I03 | 99 | 2 | 10.581 | 0.072 | 1.615 | 0.138 | 12.405 |
| M30-I04 | 24 | 2 | 3.688 | 0.031 | 0.515 | 0.044 | 4.278 |
| M30-I05 | 39 | 6 | 3.113 | 0.031 | 1.672 | 0.068 | 4.885 |
| M30-I06 | 38 | 10 | 3.115 | 0.030 | 1.378 | 0.061 | 4.584 |
| M30-I07 | 92 | 44 | 2.988 | 0.058 | 4.417 | 0.287 | 7.750 |
| M30-I08 | 79 | 3 | 4.038 | 0.056 | 2.394 | 0.110 | 6.598 |
| M30-N01 | 37 | 7 | 3.016 | 0.032 | 1.185 | 0.054 | 4.288 |
| M30-N02 | 44 | 6 | 3.372 | 0.031 | 1.509 | 0.063 | 4.975 |
| M30-N03 | 57 | 14 | 7.565 | 0.043 | 2.036 | 0.085 | 9.729 |
| M30-N04 | 51 | 26 | 7.682 | 0.040 | 1.800 | 0.143 | 9.666 |
| M30-S01 | 49 | 4 | 3.379 | 0.035 | 2.115 | 0.073 | 5.603 |

Soma dos tempos por documento: 0.234571 s; exclui inicialização do processo, preparação do manifesto e serialização final. Pico RSS Linux observado: 48920 KiB (processo inteiro, imports/interpreter incluídos), não alocação por documento nem teto garantido. Saída serializada: 1699213 bytes. Arquivos locais/cache e único lote pequeno: não é SLA de produção nem benchmark estatístico. Medição completa em `run-v2/performance.json`.

## I. Fomento, crédito, investimentos e casos especiais

- **F01:** quatro chamadas distintas, segmentos com limites 5784–6735, 6736–7490, 7491–8212 e 8213–9577; cada intervalo fica no seu contêiner. Os prazos extraídos são respectivamente 11/12/2026, 04/12/2026, 31/03/2027 e 07/01/2027, com abertura e testemunha próprias. Nenhuma evidência da última chamada inclui “Refazer a busca” ou conteúdo posterior ao contêiner. Não afirma elegibilidade completa dos PDFs não congelados.
- **F02/F08:** há previsões confirmadas com janela aberta em intervalos suportados. Retificações/anexos não congelados são indisponíveis, não completados artificialmente. F07 tem metadado “Minuta”/Anexo I parcial já conhecido; suas datas/objetivo fragmentados em páginas não foram reunidos por conveniência.
- **F05/F06:** notícias produziram confirmação provisória de instrumento, não foram negadas por gênero; datas textuais/etapas não suportadas deixam temporalidade indeterminada, divergindo da referência open. Não universalizar elegibilidade Eureka.
- **C05:** Finame genérico e Finame Direto continuam unidades distintas. O parágrafo 851–994 prevê confirmado/crédito/undetermined; `R$ 80 milhões` é requisito de faturamento, não limite de crédito ou teto de subvenção. Testemunha de audience/instruções é desse mesmo parágrafo.
- **C01/C02/C03/C04/C06:** campos reais de limites, requisitos, juros/carência foram extraídos onde explicitamente localizados, mas o fallback fragmenta os produtos. Muitas descrições não são confirmadas por falta de acesso/condições no mesmo bloco. Não anunciar disponibilidade contínua nem reconciliar automaticamente Inova Mais RS com slug mais-inovacao.
- **C07:** transação concluída e descrição do programa não foram colapsadas em uma decisão da página; permanecem vários blocos locais. Há erro de relevância conservado: o melhor bloco da transação é signal, não o não-acionável da referência. Outro bloco identifica conclusão. O programa C07-R2 permanece sinal em vez de confirmação: falso negativo exploratório, sem empréstimo de condições entre blocos.
- **I05:** seleção de gestor não virou candidatura de startups; sinais ou abstenções, nenhuma janela startup aberta inferida.
- **I06:** bloco 1173–1556 contém seleção da gestora e análise/diligência/estruturação, com campos de papel organizacional/estágio; bloco 1557–1935 extrai literalmente `R$ 500 milhões` como estimativa de capital de fundo, mesmo abstendo na descoberta desse bloco. O melhor match é sinal/undetermined, divergindo do anúncio futuro provisório e discutível da referência. Nenhuma candidatura de startups ou ticket individual é inventado. Abreviação do título `R$ 500 mi` passou a ser preservada integralmente.
- **I07:** página física 12 mantém testemunha 11779–11838 do estágio de captação de FIPs, não de inscrições de startups. O registro anotado Sul Ventures está sobresegmentado; seu maior bloco pode abster, enquanto outros blocos são sinais. Outras páginas descrevem crédito e são saídas fora desse escopo de referência, não negativos implícitos. Revisor independente não completou sua leitura adicional da página 12; o agente principal inspecionou os trechos textuais e verificou páginas mecanicamente.
- **I02/I04:** convites fragmentados em título/formulário e parágrafos não foram reconstruídos suficientemente para corresponder às confirmações de referência; maior match abstém. Não esconder esses falsos negativos. Um convite equity contextual genérico é exercitado sinteticamente; isso não prova resolução dos layouts reais.
- **I03:** portfólio não gerou confirmação de acesso startup; maior segmento abstém e blocos explícitos de portfólio ficam não acionáveis.
- **N01/N02/N03/N04:** anúncios de negócios, resultados e suplementações não receberam confirmação nos melhores matches. N01/C07 ainda geram sinais indevidos como nova descoberta; N02/N03 abstêm no melhor bloco. N04 corresponde a não acionável para propostas já analisadas, sem fabricar nova janela.

Distribuição de modalidade nos segmentos: `{"credito": 130, "fomento": 22, "investimentos": 36, "undetermined": 1461}`. Temporalidade: `{"not_applicable": 19, "open": 6, "undetermined": 1624}`. Esses denominadores incluem blocos de navegação sobreviventes e abstenções, não são prevalência de instrumentos.

## J. Ponte M1/M2

**Não implementada**, por bloqueio de contexto autorizado/mapping: `bridge_status=not_implemented_context_authorization_missing`. Não é falha operacional de extração nem tentativa de criar um novo Validation Engine.

IntegrationInput/CandidateIntegrationInput exigem NormalizationContext, candidate e snapshots com UUIDs/contextos de fonte/execução. RawSnapshot é JSON sanitizado com hash próprio, não os bytes HTTP/PDF. DocumentUnit/FieldAssertion exigem escalar estruturado e RFC6901 resolvível; offset textual não é pointer. Não há autorização para inventar fonte UUID, namespace, ciclo, atestado de revisão ou mapping financeiro equity/principal de crédito nos papéis M2 existentes.

Desenho futuro está na proposta: contexto explícito autorizado, objeto por registro, campos escalares com pointers diretos, mapa reverso para hashes/offsets originais; chamada à API de integração existente, nunca validação alternativa. Nenhum candidate nativo, promoção, merge, persistência ou atribuição de autoridade manual foi criado nesta entrega.

## K. Comparação PROVISIONAL / EXPLORATORY

Referência: 33 registros, 9 uncertain, todos provisional; **não há ground truth humano autenticado**. Nenhum uncertain foi recodificado negativo e REVIEW não foi usado como REJECTED. A avaliação emparelha por documento e sobreposição de caracteres; escolhe maior interseção (desempate por posição), sem consultar classe/valor para escolher match. Retém todos os overlaps para expor granularidade; não infere identidade canônica.

Há 32 registros com sobreposição e 1 sem: M30-F03-R1. Esse registro continua no denominador 33, não é apagado nem considerado negativo. Há 26 referências com múltiplos segmentos; nenhum segmento cruza duas unidades anotadas na comparação atual. **0 matches têm fronteira exatamente igual à referência**; inclusive os de F01 diferem ao menos em limites de whitespace. Ausência de cruzamento não prova segmentação semanticamente completa.

| Dimensão do melhor overlap | Concordâncias literais | Discordâncias | Sem match | Total referências |
|---|---:|---:|---:|---:|
| Descoberta | 13 | 19 | 1 | 33 |
| Modalidade | 19 | 13 | 1 | 33 |
| Temporal | 24 | 8 | 1 | 33 |

Campos: 27 coincidências exatas de papel+literal entre 127 campos de referência; 125 campos em referências com match e 2 sem match. Expressões mais longas/curtas e papéis diferentes são diferenças, não equivalências normalizadas presumidas. As 332 extrações têm outro denominador, incluindo conteúdo não anotado; não servem como denominador de precisão de campos.

1182 segmentos não sobrepõem unidades anotadas e ficam **fora de avaliação**, não falsos positivos automáticos. Todas as 719 ocorrências de testemunhas (inclusive referências repetidas de campos) resolveram nas unidades reconstruídas; isso não certifica atribuição semântica.

Entre as 18 confirmações de referência, o melhor match produz 9 confirmações, 4 sinais e 5 abstenções. São omissões/discordâncias exploratórias, não recall certificado. Entre os 6 não-oportunidade de referência, há 1 não acionável, 2 sinais e 3 abstenções; nenhum melhor match confirmado, mas sinais indevidos (C07-R1/N01) continuam erros relevantes. Não calcular precisão/recall/F1 nem apresentar ausência de confirmação nesses 6 como segurança estatística geral.

### Ledger por referência

| Referência | Melhor segmento | Descoberta predita | Modalidade | Temporal | Discordâncias |
|---|---|---|---|---|---|
| M30-C01-R1 | segment-0043 | opportunity_signal | credito | undetermined | discovery_label |
| M30-C02-R1 | segment-0021 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-C03-R1 | segment-0026 | opportunity_signal | credito | undetermined | discovery_label |
| M30-C04-R1 | segment-0012 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-C05-R1 | segment-0019 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-C05-R2 | segment-0021 | confirmed_opportunity | credito | undetermined | nenhuma no recorte |
| M30-C06-R1 | segment-0004 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-C07-R1 | segment-0001 | opportunity_signal | credito | undetermined | discovery_label, temporal_status |
| M30-C07-R2 | segment-0002 | opportunity_signal | credito | undetermined | discovery_label |
| M30-C08-R1 | segment-0005 | opportunity_signal | credito | undetermined | nenhuma no recorte |
| M30-F01-R1 | segment-0008 | confirmed_opportunity | fomento | open | nenhuma no recorte |
| M30-F01-R2 | segment-0009 | confirmed_opportunity | fomento | open | nenhuma no recorte |
| M30-F01-R3 | segment-0010 | confirmed_opportunity | fomento | open | nenhuma no recorte |
| M30-F01-R4 | segment-0011 | confirmed_opportunity | fomento | open | nenhuma no recorte |
| M30-F02-R1 | segment-0001 | confirmed_opportunity | fomento | open | nenhuma no recorte |
| M30-F03-R1 | SEM MATCH | — | — | — | sem match |
| M30-F05-R1 | segment-0003 | confirmed_opportunity | fomento | undetermined | temporal_status |
| M30-F06-R1 | segment-0003 | confirmed_opportunity | fomento | undetermined | temporal_status |
| M30-F07-R1 | segment-0013 | opportunity_signal | fomento | undetermined | discovery_label, temporal_status |
| M30-F08-R1 | segment-0001 | confirmed_opportunity | fomento | open | nenhuma no recorte |
| M30-I01-R1 | segment-0017 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-I02-R1 | segment-0004 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-I03-R1 | segment-0003 | abstain | undetermined | undetermined | discovery_label, modality, temporal_status |
| M30-I04-R1 | segment-0003 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-I05-R1 | segment-0018 | opportunity_signal | undetermined | undetermined | modality |
| M30-I06-R1 | segment-0024 | opportunity_signal | investimentos | undetermined | discovery_label |
| M30-I07-R1 | segment-0074 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-I08-R1 | segment-0026 | abstain | undetermined | undetermined | discovery_label, modality |
| M30-N01-R1 | segment-0019 | opportunity_signal | credito | undetermined | discovery_label, temporal_status |
| M30-N02-R1 | segment-0023 | abstain | undetermined | undetermined | discovery_label, modality, temporal_status |
| M30-N03-R1 | segment-0013 | abstain | undetermined | undetermined | discovery_label, modality, temporal_status |
| M30-N04-R1 | segment-0006 | unrelated_or_non_actionable | fomento | not_applicable | nenhuma no recorte |
| M30-S01-R1 | segment-0020 | opportunity_signal | credito | undetermined | nenhuma no recorte |

Detalhes de todos os overlaps, campos, evidências, falhas/ausências e saídas não anotadas: `data/m31/run-v2/evaluation.json`. Esta comparação não foi uma avaliação cega; resultados são desenvolvimento exploratório. Locadores válidos não provam que uma organização/data/quantia tenha o papel que a heurística atribuiu.

## L. Testes adversariais, regressão e qualidade

Novo arquivo `tests/test_m31_extraction.py`: 39 testes/casos parametrizados de processamento real, contratos e adversariais. Desenvolvimento em ciclos RED→GREEN: leitor inicialmente ausente; chamadas com prazos locais; formato contextual e falhas; CLI/freeze/eval; após revisão, expansão de segmento, fim de contêiner sintético/F01 real, expressão mi e leitura bounded. Não foram alterados os 2095 testes históricos.

Cobertura exercitada: HTML malformado, UTF-8 inválido, controles, arquivos ausentes, hashes alterados, tamanho excedente, formato não suportado, vazio, cabeçalhos duplicados, múltiplas chamadas, navegação/related/aside, datas conflitantes, instrumentos mistos, expressões sem moeda e ranges ambíguos não normalizados, acesso ausente, termos equity/valuation não suportados, troca de documento/segmento/run/hash/valor/página, ampliação de limites, isolamento de irmãos, páginas físicas incluindo vazias, prompt injection textual, imutabilidade, serialização determinística, inferência sem rótulos, poisoning de categoria e criação exclusiva.

O teste de poisoning usa cópia sintética local de um original; mutações nunca ocorrem no corpus congelado. Texto malicioso não concede aprovação ou execução. Falhas operacionais ocupam seus slots; o avaliador mantém denominadores de referências de documentos falhos no teste sintético.

Gates finais em `data/m31/quality_gates_final.json`, todos executados com exit 0:

| Comando | Resultado real |
|---|---|
| `.venv/bin/python -B -m pytest -p no:cacheprovider -q` | **2134 passed in 21.42s** |
| Mesmo comando com `--ignore=tests/test_m31_extraction.py` | **2095 passed in 20.89s** |
| `.venv/bin/ruff check --no-cache src tests` | All checks passed! |
| `.venv/bin/ruff format --check --no-cache src tests` | 99 files already formatted |
| `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src` | Success: no issues found in 38 source files |
| `PYTHONPATH=src .venv/bin/python -B -m editalfinder_v2.dataset_m30 data/m3` | Validated 28 documents and 33 records |
| `.venv/bin/python -B data/m3/provenance/verify_derivation.py` | PASS 28/28 |
| `git diff --check` | sem saída |

A primeira execução global encontrou regressão no import absoluto interno da nova CLI: 1 failed/2127 passed, recorte histórico 1 failed/2094 passed. Foi corrigido o import para relativo, sem relaxar o teste de fronteira. Esses resultados falhos estão preservados em `data/m31/quality_gates.json`, não escondidos. Ambiente `.venv` Python 3.11.16; demais versões originais em M3.0. Não foi testada matriz adicional de versões/OS.

`git diff --check` não cobre arquivos não rastreados por si só. A inspeção suplementar dos arquivos criados verifica UTF-8, newline final, whitespace final, conflitos e JSON/Python válido; inventário de preservação e lista de arquivos em `data/m31/integrity_final.json`. Originais/visões M3.0 nunca recebem limpeza de whitespace.

## M. Revisão independente e resposta aos achados

Uma única revisão sequencial read-only foi concluída pelo subagente `sa-0-de7eb92e` (`deleg_a18e0e61`), sobre o código/hash congelado v1. Artefato: `docs/v2/M31_INDEPENDENT_REVIEW.md`; hashes revisados em `run-v1/freeze.json`. Seu parecer **FAIL** identificou:

1. F01 último segmento absorvia navegação/cookies após o contêiner, de 8213 a 13344. Correção v2 retém ancestralidade e encerra em 9577. Teste real e sintético falharam antes e passaram depois.
2. Verificador aceitava expansão de bounds com evidência de outro segmento. O probe dinâmico do revisor foi negado pela camada de approval e não executado; o agente principal reproduziu depois em teste que efetivamente falhou, corrigiu com reconstrução de unidades e comprovou rejeição.

Também foram corrigidas expressão abreviada `mi` e leitura bounded de previsões. A avaliação por melhor overlap continua um diagnóstico imperfeito; não foi maquiada para produzir mais concordâncias. A própria revisão confirmou determinismo v1 e ausência de mudanças nos arquivos M3.0 inventariados, mas não executou pytest nem completou seu deep read adicional da página 12. Não afirmar esses procedimentos como realizados.

**Correções finais verificadas pelo agente principal; sem aprovação independente final.** A revisão AI não é referência humana, nem autorização de publicação. Não houve nova tentativa da revisão M3.0 bloqueada por HTTP 429.

## N. Arquivos e limitações restantes

Criados nesta M3.1:

- `src/editalfinder_v2/extraction_m31/__init__.py`, `reader.py`, `models.py`, `structure.py`, `rules.py`, `pipeline.py`, `run.py`, `evaluate.py`, `__main__.py`.
- `tests/test_m31_extraction.py`.
- `docs/v2/M31_ARCHITECTURE.md`, `docs/v2/M31_INDEPENDENT_REVIEW.md`.
- `data/m31/initial_inventory.json`, `baseline.json`, `split.json`, `quality_gates.json`, `quality_gates_final.json`, `reproducibility_v1.json`, `integrity_final.json`.
- `data/m31/run-v1/{predictions.json,freeze.json,performance.json,evaluation.json}` preservados como histórico pré-correção.
- `data/m31/run-v2/{predictions.json,freeze.json,performance.json,evaluation.json,config.json,document_outcome.schema.json,reproducibility.json}` como execução final.
- Este `EDITALFINDER_V2_M31_RESULTADOS.md`.

Não foi modificado arquivo preexistente do projeto. Houve edições incrementais apenas em arquivos novos da própria M3.1. Lista completa e hashes no inventário suplementar; índice Git e exclusão SQL anterior preservados. Nenhuma migration, Legacy, contrato M1/M2, fonte ou anotação foi reescrita.

Limitações restantes: segmentação por nós é excessiva; contextos inline perdem convite/financiador/público; contêiner único pode conter múltiplos subcontextos sem cabeçalhos claros; F03 não tem overlap após limites mais conservadores; nenhum match tem fronteira exata; notícias concluídas podem gerar sinais; I02/I04 não foram recuperados corretamente; datas textuais/PDF tables são parciais; semântica de papéis é heurística; geografia/organizações não são validadas como entidades; orçamento de memória/saída não é um hard cap de processo; sem referência humana e sem holdout não há certificação de qualidade. Limites M23D-F02/F04 herdados não foram corrigidos pela extração.

## O. Critérios de aceitação e parada

- Regressão histórica e gates: aprovados com evidência acima.
- Corpus, rótulos e contratos anteriores: preservados.
- Implementação reutilizável, processamento 28/28 e campos reais das três modalidades: executados; sem copiar respostas de anotação.
- Cadeias de evidência e isolamento estrutural: verificados, inclusive tentativas de expansão/emprestimo; limites semânticos permanecem explícitos.
- Falta de suporte: abstenções/falhas explícitas; nenhum horário, moeda, identidade, classe SQL ou candidatura inventados por fallback.
- Previsões separadas; sem promoção, fuzzy merge, banco, publicação, deployment ou novo crawler.
- Revisão independente v1 FAIL preservada; correções verificadas localmente, versão final aguardando revisão externa.

**READY somente para experimentação offline controlada**; não para descoberta autônoma de oportunidades ou avaliação certificada. Se a revisão externa encontrar violação dos invariantes, o parecer deve voltar a NOT READY; não compensar falha de segurança com métricas. Parar na M3.1. **M3.2 não iniciada.**
