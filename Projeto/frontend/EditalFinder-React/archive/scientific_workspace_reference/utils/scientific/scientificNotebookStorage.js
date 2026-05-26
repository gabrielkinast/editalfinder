import { logScientificWorkspace } from './scientificWorkspaceLog';
import { normalizeProjectLevel, levelLabel } from './scientificProjectLevels';
import { getNotebookDisplayGroup } from './scientificNotebookGroups';
import { cleanScientificTitle } from './cleanScientificTitle';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';
import { findNotebookByEntryKey, getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { deduplicateNotebookItems } from './deduplicateNotebookItems';
import { safeJsonParse } from './safeJsonParse';

const STORAGE_KEY = 'scientific_workspace_notebook';

function isValidRawNotebookItem(raw) {
  return raw != null && typeof raw === 'object' && !Array.isArray(raw);
}

function parseNotebookRaw() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];

    const parsed = safeJsonParse(raw, null, { context: 'notebook' });
    if (parsed == null) {
      logScientificWorkspace('notebook_load_invalid_shape', { reason: 'invalid_json' });
      return [];
    }

    let items;
    if (Array.isArray(parsed)) {
      items = parsed;
    } else if (typeof parsed === 'object' && Array.isArray(parsed.items)) {
      items = parsed.items;
    } else {
      logScientificWorkspace('notebook_load_invalid_shape', { reason: 'not_array' });
      return [];
    }

    return items.filter(isValidRawNotebookItem);
  } catch {
    logScientificWorkspace('notebook_load_invalid_shape', { reason: 'exception' });
    return [];
  }
}

