import { logConsultorWorkspace } from '../consultorWorkspaceLog';

const STORAGE_PREFIX = 'consultor_client_timeline_';
const MAX_EVENTS = 120;

/** @typedef {'briefing_saved'|'client_profile_updated'|'triage_report_generated'|'preproject_updated'|'csv_exported'|'tracked_opportunity'} TimelineEventType */

export const TIMELINE_EVENT_TYPES = {
  BRIEFING_SAVED: 'briefing_saved',
  CLIENT_PROFILE_UPDATED: 'client_profile_updated',
  TRIAGE_REPORT_GENERATED: 'triage_report_generated',
  PREPROJECT_UPDATED: 'preproject_updated',
  CSV_EXPORTED: 'csv_exported',
  TRACKED_OPPORTUNITY: 'tracked_opportunity',
};

export const TIMELINE_TYPE_LABEL = {
  briefing_saved: 'Briefing',
  client_profile_updated: 'Perfil',
  triage_report_generated: 'Triagem',
  preproject_updated: 'Pré-projeto',
  csv_exported: 'Exportação',
  tracked_opportunity: 'Acompanhamento',
};

function storageKey(clienteId) {
  return `${STORAGE_PREFIX}${clienteId}`;
}

/**
 * @param {string|number} clienteId
 * @returns {Array<{ id: string, type: string, title: string, description?: string, createdAt: string, metadata?: object }>}
 */
export function loadClientTimeline(clienteId) {
  if (clienteId == null) return [];
  try {
    const raw = localStorage.getItem(storageKey(clienteId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    const events = parsed?.events ?? parsed;
    if (!Array.isArray(events)) return [];
    return events
      .filter((e) => e && e.id && e.title && e.createdAt)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  } catch {
    return [];
  }
}

/**
 * @param {string|number} clienteId
 * @param {Array<object>} events
 */
function saveClientTimeline(clienteId, events) {
  if (clienteId == null) return;
  try {
    localStorage.setItem(
      storageKey(clienteId),
      JSON.stringify({ events: events.slice(0, MAX_EVENTS), updatedAt: new Date().toISOString() }),
    );
  } catch {
    /* quota */
  }
}

/**
 * @param {string|number} clienteId
 * @param {{ type: string, title: string, description?: string, metadata?: object }} partial
 * @returns {object|null}
 */
export function appendClientTimelineEvent(clienteId, partial) {
  if (clienteId == null || !partial?.type || !partial?.title) return null;
  const event = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    type: partial.type,
    title: partial.title,
    description: partial.description ? String(partial.description) : '',
    createdAt: new Date().toISOString(),
    metadata: partial.metadata && typeof partial.metadata === 'object' ? partial.metadata : {},
  };
  const prev = loadClientTimeline(clienteId);
  saveClientTimeline(clienteId, [event, ...prev]);
  logConsultorWorkspace('timeline_event_added', {
    id_cliente: clienteId,
    type: event.type,
    event_id: event.id,
  });
  return event;
}

/**
 * @param {string|number} clienteId
 */
export function clearClientTimeline(clienteId) {
  if (clienteId == null) return;
  try {
    localStorage.removeItem(storageKey(clienteId));
  } catch {
    /* ignore */
  }
  logConsultorWorkspace('timeline_clear', { id_cliente: clienteId });
}

export function formatTimelineDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    });
  } catch {
    return String(iso);
  }
}
