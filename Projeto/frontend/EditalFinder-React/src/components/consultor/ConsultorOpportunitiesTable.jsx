import { useNavigate } from 'react-router-dom';
import { getOpportunitySelectionKey } from '../../utils/consultor/opportunitySelection';
import {
  compatClass,
  prazoBadgeClass,
  rowDisplayFields,
} from '../../utils/consultor/consultorOpportunityRowDisplay';

/**
 * Visão tabela da carteira (estilo planilha / NotebookLM).
 */
export default function ConsultorOpportunitiesTable({
  matches = [],
  selectedKeys = null,
  onToggleSelect,
  onOpenRadar,
}) {
  const navigate = useNavigate();
  const selectedSet =
    selectedKeys instanceof Set ? selectedKeys : new Set(selectedKeys || []);

  if (!matches.length) {
    return <p className="consultor-empty-matches">Nenhuma oportunidade para exibir na tabela.</p>;
  }

  return (
    <div className="consultor-opps-table-wrap">
      <table className="consultor-opps-table">
        <thead>
          <tr>
            <th scope="col" className="consultor-opps-table-col-check">
              Sel.
            </th>
            <th scope="col">Programa / Edital</th>
            <th scope="col">Fonte</th>
            <th scope="col">Prazo</th>
            <th scope="col">Tipo de apoio</th>
            <th scope="col">Foco temático</th>
            <th scope="col">Observações</th>
            <th scope="col">Compat.</th>
            <th scope="col" className="consultor-opps-table-col-link">
              Link
            </th>
          </tr>
        </thead>
        <tbody>
          {matches.map((row) => {
            const selKey = getOpportunitySelectionKey(row);
            const d = rowDisplayFields(row);
            const isSelected = selectedSet.has(selKey);
            const editalPath =
              d.id != null ? `/edital/${String(d.id).replace(/^manual-/, '')}` : null;

            return (
              <tr
                key={selKey}
                className={`consultor-opps-table-row ${isSelected ? 'consultor-opps-table-row--selected' : ''}`}
              >
                <td className="consultor-opps-table-col-check">
                  {onToggleSelect ? (
                    <input
                      type="checkbox"
                      checked={isSelected}
                      aria-label={`Selecionar ${d.titulo}`}
                      onChange={(e) => onToggleSelect(row, selKey, e.target.checked)}
                    />
                  ) : null}
                </td>
                <td className="consultor-opps-table-col-titulo" title={d.titulo}>
                  {editalPath ? (
                    <button
                      type="button"
                      className="consultor-opps-table-titulo-btn"
                      onClick={() => navigate(editalPath)}
                    >
                      {d.titulo}
                    </button>
                  ) : (
                    d.titulo
                  )}
                </td>
                <td title={d.fonte}>{d.fonte}</td>
                <td>
                  <span className={`consultor-opp-grid-prazo ${prazoBadgeClass(d.prazoStatus)}`}>
                    {d.prazoLabel}
                  </span>
                </td>
                <td title={d.tipoApoio}>{d.tipoApoio}</td>
                <td className="consultor-opps-table-col-foco" title={d.focoTematico}>
                  {d.focoTematico}
                </td>
                <td className="consultor-opps-table-col-obs" title={d.observacoes}>
                  {d.observacoes}
                </td>
                <td>
                  <span className={`consultor-compat-badge consultor-compat-badge--table ${compatClass(d.compatibilidade)}`}>
                    {d.score}%
                  </span>
                </td>
                <td className="consultor-opps-table-col-link">
                  {d.link ? (
                    <a
                      href={d.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="consultor-opps-table-link"
                    >
                      Abrir
                    </a>
                  ) : editalPath ? (
                    <button
                      type="button"
                      className="consultor-opps-table-link-btn"
                      onClick={() => navigate(editalPath)}
                    >
                      Abrir
                    </button>
                  ) : onOpenRadar ? (
                    <button
                      type="button"
                      className="consultor-opps-table-link-btn"
                      onClick={() => onOpenRadar(row)}
                    >
                      Radar
                    </button>
                  ) : (
                    '—'
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
