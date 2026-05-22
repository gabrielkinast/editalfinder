import { interestLabelById } from './scientificInterestsConfig';
import { FEED_TYPE_LABEL } from './scientificFeedLoader';
import { buildScientificProjectIdeas } from './buildScientificProjectIdeas';
import { buildScientificStudyPath } from './buildScientificStudyPath';
import { buildSuggestedStudyRoute } from './buildSuggestedStudyRoute';
import { buildScientificProfessorQuestions } from './buildScientificProfessorQuestions';
import { pickRecommendedProject } from './pickRecommendedProject';
import { pickProjectsByLevelTier } from './rankScientificProjectIdeas';
import { logScientificWorkspace } from './scientificWorkspaceLog';
import { levelLabel } from './scientificProjectLevels';
import { cleanScientificTitle } from './cleanScientificTitle';
import { getDeepStudyArea } from './scientificDeepStudyCatalog';
import { resolveCanonicalInterest } from './scientificInterestAliases';
import { getBooksForArea } from './scientificBookCatalog';

/**
 * @param {object} input
 */
export function buildScientificBriefing(input = {}) {
  const activeInterests = input.activeInterests || [];
  const feedItems = input.feedItems || [];
  const notebookItems = input.notebookItems || [];

  const byType = {};
  for (const item of feedItems) {
    const t = item.feedType || 'outro';
    byType[t] = (byType[t] || 0) + 1;
  }

  const topItems = feedItems.slice(0, 3);
  const allIdeas = buildScientificProjectIdeas(activeInterests, notebookItems);
  const recommendedProject = pickRecommendedProject(allIdeas, activeInterests);
  const projectsByLevel = pickProjectsByLevelTier(allIdeas, activeInterests, notebookItems);
  const studyPath = buildScientificStudyPath(activeInterests, { feedItems, notebookItems });
  const suggestedRoute = buildSuggestedStudyRoute(activeInterests);
  const professorQuestions = buildScientificProfessorQuestions(activeInterests);
  const professorPick = professorQuestions[0] || null;

  const conceitos = (studyPath.primary || [])
    .flatMap((b) => {
      const deepFound = b.deep?.theory?.foundations?.[0];
      if (deepFound) return [deepFound, ...(b.intermediate || []).slice(0, 1)];
      return [...(b.fundamentals || []).slice(0, 1), ...(b.intermediate || []).slice(0, 1)];
    })
    .slice(0, 3);

  const primaryKey = activeInterests[0]
    ? resolveCanonicalInterest(activeInterests[0])
    : null;
  const primaryBooks = primaryKey ? getBooksForArea(primaryKey) : [];
  const theoryOfWeek =
    conceitos.length >= 2
      ? `${conceitos[0]} + ${conceitos[1]}`
      : conceitos[0] || null;
  const bookSuggestion =
    primaryBooks[0] ||
    (studyPath.primary?.[0]?.books?.[0]
      ? { title: studyPath.primary[0].books[0], author: '', why: 'Trilha de fundamentos' }
      : null);

  const categories = Object.entries(byType).map(([k, n]) => ({
    key: k,
    label: FEED_TYPE_LABEL[k] || k,
    count: n,
  }));

  const interestLabels = activeInterests.map(interestLabelById);

  const summaryLines = [
    `Interesses ativos: ${interestLabels.join(', ') || 'nenhum'}.`,
    suggestedRoute?.steps?.length
      ? `Rota sugerida (${suggestedRoute.label}): ${suggestedRoute.steps.slice(0, 4).join(' → ')}…`
      : null,
    recommendedProject
      ? `Projeto recomendado: ${cleanScientificTitle(recommendedProject.title || recommendedProject.titulo)} (${recommendedProject.levelLabel || levelLabel(recommendedProject.level)}).`
      : 'Projeto recomendado: ative interesses para sugestões.',
    conceitos.length
      ? `Conceitos para estudar: ${conceitos.join(', ')}.`
      : null,
    projectsByLevel.basico
      ? `Projeto básico: ${cleanScientificTitle(projectsByLevel.basico.title)}.`
      : null,
    projectsByLevel.intermediario
      ? `Projeto intermediário: ${cleanScientificTitle(projectsByLevel.intermediario.title)}.`
      : null,
    projectsByLevel.avancadoOuIc
      ? `Projeto avançado/IC: ${cleanScientificTitle(projectsByLevel.avancadoOuIc.title)}.`
      : null,
    theoryOfWeek ? `Teoria da semana: ${theoryOfWeek}.` : null,
    bookSuggestion
      ? `Livro sugerido: ${bookSuggestion.author ? `${bookSuggestion.author} — ` : ''}${bookSuggestion.title || bookSuggestion}.`
      : studyPath.primary?.[0]?.books?.[0]
        ? `Leitura sugerida: ${studyPath.primary[0].books[0]}.`
        : null,
    professorPick ? `Pergunta para o professor: ${professorPick.question}` : null,
    `Caderno: ${notebookItems.length} item(ns) salvo(s).`,
    `${feedItems.length} item(ns) relevante(s) no feed.`,
  ].filter(Boolean);

  const briefing = {
    generatedAt: new Date().toISOString(),
    refreshAt: input.refreshAt ?? null,
    activeInterests: interestLabels,
    feedCount: feedItems.length,
    notebookCount: notebookItems.length,
    categories,
    topItems: topItems.map((i) => ({
      titulo: i.titulo,
      tipo: FEED_TYPE_LABEL[i.feedType] || i.feedType,
      score: i.matchScore,
    })),
    ideas: allIdeas.slice(0, 2),
    conceitos,
    recommendedProject,
    suggestedRoute,
    projectsByLevel,
    professorPick,
    advancedSuggestion: projectsByLevel.avancadoOuIc?.title || null,
    basicProject: projectsByLevel.basico || null,
    intermediateProject: projectsByLevel.intermediario || null,
    theoryOfWeek,
    bookSuggestion: bookSuggestion
      ? {
          interest: studyPath.primary?.[0]?.label,
          text: bookSuggestion.author
            ? `${bookSuggestion.author} — ${bookSuggestion.title}`
            : String(bookSuggestion.title || bookSuggestion),
          why: bookSuggestion.why,
        }
      : studyPath.primary?.[0]?.books?.[0]
        ? { interest: studyPath.primary[0].label, text: studyPath.primary[0].books[0] }
        : null,
    readingSuggestion: studyPath.primary?.[0]?.books?.[0]
      ? { interest: studyPath.primary[0].label, text: studyPath.primary[0].books[0] }
      : null,
    summaryLines,
  };

  logScientificWorkspace('briefing_generated', {
    feedCount: feedItems.length,
    interests: activeInterests.length,
    hasRecommended: Boolean(recommendedProject),
    routeId: suggestedRoute?.id,
  });

  return briefing;
}
