export default function ListaClientes({ clientes, clienteSelecionado, favoritosCount = {}, onSelecionar, loading }) {
  if (loading) {
    return (
      <div className="radar-clientes-panel">
        <div className="radar-panel-header">
          <h2 className="radar-panel-title">Clientes</h2>
        </div>
        <div className="radar-empty">Carregando clientes...</div>
      </div>
    );
  }

  return (
    <div className="radar-clientes-panel">
      <div className="radar-panel-header">
        <h2 className="radar-panel-title">Clientes</h2>
        <span className="radar-count-badge">{clientes.length}</span>
      </div>

      {clientes.length === 0 ? (
        <div className="radar-empty">Nenhum cliente cadastrado.</div>
      ) : (
        <ul className="radar-clientes-lista">
          {clientes.map(c => {
            const qtdFavs = favoritosCount[c.id_cliente] || 0;
            return (
              <li
                key={c.id_cliente}
                className={`radar-cliente-item ${clienteSelecionado?.id_cliente === c.id_cliente ? 'ativo' : ''}`}
                onClick={() => onSelecionar(c)}
              >
                <div className="radar-cliente-nome-row">
                  <span className="radar-cliente-nome">{c.nome_empresa}</span>
                  {qtdFavs > 0 && (
                    <span className="radar-cliente-fav-badge" title={`${qtdFavs} favorito(s)`}>
                      ★ {qtdFavs}
                    </span>
                  )}
                </div>
                <div className="radar-cliente-meta">
                  <span className="radar-tag">{c.porte_empresa || '—'}</span>
                  {c.estado && <span className="radar-tag">{c.estado}</span>}
                  {c.setor && (
                    <span className="radar-tag radar-tag-setor">
                      {c.setor.length > 20 ? c.setor.slice(0, 20) + '…' : c.setor}
                    </span>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
