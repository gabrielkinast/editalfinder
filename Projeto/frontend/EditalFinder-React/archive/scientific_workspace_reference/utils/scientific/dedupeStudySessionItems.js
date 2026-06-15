import { slugifyStudyProgressLabel } from './scientificStudyProgressKeys';

const STATUS_RANK = {
  dominado: 4,
  estudando: 3,
  a_estudar: 2,
  none: 1,
  ignorar_agora: 0,
};

function normalizeTitle(title) {
  return slugifyStudyProgressLabel(title);
}

function statusRank(status) {
  return STATUS_RANK[status] ?? 1;
}

function pickBetterStatus(a, b) {
  return statusRank(a) >= statusRank(b) ? a : b;
}

function metadataScore(item) {
  const m = item.metadata || {};
  let s = (m.sources?.length || 0) + (item.subtitle ? 1 : 0);
  if (m.bookProgressPercent != null) s += 2;
  if (m.ideaType) s += 1;
  return s;
}

function mergeItems(existing, incoming) {
  const sources = new Set([...(existing.metadata?.sources || [existing.source]), incoming.source].filter(Boolean));
  const merged = {
    ...existing,
    ...incoming,
    metadata: {
      ...existing.metadata,
      ...incoming.metadata,
      sources: [...sources],
    },
    status: pickBetterStatus(existing.status, incoming.status),
    priority: Math.min(existing.priority ?? 50, incoming.priority ?? 50),
  };
  if (metadataScore(incoming) > metadataScore(existing)) {
    merged.subtitle = incoming.subtitle || existing.subtitle;
    merged.level = incoming.level || existing.level;
    merged.segment = incoming.segment || existing.segment;
  }
  return merged;
}

/**
 * Deduplica pool de sessão (Fase 2L-B).
 * @param {Array<object>} items
 */
export function dedupeStudySessionItems(items = []) {
  const byProgressKey = new Map();
  const byKindTitle = new Map();

  for (const item of items) {
    if (!item) continue;

    if (item.progressKey) {
      const prev = byProgressKey.get(item.progressKey);
      byProgressKey.set(item.progressKey, prev ? mergeItems(prev, item) : item);
      continue;
    }

    const titleKey = `${item.canonicalKey}|${item.kind}|${normalizeTitle(item.title)}`;
    const prev = byKindTitle.get(titleKey);
    byKindTitle.set(titleKey, prev ? mergeItems(prev, item) : item);
  }

  const out = [...byProgressKey.values()];
  for (const item of byKindTitle.values()) {
    if (item.progressKey && byProgressKey.has(item.progressKey)) continue;
    const titleKey = `${item.canonicalKey}|${item.kind}|${normalizeTitle(item.title)}`;
    const dup = out.find(
      (x) =>
        x.canonicalKey === item.canonicalKey &&
        x.kind === item.kind &&
        normalizeTitle(x.title) === normalizeTitle(item.title),
    );
    if (dup) {
      const idx = out.indexOf(dup);
      out[idx] = mergeItems(dup, item);
    } else {
      out.push(item);
    }
  }

  return out;
}
