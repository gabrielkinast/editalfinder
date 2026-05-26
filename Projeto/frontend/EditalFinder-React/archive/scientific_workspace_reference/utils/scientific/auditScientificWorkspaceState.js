import { SCIENTIFIC_INTERESTS } from './scientificInterestsConfig';
import { resolveCanonicalInterest } from './scientificInterestAliases';
import { SCIENTIFIC_DEEP_STUDY_CATALOG } from './scientificDeepStudyCatalog';
import { collectBlockProgressItems } from './buildStudyProgressSummary';
import { buildPowerIdeaProgressKey, buildRouteStepProgressKey } from './scientificStudyProgressKeys';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { STUDY_PROGRESS_STATUSES } from './scientificStudyProgressConstants';
import { BOOK_READ_STATUSES } from './scientificBookProgressStorage';
import { SCIENTIFIC_LOCAL_STORAGE_KEYS } from './clearScientificWorkspaceLocalCache';
import { logScientificWorkspace } from './scientificWorkspaceLog';

const VALID_BOOK_STATUSES = new Set(BOOK_READ_STATUSES.map((s) => s.id));

function ensureArray(v) {
  return Array.isArray(v) ? v : [];
}

function ensureObject(v) {
  return v && typeof v === 'object' && !Array.isArray(v) ? v : {};
}

function buildKnownProgressKeys(studyBlocks = [], goalRoutes = [], bookProgress = {}) {
  const keys = new Set();
  for (const block of studyBlocks) {
    for (const item of collectBlockProgressItems(block)) {
      if (item.progressKey) keys.add(item.progressKey);
    }
    const ideas = block.powerIdeas || block.deep?.powerIdeas || [];
    const ck = block.canonicalKey || block.interestId;
    for (const idea of ideas) {
      keys.add(buildPowerIdeaProgressKey(ck, idea));
    }
  }
  for (const route of goalRoutes) {
    for (const step of route.steps || []) {
      keys.add(buildRouteStepProgressKey(route.id, step));
    }
  }
  for (const bookKey of Object.keys(bookProgress || {})) {
    if (bookKey) keys.add(bookKey);
  }
  return keys;
}

function auditLocalStorageShape(warnings, errors) {
  for (const key of SCIENTIFIC_LOCAL_STORAGE_KEYS) {
    try {
      const raw = localStorage.getItem(key);
      if (raw == null) continue;
      JSON.parse(raw);
    } catch {
      errors.push(`localStorage corrompido: ${key}`);
    }
  }
}

/**
 * Auditoria local do Workspace Científico (Fase 2M).
 * @param {object} input
 */
