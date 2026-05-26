import {
  getScientificNotebookEntryKey,
  findNotebookByEntryKey,
} from './getScientificNotebookEntryKey';

/** @deprecated Use getScientificNotebookEntryKey */
export function notebookSaveKey(entry) {
  return getScientificNotebookEntryKey(entry);
}

export function findNotebookDuplicate(items, entry) {
  return findNotebookByEntryKey(items, entry);
}

export function notebookEntriesEquivalent(a, b) {
  return getScientificNotebookEntryKey(a) === getScientificNotebookEntryKey(b);
}
