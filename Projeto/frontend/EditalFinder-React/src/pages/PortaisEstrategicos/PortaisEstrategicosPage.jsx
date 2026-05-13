import { useState, useEffect, useMemo, useCallback } from 'react';
import Header from '../../components/layout/Header';
import LoadingState from '../../components/states/LoadingState';
import ErrorState from '../../components/states/ErrorState';
import EmptyState from '../../components/states/EmptyState';
import PortalEstrategicoCard from '../../components/cards/PortalEstrategicoCard';
import PortalEstrategicoFilters, { getInitialPortalFilters } from '../../components/filters/PortalEstrategicoFilters';
import { fetchFornecedoresFront, fetchInvestimentosFront } from '../../services/portaisEstrategicosService';
import {
  getPortalTipoDisplay,
  getPortalUpdatedAt,
  isAcessoLimitadoRow,
  isHubOrDocTipo,
} from '../../utils/portaisEstrategicos';
import { humanizeTechnicalLabel } from '../../utils/portaisDisplayLabels.js';
import './PortaisEstrategicosPage.css';

const TAB_FORN = 'fornecedores';
const TAB_INV = 'investimentos';

const SORT_OPTIONS = [
  { id: 'recentes', label: 'Mais recentes' },
  { id: 'fonte', label: 'Fonte (A–Z)' },
  { id: 'tipo', label: 'Tipo de portal' },
  { id: 'qualidade', label: 'Qualidade do dado' },
  { id: 'acesso_publico', label: 'Acesso público primeiro' },
];

const Q_ORDER = { alta: 3, media: 2, média: 2, baixa: 1, desconhecida: 0 };

function rowKey(row, idx) {
  if (row?.id != null) return `id-${row.id}`;
  if (row?.id_edital != null) return `ide-${row.id_edital}`;
  if (row?.link) return `link-${row.link}`;
  return `i-${idx}`;
}

/** Linhas ativas (view pode ou não trazer `ativo`). */
function activeOnly(rows) {
  return (rows || []).filter((r) => r?.ativo !== false);
}

