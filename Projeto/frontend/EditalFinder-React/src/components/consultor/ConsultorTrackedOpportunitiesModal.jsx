import Modal from '../ui/Modal';
import ConsultorTrackedOpportunityRow from './ConsultorTrackedOpportunityRow';

/**
 * Modal simples com todas as oportunidades acompanhadas.
 */
export default function ConsultorTrackedOpportunitiesModal({
  isOpen = false,
  onClose,
  items = [],
  clienteNome = '',
  onOpenRadar,
  onRemoveTracked,
}) {
  if (!isOpen) return null;

  return (
    <Modal portal zIndex={1186} onClose={onClose} className="modal-large modal-consultor-tracked">
      <div className="consultor-tracked-modal-shell">
        <header className="consultor-tracked-modal-head">
          <div>
            <h2 className="consultor-tracked-modal-title">Oportunidades acompanhadas</h2>
            {clienteNome ? (
              <p className="consultor-tracked-modal-sub">{clienteNome}</p>
            ) : null}
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
        <div className="consultor-tracked-modal-body">
          {items.length === 0 ? (
            <p className="consultor-tracked-empty">
              Nenhuma oportunidade acompanhada ainda. Selecione oportunidades na carteira ou favorite
              editais para acompanhar.
            </p>
          ) : (
            <ul className="consultor-tracked-list">
              {items.map((item) => (
                <ConsultorTrackedOpportunityRow
                  key={item.key}
                  item={item}
                  onOpenRadar={onOpenRadar}
                  onRemove={onRemoveTracked}
                  showRemove
                />
              ))}
            </ul>
          )}
        </div>
      </div>
    </Modal>
  );
}
