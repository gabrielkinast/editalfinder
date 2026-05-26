/**
 * Seleção equilibrada para foco Misto (Fase 2L-B).
 * @param {Array<object>} rankedItems
 * @param {number} plannedMinutes
 */
export function buildMixedStudySessionRecommendation(rankedItems = [], plannedMinutes = 30) {
  const quotas = { theory: 2, powerIdea: 1, book: 1 };

  const picked = [];
  const used = new Set();

  for (const [kind, n] of Object.entries(quotas)) {
    let count = 0;
    for (const item of rankedItems) {
      if (count >= n) break;
      if (item.kind !== kind || used.has(item.progressKey)) continue;
      used.add(item.progressKey);
      picked.push(item.progressKey);
      count += 1;
    }
  }

  for (const item of rankedItems) {
    if (used.has(item.progressKey)) continue;
    if (item.kind === 'project' || item.kind === 'professorQuestion') {
      used.add(item.progressKey);
      picked.push(item.progressKey);
      break;
    }
  }

  if (picked.length < 3) {
    for (const item of rankedItems) {
      if (used.has(item.progressKey)) continue;
      used.add(item.progressKey);
      picked.push(item.progressKey);
      if (picked.length >= 5) break;
    }
  }

  return picked;
}
