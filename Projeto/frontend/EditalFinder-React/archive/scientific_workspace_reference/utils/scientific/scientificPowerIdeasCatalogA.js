import { definePowerIdea } from './scientificPowerIdeasHelpers';

/** Catálogo A — Físico-química, quântica, plasmas, MD, nuclear e química nuclear (Fase 2J). */
export const POWER_IDEAS_CATALOG_A = {
  fisico_quimica: [
    definePowerIdea({
      id: 'partition-function',
      title: 'Função de partição',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Passa a ver propriedades macroscópicas como médias estatísticas sobre microestados, unificando termodinâmica e mecânica estatística num único objeto gerador.',
      shortExplanation:
        'A função de partição Z agrega todos os microestados acessíveis com seus pesos de Boltzmann. Derivando log Z obtém-se energia interna, entropia, pressão e constantes de equilíbrio de forma sistemática.',
      useFor: ['Calcular constantes de equilíbrio', 'Conectar simulação e termodinâmica', 'Derivar relações de Maxwell'],
      prerequisites: ['Estatística básica', 'Termodinâmica', 'Ensemble canônico'],
      relatedTopics: ['Distribuição de Boltzmann', 'Ensemble canônico', 'Energia livre de Gibbs'],
      projectIdeas: [
        'Implementar Z para oscilador harmônico e comparar Cv com valor clássico',
        'Estimar Kp de uma reação gasosa a partir de energias DFT',
      ],
      professorQuestions: [
        'Em que condições a função de partição clássica diverge e quando devo usar a quântica?',
        'Como conectar Z de simulação (WHAM/MBAR) com experimentos de calorimetria?',
      ],
    }),
    definePowerIdea({
      id: 'boltzmann-distribution',
      title: 'Distribuição de Boltzmann',
      type: 'lei',
      level: 'basico',
      whyItMatters:
        'Ensina que o equilíbrio não é estático: estados de menor energia dominam, mas estados excitados sempre importam à temperatura finita.',
      shortExplanation:
        'Em equilíbrio térmico, a probabilidade de um microestado é proporcional a exp(-E/kT). Populações relativas entre níveis dependem apenas da diferença de energia e da temperatura.',
      useFor: ['Interpretar espectros', 'Estimar populações vibracionais', 'Ligar cinética e equilíbrio'],
      prerequisites: ['Termodinâmica', 'Entropia', 'Temperatura absoluta'],
      relatedTopics: ['Função de partição', 'Princípio de equipartição', 'Ensemble canônico'],
      projectIdeas: [
        'Plotar fração de conformações populadas vs temperatura em um peptídeo',
        'Ajustar curva de deslocamento químico com modelo de dois estados',
      ],
      professorQuestions: [
        'Quando a distribuição de Boltzmann deixa de descrever o sistema (sistemas atrapalhados, laser)?',
        'Como medir experimentalmente a diferença de energia entre dois estados conformacionais?',
      ],
    }),
    definePowerIdea({
      id: 'equipartition',
      title: 'Princípio de equipartição',
      type: 'teorema',
      level: 'basico',
      whyItMatters:
        'Dá intuição rápida de quanta energia cada grau de liberdade absorve e quando o limite clássico quebra.',
      shortExplanation:
        'Cada grau de liberdade quadrático contribui com (1/2)kT à energia interna em média. Explica Cv de gases ideais e modos vibracionais a altas temperaturas.',
      useFor: ['Estimar calor específico', 'Validar simulações MD', 'Identificar modos congelados'],
      prerequisites: ['Distribuição de Boltzmann', 'Energia cinética e potencial'],
      relatedTopics: ['Ensemble canônico', 'Gases ideais', 'Dinâmica molecular'],
      projectIdeas: [
        'Medir energia por grau de liberdade em MD de argônio líquido',
        'Comparar Cv simulado com equipartição e com dados experimentais',
      ],
      professorQuestions: [
        'Por que modos de alta frequência não recebem (1/2)kT em temperatura ambiente?',
        'Equipartição vale no microcanônico ou só no canônico?',
      ],
    }),
    definePowerIdea({
      id: 'maximum-entropy',
      title: 'Princípio da entropia máxima',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Reformula inferência física: dado o que você sabe, o estado mais honesto é o que maximiza incerteza sem violar restrições.',
      shortExplanation:
        'Entre todos os microestados compatíveis com restrições macroscópicas (energia média, volume, partículas), o equilíbrio escolhe o de maior entropia. Fundamenta ensembles e inferência bayesiana em física.',
      useFor: ['Justificar ensembles', 'Modelar sistemas com dados incompletos', 'Conectar termodinâmica e informação'],
      prerequisites: ['Entropia de Boltzmann', 'Multiplicadores de Lagrange'],
      relatedTopics: ['Ensemble canônico', 'Distribuição de Boltzmann', 'Energia livre'],
      projectIdeas: [
        'Reconstruir distribuição de velocidades com momentos prescritos via MaxEnt',
        'Comparar MaxEnt com histograma de simulação MD',
      ],
      professorQuestions: [
        'A entropia máxima é única quando há várias restrições compatíveis?',
        'Como esse princípio aparece em modelos coarse-grained que você usa?',
      ],
    }),
    definePowerIdea({
      id: 'free-energy',
      title: 'Energia livre (Helmholtz e Gibbs)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Troca a pergunta "qual energia?" por "qual potencial governa o processo espontâneo nas condições do laboratório?"',
      shortExplanation:
        'A energia livre combina energia interna e entropia no potencial adequado às variáveis fixadas (T,V ou T,P). Minimização de G ou A define equilíbrio químico e de fase.',
      useFor: ['Prever espontaneidade', 'Ligar simulação e experimento', 'Calcular constantes de equilíbrio'],
      prerequisites: ['Termodinâmica', 'Entropia', 'Ensemble canônico'],
      relatedTopics: ['Função de partição', 'Superfícies de energia potencial', 'Teoria do estado de transição'],
      projectIdeas: [
        'Calcular ΔG de solvatação por integração de caminho em simulação',
        'Diagrama de estabilidade de fases binário a partir de G(T,x)',
      ],
      professorQuestions: [
        'Quando devo reportar ΔA em vez de ΔG em trabalhos de simulação?',
        'Como estimar incertezas em energia livre calculada por WHAM?',
      ],
    }),
    definePowerIdea({
      id: 'transition-state-theory',
      title: 'Teoria do estado de transição (TST)',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Liga estrutura molecular (sela na PES) a taxas observáveis, guiando onde investir em cálculo quântico ou amostragem.',
      shortExplanation:
        'Assume equilíbrio no estado de transição e expressa a constante de taxa em termos da energia livre de ativação. Conecta barreiras na superfície de energia potencial à cinética química.',
      useFor: ['Estimar taxas de reação', 'Interpretar barreiras DFT', 'Priorizar modos de reação'],
      prerequisites: ['Superfície de energia potencial', 'Estatística de equilíbrio', 'Cinética química'],
      relatedTopics: ['Lei de Arrhenius', 'Energia livre', 'Born-Oppenheimer'],
      projectIdeas: [
        'Localizar TS de uma reação orgânica com NEB e estimar k(TST)',
        'Comparar TST com dinâmica de reação direta em trajectória',
      ],
      professorQuestions: [
        'Em que reações a TST falha sistematicamente e qual alternativa você recomenda?',
        'Como tratar solvente explicitamente no cálculo da barreira de ativação?',
      ],
    }),
    definePowerIdea({
      id: 'arrhenius-law',
      title: 'Lei de Arrhenius',
      type: 'lei',
      level: 'basico',
      whyItMatters:
        'Oferece linguagem universal para taxas: energia de ativação como número comparável entre sistemas e experimentos.',
      shortExplanation:
        'A constante de taxa k = A exp(-Ea/RT). Um gráfico ln k vs 1/T revela Ea e o fator pré-exponencial, ligando cinética a barreiras energéticas.',
      useFor: ['Ajustar dados cinéticos', 'Extrapolar taxas com temperatura', 'Validar modelos de barreira'],
      prerequisites: ['Cinética química', 'Termodinâmica básica'],
      relatedTopics: ['Teoria do estado de transição', 'Teoria da transição', 'Flutuação-dissipação'],
      projectIdeas: [
        'Ajustar Arrhenius a dados de decomposição térmica (TGA acoplada)',
        'Comparar Ea de experimento com barreira DFT',
      ],
      professorQuestions: [
        'Quando o plot de Arrhenius mostra curvatura e como interpretar?',
        'A pode ser interpretado microscopicamente no seu sistema de estudo?',
      ],
    }),
    definePowerIdea({
      id: 'fluctuation-dissipation',
      title: 'Teorema de flutuação-dissipação',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Une ruído e resposta: agitações térmicas que você mede contêm a mesma física que transporte e relaxação.',
      shortExplanation:
        'Flutuações em equilíbrio estão ligadas à dissipação linear perto do equilíbrio. Permite obter susceptibilidades, difusão e viscosidade a partir de correladores de equilíbrio.',
      useFor: ['Calcular transporte por MD', 'Interpretar espectros de ruído', 'Validar termostatos'],
      prerequisites: ['Estatística de equilíbrio', 'Teoria linear de resposta'],
      relatedTopics: ['Difusão', 'Viscosidade', 'Dinâmica molecular'],
      projectIdeas: [
        'Obter coeficiente de difusão via integral de Green-Kubo em MD',
        'Comparar D de Einstein e de Kubo no mesmo fluido',
      ],
      professorQuestions: [
        'Quanto tempo de simulação é necessário para convergir um correlador de Kubo?',
        'O teorema vale fora do regime linear de resposta?',
      ],
    }),
    definePowerIdea({
      id: 'ergodicity',
      title: 'Hipótese ergódica',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'Justifica substituir médias de ensemble por médias temporais — base conceitual de quase toda simulação.',
      shortExplanation:
        'Afirma que médias temporais ao longo de uma trajetória longa equivalem a médias sobre microestados do ensemble. Sem ergodicidade, simulação e teoria estatística divergem.',
      useFor: ['Validar MD e MC', 'Interpretar amostragem', 'Diagnosticar sistemas vidrados'],
      prerequisites: ['Ensembles estatísticos', 'Mecânica estatística introdutória'],
      relatedTopics: ['Ensemble canônico', 'Dinâmica molecular', 'Função de partição'],
      projectIdeas: [
        'Testar convergência de médias em líquido superresfriado vs líquido normal',
        'Comparar média temporal e média de blocos em simulação de proteína',
      ],
      professorQuestions: [
        'Como você detecta quebra de ergodicidade em simulações de materiais disordenados?',
        'Sistemas com múltiplos poços profundos exigem qual estratégia de amostragem?',
      ],
    }),
    definePowerIdea({
      id: 'potential-energy-surface',
      title: 'Superfície de energia potencial (PES)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Transforma química em geometria: reações, espectros e mecanismos são caminhos e vales num landscape de energia.',
      shortExplanation:
        'A PES E({R}) descreve energia eletrônica em função das coordenadas nucleares. Mínimos são espécies estáveis; selas são estados de transição; vibrações expandem em torno dos mínimos.',
      useFor: ['Mecanismos de reação', 'Vibracional', 'Planejar amostragem de reação'],
      prerequisites: ['Química quântica básica', 'Geometria molecular'],
      relatedTopics: ['Born-Oppenheimer', 'TST', 'Dinâmica molecular'],
      projectIdeas: [
        'Mapear caminho de reação com NEB em cluster pequeno',
        'Analisar modos normais no mínimo de um intermediário',
      ],
      professorQuestions: [
        'Qual nível de teoria eletrônica é aceitável para barreiras no seu grupo?',
        'Como incluir efeitos de meio na PES de forma consistente?',
      ],
    }),
    definePowerIdea({
      id: 'born-oppenheimer',
      title: 'Aproximação de Born-Oppenheimer',
      type: 'aproximacao',
      level: 'intermediario',
      whyItMatters:
        'Separa escalas temporais: elétrons ajustam-se instantaneamente enquanto núcleos exploram uma PES — base de química computacional.',
      shortExplanation:
        'Porque elétrons são muito mais leves, o estado eletrônico adiaabático segue os núcleos lentos. Permite calcular energia eletrônica para cada geometria nuclear.',
      useFor: ['DFT e ab initio', 'MD com forças QM', 'Espectroscopia vibracional'],
      prerequisites: ['Estrutura eletrônica', 'PES'],
      relatedTopics: ['Superfície de energia potencial', 'Química quântica', 'Dinâmica molecular'],
      projectIdeas: [
        'Curva E(R) para molécula diatômica comparando níveis BO e correção de acoplamento',
        'MD ab initio curto para validar forças BO',
      ],
      professorQuestions: [
        'Em quais sistemas o acoplamento eletrônico-nuclear é crítico no seu tema?',
        'BO é compatível com simulação de estados excitados?',
      ],
    }),
    definePowerIdea({
      id: 'canonical-ensemble',
      title: 'Ensemble canônico (NVT)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Modela o laboratório termostato: energia flutua, temperatura é fixada — ponte entre simulação e experimento em T constante.',
      shortExplanation:
        'Sistema em contato com banho térmico a T fixa; probabilidade de microestados ~ exp(-H/kT). Flutuações de energia definem calor específico e ligam a função de partição.',
      useFor: ['Interpretar MD NVT', 'Derivar termodinâmica', 'Conectar a experimentos isotérmicos'],
      prerequisites: ['Termodinâmica', 'Distribuição de Boltzmann'],
      relatedTopics: ['Função de partição', 'Princípio da entropia máxima', 'Termostatos'],
      projectIdeas: [
        'Comparar flutuações de energia em NVT com predição do ensemble canônico',
        'Estimar Cv via variação de energia em simulação',
      ],
      professorQuestions: [
        'Quando NVT é inadequado frente a NPT ou μVT no seu problema?',
        'Como o termostato altera a física de flutuações que você mede?',
      ],
    }),
  ],
  quantica: [
    definePowerIdea({
      id: 'superposition',
      title: 'Princípio da superposição',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Substitui estados clássicos únicos por amplitudes combináveis: interferência e entanglement tornam-se consequências, não surpresas.',
      shortExplanation:
        'Se |ψ₁⟩ e |ψ₂⟩ são estados possíveis, qualquer combinação linear α|ψ₁⟩+β|ψ₂⟩ também é. Probabilidades vêm de |ψ|² após medição, não de misturas clássicas.',
      useFor: ['Interferência', 'Qubits', 'Base para operadores'],
      prerequisites: ['Álgebra linear', 'Vetores de estado'],
      relatedTopics: ['Operadores hermitianos', 'Princípio da incerteza', 'Medição quântica'],
      projectIdeas: [
        'Simular dupla fenda com pacote de ondas em Python',
        'Demonstrar interferência em qubit de dois níveis',
      ],
      professorQuestions: [
        'Como distinguir superposição coerente de mistura estatística no laboratório?',
        'Decoerência destrói superposição em qual escala de tempo no seu sistema?',
      ],
    }),
    definePowerIdea({
      id: 'uncertainty-principle',
      title: 'Princípio da incerteza de Heisenberg',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Impõe limite fundamental à precisão conjunta: otimizar uma medição pode custar informação em outra variável conjugada.',
      shortExplanation:
        'ΔA ΔB ≥ (1/2)|⟨[Â,B̂]⟩| para observáveis conjugadas. Não é limitação instrumental apenas, mas propriedade dos estados quânticos.',
      useFor: ['Estimar resolução experimental', 'Justificar modelos efetivos', 'Ligar a comutadores'],
      prerequisites: ['Operadores e valores esperados', 'Comutadores'],
      relatedTopics: ['Comutadores', 'Função de onda', 'Medição'],
      projectIdeas: [
        'Calcular Δx Δp para pacote gaussiano e verificar limite',
        'Analisar largura de linha espectral vs tempo de vida',
      ],
      professorQuestions: [
        'A relação de incerteza energia-tempo é interpretada como limite de qual natureza?',
        'Como a incerteza aparece em simulações semiquânticas que você valida?',
      ],
    }),
    definePowerIdea({
      id: 'angular-momentum-quantization',
      title: 'Quantização do momento angular',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Explica espectros atômicos e estrutura eletrônica: números quânticos não são etiquetas, vêm de simetria e autovalores.',
      shortExplanation:
        'Operadores L̂² e L̂z comutam e têm espectro discreto em sistemas ligados. Regras de seleção e degenerescência seguem da álgebra de momento angular.',
      useFor: ['Espectroscopia', 'Estrutura eletrônica', 'Átomo de hidrogênio'],
      prerequisites: ['Operadores hermitianos', 'Álgebra linear'],
      relatedTopics: ['Spin', 'Degenerescência', 'Átomo de hidrogênio'],
      projectIdeas: [
        'Resolver átomo de hidrogênio e plotar níveis com labels l, m',
        'Simular transições dipolares permitidas em átomo modelo',
      ],
      professorQuestions: [
        'Como o acoplamento spin-órbita altera a sequência de níveis que você mede?',
        'Em moléculas, quais aproximações de momento angular são aceitáveis?',
      ],
    }),
    definePowerIdea({
      id: 'hermitian-operators',
      title: 'Operadores hermitianos e observáveis',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Traduz física em espectro real: o que medimos são autovalores de operadores com propriedades matemáticas bem definidas.',
      shortExplanation:
        'Observáveis são representados por operadores Hermitianos com autovalores reais e autovetores ortogonais. Valores esperados são ⟨ψ|Â|ψ⟩.',
      useFor: ['Resolver problemas exatamente solúveis', 'Fundamentar medida', 'Diagonalização'],
      prerequisites: ['Álgebra linear', 'Produto interno'],
      relatedTopics: ['Comutadores', 'Teorema variacional', 'Superposição'],
      projectIdeas: [
        'Diagonalizar Hamiltoniano 2×2 e comparar com solução analítica',
        'Implementar valores esperados para spin 1/2 em bases distintas',
      ],
      professorQuestions: [
        'Quando usar base de estados próprios vs base de tempo em evolução?',
        'Operadores não-Hermitianos aparecem em quais modelos do seu grupo?',
      ],
    }),
    definePowerIdea({
      id: 'commutators',
      title: 'Comutadores e álgebra de observáveis',
      type: 'identidade-matematica',
      level: 'intermediario',
      whyItMatters:
        'Comutador nulo significa compatibilidade de medições; não nulo gera incerteza e estrutura de níveis.',
      shortExplanation:
        '[Â,B̂] = ÂB̂ − B̂Â mede não comutatividade. Relações [x̂,p̂]=iℏ e [L̂i,L̂j] definem álgebra fundamental da mecânica quântica.',
      useFor: ['Regras de seleção', 'Simetrias', 'Incerteza'],
      prerequisites: ['Operadores hermitianos', 'Produto de operadores'],
      relatedTopics: ['Princípio da incerteza', 'Momento angular', 'Teorema de Ehrenfest'],
      projectIdeas: [
        'Verificar comutação de Pauli matrices numericamente',
        'Ligar comutador de H e L² em potencial central',
      ],
      professorQuestions: [
        'Como simetrias contínuas se traduzem em comutadores no formalismo que você usa?',
        'O comutador de campo é relevante na sua linha de pesquisa?',
      ],
    }),
    definePowerIdea({
      id: 'ehrenfest-theorem',
      title: 'Teorema de Ehrenfest',
      type: 'teorema',
      level: 'intermediario',
      whyItMatters:
        'Mostra onde a mecânica clássica emerge: médias quânticas seguem leis de Newton sob condições adequadas.',
      shortExplanation:
        'd⟨x⟩/dt = ⟨p⟩/m e d⟨p⟩/dt = −⟨∇V⟩. Conecta equação de Schrödinger a trajetórias médias sem postular clássica à priori.',
      useFor: ['Interpretar pacotes de onda', 'Validar simulações semiclássicas', 'Ligar QM e MD'],
      prerequisites: ['Equação de Schrödinger', 'Valores esperados'],
      relatedTopics: ['Princípio da incerteza', 'Aproximação WKB', 'Dinâmica molecular'],
      projectIdeas: [
        'Evoluir pacote gaussiano em poço harmônico e comparar com Newton',
        'Estimar ⟨∇V⟩ ao longo de trajetória quase clássica',
      ],
      professorQuestions: [
        'Em que potenciais a trajetória de ⟨x⟩ deixa de ser clássica rapidamente?',
        'Ehrenfest ajuda a justificar force fields clássicos no seu contexto?',
      ],
    }),
    definePowerIdea({
      id: 'variational-theorem',
      title: 'Teorema variacional',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Transforma busca de estados em otimização: energia esperada é sempre cota superior ao fundamental.',
      shortExplanation:
        '⟨ψ_trial|Ĥ|ψ_trial⟩ ≥ E₀ para qualquer ψ_trial normalizado. Base de métodos variacionais e Hartree-Fock.',
      useFor: ['Estimar energias', 'HF e DFT conceitual', 'Funções de onda aproximadas'],
      prerequisites: ['Operadores hermitianos', 'Produto interno'],
      relatedTopics: ['Teoria de perturbação', 'Química quântica', 'Função de onda'],
      projectIdeas: [
        'Implementar variacional para átomo de hidrogênio com base gaussiana',
        'Comparar energia variacional com perturbativa de primeira ordem',
      ],
      professorQuestions: [
        'Como escolher funções de teste que convergem sem explodir custo computacional?',
        'O teorema variacional orienta escolha de funcionais DFT no seu trabalho?',
      ],
    }),
    definePowerIdea({
      id: 'perturbation-theory',
      title: 'Teoria de perturbação (tempo-independente)',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Permite atacar problemas intratáveis como pequenas correções sobre soluções exatas — mentalidade padrão em física aplicada.',
      shortExplanation:
        'Ĥ = Ĥ₀ + λĤ′. Correções de energia e função de onda em potências de λ quando o desvio é pequeno. Degenerescência exige diagonalização no subespaço.',
      useFor: ['Correções finas em espectros', 'Interações fracas', 'Acoplamento spin-órbita'],
      prerequisites: ['Autovalores e autovetores', 'Álgebra linear'],
      relatedTopics: ['Degenerescência', 'Teorema variacional', 'WKB'],
      projectIdeas: [
        'Calcular correção de primeira ordem em oscilador anharmônico fraco',
        'Stark effect em átomo de hidrogênio (primeira ordem)',
      ],
      professorQuestions: [
        'Quando perturbação de segunda ordem é obrigatória no seu sistema?',
        'Como tratar quase-degenerescência em clusters ou sólidos?',
      ],
    }),
    definePowerIdea({
      id: 'spin',
      title: 'Spin e graus de liberdade internos',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Adiciona graus de liberdade intrínsecos sem análogo clássico claro: espectroscopia, magnetismo e qubits dependem de spin.',
      shortExplanation:
        'Partículas com spin 1/2 têm estados |↑⟩,|↓⟩ e momento angular intrínseco. Pauli e estrutura hiperfina aparecem em átomos e sólidos.',
      useFor: ['RMN', 'Magnetismo', 'Informação quântica'],
      prerequisites: ['Momento angular', 'Matrizes de Pauli'],
      relatedTopics: ['Momento angular', 'Degenerescência', 'Estrutura hiperfina'],
      projectIdeas: [
        'Simular precessão de spin em campo B com equação de Schrödinger',
        'Calcular splitting em campo magnético para spin 1/2',
      ],
      professorQuestions: [
        'Como spin-órbita entra nos materiais que você estuda experimentalmente?',
        'Spin é tratado relativisticamente em quais cálculos do grupo?',
      ],
    }),
    definePowerIdea({
      id: 'degeneracy',
      title: 'Degenerescência e quebra de simetria',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Níveis iguais não são acidente: refletem simetria; perturbações revelam estrutura física ao partir degenerescência.',
      shortExplanation:
        'Autovalores iguais de Ĥ têm subespaço degenerado. Perturbações levantam degenerescência (ex.: campo externo). Essencial para grupo e espectroscopia.',
      useFor: ['Classificar níveis', 'Perturbação', 'Análise de simetria'],
      prerequisites: ['Autovalores', 'Teoria de perturbação'],
      relatedTopics: ['Momento angular', 'Perturbação', 'Simetria'],
      projectIdeas: [
        'Diagrama de splitting de nível 4-fold sob perturbação cúbica',
        'Identificar degenerescência em poço de potencial 3D',
      ],
      professorQuestions: [
        'Como identificar degenerescência acidental vs simétrica nos seus dados?',
        'Grupos de simetria moleculares são ensinados antes de projetos no grupo?',
      ],
    }),
    definePowerIdea({
      id: 'tunneling',
      title: 'Efeito túnel quântico',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Processos classicamente proibidos ocorrem com probabilidade finita — essencial em decaimento, química e dispositivos.',
      shortExplanation:
        'Partículas atravessam barreiras de potencial com amplitude não nula mesmo E < V₀. Taxa depende exponencialmente da largura e altura da barreira.',
      useFor: ['Decaimento alfa', 'Microscopia STM', 'Reações por túnel'],
      prerequisites: ['Solução de barreira', 'Probabilidade |ψ|²'],
      relatedTopics: ['Aproximação WKB', 'Superposição', 'TST'],
      projectIdeas: [
        'Calcular coeficiente de transmissão para barreira retangular',
        'Estimar taxa de túnel com WKB e comparar com solução numérica',
      ],
      professorQuestions: [
        'Túnel em reações químicas é dominante em qual faixa de temperatura no seu tema?',
        'Como medir barrera efetiva experimentalmente?',
      ],
    }),
    definePowerIdea({
      id: 'wkb-approximation',
      title: 'Aproximação WKB',
      type: 'aproximacao',
      level: 'avancado',
      whyItMatters:
        'Dá fórmulas analíticas onde só se via numericamente: barreiras, poços e limite semiclássico estruturam o raciocínio.',
      shortExplanation:
        'Assume ψ ~ exp(iS/ℏ) com S variando lentamente. Estima níveis em poços e taxas de túnel quando potencial varia suavemente.',
      useFor: ['Túnel', 'Níveis quase clássicos', 'Ligar fase e amplitude'],
      prerequisites: ['Equação de Schrödinger', 'Túnel'],
      relatedTopics: ['Efeito túnel', 'Teorema de Ehrenfest', 'Perturbação'],
      projectIdeas: [
        'Níveis do oscilador anharmônico via WKB e comparar com numérico',
        'Coeficiente de transmissão WKB vs transfer matrix',
      ],
      professorQuestions: [
        'Onde WKB falha nos sistemas que você modela e qual correção usar?',
        'Conexão WKB é ensinada com exemplos do seu domínio (nuclear, química)?',
      ],
    }),
  ],
  plasmas_fusao: [
    definePowerIdea({
      id: 'debye-length',
      title: 'Comprimento de Debye',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Define a escala em que o plasma se comporta coletivamente vs como gás de cargas isoladas — guia diagnósticos e modelos.',
      shortExplanation:
        'λ_D é a escala de blindagem de campos elétricos em plasma quase-neutro. Quando o sistema é maior que λ_D, aproximações de plasma fluido ou MHD são pertinentes.',
      useFor: ['Critérios de validade de modelos', 'Diagnóstico de plasma', 'Fusão e descarga'],
      prerequisites: ['Eletrostática', 'Distribuição de cargas'],
      relatedTopics: ['Quase-neutralidade', 'MHD', 'Oscilações de plasma'],
      projectIdeas: [
        'Calcular λ_D para plasma de fusão e comparar com escala do reator',
        'Estimar critério de parâmetro de acoplamento em descarga',
      ],
      professorQuestions: [
        'Em quais experimentos do grupo λ_D é resolvido vs sub-resolvido?',
        'Colisões alteram λ_D de forma significativa no seu plasma?',
      ],
    }),
    definePowerIdea({
      id: 'quasineutrality',
      title: 'Quase-neutralidade de plasma',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Permite tratar n_e ≈ n_i na maior parte do volume, simplificando equações sem ignorar instabilidades locais.',
      shortExplanation:
        'Em plasmas de interesse em fusão, desvios de neutralidade são pequenos em escalas maiores que λ_D. Campos elétricos surgem para restaurar quase-neutralidade rapidamente.',
      useFor: ['Equações de fluido', 'MHD', 'Modelagem de reator'],
      prerequisites: ['Eletrostática', 'Comprimento de Debye'],
      relatedTopics: ['MHD', 'Debye', 'Oscilações de Langmuir'],
      projectIdeas: [
        'Simular perturbação de densidade e relaxação quase-neutra 1D',
        'Estimar campo ambipolar em borda de plasma',
      ],
      professorQuestions: [
        'Onde quase-neutralidade quebra no seu dispositivo (bordas, probes)?',
        'Sheaths exigem tratamento separado no seu pipeline de simulação?',
      ],
    }),
    definePowerIdea({
      id: 'mhd',
      title: 'Magnetohidrodinâmica (MHD)',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Unifica fluido e campo magnético: confinamento, instabilidades e dinâmica de reator tornam-se equações de balanceamento.',
      shortExplanation:
        'Plasma condutor tratado como fluido acoplado a Maxwell via tensão magnética e indução. Descreve equilíbrio, reconnection e transporte em escalas macroscópicas.',
      useFor: ['Confinamento magnético', 'Equilíbrio de tokamak', 'Simulação de macro-instabilidades'],
      prerequisites: ['Eletromagnetismo', 'Mecânica dos fluidos'],
      relatedTopics: ['Critério de Lawson', 'Corrente bootstrap', 'Landau damping'],
      projectIdeas: [
        'Resolver equilíbrio MHD simples (cilindro/placa)',
        'Visualizar linhas de campo para configuração axisimétrica',
      ],
      professorQuestions: [
        'Quais extensões além de MHD ideal são obrigatórias no seu dispositivo?',
        'Como validar um código MHD com dados experimentais disponíveis?',
      ],
    }),
    definePowerIdea({
      id: 'lawson-criterion',
      title: 'Critério de Lawson',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Traduz fusão em números de engenharia: nτ e T definem se a reação gera mais energia do que perde.',
      shortExplanation:
        'Ignição exige nτE acima de um limiar dependente da reação (D-T, etc.) e temperatura. Conecta física de reação, confinamento e viabilidade de reactor.',
      useFor: ['Avaliar cenários de fusão', 'Comparar confinamentos', 'Metas de experimento'],
      prerequisites: ['Seção de choque de fusão', 'Taxas de reação'],
      relatedTopics: ['Confinamento', 'Seção de choque de fusão', 'Energia de plasma'],
      projectIdeas: [
        'Plotar diagrama nτ-T para D-T com perdas simplificadas',
        'Estimar nτ necessário dado τ_E medido em experimento modelo',
      ],
      professorQuestions: [
        'Qual figura de mérito o grupo prioriza além de Lawson (Q, gain)?',
        'Como incertezas em τ_E propagam para previsões de ignição?',
      ],
    }),
    definePowerIdea({
      id: 'confinement',
      title: 'Confinamento de plasma (tempo e geometria)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Sem confinamento adequado, o plasma perde energia e partículas antes de reagir — eixo entre física e engenharia de fusão.',
      shortExplanation:
        'τ_E e geometria (tokamak, stellarator, inercial) determinam se condições de Lawson são atingíveis. Transporte anômalo e bordas limitam τ_E na prática.',
      useFor: ['Escalar reatores', 'Interpretar experimentos', 'Comparar conceitos'],
      prerequisites: ['MHD básico', 'Transporte de energia'],
      relatedTopics: ['Critério de Lawson', 'Corrente bootstrap', 'Landau damping'],
      projectIdeas: [
        'Ajustar lei de escalamento τ_E ∝ P^α B^β n^γ a dados públicos',
        'Modelar perda de energia por convecção simplificada',
      ],
      professorQuestions: [
        'Qual modo de transporte domina no regime que você estuda?',
        'Confinamento inercial e magnético compartilham modelos úteis no grupo?',
      ],
    }),
    definePowerIdea({
      id: 'bootstrap-current',
      title: 'Corrente bootstrap',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Mostra que o plasma pode auto-gerar corrente — impacta sustentação de configuração e viabilidade de modos avançados.',
      shortExplanation:
        'Gradientes de pressão e curvatura geram corrente neoclassica sem fonte externa. Essencial em tokamaks avançados e eficiência de confinamento.',
      useFor: ['Cenários de corrente zero-drive', 'Equilíbrio de tokamak', 'Otimização de configuração'],
      prerequisites: ['MHD', 'Transporte neoclássico introdutório'],
      relatedTopics: ['MHD', 'Confinamento', 'Landau damping'],
      projectIdeas: [
        'Estimar fração de corrente bootstrap em equilíbrio simplificado',
        'Revisar sensitividade de q-profile à fração bootstrap',
      ],
      professorQuestions: [
        'Bootstrap é medido ou inferido nos dados que você usa?',
        'Controle de perfil de corrente interage com bootstrap como?',
      ],
    }),
    definePowerIdea({
      id: 'landau-damping',
      title: 'Amortecimento de Landau',
      type: 'conceito-chave',
      level: 'pesquisa',
      whyItMatters:
        'Explica dissipação sem colisões: ressonância entre ondas e partículas muda estabilidade e aquecimento.',
      shortExplanation:
        'Ondas em plasmas sem colisões podem ser amortecidas por partículas com velocidade resonante com a fase da onda. Crucial para aquecimento RF e instabilidades cinéticas.',
      useFor: ['Aquecimento de plasma', 'Estabilidade cinética', 'Ondas em plasma'],
      prerequisites: ['Função de distribuição', 'Oscilações de plasma'],
      relatedTopics: ['MHD vs cinético', 'Comprimento de Debye', 'Fusão'],
      projectIdeas: [
        'Simular amortecimento de onda de Langmuir em Vlasov 1D simplificado',
        'Revisar papel de Landau damping em aquecimento ICC',
      ],
      professorQuestions: [
        'Quando modelos fluidos falham por ausência de Landau damping?',
        'Há dados experimentais que isolam amortecimento de Landau no seu tema?',
      ],
    }),
    definePowerIdea({
      id: 'fusion-cross-section',
      title: 'Seção de choque de fusão σ(E)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Liga energia de colisão a probabilidade de reação — sem σ(E) não há previsão de taxa de fusão nem Lawson.',
      shortExplanation:
        'σ depende fortemente da energia de centro de massa; reações D-T têm ressonância em keV. Taxa de reação integra σ sobre distribuição de Maxwell-Boltzmann.',
      useFor: ['Calcular taxas de fusão', 'Critério de Lawson', 'Escolher combustível'],
      prerequisites: ['Cinética de reações', 'Distribuição Maxwelliana'],
      relatedTopics: ['Critério de Lawson', 'Plasma quente', 'Reator'],
      projectIdeas: [
        'Plotar σ(E) para D-T e D-D e integrar ⟨σv⟩ vs T',
        'Sensibilidade de potência de fusão a temperatura efetiva',
      ],
      professorQuestions: [
        'Quais incertezas em σ(E) ainda impactam projetos de reactor?',
        'Reações alternativas (p-B, etc.) são viáveis na sua linha de pesquisa?',
      ],
    }),
  ],
  dinamica_molecular: [
    definePowerIdea({
      id: 'statistical-ensembles',
      title: 'Ensembles estatísticos (NVE, NVT, NPT)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Escolher ensemble é escolher qual experimento você simula — erro aqui invalida toda comparação com laboratório.',
      shortExplanation:
        'Microcanônico fixa E,V,N; canônico T,V,N; isotérmico-isobárico T,P,N. Cada um define quais flutuações e potenciais termodinâmicos são reproduzidos.',
      useFor: ['Planejar simulações', 'Interpretar médias', 'Calcular propriedades termodinâmicas'],
      prerequisites: ['Mecânica estatística', 'Termodinâmica'],
      relatedTopics: ['Ensemble canônico', 'Termostatos', 'Equipartição'],
      projectIdeas: [
        'Comparar densidade média em NVT vs NPT para mesmo fluido',
        'Verificar drift de energia em NVE com diferentes dt',
      ],
      professorQuestions: [
        'Qual ensemble o grupo usa para comparar com calorimetria/PMTA?',
        'Como garantir equilíbrio antes de produção em cada ensemble?',
      ],
    }),
    definePowerIdea({
      id: 'equipartition-md',
      title: 'Equipartição em dinâmica molecular',
      type: 'teorema',
      level: 'basico',
      whyItMatters:
        'Teste rápido de sanidade: se energias por modo não batem com kT/2, integrador ou potencial está errado.',
      shortExplanation:
        'Em equilíbrio canônico, energias médias por grau de liberdade quadrático tendem a kT/2. Desvios indicam modos congelados, dt inadequado ou não equilíbrio.',
      useFor: ['Validar simulação', 'Escolher dt', 'Diagnosticar potencial'],
      prerequisites: ['MD básico', 'Temperatura'],
      relatedTopics: ['Termostatos', 'Conservação de energia', 'Ensemble canônico'],
      projectIdeas: [
        'Gráfico de energia cinética por componente vs tempo até equilíbrio',
        'Equipartição em solvente vs soluto em solução',
      ],
      professorQuestions: [
        'Quais modos ficam fora de equipartição em biomoléculas que você simula?',
        'Equipartição é critério suficiente para declarar equilíbrio?',
      ],
    }),
    definePowerIdea({
      id: 'effective-potentials',
      title: 'Potenciais efetivos e force fields',
      type: 'aproximacao',
      level: 'intermediario',
      whyItMatters:
        'A qualidade da física em MD está no potencial — entender aproximações evita confundir artefato com descoberta.',
      shortExplanation:
        'Potenciais empíricos ou derivados de QM aproximam E(R) sem elétrons explícitos. Parâmetros controlam estrutura, equilíbrio e dinâmica; transferibilidade é limitada.',
      useFor: ['Escolher force field', 'Materiais e biomoléculas', 'Validação'],
      prerequisites: ['PES', 'Termodinâmica estatística'],
      relatedTopics: ['Born-Oppenheimer', 'RDF', 'Energia livre'],
      projectIdeas: [
        'Comparar duas force fields na mesma propriedade (densidade, ΔHvap)',
        'Derivação de parâmetros LJ a partir de curva de dissociação QM',
      ],
      professorQuestions: [
        'Qual force field o grupo considera padrão e por quê?',
        'Quando vale derivar potencial específico vs usar biblioteca genérica?',
      ],
    }),
    definePowerIdea({
      id: 'verlet-algorithm',
      title: 'Integrador de Verlet / velocity-Verlet',
      type: 'ferramenta-computacional',
      level: 'basico',
      whyItMatters:
        'Integração estável e simples é a base de quase todo MD — entender erro ajuda a não confundir física com artefato numérico.',
      shortExplanation:
        'Algoritmos de Verlet propagam posições e velocidades com erro O(dt²) e boa conservação de energia em NVE. Variantes velocity-Verlet são padrão em produção.',
      useFor: ['Rodar MD', 'Escolher passo de tempo', 'Energia conservada em NVE'],
      prerequisites: ['Mecânica clássica', 'Discretização'],
      relatedTopics: ['Conservação de energia', 'Termostatos', 'PBC'],
      projectIdeas: [
        'Estudar drift de energia vs dt para mesmo potencial',
        'Implementar Verlet em Python para partículas em 2D',
      ],
      professorQuestions: [
        'Qual dt máximo você aceita para o sistema que estudo?',
        'Integradores symplectic são obrigatórios nas publicações do grupo?',
      ],
    }),
    definePowerIdea({
      id: 'energy-conservation',
      title: 'Conservação de energia em NVE',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Energia total constante é o termômetro do integrador: sem ela, dinâmica microcanônica perde sentido.',
      shortExplanation:
        'Em NVE, E_total = K + V deve permanecer constante dentro do erro do integrador. Drift sistemático indica dt grande, forças incorretas ou instabilidade.',
      useFor: ['Validar integrador', 'Testes de sanidade', 'Escolher dt'],
      prerequisites: ['Verlet', 'Energia cinética e potencial'],
      relatedTopics: ['Verlet', 'Ensemble microcanônico', 'Termostatos'],
      projectIdeas: [
        'Monitorar E_total em simulação longa com múltiplos dt',
        'Corrigir unidades e comparar drift antes/depois',
      ],
      professorQuestions: [
        'Quanto drift de energia é aceitável antes de descartar uma trajetória?',
        'NVE é usado para propriedades dinâmicas no seu fluxo de trabalho?',
      ],
    }),
    definePowerIdea({
      id: 'periodic-boundary-conditions',
      title: 'Condições periódicas de contorno (PBC)',
      type: 'ferramenta-computacional',
      level: 'basico',
      whyItMatters:
        'Simula bulk sem superfícies artificiais dominantes — essencial para líquidos, sólidos e transporte.',
      shortExplanation:
        'A caixa de simulação se repete infinitamente; partículas que saem por uma face reentram pela oposta. Elimina efeitos de parede em propriedades extensivas de volume.',
      useFor: ['Simular fase condensada', 'Transporte', 'RDF e difusão'],
      prerequisites: ['Cristalografia básica', 'Vetores da caixa'],
      relatedTopics: ['Convenção da imagem mínima', 'RDF', 'MSD'],
      projectIdeas: [
        'Comparar pressão em cluster finito vs PBC no mesmo N',
        'Visualizar partículas com PBC em VMD/ovito',
      ],
      professorQuestions: [
        'Tamanho mínimo de caixa para evitar artefatos de auto-interação?',
        'PBC com cargas long-range: qual método o grupo usa (Ewald, PME)?',
      ],
    }),
    definePowerIdea({
      id: 'minimum-image-convention',
      title: 'Convenção da imagem mínima',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Distâncias erradas em PBC destroem forças e RDF — regra simples evita erros silenciosos.',
      shortExplanation:
        'A distância entre duas partículas é calculada entre a partícula e a imagem periódica mais próxima. Garante que |r_ij| ≤ metade do comprimento da caixa (em caixa cúbica).',
      useFor: ['Calcular forças em PBC', 'RDF', 'Vizinhança'],
      prerequisites: ['PBC', 'Vetores da caixa'],
      relatedTopics: ['PBC', 'RDF', 'Potenciais de corte'],
      projectIdeas: [
        'Implementar distância mínima imagem para caixa triclínica',
        'Testar RDF com e sem imagem mínima (bug intencional)',
      ],
      professorQuestions: [
        'Triclínico exige tratamento especial de imagem mínima no seu código?',
        'Cutoff maior que metade da caixa ainda é usado no grupo?',
      ],
    }),
    definePowerIdea({
      id: 'radial-distribution-function',
      title: 'Função de distribuição radial g(r)',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'Traduz simulação em estrutura mensurável comparável a difração — ponte direta simulação-experimento.',
      shortExplanation:
        'g(r) mede probabilidade relativa de encontrar partículas a distância r. Picos indicam shells de coordenação em líquidos e sólidos amorfos.',
      useFor: ['Validar estrutura', 'Comparar com X-ray/neutrons', 'Force fields'],
      prerequisites: ['PBC', 'Estatística de contagem'],
      relatedTopics: ['RDF', 'MSD', 'Potenciais efetivos'],
      projectIdeas: [
        'Calcular g(r) para argônio líquido e comparar com dados NIST',
        'g(r) soluto-solvente em solução aquosa',
      ],
      professorQuestions: [
        'Normalização de g(r) no grupo segue qual convenção (bulk density)?',
        'Quanto tempo de produção para g(r) convergir no seu sistema típico?',
      ],
    }),
    definePowerIdea({
      id: 'mean-squared-displacement',
      title: 'Deslocamento quadrático médio (MSD)',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'MSD liga simulação a difusão mensurável — regime linear vs subdifusão revela física de transporte.',
      shortExplanation:
        'MSD(t) = ⟨|r(t)−r(0)|²⟩. Em regime difusivo, MSD ~ 6Dt em 3D. Plateaus ou sublinear indicam confinamento, vidro ou trappping.',
      useFor: ['Coeficiente de difusão', 'Transporte', 'Validar líquidos'],
      prerequisites: ['Estatística de trajetórias', 'PBC'],
      relatedTopics: ['Flutuação-dissipação', 'RDF', 'Ergodicidade'],
      projectIdeas: [
        'Estimar D de Einstein a partir de MSD em água TIP3P',
        'Identificar regime balístico vs difusivo em curto tempo',
      ],
      professorQuestions: [
        'MSD linear exige qual critério de tempo mínimo no seu sistema?',
        'Como tratar moléculas flexíveis no MSD (centro de massa vs átomos)?',
      ],
    }),
    definePowerIdea({
      id: 'ergodicity-md',
      title: 'Ergodicidade e amostragem em MD',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'Trajetória curta pode não visitar fase relevante — saber quando média temporal falha evita conclusões erradas.',
      shortExplanation:
        'Propriedades calculadas como médias temporais pressupõem que a trajetória explore o ensemble. Barreiras altas e vidros quebram ergodicidade em tempos acessíveis.',
      useFor: ['Planejar tempo de simulação', 'Enhanced sampling', 'Interpretar médias'],
      prerequisites: ['Ensembles', 'Barreiras de energia'],
      relatedTopics: ['Paisagens de energia livre', 'Metadynamics', 'Ergodicidade estatística'],
      projectIdeas: [
        'Comparar duas trajetórias: mesma T, diferentes condições iniciais',
        'Block averaging para estimar erro em médias',
      ],
      professorQuestions: [
        'Quais métodos de enhanced sampling o grupo domina e recomenda?',
        'Como reportar incerteza estatística em propriedades de MD?',
      ],
    }),
    definePowerIdea({
      id: 'thermostats',
      title: 'Termostatos e barostatos',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'Controle de T e P é artificial — escolher algoritmo altera flutuações e dinâmica, não só temperatura média.',
      shortExplanation:
        'Nosé-Hoover, Langevin, Berendsen etc. acoplam o sistema a banhos fictícios. Barostatos (Parrinello-Rahman) permitem NPT. Escolha afeta ensemble e transporte.',
      useFor: ['Simulação NVT/NPT', 'Equilíbrio', 'Propriedades termodinâmicas'],
      prerequisites: ['Ensemble canônico', 'Integrador'],
      relatedTopics: ['Ensembles', 'Flutuação-dissipação', 'Equipartição'],
      projectIdeas: [
        'Comparar distribuição de energia com Nosé-Hoover vs Langevin',
        'Densidade de equilíbrio em NPT com diferentes barostatos',
      ],
      professorQuestions: [
        'Berendsen ainda é aceitável para equilíbrio no grupo ou proibido?',
        'Termostato afeta D calculado — qual você recomenda para transporte?',
      ],
    }),
    definePowerIdea({
      id: 'free-energy-landscapes',
      title: 'Paisagens de energia livre F(q)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Reduz muitos graus de liberdade a coordenadas reativas — visualiza mecanismos e barreiras como em química física.',
      shortExplanation:
        'Projetando a distribuição de Boltzmann em coordenadas coletivas q obtém-se F(q) = −kT ln P(q). Revela estados metaestáveis, caminhos e barreiras efetivas.',
      useFor: ['Mecanismos conformacionais', 'Ligação', 'Enhanced sampling'],
      prerequisites: ['Energia livre', 'MD estendida'],
      relatedTopics: ['Metadynamics', 'WHAM', 'TST'],
      projectIdeas: [
        'Construir F(φ,ψ) para dipeptídeo com umbrella sampling',
        'Comparar F(q) de metadynamics com WHAM no mesmo q',
      ],
      professorQuestions: [
        'Quais CVs são defensáveis para o sistema que pretendo publicar?',
        'WHAM vs metadynamics: qual fluxo o grupo prefere para ΔF?',
      ],
    }),
  ],
  nuclear: [
    definePowerIdea({
      id: 'binding-energy-per-nucleon',
      title: 'Energia de ligação por núcleon B/A',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'A curva B/A explica por que fusão e fissão liberam energia e onde o núcleo é mais estável — mapa mental da física nuclear.',
      shortExplanation:
        'B/A ≈ 8 MeV/nucleon no vale de estabilidade (Fe). Núcleos leves e muito pesados podem liberar energia ao se aproximarem do máximo via fusão ou fissão.',
      useFor: ['Balanço de energia nuclear', 'Escolher reações', 'Estabilidade nuclear'],
      prerequisites: ['Defeito de massa', 'E=mc²'],
      relatedTopics: ['Defeito de massa', 'SEMF', 'Modelo de gota líquida'],
      projectIdeas: [
        'Plotar curva B/A empírica e marcar reações de fusão/fissão exemplo',
        'Calcular energia liberada em D-T a partir de massas tabuladas',
      ],
      professorQuestions: [
        'Como incertezas em massas atômicas afetam cálculos de Q-value no grupo?',
        'B/A é suficiente para comparar candidatos a reação de reactor?',
      ],
    }),
    definePowerIdea({
      id: 'mass-defect',
      title: 'Defeito de massa e equivalência massa-energia',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Energia nuclear vem da diferença de massa, não de “queimar matéria” — muda como você lê tabelas e balanços.',
      shortExplanation:
        'A massa do núcleo é menor que a soma das massas dos nucleons livres; o defeito Δm vira energia de ligação via E=Δmc². Q-values de reações vêm de diferenças de massa.',
      useFor: ['Calcular Q', 'Calibração de detectores', 'Balanço de reator'],
      prerequisites: ['Massa atômica', 'Conservação de energia'],
      relatedTopics: ['Energia de ligação por núcleon', 'Decaimento radioativo', 'SEMF'],
      projectIdeas: [
        'Planilha de Q-values para cadeia de decaimento simples',
        'Comparar Δm tabulado com energia de ligação calculada',
      ],
      professorQuestions: [
        'Quais bases de dados de massa o grupo padroniza (AME, ENDF)?',
        'Massa atômica vs nuclear: qual convenção em publicações?',
      ],
    }),
    definePowerIdea({
      id: 'radioactive-decay-law',
      title: 'Lei do decaimento radioativo N(t)=N₀e^{-λt}',
      type: 'lei',
      level: 'basico',
      whyItMatters:
        'Transforma meia-vida em previsão de dose, inventário e segurança — linguagem universal em radioquímica e medicina.',
      shortExplanation:
        'Decaimento exponencial com constante λ ou período T₁/₂. Atividades A=λN ligam número de átomos à taxa de contagem.',
      useFor: ['Dosimetria', 'Inventário de rejeitos', 'Datação'],
      prerequisites: ['Logaritmos', 'Atividade e número de átomos'],
      relatedTopics: ['Equilíbrio secular', 'Cadeias de decaimento', 'Regra de Fermi'],
      projectIdeas: [
        'Ajustar λ a dados de contagem com incerteza',
        'Simular decaimento de mistura de dois isótopos',
      ],
      professorQuestions: [
        'Como tratar decaimento com incerteza em λ nas análises do grupo?',
        'Atividade vs concentração: qual grandeza reportar em qual contexto?',
      ],
    }),
    definePowerIdea({
      id: 'secular-equilibrium',
      title: 'Equilíbrio secular e transiente',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Em cadeias longas, filhos herdam taxa do ancestral — essencial para inventário, ambiente e combustível gasto.',
      shortExplanation:
        'Se T₁/₂(pai) ≫ T₁/₂(filho), atividade do filho ≈ atividade do pai. Equilíbrio secular simplifica cadeias U-Th, produtos de fissão e ambientais.',
      useFor: ['Cadeias naturais', 'Combustível gasto', 'Modelagem ambiental'],
      prerequisites: ['Lei do decaimento', 'Cadeias'],
      relatedTopics: ['Cadeias de decaimento', 'Transporte', 'Química nuclear'],
      projectIdeas: [
        'Resolver Bateman para cadeia de 3 membros e plotar atividades',
        'Identificar regime secular em cadeia U-238',
      ],
      professorQuestions: [
        'Quando equilíbrio secular falha nos cenários que você modela?',
        'Química separa filho do pai — como isso entra no inventário?',
      ],
    }),
    definePowerIdea({
      id: 'cross-section-nuclear',
      title: 'Seção de choque nuclear σ',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Probabilidade de interação em escala microscópica vira taxas macroscópicas — núcleo da física de reatores e detectores.',
      shortExplanation:
        'σ mede probabilidade efetiva de um processo (fissão, captura, espalhamento). Taxas macroscópicas usam Σ = N σ; dependem de energia do neutron.',
      useFor: ['Física de reatores', 'Blindagem', 'Monte Carlo de transporte'],
      prerequisites: ['Fluxo de partículas', 'Densidade numérica'],
      relatedTopics: ['Transporte neutronico', 'Multiplicação', 'ENDF'],
      projectIdeas: [
        'Plotar σ(E) de fissão e captura para U-235 a partir de ENDF',
        'Calcular comprimento de atenuação Σ⁻¹ para blindagem',
      ],
      professorQuestions: [
        'Qual biblioteca de seções de choque o grupo valida (ENDF/B, JEFF)?',
        'Incerteza em σ propaga como para k_eff nos seus cálculos?',
      ],
    }),
    definePowerIdea({
      id: 'semf',
      title: 'Fórmula semiempírica de massa (SEMF)',
      type: 'aproximacao',
      level: 'intermediario',
      whyItMatters:
        'Resume estabilidade nuclear em termos físicos (volume, superfície, Coulomb, assimetria, pairing) — mapa rápido do chart of nuclides.',
      shortExplanation:
        'SEMF estima energia de ligação com termos de volume, superfície, Coulomb, assimetria e pairing. Prediz linha de estabilidade e energia de fissão qualitativa.',
      useFor: ['Estimar Q', 'Estabilidade', 'Educar modelo de gota'],
      prerequisites: ['Energia de ligação', 'Número Z, N, A'],
      relatedTopics: ['Modelo de gota líquida', 'Modelo de camadas', 'B/A'],
      projectIdeas: [
        'Implementar SEMF e plotar curva de valley of stability',
        'Comparar SEMF com massas tabuladas para região de interesse',
      ],
      professorQuestions: [
        'SEMF ainda é útil no grupo ou só pedagógico frente a massas experimentais?',
        'Termo de pairing: como explicar magic numbers com estudantes?',
      ],
    }),
    definePowerIdea({
      id: 'liquid-drop-model',
      title: 'Modelo de gota líquida',
      type: 'aproximacao',
      level: 'intermediario',
      whyItMatters:
        'Intuição macroscópica para núcleos: tensão superficial e carga explicam fissão e estabilidade sem resolver QCD.',
      shortExplanation:
        'Trata o núcleo como gota incompressível com termos de volume, superfície e Coulomb. Base da SEMF e visão de instabilidade para núcleos pesados.',
      useFor: ['Fissão qualitativa', 'Barreiras', 'Estabilidade'],
      prerequisites: ['SEMF', 'Eletrostática básica'],
      relatedTopics: ['SEMF', 'Fissão', 'Modelo de camadas'],
      projectIdeas: [
        'Estimar energia de fissão qualitativa deformando gota',
        'Comparar raio nuclear R~A^{1/3} com dados',
      ],
      professorQuestions: [
        'Limites do modelo de gota para núcleos muito leves ou halo?',
        'Como conectar gota líquida a cálculos de barreira de fissão modernos?',
      ],
    }),
    definePowerIdea({
      id: 'shell-model',
      title: 'Modelo de camadas nuclear',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Números mágicos e espectros não saem da gota líquida — camadas trazem estrutura tipo átomo para o núcleo.',
      shortExplanation:
        'Nucleons ocupam potenciais médios com fechamento de camadas (magic numbers). Explica períodos, spins-paridade e descontinuidades em B/A.',
      useFor: ['Interpretar níveis', 'Decaimentos permitidos', 'Estabilidade'],
      prerequisites: ['Mecânica quântica', 'Partícula em poço'],
      relatedTopics: ['Regra de Fermi', 'SEMF', 'Spin'],
      projectIdeas: [
        'Esquema de níveis para núcleo duplo-magico simplificado',
        'Tabela de previsões de spin-paridade para decaimento beta',
      ],
      professorQuestions: [
        'Quando usar shell model vs modelos coletivos no seu problema?',
        'Dados ENDF de níveis excitados são confiáveis para sua aplicação?',
      ],
    }),
    definePowerIdea({
      id: 'fermi-golden-rule',
      title: 'Regra de ouro de Fermi',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Taxas de transição ligam estrutura microscópica a observáveis — decaimentos, captura e espalhamento inelastico.',
      shortExplanation:
        'A taxa de transição entre estados inicial e final é proporcional à densidade de estados finais e ao elemento de matriz |⟨f|H′|i⟩|². Base de decaimento beta e reações de primeira ordem.',
      useFor: ['Taxas de decaimento', 'Larguras de ressonância', 'Acoplamento perturbativo'],
      prerequisites: ['Teoria de perturbação temporal', 'Estados densos'],
      relatedTopics: ['Decaimento beta', 'Seção de choque', 'Modelo de camadas'],
      projectIdeas: [
        'Estimar largura de nível com densidade de estados modelo',
        'Ordem de grandeza de taxa beta usando matriz elemento tabulado',
      ],
      professorQuestions: [
        'A regra de ouro é ensinada com exemplos do grupo (beta, gamma)?',
        'Como densidade de estados final é modelada em reações que você estuda?',
      ],
    }),
    definePowerIdea({
      id: 'criticality',
      title: 'Criticalidade e multiplicação de nêutrons',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'k_eff = 1 é a fronteira entre subcrítico seguro e supercrítico perigoso — conceito central em física e segurança.',
      shortExplanation:
        'Cada geração de nêutrons deve repor a anterior: k_eff = (número produzido)/(número que causaram fissão). k>1 cresce população; k<1 decai.',
      useFor: ['Reatores', 'Segurança', 'Subcrítico em armazenamento'],
      prerequisites: ['Seção de choque', 'Fissão'],
      relatedTopics: ['k_eff', 'Seis fatores', 'Transporte'],
      projectIdeas: [
        'Simular cadeia de gerações com k dado (modelo discreto)',
        'Estimar massa crítica qualitativa variando espessura de moderador',
      ],
      professorQuestions: [
        'Como o grupo separa exercícios acadêmicos de análise crítica licenciada?',
        'Subcrítico com moderador: qual experimento didático existe?',
      ],
    }),
    definePowerIdea({
      id: 'moderation',
      title: 'Moderação de nêutrons',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Nêutrons térmicos reagem diferente — moderador é alavanca para controle de espectro e criticidade.',
      shortExplanation:
        'Colisões elásticas com núcleos leves reduzem energia média do espectro. Moderadores (H, D, grafito) maximizam fissão térmica em certos combustíveis.',
      useFor: ['Projeto de reator', 'Blindagem', 'Espectrometria'],
      prerequisites: ['Espalhamento', 'Energia cinética em colisões'],
      relatedTopics: ['Seção de choque σ(E)', 'k_eff', 'Transporte'],
      projectIdeas: [
        'Simular espectro após N colisões em H (modelo simplificado)',
        'Comparar moderador H vs D para espectro térmico',
      ],
      professorQuestions: [
        'Espectro epitérmico importa no seu combustível-alvo?',
        'Moderador vs reflexor: qual papel no seu desenho conceitual?',
      ],
    }),
    definePowerIdea({
      id: 'transport-equation',
      title: 'Equação de transporte de nêutrons',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Unifica geometria, material e σ em um formalismo — base de códigos MCNP/OpenMC e cálculo de reator.',
      shortExplanation:
        'Balanço de nêutrons em fase-espaço inclui fonte, remoção, espalhamento e absorção. Forma integral e difusão aproximam fluxo em sistemas complexos.',
      useFor: ['Simulação de reator', 'Blindagem', 'k_eff e fluxos'],
      prerequisites: ['Seção de choque', 'Fluxo', 'Conservação'],
      relatedTopics: ['Monte Carlo', 'k_eff', 'Difusão de nêutrons'],
      projectIdeas: [
        'Resolver equação de difusão 1 grupo em esfera homogênea',
        'Comparar fluxo analítico 1D com tally de Monte Carlo educacional',
      ],
      professorQuestions: [
        'Quando difusão é aceitável vs transporte completo no seu problema?',
        'Qual código o grupo usa para validar resultados de transporte?',
      ],
    }),
  ],
  engenharia_nuclear: [
    definePowerIdea({
      id: 'k-effective',
      title: 'Fator de multiplicação efetivo k_eff',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'k_eff resume se o arranjo ganha, mantém ou perde nêutrons — linguagem comum entre física, operação e licenciamento.',
      shortExplanation:
        'k_eff é a razão entre nêutrons de uma geração e a anterior em regime estacionário. Reatores críticos operam em k_eff≈1 com margens de segurança.',
      useFor: ['Projeto de núcleo', 'Subcrítico', 'Análise de acidentes'],
      prerequisites: ['Criticalidade', 'Seção de choque'],
      relatedTopics: ['Seis fatores', 'Reatividade', 'Cinética pontual'],
      projectIdeas: [
        'Estimar k_eff com fórmula de seis fatores e comparar com MCNP',
        'Sensibilidade de k a enriquecimento e moderador',
      ],
      professorQuestions: [
        'Qual incerteza em k_eff o licenciador exige no seu contexto?',
        'k_eff vs k_inf: quando cada um é reportado?',
      ],
    }),
    definePowerIdea({
      id: 'six-factor-formula',
      title: 'Fórmula dos seis fatores',
      type: 'identidade-matematica',
      level: 'intermediario',
      whyItMatters:
        'Decompõe k em etapas físicas — mostra onde melhorar combustível, moderador ou reflexor.',
      shortExplanation:
        'k_inf = η f p ε ε̄ (notação clássica com reprodução rápida, fator de utilização térmica, etc.). Cada fator isola perdas e conversões no ciclo neutronico.',
      useFor: ['Design conceitual', 'Pedagogia de reator', 'Otimização de lattice'],
      prerequisites: ['k_eff', 'Espectro de nêutrons'],
      relatedTopics: ['k_eff', 'Moderação', 'Reatividade'],
      projectIdeas: [
        'Planilha dos seis fatores para configuração didática',
        'Identificar fator limitante em cenário hipotético',
      ],
      professorQuestions: [
        'A fórmula dos seis fatores ainda guia projetos no grupo ou é só pedagógica?',
        'Como η e f são obtidos de bibliotecas modernas?',
      ],
    }),
    definePowerIdea({
      id: 'point-kinetics',
      title: 'Cinética pontual de reator',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Liga reatividade a evolução temporal de potência — essencial para transientes e controle.',
      shortExplanation:
        'Equações acopladas para n e precursores com coeficientes de grupo. Aproximação espacial integrada; captura retardamento por nêutrons atrasados.',
      useFor: ['Transientes', 'Controle de potência', 'Análise de inserção de reatividade'],
      prerequisites: ['k_eff', 'Nêutrons atrasados'],
      relatedTopics: ['Reatividade', 'Nêutrons atrasados', 'Feedback Doppler'],
      projectIdeas: [
        'Resolver cinética pontual para degrau de reatividade pequeno',
        'Comparar resposta com e sem grupos de precursores',
      ],
      professorQuestions: [
        'Quantos grupos de precursores são usados nas análises do grupo?',
        'Limites da cinética pontual no seu dispositivo (espacial)?',
      ],
    }),
    definePowerIdea({
      id: 'delayed-neutrons',
      title: 'Nêutrons atrasados e grupos de precursores',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Sem atraso, reator seria incontrolável em ms — nêutrons atrasados compram tempo humano e automático.',
      shortExplanation:
        'Fração β de nêutrons vem de decaimento beta de precursores. Grupos com constantes λ_i modelam o retardamento e estabilizam feedback de potência.',
      useFor: ['Cinética', 'Controle', 'Margem de segurança'],
      prerequisites: ['Decaimento beta', 'Cinética pontual'],
      relatedTopics: ['Reatividade', 'Cinética pontual', 'Acidentes'],
      projectIdeas: [
        'Plotar resposta de potência com β total vs só prompt',
        'Sensibilidade do período de reactor a β efetivo',
      ],
      professorQuestions: [
        'β efetivo muda com espectro — como o grupo trata isso?',
        'Precursores em combustível MOX diferem quantitativamente?',
      ],
    }),
    definePowerIdea({
      id: 'reactivity',
      title: 'Reatividade ρ e inserção de dollars',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Mede “quão longe” de crítico de forma linearizada — linguagem de operação e experimentos de pulso.',
      shortExplanation:
        'ρ = (k−1)/k. Em dollars, ρ/β. Pequenas inserções ligam-se à resposta de cinética; grandes exigem modelos não lineares.',
      useFor: ['Controle de barras', 'Experimentos', 'Margens'],
      prerequisites: ['k_eff', 'Nêutrons atrasados'],
      relatedTopics: ['Cinética pontual', 'Coeficiente de vazio', 'Doppler'],
      projectIdeas: [
        'Converter inserção de pcm em ρ e estimar resposta linear',
        'Simular pulso de reatividade pequeno em modelo pontual',
      ],
      professorQuestions: [
        'Qual unidade (pcm, dollars, mk) o grupo padroniza em relatórios?',
        'Reatividade excessiva em testes: qual limite institucional?',
      ],
    }),
    definePowerIdea({
      id: 'doppler-feedback',
      title: 'Feedback Doppler (ressonância)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Feedback intrínseco negativo estabiliza potência — primeiro mecanismo de segurança passiva no combustível.',
      shortExplanation:
        'Aquecimento do combustível alarga ressonâncias de captura em U-238, reduzindo fissão efetiva. Coeficiente de reatividade negativo com temperatura do combustível.',
      useFor: ['Segurança de reator', 'Transientes LOCA', 'Licenciamento'],
      prerequisites: ['Seção de choque vs E', 'Reatividade'],
      relatedTopics: ['Coeficiente de vazio', 'k_eff', 'Acidentes'],
      projectIdeas: [
        'Estimar ordem de grandeza do coeficiente Doppler com modelo simplificado',
        'Revisar papel do Doppler em transientes publicados',
      ],
      professorQuestions: [
        'Doppler compensa quais inserções positivas no seu cenário?',
        'Modelagem multi-física acopla Doppler como no grupo?',
      ],
    }),
    definePowerIdea({
      id: 'void-coefficient',
      title: 'Coeficiente de reatividade de vazio',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Vaporização do refrigerante pode aumentar ou diminuir k — sinal errado causou acidentes históricos.',
      shortExplanation:
        'Mudança de densidade do moderante/reflector altera espectro e absorção. α_v = dρ/d(fração de vazio) deve ser negativo em muitos projetos LWR.',
      useFor: ['Segurança LWR', 'Análise de LOCA', 'Design de lattice'],
      prerequisites: ['k_eff', 'Moderação'],
      relatedTopics: ['Doppler', 'Reatividade', 'Defesa em profundidade'],
      projectIdeas: [
        'Qualitative map α_v vs geometria de lattice simplificada',
        'Estudo de caso Chernobyl/Three Mile Island em termos de feedback',
      ],
      professorQuestions: [
        'Como garantir α_v negativo durante todo o ciclo de queima?',
        'SMRs alteram α_v de forma relevante no seu tema?',
      ],
    }),
    definePowerIdea({
      id: 'burnup',
      title: 'Queima de combustível (burnup)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Combustível evolui com irradiacao — composição, venenos e propriedades mudam ao longo do ciclo.',
      shortExplanation:
        'Burnup (GWd/tU) mede energia extraída. Gera produtos de fissão, transmutações e degradação física que alteram k, calor e segurança.',
      useFor: ['Ciclo do combustível', 'Licenciamento', 'Química nuclear'],
      prerequisites: ['Reações de fissão', 'Inventário isotópico'],
      relatedTopics: ['k_eff', 'Química de combustível gasto', 'PSA'],
      projectIdeas: [
        'Evolução simplificada de k com burnup em planilha',
        'Inventário de Pu e actinídeos vs burnup com cadeia',
      ],
      professorQuestions: [
        'Qual burnup máximo o grupo assume para análises de desempenho?',
        'Códigos de burnup acoplados ao transporte são validados como?',
      ],
    }),
    definePowerIdea({
      id: 'safety-margin',
      title: 'Margem de segurança e limites operacionais',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Projeto não opera no limite físico, mas dentro de margens — cultura de engenharia nuclear.',
      shortExplanation:
        'Limites em linear power, ΔT, pressão e inserção de reatividade garantem distância de condições de dano ao combustível ou ruptura.',
      useFor: ['Operação', 'Licenciamento', 'Análise determinística'],
      prerequisites: ['Feedback', 'Materiais de combustível'],
      relatedTopics: ['Defesa em profundidade', 'PSA', 'ALARA'],
      projectIdeas: [
        'Tabela de limites técnicos vs margem para cenário didático',
        'Árvore de falhas para violação de margem térmica',
      ],
      professorQuestions: [
        'Quais margens são prescritivas vs analíticas no seu regulador?',
        'Como margens aparecem em artigos acadêmicos vs indústria?',
      ],
    }),
    definePowerIdea({
      id: 'defense-in-depth',
      title: 'Defesa em profundidade',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Falhas são esperadas; barreiras independentes evitam que um erro simples vire liberação — mudança de mindset de projeto.',
      shortExplanation:
        'Múltiplas barreiras (combustível, envoltório, circuito primário, contenção) e níveis de proteção independentes. Redundância e diversidade reduzem risco.',
      useFor: ['Design de usina', 'Cultura de segurança', 'Licenciamento'],
      prerequisites: ['Introdução a sistemas nucleares'],
      relatedTopics: ['PSA', 'ALARA', 'Margem de segurança'],
      projectIdeas: [
        'Diagrama de barreiras para SMR vs PWR grande',
        'Estudo de caso: qual barreira falhou em acidente histórico',
      ],
      professorQuestions: [
        'Como o grupo ensina defesa em profundidade em projetos de IC?',
        'Barreiras passivas contam como camada independente?',
      ],
    }),
    definePowerIdea({
      id: 'alara',
      title: 'Princípio ALARA',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Dose não é só cumprir limite — reduzir razoavelmente tudo que for praticável molda projeto e operação.',
      shortExplanation:
        'As Low As Reasonably Achievable: otimizar tempo, distância e blindagem além do limite regulatório quando custo-benefício justifica.',
      useFor: ['Proteção radiológica', 'Projeto de instalações', 'Planejamento de manutenção'],
      prerequisites: ['Dosimetria básica', 'Limites de dose'],
      relatedTopics: ['Proteção radiológica', 'PSA', 'Química nuclear (hot cell)'],
      projectIdeas: [
        'Plano ALARA para manutenção simulada em sala controlada',
        'Comparar duas configurações de blindagem por dose estimada',
      ],
      professorQuestions: [
        'ALARA entra em critérios de aceite de experimentos no laboratório?',
        'Como documentar “razoavelmente exequível” em projetos estudantis?',
      ],
    }),
    definePowerIdea({
      id: 'psa',
      title: 'Análise probabilística de segurança (PSA)',
      type: 'metodo',
      level: 'pesquisa',
      whyItMatters:
        'Combina falhas raras em árvores — quantifica risco onde determinismo sozinho não prioriza cenários.',
      shortExplanation:
        'PSA integra PRA de eventos iniciadores, árvores de falha e eventos, e análise de consequência. Frequências de danos ao núcleo e liberação orientam melhorias.',
      useFor: ['Licenciamento', 'Priorização de upgrades', 'Regulação'],
      prerequisites: ['Probabilidade', 'Sistemas de segurança'],
      relatedTopics: ['Defesa em profundidade', 'Margem de segurança', 'Acidentes'],
      projectIdeas: [
        'Event tree didático para perda de refrigerante simplificado',
        'Fault tree para falha de válvula de segurança em nível tutorial',
      ],
      professorQuestions: [
        'PSA nível 1/2/3: qual escopo é realista em TCC do grupo?',
        'Dados de falha de componentes: quais fontes o orientador aceita?',
      ],
    }),
  ],
  quimica_nuclear: [
    definePowerIdea({
      id: 'separation-factors',
      title: 'Fatores de separação e distribuição',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Quantifica química de particionamento — sem α ou D, reprocessamento e purificação são tentativa e erro.',
      shortExplanation:
        'α = (y_A/y_B)/(x_A/x_B) em fases ou D = [A]_org/[A]_aq descrevem preferência por fase. Governam cascatas de extração e purificação de actinídeos.',
      useFor: ['Reprocessamento', 'Radioquímica analítica', 'Purificação de radiofármacos'],
      prerequisites: ['Equilíbrio químico', 'Termodinâmica de soluções'],
      relatedTopics: ['Extração por solvente', 'Especiação', 'Cadeias de decaimento'],
      projectIdeas: [
        'Calcular estágios teóricos para α fixo em cascata',
        'Medir D por LLE em sistema U simulado não radioativo',
      ],
      professorQuestions: [
        'α medido em bancada escala para processo do grupo?',
        'Como impurezas orgânicas alteram D no seu sistema?',
      ],
    }),
    definePowerIdea({
      id: 'solvent-extraction',
      title: 'Extração por solvente (PUREX e variantes)',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Processo industrial que separa U/Pu do combustível gasto — ponte entre física de reator e química de ciclo fechado.',
      shortExplanation:
        'Contato orgânico-aquoso com extratantes seletivos (TBP, aminas) transfere espécies. Cascatas multistágio alcançam especificações de pureza.',
      useFor: ['Reprocessamento', 'Análise radioquímica', 'Gestão de rejeitos'],
      prerequisites: ['Fatores de separação', 'Química de coordenação'],
      relatedTopics: ['Radiólise', 'Química de actinídeos', 'Hot cell'],
      projectIdeas: [
        'Diagrama de fluxo PUREX simplificado com mass balance',
        'Simular N estágios com α constante em Python',
      ],
      professorQuestions: [
        'Alternativas ao PUREX (pyro, fluor) são relevantes na sua linha?',
        'Gestão de rejeito orgânico radiativo: restrições do laboratório?',
      ],
    }),
    definePowerIdea({
      id: 'radiolysis',
      title: 'Radiólise de solventes e eletrólitos',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Radiação degrada ligantes e gera gases — limita vida útil de processos e explica produtos secundários.',
      shortExplanation:
        'Partículas ionizantes quebram moléculas de solvente, gerando radicais e gases (H₂, etc.). Altera redox, viscosidade e segurança em processos altamente ativos.',
      useFor: ['Reprocessamento', 'Armazenamento de rejeitos líquidos', 'Síntese em alvo'],
      prerequisites: ['Química radiacional', 'Dose absorvida'],
      relatedTopics: ['Extração por solvente', 'Especiação', 'ALARA'],
      projectIdeas: [
        'Revisar rendimento G para H₂ em água e impacto em vasos de armazenamento',
        'Estimar dose em solvente orgânico em contato com combustível gasto',
      ],
      professorQuestions: [
        'Radiólise é medida ou apenas modelada nos seus processos?',
        'Scavengers químicos são usados no grupo para mitigar radiólise?',
      ],
    }),
    definePowerIdea({
      id: 'spent-fuel-chemistry',
      title: 'Química do combustível irradiado',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'O combustível é um material novo após burnup — clivagem, gases e alteração de matriz mudam manuseio e processos.',
      shortExplanation:
        'Fission products e actinídeos se redistribuem na matriz; gases de fissão pressurizam; clad interage. Define dissolução, volatilidade e risco de liberação.',
      useFor: ['Reprocessamento', 'Armazenamento seco', 'Modelagem de fonte'],
      prerequisites: ['Burnup', 'Produtos de fissão'],
      relatedTopics: ['Cadeias de decaimento', 'Radiólise', 'Hot cell'],
      projectIdeas: [
        'Inventário simplificado de FP após 45 GWd/tU',
        'Mapa de volatilidade Cs/I no aquecimento de pó oxidado',
      ],
      professorQuestions: [
        'Dissolução nitrica: quais parâmetros o grupo controla em escala piloto?',
        'Combustível acidentado (LOCA) muda química de dissolução como?',
      ],
    }),
    definePowerIdea({
      id: 'actinide-chemistry',
      title: 'Química de actinídeos (U, Pu, Np, Am)',
      type: 'conceito-chave',
      level: 'pesquisa',
      whyItMatters:
        'Estados de oxidação e complexação governam separação, criticalidade e ambiente — erro de valência é erro de inventário.',
      shortExplanation:
        'Actinídeos exibem múltiplos estados redox e química de coordenação rica. Especiação em ácido, redox e complexantes controla separação e mobilidade.',
      useFor: ['Reprocessamento', 'Gestão de rejeito', 'Ambiente'],
      prerequisites: ['Química inorgânica', 'Eletroquímica'],
      relatedTopics: ['Especiação', 'Extração', 'Criticalidade'],
      projectIdeas: [
        'Diagrama Eh-pH esquemático para U e Pu em solução',
        'Estimar massa de Pu para subcrítico em geometria dada',
      ],
      professorQuestions: [
        'Espectroscopia (UV-vis, EXAFS) é acessível para especiação no grupo?',
        'Minor actinídeos entram no escopo do seu projeto de ciclo?',
      ],
    }),
    definePowerIdea({
      id: 'hot-cell',
      title: 'Hot cell e manipulação de alta atividade',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'A interface entre química e segurança: sem hot cell adequada, análise radioquímica avançada não acontece.',
      shortExplanation:
        'Células blindadas com manipuladores remotos permitem dissolução, separação e análise de amostras altamente ativas com fluxo controlado de ar e rejeitos.',
      useFor: ['Radioquímica', 'Desenvolvimento de processo', 'Caracterização pós-irradiacao'],
      prerequisites: ['Proteção radiológica', 'ALARA'],
      relatedTopics: ['ALARA', 'Especiação', 'Extração'],
      projectIdeas: [
        'Fluxograma de entrada/saída de hot cell para análise alvo',
        'Checklist de contenção para experimento com α,n',
      ],
      professorQuestions: [
        'Quais atividades (Bq) exigem hot cell vs cabine de fluxo no seu lab?',
        'Treinamento de manipulação remota: existe no grupo ou parceria?',
      ],
    }),
    definePowerIdea({
      id: 'decay-chains',
      title: 'Cadeias de decaimento e inventário isotópico',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Calor, dose e radiotoxicidade evoluem no tempo — inventário dinâmico é obrigatório em rejeito e combustível.',
      shortExplanation:
        'Bateman ou códigos de burnup resolvem atividades ao longo do tempo. Filhos ingrow alteram calor residual, dose e requisitos de refrigeração.',
      useFor: ['Armazenamento', 'Transporte', 'Reprocessamento'],
      prerequisites: ['Lei do decaimento', 'Equilíbrio secular'],
      relatedTopics: ['Burnup', 'Especiação', 'Radiólise'],
      projectIdeas: [
        'Curva de calor residual vs tempo pós-desligamento (simplificado)',
        'Inventário de Sr-90 e Cs-137 após cooling de 10 anos',
      ],
      professorQuestions: [
        'Qual código de decaimento/inventário o orientador recomenda?',
        'Heat load define geometria de armazenamento no seu estudo?',
      ],
    }),
    definePowerIdea({
      id: 'speciation',
      title: 'Especiação química em meio aquoso',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'O mesmo elemento se comporta de formas distintas — separação, mobilidade e toxicidade dependem da espécie real.',
      shortExplanation:
        'Hidrólise, complexação e redox definem espécies dominantes. Modelos com constantes de formação e Eh-pH predizem comportamento em processo e ambiente.',
      useFor: ['Lixiviação', 'Reprocessamento', 'Remediação'],
      prerequisites: ['Equilíbrio químico', 'Coordenação'],
      relatedTopics: ['Química de actinídeos', 'Extração', 'Radiólise'],
      projectIdeas: [
        'Calcular fração de espécies U(VI) carbonato vs hidróxido vs pH',
        'Revisar impacto de nitrato em especiação de Pu',
      ],
      professorQuestions: [
        'Técnicas experimentais de especiação disponíveis para o meu projeto?',
        'Modelos de complexação do grupo são validados contra qual base de dados?',
      ],
    }),
  ],
};
