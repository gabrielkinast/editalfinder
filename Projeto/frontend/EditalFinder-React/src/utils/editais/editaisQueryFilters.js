import { DASHBOARD_SCOPE_ALL } from '../dashboard/dashboardClassification';
import { getDashboardEditalType } from '../dashboard/dashboardClassification';
import { editalMatchesScope } from '../dashboard/dashboardClassification';

/** @typedef {'vencendo_7'|'vencendo_30'|'sem_prazo'|'encerrados'|'prazo_confortavel'|'prazo_invalido'} PrazoQueryValue */

export const PRAZO_QUERY_VALUES = new Set([
  'vencendo_7',
  'vencendo_30',
  'sem_prazo',
  'encerrados',
  'prazo_confortavel',
  'prazo_invalido',
]);

export const SCOPE_QUERY_VALUES = new Set(['brasil', 'internacional', 'multilateral']);

/** Valor interno na EditaisPage quando nenhum escopo está ativo. */
export const SCOPE_FILTER_TODOS = 'todos';

/**
 * Normaliza parâmetro de escopo da URL ou estado da UI.
 * @param {string|null|undefined} value
 * @returns {'todos'|'brasil'|'internacional'|'multilateral'}
 */
export function normalizeScopeParam(value) {
  if (value == null || value === '') return SCOPE_FILTER_TODOS;
  const v = String(value).trim().toLowerCase();
  if (v === 'all' || v === DASHBOARD_SCOPE_ALL) return SCOPE_FILTER_TODOS;
  if (SCOPE_QUERY_VALUES.has(v)) return v;
  return SCOPE_FILTER_TODOS;
}

/**
 * Valor para query string (omitir quando "todos").
 * @param {string} scopeFilter
 * @returns {string|undefined}
 */
export function scopeFilterToQueryParam(scopeFilter) {
  const n = normalizeScopeParam(scopeFilter);
  return n === SCOPE_FILTER_TODOS ? undefined : n;
}

const PRAZO_LABELS = {
  vencendo_7: 'Prazo: vencendo em 7 dias',
  vencendo_30: 'Prazo: vencendo em 30 dias',
  sem_prazo: 'Prazo: sem prazo estruturado',
  encerrados: 'Prazo: encerrados',
  prazo_confortavel: 'Prazo: confortável',
  prazo_invalido: 'Prazo: inválido',
};

const SCOPE_LABELS = {
  brasil: 'Escopo: Brasil',
  internacional: 'Escopo: Internacional',
  multilateral: 'Escopo: Multilateral',
};

/** Preset interno da sidebar (= valor da URL para prazo). */
export function prazoQueryToPreset(prazo) {
  if (!prazo || !PRAZO_QUERY_VALUES.has(prazo)) return '';
  return prazo;
}

export function presetToPrazoQuery(preset) {
  if (!preset) return null;
  if (PRAZO_QUERY_VALUES.has(preset)) return preset;
  if (preset === 'd7') return 'vencendo_7';
  if (preset === 'd30') return 'vencendo_30';
  if (preset === 'd90') return 'vencendo_30';
  if (preset === 'sem') return 'sem_prazo';
  if (preset === 'encerrados') return 'encerrados';
  return null;
}

export function prazoFilterLabel(prazo) {
  return PRAZO_LABELS[prazo] || `Prazo: ${prazo}`;
}

export function scopeFilterLabel(scopeFilter) {
  if (!scopeFilter || scopeFilter === SCOPE_FILTER_TODOS) return 'Escopo: todos';
  return SCOPE_LABELS[scopeFilter] || `Escopo: ${scopeFilter}`;
}

/**
 * @param {object} [filters]
 * @param {string} [filters.prazo]
 * @param {string} [filters.scope]
 * @param {string} [filters.modalidade]
 * @param {string} [filters.fonte]
 */
export function buildEditaisUrl(filters = {}) {
  const params = new URLSearchParams();
  const { prazo, scope, modalidade, fonte } = filters;

  if (prazo && PRAZO_QUERY_VALUES.has(prazo)) params.set('prazo', prazo);
  const scopeParam = scopeFilterToQueryParam(scope);
  if (scopeParam) params.set('scope', scopeParam);
  if (modalidade) params.set('modalidade', modalidade);
  if (fonte) params.set('fonte', fonte);

  const q = params.toString();
  return q ? `/editais?${q}` : '/editais';
}

