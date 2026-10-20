# EditalFinder V2 — M3.2: avaliação semântica e análise de erros

## A. Estado e parecer

**READY somente para avaliação offline exploratória.** Implementação, execução real, gates, preservação e revisão técnica independente verificados. Não é aprovação de qualidade do extrator, referência humana, produção ou publicação; não iniciar M3.3. Todos os resultados abaixo são **PROVISIONAL / EXPLORATORY**.

M3.2 é avaliação, não novo extrator. Não houve alteração nos algoritmos M3.1, previsões run-v2, corpus/anotações M3.0, contratos M1/M2 ou comportamento de produção. O objetivo é tornar erros e incertezas mensuráveis, não declarar qualidade elevada.

Independência limitada: a computação e os módulos de avaliação são novos e não chamam o comparador M3.1; o agente principal também participou da implementação anterior e conhece o corpus. Não é avaliação humana cega nem holdout. A revisão técnica independente AI solicitada ao final é outra camada, não certificação humana de rótulos.

## B. Baseline congelado e ambiente

Antes de implementar, Git status, versões, dependências, manifesto e todos os hashes foram inspecionados. Baseline real: **2134 passed in 23.06s**. Validador M3.0: 28 documentos/33 registros; reprodução passiva: 28/28. Os 28 originais e 28 textos derivativos conferiram; 33 anotações continuam provisional, 9 uncertain.

Inventário inicial: 300 arquivos preexistentes do projeto, incluindo **108 arquivos sob data/m3** (cache preexistente incluído) e 18 sob data/m31. A verificação final de preservação está em `data/m32/integrity_final.json`. A exclusão SQL anterior e alterações não relacionadas não foram restauradas nem incorporadas a commit. Índice Git não foi alterado.

Ambiente executado: Python 3.11.16, Pydantic 2.14.1, pydantic_core 2.50.1, pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0. Não foi instalado pacote. `pip freeze` falhou porque não há módulo pip nesse venv; versões foram obtidas por importlib.metadata, registradas integralmente em baseline.json. Nenhuma matriz adicional de Python/OS foi executada.

Run-v2 recebido: envelope `m31-run-v1`, DTO `m31-extraction-v1`, método `m31-deterministic-v2`; data civil **2026-10-19**. SHA-256 das previsões: `c4c32df2850ac101b4389ae1d91c643f87d1bc129a45e7b96f8586c3fc9ee388`. São fingerprints de integridade, não autenticação de emissor ou significado.

Foram lidos os relatórios/revisões M3.0 e M3.1, protocolo/README/preparação, manifesto/anotações, run-v2, contratos e testes reais, leitor/regras/modelos/verify_evidence/comparador M31 e verificador M30. A revisão ChatGPT posterior `EDITALFINDER_V2_M31_REVISAO_INDEPENDENTE_CHATGPT.md` revisou run-v2 e é distinta do FAIL original. **O FAIL v1 permanece preservado** em docs/v2/M31_INDEPENDENT_REVIEW.md. A revisão independente originalmente solicitada na M3.0 foi interrompida por HTTP 429 e não concluída; nenhum desses pareceres autentica rótulos humanos.

## C. Metodologia e implementação reutilizável

Plano anterior à implementação: `data/m32/evaluation_plan.md`, tarefas A–L com unidade, elegibilidade, denominadores, unknowns, abstention, matching e limites. Código novo em `src/editalfinder_v2/evaluation_m32/`:

- inputs: JSON limitado e estrito, binding explícito, versões, hashes, conjuntos/ordens de IDs, contratos originais e verificação de evidências;
- alignment: grafo geométrico completo many-to-many, independente de rótulos;
- fields: comparação literal/role conservadora, sem normalização monetária/temporal;
- engine: tarefas separadas, matrizes, slots preservados, abstenções e tempos por documento/registro;
- reviews: observações qualitativas AI com alvo/índice/valor/quote/hashes validados, sem aprovação humana;
- reporting: ledger e fila para adjudicação;
- CLI: criação exclusiva fora das árvores protegidas, resultados determinísticos separados de performance.

`input_binding.json` fixa dataset/protocolo/data, digests de manifesto/anotações/previsões e IDs esperados. Missing, duplicata, versão incorreta, review_status approved fabricado ou evidência inválida retornam `invalid_input`, diagnósticos estruturados e results=null. Falha operacional explicitamente declarada num outcome válido permanece nos denominadores. Não se apagam referências ou campos para o relatório continuar verde.

Inputs JSON são dados passivos; chaves duplicadas e números não finitos são rejeitados. Manifesto/anotações até 1 MiB, previsões até 32 MiB, binding/receipt até 64 KiB e ledger semântico até 2 MiB/512 itens; corpus limitado a 64 documentos/256 referências no avaliador. Reuso do validador M30 e dos contratos M31 evita motor alternativo M1. Esses limites de input não são um teto de memória/expansão de relatórios; benchmark local não autoriza exposição a transporte hostil em produção.

## D. Separação das tarefas e denominadores

