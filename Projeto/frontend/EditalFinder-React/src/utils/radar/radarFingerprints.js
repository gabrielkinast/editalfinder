/**
 * Fingerprints pré-calculados (catálogo / clientes) — evita recomputar no clique.
 */
import {
  catalogFingerprintFromEditais,
  clienteFingerprintFromRow,
  optionsFingerprintFromMerged,
} from './radarPersistentCache';

export {
  catalogFingerprintFromEditais,
  clienteFingerprintFromRow,
  optionsFingerprintFromMerged,
};

export function buildClientesFingerprintMap(clientes) {
  const map = new Map();
  const list = Array.isArray(clientes) ? clientes : [];
  for (let i = 0; i < list.length; i++) {
    const c = list[i];
    const id = c?.id_cliente ?? c?.id;
    const key = id !== undefined && id !== null ? String(id) : `idx-${i}`;
    map.set(key, clienteFingerprintFromRow(c));
  }
  return map;
}
