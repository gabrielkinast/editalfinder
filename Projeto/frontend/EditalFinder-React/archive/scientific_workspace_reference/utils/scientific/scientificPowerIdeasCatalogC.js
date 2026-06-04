/**
 * Fase 2J — Bloco C: ideias poderosas para materiais, energia, eng. física,
 * instrumentação, biotecnologia, defesa, espaço, aeroespacial, tecnologias
 * estratégicas, medicina nuclear, dosimetria e proteção radiológica.
 */
import { definePowerIdea } from './scientificPowerIdeasHelpers';

export const POWER_IDEAS_CATALOG_C = {
  materiais: [
    definePowerIdea({
      id: 'materiais-structure-property-processing',
      title: 'Triângulo estrutura–propriedade–processamento',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Muda a forma de raciocinar sobre materiais: você deixa de perguntar só "qual propriedade?" e passa a perguntar "qual microestrutura e qual rota de fabricação a produzem?".',
      shortExplanation:
        'Toda propriedade macroscópica (resistência, condutividade, dureza) emerge de estrutura em múltiplas escalas e do histórico térmico-mecânico do processamento. Alterar um vértice do triângulo força mudanças nos outros dois.',
      useFor: ['Seleção de liga', 'Projeto de tratamento térmico', 'Diagnóstico de falha'],
      prerequisites: ['Cristalografia básica', 'Termodinâmica de fases'],
      relatedTopics: ['Diagramas de fase', 'Defeitos cristalinos', 'Regra alavanca'],
      projectIdeas: ['Mapa estrutura–propriedade para uma liga Al–Cu', 'Comparar propriedades após recozimento vs. têmpera'],
      professorQuestions: [
        'Se eu quiser dobrar a resistência à tração sem perder tenacidade, qual vértice do triângulo você atacaria primeiro?',
        'Como você provaria experimentalmente que a microestrutura — e não a composição nominal — explica a falha?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-fick',
      title: 'Lei de Fick e difusão em sólidos',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Transforma difusão de fenômeno misterioso em transporte quantificável — essencial para tratamentos térmicos, revestimentos e envelhecimento.',
      shortExplanation:
        'A taxa de fluxo de espécies é proporcional ao gradiente de concentração. Em sólidos, coeficientes de difusão dependem fortemente da temperatura via processos termicamente ativados.',
      useFor: ['Carburização', 'Homogeneização de ligas', 'Estimativa de tempo de tratamento'],
      prerequisites: ['Derivadas parciais', 'Arrhenius'],
      relatedTopics: ['Difusão termicamente ativada', 'Defeitos cristalinos', 'Nucleação'],
      projectIdeas: ['Simular perfil de concentração após difusão gaussiana', 'Estimar D(T) a partir de dados de envelhecimento'],
      professorQuestions: [
        'Por que a difusão intersticial é ordens de magnitude mais rápida que a substitucional?',
        'Como você separaria efeitos de difusão de efeitos de interface de grão na sua curva experimental?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-hall-petch',
      title: 'Relação Hall–Petch',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Conecta tamanho de grão — microestrutura mensurável — à resistência mecânica, guiando estratégias de refino de grão.',
      shortExplanation:
        'A resistência ao escoamento cresce com d⁻¹/², onde d é o diâmetro médio de grão. Grãos menores bloqueiam dislocações nos contornos, aumentando a resistência.',
      useFor: ['Refino de grão', 'Interpretação de ensaios mecânicos', 'Projeto de tratamentos plásticos'],
      prerequisites: ['Mecânica dos sólidos', 'Contornos de grão'],
      relatedTopics: ['Energia de contorno de grão', 'Defeitos cristalinos', 'Triângulo estrutura–propriedade'],
      projectIdeas: ['Plotar σ_y vs. d⁻¹/² para amostras recozidas', 'Comparar limite Hall–Petch com liga com precipitados'],
      professorQuestions: [
        'Em que regime de tamanho de grão a relação Hall–Petch deixa de valer e por quê?',
        'Como você mediria d de forma estatisticamente representativa na sua amostra?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-griffith',
      title: 'Critério de Griffith para fratura frágil',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Mostra que materiais frágeis falham quando a energia elástica liberada supera a energia de criar superfície — unifica resistência e tenacidade.',
      shortExplanation:
        'Uma trinca de comprimento crítico cresce espontaneamente quando G ≥ 2γ, onde G é a taxa de liberação de energia e γ a energia superficial. Conecta tensão aplicada, tamanho de defeito e tenacidade à fratura.',
      useFor: ['Análise de falha', 'Projeto à prova de trinca', 'Seleção de materiais frágeis'],
      prerequisites: ['Energia elástica', 'Tenacidade à fratura'],
      relatedTopics: ['Defeitos cristalinos', 'Diagramas de Ashby', 'Contornos de grão'],
      projectIdeas: ['Calcular ac da trinca crítica para vidro ou cerâmica', 'Comparar K_Ic medido com predição de Griffith'],
      professorQuestions: [
        'Por que o critério de Griffith precisa de adaptação para materiais dúcteis?',
        'Qual o menor defeito detectável pelo seu método NDT e o que isso implica para σ_f?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-lever-rule',
      title: 'Regra alavanca (lever rule)',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Permite prever frações de fase e composições em equilíbrio a partir de diagramas — ponte direta entre termodinâmica e microestrutura.',
      shortExplanation:
        'Em uma região bifásica, as frações de fase são inversamente proporcionais aos braços de alavanca no diagrama de fase. É uma consequência do balanço de massa em equilíbrio.',
      useFor: ['Cálculo de fração de fase', 'Interpretação de micrografia', 'Projeto de composição'],
      prerequisites: ['Diagramas de fase binários', 'Balanço de massa'],
      relatedTopics: ['Diagramas de fase', 'Nucleação', 'Triângulo estrutura–propriedade'],
      projectIdeas: ['Calcular frações α+β para liga Fe–C a 750 °C', 'Validar regra alavanca com ImageJ em micrografia'],
      professorQuestions: [
        'O que acontece com a regra alavanca se a cinética de resfriamento impedir equilíbrio?',
        'Como você distinguiria fração de fase de equilíbrio de precipitado metaestável?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-phase-diagrams',
      title: 'Diagramas de fase como mapas de processamento',
      type: 'ferramenta-computacional',
      level: 'intermediario',
      whyItMatters:
        'Diagramas deixam de ser figuras decorativas e viram mapas operacionais: onde aquecer, resfriar e quais fases esperar.',
      shortExplanation:
        'Diagramas de fase mostram fases estáveis (ou metaestáveis) em função de composição e temperatura. Softwares como CALPHAD estendem diagramas binários para sistemas multicomponentes.',
      useFor: ['Projeto de tratamento térmico', 'Previsão de solidificação', 'Seleção de liga'],
      prerequisites: ['Termodinâmica', 'Regra alavanca'],
      relatedTopics: ['Regra alavanca', 'Nucleação', 'Difusão termicamente ativada'],
      projectIdeas: ['Traçar rota de tratamento térmico no diagrama Fe–C', 'Comparar diagrama experimental com CALPHAD'],
      professorQuestions: [
        'Quais suposições de equilíbrio seu diagrama assume e onde elas falham na prática?',
        'Como você incorporaria efeitos cinéticos em um diagrama puramente termodinâmico?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-nucleation',
      title: 'Nucleação homogênea e heterogênea',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Explica por que fases novas aparecem onde e quando aparecem — nucleação controla granulometria, precipitação e solidificação.',
      shortExplanation:
        'A formação de um núcleo exige superar uma barreira energética entre energia volumétrica (driving force) e energia de interface. Nucleação heterogênea em defeitos ou contornos reduz drasticamente a barreira.',
      useFor: ['Controle de granulometria', 'Precipitação em ligas', 'Solidificação'],
      prerequisites: ['Energia livre de Gibbs', 'Energia de contorno de grão'],
      relatedTopics: ['Diagramas de fase', 'Defeitos cristalinos', 'Difusão termicamente ativada'],
      projectIdeas: ['Estimar raio crítico de núcleo para precipitação', 'Correlacionar taxa de resfriamento com tamanho de grão'],
      professorQuestions: [
        'Por que super-resfriamento é necessário para nucleação homogênea?',
        'Quais sítios preferenciais de nucleação você esperaria na sua microestrutura?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-grain-boundary-energy',
      title: 'Energia de contorno de grão',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Contornos de grão deixam de ser linhas em micrografia e passam a ser interfaces com energia, mobilidade e papel ativo na evolução microestrutural.',
      shortExplanation:
        'Contornos de grão possuem energia superficial γ_gb que impulsiona crescimento de grão, segregação e pinning por precipitados. A energia depende do desorientação e da estrutura do contorno.',
      useFor: ['Crescimento de grão', 'Modelagem de recristalização', 'Hall–Petch'],
      prerequisites: ['Cristalografia', 'Termodinâmica de interfaces'],
      relatedTopics: ['Hall–Petch', 'Nucleação', 'Defeitos cristalinos'],
      projectIdeas: ['Estimar taxa de crescimento de grão isotérmico', 'Simular pinning por partículas finas'],
      professorQuestions: [
        'Como a energia de contorno de alta ângulo difere da de baixa ângulo e qual a implicação para crescimento?',
        'Que evidência microscópica você usaria para confirmar migração de contornos?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-crystal-defects',
      title: 'Defeitos cristalinos como alavancas de propriedade',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Defeitos deixam de ser imperfeições indesejadas e passam a ser ferramentas: dislocações endurecem, vacâncias difundem, contornos refinem grão.',
      shortExplanation:
        'Vacâncias, intersticiais, dislocações, contornos de grão e empilhamentos planar alteram propriedades mecânicas, elétricas e difusivas. A densidade e tipo de defeito dependem do processamento.',
      useFor: ['Endurecimento por deformação', 'Análise de difusão', 'Interpretação de TEM'],
      prerequisites: ['Rede cristalina', 'Notação de dislocações'],
      relatedTopics: ['Hall–Petch', 'Difusão termicamente ativada', 'Dano por radiação'],
      projectIdeas: ['Contar densidade de dislocações em TEM', 'Correlacionar concentração de vacâncias com quench rate'],
      professorQuestions: [
        'Qual defeito domina o mecanismo de deformação na sua liga e em qual temperatura?',
        'Como você distinguir defeitos introduzidos por processamento de defeitos de serviço?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-thermally-activated-diffusion',
      title: 'Difusão termicamente ativada (Arrhenius)',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Conecta temperatura a taxas de processo — permite prever quanto tempo um tratamento leva ou quando um material envelhece.',
      shortExplanation:
        'Coeficientes de difusão seguem D = D₀ exp(−Q/RT). Pequenas variações de T produzem mudanças exponenciais na taxa de difusão e, portanto, na cinética de fase.',
      useFor: ['Tratamentos térmicos', 'Envelhecimento acelerado', 'Projeto de reator'],
      prerequisites: ['Lei de Fick', 'Equação de Arrhenius'],
      relatedTopics: ['Lei de Fick', 'Nucleação', 'Dano por radiação'],
      projectIdeas: ['Ajustar Q e D₀ a partir de perfis de difusão', 'Prever tempo de homogeneização a 900 °C vs. 1100 °C'],
      professorQuestions: [
        'Quais mecanismos de difusão competem na sua faixa de temperatura?',
        'Como você validaria Q experimentalmente sem assumir D₀ da literatura?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-radiation-damage',
      title: 'Dano por radiação em materiais',
      type: 'conceito-chave',
      level: 'pesquisa',
      whyItMatters:
        'Muda a perspectiva de materiais nucleares: radiação cria, move e aniquila defeitos — propriedades evoluem com fluência, não só com tempo.',
      shortExplanation:
        'Partículas energeticas deslocam átomos, criam cascatas de dano, vacâncias-intersticiais e transmutação. Acúmulo de defeitos leva a inchamento, endurecimento e amolecimento dependendo de T e microestrutura.',
      useFor: ['Materiais de reator', 'Blindagem', 'Avaliação de vida útil'],
      prerequisites: ['Defeitos cristalinos', 'Seção de choque nuclear'],
      relatedTopics: ['Defeitos cristalinos', 'Difusão termicamente ativada', 'Critério de Griffith'],
      projectIdeas: ['Revisar evolução de enduramento vs. fluência para Zr-liga', 'Simular cascata de dano com SRIM'],
      professorQuestions: [
        'Qual regime de recombinamento de defeitos você espera na temperatura de operação do seu material?',
        'Como você separaria efeitos de transmutação de efeitos de deslocamento?',
      ],
    }),
    definePowerIdea({
      id: 'materiais-ashby-plots',
      title: 'Diagramas de Ashby (seleção de materiais)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Permite comparar materiais em espaço de propriedades e identificar trade-offs — raciocínio de projeto sistemático em vez de escolha por hábito.',
      shortExplanation:
        'Diagramas de Ashby plotam propriedades (ex.: E vs. ρ, K_Ic vs. E) com contornos de índices de desempenho. Regiões ótimas e fronteiras de trade-off ficam visíveis.',
      useFor: ['Seleção preliminar de material', 'Identificação de trade-offs', 'Comunicação de projeto'],
      prerequisites: ['Propriedades mecânicas', 'Índices de desempenho'],
      relatedTopics: ['Triângulo estrutura–propriedade', 'Critério de Griffith', 'Hall–Petch'],
      projectIdeas: ['Plotar candidatos para estrutura leve em ρ–E', 'Definir índice de desempenho para eixo de turbina'],
      professorQuestions: [
        'Qual índice de desempenho você derivaria para o seu componente e por quê?',
        'Quando um diagrama de Ashby engana por ignorar fabricabilidade?',
      ],
    }),
  ],

  energia: [
    definePowerIdea({
      id: 'energia-exergy',
      title: 'Exergia e análise exergética',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Diferencia energia de qualidade — eficiência real depende de destruição de exergia, não só de balanço energético.',
      shortExplanation:
        'Exergia mede o máximo trabalho útil extraível de um fluxo em relação ao ambiente de referência. Perdas exergéticas localizam ineficiências termodinâmicas em processos e cadeias energéticas.',
      useFor: ['Auditoria de planta', 'Comparação de tecnologias', 'Otimização de processo'],
      prerequisites: ['Segunda lei da termodinâmica', 'Entropia'],
      relatedTopics: ['Ciclo de Carnot', 'LCA', 'Mix energético'],
      projectIdeas: ['Balanço exergético de uma caldeira', 'Comparar perdas exergéticas em solar térmico vs. fotovoltaico'],
      professorQuestions: [
        'Onde está a maior destruição de exergia no seu sistema e por quê?',
        'Como você define o ambiente de referência para análise exergética local?',
      ],
    }),
    definePowerIdea({
      id: 'energia-carnot',
      title: 'Limite de Carnot',
      type: 'teorema',
      level: 'basico',
      whyItMatters:
        'Estabelece o teto teórico de eficiência — qualquer motor real fica abaixo; guia expectativas e comparações.',
      shortExplanation:
        'A eficiência máxima de uma máquina térmica entre duas temperaturas T_quente e T_fria é η = 1 − T_fria/T_quente. É consequência da segunda lei e independe do fluido de trabalho.',
      useFor: ['Avaliação de ciclos térmicos', 'Comparação de tecnologias', 'Análise exergética'],
      prerequisites: ['Termodinâmica', 'Segunda lei'],
      relatedTopics: ['Exergia', 'Fator de capacidade', 'EROI'],
      projectIdeas: ['Calcular η_Carnot para ciclo Rankine a 600 °C', 'Comparar η real de turbina com limite de Carnot'],
      professorQuestions: [
        'Por que η_Carnot não é alcançável na prática e quais perdas dominam no seu ciclo?',
        'Como irreversibilidades reais se manifestam no diagrama T–s?',
      ],
    }),
    definePowerIdea({
      id: 'energia-lca',
      title: 'Análise de ciclo de vida (LCA)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Impede otimização local — emissões e impactos podem migrar para outra fase da cadeia se só olharmos operação.',
      shortExplanation:
        'LCA quantifica impactos ambientais (CO₂, água, eutrofização) desde extração de matéria-prima até fim de vida. Requer definição clara de fronteiras funcionais e unidade funcional.',
      useFor: ['Comparação de tecnologias', 'Política energética', 'Certificação ambiental'],
      prerequisites: ['Balanço de massa/energia', 'Inventários de emissão'],
      relatedTopics: ['EROI', 'Mix energético', 'Resiliência energética'],
      projectIdeas: ['LCA simplificado de painel FV vs. eólica', 'Sensibilidade de resultados LCA à fronteira do sistema'],
      professorQuestions: [
        'Qual unidade funcional você escolheu e como ela altera a conclusão?',
        'Quais incertezas do inventário dominam o resultado final?',
      ],
    }),
    definePowerIdea({
      id: 'energia-eroi',
      title: 'EROI (retorno energético sobre investimento)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Mede se uma fonte produz mais energia do que consome para existir — critério de viabilidade sistêmica além do custo financeiro.',
      shortExplanation:
        'EROI = energia entregue / energia investida (incluindo construção, manutenção, combustível). Fontes com EROI baixo limitam a complexidade social suportável pela energia disponível.',
      useFor: ['Avaliação de transição energética', 'Comparação de fontes', 'Política pública'],
      prerequisites: ['LCA energética', 'Balanço energético'],
      relatedTopics: ['LCA', 'Mix energético', 'Fator de capacidade'],
      projectIdeas: ['Estimar EROI de parque eólico offshore', 'Comparar EROI de biocombustíveis de 1ª vs. 2ª geração'],
      professorQuestions: [
        'Quais inputs energéticos você incluiu no denominador e por quê?',
        'Qual EROI mínimo sustenta a infraestrutura energética de uma economia complexa?',
      ],
    }),
    definePowerIdea({
      id: 'energia-dispatchability',
      title: 'Despachabilidade de fontes',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Renováveis variáveis e nucleares base-load têm papéis distintos — despachabilidade define quem responde à demanda.',
      shortExplanation:
        'Fonte despachável pode ajustar potência sob demanda (hidro com reservatório, térmica, baterias). Fontes não despacháveis (FV, eólica) dependem de recurso e exigem flexibilidade ou armazenamento.',
      useFor: ['Planejamento de rede', 'Integração de renováveis', 'Operação de mercado'],
      prerequisites: ['Curva de carga', 'Fator de capacidade'],
      relatedTopics: ['Armazenamento', 'Curva de carga', 'Mix energético'],
      projectIdeas: ['Simular despacho horário com FV + bateria', 'Quantificar necessidade de reserva flexível'],
      professorQuestions: [
        'Quem fornece flexibilidade quando FV e eólica caem simultaneamente?',
        'Como você quantifica o valor da despachabilidade no mercado?',
      ],
    }),
    definePowerIdea({
      id: 'energia-capacity-factor',
      title: 'Fator de capacidade',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Potência instalada não é energia entregue — fator de capacidade corrige expectativas de geração real.',
      shortExplanation:
        'FC = energia gerada / (potência nominal × tempo). Reflete disponibilidade do recurso, manutenção e curtailment. Nuclear ~90%, eólica onshore ~30–40%, FV ~15–25% (varia por região).',
      useFor: ['Planejamento de capacidade', 'Comparação de fontes', 'Análise econômica'],
      prerequisites: ['Potência vs. energia', 'Curva de carga'],
      relatedTopics: ['Despachabilidade', 'EROI', 'Armazenamento'],
      projectIdeas: ['Calcular FC histórico de usina local', 'Sensibilizar planejamento a FC de 25% vs. 35%'],
      professorQuestions: [
        'Como FC interage com custo nivelado (LCOE) na sua comparação?',
        'Quais fatores reduzem FC além da variabilidade do recurso?',
      ],
    }),
    definePowerIdea({
      id: 'energia-storage',
      title: 'Armazenamento de energia',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Armazenamento desacopla geração de consumo — habilita renováveis variáveis e resiliência.',
      shortExplanation:
        'Tecnologias (baterias, bombeamento, H₂, térmico) diferem em densidade, round-trip efficiency, tempo de descarga e custo. A escolha depende da aplicação: arbitragem, regulação ou backup.',
      useFor: ['Integração de renováveis', 'Microgrids', 'Despacho'],
      prerequisites: ['Curva de carga', 'Despachabilidade'],
      relatedTopics: ['Despachabilidade', 'Resiliência energética', 'Mix energético'],
      projectIdeas: ['Dimensionar bateria para perfil residencial + FV', 'Comparar round-trip efficiency Li-ion vs. bombeamento'],
      professorQuestions: [
        'Para qual serviço (energia vs. potência) você dimensionou o armazenamento?',
        'Como degradação cíclica altera a viabilidade econômica em 15 anos?',
      ],
    }),
    definePowerIdea({
      id: 'energia-load-curve',
      title: 'Curva de carga e perfil de demanda',
      type: 'ferramenta-computacional',
      level: 'basico',
      whyItMatters:
        'Sistemas energéticos são dimensionados pela demanda, não pela potência nominal das fontes — a curva de carga é o ponto de partida.',
      shortExplanation:
        'Curva de carga mostra demanda vs. tempo (hora, dia, estação). Picos, vales e fator de carga determinam necessidade de capacidade, armazenamento e despacho.',
      useFor: ['Dimensionamento de rede', 'Tarifação', 'Integração de renováveis'],
      prerequisites: ['Potência vs. energia', 'Estatística básica'],
      relatedTopics: ['Despachabilidade', 'Armazenamento', 'Resiliência energética'],
      projectIdeas: ['Plotar curva horária e calcular fator de carga', 'Identificar janela ideal para carregar baterias'],
      professorQuestions: [
        'Qual evento na curva de carga dita o dimensionamento do seu sistema?',
        'Como eficiência energética desloca a curva e reduz pico?',
      ],
    }),
    definePowerIdea({
      id: 'energia-resilience',
      title: 'Resiliência energética',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Confiabilidade não basta — resiliência mede capacidade de absorver perturbações e recuperar função crítica.',
      shortExplanation:
        'Resiliência inclui redundância, ilhas operacionais, armazenamento local e diversificação de fontes. Eventos extremos e ataques cibernéticos expõem vulnerabilidades de sistemas centralizados.',
      useFor: ['Microgrids', 'Infraestrutura crítica', 'Planejamento de emergência'],
      prerequisites: ['Curva de carga', 'Armazenamento'],
      relatedTopics: ['Armazenamento', 'Mix energético', 'Despachabilidade'],
      projectIdeas: ['Projeto de microgrid hospitalar com ilha', 'Análise de single points of failure na rede local'],
      professorQuestions: [
        'Quais cargas críticas devem ser atendidas em modo ilha e por quanto tempo?',
        'Como você quantifica resiliência além de SAIDI/SAIFI?',
      ],
    }),
    definePowerIdea({
      id: 'energia-mix-optimization',
      title: 'Otimização de mix energético',
      type: 'metodo',
      level: 'pesquisa',
      whyItMatters:
        'Não existe fonte ideal isolada — o mix ótimo equilibra custo, emissões, confiabilidade e restrições políticas.',
      shortExplanation:
        'Modelos de otimização (linear, estocástica) alocam capacidade e despacho minimizando custo ou emissões sob restrições de demanda, reserva e política. Incerteza de recurso e preço de carbono alteram soluções.',
      useFor: ['Planejamento de longo prazo', 'Política climática', 'Cenários de transição'],
      prerequisites: ['Despachabilidade', 'LCA', 'Programação linear'],
      relatedTopics: ['LCA', 'EROI', 'Despachabilidade', 'Resiliência energética'],
      projectIdeas: ['Modelo LP de mix para região com meta 2030', 'Sensibilidade a preço de carbono e FC de renováveis'],
      professorQuestions: [
        'Quais restrições políticas você incorporou e como elas mudam o ótimo?',
        'Como você trata incerteza de custo e recurso no modelo?',
      ],
    }),
  ],

  engenharia_fisica: [
    definePowerIdea({
      id: 'eng-fisica-dimensional-analysis',
      title: 'Análise dimensional',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Permite verificar equações, reduzir variáveis e descobrir grupos adimensionais antes de simular ou medir.',
      shortExplanation:
        'Teorema π de Buckingham reduz n variáveis com k dimensões a n−k grupos adimensionais. Consistência dimensional detecta erros e guia experimentos de escala.',
      useFor: ['Verificação de modelos', 'Design experimental', 'Similaridade dinâmica'],
      prerequisites: ['Unidades SI', 'Álgebra básica'],
      relatedTopics: ['Leis de escala', 'Propagação de erro', 'Hierarquia de modelagem'],
      projectIdeas: ['Derivar número de Reynolds por análise dimensional', 'Verificar consistência de equação de difusão'],
      professorQuestions: [
        'Quais variáveis você eliminou e qual a interpretação física do grupo adimensional resultante?',
        'Quando similaridade dinâmica completa é impossível, o que você sacrifica?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-scaling-laws',
      title: 'Leis de escala',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Conecta fenômenos em escalas diferentes — essencial para prototipagem, biologia e nanotecnologia.',
      shortExplanation:
        'Leis de potência relacionam quantidades quando uma escala muda (ex.: área ∝ L², volume ∝ L³). Efeitos dominantes mudam com escala — gravidade vs. tensão superficial, inércia vs. viscosidade.',
      useFor: ['Prototipagem', 'Micro/nanofabricação', 'Biomecânica'],
      prerequisites: ['Análise dimensional', 'Ordens de grandeza'],
      relatedTopics: ['Análise dimensional', 'Pensamento sistêmico', 'Hierarquia de modelagem'],
      projectIdeas: ['Comparar Reynolds em modelo reduzido vs. full-scale', 'Estimar limite de escala para efeito capilar'],
      professorQuestions: [
        'Qual efeito físico emerge na sua escala alvo que não aparece no protótipo?',
        'Como você compensa violação de similaridade em ensaio de túnel?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-instrumentation-chain',
      title: 'Cadeia de instrumentação',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Medição é um sistema — sensor, condicionamento, aquisição e display; falha em qualquer elo corrompe o resultado.',
      shortExplanation:
        'Cadeia típica: fenômeno → transdutor → sinal elétrico → amplificação/filtro → ADC → software. Cada estágio introduz ganho, ruído, não-linearidade e latência.',
      useFor: ['Projeto de experimento', 'Diagnóstico de ruído', 'Calibração'],
      prerequisites: ['Circuitos básicos', 'Sensores'],
      relatedTopics: ['Propagação de erro', 'SNR', 'Função de transferência'],
      projectIdeas: ['Diagrama de blocos de cadeia para termopar', 'Estimar SNR end-to-end'],
      professorQuestions: [
        'Qual elo da cadeia limita resolução efetiva no seu setup?',
        'Como você isolar se o ruído vem do sensor ou do ADC?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-error-propagation',
      title: 'Propagação de incerteza',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Resultado sem incerteza é incompleto — propagação quantifica confiança e identifica medições críticas.',
      shortExplanation:
        'Para f(x₁,…,xₙ), incerteza combinada usa derivadas parciais: u_c² = Σ(∂f/∂xᵢ)²u(xᵢ)². Correlações entre variáveis devem ser incluídas quando presentes.',
      useFor: ['Análise de experimento', 'Relatório metrológico', 'Validação de modelo'],
      prerequisites: ['Derivadas parciais', 'Estatística básica'],
      relatedTopics: ['Incerteza de medição', 'Calibração', 'Análise dimensional'],
      projectIdeas: ['Propagar incerteza em cálculo de Reynolds', 'Identificar variável que mais contribui para u_c'],
      professorQuestions: [
        'Quais termos de correlação você incluiu e por quê?',
        'Como incerteza de calibração se propaga até sua conclusão final?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-systems-thinking',
      title: 'Pensamento sistêmico',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Sistemas físicos têm retroalimentação, atrasos e emergência — otimizar partes pode piorar o todo.',
      shortExplanation:
        'Pensamento sistêmico mapeia stocks, fluxos, loops de feedback e delays. Comportamento global pode contradizer intuição linear — overshoot, oscilação e lock-in são comuns.',
      useFor: ['Projeto de controle', 'Análise de falha', 'Política tecnológica'],
      prerequisites: ['Diagramas de blocos', 'Equações diferenciais'],
      relatedTopics: ['Realimentação', 'Hierarquia de modelagem', 'Leis de escala'],
      projectIdeas: ['Diagrama causal de sistema térmico acoplado', 'Identificar loop de realimentação positiva em runaway'],
      professorQuestions: [
        'Quais delays no seu sistema causam instabilidade aparente?',
        'Onde otimização local produz efeito contrário no sistema global?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-feedback',
      title: 'Realimentação (feedback)',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Feedback explica estabilidade, oscilação e controle — base de instrumentação, eletrônica e dinâmica.',
      shortExplanation:
        'Realimentação negativa reduz erro e estabiliza; positiva amplifica e pode levar a instabilidade. Ganho em loop aberto, margem de fase e bandwidth definem desempenho de controle.',
      useFor: ['Controle de processo', 'Estabilização de instrumento', 'Eletrônica analógica'],
      prerequisites: ['Transformada de Laplace', 'Função de transferência'],
      relatedTopics: ['Processamento de sinal', 'Cadeia de instrumentação', 'Pensamento sistêmico'],
      projectIdeas: ['Projeto de controlador PI para temperatura', 'Medir margem de fase de amplificador operacional'],
      professorQuestions: [
        'O que limita bandwidth do seu loop de realimentação?',
        'Como você distinguir instabilidade por atraso de fase vs. ganho excessivo?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-signal-processing',
      title: 'Fundamentos de processamento de sinal',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Sinais medidos são amostrados, filtrados e transformados — processamento define o que você realmente observa.',
      shortExplanation:
        'Conceitos centrais: amostragem (Nyquist), filtragem (passa-baixa/alta), FFT para domínio de frequência e convolução. Aliasing e leakage distorcem espectros se mal tratados.',
      useFor: ['Análise vibracional', 'Filtragem de ruído', 'Espectroscopia'],
      prerequisites: ['Fourier', 'Cadeia de instrumentação'],
      relatedTopics: ['Nyquist-Shannon', 'Filtragem', 'SNR'],
      projectIdeas: ['Filtrar sinal ruidoso e comparar domínios tempo/frequência', 'Detectar aliasing em taxa de amostragem insuficiente'],
      professorQuestions: [
        'Qual janela FFT você usou e como ela afeta resolução espectral?',
        'Como você escolheu cutoff do filtro sem distorcer o fenômeno físico?',
      ],
    }),
    definePowerIdea({
      id: 'eng-fisica-modeling-hierarchy',
      title: 'Hierarquia de modelagem',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Modelo certo depende da pergunta — usar Navier-Stokes quando Bernoulli basta desperdiça esforço; usar Bernoulli quando turbulência domina engana.',
      shortExplanation:
        'Modelos formam hierarquia de fidelidade: analítico → lumped → numérico → multiescala. Escolha guiada por números adimensionais, incerteza aceitável e custo computacional.',
      useFor: ['Simulação', 'Validação experimental', 'Projeto preliminar'],
      prerequisites: ['Análise dimensional', 'Métodos numéricos básicos'],
      relatedTopics: ['Leis de escala', 'Pensamento sistêmico', 'Propagação de erro'],
      projectIdeas: ['Justificar modelo 0D vs. 3D para trocador de calor', 'Estimar erro de modelo lumped vs. medição'],
      professorQuestions: [
        'Qual fenômeno seu modelo ignora e isso invalida a conclusão?',
        'Como você validaria o modelo sem ajustar parâmetros post hoc?',
      ],
    }),
  ],

  instrumentacao: [
    definePowerIdea({
      id: 'instrumentacao-nyquist-shannon',
      title: 'Teorema de Nyquist–Shannon',
      type: 'teorema',
      level: 'intermediario',
      whyItMatters:
        'Define taxa mínima de amostragem — subamostrar destrói informação irreversivelmente via aliasing.',
      shortExplanation:
        'Para reconstruir um sinal limitado em banda B, amostre a ≥ 2B (Hz). Violação produz aliasing: frequências altas aparecem disfarçadas de baixas.',
      useFor: ['Aquisição de dados', 'Áudio/digitalização', 'Osciloscopia'],
      prerequisites: ['Transformada de Fourier', 'Frequência de corte'],
      relatedTopics: ['Filtragem', 'SNR', 'Função de transferência'],
      projectIdeas: ['Demonstrar aliasing com senoide e fs insuficiente', 'Dimensionar taxa de aquisição para sinal vibracional'],
      professorQuestions: [
        'Qual a banda efetiva do seu sinal e como você a estimou antes de escolher fs?',
        'Como filtro anti-aliasing interage com resposta do sensor?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-snr',
      title: 'Relação sinal-ruído (SNR)',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Medição útil exige sinal distinguível de ruído — SNR quantifica limite de detecção e resolução efetiva.',
      shortExplanation:
        'SNR = potência do sinal / potência do ruído (often em dB). Ruído térmico, shot noise, flicker e interferência limitam sensibilidade. Média e filtragem melhoram SNR à custa de bandwidth ou tempo.',
      useFor: ['Projeto de detector', 'Otimização de integração', 'Validação de medição'],
      prerequisites: ['Estatística', 'Cadeia de instrumentação'],
      relatedTopics: ['Ruído térmico', 'Filtragem', 'Incerteza de medição'],
      projectIdeas: ['Medir SNR de fotodiodo vs. tempo de integração', 'Comparar SNR antes e depois de filtro passa-banda'],
      professorQuestions: [
        'Qual fonte de ruído domina no seu experimento e é evitável?',
        'Quanto de SNR você precisa para sua incerteza alvo?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-calibration',
      title: 'Calibração de instrumentos',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Instrumento sem calibração produz números, não grandezas — calibração liga leitura a referência rastreável.',
      shortExplanation:
        'Calibração estabelece relação entre indicação e valor verdadeiro usando padrões. Inclui ajuste, verificação de linearidade, deriva temporal e documentação de incerteza.',
      useFor: ['Laboratório acreditado', 'Controle de qualidade', 'Experimento quantitativo'],
      prerequisites: ['Incerteza de medição', 'Padrões de referência'],
      relatedTopics: ['Rastreabilidade', 'Resolução vs. precisão', 'Incerteza de medição'],
      projectIdeas: ['Curva de calibração para sensor de pressão', 'Estimar deriva entre calibrações'],
      professorQuestions: [
        'Qual padrão você usou e qual a incerteza propagada até sua medição?',
        'Com que frequência recalibrar dado o ambiente do seu laboratório?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-traceability',
      title: 'Rastreabilidade metrológica',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Comparabilidade internacional exige cadeia ininterrupta até padrões primários — sem rastreabilidade, resultados não são auditáveis.',
      shortExplanation:
        'Rastreabilidade documenta ligação a padrões nacionais/internacionais (BIPM, INMETRO) via calibrações encadeadas. Cada elo contribui incerteza acumulada.',
      useFor: ['Acreditação ISO 17025', 'Indústria regulada', 'Publicação experimental'],
      prerequisites: ['Calibração', 'Incerteza de medição'],
      relatedTopics: ['Calibração', 'Incerteza de medição', 'QA em metrologia'],
      projectIdeas: ['Montar árvore de rastreabilidade para balança analítica', 'Calcular incerteza expandida da cadeia'],
      professorQuestions: [
        'Onde a cadeia de rastreabilidade do seu lab quebra ou é assumida?',
        'Como você trataria calibração interlaboratorial vs. rastreabilidade formal?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-resolution-precision',
      title: 'Resolução vs. precisão',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Display com muitos dígitos não implica medição precisa — confundir resolução e precisão leva a conclusões falsas.',
      shortExplanation:
        'Resolução é o menor incremento detectável; precisão é proximidade do valor verdadeiro; exatidão inclui tendência sistemática. Repetibilidade mede dispersão em condições fixas.',
      useFor: ['Seleção de instrumento', 'Interpretação de dados', 'Relatório experimental'],
      prerequisites: ['Estatística descritiva', 'Calibração'],
      relatedTopics: ['Incerteza de medição', 'Calibração', 'SNR'],
      projectIdeas: ['Série de medições repetidas para repetibilidade vs. resolução nominal', 'Identificar tendência sistemática pós-calibração'],
      professorQuestions: [
        'Seu instrumento é repetível mas impreciso — o que você corrigiria primeiro?',
        'Como resolução do ADC limita incerteza tipo A?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-transfer-function',
      title: 'Função de transferência',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Instrumento distorce sinal no domínio da frequência — função de transferência quantifica ganho e fase vs. frequência.',
      shortExplanation:
        'H(s) ou H(jω) relaciona entrada e saída. Pólos e zeros determinam resposta temporal e bandwidth. Sensores de 1ª ordem têm constante de tempo τ = 1/(2πf_c).',
      useFor: ['Caracterização de sensor', 'Correção de resposta', 'Controle'],
      prerequisites: ['Transformada de Laplace', 'Realimentação'],
      relatedTopics: ['Filtragem', 'Nyquist-Shannon', 'Cadeia de instrumentação'],
      projectIdeas: ['Medir resposta em frequência de acelerômetro', 'Corrigir atraso de fase em dado dinâmico'],
      professorQuestions: [
        'Qual a bandwidth do seu sensor relativa à frequência do fenômeno?',
        'Como atraso de fase distorce medição de amplitude em regime dinâmico?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-thermal-noise',
      title: 'Ruído térmico (Johnson–Nyquist)',
      type: 'lei',
      level: 'avancado',
      whyItMatters:
        'Todo resistor gera ruído — limite fundamental em detectores de baixo sinal e amplificadores.',
      shortExplanation:
        'Densidade espectral de tensão: v_n² = 4k_B T R (V²/Hz). Ruído térmico define floor de SNR e orienta escolha de impedância e temperatura de operação.',
      useFor: ['Projeto de front-end', 'Detectores cryogênicos', 'Estimativa de limite de detecção'],
      prerequisites: ['Estatística', 'Circuitos'],
      relatedTopics: ['SNR', 'Filtragem', 'Espectroscopia'],
      projectIdeas: ['Calcular ruído térmico em 50 Ω a 300 K vs. 77 K', 'Comparar com ruído medido em pré-amplificador'],
      professorQuestions: [
        'Ruído térmico ou shot noise domina no seu detector?',
        'Como redução de temperatura melhora limite de detecção quantitativamente?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-filtering',
      title: 'Filtragem de sinais',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Filtro extrai informação relevante e rejeita ruído — escolha errada distorce o fenômeno físico.',
      shortExplanation:
        'Filtros analógicos/digitais (Butterworth, Chebyshev, FIR/IIR) diferem em ripple, fase e ordem. Cutoff, rolloff e transient response devem ser compatíveis com banda do sinal.',
      useFor: ['Condicionamento de sinal', 'Anti-aliasing', 'Análise vibracional'],
      prerequisites: ['Processamento de sinal', 'Função de transferência'],
      relatedTopics: ['Nyquist-Shannon', 'SNR', 'Espectroscopia'],
      projectIdeas: ['Projeto de filtro passa-banda para linha espectral', 'Comparar distorção de fase FIR vs. IIR'],
      professorQuestions: [
        'Seu filtro altera amplitude do harmônico de interesse?',
        'Como você validou cutoff sem assumir resposta ideal?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-measurement-uncertainty',
      title: 'Incerteza de medição (GUM)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Resultado científico requer incerteza declarada — GUM padroniza avaliação tipo A e tipo B.',
      shortExplanation:
        'Incerteza tipo A vem de estatística de repetições; tipo B de fontes não estatísticas (calibração, resolução, deriva). Incerteza expandida U = k·u_c com fator k (tipicamente 2).',
      useFor: ['Relatório experimental', 'Acreditação', 'Comparação interlaboratorial'],
      prerequisites: ['Propagação de erro', 'Estatística'],
      relatedTopics: ['Calibração', 'Rastreabilidade', 'Resolução vs. precisão'],
      projectIdeas: ['Orçamento de incerteza para medição de temperatura', 'Separar contribuições tipo A e B'],
      professorQuestions: [
        'Qual contribuição domina seu orçamento de incerteza?',
        'Por que k=2 e o que significa para intervalo de confiança?',
      ],
    }),
    definePowerIdea({
      id: 'instrumentacao-spectroscopy',
      title: 'Princípios de espectroscopia',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Espectroscopia liga interação radiação–matéria a composição e estrutura — ferramenta universal em física, química e materiais.',
      shortExplanation:
        'Técnicas (UV-Vis, IR, Raman, NMR, XPS) diferem em sonda, seleção de regra, resolução e ambiente. Intensidade vs. frequência/deslocamento químico identifica espécies e ligações.',
      useFor: ['Caracterização molecular', 'Controle de qualidade', 'Diagnóstico de material'],
      prerequisites: ['Quântica básica', 'Interação eletromagnética'],
      relatedTopics: ['SNR', 'Filtragem', 'Calibração'],
      projectIdeas: ['Identificar picos IR de polímero desconhecido', 'Estimar resolução espectral necessária para separar picos'],
      professorQuestions: [
        'Qual regra de seleção permite ou proíbe a transição que você observa?',
        'Como artefatos de baseline e saturacao distorcem sua interpretação?',
      ],
    }),
  ],

  biotecnologia: [
    definePowerIdea({
      id: 'biotech-central-dogma-applied',
      title: 'Dogma central aplicado à biotecnologia',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'DNA→RNA→proteína é o mapa de onde intervenir — engenharia genética, expressão e análise seguem esse fluxo.',
      shortExplanation:
        'Manipular genes altera mRNA e proteínas; reguladores controlam expressão; retrotranscrição e edição (CRISPR) estendem o fluxo. Falhas em qualquer etapa explicam fenótipo inesperado.',
      useFor: ['Clonagem', 'Expressão recombinante', 'Diagnóstico molecular'],
      prerequisites: ['Biologia molecular', 'Genética básica'],
      relatedTopics: ['Cinética de crescimento', 'Biorreator', 'QbD'],
      projectIdeas: ['Diagrama fluxo expressão de proteína recombinante', 'Prever efeito de promotor fraco vs. forte'],
      professorQuestions: [
        'Onde no fluxo central está o gargalo da sua linhagem?',
        'Como você confirmaria expressão além de mRNA (proteína funcional)?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-growth-kinetics',
      title: 'Cinética de crescimento microbiano',
      type: 'lei',
      level: 'intermediario',
      whyItMatters:
        'Crescimento determina produtividade — modelos cinéticos preveem quando colher e como operar biorreator.',
      shortExplanation:
        'Modelo de Monod relaciona taxa específica μ a concentração de substrato. Fases lag, exponencial, estacionária e morte têm implicações distintas para escala e produto.',
      useFor: ['Otimização de fermentação', 'Scale-up', 'Balanço de massa'],
      prerequisites: ['Equações diferenciais', 'Balanço de massa'],
      relatedTopics: ['Biorreator', 'Scale-up', 'Esterilização'],
      projectIdeas: ['Ajustar parâmetros μ_max e K_s a curva de crescimento', 'Prever tempo até fase estacionária'],
      professorQuestions: [
        'Qual fase domina produtividade do seu produto secundário?',
        'Como inibição por substrato ou produto altera Monod na prática?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-bioreactor-mass-balance',
      title: 'Balanço de massa em biorreatores',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Biorreator é sistema de fluxo — balanço de massa quantifica produção, consumo e acúmulo.',
      shortExplanation:
        'Equação geral: acúmulo = entrada − saída + geração − consumo. Em batch, fed-batch e contínuo as equações diferem. Oxigênio dissolvido e substrato são variáveis críticas.',
      useFor: ['Dimensionamento', 'Controle de processo', 'Scale-up'],
      prerequisites: ['Cinética de crescimento', 'Engenharia química básica'],
      relatedTopics: ['Cinética de crescimento', 'Scale-up', 'QbD'],
      projectIdeas: ['Balanço de substrato em fed-batch simulado', 'Estimar q_p a partir de dados de produção'],
      professorQuestions: [
        'Quais termos do balanço você não consegue medir diretamente?',
        'Como transferência de oxigênio limita seu balanço em escala?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-sterilization',
      title: 'Esterilização e controle de contaminação',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Contaminação destrói batch inteiro — esterilização in situ (SIP) e assepsia são requisitos não negociáveis.',
      shortExplanation:
        'Esterilização por vapor (121 °C, 15 min), filtração 0,22 μm e agentes químicos eliminam microrganismos. F₀ e validação térmica quantificam eficácia. Contaminação cruzada exige isolamento.',
      useFor: ['Setup de fermentação', 'Validação de processo', 'Biossegurança'],
      prerequisites: ['Microbiologia', 'Transferência de calor'],
      relatedTopics: ['Biorreator', 'Validação de ensaio', 'Biossegurança'],
      projectIdeas: ['Calcular F₀ para ciclo SIP', 'Plano de amostragem ambiental para contaminação'],
      professorQuestions: [
        'Como você validaria esterilização sem cultivo positivo?',
        'Qual vetor de contaminação é mais provável no seu processo?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-qbd',
      title: 'Quality by Design (QbD)',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'Qualidade embutida no desenho do processo, não inspecionada no final — paradigma regulatório em biofarma.',
      shortExplanation:
        'QbD identifica CPPs (parâmetros críticos) e CQAs (atributos críticos de qualidade), mapeia design space e controla risco. DoE e PAT suportam compreensão do processo.',
      useFor: ['Desenvolvimento de biológicos', 'Submissão regulatória', 'Transferência de tecnologia'],
      prerequisites: ['Validação de ensaio', 'Estatística experimental'],
      relatedTopics: ['Validação de ensaio', 'Scale-up', 'Biorreator'],
      projectIdeas: ['Matriz de risco CPP→CQA para fermentação', 'Design space para temperatura e pH'],
      professorQuestions: [
        'Quais CPPs você identificou e como os ligou a CQAs?',
        'O que acontece se operar fora do design space aprovado?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-assay-validation',
      title: 'Validação de ensaios analíticos',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Dado de processo e produto só vale se o ensaio for confiável — validação define linearidade, precisão, exatidão e robustez.',
      shortExplanation:
        'ICH Q2(R2) guia validação: especificidade, linearidade, range, LOD/LOQ, precisão, exatidão e robustez. Ensaios de potência e pureza exigem critérios de aceitação documentados.',
      useFor: ['Controle de qualidade', 'Liberação de lote', 'Desenvolvimento analítico'],
      prerequisites: ['Estatística', 'Bioquímica analítica'],
      relatedTopics: ['QbD', 'Scale-up', 'Esterilização'],
      projectIdeas: ['Protocolo de validação para ELISA de título', 'Estudo de robustez variando pH do tampão'],
      professorQuestions: [
        'Qual parâmetro de validação falhou no seu ensaio e qual a causa raiz?',
        'Como você distingue variabilidade do ensaio da variabilidade do processo?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-scale-up',
      title: 'Scale-up de processos biológicos',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'O que funciona em shake flask falha em 10 000 L — scale-up preserva critérios adimensionais e ambiente celular.',
      shortExplanation:
        'Critérios de similaridade (k_L a, P/V, tempo de mistura) mantêm condições equivalentes. Limites de OTR, cisalhamento e gradientes de substrato causam perda de produtividade.',
      useFor: ['Transferência piloto→planta', 'Otimização industrial', 'Troubleshooting'],
      prerequisites: ['Biorreator', 'Cinética de crescimento'],
      relatedTopics: ['Balanço de massa', 'QbD', 'Biossegurança'],
      projectIdeas: ['Calcular P/V equivalente entre 5 L e 500 L', 'Identificar limitante de OTR em escala'],
      professorQuestions: [
        'Qual critério adimensional você priorizou e o que sacrificou?',
        'Como gradientes de nutriente explicam queda de título em escala?',
      ],
    }),
    definePowerIdea({
      id: 'biotech-biosafety',
      title: 'Biossegurança em biotecnologia',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Organismos modificados e patógenos exigem contenção — biossegurança protege trabalhadores, comunidade e meio ambiente.',
      shortExplanation:
        'Níveis de biossegurança (BSL 1–4), engenharia de contenção, EPI e práticas administrativas compõem barreiras. Avaliação de risco biológico precede manipulação de OGM.',
      useFor: ['Projeto de laboratório', 'Aprovação ética/regulatória', 'Resposta a incidentes'],
      prerequisites: ['Microbiologia', 'Ética em pesquisa'],
      relatedTopics: ['Esterilização', 'Scale-up', 'QbD'],
      projectIdeas: ['Avaliação de risco para linhagem recombinante', 'Plano de resposta a derrame biológico'],
      professorQuestions: [
        'Qual nível BSL sua linhagem exige e qual a justificativa?',
        'Como você auditaria conformidade de contenção no dia a dia?',
      ],
    }),
  ],

  engenharia_defesa: [
    definePowerIdea({
      id: 'defesa-ooda-loop',
      title: 'Ciclo OODA (Observe–Orient–Decide–Act)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Decisão em ambiente contestado exige ciclo mais rápido que o adversário — OODA estrutura observação, orientação, decisão e ação.',
      shortExplanation:
        'Desenvolvido por Boyd, o loop OODA enfatiza orientação (modelo mental) como gargalo. Ciclos mais curtos que o oponente geram vantagem tática e estratégica.',
      useFor: ['Comando e controle', 'Simulação de cenários', 'Projeto de sistemas de alerta'],
      prerequisites: ['Teoria de decisão', 'Sistemas de informação'],
      relatedTopics: ['C4ISR', 'Modelagem de ameaças', 'Guerra eletrônica'],
      projectIdeas: ['Mapear latências OODA em cenário simulado', 'Identificar gargalo de orientação em fluxo de dados'],
      professorQuestions: [
        'Onde seu sistema perde tempo no loop OODA?',
        'Como dados incorretos na fase Orient distorcem decisão?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-ew-basics',
      title: 'Fundamentos de guerra eletrônica (EW)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Espectro eletromagnético é domínio de combate — EW protege, ataca e engana via radar, comunicações e navegação.',
      shortExplanation:
        'EW divide-se em ES (suporte: detecção), EA (ataque: jamming, spoofing) e EP (proteção: ECCM). Link budget e assinatura RCS determinam detectabilidade e vulnerabilidade.',
      useFor: ['Projeto de contramedidas', 'Análise de vulnerabilidade', 'Integração sensorial'],
      prerequisites: ['RF básico', 'Radar'],
      relatedTopics: ['C4ISR', 'Sobrevivência', 'Orçamento de link'],
      projectIdeas: ['Estimar alcance de jamming vs. potência ERP', 'Matriz de vulnerabilidade EW por banda'],
      professorQuestions: [
        'Qual assinatura EM seu sistema expõe e como reduzi-la?',
        'Jamming barragem vs. spot: trade-off no seu cenário?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-survivability',
      title: 'Sobrevivência de sistemas militares',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Plataforma deve completar missão sob dano — sobrevivência integra proteção, redundância e recuperação.',
      shortExplanation:
        'Sobrevivência inclui susceptibilidade (probabilidade de acerto), vulnerabilidade (dano dado acerto) e recuperabilidade. Kill chain do adversário orienta contramedidas em cada etapa.',
      useFor: ['Projeto de blindagem', 'Arquitetura redundante', 'Avaliação de ameaça'],
      prerequisites: ['Probabilidade', 'Engenharia de sistemas'],
      relatedTopics: ['Modelagem de ameaças', 'Guerra eletrônica', 'Test & evaluation'],
      projectIdeas: ['Análise susceptibilidade–vulnerabilidade para UAV', 'Projeto de redundância tripla em aviônica crítica'],
      professorQuestions: [
        'Qual etapa da kill chain você ataca para maximizar sobrevivência?',
        'Como quantificar trade-off entre massa de blindagem e mobilidade?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-c4isr',
      title: 'C4ISR — comando, controle, comunicações, computadores, ISR',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Superioridade informacional depende de integrar sensores, redes e decisão — C4ISR é a espinha dorsal operacional.',
      shortExplanation:
        'C4ISR conecta coleta (ISR), processamento, disseminação e comando. Latência, interoperabilidade e segurança cibernética determinam eficácia. Data fusion reduz ambiguidade tática.',
      useFor: ['Arquitetura de sistemas', 'Integração de sensores', 'Planejamento operacional'],
      prerequisites: ['Redes', 'Processamento de sinal'],
      relatedTopics: ['OODA loop', 'Rastreabilidade de requisitos', 'Guerra eletrônica'],
      projectIdeas: ['Diagrama C4ISR para cenário multi-domínio', 'Análise de latência fim-a-fim sensor→decisor'],
      professorQuestions: [
        'Onde interoperabilidade falha entre sistemas legados e novos?',
        'Como você protege C4ISR contra ciberataque sem degradar latência?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-threat-modeling',
      title: 'Modelagem de ameaças',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Projeto defensivo requer adversário explícito — modelagem de ameaças estrutura capacidades, intenções e vetores.',
      shortExplanation:
        'Identifica atores, capacidades (mísseis, ciber, EW), cenários e probabilidades. STRIDE e kill chain adaptam-se a sistemas físicos e cibernéticos. Mitigações mapeiam a cada ameaça.',
      useFor: ['Análise de risco', 'Projeto de contramedidas', 'Priorização de investimento'],
      prerequisites: ['Engenharia de sistemas', 'Probabilidade'],
      relatedTopics: ['Sobrevivência', 'C4ISR', 'Test & evaluation'],
      projectIdeas: ['Matriz ameaça×mitigação para instalação crítica', 'Cenário red team vs. blue team documentado'],
      professorQuestions: [
        'Qual ameaça você subestimou por viés de cenário recente?',
        'Como validar modelo de ameaça sem revelar classificação?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-systems-engineering-v',
      title: 'Modelo V de engenharia de sistemas',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Sistemas complexos de defesa exigem rastreabilidade requisito→projeto→teste — modelo V formaliza essa ligação.',
      shortExplanation:
        'Lado esquerdo: decomposição de requisitos em projeto; lado direito: integração e verificação/validação ascendente. Cada nível de teste (unidade, integração, sistema, aceitação) valida artefatos correspondentes.',
      useFor: ['Programas de aquisição', 'Gestão de requisitos', 'Test & evaluation'],
      prerequisites: ['Engenharia de requisitos', 'Gestão de projetos'],
      relatedTopics: ['Rastreabilidade de requisitos', 'Test & evaluation', 'C4ISR'],
      projectIdeas: ['Diagrama V para subsistema de navegação', 'Matriz requisito→caso de teste'],
      professorQuestions: [
        'Qual nível do V falhou primeiro no seu programa e por quê?',
        'Como requisitos emergentes alteram a rastreabilidade?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-requirements-traceability',
      title: 'Rastreabilidade de requisitos',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Requisito sem rastreio até teste é wishful thinking — rastreabilidade prova que o sistema faz o que foi pedido.',
      shortExplanation:
        'Matriz bidirecional liga requisitos de missão a especificações, design, código e casos de teste. Mudanças propagam impacto. Ferramentas (DOORS, Jama) gerenciam versões.',
      useFor: ['Auditoria de programa', 'Gestão de mudanças', 'Certificação'],
      prerequisites: ['Engenharia de requisitos', 'Modelo V'],
      relatedTopics: ['Modelo V', 'Test & evaluation', 'C4ISR'],
      projectIdeas: ['Matriz rastreabilidade para 20 requisitos críticos', 'Análise de impacto de mudança de requisito'],
      professorQuestions: [
        'Quais requisitos não têm teste associado no seu baseline?',
        'Como requisitos derivados se distinguem de alocados?',
      ],
    }),
    definePowerIdea({
      id: 'defesa-test-evaluation',
      title: 'Test & Evaluation (T&E)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Sistema só é confiável após teste rigoroso — T&E valida desempenho operacional em condições representativas.',
      shortExplanation:
        'T&E inclui teste de desenvolvimento, qualificação, operacional (OT) e aceitação. Condições limite, cenários de stress e métricas de eficácia (MOE) vs. desempenho (MOP) guiam avaliação.',
      useFor: ['Qualificação de sistema', 'Relatório de aceitação', 'Melhoria iterativa'],
      prerequisites: ['Estatística experimental', 'Modelo V'],
      relatedTopics: ['Rastreabilidade de requisitos', 'Sobrevivência', 'Modelagem de ameaças'],
      projectIdeas: ['Plano OT para sistema de comunicação táctico', 'Definir MOE/MOP para missão de reconhecimento'],
      professorQuestions: [
        'Seu teste representa condição operacional ou apenas nominal?',
        'Como incerteza estatística afeta conclusão de aceitação?',
      ],
    }),
  ],

  espaco: [
    definePowerIdea({
      id: 'espaco-kepler',
      title: 'Leis de Kepler do movimento orbital',
      type: 'lei',
      level: 'basico',
      whyItMatters:
        'Órbitas deixam de ser misteriosas — Kepler reduz movimento planetário a geometria elíptica e leis de áreas e períodos.',
      shortExplanation:
        'Órbitas são elipses com o corpo central em um foco; raio vetor varre áreas iguais em tempos iguais; T² ∝ a³. Base para mecânica orbital moderna e planejamento de missão.',
      useFor: ['Design orbital preliminar', 'Previsão de posição', 'Transferências'],
      prerequisites: ['Mecânica clássica', 'Gravitão newtoniana'],
      relatedTopics: ['Vis-viva', 'Hohmann', 'Perturbações orbitais'],
      projectIdeas: ['Calcular período orbital da ISS', 'Plotar elipse orbital dado a e e'],
      professorQuestions: [
        'Como excentricidade afeta tempo de permanência em apogeu vs. perigeu?',
        'Quando aproximação kepleriana falha no seu regime orbital?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-vis-viva',
      title: 'Equação vis-viva',
      type: 'identidade-matematica',
      level: 'intermediario',
      whyItMatters:
        'Energia específica determina forma orbital — vis-viva liga velocidade, raio e semieixo sem integrar equações de movimento.',
      shortExplanation:
        'v² = μ(2/r − 1/a), onde μ = GM e a é semieixo maior. Permite calcular velocidade em qualquer ponto da órbita e energia total E = −μ/(2a).',
      useFor: ['Manobras orbitais', 'Análise de colisão', 'Rendezvous'],
      prerequisites: ['Leis de Kepler', 'Energia mecânica'],
      relatedTopics: ['Kepler', 'Hohmann', 'Janelas de lançamento'],
      projectIdeas: ['Calcular Δv para circularizar em perigeu', 'Comparar energia de órbitas LEO vs. GEO'],
      professorQuestions: [
        'Como vis-viva se altera após impulso tangencial infinitesimal?',
        'Qual a interpretação física de E negativa em órbita ligada?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-hohmann',
      title: 'Transferência de Hohmann',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Manobra clássica de mínima energia entre órbitas coplanares — referência para missões interplanetárias e GEO.',
      shortExplanation:
        'Dois impulsos tangenciais: elipse de transferência tangente à órbita inicial e final. Δv total mínimo para transferência coplanar entre círculos.',
      useFor: ['Transferência LEO→GEO', 'Missões a Marte', 'Planejamento Δv budget'],
      prerequisites: ['Vis-viva', 'Kepler'],
      relatedTopics: ['Janelas de lançamento', 'Perturbações orbitais', 'Tsiolkovsky'],
      projectIdeas: ['Calcular Δv LEO 400 km → GEO', 'Comparar Hohmann vs. transferência bi-elíptica'],
      professorQuestions: [
        'Quando bi-elíptica supera Hohmann apesar de tempo maior?',
        'Como inclinação orbital aumenta Δv além do Hohmann coplanar?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-launch-windows',
      title: 'Janelas de lançamento',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Alinhamento Terra–alvo é efêmero — janelas limitam quando lançar para interceptar planeta ou estação.',
      shortExplanation:
        'Janela de lançamento depende de geometria orbital, inclinação e fase. Missões interplanetárias usam período sinódico; rendezvous exige coincidência de fase e plano.',
      useFor: ['Missões interplanetárias', 'Rendezvous ISS', 'Planejamento de campanha'],
      prerequisites: ['Hohmann', 'Mecânica orbital'],
      relatedTopics: ['Hohmann', 'Perturbações orbitais', 'Orçamento de link'],
      projectIdeas: ['Calcular janela para transferência Terra–Marte', 'Sensibilidade de erro de lançamento à missão'],
      professorQuestions: [
        'Quanto erro na hora de lançamento seu Δv de correção tolera?',
        'Como inclinação do plano de lançamento restringe janela?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-orbital-perturbations',
      title: 'Perturbações orbitais',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Órbita kepleriana é idealização — J₂, arrasto, pressão solar e terceiros corpos exigem correção contínua.',
      shortExplanation:
        'Achatamento terrestre (J₂) causa precessão de nós e perigeo. Arrasto atmosférico decai LEO. Pressão solar e gravitação de terceiros corpos afetam órbitas altas e interplanetárias.',
      useFor: ['Manutenção de órbita', 'Predição de lifetime', 'Formação de constelação'],
      prerequisites: ['Kepler', 'Vis-viva'],
      relatedTopics: ['Kepler', 'Controle de atitude', 'Detritos espaciais'],
      projectIdeas: ['Estimar lifetime LEO 500 km com arrasto', 'Simular precessão J₂ para órbita SSO'],
      professorQuestions: [
        'Qual perturbação domina no seu regime orbital?',
        'Com que frequência seu satélite precisa de manobra de estação?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-attitude-control',
      title: 'Controle de atitude espacial',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Antena, painel solar e instrumento exigem orientação precisa — controle de atitude é crítico para missão.',
      shortExplanation:
        'Atuadores: roda de reação, magnetorquer, propulsor. Sensores: sol, estrela, giro. Estabilidade três eixos vs. spin. Momentum dumping e singularidade de roda são desafios operacionais.',
      useFor: ['Projeto ADCS', 'Operação de satélite', 'Apontamento de instrumento'],
      prerequisites: ['Dinâmica rotacional', 'Realimentação'],
      relatedTopics: ['Perturbações orbitais', 'Orçamento de link', 'Radiação espacial'],
      projectIdeas: ['Simular resposta de PID de atitude a perturbação', 'Dimensionar roda de reação para slew rate'],
      professorQuestions: [
        'Qual atuador você escolheu para desaturação e por quê?',
        'Como erro de atitude degrada orçamento de link?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-link-budget',
      title: 'Orçamento de link (link budget)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Comunicação espacial é marginal — link budget determina se sinal chega acima do limiar do receptor.',
      shortExplanation:
        'P_rx = P_tx + G_tx + G_rx − L_path − L_atm − L_misc (dB). Margem sobre limiar de ruído define BER aceitável. Distância, frequência e potência limitam taxa de dados.',
      useFor: ['Design de telecom', 'Seleção de antena', 'Análise de margem'],
      prerequisites: ['dB e ganho', 'Propagação EM'],
      relatedTopics: ['Controle de atitude', 'Radiação espacial', 'SSA'],
      projectIdeas: ['Link budget uplink/downlink para CubeSat LEO', 'Sensibilidade a apontamento de antena'],
      professorQuestions: [
        'Qual perda domina seu link budget?',
        'Como chuva e atmosfera afetam banda Ka vs. S?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-space-radiation',
      title: 'Radiação espacial e efeitos em eletrônica',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Ambiente espacial irradia satélites — SEE e TID degradam ou destroem componentes se não mitigados.',
      shortExplanation:
        'Cinturões Van Allen, SPE e GCR expõem eletrônica. Efeitos: bit-flip (SEU), latch-up (SEL), degradação cumulativa (TID). Blindagem, ECC e componentes rad-hard mitigam.',
      useFor: ['Seleção de componentes', 'Projeto de blindagem', 'Análise de confiabilidade'],
      prerequisites: ['Física nuclear básica', 'Eletrônica digital'],
      relatedTopics: ['Detritos espaciais', 'Controle de atitude', 'Link budget'],
      projectIdeas: ['Estimar TID em 5 anos LEO 600 km', 'Comparar FPGA comercial vs. rad-hard para missão'],
      professorQuestions: [
        'Qual efeito SEE é mais crítico no seu aviônico?',
        'Como teste acelerado em terra representa ambiente orbital?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-debris',
      title: 'Detritos espaciais e sustentabilidade orbital',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'LEO congestionado amplifica risco de colisão cascata (Kessler) — gestão de detritos é requisito de missão.',
      shortExplanation:
        'Detritos >10 cm rastreados; micropartículas perforam. Desorbitamento pós-missão, passivação e design for demise são mitigações. Probabilidade de colisão guia manobras de evitação.',
      useFor: ['Design de missão', 'Operação de constelação', 'Política espacial'],
      prerequisites: ['Mecânica orbital', 'Probabilidade'],
      relatedTopics: ['Perturbações orbitais', 'SSA', 'Radiação espacial'],
      projectIdeas: ['Calcular Pc para cruzamento de conjunção', 'Plano de desorbitamento em 25 anos'],
      professorQuestions: [
        'Seu satélite cumpre diretrizes de 25 anos pós-missão?',
        'Como incerteza de efemérides afeta decisão de manobra?',
      ],
    }),
    definePowerIdea({
      id: 'espaco-ssa',
      title: 'Space Situational Awareness (SSA)',
      type: 'conceito-chave',
      level: 'pesquisa',
      whyItMatters:
        'Operar em espaço exige saber o que orbita onde — SSA funde detecção, catalogação e predição de conjunção.',
      shortExplanation:
        'SSA combina radar, óptica e dados colaborativos para catalogar objetos, propagar efemérides e alertar conjunções. Precisão de catálogo limita Pc e manobras evasivas.',
      useFor: ['Operação de satélite', 'Defesa espacial', 'Gestão de tráfego'],
      prerequisites: ['Mecânica orbital', 'Detecção radar/óptica'],
      relatedTopics: ['Detritos espaciais', 'Link budget', 'C4ISR'],
      projectIdeas: ['Análise de alerta de conjunção com dados CDM', 'Comparar incerteza de efemérides de provedores'],
      professorQuestions: [
        'Qual limiar Pc dispara manobra no seu operador?',
        'Como SSA dual-use afeta cooperação internacional?',
      ],
    }),
  ],

  engenharia_aeroespacial: [
    definePowerIdea({
      id: 'aero-reynolds',
      title: 'Número de Reynolds',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Reynolds decide se fluxo é laminar ou turbulento — governa arrasto, mistura e similaridade de escala.',
      shortExplanation:
        'Re = ρVL/μ adimensiona inércia vs. viscosidade. Transição laminar→turbulento altera perfil de velocidade, arrasto de fricção e separação de camada limite.',
      useFor: ['Túnel de vento', 'Projeto de asa', 'Similaridade dinâmica'],
      relatedTopics: ['Mach', 'Camada limite', 'Navier-Stokes'],
      prerequisites: ['Mecânica dos fluidos', 'Análise dimensional'],
      projectIdeas: ['Calcular Re para asa em cruzeiro', 'Comparar Re modelo vs. full-scale'],
      professorQuestions: [
        'Seu fluxo é laminar, turbulento ou transicional na condição de interesse?',
        'Como rugosidade superficial altera Re crítico?',
      ],
    }),
    definePowerIdea({
      id: 'aero-mach',
      title: 'Número de Mach e regime compressível',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Acima de Ma ~0,3 compressibilidade altera aerodinâmica — essencial para aviação transônica e supersônica.',
      shortExplanation:
        'Ma = V/c. Efeitos compressíveis: ondas de choque, aumento de arrasto wave, mudança de centro de pressão. Transônico (Ma 0,8–1,2) é regime crítico em aviação comercial.',
      useFor: ['Projeto de perfil', 'Análise supersônica', 'Seleção de regime de voo'],
      prerequisites: ['Termodinâmica', 'Mecânica dos fluidos'],
      relatedTopics: ['Reynolds', 'Sustentação/arrasto', 'Navier-Stokes'],
      projectIdeas: ['Plotar Cp vs. x em perfil transônico', 'Identificar choque em simulação CFD'],
      professorQuestions: [
        'Onde choque aparece no seu perfil e qual efeito em momento?',
        'Quando correções de compressibilidade de Prandtl-Glauert bastam?',
      ],
    }),
    definePowerIdea({
      id: 'aero-lift-drag',
      title: 'Sustentação e arrasto aerodinâmico',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Voo é trade-off sustentação vs. arrasto — L/D maximiza alcance; arrasto wave limita velocidade.',
      shortExplanation:
        'Sustentação L = ½ρV²SC_L; arrasto D = ½ρV²SC_D. Polar de arrasto (C_L vs. C_D) caracteriza aerodinâmica. Induced drag domina em baixa velocidade; parasitic em alta.',
      useFor: ['Projeto preliminar', 'Performance de aeronave', 'Seleção de perfil'],
      prerequisites: ['Bernoulli', 'Reynolds'],
      relatedTopics: ['Camada limite', 'Estabilidade longitudinal', 'Reynolds'],
      projectIdeas: ['Construir polar a partir de dados de túnel', 'Calcular L/D máximo para asa retangular'],
      professorQuestions: [
        'Qual componente de arrasto domina na sua condição de projeto?',
        'Como C_L de projeto afeta peso estrutural e combustível?',
      ],
    }),
    definePowerIdea({
      id: 'aero-boundary-layer',
      title: 'Camada limite',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Arrasto de fricção e separação originam-se na camada limite — controle dela controla performance.',
      shortExplanation:
        'Camada limite é região onde viscosidade importa junto à superfície. Laminar tem menor arrasto mas separa cedo; turbulenta adere melhor mas arrasta mais. Transição e tripping são ferramentas de controle.',
      useFor: ['Projeto de perfil', 'Redução de arrasto', 'Controle de separação'],
      prerequisites: ['Reynolds', 'Navier-Stokes'],
      relatedTopics: ['Reynolds', 'Sustentação/arrasto', 'Navier-Stokes'],
      projectIdeas: ['Estimar espessura δ para placa plana', 'Comparar separação laminar vs. turbulento'],
      professorQuestions: [
        'Onde separação ocorre no seu perfil e como retardá-la?',
        'Tripping forçado vale a pena no seu Re de operação?',
      ],
    }),
    definePowerIdea({
      id: 'aero-navier-stokes',
      title: 'Equações de Navier–Stokes',
      type: 'lei',
      level: 'avancado',
      whyItMatters:
        'NS são a lei fundamental dos fluidos viscosos — CFD resolve NS para projetos onde analítico falha.',
      shortExplanation:
        'Conservação de massa + momentum viscoso compressível. Turbulência exige modelos (RANS, LES, DNS). Solução numérica (CFD) é padrão em projeto aeroespacial moderno.',
      useFor: ['CFD', 'Validação experimental', 'Projeto de asa/fuselagem'],
      prerequisites: ['Cálculo vetorial', 'Mecânica dos fluidos'],
      relatedTopics: ['Reynolds', 'Camada limite', 'Mach'],
      projectIdeas: ['Simulação 2D perfil com OpenFOAM ou SU2', 'Estudo de sensibilidade de malha'],
      professorQuestions: [
        'Qual modelo de turbulência você validou para seu caso?',
        'Como incerteza de malha afeta C_L predito?',
      ],
    }),
    definePowerIdea({
      id: 'aero-longitudinal-stability',
      title: 'Estabilidade longitudinal',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Aeronave deve retornar ao equilíbrio após perturbação — margem estática e dinâmica definem handling.',
      shortExplanation:
        'Estabilidade estática: C_mα < 0 (momento restaurador). Ponto neutro e margem estática (% MAC) determinam C_G permitido. Modos de curto e longo período governam resposta dinâmica.',
      useFor: ['Projeto de tail', 'Análise de trim', 'Certificação'],
      prerequisites: ['Sustentação/arrasto', 'Dinâmica de voo'],
      relatedTopics: ['Sustentação/arrasto', 'Controle de atitude', 'Aeroelasticidade'],
      projectIdeas: ['Calcular margem estática dado C_mα e posição CG', 'Simular resposta pitch a degrau'],
      professorQuestions: [
        'Sua aeronave é estaticamente estável e estaticamente margem suficiente?',
        'Como shift de CG em voo afeta margem?',
      ],
    }),
    definePowerIdea({
      id: 'aero-tsiolkovsky',
      title: 'Equação de Tsiolkovsky (foguete)',
      type: 'identidade-matematica',
      level: 'basico',
      whyItMatters:
        'Foguete é sistema de massa variável — Tsiolkovsky quantifica Δv vs. Isp e fração estrutural.',
      shortExplanation:
        'Δv = I_sp g₀ ln(m₀/m_f). Eficiência propulsiva e massa seca limitam payload. Staging multiplica Δv disponível.',
      useFor: ['Design de lançador', 'Análise de missão', 'Trade-off propulsor'],
      prerequisites: ['Conservação de momentum', 'Propulsão básica'],
      relatedTopics: ['Relação thrust-weight', 'Hohmann', 'Controle de atitude'],
      projectIdeas: ['Calcular Δv para single-stage vs. two-stage', 'Sensibilidade a fração estrutural'],
      professorQuestions: [
        'Por que single-stage-to-orbit é tão difícil quantitativamente?',
        'Como Isp real com atmosfera altera Δv efetivo?',
      ],
    }),
    definePowerIdea({
      id: 'aero-thrust-weight',
      title: 'Relação thrust-to-weight (T/W)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Decolagem e manobra exigem T/W > 1 — razão governa performance vertical e aceleração.',
      shortExplanation:
        'T/W = thrust/peso. T/W > 1 permite ascensão vertical; T/W baixo em cruzeiro maximiza eficiência. Trade-off entre motor pesado e aceleração.',
      useFor: ['Sizing de propulsão', 'Análise de decolagem', 'Projeto de UAV'],
      prerequisites: ['Tsiolkovsky', 'Performance de voo'],
      relatedTopics: ['Tsiolkovsky', 'Sustentação/arrasto', 'Aeroelasticidade'],
      projectIdeas: ['Calcular T/W mínimo para takeoff em 3000 m', 'Plotar T/W vs. climb rate'],
      professorQuestions: [
        'Qual T/W você dimensionou e qual margem para one-engine-out?',
        'Como altitude reduz thrust e exige T/W maior?',
      ],
    }),
    definePowerIdea({
      id: 'aero-aeroelasticity',
      title: 'Aeroelasticidade',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Interação aerodinâmica–estrutural causa flutter e divergência — failure mode catastrófico em voo.',
      shortExplanation:
        'Deformação altera carga aerodinâmica que amplifica deformação (feedback). Flutter é instabilidade dinâmica; divergência é estática. Análise acoplada CFD-CSD é padrão em certificação.',
      useFor: ['Certificação estrutural', 'Projeto de asa', 'Túnel aeroelástico'],
      prerequisites: ['Dinâmica estrutural', 'Sustentação/arrasto'],
      relatedTopics: ['Navier-Stokes', 'Estabilidade longitudinal', 'Controle de atitude'],
      projectIdeas: ['Estimar velocidade de divergência simplificada', 'Revisar caso flutter clássico (Tacoma Bridge analogia aérea)'],
      professorQuestions: [
        'Quais modos estruturais acoplam com modos aerodinâmicos no seu caso?',
        'Como damping estrutural afeta margem de flutter?',
      ],
    }),
    definePowerIdea({
      id: 'aero-attitude-control',
      title: 'Controle de atitude aeroespacial',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Missão aeroespacial exige orientação precisa — ADCS difere entre satélite, míssil e reentry vehicle.',
      shortExplanation:
        'Atuadores e sensores adaptados ao ambiente: aerodinâmico (superfícies), propulsivo (RCS), momentum (rodas). Dinâmica rotacional acoplada a trajetória em reentry.',
      useFor: ['Projeto GNC', 'Simulação 6-DOF', 'Operação de veículo'],
      prerequisites: ['Dinâmica rotacional', 'Realimentação'],
      relatedTopics: ['Estabilidade longitudinal', 'Aeroelasticidade', 'Controle de atitude espacial'],
      projectIdeas: ['Simular controle pitch com superfície de comando', 'Comparar RCS vs. aerodinâmico em reentry'],
      professorQuestions: [
        'Qual atuador domina em cada fase de voo no seu veículo?',
        'Como coupling trajetória–atitude afeta precisão de impacto?',
      ],
    }),
  ],

  tecnologias_estrategicas: [
    definePowerIdea({
      id: 'tech-strat-trl',
      title: 'Technology Readiness Level (TRL)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'TRL comunica maturidade tecnológica — evita prometer inovação laboratorial como produto operacional.',
      shortExplanation:
        'Escala 1–9: princípio observado (1) → validado em ambiente operacional (9). TRL guia investimento, aquisição e risco de integração. Gap “vale da morte” entre TRL 4–6 é crítico.',
      useFor: ['Roadmapping', 'Proposta de P&D', 'Avaliação de fornecedor'],
      prerequisites: ['Gestão de inovação', 'Engenharia de sistemas'],
      relatedTopics: ['Roadmapping', 'Inovação mission-driven', 'Dual use'],
      projectIdeas: ['Avaliar TRL de tecnologia candidata em edital', 'Plano de elevação TRL 3→6 em 24 meses'],
      professorQuestions: [
        'Qual evidência concreta sustenta o TRL que você atribuiu?',
        'O que falta para subir um nível e quanto custa?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-dual-use',
      title: 'Tecnologias dual use',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Mesma tecnologia serve civil e militar — dual use exige governança, export control e avaliação ética.',
      shortExplanation:
        'Exemplos: GPS, drones, IA, biotech, materiais avançados. Benefícios civis coexistem com risco de proliferação. Políticas de controle e due diligence mitigam misuse.',
      useFor: ['Compliance export', 'Parceria internacional', 'Avaliação de risco'],
      prerequisites: ['Política tecnológica', 'Ética em P&D'],
      relatedTopics: ['Controles de exportação', 'Soberania tecnológica', 'Cadeia crítica'],
      projectIdeas: ['Análise dual use de sensor autônomo', 'Checklist due diligence para colaboração'],
      professorQuestions: [
        'Quais usos não intencionais sua tecnologia habilita?',
        'Como balancear abertura científica e controle de exportação?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-roadmapping',
      title: 'Roadmapping tecnológico',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Roadmap alinha tecnologia, produto e mercado no tempo — evita P&D desconectado de necessidade.',
      shortExplanation:
        'Roadmaps (S&T, produto, setorial) ligam drivers, barreras, tecnologias e marcos temporais. Processo participativo integra R&D, manufatura e estratégia.',
      useFor: ['Planejamento institucional', 'Edital de fomento', 'Consórcio industrial'],
      prerequisites: ['TRL', 'Gestão de projetos'],
      relatedTopics: ['TRL', 'Foresight', 'Inovação mission-driven'],
      projectIdeas: ['Roadmap simplificado para baterias de estado sólido', 'Workshop roadmapping com stakeholders'],
      professorQuestions: [
        'Quais drivers de mercado ou missão ancoram seu roadmap?',
        'Como você revisa roadmap quando tecnologia disruptiva emerge?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-foresight',
      title: 'Foresight e inteligência tecnológica',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Antecipar rupturas e dependências — foresight informa investimento antes que crise apareça.',
      shortExplanation:
        'Métodos: Delphi, cenários, patent landscaping, weak signals. Combina dados quantitativos e julgamento expert para explorar futuros plausíveis e preparar opções estratégicas.',
      useFor: ['Política industrial', 'Priorização de P&D', 'Análise competitiva'],
      prerequisites: ['Estatística', 'Gestão estratégica'],
      relatedTopics: ['Roadmapping', 'Cadeia crítica', 'Soberania tecnológica'],
      projectIdeas: ['Cenários 2035 para semicondutores', 'Análise de patentes em quantum computing'],
      professorQuestions: [
        'Qual weak signal você monitora e qual trigger de ação?',
        'Como evitar viés de confirmacao em exercício de cenários?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-critical-supply-chain',
      title: 'Cadeias de suprimento críticas',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Dependência de fornecedor único ou região expõe indústria e defesa — cadeia crítica é segurança nacional.',
      shortExplanation:
        'Mapeamento de tiers, gargalos (litio, rare earths, semicondutores) e vulnerabilidades geopolíticas. Estratégias: diversificação, estoque estratégico, reshoring, substitutos.',
      useFor: ['Política industrial', 'Due diligence', 'Projeto de produto'],
      prerequisites: ['Economia', 'Logística'],
      relatedTopics: ['Soberania tecnológica', 'Controles de exportação', 'Foresight'],
      projectIdeas: ['Mapa de dependência para ímã de NdFeB', 'Análise what-if de embargo em insumo crítico'],
      professorQuestions: [
        'Qual single point of failure na sua cadeia e qual plano B?',
        'Substituto existe ou exige redesign completo?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-sovereignty',
      title: 'Soberania tecnológica',
      type: 'conceito-chave',
      level: 'pesquisa',
      whyItMatters:
        'Capacidade domestica de desenvolver e fabricar tecnologias críticas — autonomia estratégica vs. dependência.',
      shortExplanation:
        'Soberania abrange P&D, manufatura, talento e padrões. Setores críticos: semicondutores, energia, saúde, defesa, espaço. Parcerias internacionais coexistem com capacidade nacional mínima.',
      useFor: ['Política pública', 'Estratégia corporativa', 'Análise de risco geopolítico'],
      prerequisites: ['Economia política', 'Cadeia crítica'],
      relatedTopics: ['Cadeia crítica', 'Controles de exportação', 'Inovação mission-driven'],
      projectIdeas: ['Benchmark soberania em microeletrônica vs. referência OECD', 'Proposta capacidade mínima viável em setor X'],
      professorQuestions: [
        'Soberania total é realista ou quais trade-offs aceitar?',
        'Como medir soberania além de autossuficiência percentual?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-export-controls',
      title: 'Controles de exportação',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Tecnologia sensível requer licenciamento — violação acarreta sanções e risco de proliferação.',
      shortExplanation:
        'Regimes multilaterais (Wassenaar, NSG, MTCR) e listas nacionais classificam itens e conhecimento. EAR/ITAR (EUA) e equivalentes locais regem transferência transfronteiriça e colaboração.',
      useFor: ['Compliance', 'Parceria internacional', 'Spin-off de P&D'],
      prerequisites: ['Dual use', 'Direito comercial básico'],
      relatedTopics: ['Dual use', 'Soberania tecnológica', 'Cadeia crítica'],
      projectIdeas: ['Checklist classificação para componente eletrônico', 'Fluxo de licenciamento para colaboração EUA-Brasil'],
      professorQuestions: [
        'Seu componente está na lista de controle e quem classificou?',
        'Como deemed export afeta pesquisadores estrangeiros no lab?',
      ],
    }),
    definePowerIdea({
      id: 'tech-strat-mission-driven-innovation',
      title: 'Inovação orientada por missão',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'Grandes desafios (clima, saúde, energia) exigem coordenação público-privada — missão direciona inovação sistêmica.',
      shortExplanation:
        'Mariana Mazzucato: missões ambiciosas mobilizam P&D, mercado e regulação. Diferente de subsídio cego — define problema societal e métricas de impacto, tolerando incerteza tecnológica.',
      useFor: ['Política de fomento', 'Design de edital', 'Estratégia de cluster'],
      prerequisites: ['Economia da inovação', 'TRL'],
      relatedTopics: ['Roadmapping', 'TRL', 'Soberania tecnológica'],
      projectIdeas: ['Proposta missão descarbonização transporte pesado', 'Métricas de impacto para missão saúde digital'],
      professorQuestions: [
        'Sua missão é específica o suficiente para guiar investimento?',
        'Como evitar capture by incumbents em missão pública?',
      ],
    }),
  ],

  medicina_nuclear: [
    definePowerIdea({
      id: 'med-nuclear-radiopharmaceuticals',
      title: 'Radiofármacos e farmacocinética',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Medicina nuclear depende de moléculas marcadas — radiofármaco liga química, farmacologia e decaimento.',
      shortExplanation:
        'Radiofármaco = ligante biológico + radionuclídeo. Biodisponibilidade, especificidade de receptor e pureza radiológica determinam imagem ou terapia. Produção GMP e controle de qualidade são obrigatórios.',
      useFor: ['PET/SPECT clínico', 'Desenvolvimento de traçador', 'Terapia radiometálica'],
      prerequisites: ['Química nuclear', 'Fisiologia'],
      relatedTopics: ['Radiomarcação', 'Biodistribuição', 'Meia-vida efetiva'],
      projectIdeas: ['Revisar desenvolvimento de ⁶⁸Ga-DOTATATE', 'Fluxograma QC de radiofármaco'],
      professorQuestions: [
        'Qual critério de pureza radiológica é crítico no seu radiofármaco?',
        'Como impureza radionuclídica afeta dose e imagem?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-effective-half-life',
      title: 'Meia-vida efetiva (física + biológica)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Radionuclídeo decai enquanto corpo excreta — meia-vida efetiva governa dose e janela de imagem.',
      shortExplanation:
        '1/T_eff = 1/T_fís + 1/T_bi ol. T_eff < min(T_fís, T_bi ol). Determina tempo ótimo de aquisição e dose residual. Ex.: ¹³¹I combina T_fís longo com retenção thyroid.',
      useFor: ['Planejamento de dose', 'Protocolo de aquisição', 'Alta do paciente'],
      prerequisites: ['Decaimento radioativo', 'Farmacocinética'],
      relatedTopics: ['Radiofármacos', 'Biodistribuição', 'Dose absorvida em tecido'],
      projectIdeas: ['Calcular T_eff para ⁹⁹ᵐTc-MDP', 'Curva de retenção e ajuste bi-exponencial'],
      professorQuestions: [
        'Qual componente biológico domina T_eff no seu tracador?',
        'Como T_eff altera timing pós-injeção para PET?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-pet-spect',
      title: 'Princípios de PET e SPECT',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'PET/SPECT mapeiam função metabólica in vivo — física de detecção define resolução e sensibilidade.',
      shortExplanation:
        'PET: aniquilação e⁺ produz dois fótons 511 keV coincidentes; SPECT: colimação de fóton único. Correção de atenuação, scatter e reconstrução tomográfica afetam quantificação.',
      useFor: ['Interpretação clínica', 'Desenvolvimento de protocolo', 'Pesquisa translacional'],
      prerequisites: ['Física nuclear', 'Processamento de imagem'],
      relatedTopics: ['Reconstrução de imagem', 'Radiofármacos', 'QA em medicina nuclear'],
      projectIdeas: ['Comparar resolução PET vs. SPECT para mesmo tracador', 'Efeito de correção de atenuação em SUV'],
      professorQuestions: [
        'Por que PET tem sensibilidade superior a SPECT?',
        'Como partial volume effect distorce SUV em lesões pequenas?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-radiolabeling',
      title: 'Radiomarcação e química de coordenação',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Marcação eficiente e estável é gargalo — química define yield, especificidade e segurança do radiofármaco.',
      shortExplanation:
        'Técnicas: redução pertecnetato, chelatação (DOTA, DTPA), marcacao prostética, click chemistry. Condições (pH, temperatura, atividade específica) afetam perfil impureza e biodistribuição.',
      useFor: ['Síntese de radiofármaco', 'Desenvolvimento de traçador', 'Produção clínica'],
      prerequisites: ['Química orgânica', 'Química nuclear'],
      relatedTopics: ['Radiofármacos', 'Biodistribuição', 'QA em medicina nuclear'],
      projectIdeas: ['Otimizar condições de chelatação Ga-68', 'HPLC para pureza radiológica'],
      professorQuestions: [
        'Como atividade específica afeta afinidade receptor in vivo?',
        'Qual impurity química redistribui dose indesejada?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-biodistribution',
      title: 'Biodistribuição e farmacocinética in vivo',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Onde o radiofármaco vai determina imagem útil e dose em órgãos críticos — biodistribuição guia protocolo e segurança.',
      shortExplanation:
        'Fases: distribuição vascular, uptake específico, clearance renal/hepática. Uptake não específico e metabolitos marcados degradam contraste. Modelos compartimentais quantificam cinética.',
      useFor: ['Interpretação de imagem', 'Dosimetria interna', 'Design de traçador'],
      prerequisites: ['Fisiologia', 'Meia-vida efetiva'],
      relatedTopics: ['Radiofármacos', 'Dose absorvida em tecido', 'Teranostica'],
      projectIdeas: ['Curvas time-activity por órgão a partir de imagens', 'Comparar biodistribuição analog vs. antagonista'],
      professorQuestions: [
        'Qual órgão de uptake não específico limita seu contraste?',
        'Como metabolismo in vivo altera interpretação tardia?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-absorbed-dose-tissue',
      title: 'Dose absorvida em tecido (medicina nuclear)',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Terapia e segurança exigem estimar Gy depositados por tecido — dose absorvida liga administração a efeito biológico.',
      shortExplanation:
        'D = Ã × S (MIRD): cumulated activity Ã e S factor por radionuclídeo/tecidos. OLINDA/IDAC software implementam. Incerteza em uptake e massa orgânica afeta prescrição terapêutica.',
      useFor: ['Terapia com ¹³¹I, ¹⁷⁷Lu', 'Autorização de liberação', 'Pesquisa dosimétrica'],
      prerequisites: ['Decaimento', 'Biodistribuição'],
      relatedTopics: ['Biodistribuição', 'Teranostica', 'Regulatório em MN'],
      projectIdeas: ['Dosimetria OLINDA para paciente ¹³¹I tiroidectomia', 'Sensibilidade dose rim vs. massa renal'],
      professorQuestions: [
        'Qual órgão limitante no seu protocolo terapêutico?',
        'Como incerteza em Ã afeta decisão de atividade prescrita?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-image-reconstruction',
      title: 'Reconstrução tomográfica em medicina nuclear',
      type: 'ferramenta-computacional',
      level: 'avancado',
      whyItMatters:
        'Projeções não são imagem — algoritmo de reconstrução define ruído, artefato e quantificação (SUV).',
      shortExplanation:
        'FBP (Filtrada retroprojeção) vs. iterativo (OSEM, BSREM). Correções: atenuação, scatter, decay, normalização. Regularização reduz ruído à custa de resolução.',
      useFor: ['Pesquisa quantitativa', 'Otimização de protocolo', 'QA de imagem'],
      prerequisites: ['PET/SPECT', 'Transformada de Radon'],
      relatedTopics: ['PET/SPECT', 'QA em medicina nuclear', 'Dose absorvida em tecido'],
      projectIdeas: ['Comparar FBP vs. OSEM em phantom NEMA', 'Efeito de número de iterações em SUV recovery'],
      professorQuestions: [
        'Quantas iterações você parou e qual critério de stopping?',
        'Como artefato de movimento respiratório afeta reconstrução?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-qa',
      title: 'Garantia de qualidade em medicina nuclear',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Segurança do paciente e qualidade diagnóstica exigem QA sistemático — calibração, phantom e auditoria.',
      shortExplanation:
        'QA inclui constancy de energia, uniformidade, sensibilidade, SUV accuracy (NEMA IEC), dose calibrator e wipe tests. Frequências definidas por normas (ANVISA, IAEA).',
      useFor: ['Operação de serviço', 'Acreditação', 'Manutenção preventiva'],
      prerequisites: ['PET/SPECT', 'Metrologia'],
      relatedTopics: ['Reconstrução de imagem', 'Regulatório em MN', 'Radiofármacos'],
      projectIdeas: ['Programa QA mensal para PET/CT', 'Registro de desvios e ação corretiva'],
      professorQuestions: [
        'Qual teste QA falhou e qual impacto clínico potencial?',
        'Como você rastreia calibração do calibrador de dose?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-theranostics',
      title: 'Teranostica (imagem + terapia pareada)',
      type: 'conceito-chave',
      level: 'pesquisa',
      whyItMatters:
        'Mesmo alvo molecular com radionuclídeo diagnóstico e terapêutico — personalização e dosimetria integradas.',
      shortExplanation:
        'Par diagnóstico/terapia (ex.: ⁶⁸Ga/⁶⁸Lu-DOTATATE, ⁶⁸Ga/⁶⁸Ac-PSMA). Imagem quantifica uptake; terapia deliver dose. Resposta e toxicidade monitoradas por imagem sequencial.',
      useFor: ['Oncologia molecular', 'Dosimetria personalizada', 'Ensaios clínicos'],
      prerequisites: ['PET/SPECT', 'Dose absorvida em tecido'],
      relatedTopics: ['Radiofármacos', 'Biodistribuição', 'Regulatório em MN'],
      projectIdeas: ['Revisão evidência Lu-177 PSMA', 'Fluxo clínico teranostico em NET'],
      professorQuestions: [
        'Como imagem pré-terapia altera prescrição de atividade?',
        'Quais critérios de resposta você usa além de RECIST?',
      ],
    }),
    definePowerIdea({
      id: 'med-nuclear-regulatory',
      title: 'Regulamentação em medicina nuclear',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Prática clínica e pesquisa exigem conformidade — regulatório protege paciente, operador e meio ambiente.',
      shortExplanation:
        'Normas: autorização de uso, limites de dose, rejeitos radioativos, registro de paciente, farmacovigilância. ANVISA, CNEN e conselhos profissionais definem requisitos. RDC e guias IAEA orientam.',
      useFor: ['Licenciamento de serviço', 'Protocolo clínico', 'Submissão ética'],
      prerequisites: ['Proteção radiológica', 'Radiofármacos'],
      relatedTopics: ['QA em medicina nuclear', 'Dose absorvida em tecido', 'Teranostica'],
      projectIdeas: ['Checklist conformidade para novo radiofármaco', 'Fluxo autorização CNEN para serviço'],
      professorQuestions: [
        'Qual requisito regulatório é gargalo na sua proposta de serviço?',
        'Como evento adverso radiofármaco é reportado na sua instituição?',
      ],
    }),
  ],

  dosimetria: [
    definePowerIdea({
      id: 'dosimetria-absorbed-dose',
      title: 'Dose absorvida (D)',
      type: 'conceito-chave',
      level: 'basico',
      whyItMatters:
        'Grandeza fundamental da dosimetria — energia depositada por unidade de massa conecta radiação a efeito biológico local.',
      shortExplanation:
        'D = dE/dm (Gy = J/kg). Mede energia impartida em tecido ou detector. Distinto de exposição (C/kg) e de dose equivalente. Base para cálculos clínicos e de proteção.',
      useFor: ['Calibracao de dosímetro', 'Planejamento radioterápico', 'Proteção radiológica'],
      prerequisites: ['Física nuclear', 'Unidades SI'],
      relatedTopics: ['Kerma', 'Dose equivalente', 'Bragg-Gray'],
      projectIdeas: ['Converter exposição em dose absorvida para fótons conhecidos', 'Comparar D medida vs. calculada em phantom'],
      professorQuestions: [
        'Dose absorvida mede efeito biológico diretamente ou precisa de ponderações?',
        'Como cavidade de Bragg-Gray relaciona dose no detector à dose no meio?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-equivalent-dose',
      title: 'Dose equivalente (H_T)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Mesma dose absorvida produz dano diferente por tipo e energia de radiação — H_T corrige por eficácia biológica relativa.',
      shortExplanation:
        'H_T = Σ w_R × D_T,R, onde w_R é fator de ponderação da radiação. Converte dose absorvida por tipo de radiação em grandeza orientada à proteção do tecido irradiado.',
      useFor: ['Proteção ocupacional', 'Limites de dose', 'Classificação de área'],
      prerequisites: ['Dose absorvida', 'Fatores de ponderação'],
      relatedTopics: ['Dose efetiva', 'LET', 'RBE'],
      projectIdeas: ['Calcular H_T para neutrons + fótons em campo misto', 'Comparar w_R para elétrons vs. prótons'],
      professorQuestions: [
        'Por que neutrons exigem w_R maior que fótons?',
        'Como você mede D_T,R separadamente em campo misto?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-effective-dose',
      title: 'Dose efetiva (E)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'E resume risco estocástico whole-body — permite comparar exposições heterogêneas e aplicar limites.',
      shortExplanation:
        'E = Σ w_T × H_T, soma sobre tecidos com w_T (fator de ponderação tecidual). Grandeza de proteção, não indicada para exposições parciais extremas ou terapêuticas.',
      useFor: ['Limites regulatórios', 'Comparação de procedimentos', 'Relatório de dose ocupacional'],
      prerequisites: ['Dose equivalente', 'Fatores de ponderação'],
      relatedTopics: ['Dose equivalente', 'Incerteza dosimétrica', 'Limites de dose'],
      projectIdeas: ['Estimar E para tomografia multiphase', 'Contribuição por órgão para E total'],
      professorQuestions: [
        'Quando dose efetiva NÃO deve ser usada para comunicar risco?',
        'Como w_T de mama e gônadas reflete sensibilidade radiológica?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-kerma',
      title: 'Kerma (K)',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Kerma quantifica energia transferida por radiação indirectamente ionizante — ponte entre fluência e dose em meio.',
      shortExplanation:
        'K = dE_tr/dm, energia transferida a elétrons por massa. Em charged particle equilibrium (CPE), K ≈ D. Usado em calibração de feixes de fótons em ar.',
      useFor: ['Calibração em radioterapia', 'Dosimetria de feixe', 'Física de proteção'],
      prerequisites: ['Interação fóton-matéria', 'Dose absorvida'],
      relatedTopics: ['Equilíbrio de partículas carregadas', 'Bragg-Gray', 'Dose absorvida'],
      projectIdeas: ['Demonstrar K≈D em condição CPE', 'Calcular kerma collisional vs. radiative'],
      professorQuestions: [
        'Onde CPE falha no seu feixe e qual correção aplicar?',
        'Qual a diferença prática entre kerma e dose em ar vs. tecido?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-let',
      title: 'Transferência linear de energia (LET)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'LET caracteriza ionização densa — radiação de alto LET produz dano biológico qualitativamente diferente.',
      shortExplanation:
        'LET = dE/dx (keV/μm), média de energia depositada por unidade de caminho. Alto LET (partículas pesadas, α) vs. baixo LET (fótons, elétrons). Correlaciona com RBE e microdosimetria.',
      useFor: ['Radioterapia com íons pesados', 'Proteção em campos mistos', 'Microdosimetria'],
      prerequisites: ['Interação charged particle', 'Dose absorvida'],
      relatedTopics: ['RBE', 'Dose equivalente', 'Bragg-Gray'],
      projectIdeas: ['Comparar LET médio de próton vs. fóton em SOBP', 'Curva Bragg e LET ao longo do feixe'],
      professorQuestions: [
        'Por que RBE aumenta no final do range de próton?',
        'LET médio ou lineal de track: qual você reporta e por quê?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-rbe',
      title: 'Eficácia biológica relativa (RBE)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'RBE quantifica dano biológico relativo a referência — essencial para hadronterapia e proteção de neutrons.',
      shortExplanation:
        'RBE = dose referência / dose teste para mesmo efeito biológico. Depende de LET, dose, endpoint e linhagem celular. w_R incorpora RBE médio em proteção; clínica usa RBE clínico (ex.: 1,1 para prótons).',
      useFor: ['Prescrição em carbono/próton', 'Proteção de neutrons', 'Comparação de modalidades'],
      prerequisites: ['LET', 'Radiobiologia básica'],
      relatedTopics: ['LET', 'Dose equivalente', 'Fatores de ponderação'],
      projectIdeas: ['Revisão RBE clínico vs. experimental para prótons', 'Sensibilidade de RBE a hipóxia tumoral'],
      professorQuestions: [
        'RBE constante 1,1 para prótons é conservador ou arriscado no seu protocolo?',
        'Qual endpoint biológico você usa para definir RBE experimental?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-charged-particle-equilibrium',
      title: 'Equilíbrio de partículas carregadas (CPE)',
      type: 'principio',
      level: 'avancado',
      whyItMatters:
        'CPE é condição onde kerma aproxima dose absorvida — fundamental para calibração e escolha de profundidade.',
      shortExplanation:
        'CPE ocorre quando cada elétron criado é substituído por outro de mesma energia. Transient CPE (TCPE) precede CPE pleno. Build-up cap define região de equilíbrio em dosimetria de feixe.',
      useFor: ['Calibração de câmara de ionização', 'Dosimetria absoluta', 'Correção de profundidade'],
      prerequisites: ['Kerma', 'Interação fóton-matéria'],
      relatedTopics: ['Kerma', 'Bragg-Gray', 'Incerteza dosimétrica'],
      projectIdeas: ['Identificar profundidade de D_max e região CPE', 'Efeito de build-up cap em feixe MV'],
      professorQuestions: [
        'A que profundidade CPE é alcançado no seu phantom?',
        'Como eletrons de contato violam CPE na superfície?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-bragg-gray',
      title: 'Princípio de Bragg-Gray e dosimetria de cavidade',
      type: 'teorema',
      level: 'avancado',
      whyItMatters:
        'Relaciona dose no detector pequeno à dose no meio circundante — base da dosimetria clínica com câmara de ionização.',
      shortExplanation:
        'Se cavidade não perturba fluência e CPE existe, dose no gás sensível iguala dose no meio. Correções: perturbação, recombination, polarity, calibração N_K ou N_D,w.',
      useFor: ['Dosimetria absoluta TRS-398', 'Calibração clínica', 'Auditoria dosimétrica'],
      prerequisites: ['CPE', 'Kerma', 'Dose absorvida'],
      relatedTopics: ['CPE', 'Incerteza dosimétrica', 'Kerma'],
      projectIdeas: ['Checklist correções TRS-398 para feixe 6 MV', 'Estimar incerteza de correção de perturbação'],
      professorQuestions: [
        'Qual correção domina incerteza no seu procedimento absoluto?',
        'Quando câmara de Farmer não satisfaz Bragg-Gray?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-uncertainty',
      title: 'Incerteza dosimétrica (GUM aplicada)',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Dose sem incerteza é incompleta — orçamento de incerteza quantifica confiança e identifica melhorias.',
      shortExplanation:
        'Componentes tipo A (repetibilidade) e B (calibração, correções, geometria). u_c combinada e U expandida (k=2). TRS-398 e IAEA fornecem exemplos para dosimetria clínica.',
      useFor: ['Relatório de calibração', 'Auditoria', 'Comparação intercomparativa'],
      prerequisites: ['Propagação de erro', 'Bragg-Gray'],
      relatedTopics: ['Bragg-Gray', 'Dose efetiva', 'Fatores de ponderação'],
      projectIdeas: ['Orçamento incerteza para dose em phantom', 'Ranking contribuições por sensibilidade'],
      professorQuestions: [
        'Qual componente você subestimou no orçamento inicial?',
        'Como TPC (Type A) afeta intervalo de confiança da dose diária?',
      ],
    }),
    definePowerIdea({
      id: 'dosimetria-weighting-factors',
      title: 'Fatores de ponderação (w_R e w_T)',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Ponderações traduzem física de dose em risco relativo — valores refletem consenso científico e política de proteção.',
      shortExplanation:
        'w_R pondera tipo de radiação (fótons 1, neutrons até 20, α 20). w_T pondera sensibilidade de órgãos (gônadas 0,08, tireoide 0,04, etc.). Revisões ICRP (103, 116) atualizam valores.',
      useFor: ['Cálculo de dose efetiva', 'Regulamentação', 'Comunicação de risco'],
      prerequisites: ['Dose equivalente', 'Dose efetiva'],
      relatedTopics: ['Dose equivalente', 'Dose efetiva', 'RBE'],
      projectIdeas: ['Calcular E para exposição ocupacional documentada', 'Impacto de revisão w_R em dose de tripulacao aérea'],
      professorQuestions: [
        'Por que w_T de gônadas excede w_T de pele?',
        'Como incerteza em w_R afeta comparacao de modalidades?',
      ],
    }),
  ],

  protecao_radiologica: [
    definePowerIdea({
      id: 'prot-rad-alara',
      title: 'Princípio ALARA (As Low As Reasonably Achievable)',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Proteção não para no limite regulatório — ALARA exige otimização contínua abaixo do limite quando razoável.',
      shortExplanation:
        'Dose deve ser mantida tão baixa quanto razoavelmente exequível considerando tecnologia, economia e benefício social. Aplica-se a exposições planejadas; complementa justificação e limitação.',
      useFor: ['Procedimento operacional', 'Análise de tarefa', 'Auditoria de prática'],
      prerequisites: ['Limites de dose', 'Justificação'],
      relatedTopics: ['Otimização', 'Tempo-distância-blindagem', 'Cultura de segurança'],
      projectIdeas: ['Revisão ALARA em procedimento de radiografia industrial', 'Identificar três melhorias ALARA no laboratório'],
      professorQuestions: [
        'O que impede reduzir dose além do seu plano ALARA atual?',
        'Como você documenta trade-off custo vs. redução de dose?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-time-distance-shielding',
      title: 'Tempo, distância e blindagem',
      type: 'metodo',
      level: 'basico',
      whyItMatters:
        'Três alavancas práticas imediatas — reduzir tempo, aumentar distância (lei do inverso do quadrado) e interpor blindagem.',
      shortExplanation:
        'Dose ∝ tempo de exposição; dose ∝ 1/r² para ponto fonte; blindagem atenua por espessura e material (HVL, TVL). Combinar as três é estratégia operacional básica.',
      useFor: ['Procedimento de campo', 'Projeto de bunker', 'Emergência radiológica'],
      prerequisites: ['Dose absorvida', 'Atenuação'],
      relatedTopics: ['ALARA', 'Defesa em profundidade', 'Termo fonte'],
      projectIdeas: ['Calcular dose vs. distância para fonte Co-60', 'Dimensionar blindagem Pb para sala de radioterapia'],
      professorQuestions: [
        'Qual alavanca você priorizou e qual sacrificou no seu cenário?',
        'Como scatter aumenta dose além da linha de visão direta?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-defense-in-depth',
      title: 'Defesa em profundidade',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Barreira única falha — múltiplas camadas independentes previnem exposição mesmo com falha de uma defesa.',
      shortExplanation:
        'Camadas: contenção física, procedimento, treinamento, detecção, intertravamento. Princípio nuclear aplicado à proteção radiológica em instalações, transporte e medicina.',
      useFor: ['Projeto de instalação', 'Análise de acidente', 'Licenciamento'],
      prerequisites: ['Cultura de segurança', 'Justificação'],
      relatedTopics: ['ALARA', 'Cenários de emergência', 'Termo fonte'],
      projectIdeas: ['Mapa de barreiras para irradiador industrial', 'Análise single failure em sistema de intertravamento'],
      professorQuestions: [
        'Qual barreira é common cause failure no seu sistema?',
        'Como você testa barreiras administrativas vs. físicas?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-dose-limits',
      title: 'Limites de dose (ocupacional e público)',
      type: 'lei',
      level: 'basico',
      whyItMatters:
        'Limites definem teto regulatório — base para autorização, monitoração e ação quando excedidos.',
      shortExplanation:
        'ICRP/CNEN: limite ocupacional efetiva 20 mSv/ano (média 5 em 5 anos); público 1 mSv/ano. Limites equivalentes por tecido (lente do olho, pele, mãos). Grávidas: 1 mSv ao feto.',
      useFor: ['Classificação de área', 'Monitoração individual', 'Relatório regulatório'],
      prerequisites: ['Dose efetiva', 'Dose equivalente'],
      relatedTopics: ['ALARA', 'Monitoração individual', 'Otimização'],
      projectIdeas: ['Verificar conformidade anual de dose ocupacional', 'Simular impacto de incidente no limite de área controlada'],
      professorQuestions: [
        'Dose investigacional: qual limiar dispara investigação na sua instituição?',
        'Como limites de tecido restringem procedimentos de mãos em intervencionismo?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-optimization',
      title: 'Otimização de proteção',
      type: 'principio',
      level: 'intermediario',
      whyItMatters:
        'Terceiro princípio ICRP — maximizar benefício e minimizar dose líquida através de otimização, não só limites.',
      shortExplanation:
        'Otimização busca melhor proteção para situação dada (constraint, dose reference level). Diferente de ALARA operacional e de justificação prévia. Ex.: DRLs em imagem médica.',
      useFor: ['Protocolo de imagem', 'Projeto de instalação', 'Revisão de prática'],
      prerequisites: ['ALARA', 'Justificação'],
      relatedTopics: ['ALARA', 'Limites de dose', 'Cultura de segurança'],
      projectIdeas: ['Comparar dose de protocolo CT com DRL nacional', 'Plano otimização pós-auditoria'],
      professorQuestions: [
        'Qual constraint você propõe abaixo do limite regulatório?',
        'Como DRL difere de limite legal na prática clínica?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-justification',
      title: 'Justificação de práticas',
      type: 'principio',
      level: 'basico',
      whyItMatters:
        'Primeiro princípio ICRP — exposição só ocorre se benefício líquido supera dano; prática injustificada não se otimiza.',
      shortExplanation:
        'Nova prática (fonte, procedimento) requer análise benefício vs. risco antes de implementação. Comitês de proteção avaliam. Exposição médica: benefício ao paciente justifica dose.',
      useFor: ['Autorização de nova fonte', 'Comité de ética', 'Licenciamento'],
      prerequisites: ['Conceitos de dose', 'Regulamentação básica'],
      relatedTopics: ['Otimização', 'ALARA', 'Cultura de segurança'],
      projectIdeas: ['Memorial de justificação para novo irradiador', 'Revisão benefício de exame repetido'],
      professorQuestions: [
        'Quem aprovou justificação na sua instituição e com quais critérios?',
        'Quando benefício deixa de justificar repetição de exame?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-safety-culture',
      title: 'Cultura de segurança radiológica',
      type: 'conceito-chave',
      level: 'intermediario',
      whyItMatters:
        'Regras falham sem comportamento — cultura de segurança previne normalização de desvio e complacência.',
      shortExplanation:
        'Elementos: liderança, aprendizado, responsabilidade, comunicação, questionamento. Eventos near-miss devem ser reportados sem punição. IAEA e WANO promovem frameworks aplicáveis à radiologia.',
      useFor: ['Gestão de instalação', 'Treinamento', 'Investigação de incidente'],
      prerequisites: ['Princípios de proteção', 'Regulamentação'],
      relatedTopics: ['ALARA', 'Defesa em profundidade', 'Cenários de emergência'],
      projectIdeas: ['Survey de cultura de segurança adaptado', 'Análise de near-miss anonimizado'],
      professorQuestions: [
        'Qual desvio normalizado você observou e como revertê-lo?',
        'Como liderança demonstra prioridade de segurança sobre produtividade?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-individual-monitoring',
      title: 'Monitoração individual de dose',
      type: 'metodo',
      level: 'intermediario',
      whyItMatters:
        'Dosímetro pessoal verifica se prática e blindagem funcionam — única forma de confirmar dose real do trabalhador.',
      shortExplanation:
        'TLD, OSL, filme ou dosímetro eletrônico usado em área controlada. Leitura periódica, registro e investigação de doses elevadas. Dosímetro de área complementa, não substitui, pessoal.',
      useFor: ['Programa de radioproteção', 'Conformidade CNEN', 'Investigação de dose'],
      prerequisites: ['Limites de dose', 'Dose efetiva'],
      relatedTopics: ['Limites de dose', 'ALARA', 'Otimização'],
      projectIdeas: ['Auditoria de uso correto de dosímetro (posição, troca)', 'Investigar pico de dose mensal'],
      professorQuestions: [
        'Dosímetro na posição correta durante o procedimento de maior dose?',
        'Como você distingue dose ocupacional de exposição médica no registro?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-source-term',
      title: 'Termo fonte (source term)',
      type: 'conceito-chave',
      level: 'avancado',
      whyItMatters:
        'Quantificar atividade, nuclídeos e pathways de release — termo fonte alimenta avaliação de dose e emergência.',
      shortExplanation:
        'Caracteriza inventário radioativo, taxa de liberação normal e acidental, forma físico-química e meteorologia local. Base para dose ambiental e planejamento de resposta.',
      useFor: ['Licenciamento', 'Plano de emergência', 'Transporte de material radioativo'],
      prerequisites: ['Decaimento', 'Meteorologia básica'],
      relatedTopics: ['Cenários de emergência', 'Defesa em profundidade', 'Tempo-distância-blindagem'],
      projectIdeas: ['Inventário de fontes seladas em instalação', 'Estimar release hipotético e dose a receptor crítico'],
      professorQuestions: [
        'Qual cenário de release acidental você modelou e quais suposições?',
        'Como forma química do release afeta dose inalatória?',
      ],
    }),
    definePowerIdea({
      id: 'prot-rad-emergency-scenarios',
      title: 'Cenários de emergência radiológica',
      type: 'metodo',
      level: 'avancado',
      whyItMatters:
        'Emergência exige resposta treinada — cenários definem ações, zonas de exclusão e comunicação antes do evento.',
      shortExplanation:
        'Classificação (5 IAEA ou escalas nacionais), zonas (quente, warm, cold), contramedidas (iodo, evacuação, sheltering). Exercícios periódicos e plano atualizado. Diferente acidente industrial vs. médico vs. RDD.',
      useFor: ['Plano de emergência', 'Treinamento', 'Coordenação com autoridades'],
      prerequisites: ['Termo fonte', 'Tempo-distância-blindagem'],
      relatedTopics: ['Termo fonte', 'Defesa em profundidade', 'Cultura de segurança'],
      projectIdeas: ['Exercício tabletop de extravio de fonte', 'Fluxograma decisão evacuação vs. abrigo'],
      professorQuestions: [
        'Quem é o comando unificado no seu plano e quando acioná-lo?',
        'Como comunicação pública evita pânico sem omitir risco?',
      ],
    }),
  ],
};
