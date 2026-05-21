/**
 * Logs DEV do briefing rápido do cliente.
 */
export function logClienteBriefing(event, payload = {}) {
  if (!import.meta.env.DEV) return;
  console.info('[cliente-briefing]', event, payload);
}
