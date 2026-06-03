/**
 * Logs DEV do Workspace Científico.
 */
export function logScientificWorkspace(event, payload = {}) {
  if (!import.meta.env.DEV) return;
  console.info('[scientific-workspace]', event, payload);
}
