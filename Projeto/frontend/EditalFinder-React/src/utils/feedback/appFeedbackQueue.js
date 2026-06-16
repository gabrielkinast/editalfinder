import {
  APP_FEEDBACK_PENDING_KEY,
  APP_FEEDBACK_QUEUE_KEY,
  APP_FEEDBACK_QUEUE_MAX,
} from '../../constants/appFeedbackConfig.js';
import { normalizeFeedbackPayload } from './appFeedbackPayload.js';

function defaultStorage() {
  return typeof localStorage !== 'undefined' ? localStorage : null;
}

function parseQueue(raw) {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed;
  } catch {
    return [];
  }
}

/**
 * Preenche campos novos (1.1C.3) em itens antigos da fila sem sobrescrever dados existentes.
 */
export function normalizeQueuedFeedback(entry) {
  if (!entry || typeof entry !== 'object') return entry;
  const payload = entry.payload && typeof entry.payload === 'object' ? entry.payload : {};

  return {
    ...entry,
    payload: {
      ...normalizeFeedbackPayload(payload),
      runtime: payload.runtime ?? null,
      platform_context: payload.platform_context ?? null,
    },
  };
}

function normalizeLegacyItem(item) {
  if (!item || typeof item !== 'object') return null;
  if (item.payload && item.id_local) return item;
  const { _pendingAt, _pendingReason, ...payload } = item;
  return {
    id_local: payload.id_local || payload.id || `legacy_${_pendingAt || Date.now()}`,
    payload: { ...payload, status: payload.status || 'pending_local' },
    saved_at: _pendingAt || new Date().toISOString(),
    last_attempt_at: null,
    attempts: 0,
    last_error_reason: _pendingReason || null,
  };
}

/**
 * Lê fila v1; migra entradas legadas de app_feedback_pending se necessário.
 */
export function readAppFeedbackQueue(storage = defaultStorage()) {
  if (!storage) return [];

  const current = parseQueue(storage.getItem(APP_FEEDBACK_QUEUE_KEY))
    .map(normalizeLegacyItem)
    .filter(Boolean)
    .map(normalizeQueuedFeedback);

  if (current.length > 0) return current.slice(0, APP_FEEDBACK_QUEUE_MAX);

  const legacy = parseQueue(storage.getItem(APP_FEEDBACK_PENDING_KEY))
    .map(normalizeLegacyItem)
    .filter(Boolean)
    .map(normalizeQueuedFeedback);

  if (legacy.length > 0) {
    writeAppFeedbackQueue(legacy, storage);
    try {
      storage.removeItem(APP_FEEDBACK_PENDING_KEY);
    } catch {
      /* ignore */
    }
  }

  return legacy.slice(0, APP_FEEDBACK_QUEUE_MAX);
}

export function writeAppFeedbackQueue(queue, storage = defaultStorage()) {
  if (!storage) throw new Error('localStorage_unavailable');
  const capped = (Array.isArray(queue) ? queue : []).slice(0, APP_FEEDBACK_QUEUE_MAX);
  storage.setItem(APP_FEEDBACK_QUEUE_KEY, JSON.stringify(capped));
  return capped;
}

/**
 * @returns {{ entry: object, queueSize: number }}
 */
export function saveAppFeedbackLocal(payload, reason, storage = defaultStorage()) {
  if (!storage) throw new Error('localStorage_unavailable');
  if (!payload?.id_local) throw new Error('missing_id_local');

  const queue = readAppFeedbackQueue(storage).filter((e) => e.id_local !== payload.id_local);

  const entry = {
    id_local: payload.id_local,
    payload: {
      ...payload,
      status: 'pending_local',
    },
    saved_at: new Date().toISOString(),
    last_attempt_at: null,
    attempts: 0,
    last_error_reason: reason || null,
  };

  queue.unshift(entry);
  const capped = writeAppFeedbackQueue(queue, storage);
  return { entry, queueSize: capped.length };
}

export function clearAppFeedbackQueue(storage = defaultStorage()) {
  if (!storage) return;
  storage.removeItem(APP_FEEDBACK_QUEUE_KEY);
}
