import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { recomendarEditaisAsync, buildRadarCacheKey } from '../services/matchService';

const radarMatchCache = new Map();
const MAX_CACHE_ENTRIES = 12;

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

/**
 * Radar assíncrono em lotes + cache + cancelamento ao trocar cliente/opções.
 */
export function useRadarMatches({
  cliente,
  editais,
  options = {},
  chunkSize = 72,
  enabled = true,
}) {
  const [results, setResults] = useState([]);
  const [isCalculating, setIsCalculating] = useState(false);
  const [progress, setProgress] = useState({
    processed: 0,
    total: 0,
    originalTotal: 0,
    excludedPreScore: 0,
  });
  const [error, setError] = useState(null);
  const [meta, setMeta] = useState(null);
  const generationRef = useRef(0);
  const abortRef = useRef(null);
  const [reloadNonce, setReloadNonce] = useState(0);

  const optKey = useMemo(() => radarOptsKey(options), [options]);

  const mergedOptions = useMemo(() => mergeRadarOptions(options), [optKey]);

  const editaisSig = useMemo(
    () => editaisListSignature(editais),
    [editais],
  );

  const clienteId = cliente ? String(cliente.id_cliente ?? cliente.id ?? '') : '';

  const recalculate = useCallback(() => {
    setReloadNonce((n) => n + 1);
  }, []);

  useEffect(() => {
    if (!enabled || !cliente) {
      generationRef.current += 1;
      abortRef.current?.abort();
      setResults([]);
      setIsCalculating(false);
      setProgress({
        processed: 0,
        total: 0,
        originalTotal: 0,
        excludedPreScore: 0,
      });
      setError(null);
      setMeta(null);
      return;
    }

    const eds = Array.isArray(editais) ? editais : [];
    const headId = eds[0]?.id;
    const tailId = eds[eds.length - 1]?.id;

    const cacheKey = [
      buildRadarCacheKey(cliente, eds.length, headId, tailId, mergedOptions),
      editaisSig,
      `v${reloadNonce}`,
    ].join('::');

    if (radarMatchCache.has(cacheKey)) {
      const cached = radarMatchCache.get(cacheKey);
      setResults(cached.rows);
      setMeta(cached.meta ?? null);
      setIsCalculating(false);
      setError(null);
      const m = cached.meta;
      setProgress({
        processed: m?.afterPreFilter ?? 0,
        total: m?.afterPreFilter ?? 0,
        originalTotal: m?.totalIn ?? eds.length,
        excludedPreScore: m?.excludedPreScore ?? 0,
      });
      return;
    }

    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    const gen = ++generationRef.current;

    setIsCalculating(true);
    setError(null);
    setResults([]);
    setMeta(null);
    setProgress({
      processed: 0,
      total: 0,
      originalTotal: eds.length,
      excludedPreScore: 0,
    });

    (async () => {
      try {
        if (import.meta.env?.DEV) console.time('radar-calc');
        const out = await recomendarEditaisAsync(cliente, eds, mergedOptions, {
          chunkSize,
          signal: ac.signal,
          onProgress: (p) => {
            if (generationRef.current !== gen) return;
            setProgress({
              processed: p.processed,
              total: p.total,
              originalTotal: p.originalTotal,
              excludedPreScore: p.excludedPreScore ?? 0,
            });
          },
        });
        if (generationRef.current !== gen) return;
        if (import.meta.env?.DEV) {
          console.timeEnd('radar-calc');
          const m = out.meta;
          if (m) {
            console.info(
              '[radar] catálogo',
              m.totalIn,
              'após pré-filtro',
              m.afterPreFilter,
              'exclusões rápidas',
              m.excludedPreScore,
            );
          }
        }
        const payload = { rows: out.rows, meta: out.meta };
        cachePut(cacheKey, payload);
        setResults(out.rows);
        setMeta(out.meta ?? null);
        setIsCalculating(false);
      } catch (e) {
        if (e?.name === 'AbortError') return;
        if (generationRef.current !== gen) return;
        console.error('[useRadarMatches]', e);
        setError(e?.message || 'Não foi possível calcular o radar.');
        setResults([]);
        setIsCalculating(false);
      }
    })();

    return () => {
      ac.abort();
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

  return {
    results,
    isCalculating,
    progress,
    progressPct: pct,
    error,
    meta,
    recalculate,
    reloadNonce,
  };
}
