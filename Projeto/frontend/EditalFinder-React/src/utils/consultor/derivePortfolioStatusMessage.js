/**
 * Mensagem de status da carteira no painel do consultor.
 * @returns {{ kind: 'loading'|'info'|'ready', message: string } | null}
 */
export function derivePortfolioStatusMessage(input = {}) {
  const {
    clienteId = '',
    catalogLoading = false,
    catalogError = null,
    editaisCount = 0,
    radarLoading = false,
    topMatchesReady = false,
    isPartial = false,
    hasPreviewResults = false,
    resultsReady = false,
    totalMatches = 0,
    topMatchesCount = 0,
    selectedCount = 0,
  } = input;

  if (!clienteId) return null;

  const hasTop = topMatchesCount > 0;
  const hasAll = totalMatches > 0;
  const hasSelected = selectedCount > 0;
  const hasAnyResults = hasTop || hasAll || hasSelected;
  const analyzedCount = totalMatches > 0 ? totalMatches : topMatchesCount;

  if (catalogLoading) {
    return { kind: 'loading', message: 'Carregando catálogo de oportunidades…' };
  }
  if (catalogError) return null;
  if (editaisCount === 0) {
    return { kind: 'info', message: 'Catálogo de oportunidades indisponível no momento.' };
  }

  if (radarLoading && hasAnyResults) {
    if (isPartial && hasPreviewResults) {
      return { kind: 'info', message: 'Prévia carregada — completando lista…' };
    }
    return { kind: 'info', message: 'Atualizando carteira em segundo plano…' };
  }

  if (radarLoading && !hasAnyResults) {
    return { kind: 'loading', message: 'Calculando carteira para este cliente…' };
  }

  if (isPartial && hasPreviewResults && hasAnyResults) {
    return { kind: 'info', message: 'Prévia carregada — completando lista…' };
  }

  if (analyzedCount > 0 && (resultsReady || topMatchesReady)) {
    return {
      kind: 'ready',
      message: `Carteira carregada — ${analyzedCount} oportunidades analisadas`,
    };
  }

  return null;
}