| Task | Unidade / denominador real | Unknown/abstain/ausência |
|---|---|---|
| A processamento | 28 documentos do manifesto | nenhum outcome ausente; 0 falhas; missing seria input inválido |
| B segmentação | 33 referências e 1649 segmentos passivos | no overlap preservado com coverage zero; unannotated fora de escopo |
| C relevância ampla | 33 referências, alvo confirmado/futuro/sinal separado de não acionável | uncertain continua visível; abstain/no_overlap não viram negativo |
| D confirmação | 33 referências, matriz multiclasses e todos os overlaps | representante só diagnóstico, não candidate aceito |
| E modalidade | 12 fomento, 13 crédito, 8 investimentos, 0 undetermined de referência | unknown predito continua célula própria; subset vazio não score perfeito |
| F temporal | 33 para comparação, 27 applicable/6 not_applicable explicitamente separados | unknown não é fechado; evento/fundo futuro não é janela |
| G campos | todos os 127 campos de referência; inventário separado dos 332 claims | fora do escopo implementado fica unresolved; explicit field abstention não é discovery abstention |
| H locadores | 719 ocorrências, 532 testemunhas únicas | inválido impediria métricas, não desapareceria do denominador |
| I suporte semântico | 39 claims selecionados intencionalmente: 13 fields, 20 discovery, 6 temporal | não revisados e unresolved explícitos; sem extrapolar para corpus |
| J abstenção | todos os 1649 segmentos e seus vínculos às referências | 1413 não equivalem a 1413 oportunidades perdidas |
| K contaminação | todos os overlaps + ownership de claims; análise semântica dirigida | fora de recorte provisório não prova outro registro |
| L desempenho | avaliação de 28 docs/33 refs e estágios próprios | separados de timing do extrator; custos comuns não alocados arbitrariamente |

Não há score global, precisão, recall, F1 ou acurácia certificados. Mesmo as frações existentes são medidas geométricas/operacionais ou concordância provisória, jamais desempenho generalizado de descoberta. No resumo broad_relevance, null combina abstain, no_overlap e operational_failure; não indica negativo. A matriz discovery e os registros individuais preservam separadamente cada estado. Interpretar o resumo apenas junto dessa decomposição, sem confundi-lo com ausência de relevância.

## E. Alinhamento, fronteiras e comparabilidade

Somente mesmo documento e interseção não vazia [start,end). Preservados todos os links. Representative: maior interseção, menor start, menor end, ID lexical. Nenhum label esperado ou valor decide o emparelhamento; não há identidade canônica, fuzzy matching, merge ou reconstrução de candidato.

Cada link inclui interseção, IoU textual, interseção/segment length (pureza **contra o recorte**, não pureza semântica), interseção/reference length e fronteiras originais. Coverage de referência é união de interseções, evitando dupla contagem. Há testes com segmentos sobrepostos e com um segmento atravessando duas referências.

HTML: offsets Unicode aprovados, não bytes HTML. PDF: offsets são aqueles efetivamente existentes na serialização pdftotext congelada e páginas físicas 1-based verificadas via formfeed; IoU/coverage PDF não são geometria, precisão visual, linha física ou coordenada do PDF binário. Não normalizar texto nem deslocar spans.

Observações reproduzidas: 32/33 referências com overlap, 0/33 com fronteira exata, 26 sobresegmentadas; zero segmentos sobrepõem duas referências atuais. Isso não prova ausência de instrumentos não anotados dentro de um segmento. **32/33 NÃO é recall de oportunidades.** Há 1182 segmentos fora dos recortes, nunca marcados como negativos automáticos.

Tabela estrutural completa:

| Referência | Fragmentos | Coverage textual (chars) | Melhor IoU | Pureza do melhor contra recorte |
|---|---:|---|---:|---:|
| M30-C01-R1 | 33 | 2096/2128 | 0.138628 | 1.000000 |
| M30-C02-R1 | 33 | 3189/3221 | 0.123254 | 1.000000 |
| M30-C03-R1 | 16 | 1262/1277 | 0.231010 | 1.000000 |
| M30-C04-R1 | 87 | 4154/4240 | 0.057783 | 1.000000 |
| M30-C05-R1 | 9 | 523/531 | 0.290019 | 1.000000 |
| M30-C05-R2 | 2 | 156/157 | 0.910828 | 1.000000 |
| M30-C06-R1 | 16 | 1048/1130 | 0.235398 | 1.000000 |
| M30-C07-R1 | 2 | 646/783 | 0.720307 | 1.000000 |
| M30-C07-R2 | 4 | 1520/1523 | 0.391989 | 1.000000 |
| M30-C08-R1 | 6 | 246/299 | 0.337793 | 1.000000 |
| M30-F01-R1 | 1 | 951/952 | 0.998950 | 1.000000 |
| M30-F01-R2 | 1 | 754/755 | 0.998675 | 1.000000 |
| M30-F01-R3 | 1 | 721/722 | 0.998615 | 1.000000 |
| M30-F01-R4 | 1 | 1364/1365 | 0.999267 | 1.000000 |
| M30-F02-R1 | 2 | 1368/6957 | 0.195359 | 0.982001 |
| M30-F03-R1 | 0 | 0/185 | — | — |
| M30-F05-R1 | 1 | 1595/1595 | 0.700791 | 0.700791 |
| M30-F06-R1 | 1 | 3211/3211 | 0.839258 | 0.839258 |
| M30-F07-R1 | 15 | 8858/8889 | 0.348746 | 1.000000 |
| M30-F08-R1 | 2 | 955/6642 | 0.142643 | 0.974385 |
| M30-I01-R1 | 26 | 2117/2142 | 0.123716 | 1.000000 |
| M30-I02-R1 | 5 | 880/884 | 0.490950 | 1.000000 |
| M30-I03-R1 | 3 | 124/126 | 0.809524 | 1.000000 |
| M30-I04-R1 | 4 | 272/275 | 0.825455 | 1.000000 |
| M30-I05-R1 | 20 | 1781/2234 | 0.187108 | 1.000000 |
| M30-I06-R1 | 25 | 3017/3490 | 0.126648 | 1.000000 |
| M30-I07-R1 | 5 | 918/926 | 0.543197 | 1.000000 |
| M30-I08-R1 | 63 | 4825/5156 | 0.093483 | 1.000000 |
| M30-N01-R1 | 10 | 2270/2279 | 0.279070 | 1.000000 |
| M30-N02-R1 | 14 | 3147/3160 | 0.153165 | 1.000000 |
| M30-N03-R1 | 16 | 3154/3183 | 0.187559 | 1.000000 |
| M30-N04-R1 | 12 | 3190/3215 | 0.288336 | 1.000000 |
| M30-S01-R1 | 31 | 5654/6164 | 0.103018 | 1.000000 |

