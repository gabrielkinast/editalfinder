/**
 * Resolver central de URLs de ação externa de edital (FRONTEND 1.1G-GRANTS-LINKS).
 *
 * Botão principal → getOfficialEditalUrl (Grants.gov canonicalizado).
 * PDF → pdf_url apenas.
 * Inscrição → link_inscricao se seguro; fallback para official se page-not-found.
 */

import { normalizeExternalUrl } from '../externalActions/normalizeExternalUrl.js';
import {
  getOfficialEditalUrl,
  resolveOfficialEditalUrlInfo,
  isBrokenUrl,
  isGrantsGovUrl,
} from './officialEditalUrl.js';

export const UNSAFE_OFFICIAL_LINK_MSG =
  'Não encontramos um link oficial seguro para este edital.';

export { getOfficialEditalUrl, resolveOfficialEditalUrlInfo };

function extrasOf(item) {
  const ex = item?.extras_raw ?? item?.extras;
  return ex && typeof ex === 'object' && !Array.isArray(ex) ? ex : null;
}

function pickFirstSafeUrl(item, fieldNames, extrasKeys = [], rejected = []) {
  if (!item || typeof item !== 'object') return { url: null, fieldUsed: 'none' };

  for (const name of fieldNames) {
    const raw = item[name];
    const url = normalizeExternalUrl(raw);
    if (raw != null && raw !== '' && !url) rejected.push(String(raw));
    if (!url) continue;
    if (isBrokenUrl(url)) {
      rejected.push(url);
      continue;
    }
    return { url, fieldUsed: name };
  }

  const ex = extrasOf(item);
  if (ex) {
    for (const key of extrasKeys) {
      const raw = ex[key];
      const url = normalizeExternalUrl(raw);
      if (raw != null && raw !== '' && !url) rejected.push(String(raw));
      if (!url) continue;
      if (isBrokenUrl(url)) {
        rejected.push(url);
        continue;
      }
      return { url, fieldUsed: `extras.${key}` };
    }
  }

  return { url: null, fieldUsed: 'none' };
}

/**
 * URL oficial do edital (site / abrir edital).
 * @param {object} item
 */
export function getEditalOfficialUrl(item) {
  return getOfficialEditalUrl(item);
}

/**
 * URL de PDF — nunca substituída por Grants.gov detail.
 * @param {object} item
 */
export function getEditalPdfUrl(item, rejected = []) {
  const picked = pickFirstSafeUrl(
    item,
    ['pdf_url', 'pdfUrl', 'pdf_url_raw', 'pdf'],
    ['pdf_url', 'url_pdf', 'pdf'],
    rejected,
  );
  if (picked.url) return picked.url;
  return pickFirstSafeUrl(item, ['url_pdf', 'anexo_url'], [], rejected).url;
}

/**
 * URL de inscrição — se quebrada (page-not-found), cai para official URL.
 * @param {object} item
 */
export function getEditalInscricaoUrl(item, rejected = []) {
  const picked = pickFirstSafeUrl(
    item,
    ['link_inscricao', 'linkInscricao'],
    ['link_inscricao', 'inscricao_url', 'url_inscricao'],
    rejected,
  );
  if (picked.url) return { url: picked.url, fieldUsed: picked.fieldUsed, fallback: false };

  const official = resolveOfficialEditalUrlInfo(item);
  if (official.url) {
    return {
      url: official.url,
      fieldUsed: `fallback:${official.fieldUsed}`,
      fallback: true,
      canonicalized: official.canonicalized,
    };
  }
  return { url: null, fieldUsed: 'none', fallback: false };
}

/**
 * URL de detalhe externo (url_detalhe) — para Grants.gov usa official se url_detalhe quebrada.
 * @param {object} item
 */
