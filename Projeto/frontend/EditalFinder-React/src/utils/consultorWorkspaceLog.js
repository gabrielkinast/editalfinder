/**
 * Logs DEV do Workspace do Consultor — sem tokens nem dados sensíveis.
 */
export function logConsultorWorkspace(event, payload = {}) {
  if (!import.meta.env.DEV) return;
  console.info('[consultor-workspace]', event, payload);
}
