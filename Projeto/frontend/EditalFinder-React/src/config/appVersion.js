/**
 * Versão exibida na UI — injetada no build a partir de src-tauri/tauri.conf.json (vite.config.js).
 */
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '0.1.0';

export const APP_VERSION_LABEL = `EditalFinder v${APP_VERSION}`;
