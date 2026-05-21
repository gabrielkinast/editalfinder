/**
 * Núcleo puro do cálculo Radar (cliente × editais).
 * Sem DOM/React — utilizável na main thread e em Web Worker.
 * Regras de score: `utils/radarMatch.js` (inalteradas).
 */
import {
  toRadarCliente,
  diasAtePrazo,
  filtrarEditaisPreScoreRadar,
  avaliarEditalRadarLinha,
  finalizarRankingOportunidadesRadar,
  radarMatchToCardPayload,
} from '../radarMatch';

export const DEFAULT_RADAR_ASYNC_CHUNK = 72;
export const RADAR_FIRST_BATCH_MIN_PROCESSED = 72;
export const RADAR_FIRST_BATCH_TOP_N = 20;

function yieldToEventLoop() {
  return new Promise((r) => setTimeout(r, 0));
}

/** Ordenação final igual a `recomendarEditais` (expirados depois). */
export function ordenarLinhasRadarUi(rows, nowMs = Date.now()) {
  return [...rows].sort((a, b) => {
    const expA = a.expirado ? 1 : 0;
    const expB = b.expirado ? 1 : 0;
    if (expA !== expB) return expA - expB;
    if (b.score !== a.score) return b.score - a.score;
    const diaA = diasAtePrazo(a.edital.dataLimite);
    const diaB = diasAtePrazo(b.edital.dataLimite);
    const tA = new Date(a.edital.dataLimite || 0).getTime();
    const tB = new Date(b.edital.dataLimite || 0).getTime();
    const vA = diaA != null && diaA >= 0 ? tA - nowMs : Number.POSITIVE_INFINITY;
    const vB = diaB != null && diaB >= 0 ? tB - nowMs : Number.POSITIVE_INFINITY;
    return vA - vB;
  });
}

function enriquecerLinhasRadarOrdenadas(linhasRadar, nowMs = Date.now()) {
  const enriquecidas = linhasRadar
    .map((row) => {
      if (!row?.edital || !row?.radar_match) return null;
      const p = radarMatchToCardPayload(row.edital, row.radar_match);
      if (p.excluido) return null;
      return { edital: row.edital, ...p };
    })
    .filter(Boolean);
  return ordenarLinhasRadarUi(enriquecidas, nowMs);
}

function buildRadarPartialPreviewRows(avaliadas, merged, topN = RADAR_FIRST_BATCH_TOP_N) {
  const linhas = finalizarRankingOportunidadesRadar(avaliadas, merged);
  return enriquecerLinhasRadarOrdenadas(linhas, Date.now()).slice(0, topN);
}

function mergeRadarOptions(options = {}) {
  return {
    incluirSuspeitos: options.incluirSuspeitos ?? false,
    incluirEncerrados: options.incluirEncerrados ?? false,
    incluirAproximados: options.incluirAproximados ?? false,
    cortePrincipal: options.cortePrincipal ?? 52,
    corteFallback: options.corteFallback ?? 30,
    limite: options.limite ?? 3000,
    scoreMinimoExibir:
      options.scoreMinimoExibir ?? (options.incluirAproximados ? 12 : 24),
    ...options,
  };
}

/**
 * Pipeline assíncrono em chunks + prévia após primeiro lote.
 * @param {object} cliente
 * @param {object[]} editais
 * @param {object} options
 * @param {object} asyncOpts
 * @param {number} [asyncOpts.chunkSize]
 * @param {{ aborted: boolean }} [asyncOpts.signal]
 * @param {function} [asyncOpts.onProgress]
 * @param {function} [asyncOpts.onPartialResults]
 * @param {function} [asyncOpts.shouldContinue] retorna false para cancelar (ex.: jobId stale)
 * @param {boolean} [asyncOpts.yieldBetweenChunks] default true na main thread; worker pode usar false
 */
export async function runRadarMatchAsync(cliente, editais, options = {}, asyncOpts = {}) {
  const chunkSize = asyncOpts.chunkSize ?? DEFAULT_RADAR_ASYNC_CHUNK;
  const signal = asyncOpts.signal;
  const onProgress = asyncOpts.onProgress;
  const onPartialResults = asyncOpts.onPartialResults;
  const shouldContinue = asyncOpts.shouldContinue ?? (() => true);
  const yieldBetweenChunks = asyncOpts.yieldBetweenChunks !== false;
  const firstBatchMin =
    asyncOpts.firstBatchMinProcessed ?? RADAR_FIRST_BATCH_MIN_PROCESSED;
  const firstBatchTopN = asyncOpts.firstBatchTopN ?? RADAR_FIRST_BATCH_TOP_N;

  const eds = Array.isArray(editais) ? editais : [];
  const merged = mergeRadarOptions(options);

  const { passed, totalIn, excludedPreScore } = filtrarEditaisPreScoreRadar(eds, merged);
  const radarCliente = toRadarCliente(cliente);
  const scoreMin = merged.scoreMinimoExibir ?? (merged.incluirAproximados ? 15 : 24);

  const avaliadas = [];
  const n = passed.length;
  let firstBatchEmitted = false;

  const checkAbort = () => {
    if (signal?.aborted) {
      const err = new DOMException('Radar cancelado', 'AbortError');
      throw err;
    }
    if (!shouldContinue()) {
      const err = new DOMException('Radar cancelado', 'AbortError');
      throw err;
    }
  };

  for (let i = 0; i < n; i += chunkSize) {
    checkAbort();
    const slice = passed.slice(i, i + chunkSize);
    for (let j = 0; j < slice.length; j++) {
      avaliadas.push(avaliarEditalRadarLinha(radarCliente, slice[j], merged, scoreMin));
    }
    const processed = Math.min(i + chunkSize, n);
    onProgress?.({
      processed,
      total: n,
      originalTotal: totalIn,
      excludedPreScore,
    });

    const readyForFirstBatch =
      !firstBatchEmitted &&
      (processed >= Math.min(firstBatchMin, n) || processed === n);

    if (readyForFirstBatch && onPartialResults) {
      const previewRows = buildRadarPartialPreviewRows(avaliadas, merged, firstBatchTopN);
      firstBatchEmitted = true;
      onPartialResults({
        rows: previewRows,
        partial: true,
        processed,
        total: n,
        originalTotal: totalIn,
        excludedPreScore,
        itemsInBatch: previewRows.length,
      });
    }

    if (yieldBetweenChunks && i + chunkSize < n) {
      await yieldToEventLoop();
    }
  }

  checkAbort();
  const linhas = finalizarRankingOportunidadesRadar(avaliadas, merged);
  const now = Date.now();
  const rows = enriquecerLinhasRadarOrdenadas(linhas, now);

  return {
    rows,
    meta: {
      totalIn,
      afterPreFilter: n,
      excludedPreScore,
      chunkSize,
      progressiveFirstBatch: firstBatchEmitted,
    },
  };
}
