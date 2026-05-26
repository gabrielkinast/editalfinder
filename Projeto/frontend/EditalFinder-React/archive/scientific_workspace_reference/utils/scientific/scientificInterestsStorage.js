import { logScientificWorkspace } from './scientificWorkspaceLog';
import { DEFAULT_SCIENTIFIC_INTEREST_IDS } from './scientificInterestsConfig';
import { safeJsonParse } from './safeJsonParse';

const STORAGE_KEY = 'scientific_workspace_interests';

export function loadScientificInterests() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      logScientificWorkspace('interests_loaded', { count: DEFAULT_SCIENTIFIC_INTEREST_IDS.length, default: true });
      return [...DEFAULT_SCIENTIFIC_INTEREST_IDS];
    }
    const parsed = safeJsonParse(raw, null, { context: 'interests' });
    const list = Array.isArray(parsed) ? parsed.filter((x) => typeof x === 'string') : [];
    logScientificWorkspace('interests_loaded', { count: list.length });
    return list.length ? list : [...DEFAULT_SCIENTIFIC_INTEREST_IDS];
  } catch {
    return [...DEFAULT_SCIENTIFIC_INTEREST_IDS];
  }
}

export function saveScientificInterests(ids) {
  const list = Array.isArray(ids) ? ids : [];
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    logScientificWorkspace('interests_changed', { count: list.length, ids: list });
  } catch {
    /* quota */
  }
}
