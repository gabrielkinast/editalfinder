import {
  AREA_SCOPE_GOAL_ROUTE,
  isSpecialAreaScope,
} from './studySessionAreaScope';

const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

function isOldDominado(item, progressState = {}) {
  if (item.status !== 'dominado') return false;
  const updatedAt = progressState[item.progressKey]?.updatedAt;
  if (!updatedAt) return true;
  return Date.now() - new Date(updatedAt).getTime() >= SEVEN_DAYS_MS;
}

/**
 * @param {Array<object>} items
 * @param {object} params
 */
export function rankStudySessionItems(items = [], params = {}) {
  const {
    areaSelection = '',
    selectedCanonicalKey = '',
    focus = 'theory',
    progressState = {},
    bookProgress = {},
    notebookKeys = new Set(),
    goalRouteStepKeys = new Set(),
    goalRouteCanonicalKeys = new Set(),
  } = params;

  const areaScope = areaSelection || selectedCanonicalKey;

  const scored = items.map((item) => {
    let score = item.priority ?? 50;

    if (areaScope === AREA_SCOPE_GOAL_ROUTE) {
      if (goalRouteCanonicalKeys.has(item.canonicalKey)) score -= 28;
      if (goalRouteStepKeys.has(item.progressKey)) score -= 22;
      else if (item.kind === 'goalRouteStep') score -= 18;
    } else if (areaScope && !isSpecialAreaScope(areaScope)) {
      if (item.canonicalKey === areaScope) score -= 30;
      else score += 8;
    }

    const st = item.status || 'none';
    if (st === 'estudando') score -= 12;
    if (st === 'a_estudar') score -= 8;
    if (st === 'ignorar_agora') score += 40;

    if (goalRouteStepKeys.has(item.progressKey)) score -= 6;
    if (notebookKeys.has(item.progressKey) || item.metadata?.inNotebook) score -= 5;

    const bp = bookProgress[item.progressKey];
    if (bp?.status === 'lendo') score -= 10;

    if (focus === 'powerIdea' && item.kind === 'powerIdea') score -= 15;
    if (focus === 'project' && item.kind === 'project') score -= 15;
    if (focus === 'book' && item.kind === 'book') score -= 15;
    if (focus === 'professorQuestion' && item.kind === 'professorQuestion') score -= 15;
    if (focus === 'theory' && item.kind === 'theory') score -= 15;

    if (focus === 'review') {
      if (st === 'estudando') score -= 25;
      else if (isOldDominado(item, progressState)) score -= 18;
      else if (bp?.status === 'lendo') score -= 20;
      else if (item.kind === 'powerIdea' && st !== 'dominado' && st !== 'ignorar_agora') score -= 14;
      else if (item.kind === 'project' && (st === 'estudando' || st === 'a_estudar')) score -= 12;
      else if (item.kind === 'professorQuestion') score -= 10;
      else if (item.kind === 'goalRouteStep') score -= 8;
      else if (st === 'dominado') score += 15;
    }

    if (focus !== 'review' && st === 'dominado') score += 20;

    return { ...item, _rankScore: score };
  });

  scored.sort((a, b) => a._rankScore - b._rankScore || a.title.localeCompare(b.title));
  return scored.map(({ _rankScore, ...rest }) => rest);
}
