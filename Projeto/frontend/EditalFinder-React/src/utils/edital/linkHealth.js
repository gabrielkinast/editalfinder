/**
 * Leitura defensiva de extras.link_health (auditoria / loader).
 * Sem link_health → comportamento legado (botões habilitados).
 */

import { resolveEditalActionUrls } from './getEditalActionUrls.js';

const BROKEN = new Set([
  'broken_404',
  'broken_spa_not_found',
  'timeout',
  'invalid_url',
]);

function normalizeExtras(extras) {
  if (!extras || typeof extras !== 'object' || Array.isArray(extras)) return null;
  return extras;
}

function fieldHealth(extras, campo) {
  const ex = normalizeExtras(extras);
  const lh = ex?.link_health;
  if (!lh || typeof lh !== 'object') return null;
  const fields = lh.fields;
  if (Array.isArray(fields)) {
    const hit = fields.find((f) => f && f.campo === campo);
    if (hit) return hit;
  }
  if (campo === 'link' && lh.link_status) {
    return { campo: 'link', link_status: lh.link_status, recommendation: lh.recommendation };
  }
  return null;
}

export function isLinkStatusBroken(status) {
  return BROKEN.has(String(status || '').toLowerCase());
}

export function getEditalLinkHealth(edital) {
  const ex = normalizeExtras(edital?.extras_raw ?? edital?.extras);
  const lh = ex?.link_health;
  if (!lh || typeof lh !== 'object') {
    return {
      hasAudit: false,
      aggregateStatus: null,
      showUnavailableBadge: false,
    };
  }
  const aggregateStatus = String(lh.link_status || '').toLowerCase() || null;
  return {
    hasAudit: true,
    aggregateStatus,
    showUnavailableBadge: isLinkStatusBroken(aggregateStatus),
    allEssentialBroken: lh.all_essential_broken === true,
    fields: Array.isArray(lh.fields) ? lh.fields : [],
  };
}

export function isUrlDisabledForCampo(edital, campo, url) {
  const ex = normalizeExtras(edital?.extras_raw ?? edital?.extras);
  const lh = ex?.link_health;
  if (!lh) return false;

  const fields = lh.fields;
  if (Array.isArray(fields) && url) {
    const norm = String(url).trim();
    const hit = fields.find(
      (f) =>
        f &&
        f.campo === campo &&
        String(f.link || f.url || '').trim() === norm,
    );
    if (hit) return isLinkStatusBroken(hit.link_status);
  }

  const fh = fieldHealth(ex, campo);
  if (fh) return isLinkStatusBroken(fh.link_status);

  if (campo === 'link' || campo === 'link_inscricao') {
    return isLinkStatusBroken(lh.link_status);
  }
  return false;
}

export function resolveActionLinks(edital) {
  const resolved = resolveEditalActionUrls(edital);
  const site = resolved.site;
  const inscricao = resolved.inscricao;
  const pdf = resolved.pdf;

  const siteDisabled = site ? isUrlDisabledForCampo(edital, 'link', site) : false;
  const inscDisabled = inscricao
    ? isUrlDisabledForCampo(edital, 'link_inscricao', inscricao)
    : false;
  const pdfDisabled = pdf ? isUrlDisabledForCampo(edital, 'pdf_url', pdf) : false;

  const health = getEditalLinkHealth(edital);

  return {
    site: site && !siteDisabled ? site : null,
    inscricao: inscricao && !inscDisabled ? inscricao : null,
    pdf: pdf && !pdfDisabled ? pdf : null,
    siteDisabled,
    inscDisabled,
    pdfDisabled,
    health,
    siteMeta: resolved.siteMeta,
    inscricaoMeta: resolved.inscricaoMeta,
    rejectedUrls: resolved.rejectedUrls,
  };
}
