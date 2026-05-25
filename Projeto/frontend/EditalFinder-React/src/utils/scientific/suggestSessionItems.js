import { getStudySessionPipeline } from './getStudySessionPipeline';

/**
 * Sugestões de sessão via pool completo (Fase 2L-B).
 * @param {object} params
 */
export function suggestSessionItems(params = {}) {
  const {
    block,
    studyBlocks = [],
    studyProgress = {},
    focus = 'theory',
    bookProgress = {},
    goalRoutes = [],
    notebookItems = [],
    activeInterests = [],
    limit = 20,
    plannedMinutes = 30,
    level = '',
    status = '',
    search = '',
    selectedCanonicalKey,
  } = params;

  const canonicalKey = selectedCanonicalKey || block?.canonicalKey || block?.interestId || '';

  const pipeline = getStudySessionPipeline({
    studyBlocks: studyBlocks.length ? studyBlocks : block ? [block] : [],
    activeInterests,
    selectedCanonicalKey: canonicalKey,
    goalRoutes,
    progressState: studyProgress,
    bookProgress,
    notebookItems,
    focus,
    level,
    status,
    search,
    quantity: limit,
    plannedMinutes,
  });

  return pipeline.visible.map((item) => ({
    progressKey: item.progressKey,
    kind: item.kind,
    title: item.title,
    subtitle: item.subtitle,
    level: item.level,
    segment: item.segment,
    status: item.status,
    areaLabel: item.areaLabel,
    canonicalKey: item.canonicalKey,
    source: item.source,
    suggested: true,
    ...item,
  }));
}

export { getStudySessionPipeline };