function filterPortalRows(baseRows, filters) {
  let out = baseRows;

  if (filters.validacao) {
    out = out.filter((r) => r?.validacao_status === filters.validacao);
  } else if (!filters.includeSuspeitos) {
    out = out.filter((r) => String(r?.validacao_status || '').toLowerCase() !== 'suspeito');
  }

  if (filters.fonte) {
    out = out.filter((r) => (r?.fonte_recurso || r?.fonte) === filters.fonte);
  }
  if (filters.tipoPortal) {
    out = out.filter((r) => getPortalTipoDisplay(r) === filters.tipoPortal);
  }
  if (filters.qualidade) {
    out = out.filter((r) => r?.qualidade_dado === filters.qualidade);
  }

  if (filters.acesso === 'publico') {
    out = out.filter((r) => !isAcessoLimitadoRow(r) && r?.requer_login !== true);
  } else if (filters.acesso === 'limitado') {
    out = out.filter((r) => isAcessoLimitadoRow(r) || r?.requer_login === true);
  }

  if (filters.setor) {
    out = out.filter((r) => {
      const se = r?.setor_estrategico;
      if (Array.isArray(se)) return se.some((x) => String(x) === filters.setor);
      return String(se || '') === filters.setor;
    });
  }

  const q = (filters.search || '').trim().toLowerCase();
  if (q) {
    out = out.filter((r) => {
      const fonteHum = humanizeTechnicalLabel(r?.fonte_recurso || r?.fonte || '');
      const catHum = humanizeTechnicalLabel(r?.categoria || r?.frontend_section || '');
      const setoresHum = Array.isArray(r?.setor_estrategico)
        ? r.setor_estrategico.map((x) => humanizeTechnicalLabel(x)).join(' ')
        : '';
      const blob = [
        r?.titulo,
        r?.resumo,
        r?.descricao,
        r?.link,
        r?.fonte,
        r?.fonte_recurso,
        fonteHum,
        r?.categoria,
        r?.frontend_section,
        catHum,
        ...(Array.isArray(r?.tags) ? r.tags : []),
        getPortalTipoDisplay(r),
        setoresHum,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return blob.includes(q);
    });
  }

  return out;
}

function sortPortalRows(rows, sortId) {
  const list = [...rows];
  const fonte = (r) => (r?.fonte_recurso || r?.fonte || '').toLowerCase();

  switch (sortId) {
    case 'fonte':
      list.sort((a, b) => fonte(a).localeCompare(fonte(b), 'pt-BR'));
      break;
    case 'tipo':
      list.sort((a, b) =>
        getPortalTipoDisplay(a).localeCompare(getPortalTipoDisplay(b), 'pt-BR')
      );
      break;
    case 'qualidade': {
      list.sort((a, b) => {
        const qa = String(a?.qualidade_dado || '').toLowerCase();
        const qb = String(b?.qualidade_dado || '').toLowerCase();
        return (Q_ORDER[qb] ?? 0) - (Q_ORDER[qa] ?? 0);
      });
      break;
    }
    case 'acesso_publico': {
      const score = (r) => (isAcessoLimitadoRow(r) || r?.requer_login ? 1 : 0);
      list.sort((a, b) => score(a) - score(b));
      break;
    }
    case 'recentes':
    default:
      list.sort((a, b) => getPortalUpdatedAt(b) - getPortalUpdatedAt(a));
      break;
  }
  return list;
}

export default function PortaisEstrategicosPage() {
  const [tab, setTab] = useState(TAB_FORN);
  const [fornecedores, setFornecedores] = useState([]);
  const [investimentos, setInvestimentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(getInitialPortalFilters);
  const [sortId, setSortId] = useState('recentes');
  const [showFiltersMobile, setShowFiltersMobile] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const [f, i] = await Promise.all([fetchFornecedoresFront(), fetchInvestimentosFront()]);
        if (!cancelled) {
          setFornecedores(Array.isArray(f) ? f : []);
          setInvestimentos(Array.isArray(i) ? i : []);
        }
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

  useEffect(() => {
    setFilters(getInitialPortalFilters());
  }, [tab]);

  const rawTab = tab === TAB_INV ? investimentos : fornecedores;
  const baseRows = useMemo(() => activeOnly(rawTab), [rawTab]);

  const optionSourceRows = baseRows;

  const filteredRows = useMemo(
    () => filterPortalRows(baseRows, filters),
    [baseRows, filters]
  );

  const sortedRows = useMemo(
    () => sortPortalRows(filteredRows, sortId),
    [filteredRows, sortId]
  );

  const statsGlobal = useMemo(() => {
    return {
      nf: activeOnly(fornecedores).length,
      ni: activeOnly(investimentos).length,
    };
  }, [fornecedores, investimentos]);

  const statsFiltered = useMemo(() => {
    return {
      lim: sortedRows.filter((r) => isAcessoLimitadoRow(r) || r?.requer_login).length,
      hubDoc: sortedRows.filter((r) => isHubOrDocTipo(r)).length,
    };
  }, [sortedRows]);

  const handleClear = useCallback(() => setFilters(getInitialPortalFilters()), []);

  return (
    <>
      <Header />

      <div className="dashboard-container portais-layout">
        <button
          type="button"
          className="filter-toggle-mobile"
          onClick={() => setShowFiltersMobile(!showFiltersMobile)}
        >
          {showFiltersMobile ? '✕ Fechar Filtros' : '🔍 Abrir Filtros'}
        </button>

        <div className={`sidebar ${!showFiltersMobile ? 'mobile-hidden' : ''}`}>
          <PortalEstrategicoFilters
            filters={filters}
            onChange={setFilters}
            optionSourceRows={optionSourceRows}
            onClear={handleClear}
          />
        </div>

        <main className="main-content portais-main">
          <div className="content-header portais-header-block">
            <div>
              <h2>Portais Estratégicos</h2>
              <p className="portais-subtitle">
                Fornecedores, investimentos, procurement e hubs estratégicos organizados fora do Radar de Fomento.
              </p>
            </div>
          </div>

          <nav className="precad-nav-tabs portais-tabs" aria-label="Secções de portais">
            <button
              type="button"
              className={`precad-nav-tab ${tab === TAB_FORN ? 'is-active' : ''}`}
              onClick={() => setTab(TAB_FORN)}
            >
              Fornecedores
            </button>
            <button
              type="button"
              className={`precad-nav-tab ${tab === TAB_INV ? 'is-active' : ''}`}
              onClick={() => setTab(TAB_INV)}
            >
              Investimentos
            </button>
          </nav>

          <section className="portais-stats-bar" aria-label="Resumo">
            <div className="portais-stat-chip">
              <strong>{sortedRows.length}</strong>
              <span>Nesta lista</span>
            </div>
            <div className="portais-stat-chip">
              <strong>{baseRows.length}</strong>
              <span>Ativos na aba</span>
            </div>
            <div className={`portais-stat-chip ${tab === TAB_FORN ? 'portais-stat-chip--tab' : ''}`}>
              <strong>{statsGlobal.nf}</strong>
              <span>Fornecedores</span>
            </div>
            <div className={`portais-stat-chip ${tab === TAB_INV ? 'portais-stat-chip--tab' : ''}`}>
              <strong>{statsGlobal.ni}</strong>
              <span>Investimentos</span>
            </div>
            <div className="portais-stat-chip portais-stat-chip--accent">
              <strong>{statsFiltered.lim}</strong>
              <span>Acesso limitado</span>
            </div>
            <div className="portais-stat-chip">
              <strong>{statsFiltered.hubDoc}</strong>
              <span>Hubs e documentação</span>
            </div>
          </section>

          <div className="portais-toolbar">
            <label className="portais-sort-label">
              Ordenar por{' '}
              <select
                className="filter-select"
                value={sortId}
                onChange={(e) => setSortId(e.target.value)}
                style={{ minWidth: '200px', marginLeft: '8px' }}
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>
            <span className="editals-count">
              Mostrando {sortedRows.length} de {baseRows.length} (ativos)
            </span>
          </div>

          {loading && <LoadingState title="Carregando portais…" subtitle="A consultar as vistas configuradas no ambiente." />}

          {!loading && error && (
            <ErrorState
              title="Não foi possível carregar os portais"
              message={error}
            />
          )}

          {!loading &&
            !error &&
            sortedRows.length === 0 &&
            (baseRows.length === 0 ? (
              <EmptyState
                title="Nenhum portal ativo nesta aba por agora."
                hint="Confirme as views vw_fornecedores_front e vw_investimentos_front no Supabase e as permissões anon (RLS)."
              />
            ) : (
              <EmptyState
                title="Nenhum portal encontrado com os filtros atuais."
                hint="Tente limpar os filtros ou selecionar outra aba."
              />
            ))}

          {!loading && !error && sortedRows.length > 0 && (
            <div className="editais-grid portais-cards-grid">
              {sortedRows.map((row, idx) => (
                <PortalEstrategicoCard
                  key={rowKey(row, idx)}
                  row={row}
                  tabContext={tab === TAB_INV ? TAB_INV : TAB_FORN}
                />
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
