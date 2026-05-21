import { useState, useEffect, useMemo, useCallback } from 'react';
import Header from '../../components/layout/Header';
import LoadingState from '../../components/states/LoadingState';
import ErrorState from '../../components/states/ErrorState';
import EmptyState from '../../components/states/EmptyState';
import ConcursoCard from '../../components/cards/ConcursoCard';
import { fetchConcursos } from '../../services/concursosService';
import { ENABLE_CONCURSOS } from '../../config/env';
import { labelStatus } from '../../utils/concursos/concursosLabels';
import {
  FONTE_BANCA_OPTIONS,
  TIPO_INSTITUICAO_OPTIONS,
  TAB_DEFS,
  applyConcursosFilters,
  buildFilterOptions,
  computeConcursosStats,
  countActiveFilters,
  describeConcursosEmptyHint,
  filterByTab,
  getActiveFilterChips,
  getInitialConcursosFilters,
  removeFilterKey,
  sortConcursos,
} from '../../utils/concursos/concursosFilters';
import './ConcursosPage.css';

export { getInitialConcursosFilters };

function rowKey(row, idx) {
  if (row?.id_concurso != null) return `c-${row.id_concurso}`;
  return `i-${idx}`;
}

export default function ConcursosPage() {
  const [tab, setTab] = useState('all');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(getInitialConcursosFilters);
  const [showFiltersMobile, setShowFiltersMobile] = useState(false);

  useEffect(() => {
    if (!ENABLE_CONCURSOS) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchConcursos();
        if (!cancelled) setRows(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!cancelled) setError(e?.message || String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filterOptions = useMemo(() => buildFilterOptions(rows), [rows]);

  const tabRows = useMemo(() => filterByTab(rows, tab), [rows, tab]);

  const filteredRows = useMemo(
    () => sortConcursos(applyConcursosFilters(tabRows, filters)),
    [tabRows, filters]
  );

  const statsTop = useMemo(() => computeConcursosStats(rows), [rows]);

  const activeChips = useMemo(() => getActiveFilterChips(filters, tab), [filters, tab]);

  const activeFilterCount = useMemo(() => countActiveFilters(filters, tab), [filters, tab]);

  const emptyHint = useMemo(
    () =>
      describeConcursosEmptyHint(filters, tab, {
        tabCount: tabRows.length,
        filteredCount: filteredRows.length,
      }),
    [filters, tab, tabRows.length, filteredRows.length]
  );

  const handleClear = useCallback(() => setFilters(getInitialConcursosFilters()), []);

  const setFilter = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const removeChip = useCallback((key) => {
    if (key === '__tab') {
      setTab('all');
      return;
    }
    setFilters((prev) => removeFilterKey(prev, key));
  }, []);

  if (!ENABLE_CONCURSOS) {
    return (
      <>
        <Header />
        <div className="dashboard-container concursos-page">
          <main className="main-content concursos-main">
            <EmptyState
              title="Concursos & Seleções desativados"
              hint="Defina VITE_ENABLE_CONCURSOS=true no .env.local para ativar o módulo."
            />
          </main>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />

      <div className="dashboard-container concursos-layout">
        <button
          type="button"
          className="filter-toggle-mobile"
          onClick={() => setShowFiltersMobile(!showFiltersMobile)}
        >
          {showFiltersMobile ? '✕ Fechar filtros' : '🔍 Abrir filtros'}
          {activeFilterCount > 0 ? ` (${activeFilterCount})` : ''}
        </button>

        <aside className={`sidebar concursos-sidebar ${!showFiltersMobile ? 'mobile-hidden' : ''}`}>
          <div className="concursos-filters-head">
            <h3 className="concursos-filters-title">Filtros</h3>
            <button
              type="button"
              className="concursos-clear-btn"
              onClick={handleClear}
              disabled={activeFilterCount === 0}
            >
              Limpar filtros
            </button>
          </div>

          <div className="concursos-filters-stack">
            <label className="filter-label" htmlFor="conc-search">
              Busca
            </label>
            <input
              id="conc-search"
              type="search"
              className="filter-input-large"
              placeholder="Título, órgão, instituição, cargo, UF…"
              value={filters.search}
              onChange={(e) => setFilter('search', e.target.value)}
            />

            <p className="concursos-filter-section-label">Fonte e tipo</p>

            <label className="filter-label" htmlFor="conc-fonte">
              Fonte / banca
            </label>
            <select
              id="conc-fonte"
              className="filter-select"
              value={filters.fonte}
              onChange={(e) => setFilter('fonte', e.target.value)}
            >
              <option value="">Todas as fontes</option>
              {FONTE_BANCA_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                  {filterOptions.fonte.some((f) => f.value === o.value) ? '' : ' (sem dados)'}
                </option>
              ))}
            </select>

            <label className="filter-label" htmlFor="conc-tipo">
              Tipo de seleção
            </label>
            <select
              id="conc-tipo"
              className="filter-select"
              value={filters.tipoSelecao}
              onChange={(e) => setFilter('tipoSelecao', e.target.value)}
            >
              <option value="">Todos os tipos</option>
              {filterOptions.tipoSelecao.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>

            <label className="filter-label" htmlFor="conc-status">
              Status
            </label>
            <select
              id="conc-status"
              className="filter-select"
              value={filters.status}
              onChange={(e) => setFilter('status', e.target.value)}
            >
              <option value="">Todos</option>
              {filterOptions.status.map((v) => (
                <option key={v} value={v}>
                  {labelStatus(v)}
                </option>
              ))}
            </select>

            <p className="concursos-filter-section-label">Local e instituição</p>

            <label className="filter-label" htmlFor="conc-inst-orgao">
              Instituição ou órgão
            </label>
            <input
              id="conc-inst-orgao"
              type="search"
              className="filter-input-large"
              placeholder="Buscar por órgão, universidade, prefeitura, conselho…"
              value={filters.instituicaoOrgao}
              onChange={(e) => setFilter('instituicaoOrgao', e.target.value)}
            />

            <label className="filter-label" htmlFor="conc-tipo-inst">
              Tipo de instituição
            </label>
            <select
              id="conc-tipo-inst"
              className="filter-select"
              value={filters.tipoInstituicao}
              onChange={(e) => setFilter('tipoInstituicao', e.target.value)}
            >
              <option value="">Todos os tipos</option>
              {TIPO_INSTITUICAO_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>

            <label className="filter-label" htmlFor="conc-estado">
              Estado
            </label>
            <select
              id="conc-estado"
              className="filter-select"
              value={filters.estado}
              onChange={(e) => setFilter('estado', e.target.value)}
            >
              <option value="">Todos</option>
              {filterOptions.estado.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>

            <label className="filter-label" htmlFor="conc-mun">
              Município
            </label>
            <select
              id="conc-mun"
              className="filter-select"
              value={filters.municipio}
              onChange={(e) => setFilter('municipio', e.target.value)}
            >
              <option value="">Todos</option>
              {filterOptions.municipio.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>

            <label className="filter-label" htmlFor="conc-esc">
              Escolaridade
            </label>
            <select
              id="conc-esc"
              className="filter-select"
              value={filters.escolaridade}
              onChange={(e) => setFilter('escolaridade', e.target.value)}
            >
              <option value="">Todas</option>
              {filterOptions.escolaridade.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>

            <label className="filter-label" htmlFor="conc-area">
              Área / cargo / curso
            </label>
            <input
              id="conc-area"
              type="text"
              className="filter-input-large"
              placeholder="Substring em área, cargo ou curso"
              value={filters.areaCargo}
              onChange={(e) => setFilter('areaCargo', e.target.value)}
            />

            <p className="concursos-filter-section-label">Qualidade e prazos</p>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.somenteValidos}
                onChange={(e) => setFilter('somenteValidos', e.target.checked)}
              />
              Somente dados válidos
            </label>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.comEdital}
                onChange={(e) => setFilter('comEdital', e.target.checked)}
              />
              Somente com edital (PDF)
            </label>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.comDataFimInscricao}
                onChange={(e) => setFilter('comDataFimInscricao', e.target.checked)}
              />
              Somente com data fim de inscrição
            </label>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.inscricoesAbertas}
                onChange={(e) => setFilter('inscricoesAbertas', e.target.checked)}
              />
              Somente inscrições abertas
            </label>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.provaProxima}
                onChange={(e) => setFilter('provaProxima', e.target.checked)}
              />
              Somente prova próxima
            </label>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.comSalarioBolsa}
                onChange={(e) => setFilter('comSalarioBolsa', e.target.checked)}
              />
              Somente com salário / bolsa
            </label>

            <label className="filter-check">
              <input
                type="checkbox"
                checked={filters.comTaxa}
                onChange={(e) => setFilter('comTaxa', e.target.checked)}
              />
              Somente com taxa de inscrição
            </label>
          </div>
        </aside>

        <main className="main-content concursos-main">
          <div className="content-header concursos-header-block">
            <div>
              <h2>Concursos &amp; Seleções</h2>
              <p className="concursos-subtitle">
                Concursos públicos, processos seletivos, vestibulares, ingresso, residências e bolsas — filtros por
                fonte, local, prazos e qualidade dos dados.
              </p>
            </div>
          </div>

          <nav className="precad-nav-tabs concursos-tabs" aria-label="Categorias">
            {TAB_DEFS.map((t) => (
              <button
                key={t.id}
                type="button"
                className={`precad-nav-tab ${tab === t.id ? 'is-active' : ''}`}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </nav>

          <section className="concursos-stats-bar" aria-label="Resumo">
            <div className="concursos-stat-chip">
              <strong>{statsTop.total}</strong>
              <span>Total</span>
            </div>
            <div className="concursos-stat-chip concursos-stat-chip--ok">
              <strong>{statsTop.inscricoesAbertas}</strong>
              <span>Inscrições abertas</span>
            </div>
            <div className="concursos-stat-chip concursos-stat-chip--info">
              <strong>{statsTop.comEdital}</strong>
              <span>Com edital</span>
            </div>
            <div className="concursos-stat-chip concursos-stat-chip--valid">
              <strong>{statsTop.dadosValidos}</strong>
              <span>Dados válidos</span>
            </div>
            <div className="concursos-stat-chip concursos-stat-chip--warn">
              <strong>{statsTop.provasProximas}</strong>
              <span>Provas próximas</span>
            </div>
            <div className="concursos-stat-chip concursos-stat-chip--tab">
              <strong>{statsTop.vestibularesIngresso}</strong>
              <span>Vestibulares / ingresso</span>
            </div>
          </section>

          {activeChips.length > 0 && (
            <section className="concursos-active-filters" aria-label="Filtros ativos">
              <span className="concursos-active-filters-label">Filtros ativos:</span>
              <div className="concursos-filter-chips">
                {activeChips.map((chip) => (
                  <button
                    key={chip.key}
                    type="button"
                    className={`concursos-filter-chip ${chip.locked ? 'is-locked' : ''}`}
                    onClick={() => !chip.locked && removeChip(chip.key)}
                    disabled={chip.locked}
                    title={chip.locked ? 'Mude para a aba Todos para remover' : 'Remover filtro'}
                  >
                    <span className="concursos-filter-chip-text">
                      {chip.label}: {chip.display}
                    </span>
                    {!chip.locked && <span className="concursos-filter-chip-x" aria-hidden="true">×</span>}
                  </button>
                ))}
              </div>
            </section>
          )}

          <p className="concursos-count-line">
            Mostrando <strong>{filteredRows.length}</strong> de {tabRows.length} nesta aba
            {tab !== 'all' ? ` · ${TAB_DEFS.find((x) => x.id === tab)?.label || ''}` : ''}
            {activeFilterCount > 0 ? ` · ${activeFilterCount} filtro(s) lateral(is)` : ''}
          </p>

          {loading && (
            <LoadingState title="Carregando seleções…" subtitle="A consultar a vista pública configurada no ambiente." />
          )}

          {!loading && error && (
            <ErrorState title="Não foi possível carregar as seleções" message={error} />
          )}

          {!loading && !error && rows.length === 0 && (
            <EmptyState
              title="Nenhuma seleção disponível"
              hint="Confirme a view vw_concursos_front no Supabase, dados de teste e permissões anon (RLS)."
            />
          )}

          {!loading && !error && rows.length > 0 && filteredRows.length === 0 && (
            <EmptyState title="Nenhuma seleção encontrada com os filtros atuais" hint={emptyHint}>
              {activeFilterCount > 0 && (
                <button type="button" className="concursos-empty-clear-btn" onClick={handleClear}>
                  Limpar filtros
                </button>
              )}
            </EmptyState>
          )}

          {!loading && !error && filteredRows.length > 0 && (
            <div className="editais-grid concursos-cards-grid">
              {filteredRows.map((row, idx) => (
                <ConcursoCard key={rowKey(row, idx)} row={row} />
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
