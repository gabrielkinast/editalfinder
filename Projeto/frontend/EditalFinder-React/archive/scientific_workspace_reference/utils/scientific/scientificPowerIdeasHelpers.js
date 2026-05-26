/**
 * Factory para ideias poderosas (Fase 2J).
 * @param {object} o
 */
export function definePowerIdea(o) {
  return {
    useFor: [],
    prerequisites: [],
    relatedTopics: [],
    projectIdeas: [],
    professorQuestions: [],
    ...o,
  };
}

export const POWER_IDEA_TYPE_LABELS = {
  teorema: 'Teorema',
  principio: 'Princípio',
  lei: 'Lei',
  metodo: 'Método',
  'conceito-chave': 'Conceito-chave',
  aproximacao: 'Aproximação',
  'identidade-matematica': 'Identidade matemática',
  'ferramenta-computacional': 'Ferramenta computacional',
};

export const POWER_IDEA_LEVEL_LABELS = {
  basico: 'Básico',
  intermediario: 'Intermediário',
  avancado: 'Avançado',
  pesquisa: 'Pesquisa',
};
