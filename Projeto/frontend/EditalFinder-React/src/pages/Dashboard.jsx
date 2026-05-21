import { useState, useEffect, useCallback, useMemo } from 'react';
import * as XLSX from 'xlsx';
import Header from '../components/layout/Header';
import EditalCard from '../components/dashboard/EditalCard';
import EditaisFiltersSidebar from '../components/dashboard/EditaisFiltersSidebar';
import EditaisStatsBar from '../components/dashboard/EditaisStatsBar';
import ActiveFiltersChips from '../components/dashboard/ActiveFiltersChips';
import EditalDetailsModal from '../components/dashboard/EditalDetailsModal';
import { dataService } from '../services/dataService';
import { formatCurrency, formatDateLoose } from '../utils/formatters';
import { useSettings } from '../contexts/SettingsContext';
import { exportLandscapeTablePdf, formatDashboardFiltersForPdf } from '../services/pdfExportService';
import {
  filterCatalog,
  INITIAL_SIDEBAR_FILTERS,
  loosenSidebarForFacet,
  rollupFacet,
  summarizeCatalogFlags,
} from '../utils/edital/filtersEngine';
import { tokenizeSearchQuery } from '../utils/edital/search';
import { SORT_OPTIONS, sortEditais } from '../utils/edital/scoring';
import { coerceStringArray } from '../utils/edital/coerceArrays';
import { getFonte } from '../utils/edital/editalFieldHelpers';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useEditaisPagePrefs } from '../hooks/useEditaisPagePrefs';
import { useEditalFavorites } from '../hooks/useEditalFavorites';
import {
  getDeadlineAlertBadgeVariant,
  getDeadlineAlertLabel,
  getDeadlineAlertStatus,
} from '../utils/deadlineAlerts';
import { logEditaisVisibilityDev } from '../utils/edital/editalVisibility';

const FAVORITES_LS = 'editais_favoritos_v1';

function loadFavoriteIds() {
  try {
    const raw = JSON.parse(localStorage.getItem(FAVORITES_LS) || '[]');
    return new Set(Array.isArray(raw) ? raw.map(String) : []);
  } catch {
    return new Set();
  }
}

function saveFavoriteIds(set) {
  localStorage.setItem(FAVORITES_LS, JSON.stringify([...set]));
}

function buildFilterSuggestions(totalOriginal, dbg, _filters, searchQuery = '') {
  const out = [];
  if (totalOriginal === 0) {
    out.push(
      'Nenhum edital recebido do banco. Verifique a conexão ou a view public.vw_editais_front.',
    );
    return out;
  }
  if (!dbg) return out;

  const t = (k) => Number(dbg[k] ?? 0);

  if (t('removedBy_toggleSoPdf') > 80)
    out.push('Desative “Mostrar apenas com PDF” na barra lateral.');
  if (t('removedBy_toggleAltaQualidade') > 80)
    out.push('Desative “Apenas alta qualidade” na barra lateral.');
  if (t('removedBy_prazoVencido') > 800) out.push('Ative “Incluir encerrados” na barra lateral.');
  if (t('removedBy_suspeito') > totalOriginal * 0.5) out.push('Ative “Incluir suspeitos” na barra lateral.');
  if (t('removedBy_tituloRuidoso') > totalOriginal * 0.8)
    out.push('Em preferências, marque “Mostrar títulos ruidosos…” para rever itens ocultos como ruído.');
  if (t('removedBy_advancedSidebar') > 400)
    out.push('Limpe filtros específicos (tipo, fonte, área, valores) ou use “Relaxar filtros”.');
  if (String(searchQuery).trim() && t('removedBy_buscaTokens') > totalOriginal * 0.5) {
    out.push('A busca no topo está excluindo muitos itens; esvazie o campo ou use termos mais amplos.');
  }

  const rest = dbg.final ?? 0;
  if (rest === 0 && totalOriginal > 50 && !out.length) {
    out.push('Reveja filtros rápidos na sidebar e o campo de busca no topo.');
  }
  return out;
}

