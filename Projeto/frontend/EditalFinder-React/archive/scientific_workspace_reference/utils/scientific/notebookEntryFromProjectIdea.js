import { cleanScientificTitle } from './cleanScientificTitle';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';

/**
 * Monta payload do caderno a partir de uma ideia de projeto.
 * @param {object} idea
 */
export function notebookEntryFromProjectIdea(idea) {
  const title = cleanScientificTitle(idea.title || idea.titulo) || 'Ideia de projeto';
  const notesParts = [
    idea.expectedOutput ? `Produto esperado: ${idea.expectedOutput}` : '',
    idea.prerequisites?.length ? `Pré-requisitos: ${idea.prerequisites.join('; ')}` : '',
    idea.theoryTopics?.length ? `Teoria: ${idea.theoryTopics.join('; ')}` : '',
    idea.nextSteps?.length
      ? `Próximos passos:\n${idea.nextSteps.map((s, i) => `${i + 1}. ${s}`).join('\n')}`
      : '',
  ].filter(Boolean);

  const draft = {
    contentCategory: 'projeto',
    tipo: idea.type || 'ideia de projeto',
    titulo: title,
    level: idea.level,
    interesses: idea.interesses || idea.needs || [],
  };
  const stableKey = getScientificNotebookEntryKey(draft);

  return sanitizeScientificNotebookEntry({
    id: `idea-${stableKey.replace(/\|/g, '_').slice(0, 80)}`,
    contentCategory: 'projeto',
    notebookGroup: 'projetos',
    tipo: idea.type || 'ideia de projeto',
    titulo: title,
    title,
    fonte: 'Workspace Científico',
    resumo: idea.why || idea.porque || '',
    interesses: idea.interesses || idea.needs || [],
    level: idea.level,
    type: idea.type,
    disciplines: idea.disciplines || idea.disciplinas || [],
    tools: idea.tools || idea.ferramentas || [],
    expectedOutput: idea.expectedOutput || '',
    nextSteps: idea.nextSteps || [],
    prerequisites: idea.prerequisites || [],
    theoryTopics: idea.theoryTopics || [],
    possibleDeliverables: idea.possibleDeliverables || [],
    professorQuestions: idea.professorQuestions || [],
    difficulty: idea.difficulty,
    notes: notesParts.length ? notesParts.join('\n\n') : undefined,
    savedAt: new Date().toISOString(),
  });
}
