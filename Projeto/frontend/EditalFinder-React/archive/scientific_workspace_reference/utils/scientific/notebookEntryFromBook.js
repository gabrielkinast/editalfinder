import { cleanScientificTitle } from './cleanScientificTitle';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';
import { withStudyProgressOnNotebookEntry } from './buildStudyProgressSummary';

/**
 * @param {object} book — { title, author, level, area, why, useFor }
 */
export function notebookEntryFromBook(book) {
  const studyProgressStatus = book?.studyProgressStatus;
  const title = cleanScientificTitle(`${book.author} — ${book.title}`) || 'Livro';
  const draft = {
    contentCategory: 'livro',
    tipo: 'livro',
    titulo: title,
    interesses: book.area ? [book.area] : [],
  };
  const stableKey = getScientificNotebookEntryKey(draft);

  return withStudyProgressOnNotebookEntry(
    sanitizeScientificNotebookEntry({
      id: `book-${stableKey.replace(/\|/g, '_').slice(0, 80)}`,
      contentCategory: 'livro',
      notebookGroup: 'livros',
      tipo: 'livro',
      titulo: title,
      title,
      author: book.author,
      bookLevel: book.level,
      fonte: 'Catálogo de livros',
      resumo: book.why || '',
      useFor: book.useFor || '',
      interesses: book.area ? [book.area] : [],
      notes: book.useFor ? `Para: ${book.useFor}` : undefined,
      savedAt: new Date().toISOString(),
    }),
    studyProgressStatus,
  );
}
