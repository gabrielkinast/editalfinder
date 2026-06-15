/**
 * Normaliza URL para abertura externa (http/https/mailto).
 * Retorna null se inválida ou placeholder.
 */
export function normalizeExternalUrl(raw) {
  if (raw == null) return null;
  let s = String(raw).trim();
  if (!s || s === '#' || s === '-' || s.toLowerCase() === 'null' || s.toLowerCase() === 'undefined') {
    return null;
  }

  if (/^javascript:/i.test(s)) return null;

  if (/^\/\//.test(s)) {
    s = `https:${s}`;
  } else if (!/^[a-z][a-z0-9+.-]*:/i.test(s)) {
    if (/^[\w.-]+\.[a-z]{2,}/i.test(s)) {
      s = `https://${s}`;
    } else {
      return null;
    }
  }

  try {
    const u = new URL(s);
    if (u.protocol !== 'http:' && u.protocol !== 'https:' && u.protocol !== 'mailto:') {
      return null;
    }
    return u.href;
  } catch {
    return null;
  }
}
