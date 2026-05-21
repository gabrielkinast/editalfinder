import { useEffect } from 'react';
import ConsultorOpportunityPipeline from './ConsultorOpportunityPipeline';
import ConsultorSelectionBar from './ConsultorSelectionBar';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';
import { MAX_PREPROJECT_OPPORTUNITIES } from '../../utils/consultor/opportunitySelection';
import { CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES } from '../../utils/consultor/consultorWorkspaceConstants';

const RADAR_FAIL_CODE = 'radar_calc_failed';
const RADAR_FAIL_MESSAGE =
  'Não conseguimos calcular dentro do Workspace agora. Você ainda pode abrir o Radar deste cliente.';

export default function ConsultorRecommendedSection({
  totalMatches = 0,
  topMatches,
  loading = false,
  loadingMessage = null,
  portfolioStatus = null,
  error = null,
  isPartial = false,
  hasPreviewResults = false,
  topMatchesReady = false,
  deadlineSummary = null,
  onOpenRadar,
  onRetryRadar,
  onOpenAllOpportunities,
  enableAllOpportunitiesModal = true,
  selectedOpportunityKeys = null,
  selectionBarSummary = null,
  onToggleOpportunitySelect,
  onClearOpportunitySelection,
  onGerarPreProjetoSelecionados,
  onGerarRelatorioTriagem,
  portfolioRadarWarning = null,
  radarLoading = false,
  manualRetrying = false,
}) {
  const safeTopMatches = Array.isArray(topMatches) ? topMatches : [];
  const selectedCount = selectedOpportunityKeys?.size ?? 0;
  const hasPortfolioData =
    safeTopMatches.length > 0 || totalMatches > 0 || selectedCount > 0;
  const displayCatalogError = error && error !== RADAR_FAIL_CODE ? String(error) : null;
  const displayRadarFatal = error === RADAR_FAIL_CODE && !hasPortfolioData;
  const showPartialBanner =
    isPartial && hasPreviewResults && radarLoading && !portfolioRadarWarning;
  const showContent =
    (topMatchesReady || hasPortfolioData) && !displayCatalogError;
  const statusMessage = portfolioStatus?.message || loadingMessage;
  const showStatusBlock = Boolean(statusMessage) && (portfolioStatus || (loading && loadingMessage));
  const statusKind = portfolioStatus?.kind || (loading ? 'loading' : null);
  const hideBlockingLoading = statusKind === 'loading' && hasPortfolioData;
  const canOpenAll =
    enableAllOpportunitiesModal && showContent && totalMatches > 0 && onOpenAllOpportunities;

  useEffect(() => {
    if (!import.meta.env?.DEV) return;
    logConsultorWorkspace('selected_opportunities_count', { count: selectedCount });
  }, [selectedCount]);

  return (
    <section className="consultor-section consultor-section--recommended">
      <div className="consultor-rec-head">
        <div className="consultor-rec-head-text">
          <div className="consultor-rec-title-row">
            <h3 className="consultor-section-title">Carteira de oportunidades</h3>
            {showContent && totalMatches > 0 ? (
              <span className="consultor-rec-badge">
                {totalMatches} oportunidade{totalMatches === 1 ? '' : 's'} analisada
                {totalMatches === 1 ? '' : 's'} para este cliente
              </span>
            ) : null}
          </div>
          {showContent ? (
            <>
              <p className="consultor-section-sub consultor-section-sub--primary">
                Top {CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES} oportunidades para triagem inicial.
              </p>
              <p className="consultor-section-sub consultor-section-sub--hint">
                Selecione até {MAX_PREPROJECT_OPPORTUNITIES} oportunidades para montar uma estratégia de fomento
                objetiva. Use &quot;Explorar carteira completa&quot; para ver lista ou tabela estruturada.
              </p>
            </>
          ) : null}
        </div>
        <div className="consultor-rec-head-actions">
          {canOpenAll ? (
            <button type="button" className="btn-view consultor-btn-all-opps" onClick={onOpenAllOpportunities}>
              Explorar carteira completa
            </button>
          ) : null}
          <button
            type="button"
            className="btn-detalhes dash-action-outline consultor-btn-radar-sm"
            onClick={onOpenRadar}
          >
            Ver no Radar
          </button>
        </div>
      </div>

      {selectedCount > 0 ? (
        <ConsultorSelectionBar
          selectedCount={selectedCount}
          selectionBarSummary={selectionBarSummary}
          onGerarRelatorioTriagem={onGerarRelatorioTriagem}
          onGerarPreProjetoSelecionados={onGerarPreProjetoSelecionados}
          onClearOpportunitySelection={onClearOpportunitySelection}
          variant="compact"
        />
      ) : null}

      {showPartialBanner && !portfolioStatus?.message ? (
        <p className="consultor-partial-hint" role="status">
          Prévia — completando lista…
        </p>
      ) : null}

      {showStatusBlock && !hideBlockingLoading ? (
        <div
          className={`consultor-opps-status consultor-opps-status--${statusKind || 'loading'}`}
          role="status"
        >
          <p>{statusMessage}</p>
        </div>
      ) : null}

      {portfolioRadarWarning ? (
        <p className="consultor-partial-hint consultor-partial-hint--warn" role="status">
          {portfolioRadarWarning}
        </p>
      ) : null}

      {radarLoading && hasPortfolioData && !portfolioRadarWarning && !hideBlockingLoading ? (
        <p className="consultor-partial-hint consultor-partial-hint--inline" role="status">
          Atualizando em segundo plano…
        </p>
      ) : null}

      {displayCatalogError ? (
        <div className="consultor-opps-status consultor-opps-status--error" role="alert">
          <p>{displayCatalogError}</p>
        </div>
      ) : null}

      {displayRadarFatal ? (
        <div className="consultor-opps-status consultor-opps-status--warn" role="alert">
          <p>{RADAR_FAIL_MESSAGE}</p>
          <div className="consultor-opps-status-actions">
            {onRetryRadar ? (
              <button
                type="button"
                className="btn-view"
                onClick={onRetryRadar}
                disabled={manualRetrying}
              >
                {manualRetrying ? 'Recalculando…' : 'Tentar novamente'}
              </button>
            ) : null}
            <button type="button" className="btn-detalhes dash-action-outline" onClick={onOpenRadar}>
              Abrir no Radar
            </button>
          </div>
        </div>
      ) : null}

      {!loading && !displayRadarFatal && !displayCatalogError && topMatchesReady && totalMatches === 0 ? (
        <p className="consultor-empty-matches">
          Nenhuma oportunidade forte encontrada para este cliente.
        </p>
      ) : null}

      {!displayCatalogError && safeTopMatches.length > 0 ? (
        <div className="consultor-pipeline-scroll">
          <ConsultorOpportunityPipeline
            matches={safeTopMatches}
            selectedKeys={selectedOpportunityKeys}
            onToggleSelect={onToggleOpportunitySelect}
            onOpenRadar={onOpenRadar}
          />
        </div>
      ) : null}

      {showContent && totalMatches > 0 && deadlineSummary ? (
        <div className="consultor-deadline-summary" aria-label="Resumo de prazos">
          <span className="consultor-deadline-chip consultor-deadline-chip--urgent">
            Vence em até 7 dias: <strong>{deadlineSummary.venceAte7}</strong>
          </span>
          <span className="consultor-deadline-chip consultor-deadline-chip--muted">
            Sem prazo: <strong>{deadlineSummary.semPrazo}</strong>
          </span>
          <span className="consultor-deadline-chip consultor-deadline-chip--ok">
            Prazo confortável: <strong>{deadlineSummary.prazoConfortavel}</strong>
          </span>
        </div>
      ) : null}
    </section>
  );
}
