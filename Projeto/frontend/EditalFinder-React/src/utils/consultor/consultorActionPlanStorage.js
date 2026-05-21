const STORAGE_PREFIX = 'consultor_action_plan_done_';

/**
 * @param {string|number} clienteId
 * @returns {Array<{ id: string, reopenKey: string }>}
 */
export function loadActionPlanDone(clienteId) {
  if (clienteId == null) return [];
  try {
    const raw = localStorage.getItem(`${STORAGE_PREFIX}${clienteId}`);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((e) => e && typeof e.id === 'string' && typeof e.reopenKey === 'string')
      .map((e) => ({ id: e.id, reopenKey: e.reopenKey }));
  } catch {
    return [];
  }
}

/**
 * @param {string|number} clienteId
 * @param {Array<{ id: string, reopenKey: string }>} entries
 */
export function saveActionPlanDone(clienteId, entries) {
  if (clienteId == null) return;
  try {
    localStorage.setItem(`${STORAGE_PREFIX}${clienteId}`, JSON.stringify(entries));
  } catch {
    /* quota / private mode */
  }
}

/**
 * Aplica conclusões manuais; reabre se reopenKey mudou (estado crítico de novo).
 * @param {Array<object>} actions
 * @param {Array<{ id: string, reopenKey: string }>} doneEntries
 */
export function applyActionPlanDoneState(actions, doneEntries) {
  const doneMap = new Map(doneEntries.map((e) => [e.id, e.reopenKey]));
  return actions.map((action) => {
    const storedKey = doneMap.get(action.id);
    if (storedKey != null && storedKey === action.reopenKey) {
      return { ...action, status: 'concluida' };
    }
    if (storedKey != null && storedKey !== action.reopenKey) {
      return { ...action, status: 'pendente', wasReopened: true };
    }
    return action;
  });
}

/**
 * @param {Array<{ id: string, reopenKey: string }>} entries
 * @param {string} id
 * @param {string} reopenKey
 * @param {boolean} done
 */
export function toggleActionPlanDoneEntry(entries, id, reopenKey, done) {
  const without = entries.filter((e) => e.id !== id);
  if (!done) return without;
  return [...without, { id, reopenKey }];
}