export default function Dashboard() {
  const { settings } = useSettings();
  const { prefs, updatePrefs } = useEditaisPagePrefs();
  const favHook = useEditalFavorites();
  const favoritosRemote = favHook.favoritosRemoteEnabled;

  const [allEditais, setAllEditais] = useState([]);
  const [loading, setLoading] = useState(true);
  const [globalSearchRaw, setGlobalSearchRaw] = useState('');
  const [showFiltersMobile, setShowFiltersMobile] = useState(false);
  const [filters, setFilters] = useState(() => INITIAL_SIDEBAR_FILTERS());
  const [sortId, setSortId] = useState('relevantes');
  const [visibleCount, setVisibleCount] = useState(() => prefs.pageSize || 40);
  const [detailEdital, setDetailEdital] = useState(null);
  const [exportScope, setExportScope] = useState('filtered');
  const [favIds, setFavIds] = useState(loadFavoriteIds);
  const [showPipelineDebugPanel, setShowPipelineDebugPanel] = useState(false);

  const debouncedSearch = useDebouncedValue(globalSearchRaw, 300);
  const searchTokens = useMemo(() => tokenizeSearchQuery(debouncedSearch), [debouncedSearch]);

  useEffect(() => {
    setVisibleCount(Number(prefs.pageSize) || 40);
  }, [prefs.pageSize]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await dataService.getEditais();
        const arr = Array.isArray(data) ? data : [];
        setAllEditais(arr);
        if (import.meta.env.DEV) {
          logEditaisVisibilityDev(arr);
          console.info('[Editais] recebidos do banco:', arr.length);
          console.info('[Editais] amostra:', arr.slice(0, 3).map((e) => ({ id: e?.id, titulo: e?.titulo?.slice?.(0, 60), ativo: e?.ativo })));
          const fapesc = arr.filter((e) =>
            String(e.fonte_recurso_display || e.orgao || e.fonte_raw || '')
              .toUpperCase()
              .includes('FAPESC'),
          );
          if (fapesc.length) {
            console.info(
              '[Editais][DEV][FAPESC] classificação (amostra até 8)',
              fapesc.slice(0, 8).map((e) => ({
                id_edital: e.idNumerico ?? e.id_edital,
                titulo: (e.titulo || '').slice(0, 72),
                fonte_recurso: e.fonte_recurso_display || e.orgao,
                setor_estrategico: e.setor_estrategico_raw,
                setor_economico: e.setor_economico_raw,
                area: e.area,
                area_tecnologica: e.area_tecnologica_raw,
                tags: e.tags,
                extras_keys:
                  e.extras_raw && typeof e.extras_raw === 'object' && !Array.isArray(e.extras_raw)
                    ? Object.keys(e.extras_raw).slice(0, 15)
                    : undefined,
              })),
            );
          }
        }
      } catch (error) {
        console.error('Erro ao carregar editais:', error?.message || error);
        setAllEditais([]);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const pagePrefs = useMemo(() => ({
    showRuidos: !!prefs.showRuidos,
  }), [prefs.showRuidos]);

  const filteredOut = useMemo(
    () =>
      filterCatalog({
        catalog: allEditais,
        sidebar: filters,
        searchTokens,
        pagePrefs,
      }),
    [allEditais, filters, searchTokens, pagePrefs],
  );

  const filteredCatalog = filteredOut.filtered;

  const filteredEditaisRaw = useMemo(() => {
    let list = filteredCatalog;
    if (filters.toggleSomenteFavoritos) {
      if (favoritosRemote) {
        list = list.filter((e) => favHook.isFavorite(e));
      } else {
        list = list.filter((e) => favIds.has(String(e.id)));
      }
    }
    return list;
  }, [
    filteredCatalog,
    filters.toggleSomenteFavoritos,
    favoritosRemote,
    favHook.favorites,
    favHook.isFavorite,
    favIds,
  ]);
  const hiddenMetaBaseline = filteredOut.hiddenMeta ?? {};
  const filterPipelineDebug = filteredOut.filterDebug ?? {};

  const emptySuggestions = useMemo(
    () =>
      buildFilterSuggestions(
        allEditais.length,
        filterPipelineDebug,
        filters,
        debouncedSearch,
      ),
    [allEditais.length, filterPipelineDebug, filters, debouncedSearch],
  );

  useEffect(() => {
    if (!import.meta.env.DEV || loading) return;
    const dbg = filterPipelineDebug;
    const d = dbg || {};
    console.table({
      totalOriginal: d.totalOriginal,
      depoisAtivo: d.after_ativo,
      removedByAtivo: d.removedBy_ativo,
      depoisSuspeitos: d.after_suspeito,
      depoisEncerrados: d.after_prazoVencido,
      depoisTituloRuidoso: d.after_tituloRuidoso,
      depoisTogglePdf: d.after_toggleSoPdf,
      depoisAltaQualidade: d.after_toggleAltaQualidade,
      depoisBusca: d.after_buscaTokens,
      final: d.final,
    });
    if (typeof filterPipelineDebug.final === 'number' && filterPipelineDebug.totalOriginal > 0) {
      console.info('[Editais] filterDebug objeto:', filterPipelineDebug);
    }
  }, [loading, filters, debouncedSearch, filterPipelineDebug, allEditais.length]);

  const sortedFiltered = useMemo(
    () => sortEditais(filteredEditaisRaw, sortId, prefs),
    [filteredEditaisRaw, sortId, prefs],
  );

  const visibleEditais = useMemo(
    () => sortedFiltered.slice(0, visibleCount),
    [sortedFiltered, visibleCount],
  );

  const statsFiltered = useMemo(() => summarizeCatalogFlags(filteredEditaisRaw), [filteredEditaisRaw]);

  const facetTipoPool = useMemo(
    () =>
      filterCatalog({
        catalog: allEditais,
        sidebar: loosenSidebarForFacet(filters, 'tipoRecurso'),
        searchTokens,
        pagePrefs,
      }).filtered,
    [allEditais, filters, searchTokens, pagePrefs],
  );
  const facetFontePool = useMemo(
    () =>
      filterCatalog({
        catalog: allEditais,
        sidebar: loosenSidebarForFacet(filters, 'fontes'),
        searchTokens,
        pagePrefs,
      }).filtered,
    [allEditais, filters, searchTokens, pagePrefs],
  );
  const facetAreaPool = useMemo(
    () =>
      filterCatalog({
        catalog: allEditais,
        sidebar: loosenSidebarForFacet(filters, 'areas'),
        searchTokens,
        pagePrefs,
      }).filtered,
    [allEditais, filters, searchTokens, pagePrefs],
  );

  const facetTipoCounts = useMemo(() => {
    const m = new Map();
    for (const [lbl, cnt] of rollupFacet(
      facetTipoPool,
      (e) => String(e.tipo_recurso_raw || 'sem_tipo').toLowerCase(),
    )) {
      m.set(String(lbl).toLowerCase(), cnt);
    }
    return m;
  }, [facetTipoPool]);

  const facets = useMemo(
    () => ({
      tipoRecurso: rollupFacet(facetTipoPool, (e) =>
        String(e.tipo_recurso_raw ?? 'sem_tipo').toLowerCase(),
      ),
      tipoRecursoCounts: facetTipoCounts,
      fonte: rollupFacet(facetFontePool, (e) =>
        String(getFonte(e)).trim() === 'Fonte não informada' ? '— não informado' : getFonte(e),
      ),
      area: rollupFacet(facetAreaPool, (e) => {
        const a = coerceStringArray(e.area);
        return a.length ? a[0].trim().slice(0, 42) : '— não informado';
      }),
    }),
    [facetTipoPool, facetFontePool, facetAreaPool, facetTipoCounts],
  );

  const dynamicAreas = useMemo(() => {
    const capped = facets.area.slice(0, 40);
    return capped.map(([label, count]) => ({ label: label === '— não informado' ? 'Sem área texto' : label, count }));
  }, [facets.area]);

  const uniquePaises = useMemo(() => {
    const s = new Set();
    allEditais.forEach((e) => {
      const p = String(e.pais_raw ?? '').trim();
      if (p) s.add(p);
    });
    return [...s].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  }, [allEditais]);

  const uniqueUFs = useMemo(() => {
    const s = new Set();
    allEditais.forEach((e) => {
      const u = String(e.uf_raw ?? '').trim().toUpperCase();
      if (u.length === 2) s.add(u);
    });
    return [...s].sort();
  }, [allEditais]);

  const resetFilters = useCallback(() => {
    setFilters(INITIAL_SIDEBAR_FILTERS());
  }, []);

  /** Relaxa só PDF/qualidade/busca conforme UX — mantém incluir encerrados/suspeitos e filtros avançados como estão */
  const relaxFilters = useCallback(() => {
    setGlobalSearchRaw('');
    setFilters((f) => ({
      ...f,
      toggleSoPdf: false,
      toggleAltaQualidade: false,
      toggleSomenteFavoritos: false,
    }));
  }, []);

  const mostrarTudoPossivel = useCallback(() => {
    setGlobalSearchRaw('');
    setFilters(() => ({
      ...INITIAL_SIDEBAR_FILTERS(),
      toggleIncluirEncerrados: true,
      toggleIncluirSuspeitos: true,
      toggleMostrarInativos: true,
      toggleSoPdf: false,
      toggleAltaQualidade: false,
      toggleSomenteFavoritos: false,
    }));
    updatePrefs({ showRuidos: true });
  }, [updatePrefs]);

  const toggleLegacyFavorite = useCallback((id) => {
    setFavIds((prev) => {
      const next = new Set(prev);
      const k = String(id);
      next.has(k) ? next.delete(k) : next.add(k);
      saveFavoriteIds(next);
      return next;
    });
  }, []);

  const favoritosCountLabel = useMemo(() => {
    if (favoritosRemote) return favHook.favorites.length;
    return favIds.size;
  }, [favoritosRemote, favHook.favorites, favIds]);

  const handleCardFavorite = useCallback(
    async (edital) => {
      if (!edital) return;
      if (favoritosRemote) {
        if (favHook.needsLoginForFavorites) {
          window.alert(favHook.loginMessage || 'Entre na sua conta para favoritar editais.');
          return;
        }
        const res = await favHook.toggleFavorite(edital, { contexto: 'editais' });
        if (res?.needsLogin) {
          window.alert(res.message || favHook.loginMessage);
        }
        return;
      }
      toggleLegacyFavorite(edital.id);
    },
    [favoritosRemote, favHook, toggleLegacyFavorite],
  );

  const isEditalFavorite = useCallback(
    (edital) => {
      if (favoritosRemote) return favHook.isFavorite(edital);
      return favIds.has(String(edital?.id));
    },
    [favoritosRemote, favHook.isFavorite, favIds],
  );

  /* Chips removíveis -------------------------------------------------------- */
  const chips = useMemo(() => {
    const out = [];
    const rm = (fn) => () => fn();

    if (filters.toggleIncluirEncerrados) {
      out.push({
        key: 'enc',
        label: 'Incluir encerrados',
        onRemove: rm(() => setFilters((f) => ({ ...f, toggleIncluirEncerrados: false }))),
      });
    }
    if (filters.toggleIncluirSuspeitos) {
      out.push({
        key: 'sus',
        label: 'Incluir suspeitos',
        onRemove: rm(() => setFilters((f) => ({ ...f, toggleIncluirSuspeitos: false }))),
      });
    }
    if (filters.toggleMostrarInativos) {
      out.push({
        key: 'ina',
        label: 'Mostrar inativos',
        onRemove: rm(() => setFilters((f) => ({ ...f, toggleMostrarInativos: false }))),
      });
    }
    if (filters.toggleSoPdf) {
      out.push({
        key: 'pdf',
        label: 'Apenas com PDF',
        onRemove: rm(() => setFilters((f) => ({ ...f, toggleSoPdf: false }))),
      });
    }
    if (filters.toggleAltaQualidade) {
      out.push({
        key: 'q',
        label: 'Apenas alta qualidade',
        onRemove: rm(() => setFilters((f) => ({ ...f, toggleAltaQualidade: false }))),
      });
    }
    if (filters.toggleSomenteFavoritos) {
      out.push({
        key: 'fav',
        label: 'Somente favoritos',
        onRemove: rm(() => setFilters((f) => ({ ...f, toggleSomenteFavoritos: false }))),
      });
    }
    if (filters.tipoRecurso) {
      out.push({
        key: 'tipoR',
        label: `Tipo: ${filters.tipoRecurso}`,
        onRemove: rm(() => setFilters((f) => ({ ...f, tipoRecurso: '' }))),
      });
    }
    if (filters.tipoOportunidade) {
      out.push({
        key: 'tipoOp',
        label: `Oport.: ${filters.tipoOportunidade}`,
        onRemove: rm(() => setFilters((f) => ({ ...f, tipoOportunidade: '' }))),
      });
    }
    if (filters.fonteBusca || Object.values(filters.fontesSelectedKeys || {}).some(Boolean)) {
      out.push({
        key: 'fonte',
        label: 'Fonte filtrada',
        onRemove: rm(() =>
          setFilters((f) => ({
            ...f,
            fonteBusca: '',
            fontesSelectedKeys: {},
          })),
        ),
      });
    }
    Object.entries(filters.areas || {})
      .filter(([, v]) => v)
      .forEach(([k]) =>
        out.push({
          key: `ar-${k}`,
          label: `Área: ${k}`,
          onRemove: rm(() =>
            setFilters((f) => ({
              ...f,
              areas: { ...f.areas, [k]: false },
            })),
          ),
        }),
      );
    if (filters.regiaoLegacy) {
      out.push({
        key: 'rg',
        label: `Região: ${filters.regiaoLegacy}`,
        onRemove: rm(() => setFilters((f) => ({ ...f, regiaoLegacy: '' }))),
      });
    }
    return out;
  }, [filters]);

  /** Linhas extras no PDF sobre ordenação / escopo. */
  function buildExportFilterLines() {
    const base = formatDashboardFiltersForPdf({ ...filters, resourceType: filters.resourceTypeLegacy, regiao: filters.regiaoLegacy }, debouncedSearch);
    const extras = [`Ordenação: ${sortId}`, `Exportação: ${exportScope}`];
    return [...extras, ...base.filter((ln) => !extras.includes(ln))];
  }

  function resolveExportDataset() {
    if (exportScope === 'filtered') return sortedFiltered;
    if (exportScope === 'favorites') {
      if (favoritosRemote) return sortedFiltered.filter((e) => isEditalFavorite(e));
      return sortedFiltered.filter((e) => favIds.has(String(e.id)));
    }
    /* all carregados */
    return allEditais;
  }

  const handleExportPDF = async () => {
    try {
      const rows = resolveExportDataset();
      if (!rows.length) {
        alert('Nenhum edital para exportar.');
        return;
      }
      const cols = [
        'Título',
        'Fonte',
        'Tipo oport.',
        'Tipo recurso',
        'Perfil',
        'Setor',
        'Área tecnológica',
        'Prazo',
        'Valor',
        'Status',
        'Qualidade',
        'Link',
        'PDF',
      ];
      const tableRows = rows.map((e) => [
        e.titulo,
        getFonte(e),
        e.tipo_oportunidade_raw || '',
        e.tipo_recurso_raw || e.tipoRecurso || '',
        coerceStringArray(e.perfil_ideal_raw).slice(0, 4).join('; '),
        coerceStringArray(e.setor_estrategico_raw).slice(0, 4).join('; '),
        coerceStringArray(e.area_tecnologica_raw).slice(0, 4).join('; '),
        (e.prazo_envio_raw || e.dataLimite) ? formatDateLoose(e.prazo_envio_raw || e.dataLimite) : '',
        formatCurrency(Number(e.valor_principal_num ?? e.valor ?? 0)),
        [e.validacao_status_raw, e.situacao_raw].filter(Boolean).join(' / ') || '—',
        e.qualidade_dado_raw != null ? `${e.qualidade_dado_raw}` : '—',
        e.link_original || e.linkOriginal || '',
        e.pdf_url_raw || e.pdfUrl || '',
      ]);

      alert(`Exportando ${rows.length} editais (${exportScope}).`);

      await exportLandscapeTablePdf({
        fileNameStem: `editais_${exportScope}`,
        reportTitle: 'Relatório de editais',
        brandName: settings.logoText,
        logoImage: settings.logoImage,
        filterLines: buildExportFilterLines(),
        totalExported: rows.length,
        totalInDataset: allEditais.length,
        tableHead: [cols],
        tableBody: tableRows,
        autoTableOptions: {},
      });
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      alert('Erro ao gerar PDF.');
    }
  };

  const handleExportExcel = () => {
    try {
      const rows = resolveExportDataset();
      if (!rows.length) {
        alert('Nenhum edital para exportar.');
        return;
      }
      alert(`Exportando ${rows.length} editais (${exportScope}).`);
      const data = rows.map((e) => ({
        Título: e.titulo,
        Fonte: getFonte(e),
        tipo_oportunidade: e.tipo_oportunidade_raw || '',
        tipo_recurso: e.tipo_recurso_raw || e.tipoRecurso || '',
        perfil_ideal: coerceStringArray(e.perfil_ideal_raw).join('; '),
        setor_estrategico: coerceStringArray(e.setor_estrategico_raw).join('; '),
        area_tecnologica: coerceStringArray(e.area_tecnologica_raw).join('; '),
        prazo_envio: e.prazo_envio_raw || e.dataLimite || '',
        valor: Number(e.valor_principal_num ?? 0),
        situacao_validacao:
          `${e.validacao_status_raw ?? ''}${e.validacao_status_raw && e.situacao_raw ? ' · ' : ''}${e.situacao_raw ?? ''}`.trim() ||
          '—',
        qualidade_dado: e.qualidade_dado_raw ?? '',
        link: e.link_original || e.linkOriginal || '',
        pdf_url: e.pdf_url_raw || e.pdfUrl || '',
      }));
      const worksheet = XLSX.utils.json_to_sheet(data);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Editais');
      XLSX.writeFile(workbook, `editais_${exportScope}_${new Date().toISOString().slice(0, 10)}.xlsx`);
    } catch (error) {
      console.error('Erro ao gerar Excel:', error);
      alert('Erro ao gerar planilha.');
    }
  };

  const hasMoreOnPage = visibleCount < sortedFiltered.length;

  return (
    <>
      <Header onSearch={setGlobalSearchRaw} />

      <div className={`dashboard-container editais-dash-v2 prefs-density-${prefs.density || 'normal'}`}>
        <button
          type="button"
          className="filter-toggle-mobile"
          onClick={() => setShowFiltersMobile(!showFiltersMobile)}
        >
          {showFiltersMobile ? '✕ Fechar Filtros' : '🔍 Abrir Filtros'}
        </button>

        <div className={`sidebar ${!showFiltersMobile ? 'mobile-hidden' : ''}`}>
          <EditaisFiltersSidebar
            filters={filters}
            setFilters={setFilters}
            facets={facets}
            prefs={prefs}
            updatePrefs={updatePrefs}
            uniquePaises={uniquePaises}
            uniqueUFs={uniqueUFs}
            dynamicAreas={dynamicAreas}
            onReset={resetFilters}
          />
        </div>

        <main className="main-content">
          <div className="content-header editai-dash-header">
            <h2>Editais Disponíveis</h2>
            <div className="content-actions editai-dash-actions">
              <EditaisStatsBar
                filteredCount={sortedFiltered.length}
                catalogCount={allEditais.length}
                abertosNaLista={statsFiltered.abertos}
                comPdfNaLista={statsFiltered.comPdf}
                altaQualNaLista={statsFiltered.altaQualidade}
                showPdfToggle={!!filters.toggleSoPdf}
                showQualToggle={!!filters.toggleAltaQualidade}
                semPdfOcultos={hiddenMetaBaseline.semPdfOcultos}
                baixaQualOcultos={hiddenMetaBaseline.baixaQualOcultos}
                encerradosOcultosHint={
                  !filters.toggleIncluirEncerrados ? hiddenMetaBaseline.encerradosOcultos : 0
                }
                suspeitosOcultosHint={
                  !filters.toggleIncluirSuspeitos ? hiddenMetaBaseline.suspOcultos : 0
                }
                ruidosOcultosHint={!prefs.showRuidos ? hiddenMetaBaseline.ruidosOcultos : 0}
              />

              <div className="editais-quick-actions" aria-label="Ações rápidas de filtro">
                <button type="button" className="btn-relax-filters" onClick={relaxFilters}>
                  Relaxar filtros
                </button>
                <button
                  type="button"
                  className={`editais-fav-filter-btn ${filters.toggleSomenteFavoritos ? 'ativo' : ''}`}
                  aria-pressed={filters.toggleSomenteFavoritos}
                  title={
                    favoritosRemote
                      ? 'Mostrar apenas editais salvos como favoritos no Supabase'
                      : 'Mostrar apenas favoritos neste navegador'
                  }
                  onClick={() =>
                    setFilters((f) => ({ ...f, toggleSomenteFavoritos: !f.toggleSomenteFavoritos }))
                  }
                >
                  {filters.toggleSomenteFavoritos ? '★' : '☆'} Favoritos ({favoritosCountLabel})
                </button>
                {import.meta.env.DEV ? (
                  <>
                    <button type="button" className="btn-show-all-debug" onClick={mostrarTudoPossivel}>
                      Mostrar tudo
                    </button>
                    <button
                      type="button"
                      className="btn-pipeline-debug-toggle"
                      onClick={() => setShowPipelineDebugPanel((v) => !v)}
                    >
                      {showPipelineDebugPanel ? 'Ocultar' : 'Ver'} debug do pipeline
                    </button>
                  </>
                ) : null}
              </div>

              <div className="export-toolbar-row">
                <label className="export-scope-label">
                  Exportar:&nbsp;
                  <select value={exportScope} onChange={(e) => setExportScope(e.target.value)}>
                    <option value="filtered">Só lista filtrada</option>
                    <option value="all">Todos carregados</option>
                    <option value="favorites">Somente favoritos (na lista atual)</option>
                  </select>
                </label>
              </div>

              <div className="export-toolbar-row align-end">
                <label className="sort-label">
                  Ordenar:&nbsp;
                  <select value={sortId} onChange={(e) => setSortId(e.target.value)}>
                    {SORT_OPTIONS.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </label>
                <button type="button" onClick={handleExportPDF} className="btn-export">
                  📄 PDF
                </button>
                <button
                  type="button"
                  onClick={handleExportExcel}
                  className="btn-export btn-export-sheet"
                  style={{ backgroundColor: '#27ae60' }}
                >
                  📊 Planilha
                </button>
              </div>
            </div>
          </div>

          <ActiveFiltersChips chips={chips} onClearAll={resetFilters} />

          {favoritosRemote && favHook.error ? (
            <div className="editais-fav-toggle-error" role="alert">
              <span>
                Não foi possível carregar favoritos:{' '}
                {favHook.error?.message || favHook.error?.details || String(favHook.error)}
              </span>
            </div>
          ) : null}

          {favoritosRemote && favHook.toggleError ? (
            <div className="editais-fav-toggle-error" role="alert">
              <span>Não foi possível atualizar favoritos: {favHook.toggleError}</span>
              <button
                type="button"
                className="editais-fav-toggle-error-dismiss"
                onClick={() => favHook.clearToggleError()}
              >
                Fechar
              </button>
            </div>
          ) : null}

          {favoritosRemote && favHook.favoriteAlertsSummary.alert7dCount > 0 ? (
            <div className="editais-fav-deadline-banner" role="status">
              <span>
                Você tem <strong>{favHook.favoriteAlertsSummary.alert7dCount}</strong> edital(is) favorito(s)
                vencendo nos próximos 7 dias.
              </span>
              <button
                type="button"
                className="editais-fav-deadline-banner-btn"
                onClick={() => setFilters((f) => ({ ...f, toggleSomenteFavoritos: true }))}
              >
                Ver favoritos
              </button>
            </div>
          ) : null}

          {import.meta.env.DEV && showPipelineDebugPanel ? (
            <div className="editais-pipeline-debug-panel">
              <pre tabIndex={0}>{JSON.stringify(filterPipelineDebug, null, 2)}</pre>
            </div>
          ) : null}

          {loading ? (
            <div className="dashboard-skel-wrap">
              <div className="dashboard-skeleton-grid">
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <div key={n} className="dashboard-skeleton-card" />
                ))}
              </div>
            </div>
          ) : (
            <>
              <div className="editais-grid">
                {visibleEditais.map((edital) => {
                  const st = getDeadlineAlertStatus(edital);
                  const deadlineFavoriteBadge =
                    favoritosRemote && isEditalFavorite(edital)
                      ? {
                          label: getDeadlineAlertLabel(st),
                          variant: getDeadlineAlertBadgeVariant(st),
                        }
                      : null;
                  return (
                    <EditalCard
                      key={edital.id}
                      edital={edital}
                      searchTokensNorm={searchTokens}
                      isFavorite={isEditalFavorite(edital)}
                      onToggleFavorite={handleCardFavorite}
                      deadlineFavoriteBadge={deadlineFavoriteBadge}
                      density={prefs.density}
                      onOpenDetails={setDetailEdital}
                    />
                  );
                })}
              </div>

              {!sortedFiltered.length && (
                <div className="empty-state editais-empty-state">
                  {filters.toggleSomenteFavoritos &&
                  favoritosRemote &&
                  !favHook.loading &&
                  favHook.favorites.length === 0 ? (
                    <>
                      <h3>Nenhum edital favoritado ainda.</h3>
                      <p>Clique na estrela de um edital para acompanhá-lo.</p>
                    </>
                  ) : filters.toggleSomenteFavoritos && !favoritosRemote && favIds.size === 0 ? (
                    <>
                      <h3>Nenhum edital favoritado ainda.</h3>
                      <p>Clique na estrela de um edital para acompanhá-lo neste navegador.</p>
                    </>
                  ) : (
                    <>
                      <h3>Nenhum edital encontrado com os filtros atuais.</h3>
                      {emptySuggestions.length > 0 ? (
                        <ul className="empty-state-suggestions">
                          {emptySuggestions.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>Ajuste os filtros na barra lateral ou as preferências de ruídos.</p>
                      )}
                    </>
                  )}
                  <div className="editais-empty-actions">
                    <button type="button" className="btn-view btn-relax-filters-empty" onClick={relaxFilters}>
                      Relaxar filtros
                    </button>
                    {import.meta.env.DEV ? (
                      <button type="button" className="btn-view" onClick={mostrarTudoPossivel}>
                        Mostrar tudo
                      </button>
                    ) : null}
                  </div>
                </div>
              )}

              {hasMoreOnPage && (
                <div className="load-more-dash">
                  <button
                    type="button"
                    className="btn-view"
                    onClick={() =>
                      setVisibleCount((v) =>
                        Math.min(sortedFiltered.length, v + (prefs.pageSize || 40)),
                      )
                    }
                  >
                    Carregar mais ({sortedFiltered.length - visibleCount} restantes)
                  </button>
                </div>
              )}
            </>
          )}
        </main>

        {detailEdital != null && (
          <EditalDetailsModal edital={detailEdital} onClose={() => setDetailEdital(null)} />
        )}
      </div>
    </>
  );
}
