import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import Header from '../components/layout/Header';
import ListaClientes from '../components/radar/ListaClientes';
import RadarResultsSkeleton from '../components/radar/RadarResultsSkeleton';
import RadarResultsGrid from '../components/radar/RadarResultsGrid';
import RadarErrorBoundary from '../components/radar/RadarErrorBoundary';
import { purgeLegacyRadarSessionCaches } from '../utils/radar/radarPersistentCache';
import {
  RADAR_VISIBLE_INITIAL_CAP,
  RADAR_VISIBLE_LOAD_MORE_STEP,
} from '../constants/radarVirtual';
import {
  radarPerfClickReceived,
  radarPerfSelectClienteState,
  radarPerfStart,
} from '../utils/radarPerfLog';
import {
  buildClientesFingerprintMap,
  catalogFingerprintFromEditais,
  clienteFingerprintFromRow,
  optionsFingerprintFromMerged,
} from '../utils/radar/radarFingerprints';
import { radarRenderPerfCycle, radarRenderPerfEvent } from '../utils/radarRenderPerfLog';
import { useRadarMatches } from '../hooks/useRadarMatches';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { dataService } from '../services/dataService';
import { tiposRecursoEditaisNaAreaDoCliente, debugRadar } from '../services/matchService';
import { useEditalFavorites } from '../hooks/useEditalFavorites';
import { useAuth } from '../contexts/AuthContext';
import { filterClientsForUser } from '../utils/permissions';

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

// Favoritos persistidos no localStorage por cliente: { [clienteId]: [editalId, ...] }
function carregarFavoritos() {
  try {
    return JSON.parse(localStorage.getItem('radar_favoritos') || '{}');
  } catch {
    return {};
  }
}

/** Evita crash do React se o JSON estiver corrompido ou não for lista (new Set(null) ou Set(obj) quebra). */
function favoritosParaEstado(raw) {
  const obj = {};
  if (!raw || typeof raw !== 'object') return obj;
  for (const [cid, ids] of Object.entries(raw)) {
    const arr = Array.isArray(ids) ? ids.filter((x) => x != null) : [];
    obj[cid] = new Set(arr);
  }
  return obj;
}

function salvarFavoritos(favs) {
  localStorage.setItem('radar_favoritos', JSON.stringify(favs));
}

