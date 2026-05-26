import { logScientificWorkspace } from './scientificWorkspaceLog';

export const SCIENTIFIC_MASTERY_STORAGE_KEY = 'scientific_workspace_mastery_checks';

export function loadScientificMasteryChecks() {
  try {
    const raw = localStorage.getItem(SCIENTIFIC_MASTERY_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
  } catch {
    return {};
  }
}

export function saveScientificMasteryChecks(map) {
  try {
    localStorage.setItem(SCIENTIFIC_MASTERY_STORAGE_KEY, JSON.stringify(map || {}));
  } catch {
    /* ignore */
  }
}

/**
 * @param {object} record
 */
export function upsertMasteryCheck(record) {
  const current = loadScientificMasteryChecks();
  const key = record.progressKey;
  if (!key) return current;

  const next = {
    ...current,
    [key]: {
      ...current[key],
      ...record,
      updatedAt: new Date().toISOString(),
      confirmedAt: record.confirmedAt || new Date().toISOString(),
    },
  };
  saveScientificMasteryChecks(next);
  logScientificWorkspace('mastery_check_saved', { progressKey: key });
  return next;
}
