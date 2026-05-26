import { logScientificWorkspace } from './scientificWorkspaceLog';
import { PROJECT_LEVEL_FILTER_ALL } from './scientificProjectLevels';

const STORAGE_KEY = 'scientific_workspace_project_level_filter';

export function loadProjectLevelFilter() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return PROJECT_LEVEL_FILTER_ALL;
    const v = String(raw).trim();
    return v || PROJECT_LEVEL_FILTER_ALL;
  } catch {
    return PROJECT_LEVEL_FILTER_ALL;
  }
}

export function saveProjectLevelFilter(levelId) {
  try {
    localStorage.setItem(STORAGE_KEY, levelId);
    logScientificWorkspace('project_level_filter_changed', { level: levelId });
  } catch {
    /* quota */
  }
}
