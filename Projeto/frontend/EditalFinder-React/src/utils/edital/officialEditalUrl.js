/**
 * Seleção da URL oficial de um edital, com canonicalização especial para Grants.gov
 * (DESKTOP QA 1.0 — Bug B: alguns Grants.gov abriam .../page-not-found).
 *
 * Funções puras (sem React/DOM) para serem testáveis em Node.
 *
 * Regras Grants.gov:
 * - usar `link` se já for canônico (search-results-detail/<id>);
 * - nunca escolher `https://www.grants.gov/page-not-found`;
 * - normalizar `simpler.grants.gov/opportunity/<id>` e `view-opportunity/<id>`
 *   para `https://www.grants.gov/search-results-detail/<id>`;
 * - construir canônico a partir de `extras.grants_opportunity_id` quando disponível.
 *
 * NÃO altera backend/Supabase — apenas escolhe melhor URL a partir dos campos já recebidos.
 */

import { normalizeExternalUrl } from '../externalActions/normalizeExternalUrl.js';

const GRANTS_CANONICAL_BASE = 'https://www.grants.gov/search-results-detail/';
const GRANTS_SEARCH_BASE = 'https://www.grants.gov/search-grants';

/** Marcadores de URL inválida/quebrada que nunca devem ser escolhidos. */
const BROKEN_URL_MARKERS = ['page-not-found', 'pagenotfound', '/404', 'not-found'];

function extrasOf(item) {
  const ex = item?.extras_raw ?? item?.extras;
  return ex && typeof ex === 'object' && !Array.isArray(ex) ? ex : null;
}

/** @param {string|null|undefined} url */
export function isBrokenUrl(url) {
  if (!url) return false;
  const low = String(url).toLowerCase();
  return BROKEN_URL_MARKERS.some((m) => low.includes(m));
}

/** @param {string|null|undefined} url */
export function isGrantsGovUrl(url) {
  if (!url) return false;
  return /(^|\.)grants\.gov/i.test(String(url));
}

/**
 * Extrai o opportunity id numérico de uma URL Grants.gov conhecida.
 * Suporta: search-results-detail/<id>, opportunity/<id>, view-opportunity/<id>,
 * e querystring ?oppId=<id>.
 * @param {string|null|undefined} url
 * @returns {string|null}
 */
