/**
 * Diagnóstico dev-only do runtime e da fonte de dados (web vs desktop/Tauri).
 *
 * Objetivo: ajudar a investigar divergências de contagem de editais entre o
 * site (web) e o app desktop (EXE/Tauri) SEM vazar segredos.
 *
 * Regras de segurança:
 * - Nunca retorna a anon key completa.
 * - Por padrão expõe apenas `hasSupabaseAnonKey: true/false` e o host do Supabase.
 * - `redactKey` existe para um preview opcional (4+4 chars), mas não é usado no
 *   objeto de diagnóstico padrão.
 *
 * As funções são puras/injetáveis (aceitam `deps`) para serem testáveis em Node.
 */

import { IS_TAURI_BUILD, ROUTER_BASENAME } from '../config/routerBase.js';

/** Resolve o objeto window de forma segura (Node/SSR não têm window). */
function resolveWindow(win) {
  if (win !== undefined) return win;
  return typeof window !== 'undefined' ? window : undefined;
}

/** Resolve import.meta.env de forma segura. */
function resolveEnv(env) {
  if (env !== undefined) return env;
  try {
    return import.meta.env ?? {};
  } catch {
    return {};
  }
}

/**
 * Detecta o runtime de execução.
 * @returns {'web'|'desktop_tauri'|'unknown'}
 */
export function detectRuntime({ win, isTauriBuild = IS_TAURI_BUILD } = {}) {
  const w = resolveWindow(win);
  if (isTauriBuild) return 'desktop_tauri';
  if (w && (w.__TAURI__ || w.__TAURI_INTERNALS__ || w.__TAURI_METADATA__ || w.isTauri)) {
    return 'desktop_tauri';
  }
  if (w) return 'web';
  return 'unknown';
}

/** Host do Supabase sem query/credenciais; '' se inválido. */
export function safeHost(url) {
  try {
    return new URL(String(url)).host;
  } catch {
    return '';
  }
}

/**
 * Redação opcional de uma chave (NÃO usada no diagnóstico padrão).
 * Retorna apenas presença, comprimento e um preview 4+4.
 */
export function redactKey(key) {
  const s = key == null ? '' : String(key);
  if (!s) return { hasKey: false };
  if (s.length <= 8) return { hasKey: true, keyLength: s.length };
  return {
    hasKey: true,
    keyLength: s.length,
    keyPreview: `${s.slice(0, 4)}…${s.slice(-4)}`,
  };
}

/** Lista chaves de localStorage relacionadas a editais/filtros (sem valores). */
export function listEditalLocalStorageKeys(win) {
  const w = resolveWindow(win);
  const ls = w?.localStorage;
  if (!ls || typeof ls.length !== 'number') return [];
  const re = /(edital|filtro|filter|pref|favorit|radar|consultor)/i;
  const out = [];
  try {
    for (let i = 0; i < ls.length; i += 1) {
      const k = ls.key(i);
      if (k && re.test(k)) out.push(k);
    }
  } catch {
    return out;
  }
  return out.sort();
}

/**
 * Coleta o diagnóstico completo de runtime/fonte de dados (sem segredos).
 * Todas as dependências são injetáveis para teste.
 */
export function getRuntimeDataSourceInfo(deps = {}) {
  const env = resolveEnv(deps.env);
  const win = resolveWindow(deps.win);
  const isTauriBuild = deps.isTauriBuild ?? IS_TAURI_BUILD;
  const supabaseUrl = deps.supabaseUrl ?? env.VITE_SUPABASE_URL ?? '';
  const supabaseAnonKey =
    deps.supabaseAnonKey ?? env.VITE_SUPABASE_ANON_KEY ?? env.VITE_SUPABASE_KEY ?? '';
  const viewEditais = deps.viewEditais ?? env.VITE_VIEW_EDITAIS ?? 'vw_editais_front';
  const routerBasename = deps.routerBasename ?? ROUTER_BASENAME;

  const runtime = detectRuntime({ win, isTauriBuild });

  return {
    runtime,
    isTauri: runtime === 'desktop_tauri',
    isDev: Boolean(env.DEV),
    buildMode: env.MODE ?? 'unknown',
    appVersion: env.VITE_APP_VERSION ?? 'unknown',
    appEnv: env.VITE_APP_ENV ?? 'unknown',
    routerBasename,
    route: win?.location ? win.location.hash || win.location.pathname || '' : '',
    origin: win?.location?.origin ?? '',
    supabaseUrlHost: safeHost(supabaseUrl),
    hasSupabaseUrl: Boolean(supabaseUrl),
    hasSupabaseAnonKey: Boolean(supabaseAnonKey),
    viewEditais,
    dataSourceMode: 'supabase_live',
    queryMode: 'paged_select_all',
    localStorageKeysRelatedToEditais: listEditalLocalStorageKeys(win),
  };
}

/** Loga o diagnóstico no console (uso manual/dev). Nunca inclui segredos. */
export function logRuntimeDataSourceInfo(deps = {}) {
  const info = getRuntimeDataSourceInfo(deps);
  if (typeof console !== 'undefined') {
    console.info('[EditalFinder][RuntimeDataSource]', info);
  }
  return info;
}
