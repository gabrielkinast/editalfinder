import { favoritoRowMatchesEdital } from '../../services/favoritosService';
import {
  buildInitialPrecadastroState,
  fingerprintPrecadContext,
  loadPrecadEnvelope,
} from '../precadastroProjetoInitialState';
import { readPreProjetoContext } from '../precadastro/openPreProjetoFromOpportunity';
import { getOpportunitySelectionKey, normalizeSelectedOpportunity } from './opportunitySelection';
import {
  loadStoredTrackedItems,
  loadTrackedRemovedKeys,
} from './consultorTrackedOpportunitiesStorage';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

/**
 * Favoritos Radar por cliente (localStorage `radar_favoritos`).
 * @param {string|number} clienteId
 */
export function loadRadarFavoritoIdsForCliente(clienteId) {
  if (clienteId == null) return new Set();
  try {
    const raw = JSON.parse(localStorage.getItem('radar_favoritos') || '{}');
    const ids = raw[clienteId] ?? raw[String(clienteId)];
    if (!Array.isArray(ids)) return new Set();
    return new Set(ids.map((x) => String(x)));
  } catch {
    return new Set();
  }
}

function parsePrecadOpportunitiesJson(raw) {
  if (!raw || !String(raw).trim()) return [];
  try {
    const j = JSON.parse(raw);
    return Array.isArray(j) ? j : [];
  } catch {
    return [];
  }
}

/**
 * Oportunidades do último rascunho de pré-projeto (local).
 * @param {object|null} cliente
 */
export function loadPrecadOpportunitySnapshots(cliente) {
  const id = cliente?.id_cliente ?? cliente?.id;
  if (id == null) return [];
  const ctx = readPreProjetoContext(id);
  const fp = fingerprintPrecadContext(ctx.editalAssociado, '', ctx.radarMatch);
  try {
    const initial = buildInitialPrecadastroState(cliente, {});
    const env = loadPrecadEnvelope(id, initial, fp);
    return parsePrecadOpportunitiesJson(env.form?.bloco_estr_oportunidades_selecionadas);
  } catch {
    return [];
  }
}

function editalIdFromRow(row) {
  const ed = row?.edital || {};
  const id = ed.id ?? ed.id_edital ?? row?.id;
  return id != null ? String(id) : null;
}

function mergeItem(map, item) {
  const prev = map.get(item.key);
  if (!prev) {
    map.set(item.key, item);
    return;
  }
  const badges = new Set([...(prev.badges || []), ...(item.badges || [])]);
  const sourceTags = new Set([...(prev.sourceTags || []), ...(item.sourceTags || [])]);
  map.set(item.key, {
    ...prev,
    ...item,
    row: item.row || prev.row,
    badges: [...badges],
    sourceTags: [...sourceTags],
    titulo: item.titulo || prev.titulo,
    fonte: item.fonte || prev.fonte,
    prazo: item.prazo || prev.prazo,
    compatibilidade: item.compatibilidade || prev.compatibilidade,
    scorePct: item.scorePct ?? prev.scorePct,
    editalId: item.editalId ?? prev.editalId,
    link: item.link || prev.link,
  });
}

function itemFromNormalized(opp, badges, sourceTags = []) {
  const ed = opp.edital || {};
  return {
    key: opp.key,
    titulo: opp.titulo || ed.titulo || 'Oportunidade',
    fonte: opp.fonte_recurso || ed.fonte_recurso || ed.orgao || '—',
    prazo: opp.prazo_envio || ed.prazo_envio || '—',
    compatibilidade: opp.compatibilidade || '',
    scorePct: opp.scorePct ?? null,
    editalId: ed.id_edital ?? ed.id ?? null,
    link: opp.link || '',
    row: opp.row,
    badges: [...badges],
    sourceTags,
  };
}

function itemFromPrecadParsed(p) {
  return {
    key: p.key || `precad:${p.id_edital || p.titulo}`,
    titulo: p.titulo || 'Oportunidade',
    fonte: p.fonte_recurso || '—',
    prazo: p.prazo ?? p.prazo_envio ?? '—',
    compatibilidade: p.compatibilidade || '',
    scorePct: p.score ?? p.scorePct ?? null,
    editalId: p.id_edital ?? null,
    link: p.link || '',
    row: null,
    badges: ['preprojeto'],
    sourceTags: ['preprojeto'],
  };
}

function itemFromStored(stored) {
  return {
    key: stored.key,
    titulo: stored.titulo || 'Oportunidade',
    fonte: stored.fonte || '—',
    prazo: stored.prazo || '—',
    compatibilidade: stored.compatibilidade || '',
    scorePct: stored.scorePct ?? null,
    editalId: stored.editalId ?? null,
    link: stored.link || '',
    row: null,
    badges: ['acompanhada'],
    sourceTags: stored.sourceTags || ['stored'],
    storedOnly: true,
  };
}

