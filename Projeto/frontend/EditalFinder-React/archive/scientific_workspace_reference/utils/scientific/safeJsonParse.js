import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Parse JSON sem derrubar a UI.
 * @param {string|null} raw
 * @param {*} fallback
 * @param {{ context?: string }} [options]
 */
export function safeJsonParse(raw, fallback, options = {}) {
  if (raw == null || raw === '') return fallback;
  try {
    return JSON.parse(raw);
  } catch (err) {
    if (import.meta.env.DEV && options.context) {
      logScientificWorkspace('notebook_load_invalid_shape', {
        context: options.context,
        message: err?.message,
      });
    }
    return fallback;
  }
}
