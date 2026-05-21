import ConsultorClientStatusBadge from './ConsultorClientStatusBadge';

/**
 * Status + descrição + CTA principal no topo do painel do cliente.
 */
export default function ConsultorClientStatusBanner({
  status,
  onPrimaryAction,
  primaryActionDisabled = false,
}) {
  if (!status?.key) return null;

  const hasCta = Boolean(status.primaryActionLabel && status.primaryActionType && onPrimaryAction);

  return (
    <div className="consultor-client-status-banner">
      <div className="consultor-client-status-banner-row">
        <span className="consultor-client-status-banner-label">Status:</span>
        <ConsultorClientStatusBadge status={status} />
      </div>
      {status.description ? (
        <p className="consultor-client-status-banner-desc">{status.description}</p>
      ) : null}
      {hasCta ? (
        <button
          type="button"
          className="btn-view consultor-client-status-cta"
          disabled={primaryActionDisabled}
          onClick={() => onPrimaryAction(status.primaryActionType, status)}
        >
          {status.primaryActionLabel}
        </button>
      ) : null}
    </div>
  );
}
