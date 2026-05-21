import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { downloadConsultorPortfolioCsv } from '../../utils/consultor/exportConsultorPortfolioCsv';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';

/**
 * Menu Exportar no header do cliente (Workspace).
 */
export default function ConsultorExportMenu({
  cliente = null,
  topMatches = [],
  selectedRows = [],
  topMatchesReady = false,
  onOpenAllOpportunities,
  onCsvExported,
}) {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const rootRef = useRef(null);
  const menuId = useId();

  const clienteNome = cliente?.nome_empresa || cliente?.razao_social || '';
  const clienteId = cliente?.id_cliente ?? null;
  const safeTop = Array.isArray(topMatches) ? topMatches : [];
  const safeSelected = Array.isArray(selectedRows) ? selectedRows : [];
  const selectedCount = safeSelected.length;
  const canTop20 = topMatchesReady && safeTop.length > 0;
  const canSelected = selectedCount > 0;

  const closeMenu = useCallback(() => setOpen(false), []);

  const toggleMenu = useCallback(() => {
    setOpen((prev) => {
      const next = !prev;
      if (next) {
        logConsultorWorkspace('export_menu_open', { id_cliente: clienteId });
      }
      return next;
    });
  }, [clienteId]);

  useEffect(() => {
    if (!open) return undefined;

    const onDocMouseDown = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) {
        closeMenu();
      }
    };
    const onKeyDown = (e) => {
      if (e.key === 'Escape') closeMenu();
    };

    document.addEventListener('mousedown', onDocMouseDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onDocMouseDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open, closeMenu]);

  const runCsvExport = useCallback(
    async ({ matches, filenamePrefix, logStart }) => {
      if (exporting || !matches?.length) return;
      logConsultorWorkspace(logStart, {
        id_cliente: clienteId,
        count: matches.length,
      });
      setExporting(true);
      closeMenu();
      try {
        const { filename, rowCount } = downloadConsultorPortfolioCsv({
          matches,
          clienteNome,
          filenamePrefix,
        });
        logConsultorWorkspace('export_csv_success', {
          id_cliente: clienteId,
          source: logStart,
          count: rowCount,
          filename,
        });
        onCsvExported?.({ rowCount, filenamePrefix, filename });
      } catch (e) {
        logConsultorWorkspace('export_csv_error', {
          id_cliente: clienteId,
          source: logStart,
          message: e?.message || String(e),
        });
        alert('Não foi possível exportar o CSV. Tente novamente.');
      } finally {
        setExporting(false);
      }
    },
    [clienteId, clienteNome, closeMenu, exporting, onCsvExported],
  );

  const handleTop20 = useCallback(() => {
    runCsvExport({
      matches: safeTop,
      filenamePrefix: 'carteira_top20',
      logStart: 'export_top20_csv_start',
    });
  }, [runCsvExport, safeTop]);

  const handleSelected = useCallback(() => {
    runCsvExport({
      matches: safeSelected,
      filenamePrefix: 'carteira_selecionadas',
      logStart: 'export_selected_csv_start',
    });
  }, [runCsvExport, safeSelected]);

  const handleFiltered = useCallback(() => {
    logConsultorWorkspace('export_filtered_requested', { id_cliente: clienteId });
    closeMenu();
    onOpenAllOpportunities?.();
  }, [clienteId, closeMenu, onOpenAllOpportunities]);

  const handlePdfSoon = useCallback(() => {
    logConsultorWorkspace('export_pdf_soon_click', { id_cliente: clienteId });
  }, [clienteId]);

  return (
    <div className="consultor-export-menu" ref={rootRef}>
      <button
        type="button"
        className="btn-detalhes dash-action-outline consultor-export-menu-trigger"
        onClick={toggleMenu}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-controls={menuId}
        disabled={exporting}
      >
        Exportar
        <span className="consultor-export-menu-chevron" aria-hidden>
          ▾
        </span>
      </button>

      {open ? (
        <div
          id={menuId}
          className="consultor-export-menu-dropdown"
          role="menu"
          aria-label="Opções de exportação"
        >
          <button
            type="button"
            role="menuitem"
            className="consultor-export-menu-item"
            disabled={!canTop20 || exporting}
            title={canTop20 ? 'Exporta o top 20 da visão rápida.' : 'Aguarde a carteira carregar.'}
            onClick={handleTop20}
          >
            Exportar top 20 CSV
          </button>
          <button
            type="button"
            role="menuitem"
            className="consultor-export-menu-item"
            disabled={!canSelected || exporting}
            title={
              canSelected
                ? `Exporta ${selectedCount} oportunidade${selectedCount === 1 ? '' : 's'} selecionada${selectedCount === 1 ? '' : 's'}.`
                : 'Selecione oportunidades para exportar esta opção.'
            }
            onClick={handleSelected}
          >
            Exportar selecionadas CSV
          </button>
          <button
            type="button"
            role="menuitem"
            className="consultor-export-menu-item"
            disabled={exporting || !onOpenAllOpportunities}
            title="Abre a carteira completa para aplicar filtros e exportar CSV."
            onClick={handleFiltered}
          >
            Abrir carteira completa para exportar filtradas
          </button>
          <div className="consultor-export-menu-divider" role="separator" />
          <button
            type="button"
            role="menuitem"
            className="consultor-export-menu-item consultor-export-menu-item--soon"
            disabled
            title="Em breve: exporte um relatório executivo para o cliente."
            onClick={handlePdfSoon}
          >
            Relatório executivo PDF — Em breve
          </button>
        </div>
      ) : null}
    </div>
  );
}
