/**
 * Logs de performance do Radar (somente DEV).
 * Não altera regras de score — apenas observabilidade.
 */

const IS_DEV = import.meta.env?.DEV;

const sessions = new Map();

function nowMs() {
  return typeof performance !== 'undefined' ? performance.now() : Date.now();
}

export function radarPerfStart(sessionId, meta = {}) {
  if (!IS_DEV) return null;
  const t0 = nowMs();
  const entry = {
    sessionId,
    t0,
    meta: { ...meta },
    marks: [],
  };
  sessions.set(sessionId, entry);
  console.info('[radar-perf] click_start', {
    sessionId,
    clienteId: meta.clienteId ?? null,
    clienteNome: meta.clienteNome ?? null,
    editaisCount: meta.editaisCount ?? null,
    clickT0: meta.clickT0 ?? null,
    query: 'in-memory (worker); 0 Supabase no clique',
  });
  return sessionId;
}

export function radarPerfMark(sessionId, label, extra = {}) {
  if (!IS_DEV || !sessionId) return;
  const entry = sessions.get(sessionId);
  if (!entry) return;
  const ms = Math.round(nowMs() - entry.t0);
  const row = { label, ms, ...extra };
  entry.marks.push(row);
  console.info(`[radar-perf] ${label}`, row);
}

export function radarPerfEnd(sessionId, summary = {}) {
  if (!IS_DEV || !sessionId) return;
  const entry = sessions.get(sessionId);
  if (!entry) return;
  const totalMs = Math.round(nowMs() - entry.t0);
  const payload = {
    sessionId,
    totalMs,
    cacheHit: !!summary.cacheHit,
    cliente_id: summary.clienteId ?? entry.meta.clienteId,
    clienteId: summary.clienteId ?? entry.meta.clienteId,
    resultCount: summary.resultCount ?? null,
    items_total: summary.items_total ?? summary.resultCount ?? null,
    items_first_batch: summary.items_first_batch ?? null,
    first_results_ms: summary.first_results_ms ?? null,
    full_results_ms: summary.full_results_ms ?? summary.fetchCalcMs ?? null,
    editaisAnalyzed: summary.editaisAnalyzed ?? null,
    ...summary,
  };
  console.info('[radar-perf] complete', payload);
  sessions.delete(sessionId);
}

export function radarPerfCacheEvent({
  clienteId,
  hit,
  cacheSize,
  resultCount,
  ms,
  partial,
  source,
}) {
  if (!IS_DEV) return;
  const label = hit ? (partial ? 'cache_hit_partial' : 'cache_hit') : 'cache_miss';
  console.info(`[radar-perf] ${label}`, {
    cliente_id: clienteId,
    clienteId,
    hit,
    cacheSize,
    resultCount,
    ms: ms != null ? Math.round(ms) : undefined,
    partial: !!partial,
    source: source ?? undefined,
  });
}

/** Eventos do Web Worker (Fase 0.6). */
export function radarPerfWorkerEvent(label, extra = {}) {
  if (!IS_DEV) return;
  console.info(`[radar-perf] ${label}`, {
    main_thread_block_avoided: extra.main_thread_block_avoided ?? label.startsWith('worker_'),
    ...extra,
  });
}

/** Métricas na main thread antes do worker (clique → postMessage). */
export function radarPerfPreWorker(label, extra = {}) {
  if (!IS_DEV) return;
  console.info(`[radar-perf] ${label}`, extra);
}

export function radarPerfClickReceived(clickT0, extra = {}) {
  if (!IS_DEV || clickT0 == null) return;
  const ms = Math.round(nowMs() - clickT0);
  radarPerfPreWorker('click_received_ms', { ms, ...extra });
}

export function radarPerfSelectClienteState(clickT0, extra = {}) {
  if (!IS_DEV || clickT0 == null) return;
  const ms = Math.round(nowMs() - clickT0);
  radarPerfPreWorker('selected_cliente_set', { ms, ...extra });
  radarPerfPreWorker('select_cliente_state_ms', { ms, ...extra });
}
