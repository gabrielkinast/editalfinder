import Modal from '../ui/Modal';
import {
  formatTimelineDate,
  TIMELINE_TYPE_LABEL,
} from '../../utils/consultor/consultorClientTimeline';

/**
 * Modal com histórico completo do cliente.
 */
export default function ConsultorClientTimelineModal({
  isOpen = false,
  onClose,
  events = [],
  clienteNome = '',
}) {
  if (!isOpen) return null;

  return (
    <Modal portal zIndex={1187} onClose={onClose} className="modal-large modal-consultor-timeline">
      <div className="consultor-timeline-modal-shell">
        <header className="consultor-timeline-modal-head">
          <div>
            <h2 className="consultor-timeline-modal-title">Histórico completo</h2>
            {clienteNome ? <p className="consultor-timeline-modal-sub">{clienteNome}</p> : null}
          </div>
          <button
            type="button"
            className="consultor-all-opps-close-x"
            onClick={onClose}
            aria-label="Fechar"
          >
            ×
          </button>
        </header>
        <div className="consultor-timeline-modal-body">
          {events.length === 0 ? (
            <p className="consultor-timeline-empty">Nenhuma atividade registrada ainda.</p>
          ) : (
            <ol className="consultor-timeline-modal-list">
              {events.map((ev) => (
                <li key={ev.id} className="consultor-timeline-modal-item">
                  <div className="consultor-timeline-item-head">
                    <time className="consultor-timeline-date" dateTime={ev.createdAt}>
                      {formatTimelineDate(ev.createdAt)}
                    </time>
                    <span
                      className={`consultor-timeline-type consultor-timeline-type--${ev.type}`}
                    >
                      {TIMELINE_TYPE_LABEL[ev.type] || ev.type}
                    </span>
                  </div>
                  <p className="consultor-timeline-item-title">{ev.title}</p>
                  {ev.description ? (
                    <p className="consultor-timeline-item-desc">{ev.description}</p>
                  ) : null}
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </Modal>
  );
}
