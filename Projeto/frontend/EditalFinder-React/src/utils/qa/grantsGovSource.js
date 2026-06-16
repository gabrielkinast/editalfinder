/**
 * Detecção de fonte Grants.gov em strings de exibição (E2E + QA).
 * Distinto de isGrantsGovUrl — aqui o valor é rótulo/fonte, não URL.
 */

export function isGrantsGovSource(value) {
  if (value == null || value === '') return false;
  const s = String(value).trim().toLowerCase();
  if (!s) return false;
  if (s.includes('grants.gov')) return true;
  if (/grants[_\s-]*gov/.test(s)) return true;
  if (s === 'grants' || s === 'grants_gov') return true;
  return false;
}