Não otimizar exact equality de whitespace: F01 difere apenas em um caractere por chamada. Em contraste, C04 tem 87 fragmentos e I08 tem 63. F02/F08 cobrem grande prefixo de navegação nas referências (start=0); coverage textual baixa nesses casos não é prova de perder a maior parte da chamada. F05/F06 têm manchetes relacionadas fora dos recortes anotados: o comparador final deixa UNRESOLVED quando não há outro registro provado, em vez de erro de atribuição automático. F03 perde seu recorte porque os três blocos são excluded, confirmado em probe estrutural.

## F. Descoberta, relevância e confirmação

Unidade é referência provisória; tabela pelo representative, acompanhada de histograma de TODOS os overlaps em cada registro. Não confundir representative abstain com documento inteiro abstido, nem contar segmento não anotado como falsa oportunidade.

| Referência de descoberta | Observações preditas | Suporte |
|---|---|---:|
| announced_future_opportunity | opportunity_signal=1 | 1 |
| confirmed_opportunity | abstain=5, confirmed_opportunity=9, opportunity_signal=4 | 18 |
| opportunity_signal | abstain=4, no_overlap=1, opportunity_signal=3 | 8 |
| unrelated_or_non_actionable | abstain=3, opportunity_signal=2, unrelated_or_non_actionable=1 | 6 |

As 18 confirmações de referência têm 9 confirmações, 4 sinais e 5 abstenções no representative. Nos 6 não acionáveis de referência, há 1 não acionável, 2 sinais e 3 abstenções. Isso é concordância/desacordo de desenvolvimento, não recall, especificidade ou precisão certificados.

C03 tem também uma confirmação no FAQ fora do recorte anotado (segment-0092, 6002–6298). Não classificá-la falsa positiva por estar fora do recorte, nem inventar um link canônico para melhorar a contagem. Os 11 segmentos confirmados da execução completa foram inspecionados qualitativamente: 10 sustentados e 1 parcial (F07, instruções de submissão isoladas sem toda identidade do instrumento); não extrapolar à web. Nenhuma candidatura startup aberta foi observada como confirmação em I05–I07.

Todas as discordâncias de descoberta/modalidade/temporal têm um item com evidência e questão de adjudicação em error_cases/review_queue. Aqueles gerados só pela diferença de label permanecem unresolved_disagreement, com causa de baixa confiança. O ledger qualitativo traz racionales e distinção entre erro reproduzido, hipótese e referência possivelmente discutível.

## G. Resultados de fomento

12 referências sob modalidade provisória fomento (inclui controles N03/N04), não 12 documentos independentes. Oito das nove confirmações de referência concordam em descoberta; F07 permanece sinal no representative, enquanto outra página emite confirmação. F01 preserva quatro chamadas e seus prazos próprios. F05/F06 confirmam notícia legítima, mas temporalidade fica unknown porque a extração de datas textuais/etapas é limitada.

N04 é o contraexemplo financeiro mais importante: no mesmo parágrafo as regiões recebem R$50/100/150 milhões e o limite POR PROPOSTA é R$2–5 milhões; os três primeiros foram rotulados proposal_amount_expression. Quotes resolvem, papéis não. N03 é notícia de resultado, não nova janela; abstain não é REJECTED.

F03 é uma landing page de anexo, não o anexo completo: ausência de extração do título/link está diagnosticada, mas nenhum conteúdo de PDF não congelado foi inventado.

## H. Resultados de crédito

13 referências de crédito: descrições de programa, Finame/Finame Direto, transação C07, N01/N02 e sinal de restauração S01. Modalidade no representative: crédito em 8, unknown em 5. Isso não é prova de cinco modalidades erradas: frequentemente falta contexto no bloco escolhido.

C05 preserva overview e Finame Direto separados; R$80m é faturamento do tomador. C07 separa transação concluída e programa, mas o primeiro fica signal e o segundo signal em vez de confirmação provisória. Restituir apenas o contexto do PRIMEIRO registro transforma a classificação congelada da função em não acionável no probe; não se emprestaram campos do segundo. N01 relata financiamento aprovado à Renault e futuro lançamento de veículo, não chamada futura. Sinal de um programa mencionado continua uma questão de relevância ampla; alertar nova oferta seria injustificado.

C01/C02/C04/C06 perdem título/público/acesso/limites por regras locais e padrões limitados. Crédito mínimo, teto anual, receita e orçamento não foram comparados como se fossem mesmo significado financeiro. Ausência de datas não vira continuidade, e disponibilidade de página não garante liberação pelo agente.

## I. Resultados de investimentos

8 referências. Apenas uma modalidade investimentos no representative; sete unknown, sem recodificá-las como empréstimo ou fomento. I02 tem convite explícito a se tornar sócio e preencher formulário; I04 solicita plano de negócios para análise segundo tese do fundo. Ambos abstêm no maior bloco. O probe isola que I02 muda só após contexto completo + whitespace achatado; I04 continua abstain, portanto não é lícito atribuir todas as omissões a uma única causa de segmentação.

