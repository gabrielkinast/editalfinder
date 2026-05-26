import { interestLabelById } from './scientificInterestsConfig';
import { AREA_XP_PER_SUBLEVEL, GLOBAL_LEVELS } from './scientificXpConstants';

function globalLevelForXp(totalXp) {
  let current = GLOBAL_LEVELS[0];
  for (const row of GLOBAL_LEVELS) {
    if (totalXp >= row.minXp) current = row;
  }
  const idx = GLOBAL_LEVELS.indexOf(current);
  const next = GLOBAL_LEVELS[idx + 1] || null;
  const xpIntoLevel = totalXp - current.minXp;
  const xpToNext = next ? next.minXp - totalXp : 0;
  const range = next ? next.minXp - current.minXp : 1;
  const percent = next ? Math.min(100, Math.round((xpIntoLevel / range) * 100)) : 100;

  return {
    level: current.level,
    label: current.label,
    totalXp,
    xpToNext: Math.max(0, xpToNext),
    nextLevelLabel: next?.label || null,
    percentToNext: percent,
  };
}

function areaLevelForXp(areaXp) {
  const sub = Math.max(1, Math.floor(areaXp / AREA_XP_PER_SUBLEVEL) + 1);
  return { areaLevel: sub, areaXp };
}

/**
 * @param {object} xpState
 */
export function buildScientificLevelSummary(xpState = {}) {
  const global = globalLevelForXp(xpState.totalXp || 0);
  const byArea = xpState.byArea || {};
  const topAreas = Object.entries(byArea)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([key, xp]) => ({
      canonicalKey: key,
      label: interestLabelById(key) || key,
      xp,
      ...areaLevelForXp(xp),
    }));

  const lastEvent = xpState.events?.[0] || null;

  return {
    global,
    topAreas,
    lastEvent,
    byKind: xpState.byKind || {},
  };
}
