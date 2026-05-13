import { coerceStringArray } from './coerceArrays';

/** Alias semântico para campos array/string do banco. */
export function asArray(value) {
  return coerceStringArray(value);
}

export function getFonte(edital) {
  if (!edital) return 'Fonte não informada';
  const s = (
    edital.fonte_recurso_display ||
    edital.fonte_recurso ||
    edital.fonte_raw ||
    edital.orgao ||
    edital.origem_portal_raw ||
    ''
  ).trim();
  return s || 'Fonte não informada';
}

export function editalTemPdf(edital) {
  if (!edital) return false;
  if (edital.pdf_url_raw || edital.pdfUrl) return true;
  const ex = edital.extras_raw;
  if (ex && typeof ex === 'object' && (ex.pdf_url || ex.pdfUrl)) return true;
  if (Array.isArray(edital.documentos) && edital.documentos.length > 0) return true;
  return false;
}

export function isSuspeitoValidacao(edital) {
  const vs = String(edital?.validacao_status_raw ?? edital?.validacao_status ?? '')
    .toLowerCase()
    .trim();
  return vs === 'suspeito';
}

export function isAltaQualidade(edital) {
  const q = Number(edital?.qualidade_dado_raw ?? edital?.qualidade_dado);
  return Number.isFinite(q) && q >= 70;
}
