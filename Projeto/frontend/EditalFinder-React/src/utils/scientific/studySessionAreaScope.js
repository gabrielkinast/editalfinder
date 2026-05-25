/** Valores especiais do seletor de área (Fase 2L-C). */
export const AREA_SCOPE_ALL_ACTIVE = 'all_active';
export const AREA_SCOPE_GOAL_ROUTE = 'goal_route';
export const AREA_SCOPE_REVIEW_GENERAL = 'review_general';

export function isSpecialAreaScope(value) {
  return (
    value === AREA_SCOPE_ALL_ACTIVE ||
    value === AREA_SCOPE_GOAL_ROUTE ||
    value === AREA_SCOPE_REVIEW_GENERAL
  );
}

/**
 * @param {object} primaryGoalRoute
 */
export function getGoalRouteCanonicalKeys(primaryGoalRoute) {
  if (!primaryGoalRoute) return new Set();
  const keys = new Set(primaryGoalRoute.relatedCanonicalKeys || []);
  return keys;
}
