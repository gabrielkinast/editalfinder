/**
 * Busca em blocos de trilha profunda (Fase 2H-F).
 * @param {Array<object>} blocks
 * @param {string} query
 */
export function searchStudyPathBlocks(blocks, query) {
  const q = String(query || '').trim().toLowerCase();
  if (!q) {
    return {
      query: '',
      blocks,
      matchCount: 0,
      trailCount: blocks.length,
    };
  }

  function powerIdeaBlob(idea) {
    if (!idea) return '';
    return [
      idea.title,
      idea.type,
      idea.level,
      idea.whyItMatters,
      idea.shortExplanation,
      ...(idea.useFor || []),
      ...(idea.prerequisites || []),
      ...(idea.relatedTopics || []),
      ...(idea.projectIdeas || []),
      ...(idea.professorQuestions || []),
    ].join('\n');
  }

  function blob(block) {
    const deep = block.deep || {};
    const powerIdeas = block.powerIdeas || deep.powerIdeas || [];
    return [
      block.label,
      block.description,
      block.formationGoal,
      ...(block.matchedInterestLabels || []),
      ...Object.values(deep.prerequisites || {}).flat(),
      ...Object.values(deep.theory || {}).flat(),
      ...Object.values(deep.books || {}).flat(),
      ...Object.values(deep.projectTracks || {}).flat(),
      ...(deep.professorQuestions || block.professorQuestions || []),
      ...powerIdeas.map(powerIdeaBlob),
      ...(block.fundamentals || []),
      ...(block.intermediate || []),
      ...(block.books || []),
    ]
      .join('\n')
      .toLowerCase();
  }

  let matchCount = 0;
  const filtered = blocks.filter((block) => {
    const text = blob(block);
    if (!text.includes(q)) return false;
    const occurrences = text.split(q).length - 1;
    matchCount += Math.max(1, occurrences);
    return true;
  });

  return {
    query: q,
    blocks: filtered,
    matchCount,
    trailCount: filtered.length,
  };
}

/**
 * Destaca termo em texto (retorna array de partes para React).
 * @param {string} text
 * @param {string} query
 */
export function highlightTextParts(text, query) {
  const str = String(text || '');
  const q = String(query || '').trim().toLowerCase();
  if (!q || !str.toLowerCase().includes(q)) return [{ text: str, match: false }];

  const parts = [];
  let remaining = str;
  let lower = remaining.toLowerCase();
  while (lower.includes(q)) {
    const idx = lower.indexOf(q);
    if (idx > 0) parts.push({ text: remaining.slice(0, idx), match: false });
    parts.push({ text: remaining.slice(idx, idx + q.length), match: true });
    remaining = remaining.slice(idx + q.length);
    lower = remaining.toLowerCase();
  }
  if (remaining) parts.push({ text: remaining, match: false });
  return parts;
}
