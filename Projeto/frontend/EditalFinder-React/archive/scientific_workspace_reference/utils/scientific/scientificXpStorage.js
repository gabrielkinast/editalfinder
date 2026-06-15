import { XP_BONUS_ANSWERS_FILLED, XP_BY_KIND } from './scientificXpConstants';
import { logScientificWorkspace } from './scientificWorkspaceLog';

export const SCIENTIFIC_XP_STORAGE_KEY = 'scientific_workspace_xp';

const EMPTY_STATE = {
  totalXp: 0,
  byArea: {},
  byKind: {},
  awardedKeys: {},
  events: [],
};

export function loadScientificXp() {
  try {
    const raw = localStorage.getItem(SCIENTIFIC_XP_STORAGE_KEY);
    if (!raw) return { ...EMPTY_STATE };
    const parsed = JSON.parse(raw);
    return {
      ...EMPTY_STATE,
      ...parsed,
      byArea: parsed.byArea || {},
      byKind: parsed.byKind || {},
      awardedKeys: parsed.awardedKeys || {},
      events: Array.isArray(parsed.events) ? parsed.events : [],
    };
  } catch {
    return { ...EMPTY_STATE };
  }
}

export function saveScientificXp(state) {
  try {
    localStorage.setItem(SCIENTIFIC_XP_STORAGE_KEY, JSON.stringify(state));
  } catch {
    /* ignore */
  }
}

export function hasXpAwardedForKey(xpState, progressKey) {
  return Boolean(xpState?.awardedKeys?.[progressKey]);
}

/**
 * @param {object} params
 * @returns {{ state: object, awarded: boolean, xp: number }}
 */
export function awardScientificXp(params = {}) {
  const {
    progressKey,
    canonicalKey = '',
    kind = 'theory',
    title = '',
    reason = 'dominio_confirmado',
    bonusAnswers = false,
    customXp,
  } = params;

  const state = loadScientificXp();
  if (progressKey && hasXpAwardedForKey(state, progressKey)) {
    logScientificWorkspace('xp_duplicate_prevented', {
      progressKey,
      reason: params.reason || 'already_awarded',
      kind,
    });
    return { state, awarded: false, xp: 0 };
  }

  let xp = customXp ?? XP_BY_KIND[kind] ?? 10;
  if (bonusAnswers) xp += XP_BONUS_ANSWERS_FILLED;

  const next = {
    ...state,
    totalXp: state.totalXp + xp,
    byArea: { ...state.byArea },
    byKind: { ...state.byKind },
    awardedKeys: { ...state.awardedKeys },
    events: [...state.events],
  };

  if (canonicalKey) {
    next.byArea[canonicalKey] = (next.byArea[canonicalKey] || 0) + xp;
  }
  next.byKind[kind] = (next.byKind[kind] || 0) + xp;

  if (progressKey) {
    next.awardedKeys[progressKey] = xp;
  }

  const event = {
    id: `xp-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    date: new Date().toISOString(),
    canonicalKey,
    kind,
    title,
    xp,
    reason,
    progressKey: progressKey || null,
  };
  next.events.unshift(event);
  if (next.events.length > 200) next.events = next.events.slice(0, 200);

  saveScientificXp(next);
  logScientificWorkspace('xp_awarded', { xp, kind, canonicalKey, progressKey });

  return { state: next, awarded: true, xp };
}
