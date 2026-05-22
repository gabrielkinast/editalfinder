import { deduplicateNotebookItems } from './deduplicateNotebookItems';
import {
  loadScientificStudyProgress,
  saveScientificStudyProgress,
} from './scientificStudyProgressStorage';
import { loadStudySessions, saveStudySessions } from './scientificStudySessionStorage';
import { loadScientificXp, saveScientificXp } from './scientificXpStorage';
import { loadScientificMasteryChecks, saveScientificMasteryChecks } from './scientificMasteryStorage';
import {
  loadScientificBookProgress,
  saveScientificBookProgress,
  BOOK_READ_STATUSES,
} from './scientificBookProgressStorage';
import { STUDY_PROGRESS_STATUSES } from './scientificStudyProgressConstants';
import { logScientificWorkspace } from './scientificWorkspaceLog';

const VALID_BOOK = new Set(BOOK_READ_STATUSES.map((s) => s.id));

function saveNotebookItems(items) {
  try {
    localStorage.setItem(
      'scientific_workspace_notebook',
      JSON.stringify({ items: items.slice(0, 200), updatedAt: new Date().toISOString() }),
    );
  } catch {
    /* quota */
  }
}

function parseNotebookRawForRepair() {
  try {
    const raw = localStorage.getItem('scientific_workspace_notebook');
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed;
    if (parsed?.items && Array.isArray(parsed.items)) return parsed.items;
    return [];
  } catch {
    return [];
  }
}

/**
 * Reparos seguros no localStorage (Fase 2M). Nunca apaga tudo.
 * @param {object} [options]
 * @returns {{ actions: string[], reloadRecommended: boolean }}
 */
export function repairScientificWorkspaceState(options = {}) {
  const actions = [];
  let reloadRecommended = false;

  const rawNb = parseNotebookRawForRepair();
  const normalizedNb = rawNb.filter((r) => r && typeof r === 'object');
  const { items: dedupedNb, removed: nbRemoved } = deduplicateNotebookItems(normalizedNb);
  if (nbRemoved > 0) {
    saveNotebookItems(dedupedNb);
    actions.push(`Caderno: ${nbRemoved} duplicata(s) removida(s)`);
    reloadRecommended = true;
  }

  const progress = loadScientificStudyProgress();
  const cleanedProgress = {};
  let progressRemoved = 0;
  for (const [key, val] of Object.entries(progress)) {
    if (!key || typeof key !== 'string') {
      progressRemoved += 1;
      continue;
    }
    if (!val || typeof val !== 'object') {
      progressRemoved += 1;
      continue;
    }
    const status = STUDY_PROGRESS_STATUSES.includes(val.status) ? val.status : null;
    if (!status) {
      progressRemoved += 1;
      continue;
    }
    cleanedProgress[key] = {
      status,
      updatedAt: typeof val.updatedAt === 'string' ? val.updatedAt : new Date().toISOString(),
    };
  }
  if (progressRemoved > 0) {
    saveScientificStudyProgress(cleanedProgress);
    actions.push(`Progresso: ${progressRemoved} entrada(s) inválida(s) removida(s)`);
    reloadRecommended = true;
  }

  const { sessions } = loadStudySessions();
  const fixedSessions = [];
  let sessionsDropped = 0;
  for (const s of sessions) {
    if (!s || typeof s !== 'object' || !s.id) {
      sessionsDropped += 1;
      continue;
    }
    fixedSessions.push({
      ...s,
      selectedItems: Array.isArray(s.selectedItems) ? s.selectedItems : [],
      reflection:
        s.reflection && typeof s.reflection === 'object'
          ? s.reflection
          : {
              learned: '',
              understood: '',
              confused: '',
              nextAction: '',
              professorQuestion: '',
            },
      durationMinutes: Number(s.durationMinutes) || 0,
      xpAwarded: Number(s.xpAwarded) || 0,
    });
  }
  if (sessionsDropped > 0 || fixedSessions.length !== sessions.length) {
    saveStudySessions({ sessions: fixedSessions });
    actions.push(
      sessionsDropped > 0
        ? `Sessões: ${sessionsDropped} registro(s) corrompido(s) removido(s)`
        : 'Sessões: estrutura normalizada',
    );
    reloadRecommended = true;
  }

  const xp = loadScientificXp();
  const events = Array.isArray(xp.events) ? xp.events.filter((e) => e && typeof e === 'object') : [];
  const awardedKeys =
    xp.awardedKeys && typeof xp.awardedKeys === 'object' && !Array.isArray(xp.awardedKeys)
      ? xp.awardedKeys
      : {};
  if (events.length !== (xp.events || []).length) {
    saveScientificXp({
      ...xp,
      events,
      awardedKeys,
      byArea: xp.byArea || {},
      byKind: xp.byKind || {},
    });
    actions.push('XP: eventos inválidos removidos');
    reloadRecommended = true;
  }

  const mastery = loadScientificMasteryChecks();
  const cleanedMastery = {};
  let masteryRemoved = 0;
  for (const [key, record] of Object.entries(mastery)) {
    if (!record?.progressKey) {
      masteryRemoved += 1;
      continue;
    }
    cleanedMastery[record.progressKey] = record;
  }
  if (masteryRemoved > 0) {
    saveScientificMasteryChecks(cleanedMastery);
    actions.push(`Domínio: ${masteryRemoved} registro(s) sem progressKey removido(s)`);
    reloadRecommended = true;
  }

  const books = loadScientificBookProgress();
  const cleanedBooks = {};
  let booksFixed = 0;
  for (const [bk, entry] of Object.entries(books)) {
    if (!entry || typeof entry !== 'object') {
      booksFixed += 1;
      continue;
    }
    const status = entry.status && VALID_BOOK.has(entry.status) ? entry.status : 'quero_ler';
    let pct = entry.progressPercent;
    if (pct != null) {
      pct = Math.min(100, Math.max(0, Number(pct) || 0));
    }
    cleanedBooks[bk] = { ...entry, status, progressPercent: pct };
    if (status !== entry.status || pct !== entry.progressPercent) booksFixed += 1;
  }
  if (booksFixed > 0) {
    saveScientificBookProgress(cleanedBooks);
    actions.push(`Livros: ${booksFixed} entrada(s) corrigida(s)`);
    reloadRecommended = true;
  }

  if (actions.length === 0) {
    actions.push('Nenhuma correção necessária');
  }

  logScientificWorkspace('workspace_state_repaired', {
    actionCount: actions.length,
    reloadRecommended,
  });

  if (options.reload && reloadRecommended && typeof window !== 'undefined') {
    window.location.reload();
  }

  return { actions, reloadRecommended };
}
