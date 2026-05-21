import { getDeadlineAlertStatus } from './deadlineAlerts';

/**
 * Resumo de prazos sobre matches do Radar (workspace consultor).
 * @param {object[]} matches — linhas useRadarMatches (com .edital)
 */
export function summarizeMatchDeadlines(matches) {
  const list = Array.isArray(matches) ? matches : [];
  let venceAte7 = 0;
  let semPrazo = 0;
  let prazoConfortavel = 0;

  for (const row of list) {
    const edital = row?.edital;
    if (!edital) continue;
    const status = getDeadlineAlertStatus(edital);
    if (status === 'prazo_indefinido') {
      semPrazo += 1;
    } else if (
      status === 'vence_7_dias' ||
      status === 'vence_3_dias' ||
      status === 'vence_hoje'
    ) {
      venceAte7 += 1;
    } else if (status === 'prazo_confortavel' || status === 'vence_15_dias') {
      prazoConfortavel += 1;
    }
  }

  return { venceAte7, semPrazo, prazoConfortavel, total: list.length };
}
