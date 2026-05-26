import { interestLabelById } from './scientificInterestsConfig';
import { cleanScientificTitle } from './cleanScientificTitle';
import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * @param {object} input
 * @param {string[]} input.interests — activeInterests
 * @param {Array} input.notebookItems
 * @param {Array} input.projectIdeas
 * @param {object} input.studyRoute — suggestedRoute
 * @param {Array} input.feedItems
 * @param {object} [input.routeSummary]
 */
export function buildScientificNextAction(input = {}) {
  const interests = input.interests || input.activeInterests || [];
  const notebookItems = input.notebookItems || [];
  const projectIdeas = input.projectIdeas || [];
  const feedItems = input.feedItems || [];
  const routeSummary = input.routeSummary || {};
  const steps = input.studyRoute?.steps || routeSummary.routeSteps || [];

  const hasProjectInNotebook = notebookItems.some(
    (n) => n.contentCategory === 'projeto' || n.level,
  );
  const hasRouteInNotebook = notebookItems.some(
    (n) => String(n.tipo || '').toLowerCase() === 'rota_estudo',
  );

  let action = {
    title: 'Explore sua rota',
    description: 'Ative interesses e siga a trilha sugerida.',
    actionLabel: 'Ver interesses',
    targetSection: 'scientific-interests',
  };

  if (interests.length === 0) {
    action = {
      title: 'Defina seus interesses',
      description: 'Marque temas científicos para personalizar rota, projetos e feed.',
      actionLabel: 'Editar interesses',
      targetSection: 'scientific-interests',
    };
  } else if (notebookItems.length === 0) {
    action = {
      title: 'Monte seu caderno',
      description: 'Salve uma ideia de projeto ou sua rota científica para começar a organizar estudos.',
      actionLabel: 'Ver ideias de projeto',
      targetSection: 'scientific-projects',
    };
  } else if (!hasProjectInNotebook && projectIdeas.length > 0) {
    const mid = projectIdeas.find((i) => i.level === 'intermediario') || projectIdeas[0];
    action = {
      title: 'Salve uma ideia no caderno',
      description: mid
        ? `Considere "${cleanScientificTitle(mid.title)}" — nível ${mid.levelLabel || 'intermediário'}.`
        : 'Escolha um projeto alinhado aos seus interesses.',
      actionLabel: 'Ver projetos',
      targetSection: 'scientific-projects',
    };
  } else if (!hasRouteInNotebook && steps.length > 0) {
    action = {
      title: 'Salve sua rota de estudo',
      description: 'Guarde a sequência sugerida para retomar depois.',
      actionLabel: 'Salvar rota no caderno',
      targetSection: 'scientific-route',
    };
  } else if (steps.length >= 2) {
    const c0 = steps[0];
    const c1 = steps[1];
    action = {
      title: 'Seu próximo passo',
      description: `Estudar ${c0.toLowerCase()} e ${c1.toLowerCase()} antes de avançar na rota.`,
      actionLabel: 'Ver trilha',
      targetSection: 'scientific-study-path',
    };
  } else if (routeSummary.conceitos?.length) {
    const c = routeSummary.conceitos[0];
    action = {
      title: 'Estude os fundamentos',
      description: `Foque em: ${c}.`,
      actionLabel: 'Ver trilha',
      targetSection: 'scientific-study-path',
    };
  } else if (feedItems.length > 0) {
    const top = feedItems[0];
    const labels = (top.matchedInterests || [])
      .filter((id) => interests.includes(id))
      .map(interestLabelById);
    action = {
      title: 'Leia uma fonte do feed',
      description: top.titulo
        ? `"${top.titulo.slice(0, 60)}${top.titulo.length > 60 ? '…' : ''}"`
        : 'Há itens relevantes para seus interesses.',
      actionLabel: 'Abrir feed',
      targetSection: 'scientific-feed',
    };
    if (labels.length) {
      action.description += ` (${labels.join(', ')})`;
    }
  } else if (projectIdeas.some((i) => i.level === 'intermediario')) {
    action = {
      title: 'Escolha um projeto intermediário',
      description: 'Combine teoria e prática com um projeto de nível intermediário.',
      actionLabel: 'Ver projetos',
      targetSection: 'scientific-projects',
    };
  }

  logScientificWorkspace('next_action_generated', {
    title: action.title,
    target: action.targetSection,
  });

  return action;
}
