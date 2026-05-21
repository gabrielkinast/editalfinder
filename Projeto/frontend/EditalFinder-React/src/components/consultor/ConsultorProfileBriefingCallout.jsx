import { useEffect } from 'react';
import { logClienteBriefing } from '../../utils/cliente/clienteBriefingLog';

/**
 * Callout compacto quando o perfil está muito incompleto (< 50%).
 */
export default function ConsultorProfileBriefingCallout({
  visible = false,
  canEdit = false,
  onBriefingRapido,
  onCompletarCadastro,
}) {
  useEffect(() => {
    if (!visible || !canEdit) return;
    logClienteBriefing('cta_visible', { placement: 'callout' });
  }, [visible, canEdit]);

  if (!visible || !canEdit) return null;

  return (
    <aside className="consultor-briefing-callout" role="note">
      <p className="consultor-briefing-callout-text">
        <strong>Perfil incompleto:</strong> faça um briefing rápido para melhorar recomendações e
        reduzir pendências no pré-projeto.
      </p>
      <div className="consultor-briefing-callout-actions">
        <button
          type="button"
          className="btn-view"
          onClick={() => onBriefingRapido?.('callout')}
        >
          Fazer briefing rápido
        </button>
        <button type="button" className="btn-detalhes dash-action-outline" onClick={onCompletarCadastro}>
          Completar cadastro
        </button>
      </div>
    </aside>
  );
}
