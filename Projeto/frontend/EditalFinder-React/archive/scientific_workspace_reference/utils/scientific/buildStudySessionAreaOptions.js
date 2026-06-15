import { interestLabelById } from './scientificInterestsConfig';
import { resolveCanonicalInterest } from './scientificInterestAliases';
import { logScientificWorkspace } from './scientificWorkspaceLog';
import {
  AREA_SCOPE_ALL_ACTIVE,
  AREA_SCOPE_GOAL_ROUTE,
  AREA_SCOPE_REVIEW_GENERAL,
} from './studySessionAreaScope';

/**
 * @param {object} params
 * @returns {Array<{ value: string, label: string, type: 'special'|'area', canonicalKey?: string }>}
 */
export function buildStudySessionAreaOptions({
  studyBlocks = [],
  activeInterests = [],
  goalRoutes = [],
  includeReviewOption = false,
} = {}) {
  const options = [];

  options.push({
    value: AREA_SCOPE_ALL_ACTIVE,
    label: 'Todas as áreas ativas',
    type: 'special',
  });

  if (goalRoutes.length > 0) {
    const route = goalRoutes[0];
    options.push({
      value: AREA_SCOPE_GOAL_ROUTE,
      label: route?.title ? `Minha rota sugerida (${route.title})` : 'Minha rota sugerida',
      type: 'special',
      routeId: route?.id,
    });
  }

  if (includeReviewOption) {
    options.push({
      value: AREA_SCOPE_REVIEW_GENERAL,
      label: 'Revisão geral',
      type: 'special',
    });
  }

  const byKey = new Map();

  for (const block of studyBlocks) {
    const key = block.canonicalKey || block.interestId;
    if (!key || byKey.has(key)) continue;
    byKey.set(key, {
      value: key,
      label: block.label || interestLabelById(key) || key,
      type: 'area',
      canonicalKey: key,
      hasBlock: true,
    });
  }

  for (const interestId of activeInterests || []) {
    const key = resolveCanonicalInterest(interestId);
    if (!key || byKey.has(key)) continue;
    byKey.set(key, {
      value: key,
      label: interestLabelById(key) || key,
      type: 'area',
      canonicalKey: key,
      hasBlock: false,
    });
  }

  const areaList = [...byKey.values()].sort((a, b) =>
    String(a.label).localeCompare(String(b.label), 'pt'),
  );

  const result = [...options, ...areaList];

  if (import.meta.env.DEV) {
    logScientificWorkspace('study_session_area_options_built', {
      totalOptions: result.length,
      activeInterests: activeInterests?.length ?? 0,
      studyBlockKeys: studyBlocks.map((b) => b.canonicalKey || b.interestId),
      options: result.map((o) => ({ value: o.value, label: o.label, type: o.type })),
    });
  }

  return result;
}

/**
 * @param {string} areaSelection
 * @param {Array} areaOptions
 */
export function getAreaOptionLabel(areaSelection, areaOptions = []) {
  const found = areaOptions.find((o) => o.value === areaSelection);
  return found?.label || interestLabelById(areaSelection) || areaSelection;
}
