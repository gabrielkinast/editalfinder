import { useState, useEffect, useMemo, useCallback } from 'react';
import Header from '../components/layout/Header';
import ListaClientes from '../components/radar/ListaClientes';
import CardEditalRadar from '../components/radar/CardEditalRadar';
import RadarLoading from '../components/radar/RadarLoading';
import { useRadarMatches } from '../hooks/useRadarMatches';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { dataService } from '../services/dataService';
import { tiposRecursoEditaisNaAreaDoCliente, debugRadar } from '../services/matchService';

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
  const [clientes, setClientes]               = useState([]);
  const [editais, setEditais]                 = useState([]);
  /** ID estável — evita perder seleção com referências diferentes / hidratação. */
  const [clienteIdSelecionado, setClienteIdSelecionado] = useState(null);
  const [loading, setLoading]                 = useState(true);
  const [loadError, setLoadError]             = useState(null);

  /** Listagem progressiva dos cards após o cálculo (evita pintar ~900 elementos de uma vez). */
  const [visibleCap, setVisibleCap] = useState(40);

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

  useEffect(() => {
    async function load() {
      try {
        setLoadError(null);
        const [cls, eds] = await Promise.all([
          dataService.getClients(),
          dataService.getEditais(),
        ]);
        setClientes(cls.filter((c) => String(c.status || '').toLowerCase() === 'ativo'));
        setEditais(eds);
      } catch (e) {
        console.error('Erro ao carregar dados:', e);
        setLoadError('Não foi possível carregar clientes ou editais. Verifique a conexão e tente recarregar a página.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const clienteSelecionado = useMemo(
    () => clientePorIdNaLista(clientes, clienteIdSelecionado),
    [clientes, clienteIdSelecionado],
  );

  useEffect(() => {
    if (loading) return;
    if (clienteIdSelecionado == null) return;
    if (clientes.length === 0) {
      setClienteIdSelecionado(null);
      return;
    }
    if (!clientePorIdNaLista(clientes, clienteIdSelecionado)) {
      setClienteIdSelecionado(null);
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

  const toggleFavorito = (editalId) => {
    if (!clienteSelecionado) return;
    const cid = String(clienteSelecionado.id_cliente ?? '');

    setFavoritos(prev => {
      const next = { ...prev };
      const set = new Set(next[cid] || []);
      set.has(editalId) ? set.delete(editalId) : set.add(editalId);
      next[cid] = set;

      // Persiste: converte Sets em arrays
      const raw = {};
      Object.entries(next).forEach(([k, s]) => { raw[k] = [...s]; });
      salvarFavoritos(raw);

      return next;
    });
  };

  const {
    results: recomendacoes,
    isCalculating: recoCalculando,
    progress: radarProgress,
    progressPct: radarProgressPct,
    error: radarError,
    recalculate: radarRecalculate,
    reloadNonce: radarReloadNonce,
  } = useRadarMatches({
    cliente: clienteSelecionado,
    editais: editais ?? [],
    options: radarOpts,
    chunkSize: 72,
    enabled: Boolean(clienteSelecionado) && !loading,
  });

  useEffect(() => {
    setVisibleCap(40);
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
    return recomendacoes.filter((r) => {
      if (!r?.edital?.id) return false;
      if (filtroTipo  && r.edital.tipoRecurso?.toLowerCase() !== filtroTipo.toLowerCase()) return false;
      if (filtroOrgao && r.edital.orgao?.toUpperCase() !== filtroOrgao.toUpperCase())      return false;
      if (filtroComp  && r.compatibilidade !== filtroComp)                                  return false;
      if (filtroFavs  && !favoritosCliente.has(r.edital.id))                               return false;
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
  }, [recomendacoes, filtroTipo, filtroOrgao, filtroComp, filtroFavs, favoritosCliente, filtroBuscaDebounced]);

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
      setClienteIdSelecionado(idClienteKey(c, idx));
      limparFiltros();
    },
    [limparFiltros],
  );

  const algumFiltroAtivo = filtroTipo || filtroOrgao || filtroComp || filtroFavs || filtroBusca;

  // Separar melhores oportunidades (Alta compatibilidade)
  const melhoresOportunidades = recomendacoesFiltradas.filter(r => r.compatibilidade === 'Alta');
  const demais = recomendacoesFiltradas.filter(r => r.compatibilidade !== 'Alta');

  let capRest = visibleCap;
  const melhoresOportunidadesVis = melhoresOportunidades.slice(0, Math.min(capRest, melhoresOportunidades.length));
  capRest -= melhoresOportunidadesVis.length;
  const demaisVis = capRest > 0 ? demais.slice(0, capRest) : [];
  const podeMostrarMaisOp = visibleCap < recomendacoesFiltradas.length;

  return (
    <div className="page-wrapper">
      <Header />

      <div className="radar-page">
        {/* ── Painel esquerdo: clientes ── */}
        <ListaClientes
          clientes={clientes}
          favoritosCount={favoritosCount}
          clienteIdSelecionado={clienteIdSelecionado}
          onSelecionar={handleSelecionarCliente}
          loading={loading}
        />

        {/* ── Painel direito: recomendações ── */}
        <div className="radar-resultado-panel">

          {loadError && !loading && (
            <div className="radar-load-erro" role="alert">
              {loadError}
            </div>
          )}

          {!clienteSelecionado ? (
            <div className="radar-placeholder">
              <div className="radar-placeholder-icon">🎯</div>
              <h3>Selecione um cliente</h3>
              <p>Escolha um cliente na lista para ver os editais mais compatíveis com seu perfil.</p>
            </div>
          ) : (
            <>
              {/* Cabeçalho */}
              <div className="radar-resultado-header">
                <div>
                  <h2 className="radar-resultado-titulo">
                    Radar: <span>{clienteSelecionado.nome_empresa}</span>
                  </h2>
                  <p className="radar-resultado-sub">
                    {recoCalculando && (
                      <>Calculando melhores oportunidades… · catálogo: {radarProgress.originalTotal || editais.length} editais</>
                    )}
                    {!recoCalculando && radarError === null && (
                      <>{recomendacoesFiltradas.length} edital(is) encontrado(s)</>
                    )}
                    {!recoCalculando && radarError !== null && (
                      <>Radar indisponível no momento.</>
                    )}
                    {!recoCalculando && melhoresOportunidades.length > 0 && (
                      <> · <strong style={{ color: '#22c55e' }}>{melhoresOportunidades.length} alta compatibilidade</strong></>
                    )}
                    {favoritosCliente.size > 0 && (
                      <> · <strong style={{ color: '#f59e0b' }}>★ {favoritosCliente.size} favoritado(s)</strong></>
                    )}
                  </p>
                </div>
                <button type="button" className="radar-btn-recalc" onClick={radarRecalculate}>
                  🔄 Recalcular
                </button>
              </div>

              {radarError && (
                <div className="radar-load-erro-banner" role="alert">
                  <span>{radarError}</span>
                  <button type="button" className="radar-btn-recalc" onClick={radarRecalculate}>
                    Tentar novamente
                  </button>
                </div>
              )}

              {recoCalculando && (
                <RadarLoading
                  nomeCliente={clienteSelecionado.nome_empresa}
                  processed={radarProgress.processed}
                  total={radarProgress.total}
                  originalTotal={radarProgress.originalTotal}
                  excludedPreScore={radarProgress.excludedPreScore}
                  progressPct={radarProgressPct}
                />
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
                  {favoritosCliente.size > 0 && (
                    <span className="radar-favs-count">{favoritosCliente.size}</span>
                  )}
                </button>

                {algumFiltroAtivo && (
                  <button className="radar-btn-limpar" onClick={limparFiltros}>
                    ✕ Limpar
                  </button>
                )}
              </div>

              <div className="radar-opcoes-avancadas" style={{ marginTop: '12px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', padding: '10px 12px', background: '#f8fafc', borderRadius: '8px', border: '1px solid var(--border-light)', fontSize: '13px' }}>
                <span style={{ fontWeight: 600, color: '#64748b' }}>Radar avançado</span>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={radarOpts.incluirEncerrados}
                    onChange={(e) => setRadarOpts((o) => ({ ...o, incluirEncerrados: e.target.checked }))}
                  />
                  Incluir encerrados
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={radarOpts.incluirSuspeitos}
                    onChange={(e) => setRadarOpts((o) => ({ ...o, incluirSuspeitos: e.target.checked }))}
                  />
                  Incluir suspeitos (validação)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={radarOpts.incluirAproximados}
                    onChange={(e) => setRadarOpts((o) => ({ ...o, incluirAproximados: e.target.checked }))}
                  />
                  Incluir oportunidades aproximadas (score menor)
                </label>
              </div>

              {/* Melhores oportunidades */}
              {!recoCalculando && melhoresOportunidadesVis.length > 0 && (
                <section className="radar-secao">
                  <h3 className="radar-secao-titulo">⭐ Melhores Oportunidades</h3>
                  <div className="radar-grid">
                    {melhoresOportunidadesVis.map((row) => (
                      <CardEditalRadar
                        key={row.edital.id}
                        edital={row.edital}
                        score={row.score}
                        compatibilidade={row.compatibilidade}
                        razoes={row.razoes}
                        detalhes={row.detalhes}
                        criterioMeta={row.criterioMeta}
                        matchLinha={row.matchLinha}
                        fonteMatch={row.fonteMatch}
                        radarBadges={row.radar_badges}
                        radarPenalidades={row.radar_penalidades}
                        prazoInfo={row.prazoInfo}
                        expirado={row.expirado}
                        favorito={favoritosCliente.has(row.edital.id)}
                        onFavoritar={toggleFavorito}
                      />
                    ))}
                  </div>
                </section>
              )}

              {/* Demais editais */}
              {!recoCalculando && demaisVis.length > 0 && (
                <section className="radar-secao">
                  {melhoresOportunidades.length > 0 && (
                    <h3 className="radar-secao-titulo">Outros Editais</h3>
                  )}
                  <div className="radar-grid">
                    {demaisVis.map((row) => (
                      <CardEditalRadar
                        key={row.edital.id}
                        edital={row.edital}
                        score={row.score}
                        compatibilidade={row.compatibilidade}
                        razoes={row.razoes}
                        detalhes={row.detalhes}
                        criterioMeta={row.criterioMeta}
                        matchLinha={row.matchLinha}
                        fonteMatch={row.fonteMatch}
                        radarBadges={row.radar_badges}
                        radarPenalidades={row.radar_penalidades}
                        prazoInfo={row.prazoInfo}
                        expirado={row.expirado}
                        favorito={favoritosCliente.has(row.edital.id)}
                        onFavoritar={toggleFavorito}
                      />
                    ))}
                  </div>
                </section>
              )}

              {!recoCalculando && podeMostrarMaisOp && (
                <div style={{ textAlign: 'center', marginTop: 20 }}>
                  <button
                    type="button"
                    className="radar-btn-recalc"
                    onClick={() => setVisibleCap((c) => c + 40)}
                  >
                    Mostrar mais oportunidades
                  </button>
                </div>
              )}

              {!recoCalculando && !radarError && recomendacoesFiltradas.length === 0 && (
                <div className="radar-empty">
                  {(() => {
                    if (recomendacoes.length === 0) {
                      if (!algumFiltroAtivo) {
                        return 'Nenhuma oportunidade forte encontrada. Tente incluir oportunidades aproximadas no radar avançado.';
                      }
                      return 'Nenhum edital encontrado com os filtros aplicados.';
                    }
                    if (filtroFavs && favoritosCliente.size === 0) {
                      return 'Nenhum edital favoritado ainda. Clique em ☆ nos cards para favoritar.';
                    }
                    return 'Nenhum edital encontrado com os filtros aplicados.';
                  })()}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
