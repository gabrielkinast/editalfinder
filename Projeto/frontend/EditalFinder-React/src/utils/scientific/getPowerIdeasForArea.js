import { SCIENTIFIC_POWER_IDEAS_CATALOG } from './scientificPowerIdeasCatalog';

/**
 * @param {string} canonicalKey
 * @returns {Array<object>}
 */
export function getPowerIdeasForArea(canonicalKey) {
  if (!canonicalKey) return [];
  return SCIENTIFIC_POWER_IDEAS_CATALOG[canonicalKey] || [];
}

/**
 * @param {string} canonicalKey
 * @param {string} ideaId
 */
export function getPowerIdeaById(canonicalKey, ideaId) {
  return getPowerIdeasForArea(canonicalKey).find((i) => i.id === ideaId) || null;
}