/**
 * @param {URLSearchParams} searchParams
 */
export function parseEditaisQueryFilters(searchParams) {
  const prazoRaw = searchParams.get('prazo');
  const scopeRaw = searchParams.get('scope');
  const modalidadeRaw = searchParams.get('modalidade');
  const fonteRaw = searchParams.get('fonte');

  const prazo = prazoRaw && PRAZO_QUERY_VALUES.has(prazoRaw) ? prazoRaw : '';
  const scopeFilter = normalizeScopeParam(scopeRaw);
  const scope = scopeFilter === SCOPE_FILTER_TODOS ? '' : scopeFilter;
  const modalidade = modalidadeRaw ? String(modalidadeRaw).trim() : '';
  const fonte = fonteRaw ? String(fonteRaw).trim() : '';

  return {
    prazo,
    scope,
    scopeFilter,
    modalidade,
    fonte,
    prazoPreset: prazoQueryToPreset(prazo),
  };
}

/**
 * @param {object} sidebarState
 */
export function sidebarToSearchParams(sidebarState) {
  const params = new URLSearchParams();
  const prazo = presetToPrazoQuery(sidebarState.prazoPreset);
  if (prazo) params.set('prazo', prazo);
  if (sidebarState.queryScope) params.set('scope', sidebarState.queryScope);
  if (sidebarState.queryModalidade) params.set('modalidade', sidebarState.queryModalidade);
  if (sidebarState.queryFonte || sidebarState.fonteBusca) {
    params.set('fonte', sidebarState.queryFonte || sidebarState.fonteBusca);
  }
  return params;
}

/**
 * Aplica query string ao estado da sidebar (sem sobrescrever toggles não relacionados).
 * @param {object} filters
 * @param {ReturnType<typeof parseEditaisQueryFilters>} parsed
 */
export function applyQueryFiltersToSidebar(filters, parsed) {
  const next = {
    ...filters,
    prazoPreset: parsed.prazoPreset || '',
    queryScope: parsed.scope || '',
    queryModalidade: parsed.modalidade || '',
    queryFonte: parsed.fonte || '',
  };
  if (parsed.fonte) {
    next.fonteBusca = parsed.fonte;
  }
  if (parsed.prazo === 'encerrados') {
    next.toggleIncluirEncerrados = true;
  }
  return next;
}

/**
 * @param {Record<string, unknown>} edital
 * @param {string} scope
 */
export function editalMatchesScopeQuery(edital, scopeFilter) {
  const normalized = normalizeScopeParam(scopeFilter);
  if (normalized === SCOPE_FILTER_TODOS) return true;
  return editalMatchesScope(edital, normalized);
}

/**
 * @param {Record<string, unknown>} edital
 * @param {string} modalidadeSlug
 */
export function editalMatchesModalidadeQuery(edital, modalidadeSlug) {
  if (!modalidadeSlug) return true;
  const tipo = getDashboardEditalType(edital).toLowerCase();
  const slug = modalidadeSlug.toLowerCase().replace(/-/g, ' ');
  return tipo.includes(slug) || slug.includes(tipo.slice(0, 12));
}

/**
 * @param {object} filters
 */
export function logNavigateToEditaisFilter(filters) {
  if (!import.meta.env.DEV) return;
  console.info('[dashboard] navigate_to_editais_filter', {
    ...filters,
    url: buildEditaisUrl(filters),
  });
}

/**
 * @param {ReturnType<typeof parseEditaisQueryFilters>} applied
 */
export function logEditaisQueryFiltersApplied(applied) {
  if (!import.meta.env.DEV) return;
  console.info('[editais] query_filters_applied', {
    prazo: applied.prazo || null,
    scopeFilter: applied.scopeFilter ?? SCOPE_FILTER_TODOS,
    scope: applied.scope || null,
    modalidade: applied.modalidade || null,
    fonte: applied.fonte || null,
    prazoPreset: applied.prazoPreset || null,
  });
}

/**
 * @param {object} payload
 */
export function logEditaisDeadlineFilterResult(payload) {
  if (!import.meta.env.DEV) return;
  console.info('[editais] deadline_filter_result', payload);
}
