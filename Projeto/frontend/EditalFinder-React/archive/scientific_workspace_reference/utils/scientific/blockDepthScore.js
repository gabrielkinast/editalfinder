/**
 * Pontua profundidade de um bloco de trilha (catálogo 2H).
 * @param {object} block
 */
export function blockDepthScore(block) {
  if (!block) return 0;
  let score = block.deep ? 80 : 0;
  const tc = block.theoryCounts || {};
  score += (tc.foundations || 0) + (tc.intermediate || 0) + (tc.advanced || 0) + (tc.researchLevel || 0);
  if (block.deep?.theory) {
    for (const layer of Object.values(block.deep.theory)) {
      score += (layer?.length || 0) * 2;
    }
  }
  score += (block.deep?.bookEntries?.length || block.books?.length || 0);
  const pt = block.deep?.projectTracks;
  if (pt) {
    for (const track of Object.values(pt)) {
      score += (track?.length || 0) * 3;
    }
  }
  score += (block.professorQuestions?.length || 0);
  return score;
}
