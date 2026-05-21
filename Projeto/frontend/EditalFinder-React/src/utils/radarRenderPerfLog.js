/**
 * Logs de renderização do Radar (somente DEV).
 */

const IS_DEV = import.meta.env?.DEV;

function nowMs() {
  return typeof performance !== 'undefined' ? performance.now() : Date.now();
}

export function radarRenderPerfEvent(label, extra = {}) {
  if (!IS_DEV) return;
  console.info(`[radar-render] ${label}`, extra);
}

/**
 * Marca início/fim de um ciclo de render da lista (após commit).
 */
export function radarRenderPerfCycle(meta, onEnd) {
  if (!IS_DEV) return;
  const t0 = nowMs();
  radarRenderPerfEvent('render_start', meta);
  requestAnimationFrame(() => {
    const renderMs = Math.round(nowMs() - t0);
    const endPayload = { ...meta, render_ms: renderMs };
    radarRenderPerfEvent('render_end', endPayload);
    onEnd?.(endPayload);
  });
}
