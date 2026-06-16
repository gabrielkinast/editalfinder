import { getFonte, isAltaQualidade } from '../edital/editalFieldHelpers';
import { extractDashboardDeadline } from './dashboardDeadlineFields';
import {
  DASHBOARD_SCOPE_ALL,
  editalMatchesScope,
  getDashboardEditalType,
  getDashboardSourceScope,
  scopeBadgeLabel,
} from './dashboardClassification';

export { extractDashboardDeadline } from './dashboardDeadlineFields';
export { getDashboardEditalType, getDashboardSourceScope, classifyContentScope } from './dashboardClassification';

const MAX_PROCESS = 4000;
const TOP_CHART_LIMIT = 6;
const LIST_LIMIT = 5;
const SEM_PRAZO_WARN_RATIO = 0.55;

const PRAZO_CHART_LABELS = {
  vencendo_7: 'Vence em 7 dias',
  vencendo_30: 'Vence em 30 dias',
  prazo_confortavel: 'Prazo confortável',
  encerrado: 'Encerrados',
  sem_prazo: 'Sem prazo informado',
  prazo_invalido: 'Prazo inválido',
};

/**
 * Truncagem apenas para exibição (não usar como chave de agrupamento).
 * @param {unknown} value
 * @param {number} [maxLen=56]
 */
export function normalizeDashboardLabel(value, maxLen = 56) {
  let s = String(value ?? '')
    .trim()
    .replace(/\s+/g, ' ');
  if (!s) return 'Não informado';
  if (s.length > maxLen) return `${s.slice(0, maxLen - 1)}…`;
  return s;
}

/**
 * @param {unknown} raw
 * @returns {Date|null}
 */
export function safeDateParse(raw) {
  if (raw == null || raw === '') return null;
  const d = new Date(raw);
  return Number.isNaN(d.getTime()) ? null : d;
}

/**
 * @param {object} edital
 * @deprecated Preferir extractDashboardDeadline
 */
export function getDeadlineBucket(edital) {
  return extractDashboardDeadline(edital).status;
}

/**
 * Agrupa por chave estável; label de exibição separado.
 * @param {Array<object>} items
 * @param {(item: object) => string} keyFn
 * @param {(item: object) => string} [labelFn]
 * @param {number} limit
 */
