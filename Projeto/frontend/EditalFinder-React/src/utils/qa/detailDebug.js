/**
 * Instrumentação dev-only do carregamento de detalhe (FRONTEND 1.1F-DETALHE).
 *
 * Habilitar via:
 *   - env: VITE_DEBUG_ROUTE_DETAIL=1
 *   - runtime: localStorage.setItem('EDITALFINDER_DEBUG_ROUTE_DETAIL', '1')
 */

export const DETAIL_DEBUG_LS_KEY = 'EDITALFINDER_DEBUG_ROUTE_DETAIL';
const LOG_PREFIX = '[EditalFinder][DetailDebug]';

function isTruthyFlag(v) {
  if (v == null) return false;
  const s = String(v).trim().toLowerCase();
  return s === '1' || s === 'true' || s === 'yes' || s === 'on';
}

export function isDetailDebugEnabled({ env, win } = {}) {
  try {
    if (isTruthyFlag(env?.VITE_DEBUG_ROUTE_DETAIL)) return true;
  } catch {
    /* ignore */
  }
  const w = win ?? (typeof window !== 'undefined' ? window : undefined);
  try {
    return isTruthyFlag(w?.localStorage?.getItem(DETAIL_DEBUG_LS_KEY));
  } catch {
    return false;
  }
}

/**
 * Monta registro de debug (puro, sem segredos).
 * @param {object} payload
 */
export function buildDetailDebugRecord(payload = {}) {
  return {
    routeParam: payload.routeParam ?? null,
    normalizedId: payload.normalizedId ?? null,
    lookupBaseFound: Boolean(payload.lookupBaseFound),
    lookupViewFound: Boolean(payload.lookupViewFound),
    finalFound: Boolean(payload.finalFound ?? payload.edital),
    lookupMode: payload.lookupMode ?? null,
    attachmentsOk: payload.attachmentsOk ?? null,
    attachmentsError: payload.attachmentsError ?? null,
    errorKind: payload.errorKind ?? null,
  };
}

/**
 * Loga (dev-only) o resultado do lookup de detalhe.
 * @returns {boolean}
 */
export function logDetailDebug(payload = {}, opts = {}) {
  if (!isDetailDebugEnabled({ env: opts.env, win: opts.win })) return false;
  const logger = opts.logger ?? (typeof console !== 'undefined' ? console : null);
  if (!logger?.log) return false;
  logger.log(LOG_PREFIX, buildDetailDebugRecord(payload));
  return true;
}
