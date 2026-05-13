/** Normalização para busca: minúsculas, sem acentos para comparação. */
export function normalizeText(val) {
  if (val == null) return '';
  return String(val)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}
