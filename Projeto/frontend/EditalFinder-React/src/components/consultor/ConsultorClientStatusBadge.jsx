/**
 * Badge compacto de status do cliente no Workspace.
 */
export default function ConsultorClientStatusBadge({ status, className = '' }) {
  if (!status?.key) return null;
  const tone = status.tone || 'neutral';
  return (
    <span
      className={`consultor-client-status-badge consultor-client-status-badge--${tone} ${className}`.trim()}
      title={status.description || status.label}
    >
      {status.label}
    </span>
  );
}