I03 portfólio não virou confirmação atual. I05 seleção de gestor não virou acesso de startups; porém o compromisso Finep/FNDCT de R$50m foi rotulado como capital estimado do fundo, distinto da meta até R$250m. I06 meta até R$500m não é ticket individual; o alvo de IA/gestora/estruturação é real, disponibilidade de candidaturas permanece unknown. I07 captação do veículo e tese Sul Ventures são da página física 12; outras páginas de crédito não contam como erro de modalidade dessa referência.

Tabela por modalidade, campos diagnósticos (não semântica certificada):

| Modalidade de referência | Registros | MATCH | PARTIAL | MISSING | UNRESOLVED | Outros |
|---|---:|---:|---:|---:|---:|---:|
| fomento | 12 | 19 | 4 | 11 | 29 | 0 |
| credito | 13 | 5 | 8 | 13 | 13 | 0 |
| investimentos | 8 | 3 | 4 | 10 | 8 | 0 |
| undetermined | 0 | 0 | 0 | 0 | 0 | 0 |

## J. Notícias e futuro: estágios separados

Notícia não é negativo por gênero. F05/F06 trazem chamadas reais; C07 contém dois contextos; S01 é sinal relevante. Separar anúncio do instrumento, lançamento/operação do fundo, etapa de gestora, captação por LPs, futuro produto de beneficiário e janela explícita para candidatos.

I06 referência=announced_future_opportunity, previsão=opportunity_signal, temporal=undetermined em ambos. O representative real é segment-0024 (3048–3490, perfil de startups IA); a etapa de gestora está em segment-0017 (1173–1556). Não confundir esses dois segmentos. O contexto integral continua signal no probe: ramo de gestor precede futuro, e future_access só reconhece abertura de inscrições, enquanto a rubrica de anúncio de instrumento é mais ampla. A fonte sustenta fundo em estruturação, mas não janela startup; adjudicação pode manter signal ou aceitar announced_future conforme compromisso de acesso exigido. Não assumir referência errada nem extrator correto por conservadorismo.

A execução completa tem zero announced_future; isso identifica uma limitação de rubrica/padrão, não autoriza transformá-lo em applications open. N01 produto híbrido futuro não é nova rodada; I05 deadline de gestor não é deadline startup; I07 captação não é recebimento de candidaturas.

## K. Temporal: expressão, papel e disponibilidade

Data fixa 2026-10-19. Comparação contém 27 referências applicable e 6 not_applicable; o relatório mantém as 33 para transparência. Nas 9 referências open, 6 representatives são open e 3 undetermined (F05/F06/F07). Nas 18 undetermined, 17 undetermined e 1 no_overlap. Nas 6 not_applicable, 1 not_applicable e 5 undetermined. Não contar unknown como fechado/certo/errado automaticamente.

As seis previsões open do corpus inteiro foram inspecionadas: intervalos de inscrição contêm a data civil, com cutoff/timezone não verificados. Nenhum representative open conflita com referência closed/future/not_applicable ou unknown neste corpus; isso é observação finita, não garantia estatística ou aprovação de candidatura.

Expressões temporais retornadas: `{"opening_date": 6, "publication_date_expression": 5, "rectification_date_expression": 4, "submission_deadline": 6, "unknown_temporal_expression": 44}`. Valores e papel são auditados separadamente: publicação não é prazo, retificação não inventa precedência, resultado/evento não é abertura. Os cinco campos de publicação são mais estreitos que expressões de referência com hora, podendo ser PARTIAL. Não há suporte completo a datas textuais, múltiplas fases ou timezone; unknowns permanecem.

## L. Comparação dos 127 campos

Recomputação própria, sem chamar compare() M31: **27/127 strict name/role + literal**, mesmo valor histórico. Nenhuma normalização/FX, remoção de qualifier, junção de ranges, equivalência de datas ou papel financeiro foi feita para aumentar coincidências.

Categorias são diagnósticos conservadores de comparação, NÃO adjudicação semântica:

| Categoria | Campos de referência |
|---|---:|
| ABSTAINED | 0 |
| ATTRIBUTION_ERROR | 0 |
| MATCH | 27 |
| MISSING | 34 |
| PARTIAL | 16 |
| ROLE_ERROR | 0 |
| UNRESOLVED | 50 |
| VALUE_ERROR | 0 |

Todos os 127 slots existem, inclusive os 2 campos de F03 sem overlap. 45 target roles estão fora do escopo de campos implementado M31 e continuam explicitamente não suportados, não errados por default. PARTIAL pode reter numeral sem até, literal mais longo ou informação financeira sem papel específico; UNRESOLVED também cobre diferentes valores sem pressupor referência exaustiva.

ABSTAINED=0 é correto: M31 não possui um objeto de declínio explícito de campo. Discovery abstain não equivale a field abstention. ROLE_ERROR=0 nesta comparação de nomes NÃO prova ausência de erros financeiros: quatro dos 13 fields qualitativamente examinados têm papel incorreto, alguns são claims extras sem target de mesmo nome na referência. O inventário prediction-centric dos 332 claims é separado dos 127 targets.

ATTRIBUTION_ERROR só é candidato quando um valor pode ser localizado noutro registro explicitamente anotado, não só fora de um recorte. F05/F06 foram refinados a UNRESOLVED antes da revisão técnica; a primeira saída está preservada em preliminary-v1, não é canônica. MATCH conserva a ressalva semantic_adjudication=not_certified.

## M. Locadores e atribuição semântica

**719/719 ocorrências de witness verificadas**, correspondendo a 532 locadores únicos. São contagens diferentes por repetição de witness em fields. Verificação checa documento/run/hash original/hash de texto, unidade estrutural reconstruída, quote, valor literal, offsets, blocos admitidos e página física PDF. Não é autenticação e não certifica implicação semântica de classe/papel.

