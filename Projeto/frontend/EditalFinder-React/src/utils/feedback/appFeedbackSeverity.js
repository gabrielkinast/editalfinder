import {
  APP_FEEDBACK_SEVERITY_LEVELS,
  DEFAULT_APP_FEEDBACK_SEVERITY_VALUE,
} from '../../constants/appFeedbackConfig.js';

const BY_VALUE = new Map(APP_FEEDBACK_SEVERITY_LEVELS.map((item) => [item.value, item]));

/**
 * Mapeia valores legados de severidade para o modelo 1.1C.5.
 */
export function normalizeLegacySeverity(value) {
  if (value == null || value === '') return DEFAULT_APP_FEEDBACK_SEVERITY_VALUE;
  const normalized = String(value).trim().toLowerCase();
  if (normalized === 'normal') return 'medium';
  if (normalized === 'urgent' || normalized === 'critica') return 'high';
  if (normalized === 'critical') return 'critical';
  return normalized;
}

/**
 * Resolve severidade — nunca retorna null.
 */
export function getFeedbackSeverity(value) {
  const resolved = normalizeLegacySeverity(value);
  const found = BY_VALUE.get(resolved);
  if (found) return { ...found };

  const fallback =
    BY_VALUE.get(DEFAULT_APP_FEEDBACK_SEVERITY_VALUE) || APP_FEEDBACK_SEVERITY_LEVELS[0];
  return fallback ? { ...fallback } : { ...APP_FEEDBACK_SEVERITY_LEVELS[0] };
}
