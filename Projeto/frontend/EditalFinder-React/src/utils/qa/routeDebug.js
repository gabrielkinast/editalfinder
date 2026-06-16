/**
 * Instrumentação dev-only de rota/navegação (DESKTOP QA 1.0).
 *
 * Habilitar via:
 *   - env: VITE_DEBUG_ROUTES=1
 *   - runtime: localStorage.setItem('EDITALFINDER_DEBUG_ROUTES', '1')
 */

import { FATAL_ERROR_TEXTS } from './smokeFlows.js';

export const ROUTES_LS_KEY = 'EDITALFINDER_DEBUG_ROUTES';
const LOG_PREFIX = '[EditalFinder][RouteDebug]';

function isTruthyFlag(v) {
  if (v == null) return false;
  const s = String(v).trim().toLowerCase();
  return s === '1' || s === 'true' || s === 'yes' || s === 'on';
}

export function isRouteDebugEnabled({ env, win } = {}) {
  try {
    if (isTruthyFlag(env?.VITE_DEBUG_ROUTES)) return true;
  } catch {
    /* ignore */
  }
  const w = win ?? (typeof window !== 'undefined' ? window : undefined);
  try {
    return isTruthyFlag(w?.localStorage?.getItem(ROUTES_LS_KEY));
  } catch {
    return false;
  }
}

/**
 * Detecta texto de erro fatal num conteúdo de página (para o harness E2E).
 * @param {string} pageText
 * @returns {{ hasFatalError: boolean, matched: string|null }}
 */
export function detectFatalError(pageText) {
  const text = String(pageText ?? '');
  for (const marker of FATAL_ERROR_TEXTS) {
    if (text.includes(marker)) return { hasFatalError: true, matched: marker };
  }
  return { hasFatalError: false, matched: null };
}

/**
 * Monta registro de rota (puro).
 * @param {{ route?: string, win?: Window }} [opts]
 */
export function buildRouteDebugRecord({ route, win } = {}) {
  const w = win ?? (typeof window !== 'undefined' ? window : undefined);
  const loc = w?.location;
  return {
    route: route ?? (loc ? `${loc.pathname}${loc.hash || ''}` : '(sem location)'),
    href: loc?.href ?? null,
    ts: new Date().toISOString(),
  };
}

/**
 * Loga (dev-only) a rota atual.
 * @returns {boolean}
 */
export function logRouteDebug(opts = {}) {
  if (!isRouteDebugEnabled({ env: opts.env, win: opts.win })) return false;
  const logger = opts.logger ?? (typeof console !== 'undefined' ? console : null);
  if (!logger?.log) return false;
  logger.log(LOG_PREFIX, buildRouteDebugRecord(opts));
  return true;
}
