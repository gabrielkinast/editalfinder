/**
 * Basename do React Router.
 * Web (GitHub Pages): /editalfinder
 * Desktop (Tauri): vazio — definido em build via vite.config.js (TAURI_ENV_PLATFORM).
 */
const viteEnv = typeof import.meta !== 'undefined' ? import.meta.env : undefined;

export const ROUTER_BASENAME = viteEnv?.VITE_ROUTER_BASENAME ?? '/editalfinder';

export const IS_TAURI_BUILD =
  ROUTER_BASENAME === '' || viteEnv?.VITE_TAURI === '1';
