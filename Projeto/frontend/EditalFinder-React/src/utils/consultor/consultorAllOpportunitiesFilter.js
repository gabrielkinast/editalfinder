import { getDeadlineAlertStatus, getDaysUntilDeadline } from '../deadlineAlerts';
import { getDisplayTitle } from '../displayTitle';

export const COMPAT_FILTER_ALL = 'todas';
export const COMPAT_FILTER_ALTA = 'alta';
export const COMPAT_FILTER_MEDIA = 'media';
export const COMPAT_FILTER_BAIXA = 'baixa';

export const PRAZO_FILTER_ALL = 'todas';
export const PRAZO_FILTER_COM_PRAZO = 'com_prazo';
export const PRAZO_FILTER_VENCE_7 = 'vence_7';
export const PRAZO_FILTER_SEM_PRAZO = 'sem_prazo';

export const SORT_SCORE = 'score';
export const SORT_PRAZO = 'prazo';
export const SORT_FONTE = 'fonte';
export const SORT_TITULO = 'titulo';

function normCompat(c) {
  const s = String(c || 'baixa')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
  if (s === 'alta') return COMPAT_FILTER_ALTA;
  if (s === 'media') return COMPAT_FILTER_MEDIA;
  return COMPAT_FILTER_BAIXA;
}

function scoreOf(row) {
  const n = Number(row?.score);
  return Number.isFinite(n) ? n : 0;
}

function fonteOf(row) {
  const ed = row?.edital || {};
  return String(ed.orgao || ed.fonte_recurso || '').trim();
}

function tituloOf(row) {
  const ed = row?.edital || {};
  return getDisplayTitle({
    titulo: ed.titulo,
    link: ed.linkOriginal || ed.link || ed.linkInscricao,
    descricao: ed.descricao,
    fonte_recurso: ed.orgao || ed.fonte_recurso,
  });
}

function searchHaystack(row) {
  const ed = row?.edital || {};
  const parts = [
    ed.titulo,
    ed.orgao,
    ed.fonte_recurso,
    ed.descricao,
    row?.matchLinha,
    ...(Array.isArray(row?.razoesPositivas) ? row.razoesPositivas : []),
    ...(Array.isArray(row?.razoes) ? row.razoes : []),
  ];
  ['area_tecnologica_raw', 'setor_estrategico_raw', 'perfil_ideal_raw', 'tags'].forEach((k) => {
    const v = ed[k];
    if (Array.isArray(v)) parts.push(...v.map(String));
    else if (v != null && v !== '') parts.push(String(v));
  });
  return parts
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
}

function matchesCompat(row, compatFilter) {
  if (!compatFilter || compatFilter === COMPAT_FILTER_ALL) return true;
  return normCompat(row?.compatibilidade) === compatFilter;
}

function matchesPrazo(row, prazoFilter) {
  if (!prazoFilter || prazoFilter === PRAZO_FILTER_ALL) return true;
  const ed = row?.edital || {};
  const status = getDeadlineAlertStatus(ed);
  if (prazoFilter === PRAZO_FILTER_SEM_PRAZO) return status === 'prazo_indefinido';
  if (prazoFilter === PRAZO_FILTER_VENCE_7) {
    return status === 'vence_hoje' || status === 'vence_3_dias' || status === 'vence_7_dias';
  }
  if (prazoFilter === PRAZO_FILTER_COM_PRAZO) {
    return status !== 'prazo_indefinido';
  }
  return true;
}

function matchesSearch(row, q) {
  const needle = String(q || '')
    .trim()
    .toLowerCase();
  if (!needle) return true;
  return searchHaystack(row).includes(needle);
}

function sortMatches(list, sortBy) {
  const arr = [...list];
  switch (sortBy) {
    case SORT_PRAZO:
      arr.sort((a, b) => {
        const da = getDaysUntilDeadline(a?.edital || {});
        const db = getDaysUntilDeadline(b?.edital || {});
        const na = da == null ? 99999 : da;
        const nb = db == null ? 99999 : db;
        if (na !== nb) return na - nb;
        return scoreOf(b) - scoreOf(a);
      });
      break;
    case SORT_FONTE:
      arr.sort((a, b) => fonteOf(a).localeCompare(fonteOf(b), 'pt-BR') || scoreOf(b) - scoreOf(a));
      break;
    case SORT_TITULO:
      arr.sort((a, b) => tituloOf(a).localeCompare(tituloOf(b), 'pt-BR') || scoreOf(b) - scoreOf(a));
      break;
    case SORT_SCORE:
    default:
      arr.sort((a, b) => scoreOf(b) - scoreOf(a));
      break;
  }
  return arr;
}

/**
 * Filtra e ordena matches do Radar (client-side).
 * @param {object[]} matches
 * @param {{ search?: string; compatFilter?: string; prazoFilter?: string; sortBy?: string }} filters
 */
/** @deprecated Alias defensivo */
export function filterConsultorOpportunities(matches = [], filters = {}) {
  return filterAndSortConsultorMatches(matches, filters);
}

export function filterAndSortConsultorMatches(matches, filters = {}) {
  const list = Array.isArray(matches) ? matches : [];
  const safeFilters = filters && typeof filters === 'object' ? filters : {};
  let filtered;
  try {
    filtered = list.filter(
      (row) =>
        row &&
        typeof row === 'object' &&
        matchesSearch(row, safeFilters.search) &&
        matchesCompat(row, safeFilters.compatFilter) &&
        matchesPrazo(row, safeFilters.prazoFilter),
    );
  } catch {
    return [];
  }
  try {
    return sortMatches(filtered, safeFilters.sortBy || SORT_SCORE);
  } catch {
    return filtered;
  }
}
