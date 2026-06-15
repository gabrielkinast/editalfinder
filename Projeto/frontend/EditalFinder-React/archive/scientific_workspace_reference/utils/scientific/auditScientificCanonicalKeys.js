import { SCIENTIFIC_INTERESTS } from './scientificInterestsConfig';
import {
  resolveCanonicalInterest,
  ALL_DEEP_CATALOG_CANONICAL_KEYS,
} from './scientificInterestAliases';
import { SCIENTIFIC_DEEP_STUDY_CATALOG } from './scientificDeepStudyCatalog';
import { normalizeStudyPathLabel } from './dedupeStudyPathBlocks';
import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Audita interesses ativos vs catálogo profundo (Fase 2H-F).
 * @param {string[]} activeInterests
 */
export function auditScientificCanonicalKeys(activeInterests = []) {
  const interests = Array.isArray(activeInterests) ? activeInterests : [];
  const canonicalKeys = [];
  const seenCanonical = new Set();
  const missingCatalogKeys = [];
  const labelToKeys = new Map();

  for (const id of interests) {
    const key = resolveCanonicalInterest(id);
    if (!key) continue;
    if (!seenCanonical.has(key)) {
      seenCanonical.add(key);
      canonicalKeys.push(key);
    }
    if (!SCIENTIFIC_DEEP_STUDY_CATALOG[key] && !missingCatalogKeys.includes(key)) {
      missingCatalogKeys.push(key);
    }
    const label = SCIENTIFIC_INTERESTS.find((i) => i.id === id)?.label || id;
    const norm = normalizeStudyPathLabel(label);
    if (!labelToKeys.has(norm)) labelToKeys.set(norm, new Set());
    labelToKeys.get(norm).add(key);
  }

  const duplicateLabels = [];
  for (const [label, keys] of labelToKeys) {
    if (keys.size > 1) {
      duplicateLabels.push({ label, canonicalKeys: [...keys] });
    }
  }

  const allUiIds = SCIENTIFIC_INTERESTS.map((i) => i.id);
  const unmappedUi = allUiIds.filter((id) => !resolveCanonicalInterest(id));

  const report = {
    interests,
    canonicalKeys,
    missingCatalogKeys,
    duplicateLabels,
    unmappedUi,
    catalogKeyCount: ALL_DEEP_CATALOG_CANONICAL_KEYS.length,
  };

  if (import.meta.env.DEV) {
    logScientificWorkspace('study_path_canonical_audit', report);
  }

  return report;
}
