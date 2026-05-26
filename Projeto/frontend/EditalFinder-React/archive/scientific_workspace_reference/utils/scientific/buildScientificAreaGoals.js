import { interestLabelById } from './scientificInterestsConfig';
import { AREA_XP_PER_SUBLEVEL } from './scientificXpConstants';
import { collectBlockProgressItems } from './buildStudyProgressSummary';
import { getProgressStatusFromMap } from './scientificStudyProgressStorage';
function countDominados(items, studyProgress, predicate) {
  return items.filter((i) => {
    const st = getProgressStatusFromMap(studyProgress, i.progressKey);
    return st === 'dominado' && predicate(i);
  }).length;
}

function sessionsInArea(sessions, canonicalKey) {
  return (sessions || []).filter((s) => s.canonicalKey === canonicalKey).length;
}

/**
 * Metas para subir nível de área (Fase 2L).
 * @param {object} params
 */
export function buildScientificAreaGoals({
  canonicalKey,
  areaLabel,
  block,
  studyProgress = {},
  studySessions = [],
  notebookItems = [],
  bookProgress = {},
  xpByArea = 0,
}) {
  const items = block ? collectBlockProgressItems(block) : [];
  const label = areaLabel || interestLabelById(canonicalKey) || canonicalKey;

  const foundationsDominados = countDominados(
    items,
    studyProgress,
    (i) => i.kind === 'theory' && i.progressKey.includes('::foundations::'),
  );

  const powerDominados = countDominados(items, studyProgress, (i) => i.kind === 'powerIdea');

  const projectDominados = countDominados(items, studyProgress, (i) => i.kind === 'project');

  const hasBook =
    Object.values(bookProgress || {}).some(
      (b) => b.area === canonicalKey && (b.status === 'lido' || b.status === 'lendo'),
    ) ||
    (notebookItems || []).some(
      (n) =>
        (n.tipo === 'livro' || n.notebookGroup === 'livros') &&
        (n.interesses || []).includes(canonicalKey),
    );

  const hasProjectSaved = (notebookItems || []).some(
    (n) =>
      (n.contentCategory === 'projeto' || n.level) &&
      (n.interesses || []).includes(canonicalKey),
  );

  const sessionCount = sessionsInArea(studySessions, canonicalKey);
  const areaXp = xpByArea || 0;
  const currentAreaLevel = Math.max(1, Math.floor(areaXp / AREA_XP_PER_SUBLEVEL) + 1);
  const nextAreaLevel = currentAreaLevel + 1;

  const goals = [
    {
      id: 'foundations_3',
      label: 'Dominar 3 tópicos de fundamentos',
      target: 3,
      current: foundationsDominados,
    },
    {
      id: 'power_1',
      label: 'Dominar 1 ideia poderosa',
      target: 1,
      current: powerDominados,
    },
    {
      id: 'book_1',
      label: 'Salvar ou ler 1 livro',
      target: 1,
      current: hasBook ? 1 : 0,
    },
    {
      id: 'project_1',
      label: 'Iniciar 1 projeto (salvo ou dominado)',
      target: 1,
      current: Math.max(projectDominados, hasProjectSaved ? 1 : 0) >= 1 ? 1 : 0,
    },
    {
      id: 'sessions_2',
      label: 'Fazer 2 sessões de estudo',
      target: 2,
      current: sessionCount,
    },
  ];

  const completedCount = goals.filter((g) => g.current >= g.target).length;

  return {
    canonicalKey,
    areaLabel: label,
    currentAreaLevel,
    nextAreaLevel,
    goals,
    completedCount,
    totalGoals: goals.length,
    readyForNextLevel: completedCount >= goals.length,
  };
}

/**
 * @param {string[]} activeInterests
 * @param {object} blocksByKey — Record<canonicalKey, block>
 * @param {object} ctx
 */
export function buildAreaGoalsForActiveInterests(activeInterests, blocksByKey, ctx = {}) {
  const keys = [...new Set(activeInterests)].slice(0, 6);
  return keys
    .map((id) => {
      const canonicalKey = id;
      const block = blocksByKey[canonicalKey];
      if (!block) return null;
      return buildScientificAreaGoals({
        canonicalKey,
        block,
        studyProgress: ctx.studyProgress,
        studySessions: ctx.studySessions,
        notebookItems: ctx.notebookItems,
        bookProgress: ctx.bookProgress,
        xpByArea: ctx.xpState?.byArea?.[canonicalKey] || 0,
      });
    })
    .filter(Boolean);
}
