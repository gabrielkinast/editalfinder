import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import ConsultorClienteList from '../components/consultor/ConsultorClienteList';
import ConsultorRecommendedSection from '../components/consultor/ConsultorRecommendedSection';
import ConsultorAllOpportunitiesModal from '../components/consultor/ConsultorAllOpportunitiesModal';
import ConsultorWorkspaceErrorBoundary from '../components/consultor/ConsultorWorkspaceErrorBoundary';
import { CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL } from '../utils/consultor/consultorWorkspaceConstants';
import { derivePortfolioStatusMessage } from '../utils/consultor/derivePortfolioStatusMessage';
import { resolveAnalyzedOpportunityCount } from '../utils/consultor/resolveAnalyzedOpportunityCount';
import ConsultorPrecadastroCard from '../components/consultor/ConsultorPrecadastroCard';
import ConsultorClientProfileCard from '../components/consultor/ConsultorClientProfileCard';
import ConsultorProfileBriefingCallout from '../components/consultor/ConsultorProfileBriefingCallout';
import ConsultorWorkflowSteps from '../components/consultor/ConsultorWorkflowSteps';
import ConsultorTriageReportModal from '../components/consultor/ConsultorTriageReportModal';
import ConsultorExportMenu from '../components/consultor/ConsultorExportMenu';
import ConsultorClientBriefingModal from '../components/consultor/ConsultorClientBriefingModal';
import ConsultorActionPlanCard from '../components/consultor/ConsultorActionPlanCard';
import ConsultorTrackedOpportunitiesCard from '../components/consultor/ConsultorTrackedOpportunitiesCard';
import ConsultorClientTimelineCard from '../components/consultor/ConsultorClientTimelineCard';
import ConsultorClientStatusBanner from '../components/consultor/ConsultorClientStatusBanner';
import { buildConsultorTrackedOpportunities } from '../utils/consultor/buildConsultorTrackedOpportunities';
import {
  deriveConsultorClientStatus,
  deriveConsultorClientStatusLight,
} from '../utils/consultor/deriveConsultorClientStatus';
import { useEditalFavorites } from '../hooks/useEditalFavorites';
import { persistTrackedSnapshots } from '../utils/consultor/consultorTrackedOpportunitiesStorage';
import {
  appendClientTimelineEvent,
  TIMELINE_EVENT_TYPES,
} from '../utils/consultor/consultorClientTimeline';
import { calculateClientProfileCompleteness } from '../utils/cliente/calculateClientProfileCompleteness';
import { applyBriefingToFormState } from '../utils/cliente/clientBriefingState';
import { hasBriefingContent } from '../utils/cliente/clientBriefingSignals';
import { logClienteBriefing } from '../utils/cliente/clienteBriefingLog';
import ClientForm from '../components/admin/ClientForm';
import {
  clientFormStateFromCliente,
  clientPayloadFromFormState,
  mergeClientWritePayload,
} from '../utils/cliente/clientePerfilConsultivo';
import ProjetoPrecadastroForm from '../components/admin/ProjetoPrecadastroForm';
import Modal from '../components/ui/Modal';
import { useAuth } from '../contexts/AuthContext';
import { useConsultorWorkspace } from '../hooks/useConsultorWorkspace';
import { usePermissions } from '../hooks/usePermissions';
import { dataService } from '../services/dataService';
import {
  attachOwnerToClientPayload,
  canEditClient,
  canViewClient,
  filterClientsForUser,
  isAdminUser,
  sanitizeClientWritePayload,
  sessionUserId,
} from '../utils/permissions';
import { logConsultorWorkspace } from '../utils/consultorWorkspaceLog';
import { getClientPrecadSummary } from '../utils/precadastro/getClientPrecadSummary';
import { readPreProjetoContext } from '../utils/precadastro/openPreProjetoFromOpportunity';
import { openPreProjetoFromOpportunities } from '../utils/precadastro/openPreProjetoFromOpportunities';
import { fingerprintPrecadContext } from '../utils/precadastroProjetoInitialState';
import {
  MAX_PREPROJECT_OPPORTUNITIES,
  normalizeSelectedOpportunity,
  summarizeSelectionForBar,
} from '../utils/consultor/opportunitySelection';

function idClienteKey(c, idx = 0) {
  const v = c?.id_cliente ?? c?.id;
  return v !== undefined && v !== null ? String(v) : `idx-${idx}`;
}

function clientePorIdNaLista(clientes, idOuKey) {
  if (idOuKey == null || clientes?.length === 0) return null;
  const want = String(idOuKey);
  return (
    clientes.find((c, i) => idClienteKey(c, i) === want) ??
    clientes.find((c) => String(c?.id_cliente ?? c?.id ?? '') === want) ??
    null
  );
}

function PlaceholderCard({ title, description }) {
  return (
    <article className="consultor-placeholder-card">
      <h3 className="consultor-placeholder-title">{title}</h3>
      <p className="consultor-placeholder-desc">{description}</p>
    </article>
  );
}