Subconjunto qualitativo deliberadamente orientado a riscos, não representativo:

| Tipo de claim revisado | supported | partial | unsupported | unresolved | Total |
|---|---:|---:|---:|---:|---:|
| field | 5 | 3 | 4 | 1 | 13 |
| discovery | 11 | 5 | 2 | 2 | 20 |
| temporal | 6 | 0 | 0 | 0 | 6 |

Não foi feita uma revisão qualitativa independente de todas as modalidades nem de todos os 332 campos. **319 fields permanecem não revisados semanticamente.** Não extrapolar uma taxa do subset para eles. Os 39 juízos são AI provisórios com rationale e context_evidence resolvíveis, não labels humanos. As duas classificações unsupported de descoberta dizem respeito a acesso novo sob a rubrica de registro C07/N01: o termo confirmed_defect no ledger é **relativo a essa rubrica de novo acesso** (protocolo 106–109), não prova de irrelevância informativa do artigo. As previsões são opportunity_signal, não chamadas confirmadas nem janelas futuras. A utilidade informativa ampla da notícia concluída ainda exige adjudicação, não exclusão global por gênero.

Contrastes reproduzíveis de alta prioridade:

1. N04 segment-0010, witness [5020,5411): “a região Norte recebeu R$ 50 milhões; ... Centro-Oeste, R$ 100 milhões; ... Nordeste, R$ 150 milhões. Os limites ... para cada proposta ... R$ 2 milhões a R$ 5 milhões”. Os campos 0/1/2 têm proposal_amount_expression. Os três valores regionais não são proposta individual. Root cause forte: janela de contexto +/-120 alcança cada proposta posterior; probe preserva esse gatilho. Nenhuma troca de bytes ou valor foi necessária para expor o erro.
2. I05 segment-0019, witness [1839,2234): meta até R$250m, BNDESPAR até R$100m e Finep compromete R$50m. Field[2] fund_capital_estimate=R$50m confunde compromisso de cotista com capital do veículo. Locator passa; semântica não.
3. C01/I05/I06: números corretos, mas a expressão perde até. MATCH estrito não foi forçado removendo qualifier da referência; três observações partial registram a omissão. A testemunha integral conserva até, e credit_limit já comunica um teto: isto é perda de completude da expressão, não necessariamente número errado ou alegação financeira inteiramente sem suporte. Não agregar esses três casos aos quatro papéis financeiros incorretos.
4. F01 funding_organization_expression usa realizada pelo; prova realizador/parceria mais diretamente que responsabilidade financeira de cada componente. Permanece unresolved, não financiador certificado.

## N. Abstenções e informação não resolvida

1413/1649 segmentos abstain: 354 intersectam referências e 1059 estão fora delas. Os diagnósticos retornados insufficient_context/mixed_or_missing_financial_modality/passive-block-local aparecem em todos esses segmentos. Isso registra o que a regra fez, NÃO demonstra que a fonte inteira não contém informação.

Não há 1413 oportunidades perdidas independentes. I02/I04/I07 demonstram contexto presente mas associação insuficiente; C04/C01 têm cabeçalhos que não bastam para público/condições; F03 perdeu seleção estrutural; F05/F06 mantêm temporal unknown por expressão/estágio. Há campos financeiros realmente ausentes e anexos externos não congelados; não preenchê-los. Origem causal de cada uma das 1413 abstenções não foi adjudicada manualmente e fica não resolvida, em vez de classificar todas como segurança desejável ou defeito.

Padrões de fields: 34 MISSING dentro dos papéis alvo implementados; 45 fora de escopo; 16 PARTIAL; demais UNRESOLVED por contexto/fronteira/expressão. Esses conjuntos têm definições distintas e não devem ser somados a segmentos abstidos como se fossem oportunidades.

## O. Casos e erros de alta consequência

Estudos completos: `data/m32/case_studies.md`, e 28 arquivos per_document com IDs/URLs/hashes, todos os campos, witnesses e incertezas. F01 preserva quatro chamadas; C05 overview/Finame Direto e C07 transação/programa ficam relacionados mas não fundidos. I03 é portfólio; I05 gestor; I06 estruturação de IA; I07 captação na página física 12. Trechos/fatos, labels provisórios, previsões reais, fronteiras, campos, abstenções, causas e incertezas estão explicitados nesses artefatos.

O ledger canônico tem 93 itens: desacordos por dimensão, observações de segmentação e casos qualitativos com códigos. A fila tem 60 itens pendentes de adjudicação autorizada, ordenados por severidade/documento/ID. Não são 93 defeitos confirmados nem 60 decisões revisadas. Campos numéricos corretos mas papéis errados, potencial público gestor/startup e oportunidade de negócio concluído têm prioridade superior a whitespace.

## P. Discordâncias dos labels provisórios

Os 9 uncertain nunca foram negativos binários; REVIEW de domínio não foi usado como REJECTED. Source/label/predição ficam lado a lado. I06 é disputa de definição entre compromisso de um veículo futuro e acesso futuro; fonte não estabelece janela startup. F02/F08 mostram que os próprios recortes não são uniformes com os de F01. F05/F06 mostram manchete relacionada fora de recorte. Nenhuma anotação foi corrigida para aumentar score; revisão futura precisa de nova release autorizada.

## Q. Taxonomia e validade dos diagnósticos

`m32-error-taxonomy-v1`, somente avaliação: segmentação over/under/boundary, navigation/related, atribuição de registro/documento, modalidade, papel/valor financeiro, temporalidade, geografia/organização, futuro/existência, inferência sem suporte, locador/semântica, omissão/abstenção, ambiguidade/possível erro de referência e contrato não suportado. Cada caso tem severidade, fonte/locador, esperado/observado, certainty, confiança causal e ação. Codes existentes não são todos observados no corpus e não entram em SQL/produção.

