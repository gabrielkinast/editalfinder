import { logScientificWorkspace } from './scientificWorkspaceLog';
import { DEFAULT_STUDY_PROGRESS_STATUS, STUDY_PROGRESS_STATUSES } from './scientificStudyProgressConstants';

export const SCIENTIFIC_STUDY_PROGRESS_STORAGE_KEY = 'scientific_workspace_study_progress';

/**
 * @returns {Record<string, { status: string, updatedAt: string }>}
 */
export function loadScientificStudyProgress() {
  try {
    const raw = localStorage.getItem(SCIENTIFIC_STUDY_PROGRESS_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    const out = {};
    for (const [key, val] of Object.entries(parsed)) {
      if (!val || typeof val !== 'object') continue;
      const status = STUDY_PROGRESS_STATUSES.includes(val.status) ? val.status : DEFAULT_STUDY_PROGRESS_STATUS;
      out[key] = {
        status,
        updatedAt: typeof val.updatedAt === 'string' ? val.updatedAt : new Date().toISOString(),
      };
    }
    return out;
  } catch {
    return {};
  }
}

/**
 * @param {Record<string, { status: string, updatedAt: string }>} map
 */
export function saveScientificStudyProgress(map) {
  try {
    localStorage.setItem(SCIENTIFIC_STUDY_PROGRESS_STORAGE_KEY, JSON.stringify(map || {}));
  } catch {
    /* ignore quota */
  }
}

/**
 * @param {string} progressKey
 * @param {string} status
 * @returns {Record<string, { status: string, updatedAt: string }>}
 */
export function setScientificStudyProgressStatus(progressKey, status) {
  const current = loadScientificStudyProgress();
  const next = { ...current };
  if (!status || status === DEFAULT_STUDY_PROGRESS_STATUS) {
    delete next[progressKey];
  } else {
    next[progressKey] = {
      status,
      updatedAt: new Date().toISOString(),
    };
  }
  saveScientificStudyProgress(next);
  return next;
}

/**
 * @param {Record<string, { status: string, updatedAt: string }>} map
 * @param {string} progressKey
 */
export function getProgressStatusFromMap(map, progressKey) {
  return map?.[progressKey]?.status || DEFAULT_STUDY_PROGRESS_STATUS;
}
