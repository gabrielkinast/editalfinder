import { useState, useEffect, useMemo } from 'react';
import Header from '../components/layout/Header';
import ListaClientes from '../components/radar/ListaClientes';
import CardEditalRadar from '../components/radar/CardEditalRadar';
import { dataService } from '../services/dataService';
import { recomendarEditais } from '../services/matchService';

// Favoritos persistidos no localStorage por cliente: { [clienteId]: [editalId, ...] }
function carregarFavoritos() {
  try {
    return JSON.parse(localStorage.getItem('radar_favoritos') || '{}');
  } catch {
    return {};
  }
}

function salvarFavoritos(favs) {
  localStorage.setItem('radar_favoritos', JSON.stringify(favs));
}

export default function RadarFomento() {
  const [clientes, setClientes]               = useState([]);
  const [editais, setEditais]                 = useState([]);
  const [clienteSelecionado, setClienteSeleo] = useState(null);
  const [loading, setLoading]                 = useState(true);
  const [recalcKey, setRecalcKey]             = useState(0);

  // { [clienteId]: Set<editalId> }
  const [favoritos, setFavoritos] = useState(() => {
    const raw = carregarFavoritos();
    const obj = {};
    Object.entries(raw).forEach(([cid, ids]) => { obj[cid] = new Set(ids); });
    return obj;
  });

  // Filtros
  const [filtroTipo, setFiltroTipo]         = useState('');
  const [filtroOrgao, setFiltroOrgao]       = useState('');
  const [filtroComp, setFiltroComp]         = useState('');
  const [filtroFavs, setFiltroFavs]         = useState(false);
  const [filtroBusca, setFiltroBusca]       = useState('');

  useEffect(() => {
    async function load() {
      try {
        const [cls, eds] = await Promise.all([
          dataService.getClients(),
          dataService.getEditais(),
        ]);
        setClientes(cls.filter(c => c.status === 'Ativo'));
        setEditais(eds);
      } catch (e) {
        console.error('Erro ao carregar dados:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Favoritos do cliente selecionado (Set)
  const favoritosCliente = useMemo(() => {
    if (!clienteSelecionado) return new Set();
    return favoritos[clienteSelecionado.id_cliente] || new Set();
  }, [favoritos, clienteSelecionado]);

  // Contagem de favoritos por cliente (para o painel esquerdo)
  const favoritosCount = useMemo(() => {
    const counts = {};
    Object.entries(favoritos).forEach(([cid, ids]) => {
      counts[cid] = ids.size;
    });
    return counts;
  }, [favoritos]);

  const toggleFavorito = (editalId) => {
    if (!clienteSelecionado) return;
    const cid = clienteSelecionado.id_cliente;

    setFavoritos(prev => {
      const next = { ...prev };
      const set  = new Set(next[cid] || []);
      set.has(editalId) ? set.delete(editalId) : set.add(editalId);
      next[cid] = set;

      // Persiste: converte Sets em arrays
      const raw = {};
      Object.entries(next).forEach(([k, s]) => { raw[k] = [...s]; });
      salvarFavoritos(raw);

      return next;
    });
  };

  // Calcula recomendações
  const recomendacoes = useMemo(() => {
    if (!clienteSelecionado) return [];
    void recalcKey;
    return recomendarEditais(clienteSelecionado, editais);
  }, [clienteSelecionado, editais, recalcKey]);

  // Órgãos disponíveis para filtro
  const orgaosDisponiveis = useMemo(
    () => [...new Set(editais.map(e => e.orgao).filter(Boolean))].sort(),
    [editais]
  );

  // Aplica filtros
  const recomendacoesFiltradas = useMemo(() => {
    return recomendacoes.filter(r => {
      if (filtroTipo  && r.edital.tipoRecurso?.toLowerCase() !== filtroTipo.toLowerCase()) return false;
      if (filtroOrgao && r.edital.orgao?.toUpperCase() !== filtroOrgao.toUpperCase())      return false;
      if (filtroComp  && r.compatibilidade !== filtroComp)                                  return false;
      if (filtroFavs  && !favoritosCliente.has(r.edital.id))                               return false;
      if (filtroBusca) {
        const termo = filtroBusca.toLowerCase();
        const bate  =
          (r.edital.titulo  || '').toLowerCase().includes(termo) ||
          (r.edital.orgao   || '').toLowerCase().includes(termo) ||
          (r.edital.area    || '').toLowerCase().includes(termo);
        if (!bate) return false;
      }
      return true;
    });
  }, [recomendacoes, filtroTipo, filtroOrgao, filtroComp, filtroFavs, favoritosCliente, filtroBusca]);

  const limparFiltros = () => {
    setFiltroTipo('');
    setFiltroOrgao('');
    setFiltroComp('');
    setFiltroFavs(false);
    setFiltroBusca('');
  };

  const algumFiltroAtivo = filtroTipo || filtroOrgao || filtroComp || filtroFavs || filtroBusca;

  // Separar melhores oportunidades (Alta compatibilidade)
  const melhoresOportunidades = recomendacoesFiltradas.filter(r => r.compatibilidade === 'Alta');
  const demais = recomendacoesFiltradas.filter(r => r.compatibilidade !== 'Alta');

  return (
    <div className="page-wrapper">
      <Header />

      <div className="radar-page">
        {/* ── Painel esquerdo: clientes ── */}
        <ListaClientes
          clientes={clientes}
          clienteSelecionado={clienteSelecionado}
          favoritosCount={favoritosCount}
          onSelecionar={c => {
            setClienteSeleo(c);
            limparFiltros();
          }}
          loading={loading}
        />

        {/* ── Painel direito: recomendações ── */}
        <div className="radar-resultado-panel">

          {/* Legenda do índice de compatibilidade */}
          <div className="radar-legenda-box">
            <div className="radar-legenda-titulo">📊 Como funciona o Índice de Compatibilidade</div>
            <p className="radar-legenda-descricao">
              Cada edital recebe uma pontuação de <strong>0 a 100 pontos</strong> com base no perfil do cliente, calculada em 5 critérios:
            </p>
            <div className="radar-legenda-criterios">
              <div className="radar-legenda-criterio">
                <span className="radar-legenda-pts">até 35 pts</span>
                <div>
                  <strong>Área e Temas</strong>
                  <span>Cruza área de inovação, setor, temas de interesse e descrição do projeto do cliente com os temas, título, objetivo, público-alvo e elegibilidade do edital. +7 por palavra em comum.</span>
                </div>
              </div>
              <div className="radar-legenda-criterio">
                <span className="radar-legenda-pts">até 20 pts</span>
                <div>
                  <strong>Localização</strong>
                  <span>20 pts se o edital é nacional ou está no mesmo estado do cliente. 15 pts se mesma região. 10 pts se sem restrição geográfica.</span>
                </div>
              </div>
              <div className="radar-legenda-criterio">
                <span className="radar-legenda-pts">até 20 pts</span>
                <div>
                  <strong>Porte / Elegibilidade</strong>
                  <span>20 pts se o porte do cliente (MEI, ME, EPP, Média, Grande) é explicitamente compatível com o público-alvo do edital. 15 pts se o edital não restringe porte.</span>
                </div>
              </div>
              <div className="radar-legenda-criterio">
                <span className="radar-legenda-pts">até 15 pts</span>
                <div>
                  <strong>Faixa de Valor</strong>
                  <span>15 pts se o valor do edital está dentro da faixa de interesse do cliente. 8 pts se há sobreposição parcial. 10 pts se o cliente não definiu faixa (neutro).</span>
                </div>
              </div>
              <div className="radar-legenda-criterio">
                <span className="radar-legenda-pts">até 10 pts</span>
                <div>
                  <strong>Regularidade</strong>
                  <span>Bônus por regularidade fiscal e trabalhista (+4 pts), certidão negativa (+3 pts) e disponibilidade de contrapartida (+3 pts).</span>
                </div>
              </div>
            </div>
            <div className="radar-legenda-cores">
              <span className="radar-legenda-cor radar-legenda-cor-alta">● Alta — 75 a 100 pts</span>
              <span className="radar-legenda-cor radar-legenda-cor-media">● Média — 45 a 74 pts</span>
              <span className="radar-legenda-cor radar-legenda-cor-baixa">● Baixa — 0 a 44 pts</span>
            </div>
          </div>

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
                    {recomendacoesFiltradas.length} edital(is) encontrado(s)
                    {melhoresOportunidades.length > 0 && (
                      <> · <strong style={{ color: '#22c55e' }}>{melhoresOportunidades.length} alta compatibilidade</strong></>
                    )}
                    {favoritosCliente.size > 0 && (
                      <> · <strong style={{ color: '#f59e0b' }}>★ {favoritosCliente.size} favoritado(s)</strong></>
                    )}
                  </p>
                </div>
                <button className="radar-btn-recalc" onClick={() => setRecalcKey(k => k + 1)}>
                  🔄 Recalcular
                </button>
              </div>

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
                <select value={filtroTipo} onChange={e => setFiltroTipo(e.target.value)} className="radar-select">
                  <option value="">Todos os tipos</option>
                  <option value="Linha de crédito">Linha de crédito</option>
                  <option value="Subvenção econômica">Subvenção econômica</option>
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

              {/* Melhores oportunidades */}
              {melhoresOportunidades.length > 0 && (
                <section className="radar-secao">
                  <h3 className="radar-secao-titulo">⭐ Melhores Oportunidades</h3>
                  <div className="radar-grid">
                    {melhoresOportunidades.map(({ edital, score, compatibilidade, razoes }) => (
                      <CardEditalRadar
                        key={edital.id}
                        edital={edital}
                        score={score}
                        compatibilidade={compatibilidade}
                        razoes={razoes}
                        favorito={favoritosCliente.has(edital.id)}
                        onFavoritar={toggleFavorito}
                      />
                    ))}
                  </div>
                </section>
              )}

              {/* Demais editais */}
              {demais.length > 0 && (
                <section className="radar-secao">
                  {melhoresOportunidades.length > 0 && (
                    <h3 className="radar-secao-titulo">Outros Editais</h3>
                  )}
                  <div className="radar-grid">
                    {demais.map(({ edital, score, compatibilidade, razoes }) => (
                      <CardEditalRadar
                        key={edital.id}
                        edital={edital}
                        score={score}
                        compatibilidade={compatibilidade}
                        razoes={razoes}
                        favorito={favoritosCliente.has(edital.id)}
                        onFavoritar={toggleFavorito}
                      />
                    ))}
                  </div>
                </section>
              )}

              {recomendacoesFiltradas.length === 0 && (
                <div className="radar-empty">
                  {filtroFavs && favoritosCliente.size === 0
                    ? 'Nenhum edital favoritado ainda. Clique em ☆ nos cards para favoritar.'
                    : 'Nenhum edital encontrado com os filtros aplicados.'}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
