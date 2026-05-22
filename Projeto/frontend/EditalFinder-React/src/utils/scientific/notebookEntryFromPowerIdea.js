import { cleanScientificTitle } from './cleanScientificTitle';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';
import { withStudyProgressOnNotebookEntry } from './buildStudyProgressSummary';
import { POWER_IDEA_LEVEL_LABELS, POWER_IDEA_TYPE_LABELS } from './scientificPowerIdeasHelpers';

/**
 * @param {object} payload
 * @param {object} payload.idea
 * @param {string} payload.canonicalKey
 * @param {string} [payload.areaLabel]
 * @param {string} [payload.studyProgressStatus]
 */
export function notebookEntryFromPowerIdea({ idea, canonicalKey, areaLabel, studyProgressStatus }) {
  const titulo =
    cleanScientificTitle(`Ideia poderosa — ${idea.title}`) || 'Ideia poderosa';
  const typeLabel = POWER_IDEA_TYPE_LABELS[idea.type] || idea.type;
  const levelLabel = POWER_IDEA_LEVEL_LABELS[idea.level] || idea.level;

  const draft = {
    tipo: 'ideia_poderosa',
    titulo,
    interesses: canonicalKey ? [canonicalKey] : [],
    powerIdeaId: idea.id,
  };
  const stableKey = getScientificNotebookEntryKey(draft);

  return withStudyProgressOnNotebookEntry(
    sanitizeScientificNotebookEntry({
      id: `power-${stableKey.replace(/\|/g, '_').slice(0, 80)}`,
      contentCategory: 'ideia_poderosa',
      notebookGroup: 'ideias_poderosas',
      tipo: 'ideia_poderosa',
      titulo,
      title: titulo,
      powerIdeaId: idea.id,
      powerIdeaType: idea.type,
      powerIdeaLevel: idea.level,
      areaLabel: areaLabel || canonicalKey,
      fonte: 'Teoremas e ideias poderosas',
      resumo: idea.whyItMatters || '',
      interesses: canonicalKey ? [canonicalKey] : [],
      conceitos: idea.relatedTopics || [],
      projetos: idea.projectIdeas || [],
      perguntas: idea.professorQuestions || [],
      notes: [
        idea.shortExplanation,
        idea.useFor?.length ? `Usado para: ${idea.useFor.join(' · ')}` : '',
        idea.prerequisites?.length ? `Pré-requisitos: ${idea.prerequisites.join(' · ')}` : '',
        `${typeLabel} · ${levelLabel}`,
      ]
        .filter(Boolean)
        .join('\n\n'),
      savedAt: new Date().toISOString(),
    }),
    studyProgressStatus,
  );
}
