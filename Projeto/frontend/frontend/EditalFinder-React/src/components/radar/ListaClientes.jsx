function rowKey(c, idx) {
  const v = c?.id_cliente ?? c?.id;
  return v !== undefined && v !== null ? String(v) : `idx-${idx}`;
}

function textoSetor(setor) {
  if (setor == null || setor === '') return null;
  const s =
    typeof setor === 'string'
      ? setor
      : Array.isArray(setor)
        ? setor.map(String).join(', ')
        : String(setor);
  const t = s.trim();
  if (!t) return null;
  return t.length > 20 ? `${t.slice(0, 20)}…` : t;
}

export default function ListaClientes({
  clientes,
  clienteIdSelecionado = null,
  favoritosCount = {},
  onSelecionar,
  loading,
}) {
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
          {clientes.map((c, idx) => {
            const key = rowKey(c, idx);
            const qtdFavs = favoritosCount[c.id_cliente] ?? favoritosCount[String(c.id_cliente)] ?? 0;
            const ativo = clienteIdSelecionado != null && String(clienteIdSelecionado) === String(key);
            const setorTxt = textoSetor(c.setor);
            return (
              <li key={key} className="radar-cliente-li">
                <div
                  role="button"
                  tabIndex={0}
                  className={`radar-cliente-item ${ativo ? 'ativo' : ''}`}
                  onClick={() => onSelecionar?.(c, idx)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelecionar?.(c, idx);
                    }
                  }}
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
                    {setorTxt && <span className="radar-tag radar-tag-setor">{setorTxt}</span>}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