## R. Causas e experimentos controlados

`diagnostic_probes.json` registra sete experimentos/inspeções. A função classify permaneceu inalterada; contextos escolhidos pelas fronteiras de referência são deliberadamente **oracle-selected diagnostic contexts**, não novas previsões, tuning ou ganhos de qualidade:

- C07-R1: representative signal; contexto do mesmo registro completo non-actionable; achatamento de whitespace não muda o segundo resultado. Evidência de fator contexto.
- I02: representative e contexto completo com newlines abstain; só contexto achatado confirma investimentos. Evidência de interação regex/whitespace, não “juntar linhas resolve tudo”.
- I04: todos os contextos abstain. O problema não se explica apenas por fragmentação.
- I06: contexto completo continua signal (ramo manager), sem abertura de aplicações. A rubrica de futuro permanece questão separada.
- I07: maior fragmento abstain; contexto completo da referência sinaliza investimentos, com ou sem whitespace achatado. Isso não implica oferecer capital a startups.
- N04: a janela monetária contém a expressão cada proposta pertencente a cláusula posterior às alocações regionais.
- F03: os três blocos do recorte estão excluded; a fonte existe, o filtro a removeu.

Esses probes não estimam resultado de um futuro extrator; não foram reinjetados no baseline. Causas que não foram isoladas ficam hipóteses, não conclusão por intuição.

## S. Backlog M3.3, sem implementação

Oito propostas detalhadas em improvement_backlog.md, cada uma com casos, benefício, efeitos colaterais, componentes, contratos, testes, dificuldade e critério de verificação:

- B01/P0: associação de valores a cláusulas, papéis e sujeitos, sem trocar alocação/cotista por ticket.
- B02/P0: contexto de negócio concluído versus pista de programa/acesso, sem negar notícia inteira.
- B03/P1: hierarquia de registro e representação auxiliar de whitespace com mapa reverso de offsets.
- B04/P1: estágios/públicos de gestor, veículo, cotista e startup; anúncio futuro separado de inscrição.
- B05/P1: qualifiers/ranges e datas por papel/etapa, sem FX/timezone/precedência inventados.
- B06/P2: organização/audience e escopo de campo, sem publisher=funder.
- B07/P2: header de conteúdo versus navegação, sem fabricar anexo nem maximizar coverage de menus.
- B08/P0 governança: adjudicação humana real e corpus independente antes de métricas públicas.

Nenhum patch por M30-ID é proposto para produção. Nenhuma mudança M1/M2 é autorizada ou necessária para avaliar o baseline. Possíveis evoluções de DTO de extração exigem versão própria e outra milestone.

## T. Testes adversariais do avaliador

31 testes/casos novos em test_m32_evaluation.py, com ciclos RED→GREEN para alinhamento, loader, campos, engine, semantic reviews, CLI e refinamento de atribuição. Casos reais mais geometrias sintéticas de resultado conhecido; testes não só comparam função consigo mesma.

Exercitados: documento errado, hash obsoleto, referência inválida, cross-document, field borrowing, artefato ausente, IDs duplicados, classe não suportada, PDF page errada, HTML offset inválido, nested version ausente, witness malformado, regiões não anotadas, múltiplos segmentos por referência e múltiplas referências por segmento, papéis monetário/temporal trocados, futuro versus confirmação, approved fabricado, zero denominador/subset vazio, uncertain/abstain, versão de avaliação inválida, falha operacional mantendo 33/127 slots, poisoning de review/quote/index/context page/hash e output protegido/existente.

Mutantes são cópias temporárias controladas; nenhum teste altera o corpus ou run-v2. Falha de binding/schema/locator retorna results=null; um flag de review não concede autoridade.

## U. Desempenho exclusivo da avaliação

Uma execução local: evaluate() 0.233323 s; alinhamento 0.001554 s; verificações por doc 0.003877 s; comparação de campos 0.001246 s. Montagem/serialização de diagnósticos após o core 0.036970 s. Core 3139460 bytes; diagnósticos/per-doc 2894748 bytes. Pico RSS Linux 64632 KiB, processo completo com imports/interpreter; não hard cap.

Tempos por documento (ms), custo de estágios observados, não alocação inventada de custos globais:

