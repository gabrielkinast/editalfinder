import { buildStudySessionItemPool } from './buildStudySessionItemPool';
import { rankStudySessionItems } from './rankStudySessionItems';
import { logScientificWorkspace } from './scientificWorkspaceLog';
import { BOOK_READ_STATUSES } from './scientificBookProgressStorage';

const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

function reviewReason(item, progressState, bookProgress) {
  const st = item.status;
  const updatedAt = progressState[item.progressKey]?.updatedAt;
  const age = updatedAt ? Date.now() - new Date(updatedAt).getTime() : 0;
  const bp = bookProgress[item.progressKey];

  if (st === 'estudando') return { reason: 'Em estudo', group: 'hoje', score: 1 };
  if (bp?.status === 'lendo') {
    const stLabel = BOOK_READ_STATUSES.find((s) => s.id === bp.status)?.label || 'Lendo';
    return {
      reason: `${stLabel}${bp.progressPercent != null ? ` ${bp.progressPercent}%` : ''}`,
      group: 'livros',
      score: 0,
    };
  }
  if (item.kind === 'powerIdea' && st !== 'dominado' && st !== 'ignorar_agora') {
    return { reason: 'Ideia poderosa pendente', group: 'ideias', score: 3 };
  }
  if (st === 'dominado' && age >= SEVEN_DAYS_MS) {
    return { reason: 'Dominado há mais de 7 dias', group: 'dominados', score: 2 };
  }
  if (item.kind === 'project' && (st === 'estudando' || st === 'a_estudar')) {
    return { reason: 'Projeto em andamento', group: 'hoje', score: 4 };
  }
  if (item.kind === 'professorQuestion' && item.metadata?.inNotebook) {
    return { reason: 'Pergunta salva', group: 'perguntas', score: 5 };
  }
  if (item.kind === 'goalRouteStep' && st !== 'dominado' && st !== 'ignorar_agora') {
    return { reason: 'Passo da rota', group: 'hoje', score: 6 };
  }
  return null;
}

const GROUP_LABELS = {
  hoje: 'Para revisar hoje',
  livros: 'Livros em andamento',
  ideias: 'Ideias poderosas pendentes',
  dominados: 'Dominados antigos',
  perguntas: 'Perguntas para professor',
};

/**
 * Revisão ativa expandida (Fase 2L-B).
 * @param {object} params
 */
export function buildActiveReviewItems(params = {}) {
  const {
    studyBlocks = [],
    studyProgress: progressState = {},
    bookProgress = {},
    notebookItems = [],
    goalRoutes = [],
    activeInterests = [],
    limit = 8,
  } = params;

  const pool = buildStudySessionItemPool({
    studyBlocks,
    activeInterests,
    goalRoutes,
    progressState,
    bookProgress,
    notebookItems,
  });

  const candidates = [];
  const byReason = {};

  for (const item of pool) {
    const meta = reviewReason(item, progressState, bookProgress);
    if (!meta) continue;
    const row = {
      progressKey: item.progressKey,
      kind: item.kind,
      label: item.title,
      canonicalKey: item.canonicalKey,
      blockLabel: item.areaLabel,
      status: item.status,
      reason: meta.reason,
      reviewGroup: meta.group,
      score: meta.score,
      subtitle: item.subtitle,
      level: item.level,
      source: item.source,
    };
    candidates.push(row);
    byReason[meta.reason] = (byReason[meta.reason] || 0) + 1;
  }

  candidates.sort((a, b) => a.score - b.score);

  const seen = new Set();
  const out = [];
  for (const c of candidates) {
    if (seen.has(c.progressKey)) continue;
    seen.add(c.progressKey);
    out.push(c);
    if (out.length >= limit) break;
  }

  logScientificWorkspace('active_review_pool_built', {
    total: out.length,
    poolSize: pool.length,
    byReason,
  });

  return out;
}

/**
 * Agrupa itens de revisão para exibição no card.
 * @param {Array<object>} items
 */
export function groupActiveReviewItems(items = []) {
  const groups = {};
  for (const item of items) {
    const g = item.reviewGroup || 'hoje';
    if (!groups[g]) groups[g] = { id: g, label: GROUP_LABELS[g] || g, items: [] };
    groups[g].items.push(item);
  }
  return Object.values(groups);
}
