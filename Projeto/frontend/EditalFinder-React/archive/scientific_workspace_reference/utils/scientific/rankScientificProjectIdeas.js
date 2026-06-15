import { normalizeProjectLevel } from './scientificProjectLevels';

const LEVEL_ORDER = { basico: 1, intermediario: 2, avancado: 3, ic_tcc: 4, mestrado: 5 };

/**
 * Pontua aderência de uma ideia aos interesses ativos e ao caderno.
 */
export function scoreProjectIdea(idea, activeInterests = [], notebookItems = []) {
  const needs = idea.needs || idea.interesses || [];
  const active = activeInterests || [];
  const matchCount = needs.filter((n) => active.includes(n)).length;
  if (needs.length > 0 && matchCount < needs.length) return -1;

  let score = matchCount * 12;
  if (needs.length) score += needs.length * 2;

  const notebookBoost = (notebookItems || []).some((nb) => {
    const nbInterests = nb.interesses || [];
    return needs.some((n) => nbInterests.includes(n));
  });
  if (notebookBoost) score += 8;
  if (idea.fromNotebook) score += 15;

  return score;
}

/**
 * Ordena e limita ideias para exibição.
 * @param {Array} ideas
 * @param {object} options
 */
export function rankAndLimitProjectIdeas(
  ideas,
  activeInterests = [],
  notebookItems = [],
  options = {},
) {
  const limit = options.limit ?? 18;
  const levelFilter = options.levelFilter;
  const interestFilter = options.interestFilter;
  const searchQuery = (options.searchQuery || '').trim().toLowerCase();

  let list = [...ideas];

  if (levelFilter && levelFilter !== 'todos') {
    list = list.filter((i) => normalizeProjectLevel(i.level) === levelFilter);
  }

  if (interestFilter) {
    list = list.filter((i) => (i.needs || i.interesses || []).includes(interestFilter));
  }

  if (searchQuery) {
    list = list.filter((i) => {
      const blob = [
        i.title,
        i.why,
        i.type,
        ...(i.disciplines || []),
        ...(i.tools || []),
        ...(i.needs || []),
      ]
        .join(' ')
        .toLowerCase();
      return blob.includes(searchQuery);
    });
  }

  list = list
    .map((idea) => ({
      idea,
      score: scoreProjectIdea(idea, activeInterests, notebookItems),
    }))
    .filter((x) => x.score >= 0)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      const la = LEVEL_ORDER[a.idea.level] || 9;
      const lb = LEVEL_ORDER[b.idea.level] || 9;
      return la - lb;
    })
    .map((x) => ({ ...x.idea, relevanceScore: x.score }));

  return {
    items: list.slice(0, limit),
    totalMatched: list.length,
    truncated: list.length > limit,
  };
}

/**
 * Uma ideia destacada por nível (básico, intermediário, avançado/IC).
 */
export function pickProjectsByLevelTier(ideas, activeInterests = [], notebookItems = []) {
  const ranked = rankAndLimitProjectIdeas(ideas, activeInterests, notebookItems, {
    limit: 200,
  }).items;

  const pick = (level) =>
    ranked.find((i) => normalizeProjectLevel(i.level) === level) || null;

  const advanced =
    ranked.find((i) => {
      const l = normalizeProjectLevel(i.level);
      return l === 'avancado' || l === 'ic_tcc';
    }) || null;

  return {
    basico: pick('basico'),
    intermediario: pick('intermediario'),
    avancadoOuIc: advanced,
    mestrado: pick('mestrado'),
  };
}
