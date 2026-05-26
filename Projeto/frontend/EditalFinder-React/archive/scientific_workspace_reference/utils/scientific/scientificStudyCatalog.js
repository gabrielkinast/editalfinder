import { STUDY_CATALOG_PHASE_2B } from './scientificStudyCatalogPhase2B';

/**
 * Catálogo local de trilhas por tema (Fase 2 + 2B — sem IA externa).
 */
const STUDY_CATALOG_CORE = {
  nuclear: {
    label: 'Nuclear',
    fundamentals: [
      'Decaimento radioativo',
      'Interação radiação-matéria',
      'Fissão e fusão',
      'Reatores nucleares',
      'Blindagem e dosimetria',
    ],
    intermediate: [
      'Seção de choque',
      'Transporte de nêutrons',
      'Cinética de reatores',
      'Transferência de calor',
      'Materiais nucleares',
    ],
    advanced: [
      'Monte Carlo para transporte de partículas',
      'Queima de combustível nuclear',
      'Termo-hidráulica',
      'Segurança nuclear',
      'Materiais sob radiação',
    ],
    books: [
      'Krane — Introductory Nuclear Physics',
      'Lamarsh — Introduction to Nuclear Engineering',
      'Duderstadt & Hamilton — Nuclear Reactor Analysis',
    ],
    practicalProjects: [
      'Simulação de decaimento radioativo em Python',
      'Modelo simples de blindagem',
      'Cálculo de atividade de uma amostra',
      'Simulação Monte Carlo 1D simplificada',
    ],
    researchIdeas: [
      'Materiais para ambientes radioativos',
      'Otimização de blindagem',
      'Modelagem de difusão térmica em combustível nuclear',
      'Análise computacional de transporte de nêutrons simplificado',
    ],
    professorQuestions: [
      'Quais aproximações são aceitáveis para um modelo simples de blindagem?',
      'Como conectar decaimento radioativo com transferência de calor?',
      'Que materiais são mais usados em ambientes radioativos?',
    ],
  },
  fisico_quimica: {
    label: 'Físico-química',
    fundamentals: [
      'Termodinâmica e equilíbrio',
      'Cinética química',
      'Eletroquímica básica',
      'Espectroscopia introdutória',
      'Estados da matéria',
    ],
    intermediate: [
      'Mecânica estatística',
      'Teoria do estado de transição',
      'Química quântica molecular (HF/DFT intro)',
      'Transporte de massa',
      'Reações em fase condensada',
    ],
    advanced: [
      'Dinâmica molecular',
      'Simulação de reações com solvente',
      'Modelagem de superfícies',
      'Catálise heterogênea',
      'Espectroscopia avançada (RMN, IR)',
    ],
    books: [
      'Atkins — Physical Chemistry',
      'Levine — Quantum Chemistry',
      'McQuarrie — Statistical Mechanics',
    ],
    practicalProjects: [
      'Ajuste de curva cinética em Python',
      'Diagrama de fases simplificado',
      'Cálculo de constante de equilíbrio a partir de dados',
      'Visualização de perfis de concentração',
    ],
    researchIdeas: [
      'Estimativa de parâmetros cinéticos a partir de dados experimentais',
      'Modelo microscópico simplificado de adsorção',
      'Comparação de métodos de integração para cinética',
    ],
    professorQuestions: [
      'Quais variáveis controlam a cinética do sistema?',
      'Como estimar parâmetros a partir de dados experimentais?',
      'Como conectar termodinâmica e simulação molecular?',
    ],
  },
  materiais: {
    label: 'Ciência de materiais',
    fundamentals: [
      'Estrutura cristalina',
      'Ligações e propriedades mecânicas',
      'Diagramas de fase',
      'Cerâmicas e polímeros',
      'Caracterização básica',
    ],
    intermediate: [
      'Defeitos cristalinos',
      'Difusão em sólidos',
      'Comportamento mecânico sob carga',
      'Materiais para altas temperaturas',
      'Nanomateriais',
    ],
    advanced: [
      'Materiais sob radiação',
      'Compósitos estruturais',
      'Modelagem FEM simplificada',
      'Corrosão e degradação',
      'Seleção de materiais (Ashby)',
    ],
    books: [
      'Callister — Materials Science and Engineering',
      'Ashby — Materials Selection in Mechanical Design',
      'Kittel — Solid State Physics (referência)',
    ],
    practicalProjects: [
      'Comparativo de propriedades mecânicas',
      'Estimativa de constante de difusão',
      'Revisão de materiais para reatores',
      'Gráficos de seleção de materiais',
    ],
    researchIdeas: [
      'Defeitos induzidos por radiação em ligas',
      'Propriedades térmicas em ambientes extremos',
      'Interfaces em materiais multifásicos',
    ],
    professorQuestions: [
      'Como defeitos cristalinos afetam propriedades mecânicas?',
      'Como modelar difusão em sólidos?',
      'Quais propriedades importam em materiais para radiação?',
    ],
  },
  computacao_cientifica: {
    label: 'Computação científica',
    fundamentals: [
      'Python científico (NumPy, Matplotlib)',
      'Erro numérico e estabilidade',
      'Álgebra linear computacional',
      'Interpolação e integração',
      'Visualização de dados',
    ],
    intermediate: [
      'Métodos numéricos para EDOs/EDPs',
      'Monte Carlo',
      'Otimização numérica',
      'Paralelismo introdutório',
      'Validação e verificação de código',
    ],
    advanced: [
      'HPC e profiling',
      'Métodos multigrid / elementos finitos intro',
      'Simulação estocástica avançada',
      'C++ para núcleos críticos',
      'Reprodutibilidade computacional',
    ],
    books: [
      'Hill — Learning Scientific Programming with Python',
      'Press et al. — Numerical Recipes (referência)',
      'LeVeque — Finite Difference Methods',
    ],
    practicalProjects: [
      'Integrador numérico para EDO',
      'Simulação Monte Carlo básica',
      'Comparativo de métodos de integração',
      'Análise de sensibilidade paramétrica',
    ],
    researchIdeas: [
      'Benchmark de métodos para problema físico real',
      'Estudo de convergência em malha',
      'Pipeline reprodutível com versionamento',
    ],
    professorQuestions: [
      'Qual método numérico faz sentido para esse problema?',
      'Monte Carlo seria adequado?',
      'Como validar uma simulação simples?',
    ],
  },
  defesa: {
    label: 'Defesa / estratégico',
    fundamentals: [
      'Cadeias de suprimento de defesa',
      'Tecnologias dual-use',
      'Política de defesa e soberania',
      'Cibersegurança estratégica',
      'Organismos e programas (NATO, DARPA, etc.)',
    ],
    intermediate: [
      'Sistemas de armas e plataformas',
      'Inteligência técnica (OSINT)',
      'Espaço e defesa espacial',
      'Energia e segurança energética',
      'Export controls e compliance',
    ],
    advanced: [
      'Análise de capacidades nacionais',
      'Roadmaps tecnológicos de defesa',
      'Simulação de cenários (war gaming leve)',
      'IA autônoma e ética militar',
      'Resiliência de infraestrutura crítica',
    ],
    books: [
      'Technology and National Security (referências abertas)',
      'Relatórios SIPRI / IISS (referência)',
    ],
    practicalProjects: [
      'Mapa de atores e programas por país',
      'Linha do tempo de um programa de defesa',
      'Matriz tecnologia × aplicação militar',
    ],
    researchIdeas: [
      'Observatório de tecnologias emergentes em defesa',
      'Análise comparativa de investimentos em P&D',
    ],
    professorQuestions: [
      'Quais fontes abertas são aceitáveis para revisão?',
      'Como estruturar um observatório tecnológico?',
      'Quais riscos éticos considerar em IA de defesa?',
    ],
  },
  energia: {
    label: 'Energia',
    fundamentals: [
      'Matriz energética e balanço',
      'Termodinâmica aplicada à energia',
      'Fontes renováveis e fósseis',
      'Armazenamento e conversão',
      'Eficiência energética',
    ],
    intermediate: [
      'Sistemas nucleares e renováveis integrados',
      'Redes elétricas e smart grid',
      'Hidrogênio e combustíveis alternativos',
      'Análise de ciclo de vida (LCA intro)',
      'Política energética',
    ],
    advanced: [
      'Modelagem de transição energética',
      'Termo-hidráulica em usinas',
      'Materiais para baterias e supercapacitores',
      'Fusão energética (conceitos)',
      'Otimização de mix energético',
    ],
    books: [
      'Boyle — Renewable Energy',
      'IEA World Energy Outlook (referência)',
      'Turcotte — Geodynamics (geotermia)',
    ],
    practicalProjects: [
      'Balanço energético regional',
      'Comparativo de fontes com dados abertos',
      'Modelo de decaimento + calor em sistema nuclear',
    ],
    researchIdeas: [
      'Cenários de descarbonização regional',
      'Integração nuclear-renovável em simulação',
    ],
    professorQuestions: [
      'Como quantificar incertezas no mix energético?',
      'Quais dados públicos usar para LCA simplificado?',
    ],
  },
  quantica: {
    label: 'Quântica',
    fundamentals: [
      'Superposição e medida',
      'Operadores e observáveis',
      'Emaranhamento',
      'Qubits e portas lógicas',
      'Algoritmos de Deutsch e Grover (conceito)',
    ],
    intermediate: [
      'Circuitos quânticos',
      'Ruído e decoerência',
      'Codificação quântica de erros (intro)',
      'Simulação quântica de moléculas (conceito)',
      'Hardware NISQ',
    ],
    advanced: [
      'Algoritmos de Shor e otimização quântica',
      'Qiskit/Cirq em profundidade',
      'Informação quântica',
      'Física de dispositivos supercondutores',
      'Quântica para materiais',
    ],
    books: [
      'Nielsen & Chuang — Quantum Computation and Quantum Information',
      'Griffiths — Quantum Mechanics',
    ],
    practicalProjects: [
      'Simulador de porta Hadamard e CNOT',
      'Visualização de estados em esfera de Bloch',
      'Resumo crítico de notícias quânticas',
    ],
    researchIdeas: [
      'Comparativo de backends quânticos em problema toy',
      'Revisão de aplicações em química quântica',
    ],
    professorQuestions: [
      'Qual simulador usar para nível de graduação?',
      'Como interpretar resultados com ruído NISQ?',
    ],
  },
  espaco: {
    label: 'Espaço',
    fundamentals: [
      'Leis de Kepler e órbitas',
      'Ambiente espacial (vácuo, radiação)',
      'Satélites e payloads',
      'Propulsão química e elétrica',
      'Missões robóticas e tripuladas',
    ],
    intermediate: [
      'Mecânica orbital (manobras)',
      'Materiais para espaço',
      'Telemetria e comunicações',
      'Lançadores e cadeia de valor',
      'Defesa espacial (conceitos)',
    ],
    advanced: [
      'Astrodinâmica perturbada',
      'Missões interplanetárias',
      'Sistemas de suporte de vida',
      'Propulsão avançada',
      'Observação da Terra e dados',
    ],
    books: [
      'Curtis — Orbital Mechanics',
      'Wertz — Space Mission Engineering',
      'NASA/ESA materiais educacionais',
    ],
    practicalProjects: [
      'Cálculo de órbita circular em Python',
      'Catálogo de missões recentes',
      'Δv simplificado para transferência',
    ],
    researchIdeas: [
      'Análise de debris orbitais',
      'Comparativo de constelações LEO',
    ],
    professorQuestions: [
      'Quais simplificações são válidas em mecânica orbital?',
      'Como conectar defesa espacial com materiais?',
    ],
  },
  ia_cientifica: {
    label: 'IA científica',
    fundamentals: [
      'Python para dados científicos',
      'Regressão e classificação',
      'Validação cruzada e métricas',
      'Ética e viés em IA',
      'Visualização de resultados',
    ],
    intermediate: [
      'Redes neurais para séries e imagens',
      'Transfer learning',
      'Interpretabilidade (SHAP, LIME intro)',
      'Pipelines com scikit-learn / PyTorch leve',
      'Dados rotulados em domínio científico',
    ],
    advanced: [
      'Modelos fundacionais em ciência',
      'Simulação assistida por ML',
      'Active learning em experimentos',
      'Reprodutibilidade e versionamento de modelos',
      'IA em instrumentação autônoma',
    ],
    books: [
      'Goodfellow — Deep Learning (capítulos intro)',
      'Géron — Hands-On Machine Learning',
      'Raschka — Machine Learning with PyTorch',
    ],
    practicalProjects: [
      'Classificador de abstracts científicos',
      'Detecção de anomalias em série temporal',
      'Fine-tuning em dataset pequeno',
    ],
    researchIdeas: [
      'Benchmark de modelos em dataset aberto de física',
      'IA + simulação: surrogate model simples',
    ],
    professorQuestions: [
      'Como evitar overfitting com poucos dados experimentais?',
      'Quais métricas são adequadas para o domínio?',
      'Como documentar reprodutibilidade do modelo?',
    ],
  },
};

export const SCIENTIFIC_STUDY_CATALOG = {
  ...STUDY_CATALOG_CORE,
  ...STUDY_CATALOG_PHASE_2B,
};
