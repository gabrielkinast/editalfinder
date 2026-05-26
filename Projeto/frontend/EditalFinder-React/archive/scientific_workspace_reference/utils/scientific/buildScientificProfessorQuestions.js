import { SCIENTIFIC_STUDY_CATALOG } from './scientificStudyCatalog';
import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Perguntas heurísticas para levar ao professor/orientador.
 * @param {string[]} activeInterests
 */
export function buildScientificProfessorQuestions(activeInterests = []) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  const seen = new Set();
  const questions = [];

  for (const id of active) {
    const cat = SCIENTIFIC_STUDY_CATALOG[id];
    if (!cat?.professorQuestions) continue;
    for (const q of cat.professorQuestions) {
      if (seen.has(q)) continue;
      seen.add(q);
      questions.push({ interestId: id, label: cat.label, question: q });
    }
  }

  logScientificWorkspace('professor_questions_generated', {
    count: questions.length,
    interests: active.length,
  });

  return questions;
}
