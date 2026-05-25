import { DASHBOARD_SCOPE_ALL } from './dashboardClassification';

export const DASHBOARD_SCOPE_STORAGE_KEY = 'dashboard_scope_filter';

/**
 * @returns {string}
 */
export function loadDashboardScopePreference() {
  try {
    const v = localStorage.getItem(DASHBOARD_SCOPE_STORAGE_KEY);
    if (v && ['all', 'brasil', 'internacional', 'multilateral'].includes(v)) return v;
  } catch {
    /* ignore */
  }
  return DASHBOARD_SCOPE_ALL;
}

/**
 * @param {string} scope
 */
export function saveDashboardScopePreference(scope) {
  try {
    localStorage.setItem(DASHBOARD_SCOPE_STORAGE_KEY, scope);
  } catch {
    /* ignore */
  }
}
