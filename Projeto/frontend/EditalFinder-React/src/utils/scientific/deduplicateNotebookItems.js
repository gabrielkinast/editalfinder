import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Remove duplicatas mantendo o item mais antigo (savedAt) e mesclando campos úteis.
 * @param {unknown} items
 * @returns {{ items: Array<object>, removed: number }}
 */
export function deduplicateNotebookItems(items) {
  if (!Array.isArray(items)) {
    return { items: [], removed: 0 };
  }

  const byKey = new Map();

  for (const row of items) {
    if (!row || typeof row !== 'object') continue;

    try {
      const key = getScientificNotebookEntryKey(row);
      if (!key) continue;

      const existing = byKey.get(key);

      if (!existing) {
        byKey.set(key, { ...row });
        continue;
      }

      const merged = {
        ...existing,
        ...row,
        id: existing.id,
        savedAt: existing.savedAt,
        updatedAt: new Date().toISOString(),
        notes: row.notes?.trim?.() ? row.notes : existing.notes,
        resumo: row.resumo?.trim?.() ? row.resumo : existing.resumo,
        interesses: Array.isArray(row.interesses) && row.interesses.length
          ? row.interesses
          : existing.interesses,
      };
      byKey.set(key, merged);
    } catch (err) {
      if (import.meta.env.DEV) {
        logScientificWorkspace('notebook_item_normalize_failed', { message: err?.message });
      }
    }
  }

  const deduped = [...byKey.values()].sort(
    (a, b) => new Date(b.savedAt || 0).getTime() - new Date(a.savedAt || 0).getTime(),
  );

  return {
    items: deduped,
    removed: Math.max(0, items.length - deduped.length),
  };
}
