import { buildStudyProgressKey } from './scientificStudyProgressKeys';
import { logScientificWorkspace } from './scientificWorkspaceLog';

export const SCIENTIFIC_BOOK_PROGRESS_STORAGE_KEY = 'scientific_workspace_book_progress';

export const BOOK_READ_STATUSES = [
  { id: 'quero_ler', label: 'Quero ler' },
  { id: 'lendo', label: 'Lendo' },
  { id: 'lido', label: 'Lido' },
  { id: 'pausado', label: 'Pausado' },
];

/**
 * @param {object} book
 * @param {string} canonicalKey
 */
export function buildBookProgressKey(book, canonicalKey) {
  const label = book.author ? `${book.author} — ${book.title}` : book.title;
  return buildStudyProgressKey(canonicalKey, 'book', book.level || 'book', label);
}

export function loadScientificBookProgress() {
  try {
    const raw = localStorage.getItem(SCIENTIFIC_BOOK_PROGRESS_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
  } catch {
    return {};
  }
}

export function saveScientificBookProgress(map) {
  try {
    localStorage.setItem(SCIENTIFIC_BOOK_PROGRESS_STORAGE_KEY, JSON.stringify(map || {}));
  } catch {
    /* ignore */
  }
}

/**
 * @param {string} bookKey
 * @param {object} patch
 */
export function updateBookProgressEntry(bookKey, patch) {
  const current = loadScientificBookProgress();
  const prev = current[bookKey] || {};
  const next = {
    ...current,
    [bookKey]: {
      ...prev,
      ...patch,
      updatedAt: new Date().toISOString(),
    },
  };
  if (patch.status === 'lendo' && !prev.startedAt) {
    next[bookKey].startedAt = new Date().toISOString();
  }
  if (patch.status === 'lido') {
    next[bookKey].finishedAt = new Date().toISOString();
  }
  saveScientificBookProgress(next);
  logScientificWorkspace('book_progress_updated', { bookKey, status: patch.status });
  return next;
}
