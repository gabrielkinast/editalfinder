import { logScientificWorkspace } from './scientificWorkspaceLog';

/** Prefixos que podem ser empilhados por engano ao salvar/regerar ideias. */
const STRIP_PREFIXES = [
  /^Aprofundar:\s*/i,
  /^Projeto:\s*/i,
  /^Rota científica:\s*/i,
  /^Ideia:\s*/i,
];

const MAX_TITLE_LENGTH = 200;

/**
 * Remove prefixos duplicados, trim e limita tamanho sem alterar o núcleo do título.
 * @param {string|null|undefined} title
 * @param {{ maxLength?: number, logContext?: string }} [options]
 */
export function cleanScientificTitle(title, options = {}) {
  if (title == null) return '';
  let s = String(title).trim();
  if (!s) return '';

  const before = s;
  const maxLen = options.maxLength ?? MAX_TITLE_LENGTH;
  let guard = 0;

  while (guard < 24) {
    guard += 1;
    let changed = false;
    for (const re of STRIP_PREFIXES) {
      const next = s.replace(re, '').trim();
      if (next !== s) {
        s = next;
        changed = true;
      }
    }
    if (!changed) break;
  }

  if (s.length > maxLen) {
    s = s.slice(0, maxLen).trim();
  }

  if (options.logContext && before !== s && import.meta.env.DEV) {
    logScientificWorkspace('title_cleaned', {
      context: options.logContext,
      before: before.slice(0, 80),
      after: s.slice(0, 80),
    });
  }

  return s;
}

/**
 * Adiciona um único prefixo após limpar o título base.
 * @param {string} prefix — ex. "Aprofundar", "Rota científica"
 * @param {string} title
 */
export function withScientificPrefix(prefix, title) {
  const clean = cleanScientificTitle(title);
  const label = String(prefix || '').replace(/:\s*$/, '').trim();
  if (!label) return clean;
  if (!clean) return `${label}:`;
  return `${label}: ${clean}`;
}

/**
 * Título curto para UI (truncamento visual).
 */
/**
 * Truncamento por caracteres — evita cortes agressivos (ex.: "Apro").
 * @param {number} max — mínimo efetivo 48
 */
export function truncateDisplayTitle(title, max = 80) {
  const t = cleanScientificTitle(title);
  if (!t) return '';
  const limit = Math.max(48, max);
  if (t.length <= limit) return t;
  return `${t.slice(0, limit)}…`;
}

/**
 * Título final para renderização (cards, briefing, rota).
 * Nunca exibe prefixos empilhados; badge opcional para ideias do caderno.
 * @param {object|string} item — ideia, entrada do caderno ou string
 */
export function displayScientificTitle(item) {
  try {
    if (typeof item === 'string') {
      const title = cleanScientificTitle(item) || 'Sem título';
      return { title, titleFull: title, badge: null };
    }
    if (item == null || typeof item !== 'object') {
      return { title: 'Sem título', titleFull: 'Sem título', badge: null };
    }
    const raw = item.title ?? item.titulo ?? '';
    const title = cleanScientificTitle(raw) || 'Sem título';
    const badge =
      item.continuationFromNotebook || item.fromNotebook ? 'Continuação' : null;
    return { title, titleFull: title, badge };
  } catch {
    return { title: 'Sem título', titleFull: 'Sem título', badge: null };
  }
}
