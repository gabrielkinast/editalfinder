const SCIENTIFIC_STORAGE_PREFIX = 'scientific_workspace_';

/**
 * Remove apenas chaves do Workspace Científico no localStorage.
 * @returns {string[]} chaves removidas
 */
export function clearScientificWorkspaceLocalCache() {
  const removed = [];
  try {
    for (let i = localStorage.length - 1; i >= 0; i -= 1) {
      const key = localStorage.key(i);
      if (key && key.startsWith(SCIENTIFIC_STORAGE_PREFIX)) {
        localStorage.removeItem(key);
        removed.push(key);
      }
    }
  } catch {
    /* ignore */
  }
  return removed;
}

export const SCIENTIFIC_LOCAL_STORAGE_KEYS = [
  'scientific_workspace_interests',
  'scientific_workspace_notebook',
  'scientific_workspace_project_level_filter',
  'scientific_workspace_study_progress',
  'scientific_workspace_mastery_checks',
  'scientific_workspace_xp',
  'scientific_workspace_book_progress',
  'scientific_workspace_study_sessions',
];
