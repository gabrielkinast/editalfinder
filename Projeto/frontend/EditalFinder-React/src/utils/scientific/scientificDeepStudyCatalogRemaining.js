import { defineDeepArea } from './deepStudyCatalogHelpers';

/** Áreas canônicas adicionais — Fase 2H (conteúdo base + padding automático aos mínimos) */
export const REMAINING_DEEP_CATALOG_ENTRIES = {
  engenharia_nuclear: defineDeepArea({
    label: 'Engenharia nuclear',
    aliases: ['engenharia_nuclear'],
    formationGoal: 'Sistemas de potência e pesquisa → IC em termo-hidráulica → mestrado em acoplamentos.',
    prerequisites: {
      math: ['Cálculo', 'EDPs', 'Álgebra linear', 'Métodos numéricos'],
      physics: ['Termodinâmica', 'Mecânica dos fluidos', 'Transferência de calor', 'Física nuclear intro'],
      chemistry: ['Química do combustível'],
      computation: ['Python', 'CFD intro', 'Códigos de sistema'],
    },
    theory: {
      foundations: ['Balanco de energia', 'Ciclo do combustível', 'Barreiras de segurança', 'Crítica', 'Resfriamento', 'Contenção', 'Regulação', 'Acidentes históricos', 'Radioatividade aplicada', 'Projeto conceitual'],
      intermediate: ['Termo-hidráulica de canais', 'Sistemas de injeção', 'Resíduos', 'Materiais estruturais', 'Instrumentação de planta', 'Licenciamento', 'Dinâmica de barras', 'Queima simplificada', 'Trocadores', 'Simulação de transientes'],
      advanced: ['Acoplamento neutrônica-TH', 'Dinâmica de reatores', 'CFD de subcanais', 'Materiais em serviço', 'Análise de acidentes', 'SMR', 'Digital twin', 'Códigos RELAP-like', 'Otimização de combustível', 'Segurança probabilística'],
      researchLevel: ['IV geração', 'Fusão como sistema', 'Incerteza em códigos', 'Validação integral', 'Queima avançada', 'Corrosão em primário', 'Automação de planta', 'Gestão de envelhecimento', 'Hibridação nuclear-renovável', 'Internacionalização de projetos'],
    },
    books: {
      introductory: ['Lamarsh — Introduction to Nuclear Engineering'],
      intermediate: ['Stacey — Nuclear Reactor Physics', 'Todreas — Nuclear Systems'],
      advanced: ['Duderstadt & Hamilton — Nuclear Reactor Analysis'],
      computational: ['RELAP documentation', 'OpenMC tutorials'],
    },
    projectTracks: {
      basic: ['Balanco energético simplificado', 'Reatividade de grupo único', 'Curva de resfriamento'],
      intermediate: ['Canal 1D', 'Transiente de barras', 'Comparativo combustíveis'],
      advanced: ['Acoplamento lumped', 'Otimização de reflector', 'CFD subcanal intro'],
      ictcc: ['Vaso de pressão — materiais', 'Reator de pesquisa', 'Licenciamento case study'],
      masters: ['Digital twin de loop', 'UQ em código de sistema', 'SMR conceitual'],
    },
  }),

  quimica_nuclear: defineDeepArea({
    label: 'Química nuclear / radioquímica',
    aliases: ['quimica_nuclear', 'radioquimica'],
    prerequisites: {
      math: ['Cálculo', 'Probabilidade', 'Estatística de contagem'],
      physics: ['Física moderna', 'Radiação'],
      chemistry: ['Química geral', 'Inorgânica', 'Equilíbrio', 'Eletroquímica'],
      computation: ['Python', 'Espectroscopia numérica'],
    },
    theory: {
      foundations: ['Isótopos', 'Cadeias de decaimento', 'Separação isotópica', 'Química de actinídeos', 'Espectrometria alfa/beta/gama', 'Extração', 'Purificação', 'Gestão de rejeitos', 'Química de urânio', 'Segurança em laboratório'],
      intermediate: ['Radiofármacos', 'Cromatografia', 'Solventes', 'Especiação', 'Corrosão radiolítica', 'Produção de fontes', 'Análise radiométrica', 'Transporte aquático', 'Quimioterapia nuclear', 'Normas IAEA'],
      advanced: ['Fase gasosa', 'Actinídeos em água', 'Nanomarcadores', 'Processos de reprocessamento', 'Incerteza analítica', 'Automação de linha', 'Forense nuclear', 'Ciclo fechado', 'Química sob irradiação', 'Escalas de planta piloto'],
      researchLevel: ['Medicina nuclear avançada', 'Actinídeos minoritários', 'Análise forense', 'Interface sólido-líquido', 'Radioquímica ambiental', 'Sensoriamento', 'Green chemistry nuclear', 'Dados abertos nucleares', 'Segurança de rejeitos geológicos', 'Publicação em radioanálise'],
    },
    books: {
      introductory: ['Choppin — Radiochemistry and Nuclear Chemistry'],
      intermediate: ['Wilson — Radiochemistry'],
      advanced: ['Katz — Chemistry of the Actinide Elements'],
      computational: ['GammaVision / Python espectroscopia'],
    },
    projectTracks: {
      basic: ['Cadeia de decaimento', 'Picos em espectro sintético', 'Atividade em equilíbrio'],
      intermediate: ['Extração L/L', 'Cinética de purificação', 'Transporte 1D em água'],
      advanced: ['Corrosão sob dose', 'Especiação computada', 'Rejeitos líquidos'],
      ictcc: ['Métodos analíticos comparados', 'Linha de produção didática', 'Validação IAEA'],
      masters: ['Actinídeos com dados abertos', 'Modelagem de rejeitos', 'Forense aplicada'],
    },
  }),

  monte_carlo: defineDeepArea({
    label: 'Monte Carlo',
    aliases: ['monte_carlo'],
    prerequisites: {
      math: ['Probabilidade', 'Estatística', 'Processos estocásticos', 'Geração de aleatórios'],
      physics: ['Interação partícula-matéria', 'Transporte'],
      chemistry: [],
      computation: ['Python', 'Paralelismo', 'Profiling'],
    },
    theory: {
      foundations: ['LLN', 'Inversão', 'Rejeição', 'Importance sampling', 'Erro estatístico', 'Sementes', 'Histórias independentes', 'Tallies', 'Geometria simples', 'Validação'],
      intermediate: ['Transporte de partículas', 'Seções de choque', 'Variância', 'Correlação', 'MCMC intro', 'Geometrias compostas', 'Fontes colimadas', 'Biasing', 'Parallelização de histórias', 'Comparação com determinístico'],
      advanced: ['MCMC avançado', 'GPU MC', 'Acoplamento híbrido', 'CAD import', 'Adjoint', 'Burnup acoplado', 'Incerteza em dados', 'Exa-scale', 'Visualização 3D de tallies', 'Verificação de código'],
      researchLevel: ['Alta energia', 'Bayesian MC', 'Dados nucleares UQ', 'OpenMC avançado', 'Geant4 custom', 'Multi-physics MC', 'ML para biasing', 'Digital twin estocástico', 'Publicação de benchmark', 'Reprodutibilidade HPC'],
    },
    books: {
      introductory: ['Rubinstein — Simulation and the Monte Carlo Method'],
      intermediate: ['MacDonald — Monte Carlo Radiation Transport'],
      advanced: ['Lewis & Miller — Computational Methods of Neutron Transport'],
      computational: ['OpenMC docs', 'MCNP manual'],
    },
    projectTracks: {
      basic: ['Estimativa de π', 'Atenuação 1D', 'Erro vs N'],
      intermediate: ['Slab de nêutrons', 'Redução de variância', 'Comparativo materiais'],
      advanced: ['Geometria 2D', 'Importance', 'GPU histórias'],
      ictcc: ['Validação didática vs ref', 'Convergência estatística', 'Relatório de incerteza'],
      masters: ['UQ em seções', 'Paralelização forte', 'Benchmark publicável'],
    },
  }),

  dinamica_molecular: defineDeepArea({
    label: 'Dinâmica molecular / modelagem molecular',
    aliases: ['dinamica_molecular', 'modelagem_molecular'],
    prerequisites: {
      math: ['Cálculo', 'EDOs', 'Estatística', 'Álgebra linear'],
      physics: ['Termodinâmica estatística', 'Mecânica clássica'],
      chemistry: ['Ligações', 'Estrutura molecular'],
      computation: ['Python', 'LAMMPS/GROMACS', 'Análise de trajetórias'],
    },
    theory: {
      foundations: ['Potenciais LJ', 'Coulomb', 'Ensembles', 'Verlet', 'Termostatos', 'Barostatos', 'RDF', 'MSD', 'Energia livre intro', 'Periodic boundary'],
      intermediate: ['Force fields', 'Fluidos confinados', 'Umbrella sampling', 'TI', 'QM/MM intro', 'Validação', 'Parametrização', 'Interações específicas', 'Polímeros fundidos', 'Interfaces'],
      advanced: ['Rare events', 'Metadynamics', 'Amorfos', 'Reações com QM', 'HPC MD', 'Coarse-graining', 'Free energy surfaces', 'Adsorção', 'Biomoléculas', 'Materiais energéticos'],
      researchLevel: ['ML potentials', 'Multiescala FEM-MD', 'Proteínas em escala', 'Reações catalíticas', 'Iônicos líquidos', 'Machine learning FF', 'Experiment validation', 'High-throughput MD', 'Publicação MD', 'Open science MD'],
    },
    books: {
      introductory: ['Frenkel & Smit — Understanding Molecular Simulation'],
      intermediate: ['Allen & Tildesley — Computer Simulation of Liquids', 'Rapaport — The Art of Molecular Dynamics'],
      advanced: ['Tuckerman — Statistical Mechanics', 'Leach — Molecular Modelling'],
      computational: ['LAMMPS manual', 'GROMACS guide'],
    },
    projectTracks: {
      basic: ['Gás em caixa 2D', 'RDF Lennard-Jones', 'MSD e difusão'],
      intermediate: ['Solução salina', 'PMF simplificada', 'Validação experimental'],
      advanced: ['QM/MM modelo', 'Metadynamics', 'Coarse-grain'],
      ictcc: ['Comparativo force fields', 'Artigo curto MD', 'Reprodutibilidade'],
      masters: ['ML potential', 'Multiescala com FEM', 'Biomolécula publicável'],
    },
  }),

  plasmas_fusao: defineDeepArea({
    label: 'Física de plasmas / fusão',
    aliases: ['plasmas', 'fusao', 'energia'],
    prerequisites: {
      math: ['Cálculo vetorial', 'EDPs', 'Métodos numéricos'],
      physics: ['Eletromagnetismo', 'Mecânica dos fluidos', 'Física estatística'],
      chemistry: ['Química de plasmas'],
      computation: ['Python', 'MHD intro'],
    },
    theory: {
      foundations: ['Quasi-neutralidade', 'Comprimento de Debye', 'Frequências de plasma', 'Movimento em B', 'Colisões', 'Confinamento magnético', 'Critério de Lawson', 'Heating auxiliar', 'Divertor', 'Parede de plasma'],
      intermediate: ['Equilíbrio MHD', 'Instabilidades', 'Tokamak', 'Stellarator', 'RF heating', 'Transporte anômalo', 'Materiais de primeira parede', 'Tritio e combustível', 'Diagnósticos', 'Escalas adimensionais'],
      advanced: ['MHD numérica', 'Gyrokinetics intro', 'Turbulência', 'ELMs', 'Disrupções', 'Acoplamento plasma-parede', 'Fusão inercial', 'Laser-plasma', 'Fusão magneto-inercial', 'Engenharia de tokamak'],
      researchLevel: ['ITER physics', 'Materiais para fusão', 'Turbulência gyrokinetic', 'Otimização de confinamento', 'Plasma-wall AI', 'Reator comercial', 'Fusão e economia', 'Simulação exascale', 'Validação internacional', 'Publicação em fusão'],
    },
    books: {
      introductory: ['Chen — Introduction to Plasma Physics'],
      intermediate: ['Freidberg — Plasma Physics and Fusion Energy', 'Wesson — Tokamaks'],
      advanced: ['Stangeby — The Plasma Boundary', 'Bittencourt — Fundamentals of Plasma Physics'],
      computational: ['BOUT++ docs', 'COMSOL plasma'],
    },
    projectTracks: {
      basic: ['Órbita em B', 'Frequência de plasma', 'Lawson 0D'],
      intermediate: ['Equilíbrio cilíndrico', 'Balanco de energia', 'Configurações comparadas'],
      advanced: ['Rayleigh-Taylor linear', 'Transporte 1D', 'MHD reduzida'],
      ictcc: ['Primeira parede survey', 'Tokamak conceitual', 'Literatura ITER'],
      masters: ['MHD com validação', 'Gyrokinetics intro publicável', 'Materiais de fusão'],
    },
  }),

  aeroespacial: defineDeepArea({
    label: 'Engenharia aeroespacial',
    aliases: ['aeroespacial', 'engenharia_aeroespacial', 'espaco'],
    prerequisites: {
      math: ['Cálculo', 'EDOs', 'Álgebra linear', 'Métodos numéricos'],
      physics: ['Mecânica', 'Fluidos', 'Termodinâmica'],
      chemistry: [],
      computation: ['Python', 'CAD/CAE intro', 'CFD tutorial'],
    },
    theory: {
      foundations: ['Aerodinâmica potencial', 'Perfis NACA', 'Propulsão a jato', 'Foguete químico', 'Orbital básica', 'Estruturas leves', 'Controle intro', 'Atmosfera padrão', 'Sistemas massa', 'Qualificação de voo'],
      intermediate: ['CFD 2D', 'Combustão', 'GNC', 'Materiais compostos', 'Testes estruturais', 'Aeroelasticidade intro', 'Propulsão elétrica', 'Missão LEO', 'Reentrada balística', 'Telemetria'],
      advanced: ['Hipersônico', 'Atitude 3D', 'Térmico espacial', 'Trajetória interplanetária', 'Otimização de missão', 'Fadiga aeroespacial', 'CubeSat systems', 'Navier-Stokes numérico', 'Controle robusto', 'Integração sistema'],
      researchLevel: ['Reutilizáveis', 'Propulsão nuclear espacial', 'Formação de voo', 'Autonomia', 'Space debris', 'Digital twin veículo', 'New space economics', 'Testes ambientais', 'Publicação AIAA-like', 'Simulação de missão completa'],
    },
    books: {
      introductory: ['Anderson — Introduction to Flight', 'Curtis — Orbital Mechanics'],
      intermediate: ['Anderson — Fundamentals of Aerodynamics', 'Sutton — Rocket Propulsion Elements'],
      advanced: ['Bertin — Aerodynamics for Engineers', 'Wertz — Spacecraft Attitude Determination and Control'],
      computational: ['OpenVSP', 'SU2 tutorials'],
    },
    projectTracks: {
      basic: ['Órbita 2D', 'Cp de perfil', 'Estrutura de barra'],
      intermediate: ['CFD aerofólio', 'Kepler com J2', 'Dimensionamento propulsor'],
      advanced: ['Trajetória otimizada', 'Aero-termo-estrutural', 'ADCS simplificado'],
      ictcc: ['CubeSat conceitual', 'Comparativo propulsores', 'Relatório de missão'],
      masters: ['Otimização trajetória', 'Digital twin ADCS', 'CFD validado'],
    },
  }),

  engenharia_defesa: defineDeepArea({
    label: 'Engenharia de defesa',
    aliases: ['engenharia_defesa', 'defesa', 'tecnologias_estrategicas'],
    prerequisites: {
      math: ['Cálculo', 'Controle', 'Sinais e sistemas', 'Probabilidade'],
      physics: ['Mecânica', 'Eletromagnetismo', 'Óptica'],
      chemistry: [],
      computation: ['Python', 'Simulação', 'GIS'],
    },
    theory: {
      foundations: ['Sistemas de armas', 'Sensores', 'Fusão de dados', 'Balística', 'EW intro', 'Logística', 'Robótica móvel', 'Radar intro', 'GNSS', 'Ética e governança'],
      intermediate: ['Engajamento', 'Kalman', 'Visão computacional', 'Navegação inercial', 'Redes táticas', 'Teste e avaliação', 'Materiais balísticos', 'Propulsão tática', 'Cenários', 'Simulação 2D'],
      advanced: ['LVC', 'Autonomia', 'Guerra eletrônica', 'Otimização de trajetória', 'Resiliência', 'Cibersegurança operacional', 'IA explicável', 'Sistemas complexos', 'Análise de vulnerabilidade', 'Pós-análise de missão'],
      researchLevel: ['IA decisão', 'Simulação distribuída', 'Tecnologias duais', 'Normas internacionais', 'Swarm', 'Anti-drone', 'Space defense', 'Modelagem humano-máquina', 'Publicação em defesa', 'Validação de campo'],
    },
    books: {
      introductory: ['Blake — Radar Systems Analysis'],
      intermediate: ['Zarchan — Tactical and Strategic Missile Guidance', 'Stevens — Aircraft Control and Simulation'],
      advanced: ['Mahafza — Radar Systems'],
      computational: ['ROS2 navigation', 'ArduPilot'],
    },
    projectTracks: {
      basic: ['Balística ideal', 'Detecção em imagem', 'Cenário 2D'],
      intermediate: ['Kalman GPS-IMU', 'Simulação tática', 'EW jamming simples'],
      advanced: ['Engajamento MC', 'Autonomia ética', 'Fusão multi-sensor'],
      ictcc: ['UAV sensores', 'Trajetória perturbada', 'Relatório LVC'],
      masters: ['Simulação LVC completa', 'IA explicável cenários', 'Resiliência cyber-física'],
    },
  }),

  instrumentacao: defineDeepArea({
    label: 'Instrumentação / sensores',
    aliases: ['instrumentacao', 'robotica'],
    prerequisites: {
      math: ['Sinais e sistemas', 'Controle', 'Estatística'],
      physics: ['Eletrônica', 'Óptica', 'Sensores físicos'],
      chemistry: [],
      computation: ['Python', 'DAQ', 'Microcontroladores'],
    },
    theory: {
      foundations: ['Sensores T/P/fluxo', 'Condicionamento', 'Amostragem', 'Ruído e SNR', 'Calibração', 'Metrologia', 'ADC/DAC', 'Filtros', 'Instrumentação nuclear', 'Fibra óptica'],
      intermediate: ['Espectrometria', 'Lock-in', 'PID', 'Embarcados', 'Padrões traceáveis', 'Instrumentação espacial', 'Redes de sensores', 'Fusão', 'Teste ambiental', 'Documentação metrológica'],
      advanced: ['Sistemas críticos', 'Instrumentação distribuída', 'Radiação em eletrônica', 'Qualificação espacial', 'Optoeletrônica', 'Sensoriamento remoto', 'IoT científico', 'Incerteza GUM', 'Automatização', 'Manutenção preditiva'],
      researchLevel: ['Sensores quânticos', 'Fusão avançada', 'Instrumentação fusão', 'Biomedical devices', 'Publicação metrológica', 'Edge AI sensores', 'Digital twin instrumento', 'Normas IEEE', 'Grande instrumentação', 'Open hardware'],
    },
    books: {
      introductory: ['Fraden — Handbook of Modern Sensors', 'Webster — Measurement'],
      intermediate: ['Knoll — Radiation Detection', 'Doebelin — Measurement Systems'],
      advanced: ['White — Vacuum Technology'],
      computational: ['LabVIEW/Python DAQ'],
    },
    projectTracks: {
      basic: ['Calibração linear', 'FFT de sensor', 'SNR vs filtro'],
      intermediate: ['Espectro simulado', 'PID térmico', 'DAQ completo'],
      advanced: ['Fusão Kalman/particle', 'Instrumentação nuclear', 'Metrologia GUM'],
      ictcc: ['Detectores comparados', 'Experimento laboratório', 'Relatório de calibração'],
      masters: ['Instrumento ambiente extremo', 'Incerteza publicável', 'IoT científico'],
    },
  }),

  dosimetria: defineDeepArea({
    label: 'Dosimetria / proteção radiológica',
    aliases: ['dosimetria', 'protecao_radiologica'],
    prerequisites: {
      math: ['Probabilidade', 'Estatística'],
      physics: ['Física nuclear intro', 'Interação radiação-matéria'],
      chemistry: ['Bioquímica básica'],
      computation: ['Python', 'MC dose intro'],
    },
    theory: {
      foundations: ['Kerma e dose', 'Equivalente', 'Limites regulatórios', 'Distância e tempo', 'Blindagem', 'Monitoração', 'Efeitos biológicos', 'Fontes', 'Transporte', 'Emergência'],
      intermediate: ['Dose em heterogeneidades', 'Proteção de instalações', 'Dosimetria computacional', 'Fantomas', 'Monte Carlo dose', 'Blindagem de laboratório', 'Acidentes', 'Planejamento radioterapia intro', 'Radiação espacial', 'Incerteza'],
      advanced: ['Voxel phantoms', 'Monte Carlo clínico', 'Terapia', 'Otimização EPI', 'Proteção de público', 'Pós-acidente', 'Normas ICRP', 'Instrumentação de dose', 'Neutrons em dose', 'Validação experimental'],
      researchLevel: ['Medicina nuclear dose', 'Aceleradores', 'Recuperação ambiental', 'UQ em dose', 'Proteção de trabalhadores', 'Dose em missão espacial', 'Modelagem epidemiológica', 'Publicação dosimétrica', 'Códigos MCNP dose', 'Análise de risco'],
    },
    books: {
      introductory: ['Martin — Introduction to Radiation Protection', 'Attix — Introduction to Radiological Physics'],
      intermediate: ['ICRU reports selecionados', 'Khan — Radiation Therapy Physics'],
      advanced: ['Pelliccioni — Radiation Protection'],
      computational: ['MCNP dose tallies', 'EGSnrc'],
    },
    projectTracks: {
      basic: ['Calculadora de dose', 'Mapa 2D atenuação', 'Fatores de qualidade'],
      intermediate: ['MC fantoma', 'Plano de blindagem', 'Monitoração simulada'],
      advanced: ['Dose voxel', 'Otimização EPI', 'Validação medida'],
      ictcc: ['Comparativo códigos dose', 'Acidente hipotético', 'Relatório regulatório'],
      masters: ['Dosimetria computacional validada', 'UQ monitoração', 'Missão espacial dose'],
    },
  }),

  medicina_nuclear: defineDeepArea({
    label: 'Medicina nuclear',
    aliases: ['medicina_nuclear'],
    prerequisites: {
      math: ['Estatística', 'Cálculo'],
      physics: ['Física nuclear', 'Detecção'],
      chemistry: ['Bioquímica', 'Radioquímica intro'],
      computation: ['Python', 'Processamento de imagem'],
    },
    theory: {
      foundations: ['Radiofármacos', 'PET/SPECT intro', 'Meia-vida clínica', 'Dosimetria interna', 'Segurança do paciente', 'Regulamentação ANVISA/IAEA', 'Cintilografia', 'Contraste', 'Farmacocinética', 'Ética clínica'],
      intermediate: ['Produção de radiofármacos', 'QC analítico', 'Tomografia', 'Fusão imagem', 'Terapia com alfa/beta', 'Radioproteção hospitalar', 'Descarte', 'Protocolos clínicos', 'Física de detectores clínicos', 'Processamento de sinal'],
      advanced: ['Dosimetria personalizada', 'Teranóstica', 'Novos radionuclídeos', 'IA em imagem nuclear', 'Quantificação PET', 'Monte Carlo clínico', 'Trials', 'Radiobiologia', 'Equipamentos híbridos', 'Gestão de dose'],
      researchLevel: ['Tracers inovadores', 'Medicina personalizada', 'Imagem multiparamétrica', 'Publicação clínica', 'Trials phase', 'Radiomics', 'Produção escalável', 'Regulação internacional', 'Dose otimizada', 'Medicina nuclear molecular'],
    },
    books: {
      introductory: ['Saha — Fundamentals of Nuclear Pharmacy'],
      intermediate: ['Cherry, Sorenson & Phelps — Physics in Nuclear Medicine'],
      advanced: ['ICRP em medicina nuclear'],
      computational: ['ImageJ / pydicom'],
    },
    projectTracks: {
      basic: ['Decaimento para radiofármaco', 'Dose simplificada', 'Imagem sintética'],
      intermediate: ['QC de produção simulada', 'PET quantificação intro', 'Protocolo clínico review'],
      advanced: ['Dosimetria interna MC', 'Teranóstica case', 'IA segmentação'],
      ictcc: ['Comparativo modalidades', 'Revisão regulatória', 'Projeto hospitalar'],
      masters: ['Tracer inovador', 'Trial design', 'Radiomics publicável'],
    },
  }),

  ia_cientifica: defineDeepArea({
    label: 'IA científica / ML aplicado',
    aliases: ['ia_cientifica', 'sistemas_autonomos'],
    prerequisites: {
      math: ['Álgebra linear', 'Cálculo', 'Otimização', 'Probabilidade'],
      physics: ['Física intro para domínio'],
      chemistry: [],
      computation: ['Python', 'scikit-learn', 'PyTorch intro', 'pandas'],
    },
    theory: {
      foundations: ['Supervisionado', 'Validação cruzada', 'Overfitting', 'Features científicas', 'Métricas', 'Baseline', 'Ética', 'Viés', 'Visualização', 'Reprodutibilidade'],
      intermediate: ['Redes neurais', 'CNN', 'Séries temporais', 'Surrogate', 'Bayesian ML', 'Active learning', 'MLflow', 'Interpretabilidade SHAP', 'Domain adaptation', 'Data leakage'],
      advanced: ['PINNs', 'GNN', 'UQ em ML', 'HPC+ML', 'AutoML físico', 'Causal ML', 'Diffusion models', 'RL científico', 'Federated learning', 'MLOps'],
      researchLevel: ['Foundation models ciência', 'ML+simulação acoplada', 'Digital twin ML', 'Publicação NeurIPS-style aplicada', 'Benchmark aberto', 'Explainability legal', 'Edge deployment', 'Continual learning', 'Scientific AGI limits', 'Open datasets'],
    },
    books: {
      introductory: ['Géron — Hands-On Machine Learning', 'James — Introduction to Statistical Learning'],
      intermediate: ['Goodfellow — Deep Learning', 'Bishop — Pattern Recognition and ML'],
      advanced: ['Murphy — Probabilistic Machine Learning', 'Karniadakis — Physics-Informed ML'],
      computational: ['PyTorch docs', 'Weights & Biases'],
    },
    projectTracks: {
      basic: ['Classificação tabular', 'Regressão material', 'Baseline sklearn'],
      intermediate: ['Surrogate 1D', 'CNN micrografia', 'Pipeline MLflow'],
      advanced: ['PINN EDP', 'UQ ensemble', 'GNN moléculas'],
      ictcc: ['ML vs física', 'Reprodutibilidade', 'Artigo aplicado'],
      masters: ['Híbrido físico-ML', 'OOD validation', 'Foundation fine-tune'],
    },
  }),

  ciencia_dados: defineDeepArea({
    label: 'Ciência dos dados',
    aliases: ['ciencia_dados'],
    prerequisites: {
      math: ['Estatística', 'Álgebra linear', 'Cálculo'],
      physics: [],
      chemistry: [],
      computation: ['Python', 'pandas', 'SQL', 'Visualização'],
    },
    theory: {
      foundations: ['EDA', 'Distribuições', 'Teste de hipóteses', 'Regressão', 'Classificação', 'Clustering', 'Visualização', 'ETL', 'Qualidade de dados', 'Ética de dados'],
      intermediate: ['Feature engineering', 'Pipeline sklearn', 'Séries temporais', 'Texto intro', 'SQL avançado', 'Big data intro', 'A/B testing', 'Causal inference intro', 'Dashboards', 'APIs de dados'],
      advanced: ['Deep learning aplicado', 'MLOps', 'Spark intro', 'Grafos', 'Bayesian data science', 'Privacidade', 'Streaming', 'Experiment design', 'Otimização de negócio', 'Deploy'],
      researchLevel: ['Causal ML', 'Fairness', 'Data products', 'Publicação KDD-like', 'Open data', 'Real-time analytics', 'AutoML', 'LLM para ciência', 'Governança', 'Reprodutibilidade'],
    },
    books: {
      introductory: ['McKinney — Python for Data Analysis'],
      intermediate: ['James — ISLR', 'VanderPlas — Python Data Science Handbook'],
      advanced: ['Hastie — Elements of Statistical Learning'],
      computational: ['pandas/sklearn docs'],
    },
    projectTracks: {
      basic: ['EDA dataset aberto', 'Dashboard Streamlit', 'Limpeza de dados'],
      intermediate: ['Pipeline sklearn', 'Série temporal', 'SQL analytics'],
      advanced: ['Deploy modelo', 'Spark job', 'Causal study'],
      ictcc: ['Estudo de caso completo', 'Relatório executivo', 'Reprodutibilidade'],
      masters: ['Produto de dados', 'Causal publicável', 'Governança'],
    },
  }),

  energia: defineDeepArea({
    label: 'Energia (sistemas e transição)',
    aliases: ['energia'],
    prerequisites: {
      math: ['Cálculo', 'Otimização', 'Estatística'],
      physics: ['Termodinâmica', 'Mecânica dos fluidos', 'Eletromagnetismo'],
      chemistry: ['Química eletroquímica'],
      computation: ['Python', 'Modelagem de sistemas'],
    },
    theory: {
      foundations: ['Balanco energético', 'Renováveis', 'Redes elétricas intro', 'Armazenamento', 'Eficiência', 'Combustíveis fósseis', 'Hidrogênio', 'Política energética', 'Mercado', 'Sustentabilidade'],
      intermediate: ['Integração renovável', 'Smart grid', 'Baterias', 'Cogeração', 'Nuclear na matriz', 'Hidro', 'Solar PV detalhado', 'Eólica', 'Modelagem de demanda', 'Cenários'],
      advanced: ['Otimização de mix', 'Microgrids', 'H2 verde', 'CCUS', 'Fusão na matriz', 'Resiliência', 'Digital twin grid', 'Mercado spot', 'Incerteza', 'Transição justa'],
      researchLevel: ['100% renovável', 'Storage breakthrough', 'Policy modeling', 'Climate coupling', 'Publicação energy systems', 'International scenarios', 'Nuclear-renovável', 'Hydrogen economy', 'Grid stability AI', 'Open energy data'],
    },
    books: {
      introductory: ['Smil — Energy', 'Boyle — Renewable Energy'],
      intermediate: ['Tester — Sustainable Energy', 'González-Longatt — Fundamentals of Grid Integration'],
      advanced: ['IEA World Energy Outlook reports'],
      computational: ['PyPSA intro', 'EnergyPLAN'],
    },
    projectTracks: {
      basic: ['Balanco casa/planta', 'Curva solar diária', 'Eficiência comparativa'],
      intermediate: ['Mix renovável', 'Bateria sizing', 'Demanda forecasting'],
      advanced: ['Microgrid sim', 'CCUS chain', 'Otimização mix'],
      ictcc: ['Cenário país/região', 'Policy brief', 'Integração nuclear'],
      masters: ['Modelo transição', 'Publicação cenários', 'Resiliência climática'],
    },
  }),

  quantica: defineDeepArea({
    label: 'Física quântica',
    aliases: ['quantica'],
    prerequisites: {
      math: ['Cálculo', 'Álgebra linear', 'EDPs', 'Probabilidade'],
      physics: ['Mecânica clássica', 'Eletromagnetismo', 'Física moderna'],
      chemistry: [],
      computation: ['Python', 'Álgebra linear numérica'],
    },
    theory: {
      foundations: ['Postulados', 'Schrodinger 1D', 'Poço de potencial', 'Harmônico', 'Momento angular', 'Spin', 'Pauli', 'Átomo de hidrogênio', 'Spin-orbita', 'Medida'],
      intermediate: ['Perturbação', 'Variacional', 'WKB', 'Muitos corpos intro', 'Identidade de partículas', 'Aproximação de campo médio', 'Emaranhamento', 'Bell', 'Informação quântica', 'Qubit'],
      advanced: ['Teoria de campos intro', 'Relatividade QR', 'QFT básica', 'Computação quântica', 'Algoritmos de Shor/Grover', 'Decoerência', 'Open quantum systems', 'Condensado', 'Topológica', 'Química quântica avançada'],
      researchLevel: ['Hardware quântico', 'Error correction', 'Simulação quântica', 'QML', 'Fundamentos interpretação', 'Experimentos de precisão', 'Publicação PRX/Quantum', 'Quantum sensing', 'Cryptography', 'Many-body numérico'],
    },
    books: {
      introductory: ['Griffiths — Introduction to Quantum Mechanics'],
      intermediate: ['Sakurai — Modern Quantum Mechanics', 'Shankar — Principles of Quantum Mechanics'],
      advanced: ['Cohen-Tannoudji — Quantum Mechanics', 'Nielsen & Chuang — Quantum Computation'],
      computational: ['Qiskit tutorials', 'QuTiP'],
    },
    projectTracks: {
      basic: ['Poço infinito numérico', 'Harmônico', 'Spin 1/2'],
      intermediate: ['Perturbação', 'Variacional H', 'Qubit simulador'],
      advanced: ['QuTiP open system', 'Qiskit algorithm', 'DFT H small'],
      ictcc: ['Review computação quântica', 'Artigo didático', 'Bell inequality sim'],
      masters: ['Many-body ED', 'QML aplicado', 'Publicação numérica'],
    },
  }),

  engenharia_fisica: defineDeepArea({
    label: 'Engenharia física',
    aliases: ['engenharia_fisica'],
    prerequisites: {
      math: ['Cálculo', 'EDPs', 'Métodos numéricos', 'Estatística'],
      physics: ['Mecânica', 'EM', 'Termodinâmica', 'Quântica intro'],
      chemistry: ['Química geral'],
      computation: ['Python', 'Simulação', 'Instrumentação'],
    },
    theory: {
      foundations: ['Modelagem física', 'Análise dimensional', 'Prototipagem', 'Instrumentação', 'Materiais', 'Semicondutores intro', 'Óptica', 'Acústica', 'Física do estado sólido', 'Laboratório seguro'],
      intermediate: ['Dispositivos', 'Nanotecnologia intro', 'Controle', 'Sinais', 'Simulação multiphysics', 'Caracterização', 'Projeto integrado', 'Empreendedorismo deep tech', 'Ética', 'Comunicação científica'],
      advanced: ['Fotônica', 'Spintrônica', 'Plasmonics', 'Sensores avançados', 'Energia em escala', 'Biofísica aplicada', 'Computação científica', 'Otimização de sistema', 'Pesquisa aplicada', 'Transferência tecnologia'],
      researchLevel: ['Spin-off', 'Patentes', 'Publicação applied physics', 'Parceria indústria', 'Grand challenges', 'Interdisciplinar', 'Instrumentação inovadora', 'Standardização', 'Mentoria IC', 'Mestrado profissional'],
    },
    books: {
      introductory: ['Serway — Physics for Scientists and Engineers'],
      intermediate: ['Ashcroft & Mermin — Solid State Physics (seleções)'],
      advanced: ['Sze — Semiconductor Devices'],
      computational: ['COMSOL intro'],
    },
    projectTracks: {
      basic: ['Análise dimensional projeto', 'Instrumentação básica', 'Relatório lab'],
      intermediate: ['Simulação dispositivo', 'Caracterização material', 'Controle PID'],
      advanced: ['Protótipo sensor', 'Multiphysics', 'Estudo de mercado tech'],
      ictcc: ['Projeto integrador', 'Parceria indústria', 'Artigo applied physics'],
      masters: ['Spin-off plan', 'Instrumento inovador', 'Publicação aplicada'],
    },
  }),

  hpc: defineDeepArea({
    label: 'Computação de alto desempenho (HPC)',
    aliases: ['hpc'],
    prerequisites: {
      math: ['Álgebra linear', 'Cálculo numérico'],
      physics: [],
      chemistry: [],
      computation: ['C/C++', 'Python', 'Linux', 'MPI intro'],
    },
    theory: {
      foundations: ['Arquitetura', 'Memória', 'Cache', 'Paralelismo', 'MPI', 'OpenMP', 'Profiling', 'Strong/weak scaling', 'Clusters', 'Filesystems'],
      intermediate: ['CUDA intro', 'Otimização', 'IO paralelo', 'Job schedulers', 'Containers HPC', 'Debugging paralelo', 'Numerical libraries', 'Roofline', 'Energy HPC', 'Workflows'],
      advanced: ['GPU computing', 'Exascale', 'I/O exascale', 'Fault tolerance', 'Hybrid programming', 'Performance modeling', 'Scientific apps', 'Cloud HPC', 'AI on HPC', 'Storage hierarchy'],
      researchLevel: ['New architectures', 'Quantum+HPC', 'Green HPC', 'Publication SC', 'Benchmark TOP500 analysis', 'Parallel algorithms research', 'Interconnects', 'In-situ visualization', 'Workflow systems', 'Open source HPC stack'],
    },
    books: {
      introductory: ['Eijkhout — Introduction to High Performance Scientific Computing'],
      intermediate: ['Pacheco — Parallel Programming with MPI'],
      advanced: ['Kirk & Hwu — Programming Massively Parallel Processors'],
      computational: ['OpenMPI docs', 'SLURM guide'],
    },
    projectTracks: {
      basic: ['OpenMP loop', 'MPI hello', 'Roofline plot'],
      intermediate: ['Scaling study', 'CUDA kernel', 'Profile otimização'],
      advanced: ['Hybrid MPI+OpenMP', 'IO paralelo', 'Container cluster'],
      ictcc: ['Benchmark curso', 'Relatório scaling', 'Otimização legado'],
      masters: ['Exascale mini-app', 'Publication performance', 'Green HPC study'],
    },
  }),

  sistemas_autonomos: defineDeepArea({
    label: 'Sistemas autônomos',
    aliases: ['sistemas_autonomos'],
    prerequisites: {
      math: ['Controle', 'Probabilidade', 'Otimização'],
      physics: ['Mecânica', 'Sensores'],
      chemistry: [],
      computation: ['Python', 'ROS', 'C++'],
    },
    theory: {
      foundations: ['Percepção', 'Planejamento', 'Controle', 'SLAM intro', 'Ética autonomia', 'Segurança', 'Teste', 'Simuladores', 'Hardware', 'Regulação'],
      intermediate: ['Fusão sensorial', 'Path planning', 'Kalman SLAM', 'Visão', 'LIDAR', 'ROS navigation', 'Human-in-the-loop', 'V&V', 'Cenários', 'Redundância'],
      advanced: ['Aprendizado por reforço', 'Multi-robot', 'Swarm', 'Autonomia nível 4/5', 'Sim-to-real', 'Adversarial', 'Certificação', 'Edge compute', 'Comunicação V2X', 'Missão'],
      researchLevel: ['IA segura', 'Regulação internacional', 'Publicação RSS/ICRA', 'Campo real', 'Digital twin fleet', 'Human factors', 'Ethics publication', 'Open robotics', 'Standardization', 'Defense/civilian dual'],
    },
    books: {
      introductory: ['Siegwart — Introduction to Autonomous Mobile Robots'],
      intermediate: ['Thrun — Probabilistic Robotics'],
      advanced: ['LaValle — Planning Algorithms'],
      computational: ['ROS2 docs', 'Gazebo'],
    },
    projectTracks: {
      basic: ['Simulador 2D', 'PID trajetória', 'Sensor fusion toy'],
      intermediate: ['SLAM sim', 'ROS navigation', 'Visão lane'],
      advanced: ['RL sim-to-real', 'Multi-agent', 'Safety case'],
      ictcc: ['Competição robótica', 'Relatório V&V', 'Campo controlado'],
      masters: ['Fleet digital twin', 'Publicação autonomia', 'Certificação estudo'],
    },
  }),

  tecnologias_estrategicas: defineDeepArea({
    label: 'Tecnologias estratégicas',
    aliases: ['tecnologias_estrategicas'],
    prerequisites: {
      math: ['Estatística', 'Modelagem'],
      physics: ['Física aplicada'],
      chemistry: [],
      computation: ['Python', 'Análise de cenários'],
    },
    theory: {
      foundations: ['Cadeias de suprimento', 'Soberania tecnológica', 'Dual use', 'Inovação', 'TRL', 'Roadmaps', 'Propriedade intelectual', 'Parcerias', 'Riscos', 'Geopolítica tech'],
      intermediate: ['Semicondutores', 'Baterias', 'IA', 'Biotec', 'Espaço', 'Nuclear', 'Defesa', 'Análise multicritério', 'Cenários', 'Políticas públicas'],
      advanced: ['Gaps nacionais', 'Investimento', 'Consórcios', 'Export controls', 'Talent pipeline', 'Infraestrutura', 'Standards', 'Ethics dual use', 'Foresight', 'Portfolio'],
      researchLevel: ['Estratégia nacional', 'Publicação policy', 'Benchmark internacional', 'Simulação econômica', 'Segurança econômica', 'Open strategic data', 'Innovation systems', 'Mega-projetos', 'Risk governance', 'Future studies'],
    },
    books: {
      introductory: ['Porter — Competitive Strategy (seleções)'],
      intermediate: ['Mazzucato — The Entrepreneurial State'],
      advanced: ['OECD Science, Technology and Innovation Outlook'],
      computational: ['Cenários em Python'],
    },
    projectTracks: {
      basic: ['Mapa TRL tecnologia', 'Análise SWOT', 'Roadmap visual'],
      intermediate: ['Multicritério', 'Cenário 2035', 'Cadeia suprimento'],
      advanced: ['Portfolio investimento', 'Gap analysis país', 'Policy brief'],
      ictcc: ['Estudo estratégico setor', 'Comparativo internacional', 'Relatório executivo'],
      masters: ['Estratégia tecnológica', 'Publicação policy', 'Simulação econômica'],
    },
  }),

  robotica: defineDeepArea({
    label: 'Robótica',
    aliases: ['robotica'],
    prerequisites: {
      math: ['Álgebra linear', 'Controle', 'Cinemática'],
      physics: ['Mecânica', 'Eletromagnetismo'],
      chemistry: [],
      computation: ['Python', 'ROS', 'C++'],
    },
    theory: {
      foundations: ['Cinemática', 'Dinâmica', 'Atuadores', 'Sensores', 'Controle PID', 'Visão', 'Planejamento', 'Segurança', 'Simulação', 'Programação embarcada'],
      intermediate: ['Cinemática inversa', 'Jacobiano', 'Trajetórias', 'Force control', 'SLAM', 'Manipuladores', 'Mobile robots', 'ROS', 'Calibração', 'Teste'],
      advanced: ['Dinâmica avançada', 'Aprendizado manipulação', 'Soft robotics', 'Humanoid intro', 'Swarm', 'Medical robotics', 'Industrial IoT', 'Digital twin', 'Haptics', 'Colaborativos'],
      researchLevel: ['Publicação ICRA', 'Campo real', 'Autonomia manipulação', 'Ethics', 'Standards ISO', 'New materials', 'Underwater/space robots', 'AI planning', 'Open hardware', 'Startup robotics'],
    },
    books: {
      introductory: ['Corke — Robotics, Vision and Control'],
      intermediate: ['Siciliano — Robotics: Modelling, Planning and Control'],
      advanced: ['Murray, Li & Sastry — A Mathematical Introduction to Robotic Manipulation'],
      computational: ['ROS2 docs'],
    },
    projectTracks: {
      basic: ['Cinemática 2R', 'PID ponto a ponto', 'Sim Gazebo'],
      intermediate: ['ROS moveit intro', 'SLAM 2D', 'Visão pick'],
      advanced: ['Force control', 'RL grasp', 'Digital twin braço'],
      ictcc: ['Competição', 'Projeto manipulador', 'Relatório ISO safety'],
      masters: ['Publicação robótica', 'Campo real', 'Startup plan'],
    },
  }),

  biotecnologia: defineDeepArea({
    label: 'Biotecnologia',
    aliases: ['biotecnologia'],
    prerequisites: {
      math: ['Estatística', 'Cálculo'],
      physics: ['Biofísica intro'],
      chemistry: ['Bioquímica', 'Química orgânica'],
      computation: ['Python', 'Bioinformática leve'],
    },
    theory: {
      foundations: ['Célula', 'DNA/RNA', 'Proteínas', 'Enzimas', 'Fermentação', 'Biorreatores', 'Sterile technique', 'Biossegurança', 'Ética', 'Regulação'],
      intermediate: ['Clonagem', 'PCR', 'Sequenciamento', 'Expressão', 'Purificação', 'Metabolismo', 'Genômica', 'Proteômica', 'CRISPR intro', 'Bioprocessos'],
      advanced: ['Synthetic biology', 'Metabolic engineering', 'Scale-up', 'Downstream', 'GMP intro', 'Vaccines', 'Therapeutics', 'Omics integration', 'Systems biology', 'Biocomputação'],
      researchLevel: ['Terapia gênica', 'Publicação Nature Biotech-like', 'Clinical translation', 'Bioeconomy', 'Open science bio', 'Biosafety L3+', 'Patentes', 'Startup biotech', 'Regulatory approval', 'Personalized medicine'],
    },
    books: {
      introductory: ['Alberts — Molecular Biology of the Cell (seleções)'],
      intermediate: ['Doran — Bioprocess Engineering Principles'],
      advanced: ['Nielsen — Metabolic Engineering'],
      computational: ['Biopython docs'],
    },
    projectTracks: {
      basic: ['Crescimento microbial curva', 'PCR in silico', 'Protocolo biossegurança'],
      intermediate: ['Expressão simulada', 'Biorreator balanço', 'Genômica EDA'],
      advanced: ['Metabolic model FBA', 'CRISPR design', 'Scale-up econômico'],
      ictcc: ['Projeto bioprocesso', 'Review regulatório', 'Artigo omics'],
      masters: ['Strain engineering', 'Publicação biotech', 'Plano GMP'],
    },
  }),
};
