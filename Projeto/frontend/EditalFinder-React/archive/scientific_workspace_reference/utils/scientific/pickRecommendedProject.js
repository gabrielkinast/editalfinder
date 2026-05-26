import { normalizeProjectLevel, levelLabel } from './scientificProjectLevels';
import { cleanScientificTitle } from './cleanScientificTitle';
import { logScientificWorkspace } from './scientificWorkspaceLog';

function weekKey() {
  const d = new Date();
  const start = new Date(d.getFullYear(), 0, 1);
  const week = Math.ceil(((d - start) / 86400000 + start.getDay() + 1) / 7);
  return `${d.getFullYear()}-W${week}`;
}

function scoreIdea(idea, activeInterests) {
  const needs = idea.needs || idea.interesses || [];
  const matchCount = needs.filter((n) => activeInterests.includes(n)).length;
  if (needs.length > 0 && matchCount < needs.length) return -1;

  let score = matchCount * 10 + (needs.length ? needs.length * 2 : 1);
  const level = normalizeProjectLevel(idea.level);

  if (activeInterests.includes('computacao_cientifica')) {
    if (level === 'intermediario' || level === 'avancado') score += 8;
  }
  if (activeInterests.includes('nuclear') || activeInterests.includes('materiais')) {
    if (needs.includes('nuclear') || needs.includes('materiais')) score += 6;
  }
  if (level === 'intermediario') score += 3;

  return score;
}

/**
 * Projeto recomendado da semana (heurístico, estável na semana).
 * @param {Array<object>} ideas — saída de buildScientificProjectIdeas
 * @param {string[]} activeInterests
 */
export function pickRecommendedProject(ideas = [], activeInterests = []) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  const candidates = (ideas || [])
    .map((idea) => ({ idea, score: scoreIdea(idea, active) }))
    .filter((x) => x.score >= 0)
    .sort((a, b) => b.score - a.score);

  if (!candidates.length) {
    return null;
  }

  const wk = weekKey();
  const idx = wk.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % candidates.length;
  const pick = candidates[idx].idea;

  const cleanTitle = cleanScientificTitle(pick.title || pick.titulo) || 'Projeto';
  const recommended = {
    ...pick,
    title: cleanTitle,
    titulo: cleanTitle,
    weekKey: wk,
    levelLabel: levelLabel(pick.level),
    matchWhy:
      pick.why ||
      `Combina seus interesses (${active.map((i) => i.replace(/_/g, ' ')).join(', ') || 'gerais'}).`,
  };

  logScientificWorkspace('recommended_project_generated', {
    id: pick.id,
    level: pick.level,
    week: wk,
  });

  return recommended;
}
