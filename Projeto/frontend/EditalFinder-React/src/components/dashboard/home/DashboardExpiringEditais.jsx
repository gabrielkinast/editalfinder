import { Link } from 'react-router-dom';
import { buildEditaisUrl, scopeFilterToQueryParam } from '../../../utils/editais/editaisQueryFilters';
import DashboardEmptyState from './DashboardEmptyState';
import DashboardEditalListItem from './DashboardEditalListItem';

export default function DashboardExpiringEditais({ items = [], loading, scopeFilter }) {
  const scopeParam = scopeFilterToQueryParam(scopeFilter);
  const verTodosUrl = buildEditaisUrl({ prazo: 'vencendo_30', scope: scopeParam });

  return (
    <div className="home-dash-panel home-dash-list-panel home-dash-list-panel--expiring">
      <div className="home-dash-panel-head">
        <h3 className="home-dash-panel-title">Vencendo em breve</h3>
        <Link to={verTodosUrl} className="home-dash-panel-link">
          Ver todos
        </Link>
      </div>
      {loading ? (
        <p className="home-dash-muted">Carregando…</p>
      ) : !items.length ? (
        <DashboardEmptyState
          title="Nenhum edital com prazo nos próximos 30 dias."
          message="Ótimo momento para planejar novas buscas na listagem completa."
        />
      ) : (
        <ul className="home-dash-edital-list home-dash-edital-list--rich">
          {items.map((e) => (
            <DashboardEditalListItem
              key={e.id_edital ?? e.id ?? e.titulo}
              edital={e}
              urgentHighlight
            />
          ))}
        </ul>
      )}
    </div>
  );
}
