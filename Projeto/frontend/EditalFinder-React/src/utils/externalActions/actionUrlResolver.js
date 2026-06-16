import { EXTERNAL_ACTION_TYPES } from './actionTypes.js';
import { normalizeExternalUrl } from './normalizeExternalUrl.js';
import {
  getEditalOfficialUrl,
  getEditalPdfUrl,
  getEditalInscricaoUrl,
  getEditalDetailUrl,
  resolveExternalActionUrl,
} from '../edital/getEditalActionUrls.js';

function extrasOf(item) {
  const ex = item?.extras_raw ?? item?.extras;
  return ex && typeof ex === 'object' && !Array.isArray(ex) ? ex : null;
}

function pickFirstNormalized(item, fieldNames, extrasKeys = []) {
  if (!item || typeof item !== 'object') return null;
  for (const name of fieldNames) {
    const url = normalizeExternalUrl(item[name]);
    if (url) return url;
  }
  const ex = extrasOf(item);
  if (ex) {
    for (const key of extrasKeys) {
      const url = normalizeExternalUrl(ex[key]);
      if (url) return url;
    }
  }
  return null;
}

const FIELD_MAP = {
  [EXTERNAL_ACTION_TYPES.CONCURSO_PRIMARY]: {
    fields: ['link'],
    extras: ['link'],
  },
  [EXTERNAL_ACTION_TYPES.CONCURSO_EDITAL]: {
    fields: ['link_edital', 'link'],
    extras: ['link_edital', 'url_edital'],
  },
  [EXTERNAL_ACTION_TYPES.PORTAL_PRIMARY]: {
    fields: ['link', 'url'],
    extras: ['link'],
  },
  [EXTERNAL_ACTION_TYPES.GENERIC_URL]: {
    fields: ['url', 'link'],
    extras: ['url', 'link'],
  },
};

/**
 * Resolve URL externa por tipo de ação e item (edital, concurso, portal).
 * Editais usam getEditalActionUrls (Grants.gov canonicalizado).
 */
export function resolveActionUrl(item, actionType, options = {}) {
  if (options.rawUrl != null) {
    return resolveExternalActionUrl(item, actionType, options.rawUrl, EXTERNAL_ACTION_TYPES);
  }

  switch (actionType) {
    case EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY:
      return getEditalOfficialUrl(item);
    case EXTERNAL_ACTION_TYPES.EDITAL_PDF:
      return getEditalPdfUrl(item);
    case EXTERNAL_ACTION_TYPES.EDITAL_INSCRICAO:
      return getEditalInscricaoUrl(item).url;
    case EXTERNAL_ACTION_TYPES.EDITAL_DETAIL:
      return getEditalDetailUrl(item);
    default:
      break;
  }

  const map = FIELD_MAP[actionType];
  if (!map) return null;
  return pickFirstNormalized(item, map.fields, map.extras);
}

export { resolveExternalActionUrl };
