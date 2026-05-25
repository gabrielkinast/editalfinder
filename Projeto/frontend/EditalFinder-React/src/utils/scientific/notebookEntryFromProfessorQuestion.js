import { cleanScientificTitle } from './cleanScientificTitle';
import { withStudyProgressOnNotebookEntry } from './buildStudyProgressSummary';

/**
 * @param {{ interestId: string, label?: string, question: string, studyProgressStatus?: string }} q
 */
export function notebookEntryFromProfessorQuestion(q) {
  const titulo = cleanScientificTitle(q.question) || 'Pergunta para professor';
  const interesses = q.interestId ? [q.interestId] : [];

  return withStudyProgressOnNotebookEntry(
    {
      id: `pergunta-${q.interestId}-${Date.now()}`,
      contentCategory: 'pergunta',
      notebookGroup: 'perguntas',
      tipo: 'pergunta_professor',
      categoria: 'pergunta',
      titulo,
      title: titulo,
      fonte: 'Workspace Científico',
      link: '',
      resumo: q.label ? `Tópico: ${q.label}` : '',
      interesses,
      savedAt: new Date().toISOString(),
    },
    q.studyProgressStatus,
  );
}
