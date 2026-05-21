/**
 * Cliente do Web Worker do Radar — jobId, cancelamento, fallback, payload compacto.
 */
import { runRadarMatchAsync } from './radarMatchCore';
import { RADAR_USE_COMPACT_WORKER_PAYLOAD } from '../../constants/radarWorker';
import {
  compactRadarWorkerPayload,
  estimateRadarPayloadBytes,
} from './compactRadarWorkerPayload';
import { sanitizeRadarResults } from './radarResultShape';
import { radarPerfPreWorker, radarPerfWorkerEvent } from '../radarPerfLog';

let workerInstance = null;
let workerDisabled = false;
let workerInitError = null;

export function isRadarWorkerSupported() {
  if (workerDisabled) return false;
  if (typeof Worker === 'undefined') return false;
  if (typeof window === 'undefined') return false;
  return true;
}

function createWorker() {
  return new Worker(new URL('../../workers/radarMatchWorker.js', import.meta.url), {
    type: 'module',
  });
}

function getWorker() {
  if (!isRadarWorkerSupported()) return null;
  if (workerInstance) return workerInstance;
  try {
    workerInstance = createWorker();
    workerInstance.addEventListener('error', (e) => {
      if (import.meta.env?.DEV) {
        console.warn('[radar-perf] worker_error', { message: e?.message });
      }
      workerDisabled = true;
      workerInitError = e?.message || 'worker_error';
      try {
        workerInstance?.terminate();
      } catch {
        /* ignore */
      }
      workerInstance = null;
    });
    return workerInstance;
  } catch (e) {
    workerDisabled = true;
    workerInitError = e?.message || 'worker_construct_failed';
    return null;
  }
}

/**
 * @param {object} params
 * @param {string} params.jobId
 * @param {object} params.cliente
 * @param {object[]} params.editais
 * @param {object} params.options
 * @param {number} [params.chunkSize]
 * @param {number} [params.clickT0] performance.now() do clique (DEV)
 * @param {object} asyncOpts onProgress, onPartialResults, signal, onPreparingDone
 * @returns {Promise<{ rows, meta }|{ fallback: true, reason: string }>}
 */
