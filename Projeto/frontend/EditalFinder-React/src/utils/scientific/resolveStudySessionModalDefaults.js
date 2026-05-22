import {
  AREA_SCOPE_ALL_ACTIVE,
  AREA_SCOPE_GOAL_ROUTE,
} from './studySessionAreaScope';

/**
 * Estado inicial do modal conforme origem da abertura (Fase 2L-C).
 * @param {object} initial
 */
export function resolveStudySessionModalDefaults(initial = {}) {
  const source = initial.openSource || 'study_path';

  if (source === 'review' || initial.focus === 'review') {
    return {
      areaSelection: AREA_SCOPE_ALL_ACTIVE,
      focus: 'review',
      quantity: initial.quantity ?? 0,
      plannedMinutes: initial.plannedMinutes ?? 30,
      levelFilter: '',
      statusFilter: '',
    };
  }

  if (source === 'route' || initial.areaSelection === AREA_SCOPE_GOAL_ROUTE) {
    return {
      areaSelection: AREA_SCOPE_GOAL_ROUTE,
      focus: initial.focus || 'mixed',
      quantity: initial.quantity ?? 10,
      plannedMinutes: initial.plannedMinutes ?? 30,
      levelFilter: '',
      statusFilter: '',
      goalRouteId: initial.goalRouteId || null,
    };
  }

  if (source === 'trail' && (initial.canonicalKey || initial.areaSelection)) {
    const key = initial.areaSelection || initial.canonicalKey;
    return {
      areaSelection: key,
      focus: initial.focus || 'theory',
      quantity: initial.quantity ?? 10,
      plannedMinutes: initial.plannedMinutes ?? 30,
      levelFilter: '',
      statusFilter: '',
    };
  }

  return {
    areaSelection: initial.areaSelection || AREA_SCOPE_ALL_ACTIVE,
    focus: initial.focus || 'mixed',
    quantity: initial.quantity ?? 10,
    plannedMinutes: initial.plannedMinutes ?? 30,
    levelFilter: '',
    statusFilter: '',
  };
}
