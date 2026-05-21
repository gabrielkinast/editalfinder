import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { recomendarEditaisAsync, buildRadarCacheKey } from '../services/matchService';
import {
  cancelRadarWorkerJob,
  isRadarWorkerSupported,
  runRadarMatchViaWorker,
} from '../utils/radar/radarWorkerClient';
import {
  invalidateRadarSessionCacheForCliente,
  loadRadarSessionCache,
  saveRadarSessionCache,
  sessionEntryToMemoryPayload,
} from '../utils/radar/radarPersistentCache';
import { sanitizeRadarResults } from '../utils/radar/radarResultShape';
import {
  RADAR_PREFILTER_VERSION,
  RADAR_USE_CATALOG_PREFILTER,
} from '../constants/radarPrefilter';
import {
  logRadarCatalogNoise,
  prefilterRadarCatalog,
} from '../utils/radar/radarCatalogPrefilter';
import {
  radarPerfCacheEvent,
  radarPerfEnd,
  radarPerfMark,
  radarPerfPreWorker,
  radarPerfWorkerEvent,
} from '../utils/radarPerfLog';

const radarMatchCache = new Map();
const MAX_CACHE_ENTRIES = 24;

function cachePut(key, payload) {
  while (radarMatchCache.size >= MAX_CACHE_ENTRIES) {
    const first = radarMatchCache.keys().next().value;
    radarMatchCache.delete(first);
  }
  radarMatchCache.set(key, payload);
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

function radarOptsKey(options) {
  return JSON.stringify({
    incluirSuspeitos: !!options?.incluirSuspeitos,
    incluirEncerrados: !!options?.incluirEncerrados,
    incluirAproximados: !!options?.incluirAproximados,
    cortePrincipal: options?.cortePrincipal,
    corteFallback: options?.corteFallback,
    limite: options?.limite,
    scoreMinimoExibir: options?.scoreMinimoExibir,
  });
}

/** Assinatura leve para invalidar cache se a lista mudar (sem depender só de primeiro/último). */
function editaisListSignature(eds) {
  const list = Array.isArray(eds) ? eds : [];
  if (list.length === 0) return '0';
  let h = list.length ^ 0;
  const stride = Math.max(1, Math.floor(list.length / 80));
  for (let i = 0; i < list.length; i += stride) {
    const id = list[i]?.id;
    const s = String(id ?? '');
    h = Math.imul(h ^ s.length, 0x9e3779b9) ^ (s.charCodeAt(0) | 0);
  }
  return `${list.length}|${list[0]?.id ?? ''}|${list[list.length - 1]?.id ?? ''}|${h}`;
}

function nowMs() {
  return typeof performance !== 'undefined' ? performance.now() : Date.now();
}

function applyFullCachePayload({
  payload,
  clienteId,
  eds,
  setResults,
  setResultsForClienteId,
  setMeta,
  setIsCalculating,
  setIsPartial,
  setError,
  setLastCacheHit,
  setProgress,
  setComputeSource,
  sourceLabel,
}) {
  const t0 = nowMs();
  setResults(
    sanitizeRadarResults(payload.rows, { source: sourceLabel ?? payload.source ?? 'cache' }),
  );
  setResultsForClienteId(clienteId);
  setMeta(payload.meta ?? null);
  setIsCalculating(false);
  setIsPartial(false);
  setError(null);
  setLastCacheHit(true);
  const m = payload.meta;
  setProgress({
    processed: m?.afterPreFilter ?? 0,
    total: m?.afterPreFilter ?? 0,
    originalTotal: m?.totalIn ?? eds.length,
    excludedPreScore: m?.excludedPreScore ?? 0,
  });
  setComputeSource(sourceLabel);
  return nowMs() - t0;
}

/**
 * Radar assíncrono em lotes + cache + cancelamento + renderização progressiva (top 20).
 * @param {object} params
 * @param {import('react').MutableRefObject<string|null>} [params.perfSessionRef] ref com id de sessão DEV (click)
 */
export function useRadarMatches({
  cliente,
  editais,
  options = {},
  chunkSize = 72,
  enabled = true,
  perfSessionRef = null,
  perfClickT0Ref = null,
  catalogFingerprint: catalogFingerprintProp = null,
  clienteFingerprint: clienteFingerprintProp = null,
  optionsFingerprint: optionsFingerprintProp = null,
}) {
  const [results, setResults] = useState([]);
  const [resultsForClienteId, setResultsForClienteId] = useState('');
  const [isCalculating, setIsCalculating] = useState(false);
  const [isPartial, setIsPartial] = useState(false);
  const [lastCacheHit, setLastCacheHit] = useState(null);
  const [computeSource, setComputeSource] = useState(null);
  const [isSessionRefreshing, setIsSessionRefreshing] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);
  const [progress, setProgress] = useState({
    processed: 0,
    total: 0,
    originalTotal: 0,
    excludedPreScore: 0,
  });
  const [error, setError] = useState(null);
  const [meta, setMeta] = useState(null);
  const [prefilterStats, setPrefilterStats] = useState(null);
  const generationRef = useRef(0);
  const abortRef = useRef(null);
  const workerJobIdRef = useRef(null);
  const resultsSnapshotRef = useRef({ resultsForClienteId: '', count: 0 });
  const [reloadNonce, setReloadNonce] = useState(0);

  resultsSnapshotRef.current = {
    resultsForClienteId,
    count: results.length,
  };

  const optKey = useMemo(() => radarOptsKey(options), [options]);

  const mergedOptions = useMemo(() => mergeRadarOptions(options), [optKey]);

  const editaisSig = useMemo(
    () => editaisListSignature(editais),
    [editais],
  );

  const clienteId = cliente ? String(cliente.id_cliente ?? cliente.id ?? '') : '';

  const recalculate = useCallback(() => {
    if (clienteId) invalidateRadarSessionCacheForCliente(clienteId);
    setIsSessionRefreshing(false);
    setReloadNonce((n) => n + 1);
  }, [clienteId]);

  useEffect(() => {
    if (!enabled || !cliente) {
      generationRef.current += 1;
      abortRef.current?.abort();
      setResults([]);
      setResultsForClienteId('');
      setIsCalculating(false);
      setIsPartial(false);
      setIsSessionRefreshing(false);
      setIsPreparing(false);
      setLastCacheHit(null);
      setComputeSource(null);
      setProgress({
        processed: 0,
        total: 0,
        originalTotal: 0,
        excludedPreScore: 0,
      });
      setError(null);
      setMeta(null);
      setPrefilterStats(null);
      return;
    }

    const edsCatalog = Array.isArray(editais) ? editais : [];
    const headId = edsCatalog[0]?.id;
    const tailId = edsCatalog[edsCatalog.length - 1]?.id;
    const perfId = perfSessionRef?.current ?? null;
    const clickT0 = perfClickT0Ref?.current ?? null;
    const effectT0 = nowMs();

    if (perfId && clickT0 != null) {
      radarPerfPreWorker('time_until_effect_ms', {
        cliente_id: clienteId,
        ms: Math.round(effectT0 - clickT0),
      });
    }

    const sessionFp = {
      catalogFingerprint: catalogFingerprintProp,
      clienteFingerprint: clienteFingerprintProp,
      optionsFingerprint: optionsFingerprintProp,
    };

    const cacheKey = [
      buildRadarCacheKey(cliente, edsCatalog.length, headId, tailId, mergedOptions),
      editaisSig,
      `pf:${RADAR_USE_CATALOG_PREFILTER ? RADAR_PREFILTER_VERSION : 'off'}`,
      `v${reloadNonce}`,
    ].join('::');

    const resolveEdsForWorker = () => {
      if (!RADAR_USE_CATALOG_PREFILTER) {
        const stats = {
          catalog_total: edsCatalog.length,
          after_existing_filters: edsCatalog.length,
          sent_to_worker: edsCatalog.length,
          removed_expired: 0,
          removed_invalid_type: 0,
          removed_missing_link: 0,
          removed_duplicate: 0,
          removed_low_quality: 0,
          removed_generic_title: 0,
        };
        setPrefilterStats(stats);
        return { eds: edsCatalog, stats, rejectedSample: [] };
      }
      const pre = prefilterRadarCatalog(edsCatalog, {
        includeExpired: mergedOptions.incluirEncerrados,
        incluirEncerrados: mergedOptions.incluirEncerrados,
      });
      setPrefilterStats(pre.stats);
      logRadarCatalogNoise(pre.stats, pre.rejectedSample);
      if (perfId) {
        radarPerfMark(perfId, 'catalog_prefilter', {
          clienteId,
          sent_to_worker: pre.stats.sent_to_worker,
          catalog_total: pre.stats.catalog_total,
        });
      }
      return { eds: pre.items, stats: pre.stats, rejectedSample: pre.rejectedSample };
    };

    const cached = radarMatchCache.get(cacheKey);
    if (cached && cached.partial === false) {
      const ms = applyFullCachePayload({
        payload: cached,
        clienteId,
        eds: edsCatalog,
        setResults,
        setResultsForClienteId,
        setMeta,
        setIsCalculating,
        setIsPartial,
        setError,
        setLastCacheHit,
        setProgress,
        setComputeSource,
        sourceLabel: cached.source ?? 'cache',
      });
      if (cached.meta?.prefilter) setPrefilterStats(cached.meta.prefilter);
      radarPerfCacheEvent({
        clienteId,
        hit: true,
        cacheSize: radarMatchCache.size,
        resultCount: cached.rows?.length ?? 0,
        ms,
        partial: false,
        source: cached.source ?? 'cache',
      });
      if (perfId) {
        radarPerfMark(perfId, 'cache_hit', {
          clienteId,
          resultCount: cached.rows?.length ?? 0,
          cacheSize: radarMatchCache.size,
          partial: false,
        });
        radarPerfEnd(perfId, {
          cacheHit: true,
          clienteId,
          resultCount: cached.rows?.length ?? 0,
          editaisAnalyzed: cached.meta?.totalIn ?? edsCatalog.length,
          items_total: cached.rows?.length ?? 0,
          transformMs: Math.round(ms),
        });
        perfSessionRef.current = null;
      }
      return;
    }

    let sessionBootstrap = false;
    let sessionStaleSoon = false;

    if (!cached || cached.partial !== false) {
      if (perfId) {
        radarPerfMark(perfId, 'before_session_cache_lookup', { clienteId });
      }
      const sessionLookupT0 = nowMs();
      const sessionLoad = loadRadarSessionCache({
        clienteId,
        cliente,
        editais: edsCatalog,
        options: mergedOptions,
        ...sessionFp,
      });
      if (perfId) {
        radarPerfMark(perfId, 'after_session_cache_lookup', {
          clienteId,
          lookup_ms: Math.round(nowMs() - sessionLookupT0),
          hit: !!sessionLoad.hit,
        });
      }

      if (sessionLoad.hit && sessionLoad.entry) {
        const memPayload = sessionEntryToMemoryPayload(sessionLoad.entry);
        cachePut(cacheKey, memPayload);
        const ms = applyFullCachePayload({
          payload: memPayload,
          clienteId,
          eds: edsCatalog,
          setResults,
          setResultsForClienteId,
          setMeta,
          setIsCalculating,
          setIsPartial,
          setError,
          setLastCacheHit,
          setProgress,
          setComputeSource,
          sourceLabel: 'session_cache',
        });
        if (memPayload.meta?.prefilter) setPrefilterStats(memPayload.meta.prefilter);
        radarPerfCacheEvent({
          clienteId,
          hit: true,
          cacheSize: radarMatchCache.size,
          resultCount: memPayload.rows?.length ?? 0,
          ms,
          partial: false,
          source: 'session_cache',
        });
        if (perfId) {
          radarPerfMark(perfId, 'session_cache_hit', {
            clienteId,
            resultCount: memPayload.rows?.length ?? 0,
            stale_soon: !!sessionLoad.staleSoon,
          });
        }

        if (!sessionLoad.staleSoon) {
          if (perfId) {
            radarPerfEnd(perfId, {
              cacheHit: true,
              clienteId,
              resultCount: memPayload.rows?.length ?? 0,
              editaisAnalyzed: memPayload.meta?.totalIn ?? edsCatalog.length,
              items_total: memPayload.rows?.length ?? 0,
              transformMs: Math.round(ms),
              source: 'session_cache',
            });
            perfSessionRef.current = null;
          }
          return;
        }

        sessionBootstrap = true;
        sessionStaleSoon = true;
        setIsSessionRefreshing(true);
      }
    }

    const partialCacheOnly = cached?.partial === true && !sessionBootstrap;
    if (partialCacheOnly) {
      const partialCached = sanitizeRadarResults(cached.rows, { source: 'cache_partial' });
      setResults(partialCached);
      setResultsForClienteId(clienteId);
      setIsPartial(true);
      setMeta(cached.meta ?? null);
      setLastCacheHit(true);
      setComputeSource(cached.source ?? 'cache');
      radarPerfCacheEvent({
        clienteId,
        hit: true,
        cacheSize: radarMatchCache.size,
        resultCount: cached.rows?.length ?? 0,
        partial: true,
        source: cached.source ?? 'cache',
      });
      if (perfId) {
        radarPerfMark(perfId, 'cache_hit_partial', {
          clienteId,
          items_first_batch: cached.rows?.length ?? 0,
          partial: true,
        });
      }
    } else if (!sessionBootstrap) {
      setLastCacheHit(false);
      radarPerfCacheEvent({
        clienteId,
        hit: false,
        cacheSize: radarMatchCache.size,
        partial: false,
      });
      if (perfId) {
        radarPerfMark(perfId, 'cache_miss', { clienteId, editaisCount: edsCatalog.length });
      }
    }

    abortRef.current?.abort();
    if (workerJobIdRef.current) {
      cancelRadarWorkerJob(workerJobIdRef.current);
      workerJobIdRef.current = null;
    }
    const ac = new AbortController();
    abortRef.current = ac;
    const gen = ++generationRef.current;
    const jobId = `radar-${gen}-${clienteId}-${Date.now()}`;
    workerJobIdRef.current = jobId;

    const snap = resultsSnapshotRef.current;
    const sameClientStale =
      !partialCacheOnly &&
      !sessionBootstrap &&
      snap.resultsForClienteId === clienteId &&
      snap.count > 0;

    setIsCalculating(true);
    setIsPreparing(true);
    setError(null);
    if (!partialCacheOnly && !sameClientStale && !sessionBootstrap) {
      setResults([]);
      setResultsForClienteId('');
      setIsPartial(false);
    }
    if (!partialCacheOnly && !sessionBootstrap) {
      setMeta(null);
    }
    setProgress({
      processed: 0,
      total: 0,
      originalTotal: edsCatalog.length,
      excludedPreScore: 0,
    });

    const calcT0 = nowMs();
    let firstResultsMs = partialCacheOnly ? 0 : null;
    let itemsFirstBatch = partialCacheOnly ? (cached?.rows?.length ?? 0) : null;
    const useWorker = isRadarWorkerSupported();

    const onProgressCb = (p) => {
      if (generationRef.current !== gen) return;
      setProgress({
        processed: p.processed,
        total: p.total,
        originalTotal: p.originalTotal,
        excludedPreScore: p.excludedPreScore ?? 0,
      });
    };

    const onPartialCb = (p, sourceLabel) => {
      if (generationRef.current !== gen) return;
      if (sessionBootstrap) return;
      if (firstResultsMs == null) {
        firstResultsMs = Math.round(nowMs() - calcT0);
      }
      const itemsFirst = p.rows?.length ?? 0;
      itemsFirstBatch = itemsFirst;
      const partialRows = sanitizeRadarResults(p.rows, { source: sourceLabel });
      setResults(partialRows);
      setResultsForClienteId(clienteId);
      setIsPartial(true);
      setComputeSource(sourceLabel);
      cachePut(cacheKey, {
        rows: partialRows,
        meta: {
          totalIn: p.originalTotal,
          afterPreFilter: p.total,
          excludedPreScore: p.excludedPreScore,
          partialPreview: true,
        },
        partial: true,
        source: sourceLabel,
        clienteId,
        generatedAt: Date.now(),
      });
      const perfExtra = {
        cliente_id: clienteId,
        jobId,
        first_results_ms: firstResultsMs,
        worker_first_results_ms: sourceLabel === 'worker' ? firstResultsMs : undefined,
        items_first_batch: itemsFirst,
        processed: p.processed,
        total: p.total,
        cache_hit: false,
        cache_miss: !partialCacheOnly,
        main_thread_block_avoided: sourceLabel === 'worker',
      };
      if (import.meta.env?.DEV) {
        console.info(
          sourceLabel === 'worker' ? '[radar-perf] worker_partial' : '[radar-perf] first_results',
          perfExtra,
        );
      }
      if (perfId) {
        radarPerfMark(perfId, sourceLabel === 'worker' ? 'worker_partial' : 'first_results', {
          cliente_id: clienteId,
          jobId,
          first_results_ms: firstResultsMs,
          items_first_batch: itemsFirst,
          main_thread_block_avoided: sourceLabel === 'worker',
        });
      }
    };

    const runMainThreadFallback = async (reason) => {
      if (import.meta.env?.DEV) {
        radarPerfWorkerEvent('worker_fallback', {
          jobId,
          cliente_id: clienteId,
          worker_fallback: true,
          reason: reason ?? 'unavailable',
          main_thread_block_avoided: false,
        });
      }
      if (perfId) {
        radarPerfMark(perfId, 'worker_fallback', { jobId, cliente_id: clienteId, reason });
      }
      const out = await recomendarEditaisAsync(cliente, edsWorker, mergedOptions, {
        chunkSize,
        signal: ac.signal,
        onProgress: onProgressCb,
        onPartialResults: (p) => onPartialCb(p, 'main_thread'),
      });
      return { ...out, source: 'main_thread' };
    };

    const runComputation = async () => {
      if (generationRef.current !== gen) return;
      const { eds: edsWorker, stats: pfStats } = resolveEdsForWorker();
      setProgress((prev) => ({
        ...prev,
        originalTotal: pfStats?.sent_to_worker ?? edsWorker.length,
      }));
      const preWorkerT0 = nowMs();
      if (clickT0 != null) {
        radarPerfPreWorker('main_thread_pre_worker_ms', {
          cliente_id: clienteId,
          ms: Math.round(preWorkerT0 - clickT0),
        });
      }

      try {
        let out;
        let source = 'main_thread';

        if (useWorker) {
          if (perfId) {
            radarPerfMark(perfId, 'before_worker_payload_build', {
              jobId,
              cliente_id: clienteId,
            });
          }

          try {
            const workerOut = await runRadarMatchViaWorker(
              {
                jobId,
                cliente,
                editais: edsWorker,
                options: mergedOptions,
                chunkSize,
                clickT0,
              },
              {
                signal: ac.signal,
                onProgress: onProgressCb,
                onPartialResults: (p) => onPartialCb(p, 'worker'),
                onPreparingDone: () => {
                  if (generationRef.current === gen) setIsPreparing(false);
                },
              },
            );

            if (workerOut?.fallback) {
              out = await runMainThreadFallback(workerOut.reason);
              source = out.source;
            } else {
              out = workerOut;
              source = 'worker';
            }
          } catch (workerErr) {
            if (workerErr?.name === 'AbortError') throw workerErr;
            if (import.meta.env?.DEV) {
              radarPerfWorkerEvent('worker_error', {
                jobId,
                message: workerErr?.message,
                worker_fallback: true,
              });
            }
            out = await runMainThreadFallback(workerErr?.message || 'worker_threw');
            source = out.source;
          }
        } else {
          setIsPreparing(false);
          out = await runMainThreadFallback('worker_unsupported');
          source = out.source;
        }

        if (generationRef.current !== gen) return;
        setIsPreparing(false);

        const fullResultsMs = Math.round(nowMs() - calcT0);
        setComputeSource(source);
        const fullRows = sanitizeRadarResults(out?.rows, { source });
        const payload = {
          rows: fullRows,
          meta: out.meta,
          partial: false,
          source,
          clienteId,
          generatedAt: Date.now(),
        };
        cachePut(cacheKey, payload);
        saveRadarSessionCache({
          clienteId,
          cliente,
          editais: eds,
          options: mergedOptions,
          rows: fullRows,
          meta: out.meta,
          source,
          ...sessionFp,
        });
        setResults(fullRows);
        setResultsForClienteId(clienteId);
        setMeta(metaOut);
        setIsPartial(false);
        setIsCalculating(false);
        setIsSessionRefreshing(false);

        const itemsTotal = out.rows?.length ?? 0;
        if (import.meta.env?.DEV) {
          const m = out.meta;
          const fullLabel = source === 'worker' ? 'worker_full' : 'full_results';
          console.info(`[radar-perf] ${fullLabel}`, {
            cliente_id: clienteId,
            jobId,
            full_results_ms: fullResultsMs,
            worker_full_results_ms: source === 'worker' ? fullResultsMs : undefined,
            first_results_ms: firstResultsMs,
            items_first_batch: itemsFirstBatch,
            items_total: itemsTotal,
            cache_hit: partialCacheOnly || sessionBootstrap,
            cache_miss: !partialCacheOnly && !sessionBootstrap,
            catalogo: m?.totalIn,
            source,
            session_refresh: sessionStaleSoon,
            main_thread_block_avoided: source === 'worker',
            worker_fallback: source === 'main_thread' && useWorker,
          });
          console.info('[radar] calc_complete', {
            clienteId,
            fullResultsMs,
            firstResultsMs,
            resultCount: itemsTotal,
          });
        }

        if (perfId) {
          radarPerfMark(perfId, source === 'worker' ? 'worker_full' : 'full_results', {
            cliente_id: clienteId,
            jobId,
            full_results_ms: fullResultsMs,
            items_total: itemsTotal,
            source,
            session_refresh: sessionStaleSoon,
            main_thread_block_avoided: source === 'worker',
          });
          radarPerfEnd(perfId, {
            cacheHit: partialCacheOnly || sessionBootstrap,
            clienteId,
            resultCount: itemsTotal,
            editaisAnalyzed: metaOut.totalIn ?? edsCatalog.length,
            first_results_ms: firstResultsMs,
            full_results_ms: fullResultsMs,
            worker_first_results_ms: source === 'worker' ? firstResultsMs : undefined,
            worker_full_results_ms: source === 'worker' ? fullResultsMs : undefined,
            items_first_batch: itemsFirstBatch,
            items_total: itemsTotal,
            fetchCalcMs: fullResultsMs,
            source,
            jobId,
            session_refresh: sessionStaleSoon,
            main_thread_block_avoided: source === 'worker',
          });
          perfSessionRef.current = null;
        }
        if (generationRef.current === gen) {
          workerJobIdRef.current = null;
        }
      } catch (e) {
        if (e?.name === 'AbortError') {
          if (generationRef.current === gen) {
            workerJobIdRef.current = null;
            setIsPreparing(false);
            if (sessionBootstrap) setIsSessionRefreshing(false);
          }
          if (import.meta.env?.DEV) {
            radarPerfWorkerEvent('worker_cancel', { jobId, cliente_id: clienteId });
          }
          return;
        }
        if (generationRef.current !== gen) return;
        workerJobIdRef.current = null;
        setIsSessionRefreshing(false);
        setIsPreparing(false);
        console.error('[useRadarMatches]', e);
        setError(e?.message || 'Não foi possível calcular o radar.');
        if (!sessionBootstrap) {
          setResults([]);
          setResultsForClienteId('');
          setIsPartial(false);
        }
        setIsCalculating(false);
        if (perfId) {
          radarPerfEnd(perfId, { cacheHit: false, clienteId, error: e?.message });
          perfSessionRef.current = null;
        }
      }
    };

    const rafId = requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        runComputation();
      });
    });

    return () => {
      cancelAnimationFrame(rafId);
      ac.abort();
      if (workerJobIdRef.current) {
        cancelRadarWorkerJob(workerJobIdRef.current);
        workerJobIdRef.current = null;
      }
    };
  }, [
    enabled,
    cliente,
    clienteId,
    editaisSig,
    optKey,
    reloadNonce,
    chunkSize,
  ]);

  const pct =
    progress.total > 0 ? Math.round((100 * progress.processed) / progress.total) : 0;

  const resultsReady =
    Boolean(clienteId) && resultsForClienteId === clienteId && !isCalculating && !isPartial;

  const hasPreviewResults =
    Boolean(clienteId) &&
    resultsForClienteId === clienteId &&
    isPartial &&
    results.length > 0;

  return {
    results,
    resultsForClienteId,
    resultsReady,
    hasPreviewResults,
    isPartial,
    isCalculating,
    lastCacheHit,
    progress,
    progressPct: pct,
    error,
    meta,
    recalculate,
    reloadNonce,
    computeSource,
    isSessionRefreshing,
    isPreparing,
    prefilterStats,
  };
}
