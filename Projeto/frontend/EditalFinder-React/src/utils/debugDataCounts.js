/**
 * Sondagem dev-only de contagens de editais para diagnosticar a divergência
 * web vs desktop/Tauri.
 *
 * Ativação: somente quando `VITE_DEBUG_DATA_COUNTS` é truthy (1/true/yes/on).
 * Nunca roda silenciosamente em produção sem a flag.
 *
 * Separa três números distintos:
 * - rawCount      = COUNT(*) do servidor na view (head:true), sem filtros de UI;
 * - catalogCount  = nº de linhas efetivamente recebidas/carregadas no cliente;
 * - filteredCount = nº de linhas após os filtros client-side da lista (opcional).
 */

import { getRuntimeDataSourceInfo } from './debugRuntimeDataSource.js';

function isTruthyFlag(raw) {
  if (raw == null) return false;
  const s = String(raw).trim().toLowerCase();
  return s === '1' || s === 'true' || s === 'yes' || s === 'on';
}

/** A flag de build/dev `VITE_DEBUG_DATA_COUNTS` está ligada? (injetável para teste) */
export function dataCountsEnabled(env) {
  return isTruthyFlag(env?.VITE_DEBUG_DATA_COUNTS);
}

/** Chave de localStorage para ligar o debug sem rebuild (web/desktop:dev). */
export const DATA_COUNTS_LS_KEY = 'EDITALFINDER_DEBUG_DATA_COUNTS';

/**
 * Debug ligado por env (build-time) OU por localStorage (runtime, sem rebuild).
 * O localStorage é útil no app instalado/deploy onde não dá para rebuildar só
 * para investigar. Nunca expõe segredos.
 */
export function isDataCountDebugEnabled({ env, win } = {}) {
  if (dataCountsEnabled(env)) return true;
  const w = win ?? (typeof window !== 'undefined' ? window : undefined);
  try {
    return isTruthyFlag(w?.localStorage?.getItem(DATA_COUNTS_LS_KEY));
  } catch {
    return false;
  }
}

/**
 * Conta linhas com `head: true` (não traz payload).
 * @returns {Promise<{count: number|null, error: string|null}>}
 */
export async function probeCount(supabase, table, applyFilters) {
  try {
    let q = supabase.from(table).select('id', { count: 'exact', head: true });
    if (typeof applyFilters === 'function') q = applyFilters(q);
    const { count, error } = await q;
    return { count: count ?? null, error: error?.message ?? null };
  } catch (e) {
    return { count: null, error: e?.message ?? String(e) };
  }
}

/** Resolve import.meta.env de forma segura (Vite) com fallback Node/{}. */
function resolveViteEnv(env) {
  if (env !== undefined) return env;
  try {
    return import.meta.env ?? {};
  } catch {
    return {};
  }
}

/**
 * Loga apenas contagens client-side (catalogCount/filteredCount) + runtime.
 * Não faz consulta de rede. No-op se a flag estiver desligada.
 */
export function logEditaisClientCounts({
  catalogCount = null,
  filteredCount = null,
  env,
  consoleObj = typeof console !== 'undefined' ? console : null,
} = {}) {
  const resolvedEnv = resolveViteEnv(env);
  if (!isDataCountDebugEnabled({ env: resolvedEnv })) return null;

  const info = getRuntimeDataSourceInfo({ env: resolvedEnv });
  const payload = {
    catalogCount,
    filteredCount,
    runtime: info.runtime,
    supabaseHost: info.supabaseUrlHost,
    viewEditais: info.viewEditais,
    appVersion: info.appVersion,
    buildMode: info.buildMode,
  };
  if (consoleObj?.info) {
    consoleObj.info('[EditalFinder][DataCountDebug][client]', payload);
  }
  return payload;
}

/**
 * Loga rawCount (servidor) vs catalogCount/filteredCount (cliente) + runtime.
 * No-op se a flag estiver desligada.
 */
export async function logEditalDataCounts({
  supabase,
  viewName,
  catalogCount = null,
  filteredCount = null,
  env,
  consoleObj = typeof console !== 'undefined' ? console : null,
} = {}) {
  const resolvedEnv = resolveViteEnv(env);

  if (!isDataCountDebugEnabled({ env: resolvedEnv })) return null;
  if (!supabase || !viewName) return null;

  const info = getRuntimeDataSourceInfo({ env: resolvedEnv });
  const raw = await probeCount(supabase, viewName);

  const payload = {
    rawCount: raw.count,
    catalogCount,
    filteredCount,
    runtime: info.runtime,
    supabaseHost: info.supabaseUrlHost,
    viewEditais: info.viewEditais,
    appVersion: info.appVersion,
    buildMode: info.buildMode,
    rawError: raw.error,
  };

  if (consoleObj?.info) {
    consoleObj.info('[EditalFinder][DataCountDebug]', payload);
  }
  return payload;
}