/** @param {object} entry */
function normalizeNotebookRow(entry) {
  const id = entry.id || `nb-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const level = entry.level ? normalizeProjectLevel(entry.level) : null;
  const titulo = cleanScientificTitle(entry.titulo || entry.title, { logContext: 'notebook_load' }) || 'Sem título';
  const tipo = String(entry.tipo || entry.type || 'item').trim() || 'item';

  const row = {
    id,
    contentCategory: entry.contentCategory || inferContentCategory(entry),
    tipo,
    categoria: entry.categoria,
    titulo,
    title: titulo,
    fonte: entry.fonte || '',
    link: entry.link || '',
    resumo: entry.resumo || entry.why || '',
    interesses: Array.isArray(entry.interesses) ? entry.interesses.filter(Boolean) : [],
    savedAt: entry.savedAt || new Date().toISOString(),
    updatedAt: entry.updatedAt || entry.savedAt || new Date().toISOString(),
    notes: entry.notes || '',
    feedId: entry.feedId ?? null,
    level,
    levelLabel: level ? levelLabel(level) : entry.levelLabel || null,
    type: entry.type || tipo,
    disciplines: Array.isArray(entry.disciplines) ? entry.disciplines : [],
    tools: Array.isArray(entry.tools) ? entry.tools : [],
    expectedOutput: entry.expectedOutput || '',
    nextSteps: Array.isArray(entry.nextSteps) ? entry.nextSteps : [],
    difficulty: entry.difficulty || null,
    conceitos: Array.isArray(entry.conceitos) ? entry.conceitos : [],
    projetos: Array.isArray(entry.projetos) ? entry.projetos : [],
    perguntas: Array.isArray(entry.perguntas) ? entry.perguntas : [],
    routeSteps: Array.isArray(entry.routeSteps) ? entry.routeSteps : [],
    notebookGroup: entry.notebookGroup || null,
    entryKey: getScientificNotebookEntryKey({ ...entry, titulo, tipo, level }),
  };
  row.notebookGroup = row.notebookGroup || getNotebookDisplayGroup(row);
  return row;
}

function inferContentCategory(entry) {
  const t = String(entry.tipo || entry.type || '').toLowerCase();
  if (t === 'pergunta_professor' || entry.categoria === 'pergunta') return 'pergunta';
  if (t === 'rota_estudo' || t.includes('rota de estudo')) return 'estudo';
  if (t.includes('ideia') || entry.level || entry.expectedOutput) return 'projeto';
  if (t.includes('estudo') || t.includes('trilha')) return 'estudo';
  if (entry.feedId) return 'feed';
  return 'feed';
}

function saveNotebook(items) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ items: items.slice(0, 200), updatedAt: new Date().toISOString() }),
    );
  } catch {
    /* quota */
  }
}

function processRawNotebook(rawItems) {
  const normalized = [];

  if (!Array.isArray(rawItems)) {
    return { items: [], removed: 0, before: 0 };
  }

  for (const raw of rawItems) {
    if (!isValidRawNotebookItem(raw)) continue;
    try {
      const sanitized = sanitizeScientificNotebookEntry(raw);
      normalized.push(normalizeNotebookRow(sanitized));
    } catch (err) {
      if (import.meta.env.DEV) {
        logScientificWorkspace('notebook_item_normalize_failed', { message: err?.message });
      }
    }
  }

  const before = normalized.length;
  const { items, removed } = deduplicateNotebookItems(normalized);

  return { items, removed, before };
}

/**
 * Carrega caderno com fallback seguro — nunca lança.
 * @returns {Array<object>}
 */
export function loadScientificNotebook() {
  try {
    const rawItems = parseNotebookRaw();
    const { items, removed, before } = processRawNotebook(rawItems);

    if (removed > 0) {
      saveNotebook(items);
      logScientificWorkspace('notebook_deduplicated_on_load', { before, after: items.length });
    } else if (items.length !== rawItems.length) {
      saveNotebook(items);
      logScientificWorkspace('notebook_sanitized_on_load', { count: items.length });
    }

    return items;
  } catch (err) {
    if (import.meta.env.DEV) {
      logScientificWorkspace('notebook_load_invalid_shape', { message: err?.message });
    }
    return [];
  }
}

/**
 * @param {object} entry
 * @returns {{ row: object, status: 'saved'|'updated'|'unchanged' }}
 */
export function addScientificNotebookEntry(entry) {
  try {
    const key = getScientificNotebookEntryKey(entry);
    logScientificWorkspace('notebook_save_attempt', { tipo: entry?.tipo, key });

    const rawItems = parseNotebookRaw();
    const { items } = processRawNotebook(rawItems);

    const sanitized = sanitizeScientificNotebookEntry(entry || {});
    const row = normalizeNotebookRow(sanitized);
    const duplicate = findNotebookByEntryKey(items, row);

    if (duplicate) {
      const merged = normalizeNotebookRow({
        ...duplicate,
        ...row,
        id: duplicate.id,
        savedAt: duplicate.savedAt,
        updatedAt: new Date().toISOString(),
        notes: row.notes?.trim?.() ? row.notes : duplicate.notes,
      });

      const sameContent =
        duplicate.titulo === merged.titulo &&
        (duplicate.resumo || '') === (merged.resumo || '') &&
        (duplicate.notes || '') === (merged.notes || '') &&
        (duplicate.link || '') === (merged.link || '') &&
        (duplicate.level || '') === (merged.level || '');

      if (sameContent) {
        logScientificWorkspace('notebook_save_duplicate', { id: duplicate.id });
        logScientificWorkspace('notebook_item_already_saved', { id: duplicate.id });
        return { row: duplicate, status: 'unchanged' };
      }

      const mergedKey = getScientificNotebookEntryKey(merged);
      const next = deduplicateNotebookItems([
        merged,
        ...items.filter((i) => getScientificNotebookEntryKey(i) !== mergedKey),
      ]).items;

      saveNotebook(next);
      logScientificWorkspace('notebook_save_updated', { id: merged.id });
      logScientificWorkspace('notebook_item_updated', { id: merged.id });
      logScientificWorkspace('notebook_save_success', { status: 'updated' });
      return { row: merged, status: 'updated' };
    }

    const next = deduplicateNotebookItems([row, ...items]).items;
    saveNotebook(next);
    logScientificWorkspace('notebook_item_saved', { id: row.id });
    logScientificWorkspace('notebook_save_success', { status: 'saved' });
    return { row, status: 'saved' };
  } catch (err) {
    if (import.meta.env.DEV) {
      logScientificWorkspace('notebook_save_failed', { message: err?.message });
    }
    return { row: { id: 'error', titulo: 'Sem título' }, status: 'unchanged' };
  }
}

export function removeScientificNotebookEntry(id) {
  try {
    const rawItems = parseNotebookRaw();
    const { items } = processRawNotebook(rawItems);
    const next = items.filter((i) => i.id !== id);
    saveNotebook(next);
    logScientificWorkspace('item_removed', { id });
    return next;
  } catch {
    return [];
  }
}

export function updateScientificNotebookNotes(id, notes) {
  try {
    const rawItems = parseNotebookRaw();
    const { items } = processRawNotebook(rawItems);
    const next = items.map((i) =>
      i.id === id ? { ...i, notes: notes ?? '', updatedAt: new Date().toISOString() } : i,
    );
    saveNotebook(next);
    return next;
  } catch {
    return [];
  }
}

export const NOTEBOOK_CONTENT_CATEGORIES = [
  { id: 'feed', label: 'Feed' },
  { id: 'projeto', label: 'Projeto' },
  { id: 'estudo', label: 'Estudo' },
];
