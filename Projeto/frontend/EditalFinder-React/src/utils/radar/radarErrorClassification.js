/**
 * Erros de cancelamento / geração obsoleta não devem virar fallback fatal na UI.
 * @param {unknown} err
 */
export function isNonFatalRadarError(err) {
  if (!err) return false;
  if (err?.name === 'AbortError') return true;
  const msg = String(typeof err === 'string' ? err : err?.message || err).toLowerCase();
  return (
    msg.includes('cancelled') ||
    msg.includes('canceled') ||
    msg.includes('stale_generation') ||
    msg.includes('ignored_generation') ||
    msg.includes('abort') ||
    msg.includes('aborted')
  );
}

/**
 * @param {string} clienteId
 * @param {unknown} err
 */
export function radarErrorKey(clienteId, err) {
  const msg = typeof err === 'string' ? err : err?.message || String(err) || 'unknown';
  return `${clienteId}:${msg}`;
}
