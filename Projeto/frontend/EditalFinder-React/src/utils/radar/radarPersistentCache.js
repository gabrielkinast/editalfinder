/**
 * Cache persistente do Radar em sessionStorage (Fase 0.8).
 * Apenas resultados completos (partial: false). Sem dados além do necessário para cards.
 */
import { isValidRadarCacheEntry, sanitizeRadarResults } from './radarResultShape';

/** Versão do algoritmo / formato do payload — incrementar ao mudar score ou shape dos itens. */
export const RADAR_MATCH_CACHE_VERSION = 'v2';

/**
 * TTL do cache de sessão (2 horas).
 * Alternativa documentada para testes: 30 * 60 * 1000 (30 minutos).
 */
export const RADAR_SESSION_CACHE_TTL_MS = 2 * 60 * 60 * 1000;

/** Máximo de clientes (entradas) guardados em sessionStorage. */
export const RADAR_SESSION_CACHE_MAX_ENTRIES = 10;

/** Idade > esta fração do TTL → hit válido mas `staleSoon` (recalcular em background). */
export const RADAR_SESSION_CACHE_STALE_SOON_RATIO = 0.75;

const INDEX_KEY = 'radar:session:index';

function nowMs() {
  return Date.now();
}

function shortHash(str) {
  const s = String(str ?? '');
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(36);
}

/** Assinatura leve do catálogo (mesma lógica que useRadarMatches). */
export function catalogFingerprintFromEditais(editais) {
  const list = Array.isArray(editais) ? editais : [];
  if (list.length === 0) return '0';
  let h = list.length ^ 0;
  const stride = Math.max(1, Math.floor(list.length / 80));
  for (let i = 0; i < list.length; i += stride) {
    const id = list[i]?.id;
    const token = String(id ?? '');
    h = Math.imul(h ^ token.length, 0x9e3779b9) ^ (token.charCodeAt(0) | 0);
  }
  return `${list.length}|${list[0]?.id ?? ''}|${list[list.length - 1]?.id ?? ''}|${h}`;
}

/** Perfil do cliente relevante para o match. */
export function clienteFingerprintFromRow(cliente) {
  if (!cliente || typeof cliente !== 'object') return '0';
  const parts = [
    cliente.id_cliente ?? cliente.id ?? '',
    cliente.perfil ?? cliente.tipo_perfil ?? '',
    cliente.setor ?? '',
    cliente.porte_empresa ?? '',
    cliente.natureza_juridica ?? '',
    cliente.cnae_principal ?? '',
    cliente.area_inovacao ?? '',
    cliente.interesse_temas ?? '',
    cliente.descricao_projeto ?? '',
    cliente.updated_at ?? cliente.data_atualizacao ?? '',
  ];
  return shortHash(parts.join('|'));
}

export function optionsFingerprintFromMerged(options = {}) {
  return shortHash(
    JSON.stringify({
      incluirSuspeitos: !!options.incluirSuspeitos,
      incluirEncerrados: !!options.incluirEncerrados,
      incluirAproximados: !!options.incluirAproximados,
      cortePrincipal: options.cortePrincipal,
      corteFallback: options.corteFallback,
      limite: options.limite,
      scoreMinimoExibir: options.scoreMinimoExibir,
    }),
  );
}

export function buildRadarSessionStorageKey(clienteId, catalogFp, clienteFp, optsFp) {
  return `radar:${RADAR_MATCH_CACHE_VERSION}:${clienteId}:${catalogFp}:${clienteFp}:${optsFp}`;
}

function readIndex() {
  try {
    const raw = sessionStorage.getItem(INDEX_KEY);
    if (!raw) return { keys: [], updatedAt: {} };
    const parsed = JSON.parse(raw);
    return {
      keys: Array.isArray(parsed.keys) ? parsed.keys : [],
      updatedAt: parsed.updatedAt && typeof parsed.updatedAt === 'object' ? parsed.updatedAt : {},
    };
  } catch {
    return { keys: [], updatedAt: {} };
  }
}

