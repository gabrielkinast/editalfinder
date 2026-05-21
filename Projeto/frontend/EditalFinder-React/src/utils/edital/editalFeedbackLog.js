/**
 * Logs DEV sanitizados para fluxo de reporte de editais.
 * Prefixo: [edital-feedback]
 */

function devOnly() {
  return import.meta.env.DEV;
}

/**
 * @param {string} event
 * @param {Record<string, unknown>} [payload]
 */
export function logEditalFeedback(event, payload = {}) {
  if (!devOnly()) return;
  const safe = { ...payload };
  delete safe.comentario;
  delete safe.token;
  delete safe.session;
  delete safe.password;
  console.info(`[edital-feedback] ${event}`, safe);
}
