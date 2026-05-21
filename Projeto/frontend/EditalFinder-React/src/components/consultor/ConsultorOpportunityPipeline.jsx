import { useNavigate } from 'react-router-dom';
import { getOpportunitySelectionKey } from '../../utils/consultor/opportunitySelection';
import {
  compatClass,
  prazoBadgeClass,
  rowDisplayFields,
} from '../../utils/consultor/consultorOpportunityRowDisplay';

/**
 * Lista top oportunidades — layout em grid legível.
 */
export default function ConsultorOpportunityPipeline({
  matches = [],
  selectedKeys = null,
  onToggleSelect,
  onGerarPreProjeto,
  onOpenRadar,
}) {
  const navigate = useNavigate();
  const selectedSet = selectedKeys instanceof Set ? selectedKeys : new Set(selectedKeys || []);
  const list = Array.isArray(matches) ? matches : [];

  if (!list.length) return null;

  const openEdital = (id) => {
    if (id == null) return;
    navigate(`/edital/${String(id).replace(/^manual-/, '')}`);
  };

  return (
    <ul className="consultor-pipeline-list consultor-pipeline-list--grid">
      {list.map((row) => {
        const selKey = getOpportunitySelectionKey(row);
        const d = rowDisplayFields(row);
        const isSelected = selectedSet.has(selKey);

        return (
          <li
            key={selKey}
            className={`consultor-opp-grid-item ${isSelected ? 'consultor-opp-grid-item--selected' : ''}`}
          >
            {onToggleSelect ? (
              <label
                className="consultor-opp-grid-check"
                onClick={(e) => e.stopPropagation()}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={(e) => {
                    e.stopPropagation();
                    onToggleSelect(row, selKey, e.target.checked);
                  }}
                  onClick={(e) => e.stopPropagation()}
                  aria-label={`Selecionar ${d.titulo}`}
                />
              </label>
            ) : (
              <span className="consultor-opp-grid-check-spacer" aria-hidden />
            )}

            <div className="consultor-opp-grid-body">
              <div className="consultor-opp-grid-row1">
                <button
                  type="button"
                  className="consultor-opp-grid-title"
                  onClick={() => openEdital(d.id)}
                  title={d.titulo}
                >
                  {d.titulo}
                </button>
                <span className={`consultor-opp-grid-score ${compatClass(d.compatibilidade)}`}>
                  {d.compatibilidade} · {d.score}%
                </span>
              </div>
              <div className="consultor-opp-grid-row2">
                <div className="consultor-opp-grid-meta">
                  <span className="consultor-opp-grid-fonte" title={d.fonte}>
                    {d.fonte}
                  </span>
                  <span className={`consultor-opp-grid-prazo ${prazoBadgeClass(d.prazoStatus)}`}>
                    {d.prazoLabel}
                  </span>
                </div>
                <div className="consultor-opp-grid-actions">
                  {d.id != null ? (
                    <button
                      type="button"
                      className="btn-detalhes dash-action-outline consultor-opp-grid-link"
                      onClick={() => openEdital(d.id)}
                    >
                      Ver edital
                    </button>
                  ) : null}
                  {onOpenRadar ? (
                    <button
                      type="button"
                      className="btn-detalhes dash-action-outline consultor-opp-grid-link consultor-opp-grid-link--radar"
                      onClick={() => onOpenRadar(row)}
                    >
                      Radar
                    </button>
                  ) : null}
                  {onGerarPreProjeto && !onToggleSelect ? (
                    <button
                      type="button"
                      className="btn-view consultor-opp-grid-link"
                      onClick={() => onGerarPreProjeto(row)}
                    >
                      Pré-projeto
                    </button>
                  ) : null}
                </div>
              </div>
              {d.motivo ? (
                <p className="consultor-opp-grid-motivo" title={d.motivo}>
                  {d.motivo}
                </p>
              ) : null}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
