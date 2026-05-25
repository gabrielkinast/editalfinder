import { resolveCanonicalInterest } from './scientificInterestAliases';

/**
 * Catálogo de livros por área e nível (Fase 2G + 2H).
 * level: base | introductory | intermediate | advanced | computational | referencia
 * @typedef {{ title: string, author: string, level: string, area: string, why: string, useFor: string, prerequisites?: string[] }} ScientificBook
 */

export const SCIENTIFIC_BOOK_CATALOG = [
  { title: 'Introductory Nuclear Physics', author: 'Krane', level: 'introductory', area: 'nuclear', why: 'Base clara de física nuclear para graduação.', useFor: 'Fundamentos e primeiros projetos' },
  { title: 'Nuclear Physics: Principles and Applications', author: 'Lilley', level: 'introductory', area: 'nuclear', why: 'Liga teoria nuclear a aplicações.', useFor: 'Fundamentos e aplicações' },
  { title: 'Radiation Detection and Measurement', author: 'Knoll', level: 'intermediate', area: 'nuclear', why: 'Referência em detecção e instrumentação.', useFor: 'Projetos intermediários e IC' },
  { title: 'Introduction to Nuclear Engineering', author: 'Lamarsh', level: 'intermediate', area: 'engenharia_nuclear', why: 'Ponte engenharia-sistemas nucleares.', useFor: 'Engenharia nuclear aplicada' },
  { title: 'Nuclear Reactor Analysis', author: 'Duderstadt & Hamilton', level: 'advanced', area: 'nuclear', why: 'Transporte e análise de reatores.', useFor: 'Avançado e mestrado' },
  { title: 'Nuclear Reactor Physics', author: 'Stacey', level: 'advanced', area: 'engenharia_nuclear', why: 'Física de reatores em profundidade.', useFor: 'Pós-graduação' },
  { title: 'Physical Chemistry', author: 'Atkins', level: 'introductory', area: 'fisico_quimica', why: 'Referência clássica de físico-química.', useFor: 'Fundamentos' },
  { title: 'Physical Chemistry', author: 'McQuarrie & Simon', level: 'introductory', area: 'fisico_quimica', why: 'Abordagem matemática acessível.', useFor: 'Fundamentos e exercícios', prerequisites: ['Cálculo', 'Química geral'] },
  { title: 'Statistical Mechanics', author: 'McQuarrie', level: 'intermediate', area: 'fisico_quimica', why: 'Estatística para equilíbrio e ensembles.', useFor: 'Intermediário' },
  { title: 'Quantum Chemistry', author: 'Levine', level: 'intermediate', area: 'fisico_quimica', why: 'Química quântica molecular.', useFor: 'Avançado graduação' },
  { title: 'Understanding Molecular Simulation', author: 'Frenkel & Smit', level: 'introductory', area: 'dinamica_molecular', why: 'MD e MC em linguagem didática.', useFor: 'Primeiros projetos de simulação' },
  { title: 'Computer Simulation of Liquids', author: 'Allen & Tildesley', level: 'intermediate', area: 'dinamica_molecular', why: 'Algoritmos clássicos de MD.', useFor: 'Intermediário e avançado' },
  { title: 'The Art of Molecular Dynamics Simulation', author: 'Rapaport', level: 'intermediate', area: 'dinamica_molecular', why: 'Implementação de MD.', useFor: 'Projetos computacionais' },
  { title: 'Molecular Modelling', author: 'Leach', level: 'advanced', area: 'dinamica_molecular', why: 'Modelagem aplicada.', useFor: 'IC/TCC e mestrado' },
  { title: 'Computational Physics', author: 'Newman', level: 'introductory', area: 'computacao_cientifica', why: 'Problemas numéricos com Python.', useFor: 'Básico computacional' },
  { title: 'Computational Physics', author: 'Landau, Páez & Bordeianu', level: 'introductory', area: 'computacao_cientifica', why: 'Ampla cobertura de métodos.', useFor: 'Fundamentos numéricos' },
  { title: 'Numerical Recipes', author: 'Press et al.', level: 'intermediate', area: 'computacao_cientifica', why: 'Receitas numéricas consolidadas.', useFor: 'Implementação de métodos' },
  { title: 'Scientific Computing', author: 'Heath', level: 'intermediate', area: 'computacao_cientifica', why: 'Métodos e análise de erro.', useFor: 'Graduação avançada' },
  { title: 'Finite Difference Methods', author: 'LeVeque', level: 'advanced', area: 'computacao_cientifica', why: 'EDPs e implementação.', useFor: 'Mestrado' },
  { title: 'Materials Science and Engineering', author: 'Callister', level: 'introductory', area: 'materiais', why: 'Introdução a estrutura e propriedades.', useFor: 'Fundamentos de materiais' },
  { title: 'The Science and Engineering of Materials', author: 'Askeland', level: 'introductory', area: 'materiais', why: 'Processamento e propriedades.', useFor: 'Base graduação' },
  { title: 'Materials Selection in Mechanical Design', author: 'Ashby', level: 'intermediate', area: 'materiais', why: 'Seleção sistemática de materiais.', useFor: 'Projetos de engenharia' },
  { title: 'Phase Transformations in Metals and Alloys', author: 'Porter & Easterling', level: 'intermediate', area: 'materiais', why: 'Transformações de fase.', useFor: 'Intermediário' },
  { title: 'Introduction to Quantum Mechanics', author: 'Griffiths', level: 'introductory', area: 'fisico_quimica', why: 'Base quântica para química e física.', useFor: 'Pré-requisito teórico' },
  { title: 'Classical Electrodynamics', author: 'Jackson', level: 'advanced', area: 'fisico_quimica', why: 'Eletromagnetismo rigoroso.', useFor: 'Avançado' },
  { title: 'Electronic Structure of Materials', author: 'Sutton', level: 'advanced', area: 'materiais', why: 'Ligação eletrônica e materiais.', useFor: 'Pesquisa em materiais' },
  { title: 'Nuclear Engineering', author: 'Zohuri', level: 'intermediate', area: 'engenharia_nuclear', why: 'Visão de sistemas e aplicações.', useFor: 'Engenharia aplicada' },
  { title: 'Introduction to Plasma Physics', author: 'Chen', level: 'introductory', area: 'plasmas_fusao', why: 'Base de plasmas e fusão.', useFor: 'Fundamentos de plasmas' },
  { title: 'Plasma Physics and Fusion Energy', author: 'Freidberg', level: 'intermediate', area: 'plasmas_fusao', why: 'Fusão com enfoque de engenharia.', useFor: 'Intermediário fusão' },
  { title: 'Tokamaks', author: 'Wesson', level: 'referencia', area: 'plasmas_fusao', why: 'Referência em confinamento magnético.', useFor: 'Pesquisa em fusão' },
  { title: 'Introduction to Flight', author: 'Anderson', level: 'introductory', area: 'engenharia_aeroespacial', why: 'Fundamentos aeroespaciais.', useFor: 'Básico aeroespacial' },
  { title: 'Fundamentals of Aerodynamics', author: 'Anderson', level: 'intermediate', area: 'engenharia_aeroespacial', why: 'Aerodinâmica para projetos.', useFor: 'CFD e projeto' },
  { title: 'Orbital Mechanics for Engineering Students', author: 'Curtis', level: 'introductory', area: 'espaco', why: 'Mecânica orbital.', useFor: 'Projetos espaciais' },
  { title: 'Hands-On Machine Learning', author: 'Géron', level: 'introductory', area: 'ia_cientifica', why: 'ML prático com sklearn/TF.', useFor: 'Primeiros projetos de IA' },
  { title: 'Deep Learning', author: 'Goodfellow', level: 'advanced', area: 'ia_cientifica', why: 'Fundamentos de redes profundas.', useFor: 'Avançado e pesquisa' },
  { title: 'Radiochemistry and Nuclear Chemistry', author: 'Choppin', level: 'introductory', area: 'quimica_nuclear', why: 'Base de radioquímica.', useFor: 'Química nuclear' },
  { title: 'Simulation and the Monte Carlo Method', author: 'Rubinstein', level: 'introductory', area: 'monte_carlo', why: 'MC estatístico geral.', useFor: 'Fundamentos MC' },
  { title: 'Computational Methods of Neutron Transport', author: 'Lewis & Miller', level: 'advanced', area: 'monte_carlo', why: 'Transporte de nêutrons.', useFor: 'Avançado nuclear' },
  { title: 'Handbook of Modern Sensors', author: 'Fraden', level: 'introductory', area: 'instrumentacao', why: 'Panorama de sensores.', useFor: 'Instrumentação básica' },
  { title: 'Introduction to Radiation Protection', author: 'Martin', level: 'advanced', area: 'protecao_radiologica', why: 'Proteção radiológica aplicada.', useFor: 'Avançado' },
  { title: 'Physical Chemistry', author: 'Engel & Reid', level: 'introductory', area: 'fisico_quimica', why: 'Abordagem visual e moderna.', useFor: 'Graduação' },
  { title: 'Statistical Mechanics', author: 'McQuarrie', level: 'intermediate', area: 'fisico_quimica', why: 'Ponte para termodinâmica estatística.', useFor: 'Intermediário' },
  { title: 'Introduction to Quantum Mechanics', author: 'Griffiths', level: 'introductory', area: 'quantica', why: 'Base padrão de MQ.', useFor: 'Fundamentos' },
  { title: 'Modern Quantum Mechanics', author: 'Sakurai', level: 'intermediate', area: 'quantica', why: 'Formalismo avançado.', useFor: 'Graduação final / IC' },
  { title: 'Nuclear Reactor Engineering', author: 'Glasstone & Sesonske', level: 'intermediate', area: 'engenharia_nuclear', why: 'Engenharia de sistemas.', useFor: 'Engenharia nuclear' },
  { title: 'Radiation Shielding', author: 'Shultis & Faw', level: 'advanced', area: 'engenharia_nuclear', why: 'Blindagem de instalações.', useFor: 'Avançado' },
  { title: 'Radiochemistry and Nuclear Chemistry', author: 'Choppin, Liljenzin & Rydberg', level: 'introductory', area: 'quimica_nuclear', why: 'Referência de radioquímica.', useFor: 'Base' },
  { title: 'Nuclear and Radiochemistry', author: 'Friedlander et al.', level: 'intermediate', area: 'quimica_nuclear', why: 'Aplicações e métodos.', useFor: 'Intermediário' },
  { title: 'Introduction to Plasma Physics and Controlled Fusion', author: 'Chen', level: 'introductory', area: 'plasmas_fusao', why: 'Plasmas e fusão unificados.', useFor: 'Fundamentos' },
  { title: 'Tokamaks', author: 'Wesson', level: 'referencia', area: 'plasmas_fusao', why: 'Referência em tokamak.', useFor: 'Pesquisa fusão' },
  { title: 'Fundamentals of Plasma Physics', author: 'Bellan', level: 'advanced', area: 'plasmas_fusao', why: 'Fundamentos rigorosos.', useFor: 'Avançado' },
  { title: 'The Art of Molecular Dynamics Simulation', author: 'Rapaport', level: 'intermediate', area: 'dinamica_molecular', why: 'Implementação de MD.', useFor: 'Projetos computacionais' },
  { title: 'Molecular Modelling', author: 'Leach', level: 'advanced', area: 'dinamica_molecular', why: 'Modelagem aplicada.', useFor: 'IC/TCC' },
  { title: 'Statistical Mechanics: Theory and Molecular Simulation', author: 'Tuckerman', level: 'advanced', area: 'dinamica_molecular', why: 'MD com base estatística.', useFor: 'Mestrado' },
  { title: 'Computational Science and Engineering', author: 'Strang', level: 'introductory', area: 'computacao_cientifica', why: 'Visão unificada de métodos.', useFor: 'Fundamentos' },
  { title: 'Finite Difference Methods for ODEs and PDEs', author: 'LeVeque', level: 'advanced', area: 'computacao_cientifica', why: 'EDPs com rigor.', useFor: 'Avançado e mestrado' },
  { title: 'Introduction to High Performance Computing for Scientists and Engineers', author: 'Hager & Wellein', level: 'introductory', area: 'hpc', why: 'HPC acessível.', useFor: 'Paralelismo intro' },
  { title: 'An Introduction to Parallel Programming', author: 'Pacheco', level: 'intermediate', area: 'hpc', why: 'MPI e OpenMP.', useFor: 'Intermediário HPC' },
  { title: 'Programming Massively Parallel Processors', author: 'Kirk & Hwu', level: 'advanced', area: 'hpc', why: 'GPU CUDA.', useFor: 'Avançado' },
  { title: 'Using MPI', author: 'Gropp et al.', level: 'computational', area: 'hpc', why: 'Referência MPI.', useFor: 'Projetos em cluster' },
  { title: 'Parallel Programming in OpenMP', author: 'Chandra et al.', level: 'computational', area: 'hpc', why: 'OpenMP prático.', useFor: 'Paralelismo shared-memory' },
  { title: 'Monte Carlo Statistical Methods', author: 'Robert & Casella', level: 'intermediate', area: 'monte_carlo', why: 'MC estatístico rigoroso.', useFor: 'Intermediário' },
  { title: 'Monte Carlo Methods', author: 'Kalos & Whitlock', level: 'introductory', area: 'monte_carlo', why: 'MC físico e numérico.', useFor: 'Fundamentos' },
  { title: 'Monte Carlo Methods in Statistical Physics', author: 'Newman & Barkema', level: 'intermediate', area: 'monte_carlo', why: 'MC em física estatística.', useFor: 'Intermediário' },
  { title: 'Pattern Recognition and Machine Learning', author: 'Bishop', level: 'introductory', area: 'ia_cientifica', why: 'Base teórica de ML.', useFor: 'Fundamentos IA' },
  { title: 'Machine Learning: A Probabilistic Perspective', author: 'Murphy', level: 'intermediate', area: 'ia_cientifica', why: 'ML probabilístico.', useFor: 'Intermediário' },
  { title: 'Data-Driven Science and Engineering', author: 'Brunton & Kutz', level: 'computational', area: 'ia_cientifica', why: 'ML + dinâmica e PDEs.', useFor: 'IA científica' },
  { title: 'Mathematics for Machine Learning', author: 'Deisenroth et al.', level: 'introductory', area: 'ia_cientifica', why: 'Matemática para ML.', useFor: 'Pré-requisitos' },
  { title: 'Python for Data Analysis', author: 'McKinney', level: 'introductory', area: 'ciencia_dados', why: 'pandas e workflow.', useFor: 'Fundamentos dados' },
  { title: 'Python Data Science Handbook', author: 'VanderPlas', level: 'introductory', area: 'ciencia_dados', why: 'Stack Python de dados.', useFor: 'Exploração e visualização' },
  { title: 'The Elements of Statistical Learning', author: 'Hastie, Tibshirani & Friedman', level: 'advanced', area: 'ciencia_dados', why: 'Estatística preditiva avançada.', useFor: 'Avançado' },
  { title: 'Bayesian Data Analysis', author: 'Gelman et al.', level: 'advanced', area: 'ciencia_dados', why: 'Inferência bayesiana.', useFor: 'Mestrado' },
  { title: 'Probabilistic Robotics', author: 'Thrun, Burgard & Fox', level: 'intermediate', area: 'sistemas_autonomos', why: 'SLAM e navegação.', useFor: 'Autonomia' },
  { title: 'Planning Algorithms', author: 'LaValle', level: 'intermediate', area: 'sistemas_autonomos', why: 'Planejamento de movimento.', useFor: 'Intermediário' },
  { title: 'Artificial Intelligence: A Modern Approach', author: 'Russell & Norvig', level: 'introductory', area: 'sistemas_autonomos', why: 'Agentes e decisão.', useFor: 'Base autonomia' },
  { title: 'Robotics: Modelling, Planning and Control', author: 'Siciliano et al.', level: 'intermediate', area: 'robotica', why: 'Robótica clássica.', useFor: 'Manipulação e controle' },
  { title: 'Robotics, Vision and Control', author: 'Corke', level: 'introductory', area: 'robotica', why: 'Visão + controle em MATLAB/Python.', useFor: 'Projetos práticos' },
  { title: 'Robot Modeling and Control', author: 'Spong, Hutchinson & Vidyasagar', level: 'advanced', area: 'robotica', why: 'Dinâmica e controle avançado.', useFor: 'Mestrado' },
  { title: 'Diffusion in Solids', author: 'Shewmon', level: 'intermediate', area: 'materiais', why: 'Difusão em sólidos.', useFor: 'Intermediário materiais' },
  { title: 'Electronic Structure of Materials', author: 'Sutton', level: 'advanced', area: 'materiais', why: 'Estrutura eletrônica.', useFor: 'Avançado' },
  { title: 'Electronic Structure', author: 'Martin', level: 'advanced', area: 'materiais', why: 'Teoria eletrônica rigorosa.', useFor: 'Mestrado' },
  { title: 'Molecular Dynamics Simulation', author: 'Haile', level: 'computational', area: 'materiais', why: 'MD para materiais.', useFor: 'Simulação' },
  { title: 'Sustainable Energy Without the Hot Air', author: 'MacKay', level: 'introductory', area: 'energia', why: 'Visão quantitativa de energia.', useFor: 'Fundamentos' },
  { title: 'Thermodynamics: An Engineering Approach', author: 'Çengel & Boles', level: 'introductory', area: 'energia', why: 'Termodinâmica aplicada.', useFor: 'Ciclos e balanços' },
  { title: 'Fundamentals of Engineering Thermodynamics', author: 'Moran & Shapiro', level: 'intermediate', area: 'energia', why: 'Engenharia termodinâmica.', useFor: 'Intermediário' },
  { title: 'Fundamentals of Heat and Mass Transfer', author: 'Incropera', level: 'intermediate', area: 'energia', why: 'Transferência de calor.', useFor: 'Sistemas térmicos' },
  { title: 'Sustainable Energy', author: 'Tester et al.', level: 'intermediate', area: 'energia', why: 'Renováveis e nuclear.', useFor: 'Matriz energética' },
  { title: 'Fundamentals of Power System Economics', author: 'Kirschen & Strbac', level: 'advanced', area: 'energia', why: 'Economia de sistemas elétricos.', useFor: 'Avançado' },
  { title: 'An Introduction to Error Analysis', author: 'Taylor', level: 'introductory', area: 'engenharia_fisica', why: 'Incerteza em medidas.', useFor: 'Laboratório' },
  { title: 'Data Reduction and Error Analysis', author: 'Bevington', level: 'intermediate', area: 'engenharia_fisica', why: 'Tratamento de dados experimentais.', useFor: 'IC experimental' },
  { title: 'The Art of Electronics', author: 'Horowitz & Hill', level: 'intermediate', area: 'engenharia_fisica', why: 'Eletrônica para instrumentação.', useFor: 'Sensores e circuitos' },
  { title: 'Instrumentation for Engineering Measurements', author: 'Dally, Riley & McConnell', level: 'intermediate', area: 'engenharia_fisica', why: 'Medidas de engenharia.', useFor: 'Projetos experimentais' },
  { title: 'Fundamentals of Photonics', author: 'Saleh & Teich', level: 'advanced', area: 'engenharia_fisica', why: 'Óptica aplicada.', useFor: 'Avançado' },
  { title: 'Measurement, Instrumentation, and Sensors Handbook', author: 'Webster', level: 'intermediate', area: 'instrumentacao', why: 'Referência de sensores.', useFor: 'Instrumentação' },
  { title: 'Lehninger Principles of Biochemistry', author: 'Nelson & Cox', level: 'introductory', area: 'biotecnologia', why: 'Bioquímica fundamental.', useFor: 'Base biotech' },
  { title: 'Molecular Biology of the Cell', author: 'Alberts', level: 'introductory', area: 'biotecnologia', why: 'Biologia celular.', useFor: 'Fundamentos' },
  { title: 'Bioprocess Engineering', author: 'Shuler & Kargi', level: 'intermediate', area: 'biotecnologia', why: 'Engenharia de bioprocessos.', useFor: 'Fermentação e biorreatores' },
  { title: 'Bioprocess Engineering Principles', author: 'Doran', level: 'intermediate', area: 'biotecnologia', why: 'Princípios de bioprocessos.', useFor: 'Intermediário' },
  { title: 'Principles of Gene Manipulation and Genomics', author: 'Primrose & Twyman', level: 'advanced', area: 'biotecnologia', why: 'Engenharia genética.', useFor: 'Avançado e IC' },
  { title: 'Systems Engineering and Analysis', author: 'Blanchard & Fabrycky', level: 'introductory', area: 'engenharia_defesa', why: 'Engenharia de sistemas.', useFor: 'Defesa e integração' },
  { title: 'Systems Engineering Principles and Practice', author: 'Kossiakoff et al.', level: 'intermediate', area: 'engenharia_defesa', why: 'SE aplicada.', useFor: 'Intermediário' },
  { title: 'Introduction to Radar Systems', author: 'Skolnik', level: 'introductory', area: 'engenharia_defesa', why: 'Radar fundamental.', useFor: 'Sensores defesa' },
  { title: 'Estimation with Applications to Tracking and Navigation', author: 'Bar-Shalom et al.', level: 'intermediate', area: 'engenharia_defesa', why: 'Fusão e rastreamento.', useFor: 'Avançado' },
  { title: 'Handbook of Systems Engineering and Management', author: 'Sage & Rouse', level: 'advanced', area: 'engenharia_defesa', why: 'Gestão de sistemas complexos.', useFor: 'Mestrado' },
  { title: 'Space Mission Analysis and Design', author: 'Wertz & Larson', level: 'intermediate', area: 'espaco', why: 'Projeto de missão espacial.', useFor: 'IC espacial' },
  { title: 'Spacecraft Systems Engineering', author: 'Fortescue, Swinerd & Stark', level: 'intermediate', area: 'espaco', why: 'Subsistemas de satélite.', useFor: 'CubeSat' },
  { title: 'Fundamentals of Astrodynamics and Applications', author: 'Vallado', level: 'advanced', area: 'espaco', why: 'Astrodinâmica rigorosa.', useFor: 'Avançado' },
  { title: 'Modern Spacecraft Dynamics and Control', author: 'Kaplan', level: 'advanced', area: 'espaco', why: 'Atitude e controle orbital.', useFor: 'Mestrado' },
  { title: 'Rocket Propulsion Elements', author: 'Sutton & Biblarz', level: 'intermediate', area: 'engenharia_aeroespacial', why: 'Propulsão foguete.', useFor: 'Propulsão' },
  { title: 'Dynamics of Flight', author: 'Etkin & Reid', level: 'intermediate', area: 'engenharia_aeroespacial', why: 'Dinâmica de voo.', useFor: 'Estabilidade e controle' },
  { title: 'Aircraft Structures for Engineering Students', author: 'Megson', level: 'intermediate', area: 'engenharia_aeroespacial', why: 'Estruturas.', useFor: 'Projeto estrutural' },
  { title: 'Aerodynamics for Engineers', author: 'Bertin & Cummings', level: 'advanced', area: 'engenharia_aeroespacial', why: 'Aerodinâmica avançada.', useFor: 'CFD e projeto' },
  { title: 'Mission Economy', author: 'Mazzucato', level: 'introductory', area: 'tecnologias_estrategicas', why: 'Inovação orientada por missão.', useFor: 'Política e estratégia' },
  { title: 'Managing Innovation', author: 'Tidd & Bessant', level: 'introductory', area: 'tecnologias_estrategicas', why: 'Gestão da inovação.', useFor: 'TRL e roadmap' },
  { title: 'Competitive Advantage of Nations', author: 'Porter', level: 'intermediate', area: 'tecnologias_estrategicas', why: 'Clusters e competitividade.', useFor: 'Análise setorial' },
  { title: 'The Economics of Industrial Innovation', author: 'Freeman & Soete', level: 'intermediate', area: 'tecnologias_estrategicas', why: 'Economia da inovação.', useFor: 'Intermediário' },
  { title: 'Science, Technology and Innovation Outlook', author: 'OECD', level: 'referencia', area: 'tecnologias_estrategicas', why: 'Referência internacional.', useFor: 'Observatórios' },
  { title: 'Physics in Nuclear Medicine', author: 'Cherry, Sorenson & Phelps', level: 'intermediate', area: 'medicina_nuclear', why: 'Referência de física em medicina nuclear.', useFor: 'Intermediário e IC' },
  { title: 'Fundamentals of Nuclear Pharmacy', author: 'Saha', level: 'introductory', area: 'medicina_nuclear', why: 'Radiofármacos e farmácia nuclear.', useFor: 'Fundamentos' },
  { title: 'Essentials of Nuclear Medicine Imaging', author: 'Mettler & Guiberteau', level: 'introductory', area: 'medicina_nuclear', why: 'Imagem clínica.', useFor: 'Base clínica' },
  { title: 'Nuclear Medicine Physics', author: 'Bailey et al.', level: 'intermediate', area: 'medicina_nuclear', why: 'Física de equipamentos.', useFor: 'Avançado graduação' },
  { title: 'Nuclear Medicine Physics: A Handbook for Teachers and Students', author: 'IAEA', level: 'referencia', area: 'medicina_nuclear', why: 'Material didático IAEA.', useFor: 'Referência' },
  { title: 'Introduction to Radiological Physics and Radiation Dosimetry', author: 'Attix', level: 'introductory', area: 'dosimetria', why: 'Base dosimétrica rigorosa.', useFor: 'Fundamentos' },
  { title: 'Radiation Physics for Medical Physicists', author: 'Podgorsak', level: 'intermediate', area: 'dosimetria', why: 'Física médica.', useFor: 'Intermediário' },
  { title: 'The Physics of Radiation Therapy', author: 'Khan', level: 'intermediate', area: 'dosimetria', why: 'Dosimetria em radioterapia.', useFor: 'Terapia' },
  { title: 'Radiation Detection and Measurement', author: 'Knoll', level: 'introductory', area: 'dosimetria', why: 'Detecção e medida.', useFor: 'Instrumentação e dose' },
  { title: 'Introduction to Health Physics', author: 'Cember & Johnson', level: 'introductory', area: 'protecao_radiologica', why: 'Saúde física e proteção.', useFor: 'Fundamentos' },
  { title: 'Atoms, Radiation, and Radiation Protection', author: 'Turner', level: 'introductory', area: 'protecao_radiologica', why: 'Proteção e física.', useFor: 'Base' },
  { title: 'Radiation Protection and Safety of Radiation Sources', author: 'IAEA', level: 'referencia', area: 'protecao_radiologica', why: 'Normas e princípios IAEA.', useFor: 'Regulamentação' },
  { title: 'Radiation Shielding', author: 'Shultis & Faw', level: 'intermediate', area: 'protecao_radiologica', why: 'Blindagem de instalações.', useFor: 'Projetos de proteção' },
];

const LEVEL_ORDER = { introductory: 1, intermediate: 2, advanced: 3, computational: 4 };

/**
 * @param {string} areaKey — chave do catálogo profundo
 * @returns {ScientificBook[]}
 */
export function getBooksForArea(areaKey) {
  if (!areaKey) return [];
  const canonical = resolveCanonicalInterest(areaKey);
  return SCIENTIFIC_BOOK_CATALOG.filter((b) => b.area === canonical || b.area === areaKey).sort(
    (a, b) => (LEVEL_ORDER[a.level] || 9) - (LEVEL_ORDER[b.level] || 9),
  );
}

/**
 * @param {string[]} interestIds
 */
export function getBooksForInterests(interestIds = []) {
  const keys = new Set();
  for (const id of interestIds) {
    keys.add(resolveCanonicalInterest(id));
  }
  const out = [];
  const seen = new Set();
  for (const key of keys) {
    for (const book of getBooksForArea(key)) {
      const sig = `${book.author}|${book.title}`;
      if (seen.has(sig)) continue;
      seen.add(sig);
      out.push(book);
    }
  }
  return out;
}