export function auditScientificWorkspaceState(input = {}) {
  const warnings = [];
  const errors = [];

  const interests = ensureArray(input.interests);
  const studyBlocks = ensureArray(input.studyBlocks);
  const notebookItems = ensureArray(input.notebookItems);
  const studyProgress = ensureObject(input.studyProgress);
  const xpState = ensureObject(input.xpState);
  const masteryChecks = ensureObject(input.masteryChecks);
  const bookProgress = ensureObject(input.bookProgress);
  const studySessions = ensureArray(input.studySessions);
  const goalRoutes = ensureArray(input.goalRoutes);

  const validInterestIds = new Set(SCIENTIFIC_INTERESTS.map((i) => i.id));

  for (const id of interests) {
    if (typeof id !== 'string' || !id.trim()) {
      errors.push(`Interesse inválido: ${String(id)}`);
      continue;
    }
    if (!validInterestIds.has(id)) {
      warnings.push(`Interesse fora da lista UI: ${id}`);
    }
    const ck = resolveCanonicalInterest(id);
    if (ck && !SCIENTIFIC_DEEP_STUDY_CATALOG[ck]) {
      warnings.push(`canonicalKey sem catálogo profundo: ${ck} (de ${id})`);
    }
  }

  const blockKeys = new Map();
  for (const block of studyBlocks) {
    const ck = block.canonicalKey || block.interestId || '';
    if (!ck) warnings.push('studyBlock sem canonicalKey');
    if (blockKeys.has(ck)) {
      warnings.push(`studyBlock duplicado: ${ck}`);
    } else {
      blockKeys.set(ck, block);
    }
  }

  if (interests.length > 0 && studyBlocks.length === 0) {
    warnings.push('Há interesses ativos mas nenhuma trilha (studyBlock) gerada');
  }

  if (interests.length >= 2 && goalRoutes.length === 0) {
    warnings.push('Nenhuma rota por objetivo gerada apesar de interesses ativos');
  }

  const knownProgressKeys = buildKnownProgressKeys(studyBlocks, goalRoutes, bookProgress);
  let orphanProgress = 0;
  for (const key of Object.keys(studyProgress)) {
    if (!key || typeof key !== 'string') {
      errors.push('progressKey inválido no mapa de progresso');
      continue;
    }
    const entry = studyProgress[key];
    const status = entry?.status;
    if (status && !STUDY_PROGRESS_STATUSES.includes(status)) {
      warnings.push(`Status de progresso desconhecido em ${key}: ${status}`);
    }
    if (!knownProgressKeys.has(key)) orphanProgress += 1;
  }
  if (orphanProgress > 0) {
    warnings.push(`${orphanProgress} progressKey(s) sem item correspondente na trilha atual (órfãos)`);
  }

  const xpEvents = ensureArray(xpState.events);
  let xpMissingKey = 0;
  for (const ev of xpEvents) {
    if (!ev?.progressKey) xpMissingKey += 1;
  }
  if (xpMissingKey > 0) {
    warnings.push(`${xpMissingKey} evento(s) de XP sem progressKey`);
  }

  for (const [key, record] of Object.entries(masteryChecks)) {
    if (!record?.progressKey) {
      errors.push(`Verificação de domínio sem progressKey: ${key}`);
    }
  }

  const nbKeys = new Map();
  let notebookDupes = 0;
  for (const row of notebookItems) {
    try {
      const k = getScientificNotebookEntryKey(row);
      if (!k) continue;
      if (nbKeys.has(k)) notebookDupes += 1;
      else nbKeys.set(k, row.id);
    } catch {
      warnings.push('Item de caderno não normalizável');
    }
  }
  if (notebookDupes > 0) {
    warnings.push(`${notebookDupes} possível(is) duplicata(s) no caderno (mesma entryKey)`);
  }

  let sessionsNoItems = 0;
  let sessionsNoReflection = 0;
  for (const s of studySessions) {
    if (!s?.id) {
      warnings.push('Sessão sem id (corrompida)');
      continue;
    }
    const items = ensureArray(s.selectedItems);
    if (!items.length) sessionsNoItems += 1;
    if (!s.reflection || typeof s.reflection !== 'object') sessionsNoReflection += 1;
    for (const item of items) {
      if (!item.statusBefore) warnings.push(`Sessão ${s.id}: item sem statusBefore`);
      if (!item.statusAfter) warnings.push(`Sessão ${s.id}: item sem statusAfter`);
    }
  }
  if (sessionsNoItems > 0) {
    warnings.push(`${sessionsNoItems} sessão(ões) sem selectedItems`);
  }
  if (sessionsNoReflection > 0) {
    warnings.push(`${sessionsNoReflection} sessão(ões) sem objeto reflection`);
  }

  let invalidBooks = 0;
  for (const [bk, entry] of Object.entries(bookProgress)) {
    if (!entry || typeof entry !== 'object') {
      invalidBooks += 1;
      continue;
    }
    if (entry.status && !VALID_BOOK_STATUSES.has(entry.status)) {
      warnings.push(`Progresso de livro com status inválido: ${entry.status} (${bk})`);
    }
    const pct = entry.progressPercent;
    if (pct != null && (typeof pct !== 'number' || pct < 0 || pct > 100)) {
      warnings.push(`Progresso de livro fora de 0–100%: ${bk}`);
    }
  }
  if (invalidBooks > 0) {
    warnings.push(`${invalidBooks} entrada(s) de livro inválida(s)`);
  }

  auditLocalStorageShape(warnings, errors);

  const booksInProgressCount = Object.values(bookProgress).filter(
    (b) => b?.status === 'lendo' || b?.status === 'quero_ler',
  ).length;

  const stats = {
    interestsCount: interests.length,
    studyBlocksCount: studyBlocks.length,
    notebookCount: notebookItems.length,
    progressCount: Object.keys(studyProgress).length,
    xpEventsCount: xpEvents.length,
    sessionsCount: studySessions.length,
    booksInProgressCount,
    masteryCount: Object.keys(masteryChecks).length,
    totalXp: xpState.totalXp ?? 0,
    goalRoutesCount: goalRoutes.length,
  };

  const ok = errors.length === 0;

  const report = { ok, warnings, errors, stats };

  if (import.meta.env.DEV) {
    logScientificWorkspace('workspace_audit_completed', {
      ok,
      warningCount: warnings.length,
      errorCount: errors.length,
      stats,
    });
  }

  return report;
}
