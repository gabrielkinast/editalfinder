import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Normaliza label para deduplicação visual.
 * @param {string} label
 */
export function normalizeStudyPathLabel(label) {
  return String(label || '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .replace(/\s+/g, ' ');
}

/**
 * Mescla blocos de trilha com mesma chave canônica ou label.
 * @param {Array<object>} blocks
 * @returns {Array<object>}
 */
export function dedupeStudyPathBlocks(blocks = []) {
  const byKey = new Map();

  for (const block of blocks) {
    const canonicalKey = block.canonicalKey || block.interestId || 'unknown';
    const labelKey = normalizeStudyPathLabel(block.label);
    const mapKey = `${canonicalKey}::${labelKey}`;

    const existing = byKey.get(mapKey);
    if (!existing) {
      byKey.set(mapKey, {
        ...block,
        canonicalKey,
        matchedInterests: [...(block.matchedInterests || [block.sourceInterestId].filter(Boolean))],
      });
      continue;
    }

    const mergedInterests = new Set([
      ...(existing.matchedInterests || []),
      ...(block.matchedInterests || []),
      block.sourceInterestId,
      existing.sourceInterestId,
    ].filter(Boolean));

    existing.matchedInterests = [...mergedInterests];
    existing.matchedInterestLabels = [
      ...new Set([
        ...(existing.matchedInterestLabels || []),
        ...(block.matchedInterestLabels || []),
      ]),
    ];

    if (import.meta.env.DEV) {
      logScientificWorkspace('study_path_duplicate_merged', {
        canonicalKey,
        label: block.label,
        mergedCount: existing.matchedInterests.length,
      });
    }
  }

  return [...byKey.values()];
}
