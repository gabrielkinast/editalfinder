import { extractDashboardDeadline } from '../dashboard/dashboardDeadlineFields';

export { extractDashboardDeadline };

/**
 * Status de prazo alinhado ao Dashboard (extractDashboardDeadline).
 * @param {Record<string, unknown>} edital
 * @returns {'vencendo_7'|'vencendo_30'|'prazo_confortavel'|'encerrado'|'sem_prazo'|'prazo_invalido'}
 */
export function getEditalDeadlineStatus(edital) {
  return extractDashboardDeadline(edital).status;
}

/**
 * @param {Record<string, unknown>} edital
 * @param {string} prazoFilter
 */
export function editalMatchesPrazoQuery(edital, prazoFilter) {
  if (!prazoFilter) return true;
  const st = getEditalDeadlineStatus(edital);
  switch (prazoFilter) {
    case 'vencendo_7':
      return st === 'vencendo_7';
    case 'vencendo_30':
      return st === 'vencendo_7' || st === 'vencendo_30';
    case 'sem_prazo':
      return st === 'sem_prazo';
    case 'encerrados':
      return st === 'encerrado';
    case 'prazo_confortavel':
      return st === 'prazo_confortavel';
    case 'prazo_invalido':
      return st === 'prazo_invalido';
    default:
      return true;
  }
}
