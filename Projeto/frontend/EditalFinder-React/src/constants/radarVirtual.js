/**
 * Lista virtualizada (Fase 0.7) — EXPERIMENTAL, desativada por padrão.
 * Causou sobreposição de cards / grid quebrado. Usar grid paginado (visibleCap).
 */
export const RADAR_USE_VIRTUAL_LIST = false;

/** Abaixo deste total, grid normal (sem react-window) mesmo se virtual estiver ligada. */
export const RADAR_VIRTUAL_THRESHOLD = 30;

/** Render inicial e incremento do botão “Mostrar mais” (grid paginado). */
export const RADAR_VISIBLE_INITIAL_CAP = 24;
export const RADAR_VISIBLE_LOAD_MORE_STEP = 24;

export function shouldUseRadarVirtualList(itemCount) {
  return RADAR_USE_VIRTUAL_LIST && itemCount > RADAR_VIRTUAL_THRESHOLD;
}