function writeIndex(index) {
  sessionStorage.setItem(INDEX_KEY, JSON.stringify(index));
}

function radarPerfSession(label, extra = {}) {
  if (!import.meta.env?.DEV) return;
  console.info(`[radar-perf] ${label}`, extra);
}

function pruneIndex(index, maxEntries = RADAR_SESSION_CACHE_MAX_ENTRIES) {
  let { keys, updatedAt } = index;
  if (keys.length <= maxEntries) return { keys, updatedAt, pruned: 0 };

  const sorted = [...keys].sort(
    (a, b) => (updatedAt[a] ?? 0) - (updatedAt[b] ?? 0),
  );
  const removeCount = keys.length - maxEntries;
  const toRemove = sorted.slice(0, removeCount);
  for (const k of toRemove) {
    try {
      sessionStorage.removeItem(k);
    } catch {
      /* ignore */
    }
    delete updatedAt[k];
  }
  keys = keys.filter((k) => !toRemove.includes(k));
  radarPerfSession('session_cache_prune', { removed: removeCount, remaining: keys.length });
  return { keys, updatedAt, pruned: removeCount };
}

function touchIndexKey(storageKey) {
  const index = readIndex();
  const keys = index.keys.filter((k) => k !== storageKey);
  keys.unshift(storageKey);
  const updatedAt = { ...index.updatedAt, [storageKey]: nowMs() };
  const pruned = pruneIndex({ keys, updatedAt });
  writeIndex(pruned);
}

function removeFromIndex(storageKey) {
  const index = readIndex();
  const keys = index.keys.filter((k) => k !== storageKey);
  const updatedAt = { ...index.updatedAt };
  delete updatedAt[storageKey];
  writeIndex({ keys, updatedAt });
}

function validateEntry(entry, expected) {
  if (!entry || typeof entry !== 'object') return { valid: false, reason: 'missing' };
  if (entry.partial !== false) return { valid: false, reason: 'partial_not_stored' };
  if (entry.meta?.algorithmVersion !== RADAR_MATCH_CACHE_VERSION) {
    return { valid: false, reason: 'algorithm_version' };
  }
  const exp = expected;
  if (entry.meta?.catalogFingerprint !== exp.catalogFingerprint) {
    return { valid: false, reason: 'catalog_fingerprint' };
  }
  if (entry.meta?.clienteFingerprint !== exp.clienteFingerprint) {
    return { valid: false, reason: 'cliente_fingerprint' };
  }
  if (entry.meta?.optionsFingerprint !== exp.optionsFingerprint) {
    return { valid: false, reason: 'options_fingerprint' };
  }
  if (String(entry.clienteId) !== String(exp.clienteId)) {
    return { valid: false, reason: 'cliente_id' };
  }
  const expiresAt = entry.expiresAt ?? 0;
  if (expiresAt && nowMs() > expiresAt) {
    return { valid: false, reason: 'expired' };
  }
  if (!Array.isArray(entry.items)) {
    return { valid: false, reason: 'invalid_items' };
  }
  if (!isValidRadarCacheEntry(entry)) {
    return { valid: false, reason: 'invalid_shape' };
  }
  return { valid: true, reason: '' };
}

export function isSessionCacheStaleSoon(entry) {
  if (!entry?.generatedAt || !entry?.expiresAt) return false;
  const age = nowMs() - entry.generatedAt;
  const ttl = entry.expiresAt - entry.generatedAt;
  if (ttl <= 0) return false;
  return age >= ttl * RADAR_SESSION_CACHE_STALE_SOON_RATIO;
}

function resolveSessionFingerprints({
  cliente,
  editais,
  options,
  catalogFingerprint: catalogIn,
  clienteFingerprint: clienteIn,
  optionsFingerprint: optionsIn,
}) {
  return {
    catalogFingerprint: catalogIn ?? catalogFingerprintFromEditais(editais),
    clienteFingerprint: clienteIn ?? clienteFingerprintFromRow(cliente),
    optionsFingerprint: optionsIn ?? optionsFingerprintFromMerged(options),
  };
}

