import { cleanScientificTitle } from './cleanScientificTitle';
import { normalizeProjectLevel } from './scientificProjectLevels';

/** @param {unknown} entry */
function isNotebookEntryObject(entry) {
  return entry != null && typeof entry === 'object' && !Array.isArray(entry);
}

/** @param {object} entry */
export function normalizeNotebookTipo(entry) {
  if (!isNotebookEntryObject(entry)) return 'item';
  const t = String(entry.tipo || entry.type || entry.contentCategory || '').toLowerCase();
  if (t === 'rota_estudo' || t.includes('rota de estudo')) return 'rota_estudo';
  if (t === 'pergunta_professor' || entry.categoria === 'pergunta') return 'pergunta_professor';
  if (entry.feedId != null && entry.feedId !== '') return 'feed';
  if (entry.contentCategory === 'feed' && entry.feedId == null) return 'feed';
  if (entry.contentCategory === 'projeto' || entry.level || t.includes('ideia')) return 'projeto';
  if (entry.contentCategory === 'estudo') return 'estudo';
  if (entry.contentCategory === 'livro' || t === 'livro') return 'livro';
  if (entry.contentCategory === 'teoria' || t === 'teoria') return 'teoria';
  if (t === 'ideia_poderosa' || entry.contentCategory === 'ideia_poderosa') return 'ideia_poderosa';
  return t || 'item';
}

/**
 * Chave estável para deduplicação e estado "Já salvo".
 * @param {unknown} entry
 * @returns {string|null}
 */
export function getScientificNotebookEntryKey(entry) {
  try {
    if (!isNotebookEntryObject(entry)) return null;

    const tipo = normalizeNotebookTipo(entry);

    if (entry.feedId != null && entry.feedId !== '') {
      return `${tipo}|feed:${String(entry.feedId)}`;
    }

    if (tipo === 'ideia_poderosa' && entry.powerIdeaId) {
      const interesses = Array.isArray(entry.interesses) ? entry.interesses.filter(Boolean) : [];
      const primaryInterest = [...interesses].sort()[0] || '';
      return `${tipo}|${String(entry.powerIdeaId)}|${primaryInterest}`;
    }

    const titulo = cleanScientificTitle(entry.titulo || entry.title).toLowerCase();
    const link = String(entry.link || '')
      .trim()
      .toLowerCase()
      .replace(/\/+$/, '');
    const level = entry.level ? normalizeProjectLevel(entry.level) : '';
    const interesses = Array.isArray(entry.interesses) ? entry.interesses.filter(Boolean) : [];
    const primaryInterest = [...interesses].sort()[0] || '';

    return `${tipo}|${titulo}|${link}|${level}|${primaryInterest}`;
  } catch {
    return null;
  }
}

/**
 * @param {unknown} items
 * @param {unknown} entry
 */
export function findNotebookByEntryKey(items, entry) {
  if (!Array.isArray(items)) return null;
  const key = getScientificNotebookEntryKey(entry);
  if (!key) return null;
  return items.find((i) => getScientificNotebookEntryKey(i) === key) || null;
}