| Documento | Leitura | Evidência | Alinhamento | Campos | Montagem de registro |
|---|---:|---:|---:|---:|---:|
| M30-C01 | 5.310 | 0.326 | 0.197 | 0.080 | 0.044 |
| M30-C02 | 6.485 | 0.372 | 0.166 | 0.045 | 0.058 |
| M30-C03 | 5.606 | 0.339 | 0.125 | 0.034 | 0.023 |
| M30-C04 | 4.271 | 0.190 | 0.118 | 0.032 | 0.045 |
| M30-C05 | 3.107 | 0.112 | 0.054 | 0.029 | 0.025 |
| M30-C06 | 6.094 | 0.089 | 0.053 | 0.015 | 0.010 |
| M30-C07 | 5.771 | 0.070 | 0.061 | 0.024 | 0.017 |
| M30-C08 | 5.218 | 0.052 | 0.024 | 0.005 | 0.004 |
| M30-F01 | 10.800 | 0.170 | 0.050 | 0.204 | 0.083 |
| M30-F02 | 9.592 | 0.078 | 0.009 | 0.043 | 0.021 |
| M30-F03 | 9.598 | 0.052 | 0.006 | 0.009 | 0.003 |
| M30-F05 | 12.972 | 0.115 | 0.009 | 0.037 | 0.011 |
| M30-F06 | 12.936 | 0.124 | 0.008 | 0.032 | 0.016 |
| M30-F07 | 2.681 | 0.313 | 0.051 | 0.040 | 0.036 |
| M30-F08 | 9.724 | 0.068 | 0.010 | 0.043 | 0.018 |
| M30-I01 | 5.568 | 0.121 | 0.048 | 0.020 | 0.022 |
| M30-I02 | 3.137 | 0.049 | 0.023 | 0.015 | 0.005 |
| M30-I03 | 10.770 | 0.152 | 0.065 | 0.011 | 0.009 |
| M30-I04 | 3.707 | 0.060 | 0.021 | 0.009 | 0.004 |
| M30-I05 | 3.220 | 0.068 | 0.037 | 0.039 | 0.023 |
| M30-I06 | 3.119 | 0.078 | 0.042 | 0.031 | 0.030 |
| M30-I07 | 2.993 | 0.300 | 0.061 | 0.346 | 0.016 |
| M30-I08 | 3.937 | 0.139 | 0.085 | 0.022 | 0.031 |
| M30-N01 | 3.133 | 0.064 | 0.045 | 0.015 | 0.019 |
| M30-N02 | 3.172 | 0.070 | 0.038 | 0.012 | 0.019 |
| M30-N03 | 7.918 | 0.101 | 0.048 | 0.013 | 0.016 |
| M30-N04 | 7.796 | 0.122 | 0.047 | 0.016 | 0.035 |
| M30-S01 | 3.550 | 0.084 | 0.055 | 0.025 | 0.021 |

Tempos por referência (ms), incluindo campos/alinhamento e montagem local; não incluem parcela fictícia de leitura compartilhada:

| Referência | Alinhamento | Campos | Montagem | Soma local |
|---|---:|---:|---:|---:|
| M30-C01-R1 | 0.197 | 0.080 | 0.044 | 0.321 |
| M30-C02-R1 | 0.166 | 0.045 | 0.058 | 0.269 |
| M30-C03-R1 | 0.125 | 0.034 | 0.023 | 0.182 |
| M30-C04-R1 | 0.118 | 0.032 | 0.045 | 0.195 |
| M30-C05-R1 | 0.030 | 0.009 | 0.015 | 0.055 |
| M30-C05-R2 | 0.024 | 0.019 | 0.010 | 0.053 |
| M30-C06-R1 | 0.053 | 0.015 | 0.010 | 0.078 |
| M30-C07-R1 | 0.032 | 0.006 | 0.007 | 0.045 |
| M30-C07-R2 | 0.029 | 0.018 | 0.010 | 0.057 |
| M30-C08-R1 | 0.024 | 0.005 | 0.004 | 0.033 |
| M30-F01-R1 | 0.014 | 0.053 | 0.017 | 0.085 |
| M30-F01-R2 | 0.012 | 0.054 | 0.014 | 0.081 |
| M30-F01-R3 | 0.012 | 0.043 | 0.012 | 0.067 |
| M30-F01-R4 | 0.012 | 0.052 | 0.039 | 0.104 |
| M30-F02-R1 | 0.009 | 0.043 | 0.021 | 0.072 |
| M30-F03-R1 | 0.006 | 0.009 | 0.003 | 0.018 |
| M30-F05-R1 | 0.009 | 0.037 | 0.011 | 0.057 |
| M30-F06-R1 | 0.008 | 0.032 | 0.016 | 0.055 |
| M30-F07-R1 | 0.051 | 0.040 | 0.036 | 0.127 |
| M30-F08-R1 | 0.010 | 0.043 | 0.018 | 0.070 |
| M30-I01-R1 | 0.048 | 0.020 | 0.022 | 0.090 |
| M30-I02-R1 | 0.023 | 0.015 | 0.005 | 0.043 |
| M30-I03-R1 | 0.065 | 0.011 | 0.009 | 0.085 |
| M30-I04-R1 | 0.021 | 0.009 | 0.004 | 0.034 |
| M30-I05-R1 | 0.037 | 0.039 | 0.023 | 0.098 |
| M30-I06-R1 | 0.042 | 0.031 | 0.030 | 0.103 |
| M30-I07-R1 | 0.061 | 0.346 | 0.016 | 0.423 |
| M30-I08-R1 | 0.085 | 0.022 | 0.031 | 0.138 |
| M30-N01-R1 | 0.045 | 0.015 | 0.019 | 0.079 |
| M30-N02-R1 | 0.038 | 0.012 | 0.019 | 0.068 |
| M30-N03-R1 | 0.048 | 0.013 | 0.016 | 0.078 |
| M30-N04-R1 | 0.047 | 0.016 | 0.035 | 0.098 |
| M30-S01-R1 | 0.055 | 0.025 | 0.021 | 0.101 |

performance.json separa tempos do core e montagem posterior. Há custos globais de parsing/validação do dataset e criação de objetos não distribuídos por documento; a serialização do core e o tempo de inicialização/imports não têm medição isolada. Não apresentar soma dos estágios como wall time de todo processo. Timings M31 permanecem históricos em run-v2/performance.json; nenhuma SLA de produção é inferida. Bounded lote único, cache local e variabilidade de execução limitam conclusões.

## V. Gates e determinismo

Todos executados, exit 0, logs em data/m32/quality_gates.json:

