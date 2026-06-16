const hasWindow = typeof window !== 'undefined';
const hasNavigator = typeof navigator !== 'undefined';

/**
 * Detecta Web vs Desktop/Tauri (somente em runtime; seguro para SSR/testes).
 */
export function getRuntimeContext() {
  const isTauri = hasWindow && Boolean(window.__TAURI_INTERNALS__ || window.__TAURI__);

  return {
    runtime: isTauri ? 'desktop_tauri' : 'web_browser',
    is_desktop: isTauri,
    is_web: !isTauri,
    user_agent: hasNavigator ? navigator.userAgent?.slice(0, 500) : null,
    platform: hasNavigator ? navigator.platform : null,
    language: hasNavigator ? navigator.language : null,
  };
}

export function getRuntimeDisplayLabel(ctx) {
  const resolved = ctx ?? getRuntimeContext();
  return resolved.is_desktop ? 'Desktop/EXE' : 'Navegador';
}