function ConsultorWorkspaceContent() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const permissions = usePermissions();

  const [clientes, setClientes] = useState([]);
  const [clienteIdSelecionado, setClienteIdSelecionado] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [isClientModalOpen, setIsClientModalOpen] = useState(false);
  const [editingCliente, setEditingCliente] = useState(null);

  const [isPrecadModalOpen, setIsPrecadModalOpen] = useState(false);
  const [precadEdital, setPrecadEdital] = useState(null);
  const [precadRadar, setPrecadRadar] = useState(null);
  const [precadInitialEnvelope, setPrecadInitialEnvelope] = useState(null);
  const [precadOportunidades, setPrecadOportunidades] = useState(null);
  const [precadModalKey, setPrecadModalKey] = useState('geral');
  const [precadSummaryTick, setPrecadSummaryTick] = useState(0);
  const [selectedOpportunityRows, setSelectedOpportunityRows] = useState(() => new Map());
  const [isAllOpportunitiesOpen, setIsAllOpportunitiesOpen] = useState(false);
  const [isTriageReportOpen, setIsTriageReportOpen] = useState(false);
  const [isBriefingOpen, setIsBriefingOpen] = useState(false);
  const [briefingSaving, setBriefingSaving] = useState(false);
  const [trackedRefreshTick, setTrackedRefreshTick] = useState(0);
  const [timelineRefreshTick, setTimelineRefreshTick] = useState(0);

  const favHook = useEditalFavorites();

  const clienteSelecionado = useMemo(
    () => clientePorIdNaLista(clientes, clienteIdSelecionado),
    [clientes, clienteIdSelecionado],
  );

  const workspace = useConsultorWorkspace(clienteSelecionado, {
    enabled: permissions.canViewCadastros,
  });

  const safeAllMatches = useMemo(
    () => (Array.isArray(workspace?.allMatches) ? workspace.allMatches : []),
    [workspace?.allMatches],
  );
  const safeTopMatches = useMemo(
    () => (Array.isArray(workspace?.topMatches) ? workspace.topMatches : []),
    [workspace?.topMatches],
  );

  useEffect(() => {
    if (!import.meta.env?.DEV) return;
    logConsultorWorkspace('workspace_render_start', {
      has_cliente: Boolean(clienteSelecionado),
      all_matches_shape: {
        isArray: Array.isArray(workspace?.allMatches),
        length: safeAllMatches.length,
      },
      top_matches_shape: {
        isArray: Array.isArray(workspace?.topMatches),
        length: safeTopMatches.length,
      },
      selected_map_shape: {
        isMap: selectedOpportunityRows instanceof Map,
        size: selectedOpportunityRows instanceof Map ? selectedOpportunityRows.size : 0,
      },
    });
  }, [
    clienteSelecionado,
    safeAllMatches.length,
    safeTopMatches.length,
    selectedOpportunityRows,
    workspace?.allMatches,
    workspace?.topMatches,
  ]);

  const precadSummary = useMemo(() => {
    if (!clienteSelecionado) return null;
    void precadSummaryTick;
    return getClientPrecadSummary(clienteSelecionado, { useSessionContext: true });
  }, [clienteSelecionado, precadSummaryTick]);

  const selectedOpportunityKeys = useMemo(
    () => new Set(selectedOpportunityRows.keys()),
    [selectedOpportunityRows],
  );

  const selectedOpportunitiesNormalized = useMemo(
    () => [...selectedOpportunityRows.values()].map(normalizeSelectedOpportunity),
    [selectedOpportunityRows],
  );

  const selectionBarSummary = useMemo(
    () => summarizeSelectionForBar(selectedOpportunitiesNormalized),
    [selectedOpportunitiesNormalized],
  );

  const selectedRowsForCsv = useMemo(
    () =>
      selectedOpportunitiesNormalized
        .map((o) => o.row)
        .filter((row) => row && typeof row === 'object'),
    [selectedOpportunitiesNormalized],
  );

  const analyzedOpportunityCount = useMemo(
    () =>
      resolveAnalyzedOpportunityCount({
        totalMatches: workspace?.totalMatches,
        allMatches: safeAllMatches,
      }),
    [workspace?.totalMatches, safeAllMatches],
  );

  const portfolioStatus = useMemo(
    () =>
      derivePortfolioStatusMessage({
        clienteId: clienteSelecionado
          ? String(clienteSelecionado.id_cliente ?? clienteSelecionado.id ?? '')
          : '',
        catalogLoading: workspace.catalogLoading,
        catalogError: workspace.catalogError,
        editaisCount: workspace.editaisCount ?? 0,
        radarLoading: workspace.radarLoading,
        topMatchesReady: workspace.topMatchesReady,
        isPartial: workspace.isPartial,
        hasPreviewResults: workspace.hasPreviewResults,
        resultsReady: workspace.resultsReady,
        totalMatches: analyzedOpportunityCount,
        topMatchesCount: safeTopMatches.length,
        selectedCount: selectedOpportunityKeys.size,
      }),
    [
      clienteSelecionado,
      workspace.catalogLoading,
      workspace.catalogError,
      workspace.editaisCount,
      workspace.radarLoading,
      workspace.topMatchesReady,
      workspace.isPartial,
      workspace.hasPreviewResults,
      workspace.resultsReady,
      analyzedOpportunityCount,
      safeTopMatches.length,
      selectedOpportunityKeys.size,
    ],
  );

  const clientProfileScore = useMemo(() => {
    if (!clienteSelecionado) return 0;
    return calculateClientProfileCompleteness(clienteSelecionado).score;
  }, [clienteSelecionado]);

  const clientHasBriefing = useMemo(
    () => hasBriefingContent(clienteSelecionado),
    [clienteSelecionado],
  );

  const showBriefingCallout = Boolean(clienteSelecionado && clientProfileScore < 50);

  const recordTimeline = useCallback(
    (partial) => {
      const cid = clienteSelecionado?.id_cliente ?? clienteSelecionado?.id;
      if (cid == null) return;
      appendClientTimelineEvent(cid, partial);
      setTimelineRefreshTick((t) => t + 1);
    },
    [clienteSelecionado],
  );

  const getClientStatus = useCallback(
    (c) => {
      if (!c) return null;
      return deriveConsultorClientStatusLight(c);
    },
    [clientes, precadSummaryTick, trackedRefreshTick, timelineRefreshTick],
  );

  const trackedForSelectedStatus = useMemo(() => {
    if (!clienteSelecionado) return [];
    return buildConsultorTrackedOpportunities({
      cliente: clienteSelecionado,
      selectedOpportunities: selectedOpportunitiesNormalized,
      allMatches: safeAllMatches,
      remoteFavorites: favHook.favorites,
    });
  }, [
    clienteSelecionado,
    selectedOpportunitiesNormalized,
    safeAllMatches,
    favHook.favorites,
    trackedRefreshTick,
  ]);

  const selectedClientStatus = useMemo(() => {
    if (!clienteSelecionado) return null;
    return deriveConsultorClientStatus({
      cliente: clienteSelecionado,
      profileCompleteness: clientProfileScore,
      hasBriefing: clientHasBriefing,
      topMatches: safeTopMatches,
      selectedOpportunities: selectedOpportunitiesNormalized,
      precadSummary,
      trackedOpportunities: trackedForSelectedStatus,
      logContext: {
        mode: 'panel',
        id_cliente: clienteSelecionado.id_cliente ?? clienteSelecionado.id,
      },
    });
  }, [
    clienteSelecionado,
    clientProfileScore,
    clientHasBriefing,
    safeTopMatches,
    selectedOpportunitiesNormalized,
    precadSummary,
    trackedForSelectedStatus,
  ]);

  const radarReadyForWorkflow = useMemo(() => {
    if (workspace.error === 'radar_calc_failed') return false;
    return Boolean(workspace.topMatchesReady);
  }, [workspace.error, workspace.topMatchesReady]);

  useEffect(() => {
    setSelectedOpportunityRows(new Map());
  }, [clienteIdSelecionado]);

  const loadClientes = useCallback(async () => {
    logConsultorWorkspace('load_clients_start');
    setLoading(true);
    setLoadError(null);
    try {
      const rows = await dataService.getClients({ user });
      const allowed = filterClientsForUser(user, rows);
      const ativos = allowed.filter((c) => String(c.status || '').toLowerCase() === 'ativo');
      setClientes(ativos);
      logConsultorWorkspace('load_clients_success', { count: ativos.length });
      return ativos;
    } catch (e) {
      setLoadError('Não foi possível carregar os clientes. Tente novamente.');
      logConsultorWorkspace('load_clients_error', { message: e?.message || String(e) });
      return [];
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (!permissions.canViewCadastros) return undefined;
    let cancelled = false;
    (async () => {
      await loadClientes();
      if (cancelled) return;
    })();
    return () => {
      cancelled = true;
    };
  }, [permissions.canViewCadastros, loadClientes]);

  const selecionarClienteNaLista = useCallback((c) => {
    const id = idClienteKey(c);
    setClienteIdSelecionado(id);
    logConsultorWorkspace('select_cliente', {
      id_cliente: c?.id_cliente ?? null,
      nome_empresa: c?.nome_empresa ? String(c.nome_empresa).slice(0, 80) : null,
    });
  }, []);

  const handleSelecionarCliente = useCallback(
    (c) => {
      selecionarClienteNaLista(c);
    },
    [selecionarClienteNaLista],
  );

  const handleOpenRadar = useCallback(() => {
    if (!clienteSelecionado) return;
    const id = clienteSelecionado.id_cliente ?? clienteIdSelecionado;
    logConsultorWorkspace('open_radar_cliente', { id_cliente: id });
    const qs = id != null ? `?cliente=${encodeURIComponent(String(id))}` : '';
    navigate(`/radar-fomento${qs}`);
  }, [clienteSelecionado, clienteIdSelecionado, navigate]);

  const abrirPrecadModal = useCallback(
    (edital = null, radarMatch = null, extras = {}) => {
      if (!clienteSelecionado) return;
      if (!canViewClient(user, clienteSelecionado)) {
        alert('Você não tem permissão para aceder a este cliente.');
        return;
      }
      const multiCount = extras.oportunidadesSelecionadas?.length ?? 0;
      logConsultorWorkspace(
        multiCount > 1 ? 'preproject_multi_modal_open' : 'preproject_modal_open',
        {
          id_cliente: clienteSelecionado.id_cliente,
          has_edital: !!edital,
          has_radar: !!radarMatch,
          opportunities_count: multiCount || undefined,
        },
      );
      setPrecadEdital(edital);
      setPrecadRadar(radarMatch);
      setPrecadInitialEnvelope(extras.initialEnvelope ?? null);
      setPrecadOportunidades(extras.oportunidadesSelecionadas ?? null);
      setPrecadModalKey(
        `${clienteSelecionado.id_cliente}-${fingerprintPrecadContext(edital, '', radarMatch)}-${Date.now()}`,
      );
      setIsPrecadModalOpen(true);
    },
    [clienteSelecionado, user],
  );

  const handleAbrirPreProjeto = useCallback(() => {
    if (!clienteSelecionado) return;
    logConsultorWorkspace('preproject_start', { id_cliente: clienteSelecionado.id_cliente });
    const ctx = readPreProjetoContext(clienteSelecionado.id_cliente);
    abrirPrecadModal(ctx.editalAssociado, ctx.radarMatch);
  }, [clienteSelecionado, abrirPrecadModal]);

  const handleToggleOpportunitySelect = useCallback((row, selKey, checked, source = 'panel') => {
    setSelectedOpportunityRows((prev) => {
      const next = new Map(prev);
      if (checked) {
        if (next.has(selKey)) return prev;
        if (next.size >= MAX_PREPROJECT_OPPORTUNITIES) {
          alert(
            `Selecione no máximo ${MAX_PREPROJECT_OPPORTUNITIES} oportunidades para montar uma estratégia de fomento objetiva.`,
          );
          logConsultorWorkspace('max_selection_reached', {
            max: MAX_PREPROJECT_OPPORTUNITIES,
            key: selKey,
            source,
          });
          return prev;
        }
        next.set(selKey, row);
        logConsultorWorkspace(
          source === 'all' ? 'opportunity_select_from_all' : 'opportunity_select',
          { key: selKey, count: next.size },
        );
      } else {
        if (!next.has(selKey)) return prev;
        next.delete(selKey);
        logConsultorWorkspace(
          source === 'all' ? 'opportunity_unselect_from_all' : 'opportunity_unselect',
          { key: selKey, count: next.size },
        );
      }
      return next;
    });
  }, []);

  const handleClearOpportunitySelection = useCallback(() => {
    setSelectedOpportunityRows(new Map());
    logConsultorWorkspace('opportunity_selection_cleared');
  }, []);

  const handleOpenAllOpportunities = useCallback(() => {
    if (!clienteSelecionado || !CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL) return;
    logConsultorWorkspace('all_opportunities_modal_open', {
      id_cliente: clienteSelecionado.id_cliente,
      total_matches: safeAllMatches.length,
    });
    setIsAllOpportunitiesOpen(true);
  }, [clienteSelecionado, safeAllMatches.length]);

  const handleGerarRelatorioTriagem = useCallback(() => {
    if (!clienteSelecionado || selectedOpportunitiesNormalized.length === 0) {
      alert('Selecione pelo menos uma oportunidade para gerar o relatório de triagem.');
      return;
    }
    logConsultorWorkspace('triage_report_open', {
      id_cliente: clienteSelecionado.id_cliente,
      selected_count: selectedOpportunitiesNormalized.length,
    });
    const cid = clienteSelecionado.id_cliente ?? clienteSelecionado.id;
    const n = persistTrackedSnapshots(cid, selectedOpportunitiesNormalized, 'triagem');
    if (n > 0) {
      logConsultorWorkspace('tracked_opportunity_add', {
        id_cliente: cid,
        source: 'triagem',
        count: selectedOpportunitiesNormalized.length,
      });
      setTrackedRefreshTick((t) => t + 1);
    }
    const selCount = selectedOpportunitiesNormalized.length;
    recordTimeline({
      type: TIMELINE_EVENT_TYPES.TRIAGE_REPORT_GENERATED,
      title: 'Relatório de triagem gerado',
      description:
        selCount === 1
          ? '1 oportunidade na seleção.'
          : `${selCount} oportunidades na seleção.`,
      metadata: { count: selCount },
    });
    setIsTriageReportOpen(true);
  }, [clienteSelecionado, selectedOpportunitiesNormalized, recordTimeline]);

  const handleGerarPreProjetoSelecionados = useCallback(
    (opts = {}) => {
    if (!clienteSelecionado) return;
    const opportunities = selectedOpportunitiesNormalized;
    if (opts?.fromAll) {
      logConsultorWorkspace('preproject_from_all_start', { count: opportunities.length });
    }
    logConsultorWorkspace('preproject_multi_start', { count: opportunities.length });
    logConsultorWorkspace('preproject_multi_count', { count: opportunities.length });
    try {
      const ctx = openPreProjetoFromOpportunities({
        cliente: clienteSelecionado,
        opportunities,
        source: 'workspace_consultor',
      });
      logConsultorWorkspace('preproject_primary_selected', {
        key: ctx.primaryOpportunity?.key,
        score: ctx.primaryOpportunity?.scorePct,
        count: opportunities.length,
      });
      logConsultorWorkspace('preproject_multi_draft_built', {
        id_cliente: clienteSelecionado.id_cliente,
        count: opportunities.length,
      });
      const cid = clienteSelecionado.id_cliente ?? clienteSelecionado.id;
      const n = persistTrackedSnapshots(cid, opportunities, 'preprojeto');
      if (n > 0) {
        logConsultorWorkspace('tracked_opportunity_add', {
          id_cliente: cid,
          source: 'preprojeto',
          count: opportunities.length,
        });
        setTrackedRefreshTick((t) => t + 1);
        recordTimeline({
          type: TIMELINE_EVENT_TYPES.TRACKED_OPPORTUNITY,
          title: 'Oportunidade acompanhada',
          description: `${opportunities.length} oportunidade(s) no acompanhamento.`,
          metadata: { action: 'add', count: opportunities.length },
        });
      }
      recordTimeline({
        type: TIMELINE_EVENT_TYPES.PREPROJECT_UPDATED,
        title: 'Pré-projeto consultivo atualizado',
        description: `Rascunho iniciado com ${opportunities.length} oportunidade(s) selecionada(s).`,
        metadata: { count: opportunities.length, source: 'multi_select' },
      });
      setIsAllOpportunitiesOpen(false);
      setIsTriageReportOpen(false);
      abrirPrecadModal(ctx.editalAssociado, ctx.radarMatch, {
        initialEnvelope: ctx.initialEnvelope,
        oportunidadesSelecionadas: ctx.oportunidadesSelecionadas,
      });
    } catch (e) {
      logConsultorWorkspace('preproject_multi_error', {
        message: e?.message || String(e),
      });
      alert('Não foi possível iniciar o pré-projeto com as oportunidades selecionadas.');
    }
  },
    [clienteSelecionado, selectedOpportunitiesNormalized, abrirPrecadModal, recordTimeline],
  );

  const handleNovoCliente = useCallback(() => {
    if (!permissions.canCreate) return;
    setEditingCliente(null);
    setIsClientModalOpen(true);
  }, [permissions.canCreate]);

  const handleEditarCliente = useCallback(
    (c) => {
      if (!c || !canEditClient(user, c)) {
        alert('Você não tem permissão para editar este cliente.');
        return;
      }
      setEditingCliente(c);
      setIsClientModalOpen(true);
    },
    [user],
  );

  const handleBriefingRapido = useCallback(
    (sourceOrCliente) => {
      const briefingSources = new Set([
        'callout',
        'profile_card',
        'precad_card',
        'action_plan',
        'status_banner',
      ]);
      if (typeof sourceOrCliente === 'string' && briefingSources.has(sourceOrCliente)) {
        if (!clienteSelecionado || !canEditClient(user, clienteSelecionado)) {
          alert('Você não tem permissão para editar o briefing deste cliente.');
          return;
        }
        const logEvent =
          sourceOrCliente === 'callout'
            ? 'cta_click_callout'
            : sourceOrCliente === 'profile_card'
              ? 'cta_click_profile_card'
              : 'cta_click';
        logClienteBriefing(logEvent, {
          id_cliente: clienteSelecionado.id_cliente,
          placement: sourceOrCliente,
          score: clientProfileScore,
        });
        setIsBriefingOpen(true);
        return;
      }
      const alvo = sourceOrCliente || clienteSelecionado;
      if (!alvo || !canEditClient(user, alvo)) {
        alert('Você não tem permissão para editar o briefing deste cliente.');
        return;
      }
      logClienteBriefing('modal_open', { id_cliente: alvo.id_cliente, via: 'legacy_client_arg' });
      setIsBriefingOpen(true);
    },
    [user, clienteSelecionado, clientProfileScore],
  );

  const handleSaveBriefing = useCallback(
    async (briefingForm, { openFullForm = false } = {}) => {
      if (!clienteSelecionado) return;
      setBriefingSaving(true);
      const beforeScore = calculateClientProfileCompleteness(clienteSelecionado).score;
      try {
        const formState = applyBriefingToFormState(
          clientFormStateFromCliente(clienteSelecionado),
          briefingForm,
        );
        const patch = sanitizeClientWritePayload(
          user,
          mergeClientWritePayload(clienteSelecionado, formState),
        );
        await dataService.updateClient(clienteSelecionado.id_cliente, patch, { user });
        setIsBriefingOpen(false);
        const lista = await loadClientes();
        const updated = lista.find(
          (row) => String(row.id_cliente) === String(clienteSelecionado.id_cliente),
        );
        if (updated) selecionarClienteNaLista(updated);
        const afterScore = updated
          ? calculateClientProfileCompleteness(updated).score
          : beforeScore;
        logClienteBriefing('save_success', {
          id_cliente: clienteSelecionado.id_cliente,
          before: beforeScore,
          after: afterScore,
        });
        logClienteBriefing('profile_completion_updated', {
          id_cliente: clienteSelecionado.id_cliente,
          before: beforeScore,
          after: afterScore,
        });
        if (openFullForm) {
          logClienteBriefing('save_and_open_full_form', {
            id_cliente: clienteSelecionado.id_cliente,
          });
        }
        alert('Briefing salvo. O perfil do cliente foi atualizado.');
        recordTimeline({
          type: TIMELINE_EVENT_TYPES.BRIEFING_SAVED,
          title: 'Briefing rápido salvo',
          description:
            afterScore > beforeScore
              ? `Completude do perfil: ${beforeScore}% → ${afterScore}%.`
              : `Completude do perfil: ${afterScore}%.`,
          metadata: { before: beforeScore, after: afterScore },
        });
        if (openFullForm && updated) {
          handleEditarCliente(updated);
        }
      } catch (e) {
        alert(`Erro ao salvar briefing: ${e?.message || e}`);
        throw e;
      } finally {
        setBriefingSaving(false);
      }
    },
    [clienteSelecionado, user, loadClientes, selecionarClienteNaLista, handleEditarCliente, recordTimeline],
  );

  const handleSaveCliente = useCallback(
    async (formData) => {
      try {
        if (editingCliente) {
          if (!canEditClient(user, editingCliente)) {
            alert('Você não tem permissão para editar este cliente.');
            return;
          }
          const patch = sanitizeClientWritePayload(
            user,
            mergeClientWritePayload(editingCliente, formData),
          );
          await dataService.updateClient(editingCliente.id_cliente, patch, { user });
        } else {
          if (!isAdminUser(user) && sessionUserId(user) == null) {
            alert('Sua sessão não tem id_usuario. Faça login novamente para cadastrar clientes.');
            return;
          }
          const payload = attachOwnerToClientPayload(user, clientPayloadFromFormState(formData));
          await dataService.createClient(payload, { user });
        }
        setIsClientModalOpen(false);
        setEditingCliente(null);
        const lista = await loadClientes();
        const alvo =
          editingCliente ??
          lista.find(
            (c) =>
              String(c.nome_empresa || '') === String(formData.nome_empresa || '') &&
              String(c.cnpj || '').replace(/\D/g, '') === String(formData.cnpj || '').replace(/\D/g, ''),
          ) ??
          lista[lista.length - 1];
        if (alvo) selecionarClienteNaLista(alvo);
        const cid = alvo?.id_cliente ?? alvo?.id ?? editingCliente?.id_cliente;
        if (cid != null && editingCliente) {
          recordTimeline({
            type: TIMELINE_EVENT_TYPES.CLIENT_PROFILE_UPDATED,
            title: 'Perfil do cliente atualizado',
            description: 'Cadastro consultivo salvo no Workspace.',
            metadata: { id_cliente: cid },
          });
        }
      } catch (e) {
        alert(`Erro ao salvar cliente: ${e?.message || e}`);
      }
    },
    [editingCliente, user, loadClientes, selecionarClienteNaLista, recordTimeline],
  );

  const fecharPrecadModal = useCallback(() => {
    setIsPrecadModalOpen(false);
    setPrecadEdital(null);
    setPrecadRadar(null);
    setPrecadInitialEnvelope(null);
    setPrecadOportunidades(null);
    setPrecadSummaryTick((t) => t + 1);
    logConsultorWorkspace('preproject_modal_closed', { id_cliente: clienteSelecionado?.id_cliente });
  }, [clienteSelecionado?.id_cliente]);

  const canEditSelected =
    clienteSelecionado && permissions.canEdit && canEditClient(user, clienteSelecionado);

  const portfolioModalEnabled = CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL;

  const handleStatusPrimaryAction = useCallback(
    (actionType) => {
      if (!clienteSelecionado) return;
      logConsultorWorkspace('client_status_primary_action', {
        id_cliente: clienteSelecionado.id_cliente ?? clienteSelecionado.id,
        action: actionType,
        status_key: selectedClientStatus?.key,
      });
      switch (actionType) {
        case 'open_briefing':
          handleBriefingRapido('status_banner');
          break;
        case 'open_client_form':
          handleEditarCliente(clienteSelecionado);
          break;
        case 'open_portfolio':
          handleOpenAllOpportunities();
          break;
        case 'open_triage_report':
          handleGerarRelatorioTriagem();
          break;
        case 'open_preproject':
          handleAbrirPreProjeto();
          break;
        case 'open_tracked': {
          const el = document.getElementById('consultor-tracked-section');
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
          break;
        }
        default:
          break;
      }
    },
    [
      clienteSelecionado,
      selectedClientStatus?.key,
      handleBriefingRapido,
      handleEditarCliente,
      handleOpenAllOpportunities,
      handleGerarRelatorioTriagem,
      handleAbrirPreProjeto,
    ],
  );

  const statusPrimaryActionDisabled = useMemo(() => {
    const type = selectedClientStatus?.primaryActionType;
    if (type === 'open_portfolio' && !portfolioModalEnabled) return true;
    if (type === 'open_client_form' && !canEditSelected) return true;
    if (type === 'open_briefing' && !canEditSelected) return true;
    return false;
  }, [selectedClientStatus?.primaryActionType, portfolioModalEnabled, canEditSelected]);

  if (!permissions.canViewCadastros) {
    return (
      <div className="consultor-workspace-body">
        <p className="consultor-panel-error" role="alert">
          Você não tem permissão para aceder ao Workspace do Consultor.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="consultor-workspace-below-header">
        <header className="cad-hero consultor-workspace-hero">
          <div className="cad-hero-text">
            <h1 className="cad-hero-title">Workspace do Consultor</h1>
            <p className="cad-hero-sub">
              Use o perfil do cliente para gerar uma carteira de oportunidades, selecione as mais promissoras e
              transforme em pré-projeto consultivo.
            </p>
          </div>
        </header>

        <div className="consultor-workspace-layout consultor-workspace-shell">
          <ConsultorClienteList
            clientes={clientes}
            clienteIdSelecionado={clienteIdSelecionado}
            onSelecionar={handleSelecionarCliente}
            loading={loading}
            error={loadError}
            onNovoCliente={handleNovoCliente}
            onEditarCliente={handleEditarCliente}
            canCreate={permissions.canCreate}
            canEdit={permissions.canEdit}
            clienteSelecionado={clienteSelecionado}
            getClientStatus={getClientStatus}
          />

          <main className="consultor-main-panel consultor-workspace-main">
            {!clienteSelecionado ? (
              <div className="consultor-empty-state">
                <h2 className="consultor-empty-title">Selecione um cliente para começar</h2>
                <p className="consultor-empty-desc">
                  Crie ou escolha um cliente na coluna à esquerda para ver oportunidades, pré-projetos e próximas ações.
                </p>
                {permissions.canCreate ? (
                  <button type="button" className="btn-primary" onClick={handleNovoCliente}>
                    + Novo cliente
                  </button>
                ) : null}
              </div>
            ) : (
              <>
                <div className="consultor-client-header">
                  <div>
                    <h2 className="consultor-client-title">{clienteSelecionado.nome_empresa}</h2>
                    <p className="consultor-client-sub">
                      {[clienteSelecionado.porte_empresa, clienteSelecionado.setor, clienteSelecionado.estado]
                        .filter(Boolean)
                        .join(' · ') || 'Perfil do cliente'}
                    </p>
                    <ConsultorClientStatusBanner
                      status={selectedClientStatus}
                      onPrimaryAction={handleStatusPrimaryAction}
                      primaryActionDisabled={statusPrimaryActionDisabled}
                    />
                  </div>
                  <div className="consultor-quick-actions">
                    {canEditSelected ? (
                      <button
                        type="button"
                        className="btn-detalhes dash-action-outline"
                        onClick={() => handleEditarCliente(clienteSelecionado)}
                      >
                        Editar cliente
                      </button>
                    ) : null}
                    <button type="button" className="btn-view" onClick={handleOpenRadar}>
                      Ver Radar deste cliente
                    </button>
                    <button type="button" className="btn-view" onClick={handleAbrirPreProjeto}>
                      Abrir pré-projeto consultivo
                    </button>
                    <ConsultorExportMenu
                      cliente={clienteSelecionado}
                      topMatches={safeTopMatches}
                      selectedRows={selectedRowsForCsv}
                      topMatchesReady={workspace.topMatchesReady}
                      onOpenAllOpportunities={
                        CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL
                          ? handleOpenAllOpportunities
                          : undefined
                      }
                      onCsvExported={({ rowCount, filenamePrefix }) => {
                        recordTimeline({
                          type: TIMELINE_EVENT_TYPES.CSV_EXPORTED,
                          title: 'Carteira exportada em CSV',
                          description: `${rowCount} linha(s) · ${filenamePrefix || 'carteira'}.`,
                          metadata: { rowCount, filenamePrefix },
                        });
                      }}
                    />
                  </div>
                </div>

                <ConsultorWorkflowSteps
                  profileScore={clientProfileScore}
                  totalMatches={analyzedOpportunityCount}
                  radarReady={radarReadyForWorkflow}
                  selectedCount={selectedOpportunityKeys.size}
                  precadHadDraft={Boolean(precadSummary?.hadDraft)}
                  hasCliente
                  cliente={clienteSelecionado}
                />

                <ConsultorClientProfileCard
                  cliente={clienteSelecionado}
                  canEdit={canEditSelected}
                  onCompletarCadastro={() => handleEditarCliente(clienteSelecionado)}
                  onEditarCliente={handleEditarCliente}
                  onBriefingRapido={handleBriefingRapido}
                />

                <ConsultorRecommendedSection
                  totalMatches={analyzedOpportunityCount}
                  topMatches={safeTopMatches}
                  enableAllOpportunitiesModal={CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL}
                  loading={workspace.loading}
                  loadingMessage={workspace.loadingMessage}
                  portfolioStatus={portfolioStatus}
                  error={workspace.error}
                  isPartial={workspace.isPartial}
                  hasPreviewResults={workspace.hasPreviewResults}
                  topMatchesReady={workspace.topMatchesReady}
                  deadlineSummary={workspace.deadlineSummary}
                  onOpenRadar={handleOpenRadar}
                  onRetryRadar={workspace.recalculate}
                  portfolioRadarWarning={workspace.portfolioRadarWarning}
                  radarLoading={workspace.radarLoading}
                  manualRetrying={workspace.manualRetrying}
                  onOpenAllOpportunities={handleOpenAllOpportunities}
                  selectedOpportunityKeys={selectedOpportunityKeys}
                  selectionBarSummary={selectionBarSummary}
                  onToggleOpportunitySelect={handleToggleOpportunitySelect}
                  onClearOpportunitySelection={handleClearOpportunitySelection}
                  onGerarPreProjetoSelecionados={handleGerarPreProjetoSelecionados}
                  onGerarRelatorioTriagem={handleGerarRelatorioTriagem}
                />

                <ConsultorPrecadastroCard
                  summary={precadSummary}
                  canOpen={canViewClient(user, clienteSelecionado)}
                  onAbrir={handleAbrirPreProjeto}
                  hasBriefing={clientHasBriefing}
                  profileScore={clientProfileScore}
                  onBriefingRapido={canEditSelected ? handleBriefingRapido : undefined}
                />

                <div className="consultor-placeholder-grid consultor-placeholder-grid--secondary">
                  <ConsultorTrackedOpportunitiesCard
                    cliente={clienteSelecionado}
                    selectedOpportunities={selectedOpportunitiesNormalized}
                    allMatches={safeAllMatches}
                    remoteFavorites={favHook.favorites}
                    refreshTick={trackedRefreshTick}
                    favoritosRemoteEnabled={favHook.favoritosRemoteEnabled}
                    onOpenPortfolio={
                      CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL
                        ? handleOpenAllOpportunities
                        : undefined
                    }
                    onOpenRadar={handleOpenRadar}
                    onTrackedRemoved={(item) => {
                      recordTimeline({
                        type: TIMELINE_EVENT_TYPES.TRACKED_OPPORTUNITY,
                        title: 'Oportunidade acompanhada',
                        description: `Removida: ${item.titulo || item.key}.`,
                        metadata: { action: 'remove', key: item.key },
                      });
                    }}
                  />
                  <ConsultorActionPlanCard
                    cliente={clienteSelecionado}
                    profileCompleteness={clientProfileScore}
                    hasBriefing={clientHasBriefing}
                    selectedOpportunities={selectedOpportunitiesNormalized}
                    topMatches={safeTopMatches}
                    precadSummary={precadSummary}
                    deadlineSummary={workspace.deadlineSummary}
                    canAct={canEditSelected}
                    onOpenBriefing={() => handleBriefingRapido('action_plan')}
                    onOpenClientForm={() => handleEditarCliente(clienteSelecionado)}
                    onOpenPortfolio={handleOpenAllOpportunities}
                    onOpenPreProject={handleAbrirPreProjeto}
                    onOpenTriageReport={handleGerarRelatorioTriagem}
                    onGeneratePreProjectFromSelection={handleGerarPreProjetoSelecionados}
                  />
                </div>

                <ConsultorClientTimelineCard
                  cliente={clienteSelecionado}
                  refreshTick={timelineRefreshTick}
                />
              </>
            )}
          </main>
        </div>
      </div>

      {isClientModalOpen && (
        <Modal
          portal
          zIndex={1185}
          hideCloseButton
          onClose={() => {
            setIsClientModalOpen(false);
            setEditingCliente(null);
          }}
          className="modal-client-workspace-overlay"
        >
          <ClientForm
            variant="workspaceLarge"
            title={editingCliente ? 'Editar cliente' : 'Novo cliente'}
            initialData={editingCliente}
            onSave={handleSaveCliente}
            onCancel={() => {
              setIsClientModalOpen(false);
              setEditingCliente(null);
            }}
          />
        </Modal>
      )}

      {CONSULTOR_ENABLE_ALL_OPPORTUNITIES_MODAL && isAllOpportunitiesOpen && clienteSelecionado && (
        <ConsultorAllOpportunitiesModal
          isOpen={isAllOpportunitiesOpen}
          onClose={() => setIsAllOpportunitiesOpen(false)}
          cliente={clienteSelecionado}
          matches={safeAllMatches}
          loading={workspace.loading}
          portfolioStatus={portfolioStatus}
          error={workspace.error}
          isPartial={workspace.isPartial}
          hasPreviewResults={workspace.hasPreviewResults}
          selectedOpportunityKeys={selectedOpportunityKeys}
          selectionBarSummary={selectionBarSummary}
          onToggleOpportunitySelect={handleToggleOpportunitySelect}
          onClearOpportunitySelection={handleClearOpportunitySelection}
          onGerarPreProjetoSelecionados={handleGerarPreProjetoSelecionados}
          onOpenRadar={handleOpenRadar}
          deadlineSummary={workspace.deadlineSummary}
          onGerarRelatorioTriagem={handleGerarRelatorioTriagem}
          onCsvExported={({ rowCount, source }) => {
            recordTimeline({
              type: TIMELINE_EVENT_TYPES.CSV_EXPORTED,
              title: 'Carteira exportada em CSV',
              description: `${rowCount} linha(s) · ${source === 'selected' ? 'selecionadas' : 'filtradas'}.`,
              metadata: { rowCount, source },
            });
          }}
        />
      )}

      {isBriefingOpen && clienteSelecionado && (
        <ConsultorClientBriefingModal
          isOpen={isBriefingOpen}
          onClose={() => setIsBriefingOpen(false)}
          cliente={clienteSelecionado}
          onSaveBriefing={handleSaveBriefing}
          saving={briefingSaving}
        />
      )}

      {isTriageReportOpen && clienteSelecionado && (
        <ConsultorTriageReportModal
          isOpen={isTriageReportOpen}
          onClose={() => setIsTriageReportOpen(false)}
          cliente={clienteSelecionado}
          totalMatches={analyzedOpportunityCount}
          allMatches={safeAllMatches}
          selectedOpportunities={selectedOpportunitiesNormalized}
          deadlineSummary={workspace.deadlineSummary}
          onGerarPreProjetoConsultivo={handleGerarPreProjetoSelecionados}
        />
      )}

      {isPrecadModalOpen && clienteSelecionado && (
        <Modal
          portal
          zIndex={1200}
          onClose={fecharPrecadModal}
          className="modal-large modal-precad modal-precad-workspace-overlay"
          hideCloseButton
        >
          <ProjetoPrecadastroForm
            key={precadModalKey}
            modalSize="workspaceLarge"
            cliente={clienteSelecionado}
            editalAssociado={precadEdital}
            radarMatch={precadRadar}
            initialEnvelope={precadInitialEnvelope}
            oportunidadesSelecionadas={precadOportunidades}
            onCancel={fecharPrecadModal}
            onDraftSaved={() => {
              logConsultorWorkspace('preproject_saved', {
                id_cliente: clienteSelecionado.id_cliente,
              });
              setPrecadSummaryTick((t) => t + 1);
              recordTimeline({
                type: TIMELINE_EVENT_TYPES.PREPROJECT_UPDATED,
                title: 'Pré-projeto consultivo atualizado',
                description: 'Rascunho salvo neste navegador.',
              });
            }}
          />
        </Modal>
      )}
    </>
  );
}

export default function ConsultorWorkspace() {
  const [boundaryKey, setBoundaryKey] = useState(0);

  return (
    <div className="page-wrapper consultor-workspace-page">
      <Header searchPlaceholder="Buscar no workspace…" />
      <ConsultorWorkspaceErrorBoundary
        key={boundaryKey}
        onRetry={() => setBoundaryKey((k) => k + 1)}
      >
        <ConsultorWorkspaceContent />
      </ConsultorWorkspaceErrorBoundary>
    </div>
  );
}