export default function RadarFomento() {
  const { user } = useAuth();
  const favHook = useEditalFavorites();
  const favoritosRemote = favHook.favoritosRemoteEnabled;

  const [clientes, setClientes]               = useState([]);
  const [editais, setEditais]                 = useState([]);
  /** ID estável — evita perder seleção com referências diferentes / hidratação. */
  const [clienteIdSelecionado, setClienteIdSelecionado] = useState(null);
  const [loading, setLoading]                 = useState(true);
  const [loadError, setLoadError]             = useState(null);

  /** Listagem progressiva dos cards após o cálculo (evita pintar ~900 elementos de uma vez). */
  const [visibleCap, setVisibleCap] = useState(RADAR_VISIBLE_INITIAL_CAP);

  // { [clienteId]: Set<editalId> }
  const [favoritos, setFavoritos] = useState(() => favoritosParaEstado(carregarFavoritos()));

  // Filtros
  const [filtroTipo, setFiltroTipo]         = useState('');
  const [filtroOrgao, setFiltroOrgao]       = useState('');
  const [filtroComp, setFiltroComp]         = useState('');
  const [filtroFavs, setFiltroFavs]         = useState(false);
  const [filtroBusca, setFiltroBusca]       = useState('');
  const [radarOpts, setRadarOpts] = useState({
    incluirEncerrados: false,
    incluirSuspeitos: false,
    incluirAproximados: false,
  });
  const [radarAvancadoAberto, setRadarAvancadoAberto] = useState(false);
  const radarPerfSessionRef = useRef(null);
  const radarClickT0Ref = useRef(null);

  useEffect(() => {
    purgeLegacyRadarSessionCaches();
  }, []);

  useEffect(() => {
    async function load() {
      try {
        setLoadError(null);
        const [cls, eds] = await Promise.all([
          dataService.getClients({ user }),
          dataService.getEditais(),
        ]);
        const allowed = filterClientsForUser(user, cls);
        setClientes(allowed.filter((c) => String(c.status || '').toLowerCase() === 'ativo'));
        setEditais(eds);
      } catch (e) {
        console.error('Erro ao carregar dados:', e);
        setLoadError('Não foi possível carregar clientes ou editais. Verifique a conexão e tente recarregar a página.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user]);

  const clienteSelecionado = useMemo(
    () => clientePorIdNaLista(clientes, clienteIdSelecionado),
    [clientes, clienteIdSelecionado],
  );

  const catalogFingerprint = useMemo(
    () => catalogFingerprintFromEditais(editais),
    [editais],
  );

  const clientesFingerprintMap = useMemo(
    () => buildClientesFingerprintMap(clientes),
    [clientes],
  );

  const radarOptionsFingerprint = useMemo(
    () =>
      optionsFingerprintFromMerged({
        incluirSuspeitos: radarOpts.incluirSuspeitos,
        incluirEncerrados: radarOpts.incluirEncerrados,
        incluirAproximados: radarOpts.incluirAproximados,
        cortePrincipal: 52,
        corteFallback: 30,
        limite: 3000,
        scoreMinimoExibir: radarOpts.incluirAproximados ? 12 : 24,
      }),
    [
      radarOpts.incluirSuspeitos,
      radarOpts.incluirEncerrados,
      radarOpts.incluirAproximados,
    ],
  );

  const clienteFingerprintAtual = useMemo(() => {
    if (!clienteSelecionado) return null;
    const cid = String(
      clienteSelecionado.id_cliente ?? clienteSelecionado.id ?? '',
    );
    return (
      clientesFingerprintMap.get(cid) ??
      clienteFingerprintFromRow(clienteSelecionado)
    );
  }, [clienteSelecionado, clientesFingerprintMap]);

  useEffect(() => {
    if (loading) return;
    if (clientes.length === 0) {
      setClienteIdSelecionado(null);
      return;
    }
    if (clienteIdSelecionado != null && clientePorIdNaLista(clientes, clienteIdSelecionado)) {
      return;
    }
    if (clienteIdSelecionado != null && !clientePorIdNaLista(clientes, clienteIdSelecionado)) {
      setClienteIdSelecionado(idClienteKey(clientes[0], 0));
    }
  }, [loading, clientes, clienteIdSelecionado]);

  // Conjunto de IDs de editais realmente existentes (carregados agora)
  const editaisIdsExistentes = useMemo(
    () => new Set(editais.map(e => e.id)),
    [editais]
  );

  // Limpa favoritos órfãos (IDs de editais que não existem mais) quando os editais
  // terminam de carregar. Também persiste a limpeza no localStorage.
  useEffect(() => {
    if (loading || editais.length === 0) return;
    setFavoritos(prev => {
      let mudou = false;
      const next = {};
      Object.entries(prev).forEach(([cid, set]) => {
        if (!(set instanceof Set)) return;
        const filtrado = new Set();
        set.forEach(id => {
          if (editaisIdsExistentes.has(id)) filtrado.add(id);
        });
        if (filtrado.size !== set.size) mudou = true;
        if (filtrado.size > 0) next[cid] = filtrado;
        else if (set.size > 0) mudou = true;
      });
      if (!mudou) return prev;
      const raw = {};
      Object.entries(next).forEach(([k, s]) => { raw[k] = [...s]; });
      salvarFavoritos(raw);
      return next;
    });
  }, [loading, editais, editaisIdsExistentes]);

  // Favoritos do cliente selecionado (Set) — apenas IDs que ainda existem
  const favoritosCliente = useMemo(() => {
    if (!clienteSelecionado) return new Set();
    const cidKey = String(clienteSelecionado.id_cliente ?? '');
    const raw = favoritos[cidKey] ?? favoritos[clienteSelecionado.id_cliente];
    const bruto = raw instanceof Set ? raw : new Set();
    const valido = new Set();
    bruto.forEach(id => { if (editaisIdsExistentes.has(id)) valido.add(id); });
    return valido;
  }, [favoritos, clienteSelecionado, editaisIdsExistentes]);

  // Contagem de favoritos por cliente (painel esquerdo) — apenas editais existentes
  const favoritosCount = useMemo(() => {
    const counts = {};
    Object.entries(favoritos).forEach(([cid, ids]) => {
      if (!(ids instanceof Set)) return;
      let n = 0;
      ids.forEach(id => { if (editaisIdsExistentes.has(id)) n++; });
      counts[cid] = n;
    });
    return counts;
  }, [favoritos, editaisIdsExistentes]);

  const toggleFavoritoRadar = useCallback(
    async (editalOuId) => {
      const ed =
        editalOuId && typeof editalOuId === 'object' && 'titulo' in editalOuId
          ? editalOuId
          : editais.find((e) => e.id === editalOuId);
      if (!ed) return;
      if (favoritosRemote) {
        await favHook.toggleFavorite(ed, { contexto: 'radar' });
        return;
      }
      if (!clienteSelecionado) return;
      const cid = String(clienteSelecionado.id_cliente ?? '');
      const editalId = typeof editalOuId === 'object' ? ed.id : editalOuId;
      setFavoritos((prev) => {
        const next = { ...prev };
        const set = new Set(next[cid] || []);
        set.has(editalId) ? set.delete(editalId) : set.add(editalId);
        next[cid] = set;
        const raw = {};
        Object.entries(next).forEach(([k, s]) => {
          raw[k] = [...s];
        });
        salvarFavoritos(raw);
        return next;
      });
    },
    [favoritosRemote, favHook.toggleFavorite, editais, clienteSelecionado],
  );

  const {
    results: recomendacoes,
    resultsReady: radarResultsReady,
    hasPreviewResults: radarHasPreview,
    isPartial: radarIsPartial,
    isCalculating: recoCalculando,
    progress: radarProgress,
    progressPct: radarProgressPct,
    error: radarError,
    meta: radarMeta,
    recalculate: radarRecalculate,
    reloadNonce: radarReloadNonce,
    lastCacheHit: radarLastCacheHit,
    isSessionRefreshing: radarSessionRefreshing,
    isPreparing: radarIsPreparing,
    prefilterStats: radarPrefilterStats,
  } = useRadarMatches({
    cliente: clienteSelecionado,
    editais: editais ?? [],
    options: radarOpts,
    chunkSize: 72,
    enabled: Boolean(clienteSelecionado) && !loading,
    perfSessionRef: radarPerfSessionRef,
    perfClickT0Ref: radarClickT0Ref,
    catalogFingerprint,
    clienteFingerprint: clienteFingerprintAtual,
    optionsFingerprint: radarOptionsFingerprint,
  });

  const recomendacoesLista = Array.isArray(recomendacoes) ? recomendacoes : [];

  const showStaleResults =
    recoCalculando &&
    recomendacoesLista.length > 0 &&
    !radarResultsReady &&
    !radarHasPreview;
  const showResultCards = radarResultsReady || radarHasPreview || showStaleResults;
  const showPreparing =
    Boolean(clienteSelecionado) &&
    radarIsPreparing &&
    !showResultCards &&
    !radarHasPreview;
  const showSkeleton =
    (recoCalculando || showPreparing) && !showResultCards && !showStaleResults;

  /** Quando favoritos vêm do Supabase, contagens no painel refletem favoritos nas recomendações atuais. */
  const favoritosCountDisplay = useMemo(() => {
    if (!favoritosRemote || !clienteSelecionado) return favoritosCount;
    const cid = String(clienteSelecionado.id_cliente ?? clienteSelecionado.id ?? '');
    const n = recomendacoesLista.filter((r) => r?.edital && favHook.isFavorite(r.edital)).length;
    return { ...favoritosCount, [cid]: n };
  }, [favoritosRemote, clienteSelecionado, recomendacoesLista, favHook, favoritosCount]);

  useEffect(() => {
    setVisibleCap(RADAR_VISIBLE_INITIAL_CAP);
  }, [
    clienteIdSelecionado,
    radarReloadNonce,
    radarOpts.incluirSuspeitos,
    radarOpts.incluirEncerrados,
    radarOpts.incluirAproximados,
  ]);

  useEffect(() => {
    if (!import.meta.env?.DEV || !clienteSelecionado || editais.length === 0) return;
    if (recoCalculando) return;
    try {
      debugRadar({ cliente: clienteSelecionado, editais, options: radarOpts });
    } catch (e) {
      console.warn('[RadarFomento] debugRadar:', e);
    }
  }, [clienteSelecionado, editais, radarOpts, recoCalculando]);

  const filtroBuscaDebounced = useDebouncedValue(filtroBusca, 320);

  // Órgãos disponíveis para filtro
  const orgaosDisponiveis = useMemo(
    () => [...new Set((editais ?? []).map(e => e.orgao).filter(Boolean))].sort(),
    [editais]
  );

  // Tipos de recurso só entre editais cuja área/tema cruza com o perfil do cliente
  const tiposRecursoDisponiveis = useMemo(() => {
    if (!clienteSelecionado) return [];
    try {
      return tiposRecursoEditaisNaAreaDoCliente(clienteSelecionado, editais ?? []);
    } catch (e) {
      console.warn('[RadarFomento] tiposRecurso disponíveis:', e);
      return [];
    }
  }, [clienteSelecionado, editais]);

  useEffect(() => {
    if (!filtroTipo) return;
    if (!tiposRecursoDisponiveis.includes(filtroTipo)) setFiltroTipo('');
  }, [filtroTipo, tiposRecursoDisponiveis]);

  // Aplica filtros
  const recomendacoesFiltradas = useMemo(() => {
    return recomendacoesLista.filter((r) => {
      if (!r?.edital?.id) return false;
      if (filtroTipo  && r.edital.tipoRecurso?.toLowerCase() !== filtroTipo.toLowerCase()) return false;
      if (filtroOrgao && r.edital.orgao?.toUpperCase() !== filtroOrgao.toUpperCase())      return false;
      if (filtroComp  && r.compatibilidade !== filtroComp)                                  return false;
      if (filtroFavs && !(favoritosRemote ? favHook.isFavorite(r.edital) : favoritosCliente.has(r.edital.id)))
        return false;
      if (filtroBuscaDebounced) {
        const termo = filtroBuscaDebounced.toLowerCase();
        const bate  =
          (r.edital.titulo  || '').toLowerCase().includes(termo) ||
          (r.edital.orgao   || '').toLowerCase().includes(termo) ||
          (r.edital.area    || '').toLowerCase().includes(termo);
        if (!bate) return false;
      }
      return true;
    });
  }, [recomendacoesLista, filtroTipo, filtroOrgao, filtroComp, filtroFavs, favoritosCliente, filtroBuscaDebounced, favoritosRemote, favHook]);

  const radarFavCount = useMemo(() => {
    if (favoritosRemote) {
      return recomendacoesLista.filter((r) => r?.edital && favHook.isFavorite(r.edital)).length;
    }
    return favoritosCliente.size;
  }, [favoritosRemote, recomendacoesLista, favHook, favoritosCliente]);

  const limparFiltros = useCallback(() => {
    setFiltroTipo('');
    setFiltroOrgao('');
    setFiltroComp('');
    setFiltroFavs(false);
    setFiltroBusca('');
  }, []);

  const handleSelecionarCliente = useCallback(
    (c, idx = 0) => {
      if (!c) return;
      const clickT0 = typeof performance !== 'undefined' ? performance.now() : Date.now();
      radarClickT0Ref.current = clickT0;
      const cid = idClienteKey(c, idx);
      setClienteIdSelecionado(cid);
      limparFiltros();
      queueMicrotask(() => {
        radarPerfClickReceived(clickT0, { cliente_id: cid });
        radarPerfSelectClienteState(clickT0, { cliente_id: cid });
      });
      radarPerfSessionRef.current = radarPerfStart(`radar-${cid}-${Date.now()}`, {
        clienteId: cid,
        clienteNome: c.nome_empresa ?? c.nome ?? null,
        editaisCount: editais?.length ?? 0,
        clickT0,
      });
    },
    [limparFiltros, editais?.length],
  );

  const algumFiltroAtivo = filtroTipo || filtroOrgao || filtroComp || filtroFavs || filtroBusca;

  const melhoresOportunidades = useMemo(
    () => recomendacoesFiltradas.filter((r) => r.compatibilidade === 'Alta'),
    [recomendacoesFiltradas],
  );
  const demaisOportunidades = useMemo(
    () => recomendacoesFiltradas.filter((r) => r.compatibilidade !== 'Alta'),
    [recomendacoesFiltradas],
  );

  const { melhoresOportunidadesVis, demaisVis, cardsVisiveis, podeMostrarMaisOp } = useMemo(() => {
    let capRest = visibleCap;
    const melhoresVis = melhoresOportunidades.slice(
      0,
      Math.min(capRest, melhoresOportunidades.length),
    );
    capRest -= melhoresVis.length;
    const demaisV = capRest > 0 ? demaisOportunidades.slice(0, capRest) : [];
    return {
      melhoresOportunidadesVis: melhoresVis,
      demaisVis: demaisV,
      cardsVisiveis: melhoresVis.length + demaisV.length,
      podeMostrarMaisOp: visibleCap < recomendacoesFiltradas.length,
    };
  }, [
    visibleCap,
    melhoresOportunidades,
    demaisOportunidades,
    recomendacoesFiltradas.length,
  ]);

  const staleOverlay = showStaleResults || radarIsPartial;
  const clienteIdStr = clienteSelecionado
    ? String(clienteSelecionado.id_cliente ?? clienteSelecionado.id ?? '')
    : '';

  useEffect(() => {
    if (!showResultCards) return;
    radarRenderPerfCycle({
      virtual_enabled: false,
      items_total: cardsVisiveis,
      render_items_count: cardsVisiveis,
      visible_items_count: cardsVisiveis,
      cliente_id: clienteIdStr,
      partial: radarIsPartial,
      full: radarResultsReady,
    });
  }, [
    showResultCards,
    cardsVisiveis,
    clienteIdStr,
    radarIsPartial,
    radarResultsReady,
    radarReloadNonce,
  ]);

  return (
    <div className="page-wrapper radar-fomento-page">
      <Header />

      <div className="radar-fomento-below-header">
        <div className="radar-page-title-strip" role="note">
          <h1 className="radar-page-h1">Radar de Fomento</h1>
          <p className="radar-page-h1-sub">Compatibilidade entre clientes e oportunidades de fomento</p>
        </div>

        <div className="radar-page">
        {/* ── Painel esquerdo: clientes ── */}
        <ListaClientes
          clientes={clientes}
          favoritosCount={favoritosCountDisplay}
          clienteIdSelecionado={clienteIdSelecionado}
          onSelecionar={handleSelecionarCliente}
          loading={loading}
        />

        {/* ── Painel direito: recomendações ── */}
        <div className="radar-resultado-panel">
          <RadarErrorBoundary onRetry={radarRecalculate}>

          {loadError && !loading && (
            <div className="radar-load-erro" role="alert">
              {loadError}
            </div>
          )}

          {!clienteSelecionado ? (
            <div className="radar-placeholder">
              <div className="radar-placeholder-icon">🎯</div>
              <h3>Comece por um cliente</h3>
              <p>Selecione um cliente à esquerda para calcular o match com o catálogo de editais e ver o score de compatibilidade.</p>
            </div>
          ) : (
            <>
              {/* Cabeçalho */}
              <div className="radar-resultado-header">
                <div>
                  <h2 className="radar-resultado-titulo">
                    Radar: <span>{clienteSelecionado.nome_empresa}</span>
                  </h2>
                  <div className="radar-resultado-sub-wrap">
                    {(recoCalculando || showPreparing) && (
                      <p className="radar-resultado-sub">
                        {radarSessionRefreshing && (
                          <span className="radar-resultado-pill radar-resultado-pill--cache">
                            Resultado em cache — atualizando…
                          </span>
                        )}
                        {!radarSessionRefreshing && showPreparing && (
                          <span className="radar-resultado-pill">
                            Preparando cálculo…
                          </span>
                        )}
                        {!radarSessionRefreshing && !showPreparing && (
                          <span className="radar-resultado-pill">
                            {radarHasPreview ? 'Prévia — completando lista' : 'Em andamento'}
                          </span>
                        )}{' '}
                        Catálogo: <strong>{radarProgress.originalTotal || editais.length}</strong>
                        {radarProgress.total > 0 && (
                          <>
                            {' '}
                            · A analisar com score: <strong>{radarProgress.total}</strong> editais elegíveis
                          </>
                        )}
                      </p>
                    )}
                    {(!recoCalculando || radarHasPreview) && radarError === null && (
                      <>
                        <p className="radar-resultado-sub radar-resultado-sub--principal">
                          <strong>{recomendacoesFiltradas.length}</strong>{' '}
                          {recomendacoesFiltradas.length === 1 ? 'oportunidade listada' : 'oportunidades listadas'}
                          {radarIsPartial && recoCalculando && (
                            <span className="radar-resultado-pill"> prévia</span>
                          )}
                          {algumFiltroAtivo ? ' com os filtros atuais' : ' (ordenadas por compatibilidade)'}
                          {melhoresOportunidades.length > 0 && (
                            <span className="radar-resultado-alta">
                              {' '}
                              · <strong>{melhoresOportunidades.length}</strong> com compatibilidade{' '}
                              <span className="radar-inline-badge radar-inline-badge--alta">Alta</span>
                            </span>
                          )}
                          {radarFavCount > 0 && (
                            <span className="radar-resultado-fav">
                              {' '}
                              · ★ <strong>{radarFavCount}</strong> favorito
                              {radarFavCount !== 1 ? 's' : ''}
                            </span>
                          )}
                        </p>
                        {radarMeta && (
                          <p className="radar-contagens-micro" title="Números do pipeline do radar (não se somam como etapas lineares simples)">
                            Catálogo total: <strong>{radarMeta.totalIn}</strong>
                            {' · '}
                            Elegíveis após filtros rápidos: <strong>{radarMeta.afterPreFilter}</strong>
                            {radarMeta.excludedPreScore > 0 && (
                              <>
                                {' '}
                                · Retirados antes do score: <strong>{radarMeta.excludedPreScore}</strong>
                              </>
                            )}
                            {' · '}
                            Retornadas pelo radar: <strong>{recomendacoesLista.length}</strong>
                          </p>
                        )}
                        {cardsVisiveis < recomendacoesFiltradas.length && (
                          <p className="radar-contagens-lista">
                            Exibindo <strong>{cardsVisiveis}</strong> de <strong>{recomendacoesFiltradas.length}</strong> na
                            página — use &quot;Mostrar mais oportunidades&quot; para carregar mais cards.
                          </p>
                        )}
                      </>
                    )}
                    {!recoCalculando && radarError !== null && (
                      <p className="radar-resultado-sub">Compatibilidade indisponível no momento — use Recalcular ou tente novamente.</p>
                    )}
                  </div>
                </div>
                <button type="button" className="radar-btn-recalc" onClick={radarRecalculate}>
                  🔄 Recalcular
                </button>
              </div>

              {radarError && (
                <div className="radar-load-erro-banner" role="alert">
                  <div className="radar-load-erro-copy">
                    <strong>Não foi possível concluir o cálculo da compatibilidade.</strong>
                    <span className="radar-load-erro-detalhe">{radarError}</span>
                  </div>
                  <button type="button" className="radar-btn-recalc" onClick={radarRecalculate}>
                    Tentar novamente
                  </button>
                </div>
              )}

              {recoCalculando && !showStaleResults && (
                <RadarResultsSkeleton rows={6} />
              )}
              {recoCalculando && radarProgress.total > 0 && (
                <p className="radar-skeleton-progress" aria-live="polite">
                  Analisando {radarProgress.processed} de {radarProgress.total} editais
                  {radarProgressPct > 0 ? ` (${radarProgressPct}%)` : ''}
                  {import.meta.env?.DEV && radarLastCacheHit === false ? ' · cache miss' : ''}
                </p>
              )}

              {/* Filtros */}
              <div className="radar-filtros">
                <div className="radar-busca-wrap">
                  <span className="radar-busca-icon">🔍</span>
                  <input
                    type="text"
                    className="radar-busca-input"
                    placeholder="Buscar por título, órgão ou área..."
                    value={filtroBusca}
                    onChange={e => setFiltroBusca(e.target.value)}
                  />
                  {filtroBusca && (
                    <button className="radar-busca-clear" onClick={() => setFiltroBusca('')} title="Limpar busca">✕</button>
                  )}
                </div>
                <select
                  value={filtroTipo}
                  onChange={e => setFiltroTipo(e.target.value)}
                  className="radar-select"
                  title={
                    tiposRecursoDisponiveis.length === 0
                      ? 'Nenhum edital com tipo definido combina com áreas/temas do cadastro. Ajuste temas de interesse ou área de inovação.'
                      : 'Tipos de recurso presentes em editais alinhados às áreas e temas do cliente'
                  }
                >
                  <option value="">Todos os tipos</option>
                  {tiposRecursoDisponiveis.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <select value={filtroOrgao} onChange={e => setFiltroOrgao(e.target.value)} className="radar-select">
                  <option value="">Todos os órgãos</option>
                  {orgaosDisponiveis.map(o => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
                <select value={filtroComp} onChange={e => setFiltroComp(e.target.value)} className="radar-select">
                  <option value="">Todas compatibilidades</option>
                  <option value="Alta">Alta</option>
                  <option value="Média">Média</option>
                  <option value="Baixa">Baixa</option>
                </select>

                {/* Botão de favoritos */}
                <button
                  className={`radar-btn-favs-filtro ${filtroFavs ? 'ativo' : ''}`}
                  onClick={() => setFiltroFavs(v => !v)}
                  title="Mostrar apenas favoritos"
                >
                  {filtroFavs ? '★' : '☆'} Favoritos
                  {radarFavCount > 0 && (
                    <span className="radar-favs-count">{radarFavCount}</span>
                  )}
                </button>

                {algumFiltroAtivo && (
                  <button className="radar-btn-limpar" onClick={limparFiltros}>
                    ✕ Limpar
                  </button>
                )}
              </div>

              <div className="radar-avancado-wrap">
                <button
                  type="button"
                  className="radar-avancado-toggle"
                  onClick={() => setRadarAvancadoAberto((v) => !v)}
                  aria-expanded={radarAvancadoAberto}
                >
                  <span className="radar-avancado-toggle-titulo">Opções avançadas do radar</span>
                  <span className="radar-avancado-toggle-hint">Filtros opcionais — alteram quem entra no cálculo</span>
                  <span className="radar-avancado-chev" aria-hidden>
                    {radarAvancadoAberto ? '▲' : '▼'}
                  </span>
                </button>
                {radarAvancadoAberto && (
                  <div className="radar-opcoes-avancadas" role="group" aria-label="Opções avançadas do radar">
                    <label className="radar-avancado-label">
                      <input
                        type="checkbox"
                        checked={radarOpts.incluirEncerrados}
                        onChange={(e) => setRadarOpts((o) => ({ ...o, incluirEncerrados: e.target.checked }))}
                      />
                      <span>Incluir editais encerrados</span>
                    </label>
                    <label className="radar-avancado-label">
                      <input
                        type="checkbox"
                        checked={radarOpts.incluirSuspeitos}
                        onChange={(e) => setRadarOpts((o) => ({ ...o, incluirSuspeitos: e.target.checked }))}
                      />
                      <span>Incluir itens com validação suspeita</span>
                    </label>
                    <label className="radar-avancado-label">
                      <input
                        type="checkbox"
                        checked={radarOpts.incluirAproximados}
                        onChange={(e) => setRadarOpts((o) => ({ ...o, incluirAproximados: e.target.checked }))}
                      />
                      <span>Incluir oportunidades mais fracas (score menor)</span>
                    </label>
                    {radarPrefilterStats && radarPrefilterStats.catalog_total > 0 && (
                      <p className="radar-prefilter-hint">
                        Catálogo filtrado:{' '}
                        <strong>{radarPrefilterStats.sent_to_worker}</strong> de{' '}
                        <strong>{radarPrefilterStats.catalog_total}</strong> oportunidades consideradas
                        no cálculo
                        {import.meta.env?.DEV && radarPrefilterStats.catalog_total > radarPrefilterStats.sent_to_worker && (
                          <span className="radar-prefilter-hint-dev">
                            {' '}
                            (−
                            {radarPrefilterStats.catalog_total - radarPrefilterStats.sent_to_worker}{' '}
                            ruído/duplicatas — ver [radar-noise] no console)
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                )}
              </div>

              {showResultCards && melhoresOportunidadesVis.length > 0 && (
                <RadarResultsGrid
                  rows={melhoresOportunidadesVis}
                  staleOverlay={staleOverlay}
                  sectionTitle="⭐ Melhores Oportunidades"
                  showSectionTitle
                  favoritosRemote={favoritosRemote}
                  favoritosCliente={favoritosCliente}
                  favHook={favHook}
                  onFavoritar={toggleFavoritoRadar}
                />
              )}

              {showResultCards && demaisVis.length > 0 && (
                <RadarResultsGrid
                  rows={demaisVis}
                  staleOverlay={staleOverlay}
                  sectionTitle="Outros Editais"
                  showSectionTitle={melhoresOportunidades.length > 0}
                  favoritosRemote={favoritosRemote}
                  favoritosCliente={favoritosCliente}
                  favHook={favHook}
                  onFavoritar={toggleFavoritoRadar}
                />
              )}

              {radarResultsReady && podeMostrarMaisOp && (
                <div style={{ textAlign: 'center', marginTop: 20 }}>
                  <button
                    type="button"
                    className="radar-btn-recalc"
                    onClick={() => setVisibleCap((c) => c + RADAR_VISIBLE_LOAD_MORE_STEP)}
                  >
                    Mostrar mais oportunidades
                  </button>
                </div>
              )}

              {radarResultsReady && !radarError && recomendacoesFiltradas.length === 0 && (
                <div className="radar-empty">
                  {(() => {
                    if (recomendacoesLista.length === 0) {
                      if (!algumFiltroAtivo) {
                        return (
                          <>
                            <p className="radar-empty-titulo">Nenhuma oportunidade apareceu neste radar</p>
                            <p className="radar-empty-texto">
                              O catálogo pode ter sido filtrado no início ou o score mínimo excluiu tudo. Abra{' '}
                              <strong>Opções avançadas do radar</strong> e experimente &quot;oportunidades mais fracas&quot;
                              ou editais encerrados — ou recadastre temas de interesse no cliente.
                            </p>
                          </>
                        );
                      }
                      return (
                        <>
                          <p className="radar-empty-titulo">Nenhum resultado com estes filtros</p>
                          <p className="radar-empty-texto">Limpe a busca, os selects ou favoritos para ver de novo a lista completa do radar.</p>
                        </>
                      );
                    }
                    if (filtroFavs && radarFavCount === 0) {
                      return (
                        <>
                          <p className="radar-empty-titulo">Sem favoritos a mostrar</p>
                          <p className="radar-empty-texto">Use ☆ nos cards para guardar oportunidades e depois filtre por favoritos.</p>
                        </>
                      );
                    }
                    return (
                      <>
                        <p className="radar-empty-titulo">Nenhum resultado com estes filtros</p>
                        <p className="radar-empty-texto">Ajuste tipo, órgão, compatibilidade ou busca — ou limpe tudo com &quot;Limpar&quot;.</p>
                      </>
                    );
                  })()}
                </div>
              )}
            </>
          )}
          </RadarErrorBoundary>
        </div>
      </div>
      </div>
    </div>
  );
}
