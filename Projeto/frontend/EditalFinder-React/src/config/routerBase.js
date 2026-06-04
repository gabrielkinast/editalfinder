/**
 * Basename do React Router.
 * Web (GitHub Pages): /editalfinder
 * Desktop (Tauri): vazio — definido em build via vite.config.js (TAURI_ENV_PLATFORM).
 */
export const ROUTER_BASENAME = import.meta.env.VITE_ROUTER_BASENAME ?? '/editalfinder';

export const IS_TAURI_BUILD =
  ROUTER_BASENAME === '' || import.meta.env.VITE_TAURI === '1';
