import { defineDeepArea } from './deepStudyCatalogHelpers';
import { resolveCanonicalInterest, ALL_DEEP_CATALOG_CANONICAL_KEYS } from './scientificInterestAliases';
import { SCIENTIFIC_DEEP_STUDY_CATALOG_ENTRIES } from './scientificDeepStudyCatalogEntries';
import { REMAINING_DEEP_CATALOG_ENTRIES } from './scientificDeepStudyCatalogRemaining';
import { PHASE_2HA_PHYSICS_CHEM_NUCLEAR } from './scientificDeepStudyCatalogPhase2HA';
import { PHASE_2HB_COMPUTE_SIM_DATA } from './scientificDeepStudyCatalogPhase2HB';
import { PHASE_2HC_MATERIALS_ENERGY_INSTR_BIO } from './scientificDeepStudyCatalogPhase2HC';
import { PHASE_2HD_DEFENSE_SPACE_AERO_STRATEGIC } from './scientificDeepStudyCatalogPhase2HD';
import { PHASE_2HE_HEALTH_RADIATION } from './scientificDeepStudyCatalogPhase2HE';

/** @deprecated use resolveCanonicalInterest from scientificInterestAliases */
export const DEEP_CATALOG_INTEREST_ALIAS = {};

export const SCIENTIFIC_DEEP_STUDY_CATALOG = {
  ...SCIENTIFIC_DEEP_STUDY_CATALOG_ENTRIES,
  ...REMAINING_DEEP_CATALOG_ENTRIES,
  ...PHASE_2HA_PHYSICS_CHEM_NUCLEAR,
  ...PHASE_2HB_COMPUTE_SIM_DATA,
  ...PHASE_2HC_MATERIALS_ENERGY_INSTR_BIO,
  ...PHASE_2HD_DEFENSE_SPACE_AERO_STRATEGIC,
  ...PHASE_2HE_HEALTH_RADIATION,
};

/** Garante catálogo mínimo para qualquer chave canônica listada */
for (const key of ALL_DEEP_CATALOG_CANONICAL_KEYS) {
  if (!SCIENTIFIC_DEEP_STUDY_CATALOG[key]) {
    SCIENTIFIC_DEEP_STUDY_CATALOG[key] = defineDeepArea({
      label: key.replace(/_/g, ' '),
      aliases: [key],
    });
  }
}

/**
 * @param {string} interestId
 * @returns {string | null}
 */
export function resolveDeepCatalogKey(interestId) {
  const canonical = resolveCanonicalInterest(interestId);
  if (SCIENTIFIC_DEEP_STUDY_CATALOG[canonical]) return canonical;
  return null;
}

/**
 * @param {string} interestId
 */
export function getDeepStudyArea(interestId) {
  const key = resolveDeepCatalogKey(interestId);
  if (!key) return null;
  return { key, ...SCIENTIFIC_DEEP_STUDY_CATALOG[key] };
}
