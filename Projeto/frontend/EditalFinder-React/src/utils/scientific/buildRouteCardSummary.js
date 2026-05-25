import { interestLabelById } from './scientificInterestsConfig';
import { buildScientificBriefing } from './buildScientificBriefing';
import { pickPrimaryGoalRoute } from './buildScientificGoalRoutes';
import { pickPowerIdeaForGoalRoute } from './pickPowerIdeaForGoalRoute';
import { buildScientificStudyPath } from './buildScientificStudyPath';
import { buildScientificProjectIdeas } from './buildScientificProjectIdeas';
import { getBooksForInterests } from './scientificBookCatalog';
import { buildScientificNextAction } from './buildScientificNextAction';
import { cleanScientificTitle, withScientificPrefix } from './cleanScientificTitle';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Resumo para o card "Minha rota científica".
 */
export function buildRouteCardSummary(input = {}) {
  const activeInterests = input.activeInterests || [];
  const briefing = buildScientificBriefing(input);
  const studyPath = buildScientificStudyPath(activeInterests, input);
  const projectIdeas = buildScientificProjectIdeas(activeInterests, input.notebookItems || []);
  const goalRoute = pickPrimaryGoalRoute({
    interests: activeInterests,
    studyBlocks: studyPath.allBlocks || [...studyPath.primary, ...studyPath.secondary],
    projectIdeas,
    books: getBooksForInterests(activeInterests),
  });
  const route = goalRoute
    ? {
        id: goalRoute.id,
        label: goalRoute.title,
        steps: goalRoute.steps,
        description: goalRoute.description,
        suggestedProjects: goalRoute.suggestedProjects,
        suggestedBooks: goalRoute.suggestedBooks,
      }
    : briefing.suggestedRoute;
  const powerIdeaPick = pickPowerIdeaForGoalRoute({
    goalRoute,
    activeInterests,
  });
  const steps = route?.steps || [];
  const conceitos = briefing.conceitos || [];
  let nextConcept = conceitos[0] || steps[0] || null;
  if (steps.length >= 2) {
    nextConcept = `${steps[0]} e ${steps[1]}`;
  }

  let nextStepText = 'Ative interesses e explore a trilha de fundamentos.';
  if (steps.length >= 2) {
    nextStepText = `Estudar ${steps[0].toLowerCase()} e ${steps[1].toLowerCase()} antes de avançar na rota.`;
  } else if (steps.length === 1) {
    nextStepText = `Começar por: ${steps[0]}.`;
  } else if (conceitos.length) {
    nextStepText = `Focar em: ${conceitos.slice(0, 2).join(' e ')}.`;
  }

  const summary = {
    interestLabels: activeInterests.map(interestLabelById),
    interestsLine: activeInterests.map(interestLabelById).join(' + ') || 'Nenhum',
    routeLabel: route?.label || 'Exploratória',
    goalRouteTitle: goalRoute?.title || null,
    routeSteps: steps,
    routeDescription: route?.description || goalRoute?.description || null,
    routeBooks: goalRoute?.suggestedBooks || [],
    nextStepText,
    nextConcept,
    recommendedProject: briefing.recommendedProject,
    professorQuestion: briefing.professorPick?.question || null,
    professorLabel: briefing.professorPick?.label || null,
    topFeedItem: briefing.topItems?.[0] || null,
    conceitos,
    suggestedRoute: route,
    goalRoute,
    powerIdeaPick,
    powerIdea: powerIdeaPick?.idea || null,
    powerIdeaAreaKey: powerIdeaPick?.areaKey || null,
    powerIdeaAreaLabel: powerIdeaPick?.areaKey
      ? interestLabelById(powerIdeaPick.areaKey) || powerIdeaPick.areaKey
      : null,
  };

  summary.nextAction = buildScientificNextAction({
    interests: activeInterests,
    notebookItems: input.notebookItems,
    projectIdeas,
    studyRoute: route,
    feedItems: input.feedItems,
    routeSummary: summary,
  });

  logScientificWorkspace('route_card_rendered', {
    interests: summary.interestLabels.length,
    routeId: route?.id,
  });

  return summary;
}

/**
 * Item completo de rota para o caderno (Fase 2D).
 */
export function notebookEntryFromStudyRoute(summary, activeInterests = []) {
  const steps = summary.routeSteps || [];
  const labels = summary.interestLabels || activeInterests.map(interestLabelById);
  const titulo = withScientificPrefix('Rota científica', labels.join(' + ') || summary.routeLabel);

  const projetos = [];
  if (summary.recommendedProject?.title || summary.recommendedProject?.titulo) {
    projetos.push(
      cleanScientificTitle(summary.recommendedProject.title || summary.recommendedProject.titulo),
    );
  }

  const perguntas = [];
  if (summary.professorQuestion) perguntas.push(summary.professorQuestion);

  const routeKey = getScientificNotebookEntryKey({
    tipo: 'rota_estudo',
    titulo,
    interesses: activeInterests,
  });

  const entry = sanitizeScientificNotebookEntry({
    id: `route-${routeKey.replace(/\|/g, '_').slice(0, 72)}`,
    contentCategory: 'estudo',
    notebookGroup: 'rotas',
    tipo: 'rota_estudo',
    titulo,
    title: titulo,
    fonte: 'Workspace Científico',
    resumo: 'Sequência sugerida de conceitos e projetos.',
    interesses: [...activeInterests],
    conceitos: summary.conceitos || steps.slice(0, 8),
    projetos,
    perguntas,
    routeSteps: steps,
    savedAt: new Date().toISOString(),
    notes: [
      summary.nextStepText,
      steps.length ? `Passos:\n${steps.map((s, i) => `${i + 1}. ${s}`).join('\n')}` : '',
    ]
      .filter(Boolean)
      .join('\n\n'),
    nextSteps: steps,
    expectedOutput: 'Plano de estudo pessoal',
  });

  logScientificWorkspace('route_saved_to_notebook', {
    titulo: entry.titulo,
    interesses: activeInterests.length,
  });

  return entry;
}
