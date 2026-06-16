import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { exportRowsToXlsx } from '../utils/export/spreadsheetExport';
import Header from '../components/layout/Header';
import FeedItemCard from '../components/feed/FeedItemCard';
import FeedSidebarFilters from '../components/feed/FeedSidebarFilters';
import { formatDate } from '../utils/formatters';
import { useSettings } from '../contexts/SettingsContext';
import { exportLandscapeTablePdf, formatFeedFiltersForPdf } from '../services/pdfExportService';

function applyFeedFilters(rows, sidebarFilters, globalSearch) {
  let result = [...rows];

  if (globalSearch?.trim()) {
    const g = globalSearch.toLowerCase();
    result = result.filter((r) => {
      const blob = [
        r.titulo,
        r.resumo,
        r.fonte,
        r.fonte_recurso,
        r.codigo_oportunidade,
        Array.isArray(r.tags) ? r.tags.join(' ') : '',
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return blob.includes(g);
    });
  }

  if (sidebarFilters.somenteAtivos) result = result.filter((r) => r.ativo === true);
  if (sidebarFilters.fonte_recurso) result = result.filter((r) => r.fonte_recurso === sidebarFilters.fonte_recurso);
  if (sidebarFilters.regiao) result = result.filter((r) => r.regiao === sidebarFilters.regiao);
  if (sidebarFilters.pais) result = result.filter((r) => r.pais === sidebarFilters.pais);
  if (sidebarFilters.validacao_status)
    result = result.filter((r) => r.validacao_status === sidebarFilters.validacao_status);
  if (sidebarFilters.tipo_conteudo) {
    result = result.filter((r) => {
      const t = r.tipo_conteudo || r.content_type || '';
      return t === sidebarFilters.tipo_conteudo;
    });
  }
  if (sidebarFilters.tag) result = result.filter((r) => (r.tags || []).some((t) => String(t) === sidebarFilters.tag));

  return result;
}

export default function FeedListaPage({ title, searchPlaceholder, exportBaseName, loadItems }) {
  const { settings } = useSettings();
  const fetcherRef = useRef(loadItems);
  fetcherRef.current = loadItems;

  const [allItems, setAllItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [globalSearch, setGlobalSearch] = useState('');
  const [showFiltersMobile, setShowFiltersMobile] = useState(false);
  const [sidebarFilters, setSidebarFilters] = useState({
    fonte_recurso: '',
    regiao: '',
    pais: '',
    validacao_status: '',
    tipo_conteudo: '',
    tag: '',
    somenteAtivos: false,
  });

  const handleFilterChange = useCallback((f) => {
    setSidebarFilters(f);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setLoadError(null);
      try {
        const data = await fetcherRef.current();
        if (!cancelled) setAllItems(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!cancelled) {
          setLoadError(e?.message || String(e));
          setAllItems([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const filteredItems = useMemo(
    () => applyFeedFilters(allItems, sidebarFilters, globalSearch),
    [allItems, sidebarFilters, globalSearch]
  );

  const handleExportPDF = async () => {
    try {
      if (filteredItems.length === 0) {
        alert('Nenhum item para exportar.');
        return;
      }

      const cols = ['Título', 'Link', 'Fonte recurso', 'Região', 'Prazo', 'Ativo'];
      const body = filteredItems.map((r) => [
        r.titulo || '',
        r.link || '',
        r.fonte_recurso || r.fonte || '',
        r.regiao || '',
        r.prazo_envio ? formatDate(r.prazo_envio) : '-',
        r.ativo === false ? 'Não' : 'Sim',
      ]);

      await exportLandscapeTablePdf({
        fileNameStem: exportBaseName,
        reportTitle: `Relatório — ${title}`,
        brandName: settings.logoText,
        logoImage: settings.logoImage,
        filterLines: formatFeedFiltersForPdf(sidebarFilters, globalSearch),
        totalExported: filteredItems.length,
        totalInDataset: allItems.length,
        tableHead: [cols],
        tableBody: body,
        autoTableOptions: {
          styles: { fontSize: 7, cellPadding: 1.5 },
          columnStyles: {
            0: { cellWidth: 52 },
            1: { cellWidth: 75 },
          },
        },
      });
    } catch (err) {
      console.error(err);
      alert('Erro ao gerar PDF. Verifique o console.');
    }
  };

  const handleExportExcel = async () => {
    if (filteredItems.length === 0) {
      alert('Nenhum item para exportar.');
      return;
    }
    const data = filteredItems.map((r) => ({
      Título: r.titulo,
      Link: r.link,
      Resumo: r.resumo,
      'Fonte recurso': r.fonte_recurso,
      Fonte: r.fonte,
      Região: r.regiao,
      País: r.pais,
      'Data publicação': r.data_publicacao ? formatDate(r.data_publicacao) : '',
      Prazo: r.prazo_envio ? formatDate(r.prazo_envio) : '',
      Ativo: r.ativo === false ? 'Não' : 'Sim',
      Validação: r.validacao_status,
    }));
    try {
      await exportRowsToXlsx(data, {
        sheetName: title.slice(0, 30),
        fileName: `${exportBaseName}_${new Date().toISOString().split('T')[0]}.xlsx`,
      });
    } catch (err) {
      console.error(err);
      alert('Erro ao gerar planilha.');
    }
  };

  return (
    <>
      <Header onSearch={setGlobalSearch} searchPlaceholder={searchPlaceholder} />
      <div className="dashboard-container">
        <button
          type="button"
          className="filter-toggle-mobile"
          onClick={() => setShowFiltersMobile(!showFiltersMobile)}
        >
          {showFiltersMobile ? '✕ Fechar Filtros' : '🔍 Abrir Filtros'}
        </button>

        <div className={`sidebar ${!showFiltersMobile ? 'mobile-hidden' : ''}`}>
          <FeedSidebarFilters items={allItems} onFilterChange={handleFilterChange} />
        </div>

        <main className="main-content">
          <div className="content-header">
            <h2>{title}</h2>
            <div className="content-actions" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <span className="editals-count">
                Mostrando {filteredItems.length} de {allItems.length} no banco
              </span>
              <button type="button" onClick={handleExportPDF} className="btn-export">📄 PDF</button>
              <button type="button" onClick={handleExportExcel} className="btn-export" style={{ backgroundColor: '#27ae60' }}>📊 Planilha</button>
            </div>
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '50px' }}>
              <h3>Carregando…</h3>
            </div>
          )}
          {!loading && loadError && (
            <div className="empty-state">
              <h3>Não foi possível carregar</h3>
              <p>{loadError}</p>
            </div>
          )}
          {!loading && !loadError && (
            <div className="editais-grid">
              {filteredItems.map((row) => (
                <FeedItemCard key={row.id} item={row} />
              ))}
              {filteredItems.length === 0 && (
                <div className="empty-state">
                  <h3>Nenhum item encontrado</h3>
                  <p>Use &quot;Limpar Filtros&quot; ou refine a busca.</p>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
