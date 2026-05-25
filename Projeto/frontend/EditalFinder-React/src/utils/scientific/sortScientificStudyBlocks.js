import { resolveCanonicalInterest } from './scientificInterestAliases';

/** Trilhas “base” antes de variantes aplicadas/engenharia. */
const CANONICAL_BASE_PRIORITY = {
  nuclear: 1,
  fisico_quimica: 1,
  quantica: 1,
  plasmas_fusao: 1,
  dinamica_molecular: 1,
  quimica_nuclear: 1,
  computacao_cientifica: 1,
  monte_carlo: 1,
  materiais: 1,
  energia: 1,
  engenharia_fisica: 1,
  instrumentacao: 1,
  biotecnologia: 1,
  medicina_nuclear: 1,
  dosimetria: 1,
  protecao_radiologica: 1,
  espaco: 1,
  engenharia_aeroespacial: 1,
  engenharia_defesa: 2,
  engenharia_nuclear: 2,
  hpc: 2,
  ia_cientifica: 2,
  ciencia_dados: 2,
  sistemas_autonomos: 2,
  robotica: 2,
  tecnologias_estrategicas: 3,
};

function minInterestIndex(block, activeInterests) {
  const matched = block.matchedInterests || [block.sourceInterestId, block.interestId].filter(Boolean);
  let min = 9999;
  for (const id of matched) {
    const idx = activeInterests.indexOf(id);
    if (idx >= 0 && idx < min) min = idx;
  }
  const keyIdx = activeInterests.findIndex((id) => resolveCanonicalInterest(id) === block.canonicalKey);
  if (keyIdx >= 0 && keyIdx < min) min = keyIdx;
  return min === 9999 ? 500 : min;
}

function engagementScore(block, options = {}) {
  const matched = block.matchedInterests || [];
  const feed = options.feedItems || [];
  const notebook = options.notebookItems || [];
  let score = 0;
  for (const f of feed) {
    if ((f.matchedInterests || []).some((i) => matched.includes(i))) score += 3;
  }
  for (const n of notebook) {
    if ((n.interesses || []).some((i) => matched.includes(i) || i === block.canonicalKey)) score += 5;
  }
  return score;
}

/**
 * Ordena blocos de trilha para exibição coerente (Fase 2H-F).
 * @param {Array<object>} blocks
 * @param {string[]} activeInterests
 * @param {object} [options]
 */
export function sortScientificStudyBlocks(blocks = [], activeInterests = [], options = {}) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  return [...blocks].sort((a, b) => {
    const priA = CANONICAL_BASE_PRIORITY[a.canonicalKey] ?? 5;
    const priB = CANONICAL_BASE_PRIORITY[b.canonicalKey] ?? 5;
    if (priA !== priB) return priA - priB;

    const idxA = minInterestIndex(a, active);
    const idxB = minInterestIndex(b, active);
    if (idxA !== idxB) return idxA - idxB;

    const engA = engagementScore(a, options) + (a._sortScore || 0);
    const engB = engagementScore(b, options) + (b._sortScore || 0);
    if (engB !== engA) return engB - engA;

    return String(a.label || '').localeCompare(String(b.label || ''), 'pt-BR');
  });
}
