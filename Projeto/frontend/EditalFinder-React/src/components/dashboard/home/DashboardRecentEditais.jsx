import { Link } from 'react-router-dom';
import DashboardEmptyState from './DashboardEmptyState';
import DashboardEditalListItem from './DashboardEditalListItem';

export default function DashboardRecentEditais({
  items = [],
  loading,
  title = 'Editais recentes',
}) {
  return (
    <div className="home-dash-panel home-dash-list-panel">
      <div className="home-dash-panel-head">
        <h3 className="home-dash-panel-title">{title}</h3>
        <Link to="/editais" className="home-dash-panel-link">
          Ver todos
        </Link>
      </div>
      {loading ? (
        <p className="home-dash-muted">Carregando…</p>
      ) : !items.length ? (
        <DashboardEmptyState
          title="Nenhum edital encontrado ainda."
          message="Quando houver editais no catálogo, eles aparecerão aqui."
          action={
            <Link to="/editais" className="home-dash-cta-link">
              Ir para editais
            </Link>
          }
        />
      ) : (
        <ul className="home-dash-edital-list home-dash-edital-list--rich">
          {items.map((e) => (
            <DashboardEditalListItem
              key={e.id_edital ?? e.id ?? e.titulo}
              edital={e}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
