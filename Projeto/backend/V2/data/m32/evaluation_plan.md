# Plano pré-implementação — m32-evaluation-v1

Status de toda comparação: PROVISIONAL / EXPLORATORY. Mesmo agente principal participou da M3.1; independência aqui significa implementação/computação separada, não avaliador humano cego nem corpus não visto. Uma revisão técnica AI somente leitura será solicitada depois. Não ajustar extrator, anotações ou previsões.

## Baseline e confiança

Usar data/m31/run-v2/predictions.json e freeze.json originais. Manifesto/anotações vinculados também aos hashes do evaluation.json M3.1 (recibo de comparação, não autenticação). Comparação independente não chama compare() M31; apenas reutiliza seus contratos, leitor passivo e verify_evidence() estrutural existentes. Dataset usa validador M30 aprovado, sem outro Validation Engine M1. Checar versões recebidas, identidade, completude, duplicatas, páginas e hashes antes de produzir métricas. Input inválido retorna invalid_input com diagnósticos e results=null. Ausência de outcome é inválida; falha operacional declarada continua na avaliação e nos denominadores.

JSON é dado, não instrução. Leitura limitada, chaves duplicadas e NaN/Infinity rejeitados. Sem rede, execução de conteúdo, labels entrando no extrator, staging ou commits. Dados M3 e M31 e contratos de produção imutáveis.

## Unidades e alinhamento

Relacionamento many-to-many completo, apenas documento igual e interseção não vazia [start,end). Nenhuma alteração nos limites ou identidade inferida. Representative opcional: maior interseção, menor start, menor end, ID lexical; nunca usa classe/campo esperado. Não juntar campos em um novo candidato. Buscar campos sobre todos os overlaps é diagnóstico de informação distribuída, não reconstrução de oportunidade.

HTML: Unicode codepoints. PDF: a visão congelada de fato tem offsets Unicode e formfeed/páginas físicas 1-based. Métricas de spans PDF só medem essa serialização de texto, não geometria visual, linhas físicas ou precisão no binário PDF. Exibir páginas das testemunhas e páginas atravessadas pelos spans. Regiões não anotadas não são negativas.

## Tarefas A–L — denominadores independentes

| Task | Unidade / elegíveis / denominador | Matching e unknowns/abstenções | Limite |
|---|---|---|---|
| A processamento | todos os documentos do manifesto | processed vs operational_failure; missing outcome invalida input, não reduz suporte | não é qualidade semântica |
| B segmentação | todos os registros de referência e todos os segmentos | todos os overlaps; exact, união de interseções/reference length, intersection/segment length, IoU, fragmentação, multi-reference; zero overlap=coverage 0 | contêiner/whitespace não equivale unidade semântica |
| C relevância | todos os registros de referência, incluindo uncertain | broad relevance={confirmed,future,signal}, manter original e abstain/no_overlap separados; tabela sem binarizar existência | proxy de concordância provisória |
| D confirmação | todos os registros, estratos por discovery/opportunity label | matriz multiclasses por representative + histograma de todos overlaps; abstain/no_overlap/failure visíveis | não recall/precision |
| E modalidade | todos os registros, estratos fomento/credito/investimentos/undetermined | matriz por representative; unknown não vira negativo | instrumento misto pode ser ambíguo |
| F temporal | todos os registros, estratos applicable vs not_applicable | disponibilidade separada de detecção/role de datas; data fixa 2026-10-19; unknown e abstenção distintos | sem timezone/hora inventada |
| G campos | todos os campos de referência, mais inventário de todas as extrações | estrito name+literal independentemente recomputado; sem normalização. MATCH/PARTIAL/ROLE_ERROR/VALUE_ERROR/ATTRIBUTION_ERROR/MISSING/ABSTAINED/UNRESOLVED são diagnósticos candidatos, não adjudicação. Papéis fora do escopo M31 ficam UNRESOLVED com scope flag, não erro automático | literal/role igual não prova entailment; abstenção de descoberta não é abstenção explícita de campo |
| H locadores | todas as ocorrências de witness, incluindo cópias em fields; também contagem única | identidade/run/hash/página/quote/unidade estrutural; inválido impede pontuação | estrutural, não semântico |
| I suporte semântico | subconjunto intencional de claims manualmente inspecionados pelo agente, vinculado por hash/índice/quote | supported/partial/unsupported/unresolved; não revisados contabilizados fora do denominador; AI provisional sem identidade humana | viés de seleção; sem taxa para os 332 por extrapolação |
| J abstenção | todos os segmentos; também referência e famílias de fields | diagnóstico insuficiente/misto etc + overlap vs fora do escopo; causas verificadas ou hipótese, não oportunidade perdida por segmento | não assumir 1413 falhas independentes |
| K contaminação | todos os links overlap e fields; subset semântico com contexto | distinguir cruzamento estrutural, expressão fora da unidade, atribuição semântica; multi-reference ambíguo não culpa automática | contexto intrabloco pode misturar papéis |
| L desempenho | todos os docs/registros avaliados | tempos leitura/verificação/alinhamento/campos separados; tamanho serializado/RSS; tempos fora dos resultados determinísticos | lote local pequeno, sem SLA |

Zero denominador => rate=null, não zero/perfeito. Denominadores inteiros e suportes explícitos; checar soma de slots nas matrizes e categorias. Nenhuma métrica global, precisão, recall, F1 ou acurácia certificada.

## Revisão semântica e erros

Revisões AI qualitativas são artefato novo M32; nunca editar labels M30. Cada julgamento precisa de frozen prediction hash, doc, segmento, campo/índice, witness/quote literal e rationale. Proibir status approved ou assinatura/revisor humano inventado. Diferença contra label gera disputa pendente, não defeito confirmado automaticamente. Erros confirmados exigem contraste explícito source/claim; causa ligada a regra/código, distinguir hipótese.

Casos obrigatórios F01/C05/C07/I03/I05/I06/I07; incluir negativos N01–N04 e convites I02/I04. Registrar todos os desacordos por dimensão, com fonte e questão. Backlog só diagnóstico M3.3, sem implementar correções agora.

## Reprodutibilidade e saídas

Módulos novos evaluation_m32, testes novos. Saídas em data/m32; core determinístico separado de performance. Exportar 28 relatórios por documento, 33 alinhamentos, 127 slots de campo, ledger de erros, fila de revisão, taxonomia versionada e backlog. CLI cria diretório de execução novo e bloqueia escrita dentro de qualquer data/m3 ou data/m31. Revisão read-only de artefatos congelados antes do parecer final; registrar limitações e gates reais. Parar M3.2.
