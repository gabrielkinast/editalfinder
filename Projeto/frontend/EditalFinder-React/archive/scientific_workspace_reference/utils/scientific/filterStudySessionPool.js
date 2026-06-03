import { SESSION_FOCUS_OPTIONS, SESSION_LEVEL_OPTIONS } from './scientificStudySessionConstants';
import { logScientificWorkspace } from './scientificWorkspaceLog';
import {
  AREA_SCOPE_ALL_ACTIVE,
  AREA_SCOPE_GOAL_ROUTE,
  AREA_SCOPE_REVIEW_GENERAL,
  isSpecialAreaScope,
} from './studySessionAreaScope';

function normalizeSeg(s) {
  return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

function matchesLevel(item, levelId) {
  if (!levelId) return true;
  const opt = SESSION_LEVEL_OPTIONS.find((o) => o.id === levelId);
  if (!opt) return true;
  const seg = normalizeSeg(item.segment);
  const lvl = normalizeSeg(item.level);
  const segs = (opt.segments || []).map(normalizeSeg);
  const levels = (opt.levels || []).map(normalizeSeg);
  return segs.some((s) => seg.includes(s) || s.includes(seg)) || levels.some((l) => lvl.includes(l) || l.includes(lvl));
}

function matchesFocus(item, focus) {
  const opt = SESSION_FOCUS_OPTIONS.find((f) => f.id === focus);
  if (!opt || !opt.kinds) return true;
  return opt.kinds.includes(item.kind);
}

/**
 * @param {Array<object>} items
 * @param {object} filters
 */
export function filterStudySessionPool(items = [], filters = {}) {
  const {
    areaSelection = '',
    selectedCanonicalKey = '',
    focus = 'theory',
    level = '',
    status = '',
    search = '',
    origin = '',
    goalRouteCanonicalKeys = null,
    goalRouteId = '',
  } = filters;

  const scope = areaSelection || selectedCanonicalKey;
  const totalBefore = items.length;
  let out = items;

  if (scope === AREA_SCOPE_GOAL_ROUTE && goalRouteCanonicalKeys?.size) {
    const keys = goalRouteCanonicalKeys;
    out = out.filter(
      (i) =>
        keys.has(i.canonicalKey) ||
        i.kind === 'goalRouteStep' ||
        i.metadata?.routeId === goalRouteId ||
        String(i.segment || '') === String(goalRouteId || ''),
    );
  } else if (
    scope &&
    scope !== AREA_SCOPE_ALL_ACTIVE &&
    scope !== AREA_SCOPE_REVIEW_GENERAL &&
    !isSpecialAreaScope(scope)
  ) {
    out = out.filter((i) => i.canonicalKey === scope);
  }

  if (focus && focus !== 'review' && focus !== 'mixed') {
    out = out.filter((i) => matchesFocus(i, focus));
  }

  if (level) {
    out = out.filter((i) => matchesLevel(i, level));
  }

  if (status) {
    if (status === 'none') {
      out = out.filter((i) => i.status === 'none');
    } else {
      out = out.filter((i) => i.status === status);
    }
  }

  const q = String(search || '')
    .trim()
    .toLowerCase();
  if (q) {
    out = out.filter((i) => i.searchableText.includes(q) || i.title.toLowerCase().includes(q));
  }

  if (origin) {
    out = out.filter((i) => i.source === origin);
  }

  logScientificWorkspace('study_session_items_filtered', {
    totalBefore,
    totalAfter: out.length,
    areaSelection: scope || undefined,
    focus,
    level,
    status,
    origin: origin || undefined,
    search: q || undefined,
  });

  const focusOpt = SESSION_FOCUS_OPTIONS.find((f) => f.id === focus);
  const emptyFocusMessage =
    out.length === 0 && focusOpt?.kinds
      ? `Nenhum item desse tipo nesta área. Tente Misto ou outra área.`
      : null;

  return { items: out, emptyFocusMessage, totalBefore, totalAfter: out.length };
}

/**
 * @param {Array<object>} items
 * @param {number} quantity — 0 = todos
 */
export function limitStudySessionQuantity(items, quantity) {
  if (!quantity || quantity <= 0) return items;
  return items.slice(0, quantity);
}
