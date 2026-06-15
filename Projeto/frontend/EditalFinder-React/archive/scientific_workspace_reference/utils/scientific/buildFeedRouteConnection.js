import { interestLabelById } from './scientificInterestsConfig';

/**
 * Frase heurística "Conecta com sua rota porque…" (Fase 2D).
 */
export function buildFeedRouteConnection(item, activeInterests = []) {
  const matched = (item?.matchedInterests || []).filter((id) => activeInterests.includes(id));
  if (matched.length === 0) return null;

  const labels = matched.map(interestLabelById);
  if (labels.length === 1) {
    return `Conecta com sua rota porque envolve ${labels[0]}, um interesse ativo.`;
  }
  if (labels.length === 2) {
    return `Conecta com sua rota porque envolve ${labels[0]} e ${labels[1]}, dois interesses ativos.`;
  }
  const last = labels[labels.length - 1];
  const rest = labels.slice(0, -1).join(', ');
  return `Conecta com sua rota porque envolve ${rest} e ${last}.`;
}
