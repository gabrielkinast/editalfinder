import { SCIENTIFIC_INTERESTS, interestLabelById } from './scientificInterestsConfig';
import { SCIENTIFIC_STUDY_CATALOG } from './scientificStudyCatalog';
import { buildDeepStudyBlock } from './buildDeepStudyBlock';
import { dedupeScientificStudyBlocks } from './dedupeScientificStudyBlocks';
import { sortScientificStudyBlocks } from './sortScientificStudyBlocks';
import { auditScientificCanonicalKeys } from './auditScientificCanonicalKeys';
import { groupActiveInterestsByCanonical } from './scientificInterestAliases';
import { logScientificWorkspace } from './scientificWorkspaceLog';

const DEFAULT_BLOCK = {
  interestId: null,
  canonicalKey: 'geral',
  label: 'Geral',
  fundamentals: ['Leitura de fontes do feed', 'Organização no caderno'],
  intermediate: ['Aprofundar um tema do catálogo'],
  advanced: ['Projeto prático guiado'],
  books: ['Material aberto do domínio escolhido'],
  practicalProjects: ['Resumo crítico de 3 fontes'],
  researchIdeas: ['Definir pergunta com orientador'],
  professorQuestions: ['Quais pré-requisitos devo consolidar primeiro?'],
};

function priorityScore(canonicalKey, matchedIds, options = {}) {
  const active = options.activeInterests || [];
  let score = 0;
  for (const id of matchedIds) {
    const idx = active.indexOf(id);
    if (idx >= 0) score += Math.max(0, 20 - idx);
  }
  const feed = options.feedItems || [];
  const notebook = options.notebookItems || [];
  const feedHits = feed.filter((f) =>
    (f.matchedInterests || []).some((i) => matchedIds.includes(i)),
  ).length;
  const nbHits = notebook.filter((n) =>
    (n.interesses || []).some((i) => matchedIds.includes(i)),
  ).length;
  score += feedHits * 3 + nbHits * 5;
  return score;
}

function blockFromCanonical(canonicalKey, matchedInterestIds, options = {}) {
  const primaryId = matchedInterestIds[0];
  const deepBlock = buildDeepStudyBlock(primaryId, matchedInterestIds);
  if (deepBlock) return deepBlock;

  const meta = SCIENTIFIC_INTERESTS.find((i) => i.id === primaryId);
  const cat = SCIENTIFIC_STUDY_CATALOG[canonicalKey] || SCIENTIFIC_STUDY_CATALOG[primaryId];
  if (!cat) {
    return {
      ...DEFAULT_BLOCK,
      interestId: canonicalKey,
      canonicalKey,
      matchedInterests: matchedInterestIds,
      matchedInterestLabels: matchedInterestIds.map(interestLabelById),
      label: meta?.label || interestLabelById(primaryId) || canonicalKey,
    };
  }
  return {
    interestId: canonicalKey,
    canonicalKey,
    matchedInterests: matchedInterestIds,
    matchedInterestLabels: matchedInterestIds.map(interestLabelById),
    label: cat.label || meta?.label || canonicalKey,
    fundamentals: cat.fundamentals || [],
    intermediate: cat.intermediate || [],
    advanced: cat.advanced || [],
    books: cat.books || [],
    practicalProjects: cat.practicalProjects || [],
    researchIdeas: cat.researchIdeas || [],
    professorQuestions: cat.professorQuestions || [],
  };
}

/**
 * @param {string[]} activeInterests
 * @param {object} [options]
 */
export function buildScientificStudyPath(activeInterests = [], options = {}) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  const primaryLimit = options.primaryLimit ?? 5;

  const { canonicalKeys, interestByCanonical } = groupActiveInterestsByCanonical(active);

  const scored = canonicalKeys.map((key) => ({
    key,
    matched: interestByCanonical[key] || [],
    score: priorityScore(key, interestByCanonical[key] || [], { ...options, activeInterests: active }),
  }));

  scored.sort((a, b) => b.score - a.score);

  const allBlocks = scored.map(({ key, matched, score }) => {
    const block = blockFromCanonical(key, matched, options);
    block._sortScore = score;
    return block;
  });

  auditScientificCanonicalKeys(active);

  const deduped = sortScientificStudyBlocks(
    dedupeScientificStudyBlocks(allBlocks),
    active,
    options,
  );

  const primary = deduped.slice(0, primaryLimit);
  const secondary = deduped.slice(primaryLimit);

  if (!primary.length) {
    logScientificWorkspace('study_catalog_loaded', { count: 0, fallback: true });
    return { primary: [DEFAULT_BLOCK], secondary: [], allInterestIds: [], canonicalKeys: [] };
  }

  logScientificWorkspace('study_catalog_loaded', {
    count: primary.length,
    secondary: secondary.length,
    canonicalKeys: primary.map((b) => b.canonicalKey),
    dedupedFrom: allBlocks.length,
  });

  return {
    primary,
    secondary,
    allInterestIds: active,
    canonicalKeys: deduped.map((b) => b.canonicalKey),
    labels: deduped.map((b) => b.label),
    allBlocks: deduped,
  };
}
