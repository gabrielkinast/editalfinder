import { parseDateLoose, startOfTodayLocal } from './edital/dates';
import { getFirstParsableDeadlineRaw } from './dashboard/dashboardDeadlineFields';

/** @typedef {'prazo_indefinido'|'prazo_confortavel'|'vence_15_dias'|'vence_7_dias'|'vence_3_dias'|'vence_hoje'|'encerrado'} DeadlineAlertStatus */

/**
 * Extrai string de prazo de um edital ou linha da view de favoritos.
 * @param {Record<string, unknown>} edital
 * @returns {string|null}
 */
export function parsePrazoEnvio(edital) {
  if (!edital || typeof edital !== 'object') return null;
  const fromScan = getFirstParsableDeadlineRaw(edital);
  if (fromScan) return fromScan;
  const raw =
    edital.prazo_envio_raw ??
    edital.fim_inscricao_raw ??
    edital.dataLimite ??
    edital.prazo_envio ??
    edital.prazo ??
    edital.data_limite ??
    edital.prazo_final ??
    edital.encerramento ??
    edital.fim_inscricao ??
    null;
  if (raw == null || raw === '') return null;
  const s = String(raw).trim();
  return s || null;
}

/**
 * Dias até o prazo (meia-noite local). Negativo = já passou. null = sem prazo válido.
 * @param {Record<string, unknown>} edital
 * @returns {number|null}
 */
export function getDaysUntilDeadline(edital) {
  const raw = parsePrazoEnvio(edital);
  if (!raw) return null;
  const d = parseDateLoose(raw);
  if (!d || Number.isNaN(d.getTime())) return null;
  const end = startOfTodayLocal();
  const prazoMid = new Date(d);
  prazoMid.setHours(0, 0, 0, 0);
  return Math.round((prazoMid.getTime() - end) / 86400000);
}

/**
 * @param {Record<string, unknown>} edital
 * @returns {DeadlineAlertStatus}
 */
export function getDeadlineAlertStatus(edital) {
  const raw = parsePrazoEnvio(edital);
  if (!raw) return 'prazo_indefinido';
  const days = getDaysUntilDeadline(edital);
  if (days == null) return 'prazo_indefinido';
  if (days < 0) return 'encerrado';
  if (days === 0) return 'vence_hoje';
  if (days <= 3) return 'vence_3_dias';
  if (days <= 7) return 'vence_7_dias';
  if (days <= 15) return 'vence_15_dias';
  return 'prazo_confortavel';
}

/** @param {DeadlineAlertStatus} status */
export function getDeadlineAlertLabel(status) {
  switch (status) {
    case 'vence_hoje':
      return 'Vence hoje';
    case 'vence_3_dias':
      return 'Vence em até 3 dias';
    case 'vence_7_dias':
      return 'Vence em até 7 dias';
    case 'vence_15_dias':
      return 'Vence em até 15 dias';
    case 'prazo_confortavel':
      return 'Prazo confortável';
    case 'prazo_indefinido':
      return 'Prazo não informado';
    case 'encerrado':
      return 'Encerrado';
    default:
      return 'Prazo';
  }
}

/** @param {DeadlineAlertStatus} status */
export function getDeadlineAlertBadgeVariant(status) {
  if (status === 'encerrado') return 'bad';
  if (status === 'vence_hoje' || status === 'vence_3_dias') return 'bad';
  if (status === 'vence_7_dias') return 'warn';
  if (status === 'vence_15_dias') return 'warn';
  if (status === 'prazo_indefinido') return 'muted';
  return 'ok';
}

const ALERT_7D = new Set(['vence_hoje', 'vence_3_dias', 'vence_7_dias']);

/**
 * @param {unknown[]} favoritosRows linhas da view (ou objetos com campos de prazo)
 */
export function getFavoriteDeadlineSummary(favoritosRows) {
  const rows = Array.isArray(favoritosRows) ? favoritosRows : [];
  let alert7dCount = 0;
  const byStatus = {};
  for (const row of rows) {
    const st = getDeadlineAlertStatus(row);
    byStatus[st] = (byStatus[st] || 0) + 1;
    if (ALERT_7D.has(st)) alert7dCount += 1;
  }
  return { alert7dCount, byStatus, total: rows.length };
}
