/**
 * Lista pendências obrigatórias/recomendadas com navegação.
 */

export default function PrecadPendenciasPanel({
  completeness,
  fieldTargets = [],
  onNavigateField,
}) {
  const rq = completeness?.requiredMissing || [];
  const rec = completeness?.recommendedMissing || [];
  const consult = completeness?.consultivePendencies || [];

  return (
    <div className="precad-pend-panel">
      <h3 className="precad-subtitle">Pendências</h3>
      <p className="precad-muted small">
        {rq.length} obrigatória{rq.length === 1 ? '' : 's'} · {rec.length} recomendada{rec.length === 1 ? '' : 's'}
        {consult.length ? ` · ${consult.length} ação${consult.length === 1 ? '' : 'ões'} consultiva${consult.length === 1 ? '' : 's'}` : ''}
      </p>
      {consult.length ? (
        <div className="precad-pend-block precad-pend-block--consult">
          <h4>Para fechar com o cliente</h4>
          <ul className="precad-pend-list">
            {consult.map((t) => (
              <li key={`cv-${t}`}>{t}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {rq.length ? (
        <div className="precad-pend-block">
          <h4>Obrigatórias</h4>
          <ul className="precad-pend-list">
            {rq.map((t) => (
              <li key={`rq-${t}`}>
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="precad-muted small ok">Nenhuma pendência obrigatória automatizada pendente ✓</p>
      )}
      {rec.length ? (
        <div className="precad-pend-block muted">
          <h4>Recomendadas</h4>
          <ul className="precad-pend-list">
            {rec.slice(0, 10).map((t) => (
              <li key={`rc-${t}`}>{t}</li>
            ))}
            {rec.length > 10 ? <li className="small">…e outras.</li> : null}
          </ul>
        </div>
      ) : null}
      {fieldTargets?.length ? (
        <div className="precad-pend-jumps">
          <span className="precad-muted small">Ir aos campos-chave:</span>
          <div className="precad-pend-buttons">
            {fieldTargets.map(({ id, label }) => (
              <button key={id} type="button" className="precad-mini-btn" onClick={() => onNavigateField?.(id)}>
                {label}
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
