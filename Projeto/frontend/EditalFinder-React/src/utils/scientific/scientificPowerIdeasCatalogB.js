import { definePowerIdea } from './scientificPowerIdeasHelpers';

/** Catálogo B — computação, HPC, Monte Carlo, IA, dados, autonomia, robótica (Fase 2J). */
export const POWER_IDEAS_CATALOG_B = {
  computacao_cientifica: [
    definePowerIdea({
      id: 'condicionamento-numerico',
      title: 'Condicionamento numérico',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Explica por que pequenas perturbações nos dados podem explodir o resultado — o limite prático entre modelo correto e solução inútil.',
      useFor: ['resolução de sistemas lineares', 'ajuste de parâmetros', 'inversão de dados'],
      prerequisites: ['álgebra linear', 'normas de vetor e matriz', 'análise de erro'],
      shortExplanation:
        'O número de condição mede a sensibilidade da saída à entrada. Problemas mal condicionados exigem reformulação, regularização ou maior precisão.',
      relatedTopics: ['estabilidade', 'decomposição LU', 'mínimos quadrados'],
      projectIdeas: [
        'Estimar κ(A) para matrizes de Vandermonde e discutir perda de dígitos',
        'Comparar método direto vs. iterativo no mesmo problema mal condicionado',
      ],
      professorQuestions: [
        'Quando o condicionamento é pior: na discretização ou na formulação contínua?',
        'Como detectar mal condicionamento sem calcular κ explicitamente?',
      ],
    }),
    definePowerIdea({
      id: 'estabilidade-numerica',
      title: 'Estabilidade numérica',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Separa erro inevitável de arredondamento de algoritmos que amplificam ruído — critério para confiar em uma simulação.',
      useFor: ['esquemas para EDOs/EDPs', 'álgebra linear iterativa', 'códigos de produção'],
      prerequisites: ['análise de erro', 'normas', 'condicionamento'],
      shortExplanation:
        'Um método é estável se erros iniciais não crescem sem controle ao longo das iterações ou passos de tempo.',
      relatedTopics: ['condição CFL', 'teorema de Lax', 'erro de arredondamento'],
      projectIdeas: [
        'Demonstrar instabilidade do método de Euler explícito em um oscilador',
        'Implementar o mesmo problema com esquema estável e comparar trajetórias',
      ],
      professorQuestions: [
        'Estabilidade zero ou A-estabilidade: qual exige mais do esquema?',
        'Como estabilidade se relaciona com passo de tempo em problemas stiff?',
      ],
    }),
    definePowerIdea({
      id: 'teorema-lax',
      title: 'Equivalência de Lax (consistência + estabilidade)',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Dá o roteiro padrão para provar que um esquema numérico realmente aproxima a equação contínua — base da análise de EDPs.',
      useFor: ['diferenças finitas', 'volumes finitos', 'análise de esquemas'],
      prerequisites: ['EDPs lineares', 'estabilidade', 'consistência/truncamento'],
      shortExplanation:
        'Para problemas bem postos e esquemas lineares: consistência mais estabilidade implicam convergência.',
      relatedTopics: ['erro de truncamento', 'CFL', 'estabilidade von Neumann'],
      projectIdeas: [
        'Verificar consistência e estabilidade de um esquema 1D e medir taxa de convergência',
        'Montar tabela comparando von Neumann vs. análise de energia',
      ],
      professorQuestions: [
        'A equivalência de Lax se estende a problemas não lineares da mesma forma?',
        'O que falha primeiro em esquemas práticos: consistência ou estabilidade?',
      ],
    }),
    definePowerIdea({
      id: 'erro-truncamento',
      title: 'Erro de truncamento (discretização)',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Quantifica o custo de substituir o contínuo pelo discreto — guia refinamento de malha e ordem do esquema.',
      useFor: ['refino de malha', 'estimativa de erro', 'ordem de convergência'],
      prerequisites: ['série de Taylor', 'EDOs/EDPs', 'ordem do método'],
      shortExplanation:
        'Surge ao truncar séries, diferenças ou integrais na discretização. Controla-se refinando Δx, Δt ou subindo a ordem.',
      relatedTopics: ['erro de arredondamento', 'Lax', 'métodos de Runge-Kutta'],
      projectIdeas: [
        'Medir ordem empírica p em ||e|| ∝ Δx^p para Laplace 1D',
        'Comparar erro de truncamento vs. arredondamento em double e extended',
      ],
      professorQuestions: [
        'Quando o erro de truncamento deixa de dominar o de arredondamento?',
        'Como estimativa de erro a posteriori complementa análise de truncamento?',
      ],
    }),
    definePowerIdea({
      id: 'erro-arredondamento',
      title: 'Erro de arredondamento',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Define o piso de precisão em float e explica resultados “quase iguais” que divergem — essencial em álgebra linear longa.',
      useFor: ['precisão em HPC', 'cancelamento catastrófico', 'validação numérica'],
      prerequisites: ['representação IEEE-754', 'análise de erro'],
      shortExplanation:
        'Erros introduzidos pela aritmética finita. Acumulam-se em milhões de operações e interagem com condicionamento.',
      relatedTopics: ['condicionamento', 'estabilidade', 'verificação e validação'],
      projectIdeas: [
        'Ilustrar cancelamento catastrófico em fórmulas equivalentes para raízes de quadrática',
        'Rastrear dígitos significativos em produto de muitas matrizes ortogonais',
      ],
      professorQuestions: [
        'Em que situações mixed precision reduz erro sem perder confiança?',
        'Como reprodutibilidade bit-a-bit se choca com paralelismo?',
      ],
    }),
    definePowerIdea({
      id: 'nyquist-shannon',
      title: 'Teorema de Nyquist–Shannon',
      type: 'teorema',
      level: 'intermediario',
      whyItMatters:
        'Liga taxa de amostragem à frequência máxima do sinal — evita aliasing em simulação, sensoriamento e pós-processamento.',
      useFor: ['discretização temporal', 'filtragem', 'reconstrução de sinais'],
      prerequisites: ['transformada de Fourier', 'amostragem'],
      shortExplanation:
        'Para reconstruir um sinal limitado em banda, amostre com frequência maior que o dobro da frequência de Nyquist.',
      relatedTopics: ['erro de truncamento', 'CFL', 'instrumentação'],
      projectIdeas: [
        'Demonstrar aliasing ao subamostrar uma senoide e recuperar com filtro anti-aliasing',
        'Relacionar Δt em EDPs com frequências espaciais da malha',
      ],
      professorQuestions: [
        'Como o teorema se aplica a campos 2D/3D em malhas não uniformes?',
        'O que muda para sinais não estacionários ou espectros largos?',
      ],
    }),
    definePowerIdea({
      id: 'decomposicao-lu',
      title: 'Decomposição LU',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Transforma sistemas lineares em triangularização reutilizável — núcleo de solvers diretos em simulação e otimização.',
      useFor: ['sistemas Ax=b', 'inversão implícita', 'passos de Newton'],
      prerequisites: ['eliminação de Gauss', 'pivotamento', 'complexidade O(n³)'],
      shortExplanation:
        'Fatora A = LU (com pivotamento P quando necessário). Resolve múltiplos b com forward/back substitution barato.',
      relatedTopics: ['condicionamento', 'autovalores', 'mínimos quadrados'],
      projectIdeas: [
        'Implementar LU com pivotamento parcial e comparar com numpy.linalg.solve',
        'Reutilizar fatores LU em Newton para raiz de f(x)=0',
      ],
      professorQuestions: [
        'Quando LU perde para métodos iterativos em matrizes esparsas grandes?',
        'Como fill-in em LU esparsa afeta memória e tempo?',
      ],
    }),
    definePowerIdea({
      id: 'autovalores',
      title: 'Autovalores e autovetores',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Revelam modos de oscilação, crescimento e direções privilegiadas — leitura rápida da dinâmica linear de um sistema.',
      useFor: ['análise de estabilidade', 'PCA', 'modos normais', 'espectro de operadores'],
      prerequisites: ['álgebra linear', 'autoadjunção', 'diagonalização'],
      shortExplanation:
        'Av = λv descreve invariantes lineares. Espectros explicam stiffness, bifurcações lineares e bases modais.',
      relatedTopics: ['condicionamento', 'mínimos quadrados', 'estabilidade'],
      projectIdeas: [
        'Classificar equilíbrio de um sistema linear pelo sinal dos autovalores',
        'Calcular modos vibracionais de uma malha discreta 1D',
      ],
      professorQuestions: [
        'Autovalores de operadores discretos convergem para o contínuo em que norma?',
        'Quando métodos iterativos (Arnoldi) são preferíveis à diagonalização completa?',
      ],
    }),
    definePowerIdea({
      id: 'minimos-quadrados',
      title: 'Método dos mínimos quadrados',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Formaliza ajuste quando há mais equações que incógnitas ou ruído — ponte entre experimento, estatística e modelagem.',
      useFor: ['calibração', 'regressão', 'inversão linear', 'redução de dimensão'],
      prerequisites: ['álgebra linear', 'projeções', 'derivadas'],
      shortExplanation:
        'Minimiza ||Ax − b||². Solução normal AᵀAx = Aᵀb; em mal condicionamento usa-se QR ou SVD.',
      relatedTopics: ['decomposição LU', 'condicionamento', 'erro de truncamento'],
      projectIdeas: [
        'Ajustar parâmetros de um modelo não linear via Gauss–Newton',
        'Comparar MQ com SVD em dados ruidosos e quase colineares',
      ],
      professorQuestions: [
        'Como pesos e regularização alteram a interpretação estatística do MQ?',
        'Quando MQ ponderado é preferível a máxima verossimilhança?',
      ],
    }),
    definePowerIdea({
      id: 'runge-kutta',
      title: 'Métodos de Runge–Kutta',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Família padrão para integrar EDOs com ordem controlada — usada em praticamente todo simulador dinâmico.',
      useFor: ['integração temporal', 'sistemas não lineares', 'controle de passo adaptativo'],
      prerequisites: ['EDOs', 'série de Taylor', 'estabilidade'],
      shortExplanation:
        'Combinam avaliações de f em estágios intermediários para alta ordem sem Jacobianas. RK4 é o ponto de partida clássico.',
      relatedTopics: ['estabilidade', 'CFL', 'erro de truncamento'],
      projectIdeas: [
        'Implementar RK4 com passo adaptativo em problema stiff e comparar com BDF',
        'Medir ordem empírica em problema com solução analítica',
      ],
      professorQuestions: [
        'RK explícito vs. implícito: onde cada um é obrigatório?',
        'Como emparelhar RK com conservação de energia em Hamiltonianos?',
      ],
    }),
    definePowerIdea({
      id: 'condicao-cfl',
      title: 'Condição CFL',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Liga passo de tempo à malha espacial para esquemas explícitos — evita simulações que “explodem” por violação física-numérica.',
      useFor: ['EDPs hiperbólicas/parabólicas', 'malha adaptativa', 'HPC com passo explícito'],
      prerequisites: ['ondas discretas', 'estabilidade von Neumann', 'velocidade de propagação'],
      shortExplanation:
        'Δt ≤ C·Δx/λ_max, com λ_max dependendo do esquema e da velocidade característica. Violação gera instabilidade.',
      relatedTopics: ['estabilidade', 'Lax', 'Nyquist–Shannon'],
      projectIdeas: [
        'Mapear região estável de um esquema advecção-difusão 1D',
        'Automatizar escolha de Δt a partir de malha e CFL alvo',
      ],
      professorQuestions: [
        'CFL em múltiplas dimensões e malhas não estruturadas: quais conservadorismos?',
        'Esquemas implicitamente estáveis ainda precisam de CFL para precisão?',
      ],
    }),
    definePowerIdea({
      id: 'verificacao-validacao',
      title: 'Verificação e validação (V&V)',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'Distingue “o código está certo” de “o modelo representa a realidade” — cultura necessária em engenharia e pesquisa computacional.',
      useFor: ['simulação credível', 'publicação', 'regulação', 'benchmarks'],
      prerequisites: ['análise de erro', 'testes unitários', 'dados experimentais'],
      shortExplanation:
        'Verificação: implementação correta do modelo matemático. Validação: concordância com fenômeno real dentro de incertezas.',
      relatedTopics: ['erro de truncamento', 'condicionamento', 'Monte Carlo'],
      projectIdeas: [
        'Montar plano V&V para um código 1D com solução analítica e caso experimental',
        'Documentar incertezas de entrada e saída em um estudo de sensibilidade',
      ],
      professorQuestions: [
        'Que evidências mínimas você exigiria antes de usar um código em decisão de projeto?',
        'Como separar erro de modelo de erro numérico na validação?',
      ],
    }),
  ],

  hpc: [
    definePowerIdea({
      id: 'lei-amdahl',
      title: 'Lei de Amdahl',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Mostra que a fração serial limita o ganho de paralelismo — explica por que “mais núcleos” nem sempre acelera.',
      useFor: ['planejamento de paralelização', 'expectativa de speedup', 'otimização de gargalos'],
      prerequisites: ['paralelismo', 'tempo de execução', 'fração serial'],
      shortExplanation:
        'Speedup ≤ 1 / (s + (1−s)/N), com s serial. Mesmo s pequeno impõe teto quando N → ∞.',
      relatedTopics: ['Gustafson', 'escalonamento forte', 'balanceamento de carga'],
      projectIdeas: [
        'Medir s em um loop com seção crítica artificial e plotar speedup vs. N',
        'Identificar trecho serial dominante em um código real',
      ],
      professorQuestions: [
        'Amdahl vs. medição real: onde overhead de comunicação entra?',
        'Quando vale reescrever o serial em vez de paralelizar o resto?',
      ],
    }),
    definePowerIdea({
      id: 'lei-gustafson',
      title: 'Lei de Gustafson',
      type: 'lei',
      level: 'avancado',
      whyItMatters:
        'Reenquadra o problema quando o tamanho cresce com os recursos — visão mais otimista que Amdahl para muitas simulações.',
      useFor: ['computação em larga escala', 'weak scaling', 'problemas de fronteira'],
      prerequisites: ['Amdahl', 'escalonamento', 'tamanho do problema'],
      shortExplanation:
        'Ao aumentar o problema com N, a fração “serial” efetiva pode cair; o tempo fixo serial deixa de dominar tanto.',
      relatedTopics: ['Amdahl', 'weak scaling', 'roofline'],
      projectIdeas: [
        'Comparar speedup forte e fraco no mesmo solver para malhas 2ⁿ',
        'Argumentar com dados se seu problema segue Amdahl ou Gustafson',
      ],
      professorQuestions: [
        'Em que classes de PDEs o tamanho e o paralelismo crescem juntos naturalmente?',
        'Gustafson justifica ignorar o serial residual?',
      ],
    }),
    definePowerIdea({
      id: 'escalonamento-forte-fraco',
      title: 'Escalonamento forte e fraco',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Define o experimento de benchmark em clusters — sem isso, gráficos de speedup são incomparáveis.',
      useFor: ['benchmark HPC', 'capacidade de máquina', 'comparação de algoritmos'],
      prerequisites: ['paralelismo', 'Amdahl', 'tamanho de malha'],
      shortExplanation:
        'Forte: problema fixo, mais processadores. Fraco: problema por processador fixo, malha total cresce com N.',
      relatedTopics: ['Gustafson', 'MPI', 'balanceamento de carga'],
      projectIdeas: [
        'Rodar strong e weak scaling do mesmo kernel e interpretar inclinações',
        'Relacionar queda de eficiência com comunicação vs. trabalho local',
      ],
      professorQuestions: [
        'Qual modo de escalonamento reflete melhor o uso em produção no seu domínio?',
        'Como malha adaptativa complica weak scaling?',
      ],
    }),
    definePowerIdea({
      id: 'mpi-paralelismo',
      title: 'MPI (Message Passing Interface)',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'Padrão para memória distribuída em clusters — necessário para simulações que não cabem em um nó.',
      useFor: ['clusters', 'domínios decomposição', 'I/O paralelo'],
      prerequisites: ['paralelismo', 'latência/banda', 'modelo de memória'],
      shortExplanation:
        'Processos com memória privada trocam mensagens (send/recv, collective). Escala a milhares de nós com topologia de rede.',
      relatedTopics: ['OpenMP', 'balanceamento de carga', 'roofline'],
      projectIdeas: [
        'Implementar halo exchange 2D com MPI_Isend/Irecv',
        'Medir tempo de um Allreduce vs. tamanho de mensagem na máquina local',
      ],
      professorQuestions: [
        'MPI + OpenMP híbrido: quando o overhead compensa?',
        'Como escolher granularidade de domínio para minimizar comunicação?',
      ],
    }),
    definePowerIdea({
      id: 'openmp-shared',
      title: 'OpenMP (memória compartilhada)',
      type: 'ferramenta-computacional',
      level: 'basico',
      whyItMatters:
        'Paraleliza loops e regiões em um socket com poucas linhas — ganho rápido em núcleos multicore.',
      useFor: ['loops intensivos', 'nós multicore', 'híbrido com MPI'],
      prerequisites: ['threads', 'race conditions', 'reduções'],
      shortExplanation:
        'Diretivas pragma criam equipes de threads; work-sharing distribui iterações. Exige atenção a variáveis shared/private.',
      relatedTopics: ['MPI', 'localidade de cache', 'Amdahl'],
      projectIdeas: [
        'Paralelizar produto matriz-vetor com reduction e comparar speedup',
        'Diagnosticar false sharing alterando padding de estruturas',
      ],
      professorQuestions: [
        'Schedule static vs. dynamic: impacto em carga desbalanceada?',
        'OpenMP 5.x e offload: ainda vale para GPUs no seu caso?',
      ],
    }),
    definePowerIdea({
      id: 'localidade-cache',
      title: 'Localidade de cache',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Explica por que algoritmos assintoticamente iguais podem diferir 10× — o gargalo real em HPC moderno.',
      useFor: ['otimização de kernels', 'ordem de loops', 'estruturas de dados'],
      prerequisites: ['hierarquia de memória', 'complexidade', 'matrizes'],
      shortExplanation:
        'Acesso temporal e espacial próximo mantém linhas de cache quentes. Loop blocking (tiling) melhora reuso.',
      relatedTopics: ['roofline', 'OpenMP', 'balanceamento de carga'],
      projectIdeas: [
        'Comparar i-j vs. j-i em multiplicação de matrizes e reportar GFLOPS',
        'Reordenar dados struct-of-arrays vs. array-of-structs em um stencil',
      ],
      professorQuestions: [
        'Como o roofline identifica se você é bound por memória ou compute?',
        'Prefetch e vetorização: quando o compilador não basta?',
      ],
    }),
    definePowerIdea({
      id: 'modelo-roofline',
      title: 'Modelo roofline',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Une pico de FLOPS e banda de memória num gráfico — mostra se otimizar compute ou tráfego de dados.',
      useFor: ['tuning de kernels', 'escolha de precisão', 'comparação de hardware'],
      prerequisites: ['localidade de cache', 'FLOPS', 'arithmetic intensity'],
      shortExplanation:
        'Plota performance vs. intensidade aritmética (FLOPs/byte). O “teto” é o mínimo entre limite de compute e de memória.',
      relatedTopics: ['localidade de cache', 'MPI', 'escalonamento'],
      projectIdeas: [
        'Posicionar um stencil 3D no diagrama roofline da máquina',
        'Propor mudança (tiling, fused ops) para subir intensidade aritmética',
      ],
      professorQuestions: [
        'Roofline em GPUs e CPUs: quais métricas de banda usar?',
        'O modelo captura latência de MPI em multi-nó?',
      ],
    }),
    definePowerIdea({
      id: 'balanceamento-carga',
      title: 'Balanceamento de carga',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Evita processadores ociosos quando o trabalho é irregular — comum em malhas adaptativas e Monte Carlo.',
      useFor: ['MPI dinâmico', 'particionamento de malha', 'filas de tarefas'],
      prerequisites: ['MPI', 'paralelismo', 'desbalanceamento'],
      shortExplanation:
        'Redistribui trabalho ou dados para equalizar tempo por rank. Pode ser estático (partição) ou dinâmico (work stealing).',
      relatedTopics: ['Amdahl', 'escalonamento', 'Monte Carlo'],
      projectIdeas: [
        'Simular desbalanceamento e aplicar work stealing em Monte Carlo',
        'Comparar particionamento geométrico vs. carga em grafo de malha',
      ],
      professorQuestions: [
        'Custo de rebalanceamento dinâmico: quando amortiza?',
        'Balanceamento em GPU multi-node com MPI: desafios específicos?',
      ],
    }),
  ],

  monte_carlo: [
    definePowerIdea({
      id: 'lei-grandes-numeros',
      title: 'Lei dos grandes números',
      type: 'lei',
      level: 'basico',
      whyItMatters:
        'Fundamenta por que médias de amostras convergem — sem isso, Monte Carlo parece “sorte” em vez de estimativa controlada.',
      useFor: ['estimativa de médias', 'erro estatístico', 'convergência MC'],
      prerequisites: ['probabilidade', 'variância', 'amostragem'],
      shortExplanation:
        'A média amostral converge para a esperança quando N cresce. Velocidade depende da variância do estimador.',
      relatedTopics: ['teorema central do limite', 'erro-1-sqrt-n', 'convergência MC'],
      projectIdeas: [
        'Estimar π por dardo e mostrar convergência da média com N',
        'Plotar erro empírico vs. 1/√N para uma integral MC',
      ],
      professorQuestions: [
        'LLN forte vs. fraca: qual você usa ao justificar um código MC?',
        'Quando correlações entre amostras invalidam a LLN na prática?',
      ],
    }),
    definePowerIdea({
      id: 'teorema-central-limite',
      title: 'Teorema central do limite',
      type: 'teorema',
      level: 'intermediario',
      whyItMatters:
        'Permite construir intervalos de confiança e testes — transforma flutuação estocástica em quantificação de incerteza.',
      useFor: ['intervalos de confiança', 'bootstrap', 'análise de erro MC'],
      prerequisites: ['LLN', 'variância', 'distribuição normal'],
      shortExplanation:
        'Somas (ou médias) de variáveis i.i.d. tendem à normalidade; escala de erro ~ σ/√N para estimadores bem comportados.',
      relatedTopics: ['erro-1-sqrt-n', 'bootstrap', 'inferência bayesiana'],
      projectIdeas: [
        'Histogramar distribuição de estimadores MC repetidos e comparar com normal',
        'Construir IC 95% para uma integral e verificar cobertura empírica',
      ],
      professorQuestions: [
        'CLT falha para quais distribuições relevantes em física (caudas pesadas)?',
        'Como CLT se altera com amostras correlacionadas (cadeias MCMC)?',
      ],
    }),
    definePowerIdea({
      id: 'amostragem-rejeicao',
      title: 'Amostragem por rejeição',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Método universal para amostrar distribuições complicadas — base conceitual antes de MCMC e importance sampling.',
      useFor: ['distribuições não padronizadas', 'geometria complexa', 'protótipos'],
      prerequisites: ['PDF', 'proposta majorante', 'eficiência de aceitação'],
      shortExplanation:
        'Amostra de uma proposta q e aceita com probabilidade proporcional a p/q. Simples, mas pode ser ineficiente se q for pobre.',
      relatedTopics: ['importance sampling', 'Metropolis–Hastings', 'variância'],
      projectIdeas: [
        'Amostrar de mistura gaussiana com envelope uniforme e medir taxa de aceitação',
        'Desenhar região 2D e amostrar pontos uniformes por rejeição',
      ],
      professorQuestions: [
        'Como escolher q para manter aceitação alta sem viés?',
        'Rejeição vs. transformação inversa: critérios de escolha?',
      ],
    }),
    definePowerIdea({
      id: 'importance-sampling',
      title: 'Importance sampling',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Reduz variância focando amostras onde o integrando é grande — essencial em raros eventos e transporte.',
      useFor: ['eventos raros', 'transporte de partículas', 'redução de variância'],
      prerequisites: ['expectativa', 'pesos', 'viés e variância'],
      shortExplanation:
        'Amostra de q com pesos p/q. Com q bem escolhida, a variância do estimador cai drasticamente.',
      relatedTopics: ['rejeição', 'variance reduction', 'russian roulette'],
      projectIdeas: [
        'Estimar cauda de distribuição com IS ingênuo vs. q adaptada',
        'Implementar biased sampling em penetração 1D slab',
      ],
      professorQuestions: [
        'Como detectar pesos explosivos (variance inflation) em IS adaptativo?',
        'IS em MCMC: quais armadilhas de pesos auto-normalizados?',
      ],
    }),
    definePowerIdea({
      id: 'cadeias-markov',
      title: 'Cadeias de Markov',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Modelo de dependência temporal em MCMC — entender memória e estacionariedade evita amostras falsamente independentes.',
      useFor: ['MCMC', 'processos estocásticos', 'tempo de mistura'],
      prerequisites: ['probabilidade', 'matriz de transição', 'estacionariedade'],
      shortExplanation:
        'O futuro depende só do presente. Em MCMC, construímos cadeias cuja distribuição estacionária é o alvo p.',
      relatedTopics: ['Metropolis–Hastings', 'convergência MC', 'autocorrelação'],
      projectIdeas: [
        'Simular cadeia finita 2-estados e tempo até equilíbrio',
        'Estimar autocorrelação de cadeia MCMC e effective sample size',
      ],
      professorQuestions: [
        'Critérios práticos para “burn-in” além de olhar gráficos?',
        'Cadeias não reversíveis: quando valem a pena?',
      ],
    }),
    definePowerIdea({
      id: 'metropolis-hastings',
      title: 'Metropolis–Hastings',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Algoritmo workhorse de MCMC — amostra posteriors e energias sem normalização, ubíquo em física e estatística.',
      useFor: ['bayesiana', 'simulação estatística', 'posteriors complexas'],
      prerequisites: ['cadeias de Markov', 'detailed balance', 'proposta'],
      shortExplanation:
        'Propõe movimento e aceita/rejeita com critério que preserva p. Generaliza Metropolis com propostas assimétricas.',
      relatedTopics: ['cadeias de Markov', 'importance sampling', 'convergência'],
      projectIdeas: [
        'MH em distribuição 2D multimodal com proposta gaussiana ajustável',
        'Comparar random walk MH vs. HMC em mesmo alvo (conceitual)',
      ],
      professorQuestions: [
        'Passo da proposta: trade-off aceitação vs. mixing?',
        'Diagnósticos R̂ e ESS: o que exigir antes de publicar?',
      ],
    }),
    definePowerIdea({
      id: 'variance-reduction',
      title: 'Redução de variância',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Ataca o 1/√N com engenharia do estimador — diferença entre simulação viável e inviável em eventos raros.',
      useFor: ['transporte', 'finanças', 'confiabilidade', 'MC de produção'],
      prerequisites: ['variância', 'covariância', 'estimadores'],
      shortExplanation:
        'Técnicas (controle, antitético, estratificação, IS) diminuem σ do estimador sem aumentar N linearmente.',
      relatedTopics: ['importance sampling', 'russian roulette', 'erro-1-sqrt-n'],
      projectIdeas: [
        'Implementar variáveis antitéticas em estimativa de integral e reportar ganho',
        'Combinar controle com analítico parcial em transporte 1D',
      ],
      professorQuestions: [
        'Como combinar várias técnicas sem double-counting de ganho?',
        'Variance reduction em GPU batch MC: o que paraleliza bem?',
      ],
    }),
    definePowerIdea({
      id: 'russian-roulette-splitting',
      title: 'Russian roulette e splitting',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Controla população de histórias com peso — truque central em códigos de transporte Monte Carlo profissionais.',
      useFor: ['transporte de nêutrons/fótons', 'partículas com peso', 'deep penetration'],
      prerequisites: ['pesos MC', 'viés', 'variance reduction'],
      shortExplanation:
        'Russian roulette elimina partículas improváveis com compensação de peso; splitting multiplica ramos em regiões importantes.',
      relatedTopics: ['importance sampling', 'variance reduction', 'convergência'],
      projectIdeas: [
        'Simular slab com splitting na entrada e roulette na saída',
        'Documentar como pesos preservam esperança do fluxo',
      ],
      professorQuestions: [
        'Limites de splitting antes de explodir memória/tempo?',
        'Como auditar imparcialidade quando várias VR são ligadas?',
      ],
    }),
    definePowerIdea({
      id: 'erro-estatistico-sqrt-n',
      title: 'Erro estatístico ∝ 1/√N',
      type: 'identidade-matematica',
      level: 'basico',
      whyItMatters:
        'Regra de bolso para planejar tempo de CPU — dobrar precisão custa ~4× amostras na MC ingênua.',
      useFor: ['planejamento de run', 'critério de parada', 'comparação de métodos'],
      prerequisites: ['CLT', 'variância', 'LLN'],
      shortExplanation:
        'Erro típico de Monte Carlo escala como σ/√N. Redução de variância muda σ efetivo, não a lei de potência básica.',
      relatedTopics: ['variance reduction', 'convergência', 'bootstrap'],
      projectIdeas: [
        'Log-log de erro vs. N para confirmar inclinação −1/2',
        'Calcular N necessário para tolerância ε dada σ estimada piloto',
      ],
      professorQuestions: [
        'Quando erro deixa de seguir 1/√N (burn-in, pesos, caudas)?',
        'Adaptive MC: como reportar erro sem viés de parada?',
      ],
    }),
    definePowerIdea({
      id: 'convergencia-monte-carlo',
      title: 'Convergência em Monte Carlo',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Distingue “parei de rodar” de “estimativa confiável” — evita decisões baseadas em amostra ainda misturando.',
      useFor: ['critério de parada', 'MCMC diagnostics', 'QA de códigos'],
      prerequisites: ['LLN', 'CLT', 'autocorrelação'],
      shortExplanation:
        'Convergência quase certa da estimativa; em MCMC, exige também mistura e amostras efetivamente independentes.',
      relatedTopics: ['Metropolis–Hastings', 'bootstrap', 'erro-1-sqrt-n'],
      projectIdeas: [
        'Monitorar média cumulativa e janelas móveis de variância',
        'Comparar convergência IS vs. MCMC no mesmo alvo 2D',
      ],
      professorQuestions: [
        'Testes Gelman-Rubin vs. heurísticas de platô: o que você confia?',
        'Convergência em transporte com VR: como separar estatística de física?',
      ],
    }),
    definePowerIdea({
      id: 'bootstrap',
      title: 'Bootstrap',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Quantifica incerteza sem fórmulas analíticas — útil quando a estatística do estimador é intrincada.',
      useFor: ['intervalos de confiança', 'erro de estimadores complexos', 'validação'],
      prerequisites: ['amostragem com reposição', 'estimadores', 'CLT'],
      shortExplanation:
        'Reamostra os dados (ou blocos) muitas vezes para distribuição do estimador. Non-paramétrico e flexível.',
      relatedTopics: ['CLT', 'inferência bayesiana', 'convergência MC'],
      projectIdeas: [
        'Bootstrap paramétrico vs. não paramétrico para média de MC repetidos',
        'Bootstrap em série temporal com block bootstrap',
      ],
      professorQuestions: [
        'Bootstrap em amostras MCMC correlacionadas: quais variantes?',
        'Quando bootstrap falha (amostras muito pequenas)?',
      ],
    }),
    definePowerIdea({
      id: 'inferencia-bayesiana',
      title: 'Inferência bayesiana',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Incorpora incerteza e conhecimento prévio explicitamente — framework natural para calibrar modelos com dados ruidosos.',
      useFor: ['calibração de parâmetros', 'UQ', 'MCMC', 'modelos hierárquicos'],
      prerequisites: ['Teorema de Bayes', 'verossimilhança', 'priors'],
      shortExplanation:
        'Atualiza crenças: posterior ∝ likelihood × prior. Integrais em θ são resolvidas por MCMC ou métodos determinísticos.',
      relatedTopics: ['Metropolis–Hastings', 'bootstrap', 'Gaussian processes'],
      projectIdeas: [
        'Inferir parâmetro de decaimento com prior log-normal e likelihood Poisson',
        'Comparar MAP vs. média posterior em problema com multimodalidade',
      ],
      professorQuestions: [
        'Priors informativos vs. reguladores: como justificar em física?',
        'Bayesiano vs. máxima verossimilhança em dados escassos?',
      ],
    }),
  ],

  ia_cientifica: [
    definePowerIdea({
      id: 'tradeoff-vies-variancia',
      title: 'Compromisso viés–variância',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Organiza por que modelos simples e complexos falham de modos opostos — mapa mental para escolher complexidade em ciência.',
      useFor: ['seleção de modelos', 'regularização', 'interpretação de erro'],
      prerequisites: ['erro de generalização', 'ajuste', 'variância'],
      shortExplanation:
        'Erro total decomõe em viés (rigidez) e variância (sensibilidade aos dados). Complexidade move o equilíbrio entre ambos.',
      relatedTopics: ['overfitting', 'regularização', 'validação cruzada'],
      projectIdeas: [
        'Curva de erro treino/teste vs. grau de polinômio em dados sintéticos',
        'Relacionar capacidade de rede com viés/variância em dataset pequeno',
      ],
      professorQuestions: [
        'Viés–variância ainda orienta deep learning com milhões de parâmetros?',
        'Como dados ruidosos de experimento deslocam o ponto ótimo?',
      ],
    }),
    definePowerIdea({
      id: 'overfitting',
      title: 'Overfitting (sobreajuste)',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Alerta para modelos que decoram ruído — risco alto quando dados experimentais são caros e escassos.',
      useFor: ['validação', 'regularização', 'publicação com ML'],
      prerequisites: ['treino/teste', 'viés–variância', 'generalização'],
      shortExplanation:
        'Desempenho excelente no treino e ruim em dados novos. Combatido com mais dados, regularização ou modelos mais simples.',
      relatedTopics: ['validação cruzada', 'regularização', 'surrogate models'],
      projectIdeas: [
        'Mostrar gap treino/validação ao aumentar parâmetros de rede',
        'Aplicar early stopping e comparar curvas de perda',
      ],
      professorQuestions: [
        'Em física, quando um “bom ajuste” ainda é fisicamente inaceitável?',
        'Data leakage vs. overfitting: como distinguir na prática?',
      ],
    }),
    definePowerIdea({
      id: 'regularizacao',
      title: 'Regularização',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Incorpora prior físico ou estatístico no ajuste — torna modelos identificáveis e generalizáveis com poucos dados.',
      useFor: ['regressão', 'redes neurais', 'inversão de parâmetros'],
      prerequisites: ['viés–variância', 'otimização', 'normas L1/L2'],
      shortExplanation:
        'Penaliza complexidade (L2, L1, dropout, priors). Equivale a impor suavidade, esparsidade ou leis de conservação soft.',
      relatedTopics: ['PINNs', 'validação cruzada', 'Bayesian optimization'],
      projectIdeas: [
        'Ridge vs. Lasso em espectro ruidoso e interpretar coeficientes',
        'Adicionar termo de penalidade física em loss de rede',
      ],
      professorQuestions: [
        'Regularização como prior bayesiano: exemplos no seu domínio?',
        'PINN já é regularização suficiente ou precisa de L2 adicional?',
      ],
    }),
    definePowerIdea({
      id: 'validacao-cruzada',
      title: 'Validação cruzada',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Estima generalização sem desperdiçar dados raros — padrão antes de treinar modelo final em produção científica.',
      useFor: ['seleção de hiperparâmetros', 'comparação de modelos', 'datasets pequenos'],
      prerequisites: ['partição treino/teste', 'métricas', 'overfitting'],
      shortExplanation:
        'Rotaciona folds de validação para média de erro out-of-sample. k-fold e LOOCV são variantes comuns.',
      relatedTopics: ['overfitting', 'active learning', 'quantificação de incerteza'],
      projectIdeas: [
        'Grid search com k-fold em modelo de substituição (surrogate)',
        'Analisar variância da métrica entre folds em dataset experimental',
      ],
      professorQuestions: [
        'CV em séries temporais ou dados espaciais: qual esquema usar?',
        'Nested CV: quando é obrigatório vs. overkill?',
      ],
    }),
    definePowerIdea({
      id: 'processos-gaussianos',
      title: 'Processos gaussianos',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Fornecem média e incerteza em regressão — ideais para substitutos baratos de simulações caras.',
      useFor: ['surrogate models', 'otimização bayesiana', 'kriging'],
      prerequisites: ['matrizes de covariância', 'kernels', 'regressão'],
      shortExplanation:
        'Distribuição sobre funções com marginais gaussianas. Kernel define suavidade; incerteza cresce longe dos dados.',
      relatedTopics: ['Bayesian optimization', 'active learning', 'UQ'],
      projectIdeas: [
        'GP em função 1D desconhecida e plotar banda de incerteza',
        'Comparar GP com rede pequena em mesmo budget de pontos',
      ],
      professorQuestions: [
        'Kernels físicos (periodic, Matérn): como escolher com poucos pontos?',
        'Escalabilidade O(n³): alternativas aceitáveis em produção?',
      ],
    }),
    definePowerIdea({
      id: 'otimizacao-bayesiana',
      title: 'Otimização bayesiana',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Explora espaço de parâmetros com poucas avaliações de simulador caro — padrão em calibração e design de experimentos.',
      useFor: ['hiperparâmetros', 'calibração', 'design computacional'],
      prerequisites: ['GP', 'acquisition functions', 'incerteza'],
      shortExplanation:
        'Modela superfície de resposta com GP e escolhe próximo ponto via acquisition (EI, UCB). Balanceia exploração e explotação.',
      relatedTopics: ['processos gaussianos', 'active learning', 'surrogate models'],
      projectIdeas: [
        'BO para minimizar tempo de simulação 1D com orçamento de 20 calls',
        'Comparar grid search vs. BO no mesmo simulador ruidoso',
      ],
      professorQuestions: [
        'Restrições físicas (monotonicidade) entram como prior ou pós-processo?',
        'BO multi-objetivo: como apresentar trade-offs ao orientador?',
      ],
    }),
    definePowerIdea({
      id: 'pinns',
      title: 'Physics-Informed Neural Networks (PINNs)',
      type: 'metodo',
      level: 'pesquisa',
      whyItMatters:
        'Embute EDPs e condições de contorno na loss — tenta unir flexibilidade de redes com leis físicas explícitas.',
      useFor: ['EDPs com dados esparsos', 'inversão', 'campos continuados'],
      prerequisites: ['EDPs', 'autodiff', 'otimização'],
      shortExplanation:
        'A rede aproxima a solução; resíduos da equação e BCs entram como termos de penalidade no treinamento.',
      relatedTopics: ['regularização', 'surrogate models', 'UQ'],
      projectIdeas: [
        'PINN 1D para Poisson com dados de contorno parciais',
        'Ablation: loss só dados vs. dados + física',
      ],
      professorQuestions: [
        'PINNs substituem CFD bem estabelecido em que regimes?',
        'Como quantificar incerteza em PINNs para decisão de engenharia?',
      ],
    }),
    definePowerIdea({
      id: 'surrogate-models',
      title: 'Modelos substitutos (surrogate)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Trocam simulação cara por predição rápida — viabilizam otimização, UQ e milhares de cenários.',
      useFor: ['design', 'sensibilidade', 'digital twin leve'],
      prerequisites: ['amostragem de design', 'GP ou redes', 'erro de generalização'],
      shortExplanation:
        'Ajustam metamodelo (GP, polinômio, rede) a um design of experiments sobre o simulador verdadeiro.',
      relatedTopics: ['GP', 'active learning', 'validação cruzada'],
      projectIdeas: [
        'Latin hypercube + surrogate de tempo de execução de código legado',
        'Validar surrogate fora do DOE e reportar erro máximo',
      ],
      professorQuestions: [
        'Quando surrogate falha em extrapolação fora do DOE?',
        'Co-kriging multi-fidelidade: vale em seu laboratório?',
      ],
    }),
    definePowerIdea({
      id: 'active-learning',
      title: 'Aprendizado ativo',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Escolhe o próximo experimento ou simulação — maximiza informação por custo em laboratório e HPC.',
      useFor: ['aquisição de dados', 'rotulagem', 'DOE adaptativo'],
      prerequisites: ['incerteza', 'surrogate', 'critérios de aquisição'],
      shortExplanation:
        'Seleciona pontos onde o modelo é incerto ou onde o ganho esperado na tarefa é maior. Reduz N total necessário.',
      relatedTopics: ['Bayesian optimization', 'GP', 'explainability'],
      projectIdeas: [
        'Loop ativo: GP + incerteza para amostrar fronteira de fase 2D',
        'Comparar random vs. uncertainty sampling no mesmo budget',
      ],
      professorQuestions: [
        'Active learning com simulador ruidoso: como propagar incerteza?',
        'Critérios diversity vs. uncertainty: quando combinar?',
      ],
    }),
    definePowerIdea({
      id: 'quantificacao-incerteza-ml',
      title: 'Quantificação de incerteza (UQ) em ML',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Predição sem incerteza é incompleta em decisão científica — distingue “não sei” de “confiante e errado”.',
      useFor: ['modelos confiáveis', 'fusão com experimento', 'regulação'],
      prerequisites: ['bayesiana', 'ensembles', 'calibração'],
      shortExplanation:
        'Inclui intervalos, posteriors ou ensembles. Epistêmica (modelo) vs. aleatória (ruído) devem ser separadas quando possível.',
      relatedTopics: ['GP', 'bootstrap', 'explainability'],
      projectIdeas: [
        'Deep ensemble vs. MC dropout em mesmo dataset e medir calibração',
        'Propagar incerteza de surrogate para quantidade de engenharia',
      ],
      professorQuestions: [
        'UQ em extrapolação: o que comunicar a um orientador de experimento?',
        'Conformal prediction resolve o que Bayes não resolve no seu caso?',
      ],
    }),
  ],

  ciencia_dados: [
    definePowerIdea({
      id: 'vies-variancia-aplicado',
      title: 'Viés–variância na prática de dados',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Traduz estatística de ML para pipelines reais — explica métricas instáveis entre splits e features novas.',
      useFor: ['feature selection', 'modelos lineares vs. árvores', 'comunicação com equipe'],
      prerequisites: ['métricas', 'treino/validação', 'dados tabulares'],
      shortExplanation:
        'Em pipelines, viés aparece como underfitting sistemático; variância como sensibilidade a amostras e features espúrias.',
      relatedTopics: ['validação cruzada', 'leakage', 'calibração'],
      projectIdeas: [
        'Decompor erro em modelo linear vs. random forest no mesmo dataset científico',
        'Documentar como nova feature move viés/variância',
      ],
      professorQuestions: [
        'Métricas de negócio vs. MSE: como alinhar com viés–variância?',
        'Dados desbalanceados alteram o trade-off de forma previsível?',
      ],
    }),
    definePowerIdea({
      id: 'particao-treino-teste',
      title: 'Partição treino–teste (hold-out)',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Primeira linha de defesa contra autoengano — sem hold-out honesto, métricas publicadas são inválidas.',
      useFor: ['benchmark interno', 'relatórios', 'pré-processamento'],
      prerequisites: ['amostragem', 'métricas', 'reprodutibilidade'],
      shortExplanation:
        'Reserva dados nunca vistos no ajuste para estimar generalização. Deve ser feita antes de qualquer decisão guiada pelos rótulos.',
      relatedTopics: ['leakage', 'validação cruzada', 'reprodutibilidade'],
      projectIdeas: [
        'Comparar métricas treino vs. teste após pipeline completo',
        'Implementar split estratificado em classes raras',
      ],
      professorQuestions: [
        'Hold-out único vs. k-fold com poucos pontos experimentais?',
        'Como split temporal evita leakage em sensores?',
      ],
    }),
    definePowerIdea({
      id: 'engenharia-features',
      title: 'Engenharia de features',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Codifica conhecimento de domínio em variáveis — frequentemente mais impacto que trocar algoritmo de ML.',
      useFor: ['dados de laboratório', 'séries temporais', 'imagens científicas'],
      prerequisites: ['domínio', 'normalização', 'dimensionalidade'],
      shortExplanation:
        'Constrói transformações (log, Fourier, invariantes) que tornam relações aprendíveis e estáveis fora da amostra.',
      relatedTopics: ['leakage', 'causal inference', 'FAIR'],
      projectIdeas: [
        'Criar features adimensionais a partir de grandezas físicas',
        'Ablation: modelo com vs. sem features de domínio',
      ],
      professorQuestions: [
        'Até onde automatizar features vs. impor física?',
        'Features derivadas do alvo: como auditar leakage?',
      ],
    }),
    definePowerIdea({
      id: 'data-leakage',
      title: 'Vazamento de dados (data leakage)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Causa “resultados perfeitos” que somem em produção — falha ética e científica grave em publicações.',
      useFor: ['pipelines', 'pré-processamento', 'revisão de artigos'],
      prerequisites: ['hold-out', 'normalização', 'séries temporais'],
      shortExplanation:
        'Informação do futuro ou do teste entra no treino (ex.: normalizar com estatística global, target encoding sem CV).',
      relatedTopics: ['treino-teste', 'reprodutibilidade', 'calibração'],
      projectIdeas: [
        'Demonstrar leakage por normalização global e corrigir com fit só no treino',
        'Checklist de leakage para pipeline de espectroscopia',
      ],
      professorQuestions: [
        'Leakage sutil em meta-análises e múltiplos experimentos: exemplos?',
        'Como revisor detecta leakage sem acesso ao notebook?',
      ],
    }),
    definePowerIdea({
      id: 'calibracao-modelos',
      title: 'Calibração de modelos',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Probabilidades devem significar frequências — essencial quando saídas alimentam decisão de risco ou experimento.',
      useFor: ['classificação probabilística', 'previsão', 'fusão com especialistas'],
      prerequisites: ['probabilidades', 'curvas de confiabilidade', 'Brier score'],
      shortExplanation:
        'Modelo calibrado: entre eventos preditos com p≈0.7, ~70% ocorrem. Platt scaling, isotonic e temperatura corrigem descalibração.',
      relatedTopics: ['UQ', 'inferência bayesiana', 'vies-variancia'],
      projectIdeas: [
        'Plotar reliability diagram antes/depois de temperatura scaling',
        'Relacionar calibração com custo de falsos positivos em detecção',
      ],
      professorQuestions: [
        'Calibração vs. acurácia: pode sacrificar uma pela outra?',
        'Modelos bem calibrados em treino mas não em shift de domínio?',
      ],
    }),
    definePowerIdea({
      id: 'inferencia-causal-basica',
      title: 'Inferência causal (noções)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Correlação em dados observacionais não basta para política ou intervenção — separa efeito de confundidores.',
      useFor: ['políticas', 'desenho de experimento', 'interpretação de ML'],
      prerequisites: ['variáveis confundidoras', 'grafos causais', 'experimento'],
      shortExplanation:
        'Pergunta “o que acontece se intervir?” exige identificação causal (RCT, IV, do-calculus). ML sozinho não responde isso.',
      relatedTopics: ['engenharia de features', 'leakage', 'reprodutibilidade'],
      projectIdeas: [
        'Simular confundidor e comparar regressão vs. estimativa com variável instrumental',
        'Desenhar DAG para hipótese em dataset de laboratório',
      ],
      professorQuestions: [
        'Quando proxy variáveis em física induzem conclusões causais falsas?',
        'Causal ML (Double ML): aplicável com N pequeno?',
      ],
    }),
    definePowerIdea({
      id: 'reprodutibilidade-dados',
      title: 'Reprodutibilidade em ciência de dados',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Sem seeds, versões e dados fixos, resultados não replicam — requisito mínimo em colaboração e revisão.',
      useFor: ['notebooks', 'publicação', 'CI de modelos'],
      prerequisites: ['versionamento', 'ambientes', 'documentação'],
      shortExplanation:
        'Fixar dados, código, dependências e aleatoriedade. Pré-registro e pipelines idempotentes reduzem p-hacking e drift.',
      relatedTopics: ['FAIR', 'leakage', 'treino-teste'],
      projectIdeas: [
        'Empacotar pipeline com Dockerfile + seed + hash de dataset',
        'Rodar notebook duas vezes em máquinas distintas e diff de métricas',
      ],
      professorQuestions: [
        'Reprodutibilidade vs. replicabilidade: o que seu grupo exige?',
        'Dados proprietários: como reproduzir sem compartilhar tudo?',
      ],
    }),
    definePowerIdea({
      id: 'dados-fair',
      title: 'Princípios FAIR de dados',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Dados encontráveis e reutilizáveis multiplicam impacto — alinhado a financiadores e infraestrutura científica aberta.',
      useFor: ['repositórios', 'metadados', 'colaboração internacional'],
      prerequisites: ['metadados', 'DOI/ORCID', 'formatos abertos'],
      shortExplanation:
        'Findable, Accessible, Interoperable, Reusable. Metadados ricos e licenças claras permitem reuso por outros grupos.',
      relatedTopics: ['reprodutibilidade', 'engenharia de features', 'leakage'],
      projectIdeas: [
        'Publicar dataset piloto com README, schema e licença Creative Commons',
        'Mapear checklist FAIR para dados de simulação do grupo',
      ],
      professorQuestions: [
        'FAIR com dados sensíveis de defesa ou saúde: limites práticos?',
        'Metadados mínimos que você exigiria antes de aceitar dataset externo?',
      ],
    }),
  ],

  sistemas_autonomos: [
    definePowerIdea({
      id: 'sense-plan-act',
      title: 'Arquitetura sense–plan–act',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Estrutura todo sistema autônomo em módulos auditáveis — base para integrar percepção, decisão e atuação com segurança.',
      useFor: ['robótica', 'UAV', 'veículos autônomos', 'missões'],
      prerequisites: ['sensores', 'planejamento', 'atuadores'],
      shortExplanation:
        'Percepção constrói mundo, planejador escolhe ação, atuadores executam. Laços de feedback e tempo real cruzam as camadas.',
      relatedTopics: ['fusão de sensores', 'estimação de estado', 'safety case'],
      projectIdeas: [
        'Diagramar pipeline sense–plan–act para um robô móvel simulado',
        'Identificar latências e falhas por camada em log de missão',
      ],
      professorQuestions: [
        'End-to-end learning substitui qual camada com evidência de segurança?',
        'Como documentar interfaces entre camadas para certificação?',
      ],
    }),
    definePowerIdea({
      id: 'filtro-kalman',
      title: 'Filtro de Kalman',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Funde modelo dinâmico com medições ruidosas de forma ótima (linear-Gauss) — núcleo de navegação e rastreamento.',
      useFor: ['fusão sensorial', 'controle', 'SLAM simplificado'],
      prerequisites: ['espaço de estados', 'ruído gaussiano', 'modelo linear'],
      shortExplanation:
        'Predição pelo modelo e correção pela medição, com ganhos de Kalman que balanceiam confiança em cada fonte.',
      relatedTopics: ['estimação de estado', 'fusão de sensores', 'SLAM'],
      projectIdeas: [
        'KF em trajetória 2D com GPS ruidoso e modelo de velocidade constante',
        'Comparar EKF vs. UKF em bearing-only tracking (conceitual)',
      ],
      professorQuestions: [
        'Quando linearização do EKF quebra em manobras agressivas?',
        'Kalman vs. particle filter: critérios de escolha no seu veículo?',
      ],
    }),
    definePowerIdea({
      id: 'slam-basico',
      title: 'SLAM (localização e mapeamento simultâneos)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Resolve o ovo e a galinha da navegação sem mapa prévio — habilita robôs e drones em ambientes desconhecidos.',
      useFor: ['robótica móvel', 'exploração', 'UAV indoor'],
      prerequisites: ['Kalman', 'grafos de fatores', 'sensores exteroceptivos'],
      shortExplanation:
        'Estima pose do robô e mapa junto. Incerteza correlaciona poses; otimização em grafo ou filtros propagam covariância.',
      relatedTopics: ['Kalman', 'fusão de sensores', 'sense-plan-act'],
      projectIdeas: [
        'SLAM 2D lidar em simulador e trajetória vs. ground truth',
        'Loop closure: efeito no mapa antes/depois',
      ],
      professorQuestions: [
        'SLAM em ambientes dinâmicos: quais suposições quebram primeiro?',
        'Monocular vs. lidar SLAM: trade-offs para seu projeto?',
      ],
    }),
    definePowerIdea({
      id: 'controle-pid',
      title: 'Controle PID',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Controlador dominante na indústria e em protótipos — entender P, I, D evita oscilações e saturação em atuadores reais.',
      useFor: ['atitude', 'velocidade', 'temperatura', 'braços'],
      prerequisites: ['malha de controle', 'sistemas lineares', 'atuadores'],
      shortExplanation:
        'Erro e sua integral e derivada comandam ação. Tuning (Ziegler–Nichols, etc.) balanceia rapidez e overshoot.',
      relatedTopics: ['estimação de estado', 'impedância', 'V-model'],
      projectIdeas: [
        'PID em simulação de posição com saturação e anti-windup',
        'Comparar P vs. PI vs. PID em mesmo sistema de segunda ordem',
      ],
      professorQuestions: [
        'PID sem modelo: quando migrar para LQR/MPC?',
        'Derivativo ruidoso: filtros e discretização segura?',
      ],
    }),
    definePowerIdea({
      id: 'estimacao-estado',
      title: 'Estimação de estado',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Estado verdadeiro nunca é medido diretamente — estimação une modelo, sensores e incerteza para decisão segura.',
      useFor: ['navegação', 'controle', 'diagnóstico'],
      prerequisites: ['espaço de estados', 'observabilidade', 'ruído'],
      shortExplanation:
        'Reconstrói variáveis internas (pose, velocidade, bias) a partir de medições e dinâmica. Covariância quantifica confiança.',
      relatedTopics: ['Kalman', 'fusão de sensores', 'SLAM'],
      projectIdeas: [
        'Observador de Luenberger vs. KF no mesmo modelo linear',
        'Analisar observabilidade de IMU + encoders em trajetória',
      ],
      professorQuestions: [
        'Estados não observáveis: como detectar antes de voar?',
        'Estimação com constraints (ex.: contato): abordagens recomendadas?',
      ],
    }),
    definePowerIdea({
      id: 'fusao-sensores',
      title: 'Fusão de sensores',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Nenhum sensor basta sozinho — combinar IMU, câmera, lidar e GPS é o que torna autonomia robusta.',
      useFor: ['percepção', 'navegação', 'detecção multi-modal'],
      prerequisites: ['Kalman', 'calibração', 'sincronização temporal'],
      shortExplanation:
        'Alinha tempos e referenciais, pondera confiança e reduz redundância. Pode ser filtro, otimização ou aprendizado com estrutura.',
      relatedTopics: ['estimação de estado', 'SLAM', 'sense-plan-act'],
      projectIdeas: [
        'Fusão IMU + odometria com bias estimado online',
        'Calibração extrínseca câmera–lidar em dataset de laboratório',
      ],
      professorQuestions: [
        'Fusão quando sensores entram em falha degradada?',
        'Deep fusion vs. fusão filtrada clássica: evidência no seu domínio?',
      ],
    }),
    definePowerIdea({
      id: 'safety-case',
      title: 'Safety case (caso de segurança)',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'Argumenta estruturadamente que o sistema é suficientemente seguro — exigido em defesa, aviação e veículos autônomos.',
      useFor: ['certificação', 'revisão de risco', 'missões críticas'],
      prerequisites: ['análise de falhas', 'requisitos', 'testes'],
      shortExplanation:
        'Cadeia claim–argument–evidence liga requisitos de segurança a testes, análises formais e dados de campo.',
      relatedTopics: ['V-model', 'sense-plan-act', 'sim-to-real'],
      projectIdeas: [
        'Esboçar safety case para módulo de detecção de obstáculo em simulação',
        'Tabela de hazards FMEA ligada a testes de regressão',
      ],
      professorQuestions: [
        'ML em safety case: que evidência é aceitável hoje?',
        'Safety case vs. checklist: quando um orientador exige qual?',
      ],
    }),
    definePowerIdea({
      id: 'modelo-v',
      title: 'Modelo em V (V-model)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Amarra requisitos, implementação e verificação — evita “integrar e rezar” em sistemas autônomos complexos.',
      useFor: ['engenharia de sistemas', 'testes', 'documentação'],
      prerequisites: ['requisitos', 'testes unitários', 'integração'],
      shortExplanation:
        'Cada nível de decomposição (sistema, SW, HW) tem teste correspondente à esquerda. Validação final confirma necessidade do usuário.',
      relatedTopics: ['safety case', 'V&V', 'reprodutibilidade'],
      projectIdeas: [
        'Mapear artefatos do seu projeto UAV no diagrama em V',
        'Definir teste de integração que cobre requisito de latência máxima',
      ],
      professorQuestions: [
        'Agile e V-model: como seu laboratório concilia iteração e evidência?',
        'Onde simulação entra vs. teste em hardware-in-the-loop?',
      ],
    }),
  ],

  robotica: [
    definePowerIdea({
      id: 'cinematica-direta-inversa',
      title: 'Cinemática direta e inversa',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Liga ângulos das juntas à pose do efetuador — sem inversa, não há “mover para coordenada X” em manipuladores.',
      useFor: ['braços robóticos', 'células industriais', 'cinemática de pernas'],
      prerequisites: ['matrizes homogêneas', 'geometria', 'graus de liberdade'],
      shortExplanation:
        'Direta: q → pose. Inversa: pose desejada → q (múltiplas soluções possíveis). Singularidades exigem cuidado numérico.',
      relatedTopics: ['Jacobiano', 'manipulabilidade', 'planejamento de trajetória'],
      projectIdeas: [
        'Implementar FK/IK analítica para braço 2R ou 3R em Python',
        'Visualizar múltiplas soluções IK para mesmo alvo 2D',
      ],
      professorQuestions: [
        'IK numérica vs. analítica: quando cada uma no seu robô?',
        'Como escolher postura entre soluções IK para evitar colisão?',
      ],
    }),
    definePowerIdea({
      id: 'jacobiano-manipulador',
      title: 'Jacobiano do manipulador',
      type: 'identidade-matematica',
      level: 'avancado',
      whyItMatters:
        'Relaciona velocidades articulares à do efetuador — base para controle diferencial, singularidades e força.',
      useFor: ['controle em espaço cartesiano', 'singularidades', 'impedância'],
      prerequisites: ['cinemática', 'derivadas', 'álgebra linear'],
      shortExplanation:
        'ẋ = J(q)q̇. Inversão de J (ou pseudoinversa) mapeia comandos cartesianos em juntas; perde rank em singularidades.',
      relatedTopics: ['cinemática inversa', 'dinâmica', 'manipulabilidade'],
      projectIdeas: [
        'Calcular índice de manipulabilidade ao longo de trajetória planejada',
        'Controlar velocidade cartesiana com Jacobian transpose',
      ],
      professorQuestions: [
        'Damped least squares em singularidades: como escolher λ?',
        'Jacobiano analítico vs. numérico em simulador: impacto em tempo real?',
      ],
    }),
    definePowerIdea({
      id: 'dinamica-robotica',
      title: 'Dinâmica robótica',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Torques dependem de inércia, Coriolis e gravidade — ignorar dinâmica gera erro e instabilidade em movimentos rápidos.',
      useFor: ['controle de torque', 'simulação física', 'colisão'],
      prerequisites: ['mecânica clássica', 'Lagrange', 'cinemática'],
      shortExplanation:
        'Equações M(q)q̈ + C(q,q̇)q̇ + g(q) = τ. Identificação de parâmetros e controle computed-torque usam o modelo.',
      relatedTopics: ['Jacobiano', 'impedância', 'sim-to-real'],
      projectIdeas: [
        'Simular braço 2R com controle computed-torque vs. apenas PID em juntas',
        'Estimar parâmetro de massa por experimento de payload',
      ],
      professorQuestions: [
        'Modelo identificado vs. nominal: quanto erro tolera controle?',
        'Dinâmica em contato: extensões mínimas necessárias?',
      ],
    }),
    definePowerIdea({
      id: 'planejamento-trajetoria',
      title: 'Planejamento de trajetória',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Move o robô suavemente respeitando limites de velocidade/aceleração — evita vibração, saturação e colisões.',
      useFor: ['pick-and-place', 'CNC robótico', 'UAV'],
      prerequisites: ['cinemática', 'splines', 'restrições'],
      shortExplanation:
        'Gera perfis q(t) ou x(t) com continuidade C¹/C². Trapezoidal, splines ou otimização com constraints de atuador.',
      relatedTopics: ['cinemática', 'dinâmica', 'impedância'],
      projectIdeas: [
        'Comparar perfil trapezoidal vs. spline quintic em mesmo waypoint',
        'Inserir limite de jerk e medir torque pico em simulação',
      ],
      professorQuestions: [
        'Trajetória em espaço de juntas vs. cartesiano: qual preserva singularidades?',
        'Replanejamento online: quando abortar trajetória planejada?',
      ],
    }),
    definePowerIdea({
      id: 'controle-impedancia',
      title: 'Controle de impedância',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Regula relação força–movimento como mola/amortecedor — essencial para contato, assembly e colaboração humano–robô.',
      useFor: ['manipulação com contato', 'cobots', 'polimento'],
      prerequisites: ['dinâmica', 'Jacobiano', 'sensores de força'],
      shortExplanation:
        'Comportamento desejado F = Mẍ + Bẋ + Kx (ou equivalente em cartesiano). Troca rigidez sem reprogramar trajetória posição.',
      relatedTopics: ['dinâmica', 'fusão de sensores', 'sim-to-real'],
      projectIdeas: [
        'Simular contato com mola virtual em eixo Z do efetuador',
        'Comparar impedância fixa vs. adaptativa em superfície inclinada',
      ],
      professorQuestions: [
        'Estabilidade passiva em impedância com atraso de sensor?',
        'Impedância vs. admittance control: qual para seu hardware?',
      ],
    }),
    definePowerIdea({
      id: 'grafo-ros',
      title: 'Grafo de computação ROS',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'Padrão de integração modular — entender nós, tópicos e TF evita bugs silenciosos em robôs reais.',
      useFor: ['protótipos', 'simulação', 'integração de drivers'],
      prerequisites: ['Linux', 'mensageria', 'sistemas distribuídos básicos'],
      shortExplanation:
        'Nós publicam/assinem tópicos; parâmetros e serviços configuram; tf2 mantém árvore de coordenadas entre elos e mundo.',
      relatedTopics: ['sense-plan-act', 'sim-to-real', 'fusão de sensores'],
      projectIdeas: [
        'Publicar odometria e visualizar em RViz com tf correto',
        'Diagramar grafo de nós do seu stack e latências medidas',
      ],
      professorQuestions: [
        'ROS1 vs. ROS2: o que muda para projeto de IC com prazo curto?',
        'QoS e perda de mensagens: impacto em controle de 100 Hz?',
      ],
    }),
    definePowerIdea({
      id: 'sim-to-real',
      title: 'Sim-to-real (transferência simulação–real)',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Treino em sim é barato, mas gap físico mata políticas — dominar transferência acelera pesquisa em robótica e autonomia.',
      useFor: ['aprendizado por reforço', 'visão', 'dinâmica'],
      prerequisites: ['simuladores', 'identificação', 'domínio aleatório'],
      shortExplanation:
        'Randomização de domínio, adaptação de dinâmica e calibração reduzem realidade gap entre Gazebo/Isaac e hardware.',
      relatedTopics: ['dinâmica', 'fusão de sensores', 'safety case'],
      projectIdeas: [
        'Treinar política simples no sim e medir queda de desempenho no real',
        'Randomizar atrito/massa e plotar robustez',
      ],
      professorQuestions: [
        'Sim-to-real sem RL: o que basta calibrar analyticamente?',
        'Como validar sim antes de confiar em safety case?',
      ],
    }),
    definePowerIdea({
      id: 'manipulabilidade',
      title: 'Manipulabilidade',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Quantifica “quão bem” o robô pode mover-se em uma pose — evita escolher configurações no limiar de singularidade.',
      useFor: ['planejamento', 'otimização de postura', 'células redundantes'],
      prerequisites: ['Jacobiano', 'cinemática', 'álgebra linear'],
      shortExplanation:
        'Medidas como √det(JJᵀ) ou número de condição de J indicam margem de velocidade/força em todas as direções.',
      relatedTopics: ['Jacobiano', 'cinemática inversa', 'planejamento de trajetória'],
      projectIdeas: [
        'Heatmap de manipulabilidade no workspace 2R',
        'Escolher postura IK maximizando manipulabilidade para mesma pose alvo',
      ],
      professorQuestions: [
        'Manipulabilidade vs. distância a obstáculo: como combinar no planner?',
        'Braços redundantes: critério além de manipulabilidade escalar?',
      ],
    }),
  ],
};
