import { deriveConsultorWorkflowSteps } from '../../utils/consultor/workflowSteps';

const STATUS_LABEL = {
  complete: 'Completo',
  active: 'Em andamento',
  pending: 'Pendente',
  soon: 'Em breve',
};

/**
 * Barra visual da esteira: Perfil → Carteira → Seleção → Pré-projeto → Relatório.
 */
export default function ConsultorWorkflowSteps({
  profileScore = 0,
  totalMatches = 0,
  radarReady = false,
  selectedCount = 0,
  precadHadDraft = false,
  hasCliente = true,
  cliente = null,
}) {
  const steps = deriveConsultorWorkflowSteps({
    profileScore,
    totalMatches,
    radarReady,
    selectedCount,
    precadHadDraft,
    hasCliente,
    cliente,
  });

  return (
    <nav className="consultor-workflow" aria-label="Esteira de consultoria em fomento">
      <ol className="consultor-workflow-list">
        {steps.map((step, idx) => (
          <li key={step.id} className="consultor-workflow-item-wrap">
            {idx > 0 ? <span className="consultor-workflow-arrow" aria-hidden="true" /> : null}
            <div className={`consultor-workflow-step consultor-workflow-step--${step.status}`}>
              <span className="consultor-workflow-step-num">{idx + 1}</span>
              <span className="consultor-workflow-step-label">{step.label}</span>
              <span className="consultor-workflow-step-status">{STATUS_LABEL[step.status]}</span>
              {step.briefingNote ? (
                <span
                  className={`consultor-workflow-briefing-note consultor-workflow-briefing-note--${step.briefingNoteKind || 'default'}`}
                >
                  {step.briefingNote}
                </span>
              ) : null}
            </div>
          </li>
        ))}
      </ol>
    </nav>
  );
}
