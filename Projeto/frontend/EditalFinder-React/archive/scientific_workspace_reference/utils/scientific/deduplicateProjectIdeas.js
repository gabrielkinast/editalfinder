import { cleanScientificTitle } from './cleanScientificTitle';
import { normalizeProjectLevel } from './scientificProjectLevels';

const MAX_NOTEBOOK_CONTINUATIONS = 3;

/**
 * Remove cards duplicados (mesmo título limpo + nível + interesses).
 * Limita ideias "Continuação" vindas do caderno.
 * @param {Array<object>} ideas
 */
export function deduplicateProjectIdeas(ideas = []) {
  const seen = new Set();
  const out = [];
  let continuationCount = 0;

  for (const idea of ideas) {
    const title = cleanScientificTitle(idea.title || idea.titulo).toLowerCase();
    const level = normalizeProjectLevel(idea.level);
    const needs = [...(idea.needs || idea.interesses || [])].filter(Boolean).sort().join(',');
    const key = `${title}|${level}|${needs}`;

    if (idea.continuationFromNotebook || idea.fromNotebook) {
      if (continuationCount >= MAX_NOTEBOOK_CONTINUATIONS) continue;
      if (seen.has(key)) continue;
      continuationCount += 1;
    }

    if (seen.has(key)) continue;
    seen.add(key);
    out.push(idea);
  }

  return out;
}