| Gate | Saída real |
|---|---|
| pytest completo, -B, no:cacheprovider | **2165 passed in 26.39s** |
| pytest --ignore=tests/test_m32_evaluation.py | **2134 passed in 21.92s** |
| Ruff check --no-cache src tests | All checks passed! |
| Ruff format --check --no-cache src tests | 108 files already formatted |
| mypy --no-incremental --cache-dir=/dev/null src | Success: no issues found in 46 source files |
| PYTHONPATH=src python -B -m editalfinder_v2.dataset_m30 data/m3 | Validated 28 documents and 33 records |
| git diff --check | sem saída |

Comando de reprodução do README executado em novo processo/diretório scratch: evaluation_results, error_cases, review_queue e os 28 per_document coincidiram byte a byte. Performance fica fora dessa comparação. SHA-256 do core final: `36625ca2e5d160c40a40eedfa4f1e6cfac78979984068209e9878f4721bd7cf9`. Code hashes e output hashes em freeze.json. Não se regenerou ou substituiu o baseline de extração; os probes só diagnosticam trechos.

Untracked files inspecionados separadamente por UTF-8/newline/whitespace/conflitos, JSON/Python e hashes; Git diff isolado não cobriria esses arquivos. Não foram enfraquecidos testes/contratos anteriores.

## W. Revisão técnica independente

**Concluída: PASS limitado à avaliação offline provisória**, sem security_concerns ou logic_errors confirmados. Revisão AI sequencial `deleg_12c4ba53` / `sa-0-1a0b7a43`, somente leitura. Registro: `data/m32/independent_review.json`.

O revisor relatou reprodução exata do core, ledger de 93 casos e fila de 60 itens; 38 verificações de freeze coincidentes; 230 entradas protegidas selecionadas sem mudanças; e 1000 geometrias em memória com união de cobertura e invariância à ordem. O agente principal confirma separadamente todos os hashes fornecidos e os 300 arquivos do inventário inicial. Os 1000 probes são resultado relatado pelo revisor, não uma segunda execução pelo agente principal.

Os quatro problemas de papel financeiro N04/I05 foram considerados sustentados por fonte/previsão reais; I06 segue unresolved quanto a signal/future, sem janela inventada. Recomendações não bloqueantes incorporadas à apresentação: defeito de C07/N01 relativo à rubrica de acesso novo, null do resumo amplo explicado e perda de até separada de erro de valor/papel.

O revisor leu os logs de 2165/2134 testes, mas NÃO executou uma suíte pytest independente; não criou/modificou arquivos nem usou rede/instalação/banco. O relatório final ainda não estava disponível quando foi procurado durante a revisão: esta redação foi produzida pelo agente principal e **não recebeu revisão independente**. PASS refere-se ao código/artefatos congelados e metodologia examinados, não à aprovação de cada frase deste relatório, verdade humana dos labels ou prontidão de produção. Aguardar revisão externa desta entrega.

## X. Arquivos criados/modificados

Somente arquivos novos M3.2:

- src/editalfinder_v2/evaluation_m32/{__init__,alignment,inputs,fields,engine,reviews,reporting,__main__}.py;
- tests/test_m32_evaluation.py;
- data/m32/{README.md,evaluation_plan.md,input_binding.json,baseline.json,initial_inventory.json,semantic_reviews.json,error_taxonomy.md,case_studies.md,diagnostic_probes.json,improvement_backlog.md};
- data/m32/{evaluation_results.json,error_cases.json,review_queue.json,performance.json,freeze.json,quality_gates.json,reproducibility.json,integrity_final.json};
- data/m32/per_document/document-000.json a document-027.json e arquivo preliminary-v1 de saída inicial, preservado;
- este relatório e data/m32/independent_review.json; data/m32/integrity_pre_review.json também preserva a checagem anterior ao parecer.

Nenhum arquivo preexistente foi modificado. Lista/hashes finais no inventário suplementar. A saída inicial conservada não deve ser confundida com o canônico da raiz. Sem staging/commit, Legacy, SQL, Supabase, aquisição ou deploy.

## Y. Limites e incerteza restante

Piloto pequeno e selecionado, referência provisória, exposição prévia a labels, subset semântico intencional de 39 claims, 319 fields não revisados, matrizes baseadas em representative geométrico e não adjudicação de registro. Campos equivalentes por nomes/literal não garantem sentido. Alguns recortes de referência incluem menu ou excluem manchete relacionada; métricas estruturais não têm pureza semântica automática. Não há geometria PDF nem investigação exaustiva de cada navegação/related fragment; ausência de erro observado não prova ausência geral.

Os juízos de notícia concluída como signal precisam preservar a definição do produto: pista informativa pode ser útil, mas notificar oferta nova exige prova diferente. Há problemas reais de papel financeiro independentemente de label, mas isso não autoriza patch nesta milestone. Nenhum defeito de extração diagnosticado impede a avaliação offline ou concede promoção.

## Z. Parada e aceitação

**READY para avaliação offline exploratória**, com os vinte critérios de aceitação cobertos: baseline histórico preservado; corpus/previsões imutáveis; implementação reutilizável e metodologia documentada; alinhamento e denominadores explícitos; unannotated/unknown/abstain não tratados como negativos; modalidade/futuro/temporal/campos/evidência separados; erros reproduzíveis e backlog concreto; gates aprovados; nenhuma mudança de comportamento de produção; nenhuma métrica certificada alegada.

A revisão independente não encontrou medição enganosa confirmada nem inference leakage. Limitações e sugestões permanecem documentadas. Se revisão externa posterior reproduzir uma medição enganosa ou leakage não controlado, retornar **NOT READY**, sem compensar com contagem de testes ou maquiar denominadores.

READY significa somente avaliação offline exploratória honesta/reproduzível, não alta qualidade de extração, ground truth humano ou publicação. **M3.3 não iniciada. Aguardar revisão externa.**
