/** Converte texto JSONB/array/string em lista de strings. */
export function coerceStringArray(val) {
  if (val == null) return [];
  if (typeof val === 'object' && !Array.isArray(val)) {
    try {
      const flat = Object.values(val).flat(Infinity);
      return flat.map((x) => String(x).trim()).filter(Boolean);
    } catch {
      return [];
    }
  }
  if (Array.isArray(val)) return val.map((x) => String(x).trim()).filter(Boolean);
  if (typeof val === 'string') {
    const t = val.trim();
    if (t.startsWith('[')) {
      try {
        const arr = JSON.parse(t);
        if (Array.isArray(arr)) return arr.map((x) => String(x).trim()).filter(Boolean);
      } catch {
        /* segue como string */
      }
    }
    return t
      .split(/[,;|]/)
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return [String(val)].filter(Boolean);
}
