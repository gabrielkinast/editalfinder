import { getProgressStatusFromMap } from './scientificStudyProgressStorage';
export const SCIENTIFIC_BADGE_DEFINITIONS = [
  {
    id: 'primeiros_passos',
    label: 'Primeiros passos',
    description: 'Primeiro tópico marcado como dominado.',
    icon: '🎯',
  },
  {
    id: 'leitor_cientifico',
    label: 'Leitor científico',
    description: 'Primeiro livro marcado como lido/estudado.',
    icon: '📚',
  },
  {
    id: 'cacador_teoremas',
    label: 'Caçador de teoremas',
    description: '5 ideias poderosas dominadas.',
    icon: '💡',
  },
  {
    id: 'nuclear_iniciante',
    label: 'Nuclear iniciante',
    description: '5 itens dominados em física nuclear.',
    icon: '☢️',
  },
  {
    id: 'computacao_iniciante',
    label: 'Computação científica iniciante',
    description: '5 itens dominados em computação científica.',
    icon: '💻',
  },
  {
    id: 'monte_carlo_iniciado',
    label: 'Monte Carlo iniciado',
    description: '3 itens dominados em Monte Carlo.',
    icon: '🎲',
  },
  {
    id: 'projeto_em_movimento',
    label: 'Projeto em movimento',
    description: 'Primeiro projeto marcado como dominado.',
    icon: '🔬',
  },
  {
    id: 'rota_ativa',
    label: 'Rota ativa',
    description: 'Primeira rota por objetivo salva no caderno.',
    icon: '🧭',
  },
  {
    id: 'interdisciplinar',
    label: 'Interdisciplinar',
    description: 'XP em 5 áreas diferentes.',
    icon: '🌐',
  },
  {
    id: 'pre_pesquisador',
    label: 'Pré-pesquisador',
    description: '1000 XP total acumulados.',
    icon: '🏆',
  },
];

function countDominados(studyProgress, predicate) {
  let n = 0;
  for (const [key, val] of Object.entries(studyProgress || {})) {
    if (val?.status !== 'dominado') continue;
    if (predicate(key)) n += 1;
  }
  return n;
}

function countDominadosInArea(studyProgress, area) {
  return countDominados(studyProgress, (k) => k.startsWith(`${area}::`));
}

function countDominadosPowerIdeas(studyProgress) {
  return countDominados(studyProgress, (k) => k.includes('::powerIdea::'));
}

/**
 * @param {object} input
 */
export function buildScientificBadges(input = {}) {
  const studyProgress = input.studyProgress || {};
  const xpState = input.xpState || {};
  const notebookItems = input.notebookItems || [];
  const bookProgress = input.bookProgress || {};

  const anyDominado = Object.values(studyProgress).some((v) => v?.status === 'dominado');
  const bookLido =
    Object.values(bookProgress).some((b) => b.status === 'lido') ||
    countDominados(studyProgress, (k) => k.includes('::book::')) > 0;
  const hasRoute = notebookItems.some(
    (i) => String(i.tipo || '').includes('rota') || i.notebookGroup === 'rotas',
  );
  const areasWithXp = Object.keys(xpState.byArea || {}).filter((k) => xpState.byArea[k] > 0).length;

  const conditions = {
    primeiros_passos: anyDominado,
    leitor_cientifico: bookLido,
    cacador_teoremas: countDominadosPowerIdeas(studyProgress) >= 5,
    nuclear_iniciante: countDominadosInArea(studyProgress, 'nuclear') >= 5,
    computacao_iniciante: countDominadosInArea(studyProgress, 'computacao_cientifica') >= 5,
    monte_carlo_iniciado: countDominadosInArea(studyProgress, 'monte_carlo') >= 3,
    projeto_em_movimento: countDominados(studyProgress, (k) => k.includes('::project::')) >= 1,
    rota_ativa: hasRoute,
    interdisciplinar: areasWithXp >= 5,
    pre_pesquisador: (xpState.totalXp || 0) >= 1000,
  };

  return SCIENTIFIC_BADGE_DEFINITIONS.map((def) => ({
    ...def,
    unlocked: Boolean(conditions[def.id]),
  }));
}