export function buildTopBuckets(items, keyFn, labelFn, limit = TOP_CHART_LIMIT) {
  const map = new Map();
  for (const item of items) {
    const key = keyFn(item);
    const displayKey = labelFn ? labelFn(item) : key;
    const prev = map.get(key) || { label: displayKey, value: 0, key };
    prev.value += 1;
    map.set(key, prev);
  }
  return [...map.values()]
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

/**
 * @param {Array<object>} items
 * @param {number} limit
 */
function buildTopFonteBuckets(items, limit = TOP_CHART_LIMIT) {
  const map = new Map();
  for (const item of items) {
    const fonte = getFonte(item);
    const scope = getDashboardSourceScope(item);
    const key = fonte;
    const prev = map.get(key) || {
      label: normalizeDashboardLabel(fonte, 72),
      fullLabel: fonte,
      value: 0,
      scope,
      scopeLabel: scopeBadgeLabel(scope),
    };
    prev.value += 1;
    map.set(key, prev);
  }
  return [...map.values()]
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

function parseTime(edital) {
  const d = safeDateParse(
    edital.atualizado_em_raw ||
      edital.atualizado_em ||
      edital.criado_em ||
      edital.created_at,
  );
  return d ? d.getTime() : 0;
}

/**
 * @param {Array<object>} editais
 * @param {string} [scopeFilter]
 */
export function filterEditaisForDashboardScope(editais = [], scopeFilter = DASHBOARD_SCOPE_ALL) {
  const list = Array.isArray(editais) ? editais : [];
  if (!scopeFilter || scopeFilter === DASHBOARD_SCOPE_ALL) return list;
  return list.filter((e) => editalMatchesScope(e, scopeFilter));
}

/**
 * @param {Array<object>} editais
 * @param {string} [scopeFilter]
 */
export function buildDashboardAggregations(editais = [], scopeFilter = DASHBOARD_SCOPE_ALL) {
  const catalogCount = Array.isArray(editais) ? editais.length : 0;
  const scoped = filterEditaisForDashboardScope(editais, scopeFilter);
  const list = scoped.slice(0, MAX_PROCESS);

  let oportunidadesProvavelmenteAbertas = 0;
  let expiringSoon = 0;
  let expiring30 = 0;
  let highQualityOpen = 0;
  let prazoConfirmado = 0;
  const prazoBuckets = {
    vencendo_7: 0,
    vencendo_30: 0,
    prazo_confortavel: 0,
    encerrado: 0,
    sem_prazo: 0,
    prazo_invalido: 0,
  };

  for (const e of list) {
    const dl = extractDashboardDeadline(e);
    prazoBuckets[dl.status] = (prazoBuckets[dl.status] || 0) + 1;

    if (dl.status === 'vencendo_7') {
      expiringSoon += 1;
      oportunidadesProvavelmenteAbertas += 1;
      prazoConfirmado += 1;
      if (isAltaQualidade(e)) highQualityOpen += 1;
    } else if (dl.status === 'vencendo_30') {
      expiring30 += 1;
      oportunidadesProvavelmenteAbertas += 1;
      prazoConfirmado += 1;
      if (isAltaQualidade(e)) highQualityOpen += 1;
    } else if (dl.status === 'prazo_confortavel') {
      oportunidadesProvavelmenteAbertas += 1;
      prazoConfirmado += 1;
      if (isAltaQualidade(e)) highQualityOpen += 1;
    }
  }

  const recentEditais = [...list].sort((a, b) => parseTime(b) - parseTime(a)).slice(0, LIST_LIMIT);

  const expiringEditais = [...list]
    .filter((e) => {
      const dl = extractDashboardDeadline(e);
      return (
        dl.daysUntil != null &&
        dl.daysUntil >= 0 &&
        dl.daysUntil <= 30 &&
        dl.status !== 'encerrado' &&
        dl.status !== 'sem_prazo' &&
        dl.status !== 'prazo_invalido'
      );
    })
    .sort((a, b) => {
      const da = extractDashboardDeadline(a).daysUntil ?? 999;
      const db = extractDashboardDeadline(b).daysUntil ?? 999;
      return da - db;
    })
    .slice(0, LIST_LIMIT);

  const semPrazoRatio = list.length ? prazoBuckets.sem_prazo / list.length : 0;
  const prazoDataQualityWarning =
    semPrazoRatio >= SEM_PRAZO_WARN_RATIO
      ? 'Muitos registros não possuem prazo estruturado. Verifique o parser/backend.'
      : semPrazoRatio > 0.35
        ? 'Parte da base ainda não possui prazo estruturado.'
        : null;

  const charts = {
    editaisByFonte: buildTopFonteBuckets(list),
    editaisByTipo: buildTopBuckets(
      list,
      (e) => getDashboardEditalType(e),
      (e) => getDashboardEditalType(e),
    ),
    editaisByPrazo: Object.entries(prazoBuckets)
      .map(([key, value]) => ({
        label: PRAZO_CHART_LABELS[key] || key,
        value,
      }))
      .filter((x) => x.value > 0),
    totalAnalyzed: list.length,
    prazoDataQualityWarning,
    tipoChartSubtitle: 'Classificação estimada a partir dos campos disponíveis.',
    tipoChartTitle: 'Editais por modalidade',
    fonteChartSubtitle: 'Top fontes da base atual (badge = escopo estimado)',
  };

  const openEditais = oportunidadesProvavelmenteAbertas;
  const semPrazoEstruturado = prazoBuckets.sem_prazo + prazoBuckets.prazo_invalido;

  const metrics = {
    totalEditais: list.length,
    catalogEditais: catalogCount,
    scopedEditais: scoped.length,
    openEditais,
    oportunidadesProvavelmenteAbertas: openEditais,
    expiringSoon,
    expiring30,
    highQualityOpen,
    encerrados: prazoBuckets.encerrado,
    semPrazo: prazoBuckets.sem_prazo,
    semPrazoEstruturado,
    prazoConfirmado,
    prazoInvalido: prazoBuckets.prazo_invalido,
    semPrazoRatio,
    openPct: list.length ? Math.round((openEditais / list.length) * 100) : 0,
    prazoConfirmadoPct: list.length ? Math.round((prazoConfirmado / list.length) * 100) : 0,
    highQualityPct: openEditais
      ? Math.round((highQualityOpen / openEditais) * 100)
      : 0,
    totalNoticiasRecentes: 0,
    totalPesquisasRecentes: 0,
    totalClients: 0,
    reportedProblemsPending: 0,
  };

  return {
    metrics,
    recentEditais,
    expiringEditais,
    charts,
    processedCount: list.length,
    truncated: editais.length > MAX_PROCESS,
    scopeFilter,
  };
}

/**
 * @param {Array<object>} items
 * @param {number} days
 */
export function countRecentByDate(items = [], days = 30) {
  const cutoff = Date.now() - days * 86400000;
  let n = 0;
  for (const item of items) {
    const d = safeDateParse(
      item.data_publicacao || item.publicado_em || item.atualizado_em || item.created_at,
    );
    if (d && d.getTime() >= cutoff) n += 1;
  }
  return n;
}
