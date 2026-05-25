import { parseDateLoose, startOfTodayLocal } from '../edital/dates';

/**
 * @typedef {'vencendo_7'|'vencendo_30'|'prazo_confortavel'|'encerrado'|'sem_prazo'|'prazo_invalido'} DashboardDeadlineStatus
 */

const ENCERRADO_STATUS = new Set([
  'encerrado',
  'encerrada',
  'closed',
  'fechado',
  'fechada',
  'finalizado',
  'finalizada',
  'inativo',
  'inactive',
  'cancelado',
  'cancelada',
]);

/**
 * @param {unknown} extras
 * @param {string[]} keys
 */
function pickExtras(extras, keys) {
  if (!extras || typeof extras !== 'object' || Array.isArray(extras)) return null;
  for (const k of keys) {
    const v = extras[k];
    if (v != null && v !== '') return v;
  }
  const meta = extras.metadata;
  if (meta && typeof meta === 'object') {
    for (const k of keys) {
      const v = meta[k];
      if (v != null && v !== '') return v;
    }
  }
  return null;
}

/**
 * @param {Record<string, unknown>} edital
 * @returns {Array<{ field: string, raw: string, confidence: number }>}
 */
export function collectDeadlineCandidates(edital) {
  if (!edital || typeof edital !== 'object') return [];
  const ex = edital.extras_raw ?? edital.extras;
  /** @type {Array<{ field: string, raw: unknown, confidence: number }>} */
  const rows = [
    { field: 'prazo_envio_raw', raw: edital.prazo_envio_raw, confidence: 1 },
    { field: 'fim_inscricao_raw', raw: edital.fim_inscricao_raw, confidence: 0.98 },
    { field: 'dataLimite', raw: edital.dataLimite, confidence: 0.98 },
    { field: 'data_encerramento_raw', raw: edital.data_encerramento_raw, confidence: 0.95 },
    { field: 'prazo_envio', raw: edital.prazo_envio, confidence: 0.95 },
    { field: 'prazo', raw: edital.prazo, confidence: 0.9 },
    { field: 'data_limite', raw: edital.data_limite, confidence: 0.9 },
    { field: 'dataLimite_legacy', raw: edital.dataLimite, confidence: 0.88 },
    { field: 'data_encerramento', raw: edital.data_encerramento, confidence: 0.88 },
    { field: 'data_fim', raw: edital.data_fim, confidence: 0.85 },
    { field: 'deadline', raw: edital.deadline, confidence: 0.85 },
    { field: 'closing_date', raw: edital.closing_date, confidence: 0.85 },
    { field: 'prazo_final', raw: edital.prazo_final, confidence: 0.85 },
    { field: 'encerramento', raw: edital.encerramento, confidence: 0.82 },
    { field: 'fim_inscricao', raw: edital.fim_inscricao, confidence: 0.82 },
    { field: 'data_submissao', raw: edital.data_submissao, confidence: 0.75 },
    { field: 'extras.prazo', raw: pickExtras(ex, ['prazo', 'deadline', 'data_limite', 'closing_date']), confidence: 0.8 },
    { field: 'extras.data_limite', raw: pickExtras(ex, ['data_limite', 'data_fim', 'data_encerramento']), confidence: 0.78 },
    { field: 'metadata.prazo', raw: pickExtras(ex, ['prazo']), confidence: 0.72 },
  ];

  const seen = new Set();
  const out = [];
  for (const row of rows) {
    if (row.raw == null || row.raw === '') continue;
    const s = String(row.raw).trim();
    if (!s || seen.has(s)) continue;
    seen.add(s);
    out.push({ field: row.field, raw: s, confidence: row.confidence });
  }
  return out;
}

/**
 * Primeiro valor de prazo parseável (uso em listagens gerais).
 * @param {Record<string, unknown>} edital
 * @returns {string|null}
 */
export function getFirstParsableDeadlineRaw(edital) {
  const candidates = collectDeadlineCandidates(edital);
  for (const c of candidates) {
    const d = parseDateLoose(c.raw);
    if (d && !Number.isNaN(d.getTime())) return c.raw;
  }
  return candidates[0]?.raw ?? null;
}

/**
 * @param {Record<string, unknown>} edital
 */
function isEncerradoByStatus(edital) {
  const st = String(edital.situacao_raw ?? edital.situacao ?? edital.status ?? '')
    .trim()
    .toLowerCase();
  if (!st) return edital.ativo === false;
  return ENCERRADO_STATUS.has(st) || /\bencerrad|\bfechad|\bcancelad|\binativ/.test(st);
}

/**
 * @param {number|null} days
 * @returns {DashboardDeadlineStatus}
 */
function statusFromDays(days) {
  if (days == null) return 'sem_prazo';
  if (days < 0) return 'encerrado';
  if (days <= 7) return 'vencendo_7';
  if (days <= 30) return 'vencendo_30';
  return 'prazo_confortavel';
}

/**
 * @param {Record<string, unknown>} edital
 * @returns {{
 *   date: Date|null,
 *   sourceField: string|null,
 *   confidence: number,
 *   rawValue: string|null,
 *   status: DashboardDeadlineStatus,
 *   daysUntil: number|null,
 * }}
 */
export function extractDashboardDeadline(edital) {
  const candidates = collectDeadlineCandidates(edital);

  for (const c of candidates) {
    const d = parseDateLoose(c.raw);
    if (!d || Number.isNaN(d.getTime())) continue;
    const prazoMid = new Date(d);
    prazoMid.setHours(0, 0, 0, 0);
    const days = Math.round((prazoMid.getTime() - startOfTodayLocal()) / 86400000);
    return {
      date: d,
      sourceField: c.field,
      confidence: c.confidence,
      rawValue: c.raw,
      status: statusFromDays(days),
      daysUntil: days,
    };
  }

  if (candidates.length > 0) {
    return {
      date: null,
      sourceField: candidates[0].field,
      confidence: 0.4,
      rawValue: candidates[0].raw,
      status: 'prazo_invalido',
      daysUntil: null,
    };
  }

  if (isEncerradoByStatus(edital)) {
    return {
      date: null,
      sourceField: 'situacao/status',
      confidence: 0.45,
      rawValue: String(edital.situacao_raw ?? edital.situacao ?? edital.status ?? ''),
      status: 'encerrado',
      daysUntil: null,
    };
  }

  return {
    date: null,
    sourceField: null,
    confidence: 0,
    rawValue: null,
    status: 'sem_prazo',
    daysUntil: null,
  };
}
