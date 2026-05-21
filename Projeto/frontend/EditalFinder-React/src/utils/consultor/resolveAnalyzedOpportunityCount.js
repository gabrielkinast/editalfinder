/**
 * Total de oportunidades analisadas (carteira Radar) com fallback seguro.
 * @param {object} [params]
 * @param {number} [params.totalMatches]
 * @param {object[]} [params.allMatches]
 */
export function resolveAnalyzedOpportunityCount({ totalMatches, allMatches } = {}) {
  const fromTotal = Number(totalMatches);
  if (Number.isFinite(fromTotal) && fromTotal > 0) return fromTotal;
  const len = Array.isArray(allMatches) ? allMatches.length : 0;
  return len > 0 ? len : 0;
}
