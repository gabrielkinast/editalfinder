/**
 * Normaliza títulos vindos de coleta onde o servidor devolveu HTML de SPA/noscript
 * (ex.: "JavaScript is disabled") em vez do título real.
 */

const JUNK_TITLE_REGEXES = [
  /javascript\s+is\s+disabled/i,
  /please\s+enable\s+javascript/i,
  /you\s+(need\s+to|must)\s+enable\s+javascript/i,
  /this\s+(page|site|application)\s+requires\s+javascript/i,
  /enable\s+javascript\s+to\s+continue/i,
  /^noscript$/i,
  /^loading\.{0,3}$/i,
  /^just\s+a\s+moment/i, // páginas de desafio
  /^attention\s+required/i,
  /^access\s+denied$/i,
];

export function isJunkPortalTitle(text) {
  if (text == null || typeof text !== 'string') return true;
  const t = text.replace(/\s+/g, ' ').trim();
  if (t.length < 3) return true;
  return JUNK_TITLE_REGEXES.some((re) => re.test(t));
}

function firstSnippet(text, maxLen = 140) {
  if (!text || typeof text !== 'string') return null;
  const normalized = text.replace(/\s+/g, ' ').trim();
  if (normalized.length < 20) return null;
  if (isJunkPortalTitle(normalized)) return null;
  let chunk = normalized;
  const cut = chunk.search(/[.!?]\s/);
  if (cut > 30 && cut < 200) chunk = chunk.slice(0, cut);
  chunk = chunk.slice(0, maxLen).trim();
  if (normalized.length > maxLen) chunk += '…';
  if (chunk.length < 15) return null;
  return chunk;
}

function hostnameHint(link) {
  if (!link || typeof link !== 'string') return null;
  try {
    const u = new URL(link.trim());
    return u.hostname.replace(/^www\./i, '');
  } catch {
    return null;
  }
}

/**
 * @param {Object} o
 * @param {string} [o.titulo]
 * @param {string} [o.link]
 * @param {string} [o.descricao]
 * @param {string} [o.objetivo]
 * @param {string} [o.temas]
 * @param {string} [o.fonte_recurso]
 * @param {string} [o.resumo]
 */
export function getDisplayTitle(o = {}) {
  const raw = (o.titulo || '').replace(/\s+/g, ' ').trim();
  if (raw && !isJunkPortalTitle(raw)) return raw;

  const fromBody =
    firstSnippet(o.descricao) ||
    firstSnippet(o.objetivo) ||
    firstSnippet(o.resumo);
  if (fromBody) return fromBody;

  const temas = (o.temas || '').replace(/\s+/g, ' ').trim();
  if (temas.length >= 12 && !isJunkPortalTitle(temas)) {
    return temas.length > 140 ? `${temas.slice(0, 137)}…` : temas;
  }

  const host = hostnameHint(o.link);
  if (host) return `Chamada — ${host}`;

  const org = (o.fonte_recurso || '').trim();
  if (org) return `Edital — ${org}`;

  return 'Edital (título indisponível)';
}
