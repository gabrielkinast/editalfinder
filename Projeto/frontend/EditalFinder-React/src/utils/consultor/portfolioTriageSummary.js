import { CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES } from './consultorWorkspaceConstants';
import { pickPrimaryOpportunity } from './opportunitySelection';

function tituloCurto(t, max = 64) {
  const s = String(t || '').trim();
  if (!s) return null;
  return s.length > max ? `${s.slice(0, max)}…` : s;
}

/**
 * Resumo consultivo para triagem (carteira completa / modal).
 * @param {object} params
 */
export function buildPortfolioTriageSummary({
  totalMatches = 0,
  quickViewCount = CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES,
  selectedCount = 0,
  selectionBarSummary = null,
  deadlineSummary = null,
  topMatchTitulo = null,
}) {
  const principalTitulo =
    selectionBarSummary?.primaryTitulo ||
    (selectionBarSummary?.primary ? selectionBarSummary.primary.titulo : null) ||
    topMatchTitulo;

  return {
    totalMatches,
    quickViewCount,
    selectedCount,
    principalTitulo: tituloCurto(principalTitulo, 72),
    semPrazo: deadlineSummary?.semPrazo ?? selectionBarSummary?.semPrazo ?? 0,
    venceAte7: deadlineSummary?.venceAte7 ?? 0,
    prazoConfortavel: deadlineSummary?.prazoConfortavel ?? 0,
  };
}

/**
 * Principal sugerida por maior score entre matches visíveis.
 * @param {object[]} matches
 */
export function suggestedPrincipalFromMatches(matches) {
  if (!Array.isArray(matches) || !matches.length) return null;
  const normalized = matches.map((row) => ({
    key: row?.edital?.id ?? row?.id,
    titulo: row?.edital?.titulo || '',
    scorePct: Number.isFinite(Number(row?.score)) ? Math.round(Number(row.score)) : 0,
    row,
  }));
  const p = pickPrimaryOpportunity(normalized);
  return p?.titulo ? tituloCurto(p.titulo, 72) : null;
}