/**
 * @returns {{ hit: boolean, entry?: object, staleSoon?: boolean, reason?: string }}
 */
export function loadRadarSessionCache({
  clienteId,
  cliente,
  editais,
  options,
  catalogFingerprint: catalogIn,
  clienteFingerprint: clienteIn,
  optionsFingerprint: optionsIn,
}) {
  if (typeof sessionStorage === 'undefined') {
    return { hit: false, reason: 'no_session_storage' };
  }

  const { catalogFingerprint, clienteFingerprint, optionsFingerprint } =
    resolveSessionFingerprints({
      cliente,
      editais,
      options,
      catalogFingerprint: catalogIn,
      clienteFingerprint: clienteIn,
      optionsFingerprint: optionsIn,
    });
  const storageKey = buildRadarSessionStorageKey(
    clienteId,
    catalogFingerprint,
    clienteFingerprint,
    optionsFingerprint,
  );

  try {
    const raw = sessionStorage.getItem(storageKey);
    if (!raw) {
      radarPerfSession('session_cache_miss', {
        cliente_id: clienteId,
        storage_key: storageKey,
      });
      return { hit: false, reason: 'miss' };
    }

    const entry = JSON.parse(raw);
    const validation = validateEntry(entry, {
      clienteId,
      catalogFingerprint,
      clienteFingerprint,
      optionsFingerprint,
    });

    if (!validation.valid) {
      sessionStorage.removeItem(storageKey);
      removeFromIndex(storageKey);
      const label =
        validation.reason === 'expired'
          ? 'session_cache_stale'
          : validation.reason === 'invalid_shape'
            ? 'session_cache_invalid_shape'
            : 'session_cache_miss';
      radarPerfSession(label, {
        cliente_id: clienteId,
        reason: validation.reason,
      });
      return { hit: false, reason: validation.reason };
    }

    const staleSoon = isSessionCacheStaleSoon(entry);
    radarPerfSession('session_cache_hit', {
      cliente_id: clienteId,
      items_total: entry.items.length,
      stale_soon: staleSoon,
      age_ms: nowMs() - (entry.generatedAt ?? 0),
      expires_in_ms: (entry.expiresAt ?? 0) - nowMs(),
    });
    if (staleSoon) {
      radarPerfSession('session_cache_stale', {
        cliente_id: clienteId,
        message: 'TTL quase expirado — recalcular em background',
      });
    }

    touchIndexKey(storageKey);
    return { hit: true, entry, staleSoon, storageKey };
  } catch (e) {
    radarPerfSession('session_cache_error', {
      cliente_id: clienteId,
      phase: 'load',
      message: e?.message,
    });
    return { hit: false, reason: 'error' };
  }
}

/**
 * Persiste apenas resultado completo (partial: false).
 */
