/**
 * Perguntas heurísticas para verificação de domínio (Fase 2K).
 * @param {object} input
 */
export function buildMasteryCheckQuestions(input = {}) {
  const {
    canonicalKey = '',
    kind = 'theory',
    title = 'Item',
    level = '',
    relatedTopics = [],
    whyItMatters = '',
    shortExplanation = '',
  } = input;

  const rel = relatedTopics?.length
    ? relatedTopics.slice(0, 3).join(', ')
    : canonicalKey.replace(/_/g, ' ');

  const templates = {
    theory: [
      {
        type: 'explicar_com_suas_palavras',
        question: `Explique "${title}" com suas próprias palavras, sem copiar definição de livro.`,
        expectedSkill: 'Compreensão conceitual',
      },
      {
        type: 'exemplo_aplicacao',
        question: `Dê um exemplo concreto de aplicação de "${title}" em ${canonicalKey.replace(/_/g, ' ')} ou em um projeto.`,
        expectedSkill: 'Transferência para contexto',
      },
      {
        type: 'conexao_com_area',
        question: `Quais pré-requisitos ou conceitos relacionados (${rel}) você precisa dominar antes de usar "${title}" com segurança?`,
        expectedSkill: 'Mapa de dependências',
      },
    ],
    powerIdea: [
      {
        type: 'explicar_com_suas_palavras',
        question: whyItMatters
          ? `Por que "${title}" muda o jeito de pensar a área? Resuma com suas palavras.`
          : `Por que a ideia "${title}" é poderosa nesta área?`,
        expectedSkill: 'Visão estratégica',
      },
      {
        type: 'exemplo_aplicacao',
        question: `Onde "${title}" aparece em um problema real (simulação, experimento, projeto)?`,
        expectedSkill: 'Aplicação em pesquisa',
      },
      {
        type: 'erro_comum',
        question: `Qual erro comum alguém comete ao aplicar "${title}" sem entender ${shortExplanation ? 'o fundamento' : 'o contexto'}?`,
        expectedSkill: 'Autocrítica',
      },
    ],
    book: [
      {
        type: 'interpretacao',
        question: `Qual capítulo ou conceito principal de "${title}" você estudou até agora?`,
        expectedSkill: 'Escopo da leitura',
      },
      {
        type: 'explicar_com_suas_palavras',
        question: `O que este livro esclareceu que antes estava confuso para você?`,
        expectedSkill: 'Síntese pessoal',
      },
      {
        type: 'exemplo_aplicacao',
        question: `Como você aplicaria o que aprendeu em "${title}" em um projeto ou IC/TCC?`,
        expectedSkill: 'Projeção prática',
      },
    ],
    project: [
      {
        type: 'explicar_com_suas_palavras',
        question: `Qual problema o projeto "${title}" resolve ou explora?`,
        expectedSkill: 'Objetivo claro',
      },
      {
        type: 'comparacao',
        question: `Quais hipóteses ou simplificações você usaria (ou usou) neste projeto?`,
        expectedSkill: 'Modelagem',
      },
      {
        type: 'mini_problema',
        question: `Como você validaria o resultado (dados, ordem de grandeza, benchmark)?`,
        expectedSkill: 'Verificação',
      },
    ],
    question: [
      {
        type: 'explicar_com_suas_palavras',
        question: `Qual resposta você espera obter do orientador sobre: "${title}"?`,
        expectedSkill: 'Expectativa de mentoria',
      },
      {
        type: 'conexao_com_area',
        question: `Que conceito da trilha motivou esta pergunta?`,
        expectedSkill: 'Ligação com formação',
      },
      {
        type: 'interpretacao',
        question: `Como a resposta pode mudar sua rota de estudo ou próximo projeto?`,
        expectedSkill: 'Planejamento',
      },
    ],
    route_step: [
      {
        type: 'exemplo_aplicacao',
        question: `O que você já fez ou fará em relação ao passo "${title}"?`,
        expectedSkill: 'Execução',
      },
      {
        type: 'conexao_com_area',
        question: `Como este passo se conecta aos seus interesses ativos em ${canonicalKey.replace(/_/g, ' ')}?`,
        expectedSkill: 'Coerência da rota',
      },
      {
        type: 'erro_comum',
        question: `Qual obstáculo você antecipa neste passo e como contorná-lo?`,
        expectedSkill: 'Antecipação',
      },
    ],
  };

  const base = templates[kind] || templates.theory;
  return base.map((q, i) => ({
    id: `${kind}-${canonicalKey}-${i}`,
    ...q,
    level,
  }));
}
