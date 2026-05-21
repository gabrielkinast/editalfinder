import { useCallback, useEffect, useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import ConsultorOpportunityCompactRow from './ConsultorOpportunityCompactRow';
import ConsultorOpportunitiesTable from './ConsultorOpportunitiesTable';
import ConsultorPortfolioSummary from './ConsultorPortfolioSummary';
import ConsultorSelectionBar from './ConsultorSelectionBar';
import { CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES } from '../../utils/consultor/consultorWorkspaceConstants';
import { suggestedPrincipalFromMatches } from '../../utils/consultor/portfolioTriageSummary';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';
import {
  CONSULTOR_ALL_OPPORTUNITIES_INCREMENT,
  CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP,
} from '../../utils/consultor/consultorWorkspaceConstants';
import {
  COMPAT_FILTER_ALL,
  COMPAT_FILTER_ALTA,
  COMPAT_FILTER_BAIXA,
  COMPAT_FILTER_MEDIA,
  filterAndSortConsultorMatches,
  PRAZO_FILTER_ALL,
  PRAZO_FILTER_COM_PRAZO,
  PRAZO_FILTER_SEM_PRAZO,
  PRAZO_FILTER_VENCE_7,
  SORT_FONTE,
  SORT_PRAZO,
  SORT_SCORE,
  SORT_TITULO,
} from '../../utils/consultor/consultorAllOpportunitiesFilter';
import {
  getOpportunitySelectionKey,
  MAX_PREPROJECT_OPPORTUNITIES,
} from '../../utils/consultor/opportunitySelection';
import { downloadConsultorPortfolioCsv } from '../../utils/consultor/exportConsultorPortfolioCsv';

const ERROR_MSG = 'Não foi possível carregar as oportunidades agora.';

/**
 * Modal com todos os matches do Radar para o cliente (filtros + seleção compartilhada).
 */
export default function ConsultorAllOpportunitiesModal({
  isOpen = false,
  onClose,
  cliente = null,
  matches = [],
  loading = false,
  portfolioStatus = null,
  error = null,
  isPartial = false,
  hasPreviewResults = false,
  selectedOpportunityKeys = null,
  selectionBarSummary = null,
  onToggleOpportunitySelect,
  onClearOpportunitySelection,
  onGerarPreProjetoSelecionados,
  onOpenRadar,
  deadlineSummary = null,
  onGerarRelatorioTriagem,
  onCsvExported,
}) {
  const [search, setSearch] = useState('');
  const [compatFilter, setCompatFilter] = useState(COMPAT_FILTER_ALL);
  const [prazoFilter, setPrazoFilter] = useState(PRAZO_FILTER_ALL);
  const [sortBy, setSortBy] = useState(SORT_SCORE);
  const [visibleCap, setVisibleCap] = useState(CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP);
  const [viewMode, setViewMode] = useState('list');
  const [exportingCsv, setExportingCsv] = useState(false);

  const safeMatches = useMemo(() => (Array.isArray(matches) ? matches : []), [matches]);

  const selectedSet =
    selectedOpportunityKeys instanceof Set
      ? selectedOpportunityKeys
      : new Set(selectedOpportunityKeys || []);

  const filteredMatches = useMemo(
    () =>
      filterAndSortConsultorMatches(safeMatches, {
        search,
        compatFilter,
        prazoFilter,
        sortBy,
      }),
    [safeMatches, search, compatFilter, prazoFilter, sortBy],
  );

  const visibleMatches = useMemo(
    () => filteredMatches.slice(0, visibleCap),
    [filteredMatches, visibleCap],
  );

  const hasMore = visibleCap < filteredMatches.length;
  const selectedCount = selectedSet.size;
  const hasPortfolioData = safeMatches.length > 0 || selectedCount > 0;
  const statusMessage = portfolioStatus?.message;
  const statusKind = portfolioStatus?.kind || (loading ? 'loading' : null);
  const showStatusInModal = Boolean(statusMessage) && !(statusKind === 'loading' && hasPortfolioData);

  useEffect(() => {
    if (!isOpen) return;
    setVisibleCap(CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP);
    setSearch('');
    setCompatFilter(COMPAT_FILTER_ALL);
    setPrazoFilter(PRAZO_FILTER_ALL);
    setSortBy(SORT_SCORE);
    setViewMode('list');
    logConsultorWorkspace('all_opportunities_open', {
      id_cliente: cliente?.id_cliente ?? null,
      total_matches: safeMatches.length,
    });
  }, [isOpen, cliente?.id_cliente, safeMatches.length]);

  useEffect(() => {
    if (!isOpen) return;
    logConsultorWorkspace('all_opportunities_visible_count', {
      visible: visibleMatches.length,
      filtered: filteredMatches.length,
      total: safeMatches.length,
    });
  }, [isOpen, visibleMatches.length, filteredMatches.length, safeMatches.length]);

  const logFilterChange = useCallback((field, value) => {
    logConsultorWorkspace('all_opportunities_filter_change', { field, value });
  }, []);

  const handleToggle = useCallback(
    (row, selKey, checked) => {
      onToggleOpportunitySelect?.(row, selKey, checked, 'all');
    },
    [onToggleOpportunitySelect],
  );

  const handleGerar = useCallback(() => {
    logConsultorWorkspace('preproject_from_all_start', { count: selectedCount });
    onGerarPreProjetoSelecionados?.({ fromAll: true });
  }, [onGerarPreProjetoSelecionados, selectedCount]);

  const handleShowMore = useCallback(() => {
    setVisibleCap((c) => {
      const next = c + CONSULTOR_ALL_OPPORTUNITIES_INCREMENT;
      logConsultorWorkspace('all_opportunities_show_more', {
        new_cap: next,
        filtered_total: filteredMatches.length,
      });
      return next;
    });
  }, [filteredMatches.length]);

  const handleClose = useCallback(() => {
    logConsultorWorkspace('all_opportunities_close', {
      id_cliente: cliente?.id_cliente ?? null,
      selected_count: selectedCount,
    });
    onClose?.();
  }, [onClose, cliente?.id_cliente, selectedCount]);

  const principalSugerida = useMemo(
    () => suggestedPrincipalFromMatches(safeMatches),
    [safeMatches],
  );

  const logViewChange = useCallback((mode) => {
    logConsultorWorkspace('all_opportunities_view_change', { mode });
    setViewMode(mode);
  }, []);

  const exportCsvRows = useMemo(() => {
    if (selectedCount > 0) {
      return safeMatches.filter((row) => selectedSet.has(getOpportunitySelectionKey(row)));
    }
    return filteredMatches;
  }, [selectedCount, safeMatches, filteredMatches, selectedSet]);

  const canExportCsv = exportCsvRows.length > 0 && !loading && !error;

  const handleExportCsv = useCallback(() => {
    if (exportingCsv || exportCsvRows.length === 0) return;
    const source = selectedCount > 0 ? 'selected' : 'filtered';
    logConsultorWorkspace('export_csv_start', {
      id_cliente: cliente?.id_cliente ?? null,
      source,
      count: exportCsvRows.length,
    });
    setExportingCsv(true);
    try {
      const { filename, rowCount } = downloadConsultorPortfolioCsv({
        matches: exportCsvRows,
        clienteNome: cliente?.nome_empresa || cliente?.razao_social || '',
      });
      logConsultorWorkspace('export_csv_success', {
        id_cliente: cliente?.id_cliente ?? null,
        source,
        count: rowCount,
        filename,
      });
      onCsvExported?.({ rowCount, source });
    } catch (e) {
      logConsultorWorkspace('export_csv_error', {
        id_cliente: cliente?.id_cliente ?? null,
        message: e?.message || String(e),
      });
      alert('Não foi possível exportar o CSV. Tente novamente.');
    } finally {
      setExportingCsv(false);
    }
  }, [
    cliente?.id_cliente,
    onCsvExported,
    cliente?.nome_empresa,
    cliente?.razao_social,
    exportCsvRows,
    exportingCsv,
    selectedCount,
  ]);

  if (!isOpen) return null;

  const showPartial = isPartial && hasPreviewResults;
  const displayError = error ? ERROR_MSG : null;
  const clienteNome = cliente?.nome_empresa ? String(cliente.nome_empresa) : '';

  return (
    <Modal onClose={handleClose} className="modal-large modal-consultor-all-opps">
      <div className="consultor-all-opps-shell">
        <header className="consultor-all-opps-header consultor-all-opps-header--compact">
          <div className="consultor-all-opps-header-left">
            <div className="consultor-all-opps-header-title-row">
              <h2 className="consultor-all-opps-title">Explorar carteira completa</h2>
              {clienteNome ? (
                <span className="consultor-all-opps-client" title={clienteNome}>
                  · {clienteNome}
                </span>
              ) : null}
            </div>
            <p className="consultor-all-opps-sub">Filtre, selecione e gere pré-projeto consultivo.</p>
          </div>
          <div className="consultor-all-opps-header-right">
            <div className="consultor-view-toggle" role="group" aria-label="Visualização">
              <button
                type="button"
                className={`consultor-view-toggle-btn ${viewMode === 'list' ? 'is-active' : ''}`}
                onClick={() => logViewChange('list')}
              >
                Lista
              </button>
              <button
                type="button"
                className={`consultor-view-toggle-btn ${viewMode === 'table' ? 'is-active' : ''}`}
                onClick={() => logViewChange('table')}
              >
                Tabela
              </button>
            </div>
            <button
              type="button"
              className="consultor-all-opps-close-x"
              onClick={handleClose}
              aria-label="Fechar"
            >
              ×
            </button>
          </div>
        </header>

        <div className="consultor-all-opps-toolbar">
          <div className="consultor-all-opps-filters" role="search">
            <label className="consultor-all-opps-filter consultor-all-opps-filter--search">
              <span className="consultor-all-opps-filter-label">Busca</span>
              <input
                type="search"
                className="consultor-all-opps-input"
                placeholder="Título, fonte, área…"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setVisibleCap(CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP);
                  logFilterChange('search', e.target.value.slice(0, 40));
                }}
              />
            </label>
            <label className="consultor-all-opps-filter">
              <span className="consultor-all-opps-filter-label">Compat.</span>
              <select
                className="consultor-all-opps-select"
                value={compatFilter}
                onChange={(e) => {
                  setCompatFilter(e.target.value);
                  setVisibleCap(CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP);
                  logFilterChange('compat', e.target.value);
                }}
              >
                <option value={COMPAT_FILTER_ALL}>Todas</option>
                <option value={COMPAT_FILTER_ALTA}>Alta</option>
                <option value={COMPAT_FILTER_MEDIA}>Média</option>
                <option value={COMPAT_FILTER_BAIXA}>Baixa</option>
              </select>
            </label>
            <label className="consultor-all-opps-filter">
              <span className="consultor-all-opps-filter-label">Prazo</span>
              <select
                className="consultor-all-opps-select"
                value={prazoFilter}
                onChange={(e) => {
                  setPrazoFilter(e.target.value);
                  setVisibleCap(CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP);
                  logFilterChange('prazo', e.target.value);
                }}
              >
                <option value={PRAZO_FILTER_ALL}>Todas</option>
                <option value={PRAZO_FILTER_COM_PRAZO}>Com prazo</option>
                <option value={PRAZO_FILTER_VENCE_7}>Vence 7d</option>
                <option value={PRAZO_FILTER_SEM_PRAZO}>Sem prazo</option>
              </select>
            </label>
            <label className="consultor-all-opps-filter">
              <span className="consultor-all-opps-filter-label">Ordenar</span>
              <select
                className="consultor-all-opps-select"
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setVisibleCap(CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP);
                  logFilterChange('sort', e.target.value);
                }}
              >
                <option value={SORT_SCORE}>Compatibilidade</option>
                <option value={SORT_PRAZO}>Prazo</option>
                <option value={SORT_FONTE}>Fonte</option>
                <option value={SORT_TITULO}>Título</option>
              </select>
            </label>
          </div>

          {!loading && !displayError && safeMatches.length > 0 ? (
            <ConsultorPortfolioSummary
              totalMatches={safeMatches.length}
              quickViewCount={CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES}
              selectedCount={selectedCount}
              selectionBarSummary={selectionBarSummary}
              deadlineSummary={deadlineSummary}
              principalTitulo={principalSugerida}
              filteredCount={filteredMatches.length}
            />
          ) : null}

          <div className="consultor-all-opps-toolbar-actions">
            <button
              type="button"
              className="consultor-all-opps-mini-btn consultor-all-opps-mini-btn--active"
              disabled={selectedCount === 0}
              title={
                selectedCount === 0
                  ? 'Selecione oportunidades para gerar o relatório.'
                  : 'Resumo da triagem antes do pré-projeto.'
              }
              onClick={() => {
                logConsultorWorkspace('triage_report_open_from_all', { count: selectedCount });
                onGerarRelatorioTriagem?.();
              }}
            >
              Relatório de triagem
            </button>
            <button
              type="button"
              className="consultor-all-opps-mini-btn consultor-all-opps-mini-btn--active"
              disabled={!canExportCsv || exportingCsv}
              title="Exporta selecionadas; se não houver seleção, exporta resultados filtrados."
              onClick={handleExportCsv}
            >
              {exportingCsv ? 'Exportando…' : 'Exportar CSV'}
            </button>
          </div>

        <ConsultorSelectionBar
          selectedCount={selectedCount}
          selectionBarSummary={selectionBarSummary}
          onGerarRelatorioTriagem={onGerarRelatorioTriagem}
          onGerarPreProjetoSelecionados={handleGerar}
          onClearOpportunitySelection={onClearOpportunitySelection}
          variant="sticky"
        />
        </div>

        <div className="consultor-all-opps-results">
          <div className="consultor-all-opps-results-scroll">
            {showPartial && !portfolioStatus?.message ? (
              <p className="consultor-partial-hint consultor-partial-hint--inline" role="status">
                Prévia — completando lista…
              </p>
            ) : null}

            {showStatusInModal ? (
              <div
                className={`consultor-opps-status consultor-opps-status--${statusKind || 'loading'}`}
                role="status"
              >
                <p>{statusMessage}</p>
              </div>
            ) : null}

            {loading && !hasPortfolioData && !showStatusInModal ? (
              <div className="consultor-opps-status consultor-opps-status--loading" role="status">
                <p>Calculando oportunidades para este cliente…</p>
              </div>
            ) : null}

            {displayError && !loading ? (
              <div className="consultor-opps-status consultor-opps-status--warn" role="alert">
                <p>{displayError}</p>
                {onOpenRadar ? (
                  <div className="consultor-opps-status-actions">
                    <button type="button" className="consultor-opp-sheet-btn" onClick={onOpenRadar}>
                      Abrir no Radar
                    </button>
                  </div>
                ) : null}
              </div>
            ) : null}

            {!loading && !displayError && filteredMatches.length === 0 ? (
              <p className="consultor-empty-matches">Nenhuma oportunidade para os filtros atuais.</p>
            ) : null}

            {!displayError && visibleMatches.length > 0 ? (
              viewMode === 'table' ? (
                <ConsultorOpportunitiesTable
                  matches={visibleMatches}
                  selectedKeys={selectedSet}
                  onToggleSelect={handleToggle}
                  onOpenRadar={onOpenRadar}
                />
              ) : (
                <ul className="consultor-all-opps-list consultor-all-opps-list--sheet">
                  {visibleMatches.map((row) => {
                    const selKey = getOpportunitySelectionKey(row);
                    return (
                      <ConsultorOpportunityCompactRow
                        key={selKey}
                        variant="sheet"
                        row={row}
                        isSelected={selectedSet.has(selKey)}
                        onToggleSelect={handleToggle}
                        onOpenRadar={onOpenRadar}
                      />
                    );
                  })}
                </ul>
              )
            ) : null}

            {!displayError && hasMore ? (
              <div className="consultor-all-opps-more">
                <button type="button" className="consultor-opp-sheet-btn consultor-all-opps-more-btn" onClick={handleShowMore}>
                  Mostrar mais ({filteredMatches.length - visibleCap})
                </button>
              </div>
            ) : null}
          </div>

          <p className="consultor-all-opps-footer-hint">
            Até {MAX_PREPROJECT_OPPORTUNITIES} oportunidades por pré-projeto.
          </p>
        </div>
      </div>
    </Modal>
  );
}