export function getEditalDetailUrl(item, rejected = []) {
  const picked = pickFirstSafeUrl(
    item,
    ['url_detalhe', 'url_detalhe_raw'],
    ['url_detalhe'],
    rejected,
  );
  if (picked.url) return picked.url;

  const fonte = String(item?.fonte ?? item?.fonte_recurso ?? '').toLowerCase();
  const hints = [item?.link, item?.url_detalhe].map((v) => String(v ?? '')).join(' ');
  if (fonte.includes('grants') || isGrantsGovUrl(hints)) {
    return getOfficialEditalUrl(item);
  }
  return null;
}

/**
 * Resolve todas as URLs de ação + metadata para debug.
 * @param {object} edital
 */
export function resolveEditalActionUrls(edital) {
  const rejectedUrls = [];
  const officialInfo = resolveOfficialEditalUrlInfo(edital);

  const pdf = getEditalPdfUrl(edital, rejectedUrls);
  const inscricaoInfo = getEditalInscricaoUrl(edital, rejectedUrls);
  const detail = getEditalDetailUrl(edital, rejectedUrls);

  return {
    site: officialInfo.url,
    siteMeta: officialInfo,
    inscricao: inscricaoInfo.url,
    inscricaoMeta: inscricaoInfo,
    pdf,
    detail,
    rejectedUrls: [...new Set(rejectedUrls)],
  };
}

/**
 * Valida URL antes de abrir; para EDITAL_PRIMARY recanoniza Grants.gov se necessário.
 * @param {object|null} item
 * @param {string} actionType
 * @param {string|null|undefined} urlOverride
 */
export function resolveExternalActionUrl(item, actionType, urlOverride, actionTypes = {}) {
  const {
    EDITAL_PRIMARY = 'edital_primary',
    EDITAL_PDF = 'edital_pdf',
    EDITAL_INSCRICAO = 'edital_inscricao',
    EDITAL_DETAIL = 'edital_detail',
  } = actionTypes;

  if (urlOverride != null && urlOverride !== '') {
    const norm = normalizeExternalUrl(urlOverride);
    if (norm && !isBrokenUrl(norm)) {
      if (actionType === EDITAL_PRIMARY && item) {
        const official = getOfficialEditalUrl(item);
        if (official && (isBrokenUrl(norm) || shouldPreferOfficialOver(norm, official))) {
          return official;
        }
      }
      return norm;
    }
    if (actionType === EDITAL_PRIMARY && item) return getOfficialEditalUrl(item);
    if (actionType === EDITAL_INSCRICAO && item) return getEditalInscricaoUrl(item).url;
    if (actionType === EDITAL_PDF && item) return getEditalPdfUrl(item);
    if (actionType === EDITAL_DETAIL && item) return getEditalDetailUrl(item);
    return null;
  }

  if (!item) return null;

  switch (actionType) {
    case EDITAL_PRIMARY:
      return getOfficialEditalUrl(item);
    case EDITAL_PDF:
      return getEditalPdfUrl(item);
    case EDITAL_INSCRICAO:
      return getEditalInscricaoUrl(item).url;
    case EDITAL_DETAIL:
      return getEditalDetailUrl(item);
    default:
      return null;
  }
}

/** Grants.gov: preferir official se override ainda é simpler/view-opportunity/page-not-found. */
function shouldPreferOfficialOver(candidate, official) {
  if (!candidate || !official) return false;
  if (isBrokenUrl(candidate)) return true;
  const low = String(candidate).toLowerCase();
  if (/page-not-found|view-opportunity|simpler\.grants\.gov\/opportunity/.test(low)) return true;
  if (isGrantsGovUrl(candidate) && !/\/search-results-detail\/\d+/i.test(candidate)) {
    return isGrantsGovUrl(official) && /\/search-results-detail\/\d+/i.test(official);
  }
  return false;
}

/**
 * Notifica falha de link (fallback simples — alerta nativo).
 */
export function notifyUnsafeLinkFailure(message = UNSAFE_OFFICIAL_LINK_MSG) {
  if (typeof window !== 'undefined' && typeof window.alert === 'function') {
    window.alert(message);
  }
}
