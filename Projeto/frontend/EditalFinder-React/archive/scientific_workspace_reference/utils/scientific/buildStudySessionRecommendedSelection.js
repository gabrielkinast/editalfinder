import { buildMixedStudySessionRecommendation } from './buildMixedStudySessionRecommendation';

const STATUS_PRIO = {
  estudando: 0,
  a_estudar: 1,
  none: 2,
  dominado: 4,
  ignorar_agora: 5,
};

function statusScore(item) {
  return STATUS_PRIO[item.status] ?? 3;
}

function pickFromPool(pool, predicate, max, sortFn) {
  const list = pool.filter(predicate).sort(sortFn || ((a, b) => statusScore(a) - statusScore(b)));
  const keys = [];
  for (const item of list) {
    if (keys.length >= max) break;
    keys.push(item.progressKey);
  }
  return keys;
}

function theorySegmentRotation(items, max) {
  const segments = ['foundations', 'intermediate', 'advanced', 'researchlevel'];
  const keys = [];
  const used = new Set();
  for (const seg of segments) {
    if (keys.length >= max) break;
    const pick = items.find(
      (i) =>
        i.kind === 'theory' &&
        !used.has(i.progressKey) &&
        String(i.segment || '').toLowerCase().includes(seg.replace('level', '')),
    );
    if (pick) {
      used.add(pick.progressKey);
      keys.push(pick.progressKey);
    }
  }
  for (const item of items) {
    if (keys.length >= max) break;
    if (item.kind === 'theory' && !used.has(item.progressKey)) {
      used.add(item.progressKey);
      keys.push(item.progressKey);
    }
  }
  return keys;
}

/**
 * Seleção recomendada por foco (Fase 2L-C) — quantidades moderadas.
 * @param {Array<object>} rankedItems
 * @param {object} opts
 */
export function buildStudySessionRecommendedSelection(rankedItems = [], opts = {}) {
  const { focus = 'theory', plannedMinutes = 30 } = opts;
  const pool = rankedItems;

  if (focus === 'mixed') {
    return buildMixedStudySessionRecommendation(pool, plannedMinutes);
  }

  if (focus === 'theory') {
    const theoryItems = pool
      .filter((i) => i.kind === 'theory')
      .sort((a, b) => statusScore(a) - statusScore(b));
    return theorySegmentRotation(theoryItems, 5).slice(0, 6);
  }

  if (focus === 'powerIdea') {
    return pickFromPool(pool, (i) => i.kind === 'powerIdea', 5);
  }

  if (focus === 'book') {
    const books = pool
      .filter((i) => i.kind === 'book')
      .sort((a, b) => {
        const aLendo = a.metadata?.bookProgressPercent != null ? -1 : 0;
        const bLendo = b.metadata?.bookProgressPercent != null ? -1 : 0;
        if (aLendo !== bLendo) return aLendo - bLendo;
        return statusScore(a) - statusScore(b);
      });
    return books.slice(0, 2).map((i) => i.progressKey);
  }

  if (focus === 'project') {
    return pickFromPool(pool, (i) => i.kind === 'project', 3);
  }

  if (focus === 'professorQuestion') {
    return pickFromPool(pool, (i) => i.kind === 'professorQuestion', 5);
  }

  if (focus === 'review') {
    const reviewPool = pool
      .filter((i) => {
        if (i.status === 'estudando') return true;
        if (i.status === 'dominado') return true;
        if (i.kind === 'book' && i.subtitle?.includes('Lendo')) return true;
        return false;
      })
      .sort((a, b) => statusScore(a) - statusScore(b));
    return reviewPool.slice(0, 8).map((i) => i.progressKey);
  }

  return pool.slice(0, 6).map((i) => i.progressKey);
}
