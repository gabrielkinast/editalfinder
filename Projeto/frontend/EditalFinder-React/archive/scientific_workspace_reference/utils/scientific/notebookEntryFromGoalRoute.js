import { cleanScientificTitle } from './cleanScientificTitle';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';

/**
 * @param {object} route — rota por objetivo
 * @param {string[]} activeInterests
 */
export function notebookEntryFromGoalRoute(route, activeInterests = []) {
  const titulo = cleanScientificTitle(`Rota — ${route.title}`) || 'Rota por objetivo';
  const steps = route.steps || [];

  const draft = {
    tipo: 'rota_estudo',
    titulo,
    interesses: activeInterests,
  };
  const stableKey = getScientificNotebookEntryKey(draft);

  return sanitizeScientificNotebookEntry({
    id: `goal-route-${stableKey.replace(/\|/g, '_').slice(0, 72)}`,
    contentCategory: 'estudo',
    notebookGroup: 'rotas',
    tipo: 'rota_estudo',
    titulo,
    title: titulo,
    fonte: 'Rota por objetivo',
    resumo: route.description || '',
    interesses: [...activeInterests],
    conceitos: steps,
    projetos: route.suggestedProjects || [],
    routeSteps: steps,
    notes: [
      route.description,
      steps.length ? steps.map((s, i) => `${i + 1}. ${s}`).join('\n') : '',
      route.suggestedBooks?.length ? `Livros:\n${route.suggestedBooks.join('\n')}` : '',
    ]
      .filter(Boolean)
      .join('\n\n'),
    savedAt: new Date().toISOString(),
  });
}
