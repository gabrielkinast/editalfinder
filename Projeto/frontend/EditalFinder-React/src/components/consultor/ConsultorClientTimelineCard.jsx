import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  clearClientTimeline,
  formatTimelineDate,
  loadClientTimeline,
  TIMELINE_TYPE_LABEL,
} from '../../utils/consultor/consultorClientTimeline';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';
import ConsultorClientTimelineModal from './ConsultorClientTimelineModal';

const VISIBLE_LIMIT = 5;

/**
 * Card “Histórico do cliente” — linha do tempo local (Workspace).
 */
export default function ConsultorClientTimelineCard({ cliente = null, refreshTick = 0 }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [localTick, setLocalTick] = useState(0);

  const clienteId = cliente?.id_cliente ?? cliente?.id ?? null;
  const clienteNome = cliente?.nome_empresa || cliente?.razao_social || '';

  const events = useMemo(() => {
    void refreshTick;
    void localTick;
    return loadClientTimeline(clienteId);
  }, [clienteId, refreshTick, localTick]);

  useEffect(() => {
    if (!clienteId) return;
    logConsultorWorkspace('timeline_loaded', {
      id_cliente: clienteId,
      count: events.length,
    });
  }, [clienteId, events.length]);

  const visibleEvents = events.slice(0, VISIBLE_LIMIT);
  const hasMore = events.length > VISIBLE_LIMIT;

  const handleOpenFull = useCallback(() => {
    logConsultorWorkspace('timeline_open', { id_cliente: clienteId, full: true });
    setModalOpen(true);
  }, [clienteId]);

  const handleClear = useCallback(() => {
    if (!clienteId) return;
    const ok = window.confirm(
      'Limpar todo o histórico local deste cliente? Esta ação não pode ser desfeita.',
    );
    if (!ok) return;
    clearClientTimeline(clienteId);
    setLocalTick((t) => t + 1);
    setModalOpen(false);
  }, [clienteId]);

  if (!cliente) return null;

  return (
    <>
      <section className="consultor-section consultor-section--timeline">
        <div className="consultor-section-head">
          <div>
            <h3 className="consultor-section-title">Histórico do cliente</h3>
            <p className="consultor-section-sub">
              Atividades recentes neste navegador (briefing, triagem, pré-projeto, exportações).
            </p>
          </div>
        </div>

        {events.length === 0 ? (
          <p className="consultor-timeline-empty">Nenhuma atividade registrada ainda.</p>
        ) : (
          <ol className="consultor-timeline-list">
            {visibleEvents.map((ev) => (
              <li key={ev.id} className="consultor-timeline-item">
                <div className="consultor-timeline-item-head">
                  <time className="consultor-timeline-date" dateTime={ev.createdAt}>
                    {formatTimelineDate(ev.createdAt)}
                  </time>
                  <span className={`consultor-timeline-type consultor-timeline-type--${ev.type}`}>
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

        <div className="consultor-timeline-footer">
          {hasMore ? (
            <button type="button" className="btn-view consultor-timeline-footer-btn" onClick={handleOpenFull}>
              Ver histórico completo ({events.length})
            </button>
          ) : events.length > 0 ? (
            <button
              type="button"
              className="btn-detalhes dash-action-outline consultor-timeline-footer-btn"
              onClick={handleOpenFull}
            >
              Ver histórico completo
            </button>
          ) : null}
          {events.length > 0 ? (
            <button
              type="button"
              className="btn-detalhes dash-action-outline consultor-timeline-footer-btn consultor-timeline-clear-btn"
              onClick={handleClear}
            >
              Limpar histórico local
            </button>
          ) : null}
        </div>
      </section>

      <ConsultorClientTimelineModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        events={events}
        clienteNome={clienteNome}
      />
    </>
  );
}
