import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from './usePermissions';
import { dataService } from '../services/dataService';
import {
  buildDashboardAggregations,
  countRecentByDate,
} from '../utils/dashboard/dashboardAggregations';
import {
  auditDashboardDataQuality,
  logDashboardDataQualityAudit,
} from '../utils/dashboard/auditDashboardDataQuality';
import { buildDashboardPriorities } from '../utils/dashboard/buildDashboardPriorities';
import {
  loadDashboardScopePreference,
  saveDashboardScopePreference,
} from '../utils/dashboard/dashboardScopeStorage';
import { hasBriefingContent } from '../utils/cliente/clientBriefingSignals';
import { APP_FEEDBACK_PENDING_KEY } from '../constants/appFeedbackConfig';
import { handleAppActionError } from '../utils/errors/reportableActionError';

const EMPTY_CHARTS = {
  editaisByFonte: [],
  editaisByTipo: [],
  editaisByPrazo: [],
  totalAnalyzed: 0,
  prazoDataQualityWarning: null,
  tipoChartTitle: 'Editais por modalidade',
  tipoChartSubtitle: '',
  fonteChartSubtitle: '',
};

function loadPendingFeedbackCount() {
  try {
    const raw = localStorage.getItem(APP_FEEDBACK_PENDING_KEY);
    if (!raw) return 0;
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.length : 0;
  } catch {
    return 0;
  }
}

function buildRadarSummary(clients = []) {
  let withBriefing = 0;
  let withProfile = 0;
  for (const c of clients) {
    if (hasBriefingContent(c)) withBriefing += 1;
    const nome = String(c.nome || c.razao_social || '').trim();
    if (nome.length >= 3) withProfile += 1;
  }
  return {
    total: clients.length,
    withBriefing,
    withProfile,
  };
}

/**
 * Dados agregados para a home /dashboard.
 */
export function useDashboardData() {
  const { user } = useAuth();
  const permissions = usePermissions();

  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState({});
  const [editais, setEditais] = useState([]);
  const [noticias, setNoticias] = useState([]);
  const [pesquisas, setPesquisas] = useState([]);
  const [clients, setClients] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [scopeFilter, setScopeFilterState] = useState(loadDashboardScopePreference);

  const setScopeFilter = useCallback((scope) => {
    setScopeFilterState(scope);
    saveDashboardScopePreference(scope);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    const nextErrors = {};

    const tasks = [
      { key: 'editais', run: () => dataService.getEditais() },
      { key: 'noticias', run: () => dataService.getNoticias() },
      { key: 'pesquisas', run: () => dataService.getPesquisas() },
    ];

    if (permissions.canViewCadastros) {
      tasks.push({ key: 'clients', run: () => dataService.getClients({ user }) });
    }

    const results = await Promise.allSettled(tasks.map((t) => t.run()));

    results.forEach((result, i) => {
      const key = tasks[i].key;
      if (result.status === 'fulfilled') {
        const data = Array.isArray(result.value) ? result.value : [];
        if (key === 'editais') setEditais(data);
        if (key === 'noticias') setNoticias(data);
        if (key === 'pesquisas') setPesquisas(data);
        if (key === 'clients') setClients(data);
      } else {
        nextErrors[key] = result.reason;
        handleAppActionError({
          error: result.reason,
          origem: 'dashboard',
          pagina: 'Dashboard',
          acao: `load_${key}`,
          componente: 'useDashboardData',
          userMessage: null,
        });
        if (key === 'editais') setEditais([]);
        if (key === 'noticias') setNoticias([]);
        if (key === 'pesquisas') setPesquisas([]);
        if (key === 'clients') setClients([]);
      }
    });

    setErrors(nextErrors);
    setLastUpdated(new Date());
    setLoading(false);
  }, [permissions.canViewCadastros, user]);

  useEffect(() => {
    load();
  }, [load, refreshKey]);

  const dataQualityAudit = useMemo(() => {
    const audit = auditDashboardDataQuality({ editais, noticias, pesquisas });
    logDashboardDataQualityAudit(audit);
    return audit;
  }, [editais, noticias, pesquisas]);

  const aggregation = useMemo(
    () => buildDashboardAggregations(editais, scopeFilter),
    [editais, scopeFilter],
  );

  const recentNoticias = useMemo(
    () =>
      [...noticias]
        .sort((a, b) => {
          const ta = new Date(a.data_publicacao || a.publicado_em || 0).getTime();
          const tb = new Date(b.data_publicacao || b.publicado_em || 0).getTime();
          return tb - ta;
        })
        .slice(0, 20),
    [noticias],
  );

  const recentPesquisas = useMemo(
    () =>
      [...pesquisas]
        .sort((a, b) => {
          const ta = new Date(a.data_publicacao || a.publicado_em || 0).getTime();
          const tb = new Date(b.data_publicacao || b.publicado_em || 0).getTime();
          return tb - ta;
        })
        .slice(0, 20),
    [pesquisas],
  );

  const radarSummary = useMemo(() => buildRadarSummary(clients), [clients]);

  const metrics = useMemo(
    () => ({
      ...aggregation.metrics,
      totalNoticiasRecentes: errors.noticias ? 0 : countRecentByDate(noticias, 30),
      totalPesquisasRecentes: errors.pesquisas ? 0 : countRecentByDate(pesquisas, 30),
      totalClients: errors.clients ? 0 : radarSummary.total,
      reportedProblemsPending: loadPendingFeedbackCount(),
    }),
    [aggregation.metrics, noticias, pesquisas, radarSummary.total, errors],
  );

  const charts = useMemo(() => aggregation.charts || EMPTY_CHARTS, [aggregation.charts]);

  const priorities = useMemo(
    () =>
      buildDashboardPriorities({
        metrics,
        expiringEditais: aggregation.expiringEditais,
        pendingReports: metrics.reportedProblemsPending,
        radarSummary,
        canViewCadastros: permissions.canViewCadastros,
        scopeFilter,
      }),
    [metrics, aggregation.expiringEditais, radarSummary, permissions.canViewCadastros, scopeFilter],
  );

  const refresh = useCallback(() => {
    setRefreshKey((k) => k + 1);
  }, []);

  const error = errors.editais && !editais.length ? errors.editais : null;

  return {
    loading,
    error,
    errors,
    metrics,
    priorities,
    recentEditais: aggregation.recentEditais,
    expiringEditais: aggregation.expiringEditais,
    recentNoticias,
    recentPesquisas,
    charts,
    radarSummary,
    clientsSummary: radarSummary,
    lastUpdated,
    refresh,
    truncatedEditais: aggregation.truncated,
    scopeFilter,
    setScopeFilter,
    dataQualityAudit,
  };
}
