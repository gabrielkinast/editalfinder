import { ENABLE_SCIENTIFIC_AI } from '../../config/env';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

/**
 * Placeholder para IA científica futura (sem chamada no browser).
 */
export default function ScientificAiPlaceholder({ compact = false }) {
  if (ENABLE_SCIENTIFIC_AI) return null;

  const handleClick = () => {
    logScientificWorkspace('ai_placeholder_clicked', { enabled: false });
  };

  return (
    <p
      className={`scientific-ai-placeholder ${compact ? 'scientific-ai-placeholder--compact' : ''}`}
      role="note"
    >
      <button type="button" className="scientific-btn scientific-btn-ghost" onClick={handleClick}>
        IA científica — em breve
      </button>
      <span className="scientific-muted">
        {' '}
        (respostas via servidor; sem chave no navegador)
      </span>
    </p>
  );
}
