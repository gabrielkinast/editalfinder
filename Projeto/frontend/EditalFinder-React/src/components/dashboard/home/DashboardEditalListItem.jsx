import { Link } from 'react-router-dom';
import { formatDateLoose } from '../../../utils/formatters';
import { getFonte } from '../../../utils/edital/editalFieldHelpers';
import {
  getDaysUntilDeadline,
  getDeadlineAlertLabel,
  getDeadlineAlertStatus,
  getDeadlineAlertBadgeVariant,
  parsePrazoEnvio,
} from '../../../utils/deadlineAlerts';

function editalTitle(e) {
  return e.titulo || e.title || e.nome || `Edital #${e.id_edital || e.id || ''}`;
}

function editalId(e) {
  return e.id_edital ?? e.id;
}

function prazoDisplay(e) {
  const raw = parsePrazoEnvio(e);
  if (!raw) return null;
  return formatDateLoose(raw);
}

/**
 * @param {object} props
 * @param {object} props.edital
 * @param {boolean} [props.urgentHighlight]
 */
export default function DashboardEditalListItem({ edital, urgentHighlight = false }) {
  const id = editalId(edital);
  const status = getDeadlineAlertStatus(edital);
  const badgeVariant = getDeadlineAlertBadgeVariant(status);
  const statusLabel = getDeadlineAlertLabel(status);
  const days = getDaysUntilDeadline(edital);
  const dateStr = prazoDisplay(edital);
  const isUrgent =
    urgentHighlight &&
    days != null &&
    days >= 0 &&
    days <= 7 &&
    status !== 'encerrado' &&
    status !== 'prazo_indefinido';

  return (
    <li
      className={`home-dash-edital-row ${isUrgent ? 'home-dash-edital-row--urgent' : ''}`}
    >
      <div className="home-dash-edital-row-main">
        <Link
          to={id ? `/edital/${id}` : '/editais'}
          className="home-dash-edital-title-link"
        >
          {editalTitle(edital)}
        </Link>
        <div className="home-dash-edital-tags">
          <span className="home-dash-badge home-dash-badge--muted">{getFonte(edital)}</span>
          <span className={`home-dash-badge home-dash-badge--${badgeVariant}`}>
            {statusLabel}
          </span>
          {dateStr ? (
            <span className="home-dash-badge home-dash-badge--date">{dateStr}</span>
          ) : (
            <span className="home-dash-badge home-dash-badge--muted">Prazo não informado</span>
          )}
        </div>
      </div>
      <Link
        to={id ? `/edital/${id}` : '/editais'}
        className="home-dash-edital-open-btn"
      >
        Abrir
      </Link>
    </li>
  );
}
