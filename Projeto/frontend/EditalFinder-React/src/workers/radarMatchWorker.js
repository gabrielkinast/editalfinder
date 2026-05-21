/**
 * Web Worker — cálculo Radar off main thread.
 * Mensagens: START_RADAR_MATCH, CANCEL_RADAR_MATCH.
 */
import { runRadarMatchAsync } from '../utils/radar/radarMatchCore';

let activeJobId = null;
let cancelRequested = false;

function post(type, jobId, payload = {}) {
  self.postMessage({ type, jobId, payload, at: Date.now() });
}

self.onmessage = async (ev) => {
  const { type, payload } = ev.data || {};
  if (!type || !payload) return;

  const { jobId } = payload;

  if (type === 'CANCEL_RADAR_MATCH') {
    if (jobId === activeJobId) {
      cancelRequested = true;
      post('RADAR_CANCELLED', jobId, { reason: 'cancel_requested' });
    }
    return;
  }

  if (type === 'PING') {
    post('PONG', jobId || 'ping', { ok: true });
    return;
  }

  if (type !== 'START_RADAR_MATCH') return;

  activeJobId = jobId;
  cancelRequested = false;

  const {
    cliente,
    editais,
    options = {},
    chunkSize,
    startedAt,
  } = payload;

  const signal = {
    get aborted() {
      return cancelRequested || activeJobId !== jobId;
    },
  };

  try {
    const out = await runRadarMatchAsync(cliente, editais, options, {
      chunkSize,
      signal,
      yieldBetweenChunks: false,
      shouldContinue: () => activeJobId === jobId && !cancelRequested,
      onProgress: (p) => {
        if (activeJobId !== jobId) return;
        post('RADAR_PROGRESS', jobId, p);
      },
      onPartialResults: (p) => {
        if (activeJobId !== jobId) return;
        post('RADAR_PARTIAL_RESULTS', jobId, {
          ...p,
          partial: true,
          startedAt,
        });
      },
    });

    if (activeJobId !== jobId || cancelRequested) {
      post('RADAR_CANCELLED', jobId, { reason: 'stale_or_cancelled' });
      return;
    }

    post('RADAR_FULL_RESULTS', jobId, {
      rows: out.rows,
      meta: out.meta,
      partial: false,
      startedAt,
    });
  } catch (e) {
    if (activeJobId !== jobId) return;
    if (e?.name === 'AbortError' || cancelRequested) {
      post('RADAR_CANCELLED', jobId, { reason: e?.message || 'aborted' });
      return;
    }
    post('RADAR_ERROR', jobId, {
      message: e?.message || String(e),
      name: e?.name,
    });
  } finally {
    if (activeJobId === jobId) {
      activeJobId = null;
      cancelRequested = false;
    }
  }
};
