/**
 * Instrumentação dev-only de links externos (DESKTOP QA 1.0 — Bug B).
 *
 * Permite registrar, em DEV/QA, qual URL um botão de edital vai abrir, sem
 * expor segredos e sem efeitos em produção (gated por flag).
 *
 * Habilitar via:
 *   - env: VITE_DEBUG_EXTERNAL_LINKS=1
 *   - runtime: localStorage.setItem('EDITALFINDER_DEBUG_EXTERNAL_LINKS', '1')
 *
 * Funções de montagem do registro são puras e testáveis em Node.
 */

import { resolveOfficialEditalUrlInfo } from '../edital/officialEditalUrl.js';

export const EXTERNAL_LINKS_LS_KEY = 'EDITALFINDER_DEBUG_EXTERNAL_LINKS';
const LOG_PREFIX = '[EditalFinder][ExternalLinkDebug]';

function isTruthyFlag(v) {
  if (v == null) return false;
  const s = String(v).trim().toLowerCase();
  return s === '1' || s === 'true' || s === 'yes' || s === 'on';
}

function envFlag(env) {
  try {
    return isTruthyFlag(env?.VITE_DEBUG_EXTERNAL_LINKS);
  } catch {
    return false;
  }
}

/**
 * @param {{ env?: Record<string, unknown>, win?: Window }} [deps]
 */
export function isExternalLinkDebugEnabled({ env, win } = {}) {
  if (envFlag(env)) return true;
  const w = win ?? (typeof window !== 'undefined' ? window : undefined);
  try {
    return isTruthyFlag(w?.localStorage?.getItem(EXTERNAL_LINKS_LS_KEY));
  } catch {
    return false;
  }
}

/** Marca uma URL como suspeita para facilitar triagem no log. */
export function classifyExternalUrl(url) {
  const low = String(url ?? '').toLowerCase();
  return {
    pageNotFound: /page-not-found|pagenotfound|\/404|not-found/.test(low),
    simplerOpportunity: /simpler\.grants\.gov\/opportunity\//.test(low),
    viewOpportunity: /view-opportunity\//.test(low),
    searchResultsDetail: /search-results-detail\/\d+/.test(low),
    grantsGov: /(^|\.)grants\.gov/.test(low),
  };
}

/**
 * Monta o registro de debug (puro, sem segredos).
 * @param {object} item — edital/concurso
 * @param {{ chosenUrl?: string, fieldUsed?: string, runtime?: string }} [opts]
 */
export function buildExternalLinkDebugRecord(item, opts = {}) {
  const info = resolveOfficialEditalUrlInfo(item);
  const chosenUrl = opts.chosenUrl ?? info.url ?? null;
  const fieldUsed = opts.fieldUsed ?? info.fieldUsed ?? 'unknown';
  const idEdital =
    item?.id_edital ?? item?.idNumerico ?? String(item?.id ?? '').replace(/^manual-/i, '') ?? null;

  let runtime = opts.runtime ?? null;
  if (!runtime && typeof window !== 'undefined') {
    runtime = window.__TAURI_INTERNALS__ || window.__TAURI__ ? 'desktop_tauri' : 'web';
  }

  return {
    title: String(item?.titulo ?? item?.title ?? item?.nome ?? '').slice(0, 120) || '(sem título)',
    id_edital: idEdital,
    fonte: String(item?.fonte ?? item?.fonte_recurso ?? item?.source ?? item?.orgao ?? '') || '(sem fonte)',
    chosenUrl,
    fieldUsed,
    wasCanonicalized: Boolean(info.canonicalized),
    canonicalized: Boolean(info.canonicalized),
    rejectedUrls: info.rejectedUrls ?? [],
    source: info.source,
    flags: classifyExternalUrl(chosenUrl),
    runtime,
  };
}

/**
 * Loga (dev-only) o registro de link externo.
 * @param {object} item
 * @param {{ chosenUrl?: string, fieldUsed?: string, env?: object, win?: Window, logger?: Console }} [opts]
 * @returns {boolean} true se efetivamente logou
 */
export function logExternalLinkDebug(item, opts = {}) {
  if (!isExternalLinkDebugEnabled({ env: opts.env, win: opts.win })) return false;
  const record = buildExternalLinkDebugRecord(item, opts);
  const logger = opts.logger ?? (typeof console !== 'undefined' ? console : null);
  if (!logger?.log) return false;
  if (record.flags.pageNotFound) {
    (logger.warn ?? logger.log)(`${LOG_PREFIX} ⚠ page-not-found`, record);
  } else {
    logger.log(LOG_PREFIX, record);
  }
  return true;
}
