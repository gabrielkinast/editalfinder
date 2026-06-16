import { getEditalStatusBadges } from '../../utils/edital/editalStatusBadges';

const TONE_CLASS = {
  success: 'edital-b-ok',
  warning: 'edital-b-warn',
  danger: 'edital-b-bad',
  info: 'edital-b-info',
  neutral: 'edital-b-neutral',
  muted: 'edital-b-muted',
};

/**
 * Badges de validade/prazo/semântica reutilizáveis em cards, listas e detalhe.
 *
 * @param {Object} props
 * @param {unknown} props.edital
 * @param {number} [props.maxVisible=3]
 * @param {boolean} [props.compact=false]
 */
export default function EditalStatusBadges({ edital, maxVisible = 3, compact = false }) {
  const badges = getEditalStatusBadges(edital);
  if (!badges.length) return null;

  const limit = Number.isFinite(maxVisible) && maxVisible > 0 ? maxVisible : badges.length;
  const visible = badges.slice(0, limit);
  const hidden = badges.slice(limit);

  return (
    <div
      className={`edital-status-badges${compact ? ' edital-status-badges--compact' : ''}`}
      role="list"
      aria-label="Situação da oportunidade"
    >
      {visible.map((b) => (
        <span
          key={b.kind}
          role="listitem"
          className={`edital-badge-mini ${TONE_CLASS[b.tone] || 'edital-b-muted'}`}
          title={b.title}
        >
          {b.label}
        </span>
      ))}
      {hidden.length > 0 ? (
        <span
          className="edital-badge-mini edital-b-muted edital-status-more"
          title={hidden.map((b) => b.label).join(', ')}
        >
          +{hidden.length}
        </span>
      ) : null}
    </div>
  );
}
