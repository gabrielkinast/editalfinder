import { logScientificWorkspace } from './scientificWorkspaceLog';
import { blockDepthScore } from './blockDepthScore';
import { normalizeStudyPathLabel, dedupeStudyPathBlocks as dedupeByKey } from './dedupeStudyPathBlocks';

export { normalizeStudyPathLabel };

function mergeBlocks(target, source) {
  const mergedInterests = new Set([
    ...(target.matchedInterests || []),
    ...(source.matchedInterests || []),
    target.sourceInterestId,
    source.sourceInterestId,
  ].filter(Boolean));

  target.matchedInterests = [...mergedInterests];
  target.matchedInterestLabels = [
    ...new Set([...(target.matchedInterestLabels || []), ...(source.matchedInterestLabels || [])]),
  ];

  if (blockDepthScore(source) > blockDepthScore(target)) {
    const keepMatched = target.matchedInterests;
    const keepLabels = target.matchedInterestLabels;
    Object.assign(target, source, {
      matchedInterests: keepMatched,
      matchedInterestLabels: keepLabels,
    });
  }
}

/**
 * Deduplica trilhas por canonicalKey e label; mantém a mais profunda (Fase 2H-F).
 * @param {Array<object>} blocks
 * @returns {Array<object>}
 */
export function dedupeScientificStudyBlocks(blocks = []) {
  const byCanonical = new Map();

  for (const block of blocks) {
    const canonicalKey = block.canonicalKey || block.interestId || 'unknown';
    const existing = byCanonical.get(canonicalKey);
    if (!existing) {
      byCanonical.set(canonicalKey, {
        ...block,
        canonicalKey,
        matchedInterests: [...(block.matchedInterests || [block.sourceInterestId].filter(Boolean))],
      });
      continue;
    }
    mergeBlocks(existing, block);
    if (import.meta.env.DEV) {
      logScientificWorkspace('study_path_duplicate_merged', {
        canonicalKey,
        label: block.label,
        mergedCount: existing.matchedInterests?.length,
        reason: 'canonicalKey',
      });
    }
  }

  let list = [...byCanonical.values()];

  const byLabel = new Map();
  for (const block of list) {
    const labelKey = normalizeStudyPathLabel(block.label);
    const existing = byLabel.get(labelKey);
    if (!existing) {
      byLabel.set(labelKey, block);
      continue;
    }
    mergeBlocks(existing, block);
    if (import.meta.env.DEV) {
      logScientificWorkspace('study_path_duplicate_merged', {
        label: block.label,
        canonicalKey: block.canonicalKey,
        reason: 'label',
      });
    }
  }

  list = [...byLabel.values()];

  return dedupeByKey(list);
}
