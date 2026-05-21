import { getBriefingWorkflowBadge, hasBriefingContent } from '../cliente/clientBriefingSignals';

/**
 * Etapas da esteira de consultoria no Workspace (visual, derivado de dados existentes).
 */

export const WORKFLOW_STEP_IDS = {
  PERFIL: 'perfil',
  CARTEIRA: 'carteira',
  SELECAO: 'selecao',
  PREPROJETO: 'preprojeto',
  RELATORIO: 'relatorio',
};

/** @typedef {'complete'|'active'|'pending'|'soon'} WorkflowStepStatus */

const STEP_DEFS = [
  { id: WORKFLOW_STEP_IDS.PERFIL, label: 'Perfil do cliente', flag: 'perfil' },
  { id: WORKFLOW_STEP_IDS.CARTEIRA, label: 'Carteira de oportunidades', flag: 'carteira' },
  { id: WORKFLOW_STEP_IDS.SELECAO, label: 'Triagem e seleção', flag: 'selecao' },
  { id: WORKFLOW_STEP_IDS.PREPROJETO, label: 'Pré-projeto consultivo', flag: 'preprojeto' },
  { id: WORKFLOW_STEP_IDS.RELATORIO, label: 'Relatório / exportação', soon: true },
];

/**
 * @param {object} input
 * @param {number} [input.profileScore]
 * @param {number} [input.profileThreshold=70]
 * @param {number} [input.totalMatches]
 * @param {boolean} [input.radarReady]
 * @param {number} [input.selectedCount]
 * @param {boolean} [input.precadHadDraft]
 * @param {object|null} [input.cliente]
 * @param {boolean} [input.hasCliente]
 */
export function deriveConsultorWorkflowSteps(input = {}) {
  const {
    profileScore = 0,
    profileThreshold = 70,
    totalMatches = 0,
    radarReady = false,
    selectedCount = 0,
    precadHadDraft = false,
    hasCliente = false,
    cliente = null,
  } = input;

  const flags = {
    perfil: hasCliente && profileScore >= profileThreshold,
    carteira: hasCliente && radarReady && totalMatches > 0,
    selecao: selectedCount >= 1,
    preprojeto: precadHadDraft,
  };

  let assignedActive = false;

  const briefingBadge =
    hasCliente && cliente
      ? getBriefingWorkflowBadge(cliente, profileScore, profileThreshold)
      : { kind: null, label: '' };

  return STEP_DEFS.map((def) => {
    if (def.soon) {
      return { id: def.id, label: def.label, status: /** @type {WorkflowStepStatus} */ ('soon') };
    }
    const complete = flags[def.flag];
    let briefingNote = '';
    let briefingNoteKind = null;
    if (def.id === WORKFLOW_STEP_IDS.PERFIL && briefingBadge.label) {
      briefingNote = briefingBadge.label;
      briefingNoteKind = briefingBadge.kind;
    }
    if (!hasCliente) {
      return {
        id: def.id,
        label: def.label,
        status: 'pending',
        briefingNote,
        briefingNoteKind,
      };
    }
    if (complete) {
      return {
        id: def.id,
        label: def.label,
        status: 'complete',
        briefingNote,
        briefingNoteKind,
      };
    }
    if (!assignedActive) {
      assignedActive = true;
      return {
        id: def.id,
        label: def.label,
        status: 'active',
        briefingNote,
        briefingNoteKind,
      };
    }
    return {
      id: def.id,
      label: def.label,
      status: 'pending',
      briefingNote,
      briefingNoteKind,
    };
  });
}
