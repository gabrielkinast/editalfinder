const STORAGE_PREFIX = 'consultor_tracked_opportunities_';
const REMOVED_SUFFIX = '_removed';

function storageKey(clienteId) {
  return `${STORAGE_PREFIX}${clienteId}`;
}

function removedKey(clienteId) {
  return `${STORAGE_PREFIX}${clienteId}${REMOVED_SUFFIX}`;
}

/**
 * @param {string|number} clienteId
 * @returns {Set<string>}
 */
export function loadTrackedRemovedKeys(clienteId) {
  if (clienteId == null) return new Set();
  try {
    const raw = localStorage.getItem(removedKey(clienteId));
    if (!raw) return new Set();
    const arr = JSON.parse(raw);
    return new Set(Array.isArray(arr) ? arr.filter(Boolean) : []);
  } catch {
    return new Set();
  }
}

/**
 * @param {string|number} clienteId
 * @param {Set<string>|string[]} keys
 */
export function saveTrackedRemovedKeys(clienteId, keys) {
  if (clienteId == null) return;
  try {
    const arr = keys instanceof Set ? [...keys] : keys;
    localStorage.setItem(removedKey(clienteId), JSON.stringify(arr));
  } catch {
    /* ignore */
  }
}

/**
 * @param {string|number} clienteId
 * @returns {Array<object>}
 */
export function loadStoredTrackedItems(clienteId) {
  if (clienteId == null) return [];
  try {
    const raw = localStorage.getItem(storageKey(clienteId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    const items = parsed?.items ?? parsed;
    return Array.isArray(items) ? items : [];
  } catch {
    return [];
  }
}

/**
 * @param {string|number} clienteId
 * @param {Array<object>} items
 */
export function saveStoredTrackedItems(clienteId, items) {
  if (clienteId == null) return;
  try {
    localStorage.setItem(
      storageKey(clienteId),
      JSON.stringify({ items, updatedAt: new Date().toISOString() }),
    );
  } catch {
    /* ignore */
  }
}

/**
 * Normaliza oportunidade selecionada para snapshot armazenado.
 * @param {ReturnType<import('./opportunitySelection').normalizeSelectedOpportunity>} opp
 * @param {string} [eventTag]
 */
export function snapshotFromNormalizedOpportunity(opp, eventTag = 'manual') {
  const ed = opp?.edital || {};
  return {
    key: opp.key,
    titulo: opp.titulo || ed.titulo || '',
    fonte: opp.fonte_recurso || ed.fonte_recurso || ed.orgao || '',
    prazo: opp.prazo_envio || ed.prazo_envio || '',
    compatibilidade: opp.compatibilidade || '',
    scorePct: opp.scorePct ?? null,
    editalId: ed.id_edital ?? ed.id ?? null,
    link: opp.link || ed.link || '',
    sourceTags: [eventTag],
    savedAt: new Date().toISOString(),
  };
}

/**
 * Mescla snapshots ao salvar após triagem ou pré-projeto.
 * @param {string|number} clienteId
 * @param {Array} normalizedOpportunities
 * @param {'triagem'|'preprojeto'|'manual'} eventTag
 */
export function persistTrackedSnapshots(clienteId, normalizedOpportunities, eventTag) {
  if (clienteId == null || !Array.isArray(normalizedOpportunities) || !normalizedOpportunities.length) {
    return 0;
  }
  const existing = loadStoredTrackedItems(clienteId);
  const byKey = new Map(existing.map((it) => [it.key, { ...it }]));
  const removed = loadTrackedRemovedKeys(clienteId);

  for (const opp of normalizedOpportunities) {
    const snap = snapshotFromNormalizedOpportunity(opp, eventTag);
    removed.delete(snap.key);
    const prev = byKey.get(snap.key);
    if (prev) {
      const tags = new Set([...(prev.sourceTags || []), eventTag]);
      byKey.set(snap.key, { ...prev, ...snap, sourceTags: [...tags] });
    } else {
      byKey.set(snap.key, snap);
    }
  }

  const merged = [...byKey.values()];
  saveStoredTrackedItems(clienteId, merged);
  saveTrackedRemovedKeys(clienteId, removed);
  return merged.length;
}

/**
 * Remove do acompanhamento persistido (não desfaz seleção ativa).
 * @param {string|number} clienteId
 * @param {string} key
 */
export function removeTrackedOpportunity(clienteId, key) {
  if (clienteId == null || !key) return;
  const removed = loadTrackedRemovedKeys(clienteId);
  removed.add(key);
  saveTrackedRemovedKeys(clienteId, removed);

  const items = loadStoredTrackedItems(clienteId).filter((it) => it.key !== key);
  saveStoredTrackedItems(clienteId, items);
}
