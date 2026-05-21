import { useEffect, useMemo } from 'react';
import { calculateClientProfileCompleteness } from '../../utils/cliente/calculateClientProfileCompleteness';
import { hasBriefingContent } from '../../utils/cliente/clientBriefingSignals';
import { logClienteBriefing } from '../../utils/cliente/clienteBriefingLog';

const PROFILE_STRONG_THRESHOLD = 70;

/**
 * Card “Perfil do cliente” no painel do Workspace.
 */
export default function ConsultorClientProfileCard({
  cliente,
  canEdit = false,
  onCompletarCadastro,
  onEditarCliente,
  onBriefingRapido,
}) {
  const completeness = useMemo(
    () => (cliente ? calculateClientProfileCompleteness(cliente) : null),
    [cliente],
  );

  const score = completeness?.score ?? 0;
  const profileLow = score < PROFILE_STRONG_THRESHOLD;
  const briefingSaved = useMemo(() => hasBriefingContent(cliente), [cliente]);
  const briefingIsPrimary = profileLow || briefingSaved;
  const briefingLabel = briefingSaved ? 'Atualizar briefing' : 'Fazer briefing rápido';

  const guidanceText = briefingSaved
    ? 'Briefing salvo. Você pode atualizar o briefing ou completar o cadastro consultivo para melhorar as próximas recomendações.'
    : profileLow
      ? 'Comece pelo briefing: ele preenche o essencial para gerar carteira, triagem e pré-projeto com menos retrabalho.'
      : null;

  useEffect(() => {
    if (!canEdit || !cliente) return;
    if (briefingIsPrimary) {
      logClienteBriefing('cta_visible', {
        placement: 'profile_card',
        score,
        briefing_saved: briefingSaved,
      });
    }
  }, [canEdit, cliente, briefingIsPrimary, briefingSaved, score]);

  if (!cliente || !completeness) return null;

  const lacunas = [];
  for (const s of Object.values(completeness.sections)) {
    if (s.missing?.length) lacunas.push(...s.missing.slice(0, 2));
  }
  const lacunasUnicas = [...new Set(lacunas)].slice(0, 5);

  const handleBriefingClick = () => {
    logClienteBriefing('cta_click_profile_card', {
      id_cliente: cliente.id_cliente,
      score,
      label: briefingLabel,
    });
    onBriefingRapido?.('profile_card');
  };

  return (
    <section
      className={`consultor-section consultor-section--profile ${profileLow ? 'consultor-section--profile-low' : ''} ${briefingSaved ? 'consultor-section--profile-briefing-saved' : ''}`}
    >
      <div className="consultor-section-head">
        <div>
          <h3 className="consultor-section-title">Perfil do cliente</h3>
          {guidanceText ? (
            <p
              className={`consultor-profile-guidance ${briefingSaved ? 'consultor-profile-guidance--saved' : 'consultor-profile-guidance--start'}`}
            >
              {guidanceText}
            </p>
          ) : (
            <p className="consultor-section-sub consultor-profile-briefing-meta">
              Completude do cadastro consultivo — melhora pré-projetos, PDF e futuras regras do Radar.
            </p>
          )}
        </div>
        <span className={`consultor-profile-pct consultor-profile-pct--${completeness.level}`}>
          {completeness.score}% completo
        </span>
      </div>

      <p className="consultor-profile-hint">{completeness.radarImprovementHint}</p>

      {lacunasUnicas.length > 0 ? (
        <ul className="consultor-profile-gaps">
          {lacunasUnicas.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="consultor-muted-hint small">Perfil com boa cobertura para relatórios consultivos.</p>
      )}

      {canEdit ? (
        <div
          className={`consultor-profile-actions ${briefingIsPrimary ? 'consultor-profile-actions--briefing-first' : ''}`}
        >
          <button
            type="button"
            className={
              briefingIsPrimary
                ? 'btn-view consultor-btn-briefing-primary'
                : 'btn-detalhes dash-action-outline'
            }
            onClick={handleBriefingClick}
          >
            {briefingLabel}
          </button>
          <button
            type="button"
            className={briefingIsPrimary ? 'btn-detalhes dash-action-outline' : 'btn-view'}
            onClick={onCompletarCadastro}
          >
            Completar cadastro
          </button>
          <button
            type="button"
            className="btn-detalhes dash-action-outline"
            onClick={() => onEditarCliente?.(cliente)}
          >
            Editar cliente
          </button>
        </div>
      ) : null}
    </section>
  );
}