export function runRadarMatchViaWorker(params, asyncOpts = {}) {
  const worker = getWorker();
  if (!worker) {
    return Promise.resolve({
      fallback: true,
      reason: workerInitError || 'worker_unavailable',
    });
  }

  const { jobId, cliente, editais, options, chunkSize = 72, clickT0 } = params;
  const { onProgress, onPartialResults, signal, onPreparingDone } = asyncOpts;
  const preT0 = typeof performance !== 'undefined' ? performance.now() : Date.now();

  if (import.meta.env?.DEV) {
    radarPerfPreWorker('before_worker_payload_build', {
      jobId,
      cliente_id: String(cliente?.id_cliente ?? cliente?.id ?? ''),
      since_click_ms: clickT0 != null ? Math.round(preT0 - clickT0) : undefined,
    });
  }

  const compact = RADAR_USE_COMPACT_WORKER_PAYLOAD
    ? compactRadarWorkerPayload(cliente, editais)
    : {
        cliente,
        editais: Array.isArray(editais) ? editais : [],
        inputCount: Array.isArray(editais) ? editais.length : 0,
        compactCount: Array.isArray(editais) ? editais.length : 0,
      };
  const payloadBuildMs =
    (typeof performance !== 'undefined' ? performance.now() : Date.now()) - preT0;

  if (import.meta.env?.DEV) {
    const bytes = estimateRadarPayloadBytes({
      cliente: compact.cliente,
      editais: compact.editais,
      options,
    });
    radarPerfPreWorker('after_worker_payload_build', {
      jobId,
      build_ms: Math.round(payloadBuildMs),
      worker_payload_size_items: compact.compactCount,
      payload_bytes_estimate: bytes,
      since_click_ms: clickT0 != null ? Math.round(performance.now() - clickT0) : undefined,
    });
  }

  onPreparingDone?.();

  return new Promise((resolve, reject) => {
    let settled = false;

    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      worker.removeEventListener('message', onMessage);
      fn(value);
    };

    const onMessage = (ev) => {
      const msg = ev.data || {};
      if (msg.jobId !== jobId) return;

      switch (msg.type) {
        case 'RADAR_PROGRESS':
          onProgress?.(msg.payload);
          break;
        case 'RADAR_PARTIAL_RESULTS': {
          const partialRows = msg.payload?.rows;
          if (!Array.isArray(partialRows)) {
            if (import.meta.env?.DEV) {
              radarPerfWorkerEvent('worker_invalid_payload', {
                jobId,
                type: msg.type,
              });
            }
            break;
          }
          const sanitizedPartial = sanitizeRadarResults(partialRows, {
            source: 'worker_partial',
          });
          onPartialResults?.({ ...msg.payload, rows: sanitizedPartial });
          if (import.meta.env?.DEV) {
            console.info('[radar-perf] worker_partial', {
              jobId,
              items_first_batch: sanitizedPartial.length,
              processed: msg.payload?.processed,
            });
          }
          break;
        }
        case 'RADAR_FULL_RESULTS': {
          const fullRows = msg.payload?.rows;
          if (!Array.isArray(fullRows)) {
            if (import.meta.env?.DEV) {
              radarPerfWorkerEvent('worker_invalid_payload', {
                jobId,
                type: msg.type,
              });
            }
            finish(resolve, { fallback: true, reason: 'worker_invalid_payload' });
            break;
          }
          const sanitizedFull = sanitizeRadarResults(fullRows, { source: 'worker_full' });
          if (import.meta.env?.DEV) {
            console.info('[radar-perf] worker_full', {
              jobId,
              items_total: sanitizedFull.length,
              main_thread_block_avoided: true,
            });
          }
          finish(resolve, {
            rows: sanitizedFull,
            meta: msg.payload?.meta ?? null,
            source: 'worker',
          });
          break;
        }
        case 'RADAR_ERROR':
          if (import.meta.env?.DEV) {
            console.warn('[radar-perf] worker_error', {
              jobId,
              message: msg.payload?.message,
            });
          }
          finish(reject, Object.assign(new Error(msg.payload?.message || 'Worker error'), {
            workerFailed: true,
          }));
          break;
        case 'RADAR_CANCELLED':
          finish(reject, Object.assign(new Error('Radar cancelado'), { name: 'AbortError' }));
          break;
        default:
          break;
      }
    };

    worker.addEventListener('message', onMessage);

    if (signal) {
      const onAbort = () => {
        cancelRadarWorkerJob(jobId);
      };
      if (signal.aborted) {
        onAbort();
        return;
      }
      signal.addEventListener?.('abort', onAbort, { once: true });
    }

    const postT0 = typeof performance !== 'undefined' ? performance.now() : Date.now();

    if (import.meta.env?.DEV) {
      radarPerfPreWorker('before_worker_postMessage', {
        jobId,
        worker_payload_size_items: compact.compactCount,
        since_click_ms: clickT0 != null ? Math.round(postT0 - clickT0) : undefined,
      });
      radarPerfPreWorker('time_until_worker_start', {
        jobId,
        ms: clickT0 != null ? Math.round(postT0 - clickT0) : Math.round(postT0 - preT0),
      });
    }

    worker.postMessage({
      type: 'START_RADAR_MATCH',
      payload: {
        jobId,
        cliente: compact.cliente ?? cliente,
        editais: compact.editais ?? editais,
        options,
        chunkSize,
        startedAt: Date.now(),
        compact: RADAR_USE_COMPACT_WORKER_PAYLOAD,
      },
    });

    const postMs =
      (typeof performance !== 'undefined' ? performance.now() : Date.now()) - postT0;

    if (import.meta.env?.DEV) {
      radarPerfPreWorker('after_worker_postMessage', {
        jobId,
        post_ms: Math.round(postMs),
        main_thread_pre_worker_ms: Math.round(
          (typeof performance !== 'undefined' ? performance.now() : Date.now()) - preT0,
        ),
      });
      radarPerfWorkerEvent('worker_start', {
        jobId,
        cliente_id: String(cliente?.id_cliente ?? cliente?.id ?? ''),
        items_total_input: compact.inputCount,
        worker_payload_size_items: compact.compactCount,
        main_thread_block_avoided: true,
      });
    }
  });
}

export function cancelRadarWorkerJob(jobId) {
  if (!workerInstance || !jobId) return;
  if (import.meta.env?.DEV) {
    console.info('[radar-perf] worker_cancel', { jobId });
  }
  try {
    workerInstance.postMessage({
      type: 'CANCEL_RADAR_MATCH',
      payload: { jobId },
    });
  } catch {
    /* ignore */
  }
}

/**
 * Fallback main thread — mesma lógica, `source: main_thread`.
 */
export async function runRadarMatchMainThread(cliente, editais, options, asyncOpts = {}) {
  const out = await runRadarMatchAsync(cliente, editais, options, {
    ...asyncOpts,
    yieldBetweenChunks: true,
  });
  return { ...out, source: 'main_thread' };
}

/** Ping opcional para health check DEV. */
export function pingRadarWorker() {
  const worker = getWorker();
  if (!worker) return Promise.resolve({ ok: false, reason: 'no_worker' });
  return new Promise((resolve) => {
    const jobId = `ping-${Date.now()}`;
    const t = setTimeout(() => resolve({ ok: false, reason: 'timeout' }), 2000);
    const handler = (ev) => {
      if (ev.data?.type === 'PONG') {
        clearTimeout(t);
        worker.removeEventListener('message', handler);
        resolve({ ok: true });
      }
    };
    worker.addEventListener('message', handler);
    worker.postMessage({ type: 'PING', payload: { jobId } });
  });
}
