import {
  AREA_SCOPE_ALL_ACTIVE,
  AREA_SCOPE_GOAL_ROUTE,
} from './studySessionAreaScope';
import { getAreaOptionLabel } from './buildStudySessionAreaOptions';

/**
 * @param {object} params
 */
export function formatStudySessionCounter({
  areaSelection,
  areaOptions = [],
  totalInScope = 0,
  distinctAreas = 0,
  displayedCount = 0,
  selectedCount = 0,
}) {
  let headline = '';
  if (areaSelection === AREA_SCOPE_ALL_ACTIVE) {
    headline = `${totalInScope} itens encontrados em ${distinctAreas} área${distinctAreas !== 1 ? 's' : ''} ativa${distinctAreas !== 1 ? 's' : ''}`;
  } else if (areaSelection === AREA_SCOPE_GOAL_ROUTE) {
    headline = `${totalInScope} itens encontrados na sua rota sugerida`;
  } else {
    const label = getAreaOptionLabel(areaSelection, areaOptions);
    headline = `${totalInScope} itens encontrados em ${label}`;
  }

  const sub =
    displayedCount >= totalInScope
      ? `Mostrando todos. Use busca para refinar.`
      : `Mostrando ${displayedCount}. Use busca/filtros para refinar.`;

  const sel = selectedCount > 0 ? ` · ${selectedCount} selecionado${selectedCount !== 1 ? 's' : ''}` : '';

  return { headline, sub: sub + sel };
}
