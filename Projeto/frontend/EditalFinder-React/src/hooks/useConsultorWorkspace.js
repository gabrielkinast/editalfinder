import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { dataService } from '../services/dataService';
import { useRadarMatches } from './useRadarMatches';
import {
  catalogFingerprintFromEditais,
  clienteFingerprintFromRow,
  optionsFingerprintFromMerged,
} from '../utils/radar/radarFingerprints';
import {
  isNonFatalRadarError,
  radarErrorKey,
} from '../utils/radar/radarErrorClassification';
import { summarizeMatchDeadlines } from '../utils/consultorDeadlineSummary';
import { derivePortfolioStatusMessage } from '../utils/consultor/derivePortfolioStatusMessage';
import { logConsultorWorkspace } from '../utils/consultorWorkspaceLog';
import { CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES } from '../utils/consultor/consultorWorkspaceConstants';

/** Mesmas opções padrão do Radar (sem encerrados/suspeitos/aproximados). */
export const CONSULTOR_RADAR_OPTIONS = {
  incluirEncerrados: false,
  incluirSuspeitos: false,
  incluirAproximados: false,
  cortePrincipal: 52,
  corteFallback: 30,
  limite: 3000,
  scoreMinimoExibir: 24,
};

export { CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES } from '../utils/consultor/consultorWorkspaceConstants';

/** @deprecated Use CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES */
export const CONSULTOR_TOP_MATCHES_LIMIT = CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES;

const RADAR_AUTO_RETRY_MS = 700;
const RADAR_CHUNK_SIZE = 72;

const radarOptionsMemo = CONSULTOR_RADAR_OPTIONS;
const optionsFingerprintMemo = optionsFingerprintFromMerged(CONSULTOR_RADAR_OPTIONS);

/**
 * Workspace do consultor — catálogo + useRadarMatches (read-only, sem duplicar score).
 * @param {object|null} cliente — linha normalizada de `cliente`
 * @param {{ enabled?: boolean }} [options]
 */
