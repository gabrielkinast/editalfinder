import { buildStudySessionItemPool } from './buildStudySessionItemPool';
import { rankStudySessionItems } from './rankStudySessionItems';
import { filterStudySessionPool, limitStudySessionQuantity } from './filterStudySessionPool';
import { buildStudySessionRecommendedSelection } from './buildStudySessionRecommendedSelection';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { buildRouteStepProgressKey } from './scientificStudyProgressKeys';
import { logScientificWorkspace } from './scientificWorkspaceLog';
import { getGoalRouteCanonicalKeys } from './studySessionAreaScope';

/**
 * Pool → rank → filter → limit (Fase 2L-B / 2L-C).
 */
export function getStudySessionPipeline(params = {}) {
  const {
    studyBlocks = [],
    activeInterests = [],
    areaSelection = '',
    selectedCanonicalKey = '',
    goalRoutes: rawGoalRoutes = [],
    goalRouteId = null,
    progressState = {},
    bookProgress = {},
    notebookItems: rawNotebookItems = [],
    focus = 'theory',
    level = '',
    status = '',
    search = '',
    origin = '',
    quantity = 20,
    plannedMinutes = 30,
  } = params;

  const scope = areaSelection || selectedCanonicalKey;
  const goalRoutes = Array.isArray(rawGoalRoutes) ? rawGoalRoutes : [];
  const notebookItems = Array.isArray(rawNotebookItems) ? rawNotebookItems : [];

  const primaryGoalRoute =
    goalRoutes.find((r) => r.id === goalRouteId) || goalRoutes[0] || null;
  const goalRouteCanonicalKeys = getGoalRouteCanonicalKeys(primaryGoalRoute);

  const pool = buildStudySessionItemPool({
    studyBlocks,
    activeInterests,
    goalRoutes,
    progressState,
    bookProgress,
    notebookItems,
    focus,
  });

  const notebookKeys = new Set();
  for (const entry of notebookItems || []) {
    const k = getScientificNotebookEntryKey(entry);
    if (k) notebookKeys.add(k);
  }

  const goalRouteStepKeys = new Set();
  for (const route of goalRoutes || []) {
    for (const step of route.steps || []) {
      goalRouteStepKeys.add(buildRouteStepProgressKey(route.id, step));
    }
  }

  const ranked = rankStudySessionItems(pool, {
    areaSelection: scope,
    focus,
    progressState,
    bookProgress,
    notebookKeys,
    goalRouteStepKeys,
    goalRouteCanonicalKeys,
  });

  const { items: filtered, emptyFocusMessage, totalBefore, totalAfter } = filterStudySessionPool(
    ranked,
    {
      areaSelection: scope,
      focus,
      level,
      status,
      search,
      origin,
      goalRouteCanonicalKeys,
      goalRouteId: primaryGoalRoute?.id || goalRouteId,
    },
  );

  const distinctAreas = new Set(filtered.map((i) => i.canonicalKey).filter(Boolean)).size;

  const visible = limitStudySessionQuantity(filtered, quantity);

  const baseForRecommend = filtered.length ? filtered : ranked;

  const recommendedKeys = buildStudySessionRecommendedSelection(baseForRecommend, {
    focus,
    plannedMinutes,
  });

  return {
    pool,
    ranked,
    filtered,
    visible,
    recommendedKeys,
    emptyFocusMessage,
    totalBefore,
    totalAfter,
    displayedCount: visible.length,
    poolMeta: {
      totalInScope: totalAfter,
      distinctAreas,
      areaSelection: scope,
    },
  };
}

export function logStudySessionRecommendedSelected(count, focus, duration) {
  logScientificWorkspace('study_session_recommended_selected', {
    count,
    focus,
    duration,
  });
}
