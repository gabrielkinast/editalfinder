import { STUDY_PROGRESS_STATUS_LABELS } from './scientificStudyProgressConstants';
import { BOOK_READ_STATUSES } from './scientificBookProgressStorage';
import { KIND_DISPLAY_LABELS } from './scientificStudySessionConstants';

const BOOK_STATUS_LABELS = Object.fromEntries(BOOK_READ_STATUSES.map((s) => [s.id, s.label]));

/**
 * Status de progresso na UI (Fase 2M).
 * @param {string} status
 */
export function displayStudyProgressStatus(status) {
  if (!status || status === 'none') return 'Novo';
  return STUDY_PROGRESS_STATUS_LABELS[status] || formatSnakeLabel(status);
}

/**
 * @param {string} kind
 */
export function displayScientificKind(kind) {
  if (!kind) return '';
  return KIND_DISPLAY_LABELS[kind] || formatSnakeLabel(kind);
}

/**
 * @param {string} bookStatus
 */
export function displayBookReadStatus(bookStatus) {
  if (!bookStatus) return '';
  return BOOK_STATUS_LABELS[bookStatus] || formatSnakeLabel(bookStatus);
}

function formatSnakeLabel(value) {
  return String(value)
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
