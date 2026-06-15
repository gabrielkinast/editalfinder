/**
 * Rascunhos locais de cadastro manual de edital (falha Supabase/RLS/rede).
 */
import { redactSensitiveFeedbackObject } from '../feedback/appFeedbackSensitive.js';

export const PENDING_MANUAL_EDITAIS_KEY = 'editalfinder:pending_manual_editais:v1';

function storageAvailable() {
  return typeof localStorage !== 'undefined';
}

function readQueue() {
  if (!storageAvailable()) return [];
  try {
    const raw = localStorage.getItem(PENDING_MANUAL_EDITAIS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeQueue(list) {
  if (!storageAvailable()) return false;
  try {
    localStorage.setItem(PENDING_MANUAL_EDITAIS_KEY, JSON.stringify(list));
    return true;
  } catch {
    return false;
  }
}

export function createLocalDraftId() {
  return `draft_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * @param {object} payload — dados do formulário (já sanitizados)
 * @param {object} context — metadados seguros
 */
export function savePendingManualEditalDraft(payload, context = {}) {
  const localId = context.localId || createLocalDraftId();
  const entry = {
    localId,
    createdAt: new Date().toISOString(),
    payload: redactSensitiveFeedbackObject(payload && typeof payload === 'object' ? payload : {}),
    context: redactSensitiveFeedbackObject({
      route: '/cadastros',
      operation: 'insert',
      table: 'edital',
      ...context,
      localId,
    }),
  };

  const queue = readQueue();
  const idx = queue.findIndex((q) => q.localId === localId);
  if (idx >= 0) queue[idx] = entry;
  else queue.unshift(entry);

  const trimmed = queue.slice(0, 20);
  writeQueue(trimmed);
  return localId;
}

export function listPendingManualEditalDrafts() {
  return readQueue();
}

export function removePendingManualEditalDraft(localId) {
  const queue = readQueue().filter((q) => q.localId !== localId);
  writeQueue(queue);
  return queue.length;
}

export function clearPendingManualEditalDrafts() {
  if (!storageAvailable()) return;
  try {
    localStorage.removeItem(PENDING_MANUAL_EDITAIS_KEY);
  } catch {
    /* ignore */
  }
}