export function extractGrantsOpportunityId(url) {
  if (!isGrantsGovUrl(url)) return null;
  const s = String(url);
  const path = s.match(
    /\/(?:search-results-detail|opportunity|view-opportunity(?:\.html)?|opportunities)\/(\d{3,})/i,
  );
  if (path) return path[1];
  const htmlQuery = s.match(/view-opportunity\.html[^?]*\?(?:[^#]*&)?(?:oppId|id)=(\d{3,})/i);
  if (htmlQuery) return htmlQuery[1];
  const query = s.match(/[?&](?:oppId|id)=(\d{3,})/i);
  if (query) return query[1];
  return null;
}

/** Constrói a URL canônica de detalhe Grants.gov a partir de um id. */
export function buildGrantsCanonicalUrl(opportunityId) {
  const id = String(opportunityId ?? '').trim();
  if (!/^\d{3,}$/.test(id)) return null;
  return `${GRANTS_CANONICAL_BASE}${id}`;
}

function pickGrantsOpportunityIdFromExtras(item) {
  const ex = extrasOf(item);
  if (!ex) return null;
  const candidates = [
    ex.grants_opportunity_id,
    ex.grantsOpportunityId,
    ex.opportunity_id,
    ex.oppId,
    ex.opp_id,
    ex.funding_opportunity_number,
    ex.fundingOpportunityNumber,
  ];
  for (const c of candidates) {
    const id = String(c ?? '').trim();
    if (/^\d{3,}$/.test(id)) return id;
  }
  return null;
}

/**
 * Resolve a melhor URL oficial de um edital Grants.gov.
 * @param {object} item
 * @returns {{ url: string|null, fieldUsed: string, canonicalized: boolean }}
 */
function resolveGrantsUrl(item) {
  const rejectedUrls = [];
  const fieldOrder = ['link', 'linkOriginal', 'link_raw', 'url', 'url_detalhe', 'url_detalhe_raw'];

  for (const field of fieldOrder) {
    const rawVal = item?.[field];
    const raw = normalizeExternalUrl(rawVal);
    if (raw && isBrokenUrl(raw)) rejectedUrls.push(raw);
    else if (rawVal != null && rawVal !== '' && !raw) rejectedUrls.push(String(rawVal));
  }

  // id estruturado em extras → canônico garantido.
  const extrasId = pickGrantsOpportunityIdFromExtras(item);
  if (extrasId) {
    return {
      url: buildGrantsCanonicalUrl(extrasId),
      fieldUsed: 'extras.grants_opportunity_id',
      canonicalized: true,
      rejectedUrls,
    };
  }

  // varre campos de link em ordem de preferência.
  let firstValidNonGrants = null;

  for (const field of fieldOrder) {
    const rawVal = item?.[field];
    const raw = normalizeExternalUrl(rawVal);
    if (rawVal != null && rawVal !== '' && !raw) rejectedUrls.push(String(rawVal));
    if (!raw) continue;
    if (isBrokenUrl(raw)) {
      if (!rejectedUrls.includes(raw)) rejectedUrls.push(raw);
      continue;
    }

    if (isGrantsGovUrl(raw)) {
      if (/\/search-results-detail\/\d{3,}/i.test(raw)) {
        return { url: raw, fieldUsed: field, canonicalized: false, rejectedUrls };
      }
      const id = extractGrantsOpportunityId(raw);
      if (id) {
        return {
          url: buildGrantsCanonicalUrl(id),
          fieldUsed: field,
          canonicalized: true,
          rejectedUrls,
        };
      }
      return { url: raw, fieldUsed: field, canonicalized: false, rejectedUrls };
    }

    if (!firstValidNonGrants) {
      firstValidNonGrants = { url: raw, fieldUsed: field, canonicalized: false, rejectedUrls };
    }
  }

  if (firstValidNonGrants) return firstValidNonGrants;

  return {
    url: GRANTS_SEARCH_BASE,
    fieldUsed: 'fallback_search',
    canonicalized: true,
    rejectedUrls,
  };
}

/**
 * Resolve a melhor URL oficial de qualquer edital.
 * Para Grants.gov aplica canonicalização; para os demais, primeira URL válida.
 * @param {object} item
 * @returns {{ url: string|null, fieldUsed: string, canonicalized: boolean, source: 'grants'|'generic' }}
 */
export function resolveOfficialEditalUrlInfo(item) {
  if (!item || typeof item !== 'object') {
    return {
      url: null,
      fieldUsed: 'none',
      canonicalized: false,
      source: 'generic',
      rejectedUrls: [],
    };
  }

  const fonte = String(item.fonte ?? item.fonte_recurso ?? item.source ?? '').toLowerCase();
  const linkHints = [item.link, item.link_raw, item.url, item.url_detalhe]
    .map((v) => String(v ?? '').toLowerCase())
    .join(' ');
  const looksGrants = fonte.includes('grants') || isGrantsGovUrl(linkHints);

  if (looksGrants) {
    return { ...resolveGrantsUrl(item), source: 'grants' };
  }

  const rejectedUrls = [];
  const fieldOrder = ['link', 'linkOriginal', 'link_raw', 'url', 'url_detalhe', 'url_detalhe_raw'];
  for (const field of fieldOrder) {
    const rawVal = item?.[field];
    const raw = normalizeExternalUrl(rawVal);
    if (rawVal != null && rawVal !== '' && !raw) rejectedUrls.push(String(rawVal));
    if (raw && !isBrokenUrl(raw)) {
      return { url: raw, fieldUsed: field, canonicalized: false, source: 'generic', rejectedUrls };
    }
    if (raw && isBrokenUrl(raw)) rejectedUrls.push(raw);
  }
  return { url: null, fieldUsed: 'none', canonicalized: false, source: 'generic', rejectedUrls };
}

/**
 * Atalho: retorna apenas a URL oficial (ou null).
 * @param {object} item
 * @returns {string|null}
 */
export function getOfficialEditalUrl(item) {
  return resolveOfficialEditalUrlInfo(item).url;
}