export function useConsultorWorkspace(cliente, options = {}) {
  const enabled = options.enabled !== false;
  const clienteId = cliente ? String(cliente.id_cliente ?? cliente.id ?? '') : '';

  const retryStateRef = useRef({
    clienteId: null,
    attemptedForErrorKey: null,
  });
  const radarTransitionCycleRef = useRef(0);
  const manualRetryInFlightRef = useRef(false);

  const [editais, setEditais] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [catalogError, setCatalogError] = useState(null);
  const [manualRetrying, setManualRetrying] = useState(false);

  useEffect(() => {
    if (!enabled) {
      setEditais([]);
      setCatalogError(null);
      setCatalogLoading(false);
      return undefined;
    }

    let cancelled = false;

    async function loadCatalog() {
      logConsultorWorkspace('radar_load_start', {});
      setCatalogLoading(true);
      setCatalogError(null);
      try {
        const eds = await dataService.getEditais();
        if (cancelled) return;
        setEditais(Array.isArray(eds) ? eds : []);
        logConsultorWorkspace('radar_load_success', {
          editais_count: Array.isArray(eds) ? eds.length : 0,
        });
      } catch (e) {
        if (cancelled) return;
        const msg = 'Não foi possível carregar o catálogo de oportunidades.';
        setCatalogError(msg);
        setEditais([]);
        logConsultorWorkspace('radar_load_error', {
          message: e?.message || String(e),
        });
      } finally {
        if (!cancelled) setCatalogLoading(false);
      }
    }

    loadCatalog();
    return () => {
      cancelled = true;
    };
  }, [enabled]);

  useEffect(() => {
    if (retryStateRef.current.clienteId !== clienteId) {
      retryStateRef.current = { clienteId, attemptedForErrorKey: null };
      manualRetryInFlightRef.current = false;
      setManualRetrying(false);
    }
  }, [clienteId]);

  const catalogFingerprint = useMemo(
    () => catalogFingerprintFromEditais(editais),
    [editais],
  );

  const clienteFingerprintKey = useMemo(() => {
    if (!cliente || !clienteId) return null;
    return clienteFingerprintFromRow(cliente);
  }, [cliente, clienteId]);

  const editaisCount = Array.isArray(editais) ? editais.length : 0;
  const catalogReady =
    enabled && !catalogLoading && !catalogError && Array.isArray(editais) && editaisCount > 0;

  const radarEnabled = Boolean(cliente) && Boolean(clienteId) && catalogReady;

  const radar = useRadarMatches({
    cliente,
    editais,
    options: radarOptionsMemo,
    chunkSize: RADAR_CHUNK_SIZE,
    enabled: radarEnabled,
    catalogFingerprint,
    clienteFingerprint: clienteFingerprintKey,
    optionsFingerprint: optionsFingerprintMemo,
  });

  const allMatches = useMemo(() => {
    const cid = clienteId;
    if (!cid || radar.resultsForClienteId !== cid) return [];
    return Array.isArray(radar.results) ? radar.results : [];
  }, [radar.results, radar.resultsForClienteId, clienteId]);

  const topMatches = useMemo(
    () => allMatches.slice(0, CONSULTOR_TOP_MATCHES_LIMIT),
    [allMatches],
  );

  const deadlineSummary = useMemo(
    () => summarizeMatchDeadlines(allMatches),
    [allMatches],
  );

  const safeAllMatches = Array.isArray(allMatches) ? allMatches : [];
  const safeTopMatches = Array.isArray(topMatches) ? topMatches : [];
  const totalMatches = safeAllMatches.length;

  const radarLoading = Boolean(
    radarEnabled && (radar.isCalculating || radar.isPreparing || radar.isSessionRefreshing),
  );
  const loading = catalogLoading || radarLoading;

  const topMatchesReady =
    Boolean(clienteId) &&
    (radar.resultsReady || (radar.hasPreviewResults && safeTopMatches.length > 0));

  const hasUsableResults =
    safeTopMatches.length > 0 ||
    safeAllMatches.length > 0 ||
    Number(totalMatches) > 0;

  const radarErrorRaw = radar.error || null;
  const radarErrorNonFatal = isNonFatalRadarError(radarErrorRaw);

  const shouldShowFatalRadarError =
    Boolean(clienteId) &&
    !catalogLoading &&
    !catalogError &&
    !loading &&
    !radarLoading &&
    !radar.isPartial &&
    !radar.hasPreviewResults &&
    !hasUsableResults &&
    Boolean(radarErrorRaw) &&
    !radarErrorNonFatal;

  const error = catalogError
    ? catalogError
    : shouldShowFatalRadarError
      ? 'radar_calc_failed'
      : null;

  const portfolioRadarWarning = useMemo(() => {
    if (!radarErrorRaw || !hasUsableResults || radarErrorNonFatal) return null;
    return 'Atualização automática falhou; exibindo última carteira calculada.';
  }, [radarErrorRaw, hasUsableResults, radarErrorNonFatal]);

  useEffect(() => {
    if (!import.meta.env?.DEV || !clienteId) return;
    radarTransitionCycleRef.current += 1;
    logConsultorWorkspace('radar_state_transition', {
      clienteId,
      editaisCount,
      loading,
      radarLoading,
      radarError: radarErrorRaw,
      hasTopMatches: safeTopMatches.length > 0,
      topMatchesCount: safeTopMatches.length,
      allMatchesCount: safeAllMatches.length,
      totalMatches,
      isPartial: Boolean(radar.isPartial),
      hasPreviewResults: Boolean(radar.hasPreviewResults),
      retryAttempted: Boolean(retryStateRef.current.attemptedForErrorKey),
      generationId: radar.reloadNonce,
      cycle: radarTransitionCycleRef.current,
      timestamp: Date.now(),
    });
  }, [
    clienteId,
    editaisCount,
    loading,
    radarLoading,
    radarErrorRaw,
    safeTopMatches.length,
    safeAllMatches.length,
    totalMatches,
    radar.isPartial,
    radar.hasPreviewResults,
    radar.reloadNonce,
  ]);

  useEffect(() => {
    if (!radarErrorRaw || !hasUsableResults) return;
    logConsultorWorkspace('radar_error_ignored_has_results', {
      id_cliente: clienteId,
      message: typeof radarErrorRaw === 'string' ? radarErrorRaw : String(radarErrorRaw),
      all_matches: safeAllMatches.length,
      top_matches: safeTopMatches.length,
    });
  }, [radarErrorRaw, hasUsableResults, clienteId, safeAllMatches.length, safeTopMatches.length]);

  useEffect(() => {
    if (!shouldShowFatalRadarError) return;
    logConsultorWorkspace('radar_render_error', {
      message: typeof radarErrorRaw === 'string' ? radarErrorRaw : String(radarErrorRaw),
      id_cliente: clienteId || null,
    });
  }, [shouldShowFatalRadarError, radarErrorRaw, clienteId]);

  useEffect(() => {
    if (!topMatchesReady || !clienteId) return;
    logConsultorWorkspace('top_matches_ready', {
      id_cliente: clienteId,
      total_matches: safeAllMatches.length,
      top_count: safeTopMatches.length,
      is_partial: radar.isPartial,
      has_preview: radar.hasPreviewResults,
    });
  }, [
    topMatchesReady,
    clienteId,
    safeAllMatches.length,
    safeTopMatches.length,
    radar.isPartial,
    radar.hasPreviewResults,
  ]);

  useEffect(() => {
    if (!clienteId || catalogLoading || loading) return;
    if (!radarErrorRaw || hasUsableResults || radarErrorNonFatal) return;
    if (!shouldShowFatalRadarError) return;
    if (!editaisCount) return;

    const errorKey = radarErrorKey(clienteId, radarErrorRaw);
    if (retryStateRef.current.attemptedForErrorKey === errorKey) return;

    retryStateRef.current.attemptedForErrorKey = errorKey;
    logConsultorWorkspace('radar_retry_triggered', {
      id_cliente: clienteId,
      error_key: errorKey,
      automatic: true,
    });

    const t = setTimeout(() => {
      try {
        radar.recalculate?.();
      } catch (e) {
        logConsultorWorkspace('radar_retry_failed', { message: e?.message || String(e) });
      }
    }, RADAR_AUTO_RETRY_MS);

    return () => clearTimeout(t);
  }, [
    clienteId,
    catalogLoading,
    loading,
    radarErrorRaw,
    hasUsableResults,
    radarErrorNonFatal,
    shouldShowFatalRadarError,
    editaisCount,
    radar.recalculate,
  ]);

  useEffect(() => {
    if (!manualRetrying && !manualRetryInFlightRef.current) return;
    if (!radarLoading && !loading) {
      manualRetryInFlightRef.current = false;
      setManualRetrying(false);
    }
  }, [manualRetrying, radarLoading, loading]);

  const handleRetryRadar = useCallback(() => {
    if (!clienteId || manualRetryInFlightRef.current) return;
    manualRetryInFlightRef.current = true;
    setManualRetrying(true);
    retryStateRef.current.attemptedForErrorKey = null;
    logConsultorWorkspace('radar_retry_triggered', {
      id_cliente: clienteId,
      manual: true,
    });
    try {
      radar.recalculate?.();
      logConsultorWorkspace('radar_retry_scheduled', { manual: true });
    } catch (e) {
      manualRetryInFlightRef.current = false;
      setManualRetrying(false);
      logConsultorWorkspace('radar_retry_failed', { message: e?.message || String(e), manual: true });
    }
  }, [clienteId, radar.recalculate]);

  const portfolioStatus = useMemo(
    () =>
      derivePortfolioStatusMessage({
        clienteId,
        catalogLoading,
        catalogError,
        editaisCount,
        radarLoading,
        topMatchesReady,
        isPartial: Boolean(radar.isPartial),
        hasPreviewResults: Boolean(radar.hasPreviewResults),
        resultsReady: Boolean(radar.resultsReady),
        totalMatches,
        topMatchesCount: safeTopMatches.length,
        selectedCount: 0,
      }),
    [
      clienteId,
      catalogLoading,
      catalogError,
      editaisCount,
      radarLoading,
      topMatchesReady,
      radar.isPartial,
      radar.hasPreviewResults,
      radar.resultsReady,
      totalMatches,
      safeTopMatches.length,
    ],
  );

  const loadingMessage =
    portfolioStatus?.kind === 'loading' ? portfolioStatus.message : null;

  return {
    loading,
    error,
    topMatches: safeTopMatches,
    totalMatches,
    isPartial: Boolean(radar.isPartial),
    hasPreviewResults: Boolean(radar.hasPreviewResults),
    deadlineSummary: deadlineSummary ?? null,
    topMatchesReady,
    allMatches: safeAllMatches,
    catalogLoading,
    catalogError,
    radarLoading,
    radarError: shouldShowFatalRadarError ? radarErrorRaw : null,
    portfolioRadarWarning,
    hasUsableResults,
    resultsReady: radar.resultsReady,
    progressPct: radar.progressPct,
    recalculate: handleRetryRadar,
    manualRetrying,
    loadingMessage,
    portfolioStatus,
    editaisCount,
    radarEnabled,
  };
}
