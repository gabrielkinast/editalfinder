import { APP_FEEDBACK_CATEGORY_LABELS } from '../../constants/appFeedbackConfig.js';
import { getFeedbackProblemType } from './appFeedbackTaxonomy.js';

/**
 * Normaliza rota para exibição em assunto/corpo do e-mail.
 */
export function normalizeRouteForEmail(route) {
  const raw = String(route ?? '').trim();
  if (!raw) return 'sem rota';
  const pathOnly = raw.split('?')[0].split('#')[0].trim();
  if (!pathOnly) return 'sem rota';
  if (pathOnly.startsWith('/')) return pathOnly.slice(0, 120);
  return `/${pathOnly}`.slice(0, 120);
}

/**
 * Label humano para grupo/categoria técnica.
 */
export function getCategoryLabel(groupOrCategoria) {
  const key = String(groupOrCategoria ?? '').trim().toLowerCase();
  if (!key) return APP_FEEDBACK_CATEGORY_LABELS.other;
  return APP_FEEDBACK_CATEGORY_LABELS[key] || APP_FEEDBACK_CATEGORY_LABELS.other;
}

/**
 * Label humano do tipo — prefere tipo_label do payload.
 */
export function getProblemTypeLabel(payload = {}) {
  if (payload?.tipo_label) return String(payload.tipo_label);
  return getFeedbackProblemType(payload?.tipo).label;
}

/**
 * Data legível para triagem (pt-BR).
 */
export function formatFeedbackDateForEmail(iso) {
  if (!iso) return '—';
  try {
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return String(iso);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(iso);
  }
}
