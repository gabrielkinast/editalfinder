import { useNavigate } from 'react-router-dom';
import { TRACKED_BADGE_LABEL } from '../../utils/consultor/buildConsultorTrackedOpportunities';
import { compatClass } from '../../utils/consultor/consultorOpportunityRowDisplay';

/**
 * Linha de oportunidade acompanhada no card/modal do Workspace.
 */
export default function ConsultorTrackedOpportunityRow({
  item,
  onOpenRadar,
  onRemove,
  showRemove = false,
}) {
  const navigate = useNavigate();
  const editalId = item.editalId;
  const editalPath =
    editalId != null ? `/edital/${String(editalId).replace(/^manual-/, '')}` : null;

  const handleOpen = (type) => {
    if (type === 'edital' && editalPath) navigate(editalPath);
    if (type === 'radar') onOpenRadar?.(item);
  };

  return (
    <li className="consultor-tracked-item">
      <div className="consultor-tracked-item-head">
        <div className="consultor-tracked-badges">
          {(item.badges || []).map((b) => (
            <span key={b} className={`consultor-tracked-badge consultor-tracked-badge--${b}`}>
              {TRACKED_BADGE_LABEL[b] || b}
            </span>
          ))}
        </div>
        {item.compatibilidade || item.scorePct != null ? (
          <span className={`consultor-tracked-compat ${compatClass(item.compatibilidade || 'Baixa')}`}>
            {item.compatibilidade ? `${item.compatibilidade}` : ''}
            {item.scorePct != null ? `${item.compatibilidade ? ' · ' : ''}${item.scorePct}%` : ''}
          </span>
        ) : null}
      </div>
      <p className="consultor-tracked-title" title={item.titulo}>
        {item.titulo}
      </p>
      <p className="consultor-tracked-meta">
        <span>{item.fonte || '—'}</span>
        <span className="consultor-tracked-meta-sep">·</span>
        <span>{item.prazo || '—'}</span>
      </p>
      <div className="consultor-tracked-actions">
        {editalPath ? (
          <button type="button" className="consultor-tracked-btn" onClick={() => handleOpen('edital')}>
            Ver edital
          </button>
        ) : item.link ? (
          <a
            className="consultor-tracked-btn consultor-tracked-btn--link"
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
          >
            Ver edital
          </a>
        ) : null}
        {onOpenRadar ? (
          <button type="button" className="consultor-tracked-btn" onClick={() => handleOpen('radar')}>
            Abrir no Radar
          </button>
        ) : null}
        {showRemove && onRemove ? (
          <button
            type="button"
            className="consultor-tracked-btn consultor-tracked-btn--muted"
            onClick={() => onRemove(item)}
          >
            Remover
          </button>
        ) : null}
      </div>
    </li>
  );
}