function itemFromFavoriteRow(favRow, allMatches) {
  const row = (allMatches || []).find((m) => favoritoRowMatchesEdital(favRow, m?.edital));
  if (row) {
    const norm = normalizeSelectedOpportunity(row);
    return itemFromNormalized(norm, ['favorita'], ['favorita']);
  }
  const id = favRow.id_edital ?? favRow.idEdital;
  const link = favRow.edital_link ?? favRow.link;
  const key = id != null ? `id:${id}` : link ? `link:${link}` : `fav:${favRow.id ?? favRow.id_favorito}`;
  return {
    key,
    titulo: favRow.edital_titulo ?? favRow.titulo ?? 'Edital favorito',
    fonte: favRow.fonte_recurso ?? favRow.orgao ?? '—',
    prazo: favRow.prazo_envio ?? favRow.data_limite ?? '—',
    compatibilidade: '',
    scorePct: null,
    editalId: id,
    link: link || '',
    row: null,
    badges: ['favorita'],
    sourceTags: ['favorita'],
  };
}

const BADGE_SORT = { selecionada: 0, preprojeto: 1, favorita: 2, acompanhada: 3 };

function sortTrackedItems(list) {
  return [...list].sort((a, b) => {
    const ba = Math.min(...(a.badges || []).map((x) => BADGE_SORT[x] ?? 9));
    const bb = Math.min(...(b.badges || []).map((x) => BADGE_SORT[x] ?? 9));
    if (ba !== bb) return ba - bb;
    return (b.scorePct || 0) - (a.scorePct || 0);
  });
}

/**
 * Lista unificada de oportunidades acompanhadas para o cliente.
 * @param {object} input
 */
export function buildConsultorTrackedOpportunities(input = {}) {
  const {
    cliente = null,
    selectedOpportunities = [],
    allMatches = [],
    remoteFavorites = [],
    storedItems = null,
    removedKeys = null,
  } = input;

  const clienteId = cliente?.id_cliente ?? cliente?.id ?? null;
  const removed =
    removedKeys instanceof Set ? removedKeys : loadTrackedRemovedKeys(clienteId);
  const stored = storedItems ?? loadStoredTrackedItems(clienteId);
  const map = new Map();

  const selectedKeys = new Set();

  for (const opp of selectedOpportunities || []) {
    selectedKeys.add(opp.key);
    removed.delete(opp.key);
    mergeItem(map, itemFromNormalized(opp, ['selecionada'], ['selecao']));
  }

  for (const p of loadPrecadOpportunitySnapshots(cliente)) {
    const it = itemFromPrecadParsed(p);
    if (!removed.has(it.key) || selectedKeys.has(it.key)) {
      mergeItem(map, it);
    }
  }

  const radarFavIds = loadRadarFavoritoIdsForCliente(clienteId);
  for (const row of allMatches || []) {
    const eid = editalIdFromRow(row);
    if (eid && radarFavIds.has(eid)) {
      const norm = normalizeSelectedOpportunity(row);
      if (!removed.has(norm.key) || selectedKeys.has(norm.key)) {
        mergeItem(map, itemFromNormalized(norm, ['favorita'], ['radar_favorito']));
      }
    }
  }

  for (const favRow of remoteFavorites || []) {
    if (!favRow || favRow.ativo === false) continue;
    const it = itemFromFavoriteRow(favRow, allMatches);
    if (!removed.has(it.key) || selectedKeys.has(it.key)) {
      mergeItem(map, it);
    }
  }

  for (const st of stored) {
    if (removed.has(st.key) && !selectedKeys.has(st.key)) continue;
    if (map.has(st.key)) {
      const prev = map.get(st.key);
      mergeItem(map, {
        ...itemFromStored(st),
        badges: prev.badges,
        sourceTags: [...new Set([...(prev.sourceTags || []), ...(st.sourceTags || [])])],
        row: prev.row,
        storedOnly: false,
      });
    } else {
      mergeItem(map, itemFromStored(st));
    }
  }

  let list = [...map.values()].filter((it) => hasText(it.titulo) || hasText(it.key));

  list = list.map((it) => {
    const key = it.key || getOpportunitySelectionKey(it.row);
    return { ...it, key };
  });

  return sortTrackedItems(list);
}

export const TRACKED_BADGE_LABEL = {
  selecionada: 'Selecionada',
  preprojeto: 'Pré-projeto',
  favorita: 'Favorita',
  acompanhada: 'Acompanhada',
};
