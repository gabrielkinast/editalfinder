/**
 * Chaves estáveis para progresso local (Fase 2I).
 * Formato: canonicalKey::kind::segment::slug
 */

export function slugifyStudyProgressLabel(text) {
  return String(text || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);
}

/**
 * @param {string} canonicalKey
 * @param {'theory'|'book'|'project'|'question'|'route_step'|'powerIdea'} kind
 * @param {string} segment — ex. foundations, introductory, basic, routeId
 * @param {string} label — texto do tópico/livro/projeto
 */
export function buildStudyProgressKey(canonicalKey, kind, segment, label) {
  const base = canonicalKey || 'geral';
  const seg = segment || 'general';
  const slug = slugifyStudyProgressLabel(label) || 'item';
  return `${base}::${kind}::${seg}::${slug}`;
}

export function buildRouteStepProgressKey(routeId, stepLabel) {
  return buildStudyProgressKey(`goal::${routeId}`, 'route_step', 'step', stepLabel);
}

/**
 * @param {string} canonicalKey
 * @param {{ id: string, level?: string, title?: string }} idea
 */
export function buildPowerIdeaProgressKey(canonicalKey, idea) {
  return buildStudyProgressKey(canonicalKey, 'powerIdea', idea.level || 'general', idea.id || idea.title);
}