export function saveRadarSessionCache({
  clienteId,
  cliente,
  editais,
  options,
  rows,
  meta,
  source = 'worker',
  catalogFingerprint: catalogIn,
  clienteFingerprint: clienteIn,
  optionsFingerprint: optionsIn,
}) {
  if (typeof sessionStorage === 'undefined') return false;
  if (!Array.isArray(rows)) return false;

  const { catalogFingerprint, clienteFingerprint, optionsFingerprint } =
    resolveSessionFingerprints({
      cliente,
      editais,
      options,
      catalogFingerprint: catalogIn,
      clienteFingerprint: clienteIn,
      optionsFingerprint: optionsIn,
    });
  const storageKey = buildRadarSessionStorageKey(
    clienteId,
    catalogFingerprint,
    clienteFingerprint,
    optionsFingerprint,
  );

  const generatedAt = nowMs();
  const entry = {
    clienteId: String(clienteId),
    generatedAt,
    expiresAt: generatedAt + RADAR_SESSION_CACHE_TTL_MS,
    partial: false,
    source: 'session_cache',
    items: rows,
    meta: {
      catalogFingerprint,
      clienteFingerprint,
      optionsFingerprint,
      algorithmVersion: RADAR_MATCH_CACHE_VERSION,
      computeSource: source,
      ...(meta && typeof meta === 'object' ? meta : {}),
    },
  };

  const payload = JSON.stringify(entry);

  try {
    sessionStorage.setItem(storageKey, payload);
    touchIndexKey(storageKey);
    radarPerfSession('session_cache_save', {
      cliente_id: clienteId,
      items_total: rows.length,
      storage_key: storageKey,
      ttl_ms: RADAR_SESSION_CACHE_TTL_MS,
    });
    return true;
  } catch (e) {
    const isQuota =
      e?.name === 'QuotaExceededError' ||
      e?.code === 22 ||
      e?.code === 1014;
    radarPerfSession('session_cache_error', {
      cliente_id: clienteId,
      phase: 'save',
      quota: isQuota,
      message: e?.message,
    });

    if (isQuota) {
      const index = readIndex();
      const pruned = pruneIndex(index, Math.max(2, Math.floor(RADAR_SESSION_CACHE_MAX_ENTRIES / 2)));
      writeIndex(pruned);
      try {
        sessionStorage.setItem(storageKey, payload);
        touchIndexKey(storageKey);
        radarPerfSession('session_cache_save', {
          cliente_id: clienteId,
          items_total: rows.length,
          after_prune: true,
        });
        return true;
      } catch (e2) {
        radarPerfSession('session_cache_error', {
          cliente_id: clienteId,
          phase: 'save_retry',
          message: e2?.message,
        });
      }
    }
    return false;
  }
}

/** Remove todas as entradas de sessionStorage para um cliente. */
export function invalidateRadarSessionCacheForCliente(clienteId) {
  if (typeof sessionStorage === 'undefined' || !clienteId) return 0;
  const prefix = `radar:${RADAR_MATCH_CACHE_VERSION}:${clienteId}:`;
  const index = readIndex();
  let removed = 0;
  const keys = index.keys.filter((k) => !k.startsWith(prefix));
  const updatedAt = { ...index.updatedAt };
  for (const k of index.keys) {
    if (k.startsWith(prefix)) {
      try {
        sessionStorage.removeItem(k);
        removed += 1;
      } catch {
        /* ignore */
      }
      delete updatedAt[k];
    }
  }
  writeIndex({ keys, updatedAt });
  if (removed > 0 && import.meta.env?.DEV) {
    radarPerfSession('session_cache_prune', { cliente_id: clienteId, removed, reason: 'invalidate_cliente' });
  }
  return removed;
}

/** Remove chaves de versões antigas (ex. v1) no startup. */
export function purgeLegacyRadarSessionCaches() {
  if (typeof sessionStorage === 'undefined') return 0;
  const currentPrefix = `radar:${RADAR_MATCH_CACHE_VERSION}:`;
  let removed = 0;
  try {
    const index = readIndex();
    const keys = [...index.keys];
    const kept = [];
    const updatedAt = {};
    for (const k of keys) {
      if (k.startsWith('radar:') && !k.startsWith(currentPrefix)) {
        try {
          sessionStorage.removeItem(k);
          removed += 1;
        } catch {
          /* ignore */
        }
      } else {
        kept.push(k);
        if (index.updatedAt[k]) updatedAt[k] = index.updatedAt[k];
      }
    }
    writeIndex({ keys: kept, updatedAt });
    if (removed > 0 && import.meta.env?.DEV) {
      radarPerfSession('session_cache_prune', { removed, reason: 'legacy_version' });
    }
  } catch {
    /* ignore */
  }
  return removed;
}

/** Converte entrada de sessionStorage para payload do cache em memória. */
export function sessionEntryToMemoryPayload(entry, sourceLabel = 'session_cache') {
  return {
    rows: sanitizeRadarResults(entry.items, { source: sourceLabel }),
    meta: entry.meta,
    partial: false,
    source: sourceLabel,
    clienteId: entry.clienteId,
    generatedAt: entry.generatedAt,
  };
}
