/**
 * Tema (Fase 1) — preferência persistida e aplicação via classe no <html>.
 *
 * Preferência: 'light' | 'dark' | 'system'
 * Classe aplicada: 'theme-light' | 'theme-dark'
 *
 * Regras:
 * - Nunca depende de backend/Supabase.
 * - Não assume que `window` exista (SSG/SSR-safe).
 */

const STORAGE_KEY = 'editalfinder.theme';

/** @typedef {'light'|'dark'|'system'} ThemePreference */
/** @typedef {'light'|'dark'} ResolvedTheme */

let _mql = null;
let _mqlListener = null;

function hasWindow() {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
}

function safeMatchMedia() {
  if (!hasWindow()) return null;
  if (typeof window.matchMedia !== 'function') return null;
  try {
    return window.matchMedia('(prefers-color-scheme: dark)');
  } catch {
    return null;
  }
}

export function getSavedThemePreference() {
  if (!hasWindow()) return 'system';
  try {
    const raw = String(window.localStorage.getItem(STORAGE_KEY) || '').trim().toLowerCase();
    if (raw === 'light' || raw === 'dark' || raw === 'system') return raw;
  } catch {
    /* ignore */
  }
  return 'system';
}

export function saveThemePreference(pref) {
  if (!hasWindow()) return;
  try {
    window.localStorage.setItem(STORAGE_KEY, pref);
  } catch {
    /* ignore */
  }
}

export function resolveThemePreference(pref) {
  /** @type {ThemePreference} */
  const p = pref === 'light' || pref === 'dark' || pref === 'system' ? pref : 'system';
  if (p === 'light' || p === 'dark') return p;
  const mql = safeMatchMedia();
  return mql?.matches ? 'dark' : 'light';
}

function applyResolvedTheme(resolved) {
  if (!hasWindow()) return;
  const root = document.documentElement;
  if (!root) return;
  root.classList.remove('theme-light', 'theme-dark');
  root.classList.add(resolved === 'dark' ? 'theme-dark' : 'theme-light');
}

function detachSystemListener() {
  if (!_mql || !_mqlListener) return;
  try {
    _mql.removeEventListener?.('change', _mqlListener);
  } catch {
    /* ignore */
  }
  _mql = null;
  _mqlListener = null;
}

function attachSystemListener(onChange) {
  const mql = safeMatchMedia();
  if (!mql) return;
  _mql = mql;
  _mqlListener = () => onChange();
  try {
    mql.addEventListener?.('change', _mqlListener);
  } catch {
    /* ignore */
  }
}

/**
 * Aplica a preferência e configura/limpa listener do tema do sistema.
 * @param {ThemePreference} pref
 */
export function applyTheme(pref) {
  const resolved = resolveThemePreference(pref);
  applyResolvedTheme(resolved);

  // Listener só é necessário quando prefer = system
  detachSystemListener();
  if (pref === 'system') {
    attachSystemListener(() => applyResolvedTheme(resolveThemePreference('system')));
  }
}

export function clearThemeSystemListener() {
  detachSystemListener();
}

