import { Link } from 'react-router-dom';
import { useAppFeedback } from '../../../contexts/AppFeedbackContext';

function PriorityCard({ item }) {
  const { openAppFeedbackModal } = useAppFeedback();

  return (
    <article className="home-dash-priority-item">
      <div className="home-dash-priority-item-head">
        <span className={`home-dash-badge home-dash-badge--${item.badgeVariant || 'info'}`}>
          {item.badge}
        </span>
      </div>
      <h4 className="home-dash-priority-title">{item.title}</h4>
      <p className="home-dash-priority-desc">{item.description}</p>
      {item.ctaLabel && item.to && (
        <Link to={item.to} className="home-dash-priority-cta">
          {item.ctaLabel}
        </Link>
      )}
      {item.ctaLabel && item.action === 'feedback' && (
        <button
          type="button"
          className="home-dash-priority-cta home-dash-priority-cta--btn"
          onClick={() =>
            openAppFeedbackModal({
              origem: 'dashboard',
              pagina: 'Dashboard',
              componente: 'DashboardPriorityPanel',
              acao: 'ver_relatorios_pendentes',
              tipo: 'outro',
            })
          }
        >
          {item.ctaLabel}
        </button>
      )}
    </article>
  );
}

/**
 * @param {object} props
 * @param {Array<object>} props.priorities
 * @param {boolean} props.loading
 */
export default function DashboardPriorityPanel({ priorities = [], loading }) {
  return (
    <section className="home-dash-panel home-dash-priority-panel" aria-label="Prioridades agora">
      <div className="home-dash-priority-panel-head">
        <div>
          <h2 className="home-dash-priority-panel-title">Prioridades agora</h2>
          <p className="home-dash-priority-panel-sub">
            O que merece sua atenção nesta sessão
          </p>
        </div>
      </div>
      {loading ? (
        <p className="home-dash-muted">Analisando prioridades…</p>
      ) : (
        <div className="home-dash-priority-grid">
          {priorities.map((item) => (
            <PriorityCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}
