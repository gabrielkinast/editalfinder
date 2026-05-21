import { calculateClientProfileCompleteness } from '../cliente/calculateClientProfileCompleteness';
import { hasBriefingContent } from '../cliente/clientBriefingSignals';
import { getClientPrecadSummary } from '../precadastro/getClientPrecadSummary';
import { logConsultorWorkspace } from '../consultorWorkspaceLog';
import { loadRadarFavoritoIdsForCliente } from './buildConsultorTrackedOpportunities';
import { loadStoredTrackedItems } from './consultorTrackedOpportunitiesStorage';

/** @typedef {'warning'|'info'|'primary'|'success'|'neutral'} ClientStatusTone */

/** @typedef {'open_briefing'|'open_client_form'|'open_portfolio'|'open_triage_report'|'open_preproject'|'open_tracked'} ClientStatusPrimaryAction */

export const CLIENT_STATUS_KEYS = {
  PRECISA_BRIEFING: 'precisa_briefing',
  PERFIL_EM_MONTAGEM: 'perfil_em_montagem',
  CARTEIRA_PRONTA: 'carteira_pronta',
  TRIAGEM_EM_ANDAMENTO: 'triagem_em_andamento',
  PREPROJETO_EM_ELABORACAO: 'preprojeto_em_elaboracao',
  PRONTO_PARA_CLIENTE: 'pronto_para_cliente',
  ACOMPANHAMENTO: 'acompanhamento',
  EM_ANALISE: 'em_analise',
};

const STATUS_CATALOG = {
  [CLIENT_STATUS_KEYS.PRECISA_BRIEFING]: {
    key: CLIENT_STATUS_KEYS.PRECISA_BRIEFING,
    label: 'Precisa briefing',
    description: 'Complete o briefing rápido para melhorar carteira, triagem e pré-projeto.',
    tone: 'warning',
    priority: 60,
    primaryActionLabel: 'Fazer briefing',
    primaryActionType: 'open_briefing',
  },
  [CLIENT_STATUS_KEYS.PERFIL_EM_MONTAGEM]: {
    key: CLIENT_STATUS_KEYS.PERFIL_EM_MONTAGEM,
    label: 'Perfil em montagem',
    description: 'Complete o briefing e dados essenciais do cadastro consultivo.',
    tone: 'info',
    priority: 50,
    primaryActionLabel: 'Completar cadastro',
    primaryActionType: 'open_client_form',
  },
  [CLIENT_STATUS_KEYS.CARTEIRA_PRONTA]: {
    key: CLIENT_STATUS_KEYS.CARTEIRA_PRONTA,
    label: 'Carteira pronta',
    description:
      'Revise as oportunidades recomendadas e selecione até 20 para gerar triagem ou pré-projeto.',
    tone: 'info',
    priority: 40,
    primaryActionLabel: 'Explorar carteira',
    primaryActionType: 'open_portfolio',
  },
  [CLIENT_STATUS_KEYS.TRIAGEM_EM_ANDAMENTO]: {
    key: CLIENT_STATUS_KEYS.TRIAGEM_EM_ANDAMENTO,
    label: 'Triagem em andamento',
    description:
      'Você já selecionou oportunidades. Gere uma triagem ou avance para o pré-projeto consultivo.',
    tone: 'primary',
    priority: 35,
    primaryActionLabel: 'Gerar relatório de triagem',
    primaryActionType: 'open_triage_report',
  },
  [CLIENT_STATUS_KEYS.PREPROJETO_EM_ELABORACAO]: {
    key: CLIENT_STATUS_KEYS.PREPROJETO_EM_ELABORACAO,
    label: 'Pré-projeto em elaboração',
    description:
      'Há um rascunho em andamento. Resolva pendências antes de apresentar ao cliente.',
    tone: 'primary',
    priority: 30,
    primaryActionLabel: 'Abrir pré-projeto',
    primaryActionType: 'open_preproject',
  },
  [CLIENT_STATUS_KEYS.PRONTO_PARA_CLIENTE]: {
    key: CLIENT_STATUS_KEYS.PRONTO_PARA_CLIENTE,
    label: 'Pronto para cliente',
    description: 'Pré-projeto com boa completude — prepare a apresentação.',
    tone: 'success',
    priority: 10,
    primaryActionLabel: 'Abrir pré-projeto',
    primaryActionType: 'open_preproject',
  },
  [CLIENT_STATUS_KEYS.ACOMPANHAMENTO]: {
    key: CLIENT_STATUS_KEYS.ACOMPANHAMENTO,
    label: 'Em acompanhamento',
    description: 'Há oportunidades acompanhadas — retome a seleção ou o pré-projeto quando fizer sentido.',
    tone: 'neutral',
    priority: 45,
    primaryActionLabel: 'Ver acompanhadas',
    primaryActionType: 'open_tracked',
  },
  [CLIENT_STATUS_KEYS.EM_ANALISE]: {
    key: CLIENT_STATUS_KEYS.EM_ANALISE,
    label: 'Em análise',
    description: 'Explore a carteira e avance na esteira de consultoria.',
    tone: 'neutral',
    priority: 70,
    primaryActionLabel: 'Explorar carteira',
    primaryActionType: 'open_portfolio',
  },
};

export const CLIENT_STATUS_FILTER_OPTIONS = [
  { value: '', label: 'Status (todos)' },
  { value: CLIENT_STATUS_KEYS.PRECISA_BRIEFING, label: 'Precisa briefing' },
  { value: CLIENT_STATUS_KEYS.PERFIL_EM_MONTAGEM, label: 'Perfil em montagem' },
  { value: CLIENT_STATUS_KEYS.CARTEIRA_PRONTA, label: 'Carteira pronta' },
  { value: CLIENT_STATUS_KEYS.TRIAGEM_EM_ANDAMENTO, label: 'Triagem' },
  { value: CLIENT_STATUS_KEYS.PREPROJETO_EM_ELABORACAO, label: 'Pré-projeto' },
  { value: CLIENT_STATUS_KEYS.PRONTO_PARA_CLIENTE, label: 'Pronto' },
  { value: CLIENT_STATUS_KEYS.ACOMPANHAMENTO, label: 'Acompanhamento' },
];

function pickStatus(key) {
  return STATUS_CATALOG[key] || STATUS_CATALOG[CLIENT_STATUS_KEYS.EM_ANALISE];
}

/**
 * Deriva status a partir de sinais já disponíveis (ordem de prioridade).
 * @param {object} input
 */
export function deriveConsultorClientStatus(input = {}) {
  const profileCompleteness = Number(input.profileCompleteness) || 0;
  const hasBriefing = Boolean(input.hasBriefing);
  const topCount = Array.isArray(input.topMatches) ? input.topMatches.length : 0;
  const selCount = Array.isArray(input.selectedOpportunities)
    ? input.selectedOpportunities.length
    : 0;
  const precad = input.precadSummary || null;
  const hadDraft = Boolean(precad?.hadDraft);
  const pendenciesCount = Number(precad?.pendenciesCount) || 0;
  const precadScore = Number(precad?.score) || 0;
  const trackedCount = Array.isArray(input.trackedOpportunities)
    ? input.trackedOpportunities.length
    : Number(input.trackedCount) || 0;

  let key = CLIENT_STATUS_KEYS.EM_ANALISE;

  if (hadDraft && precadScore >= 80 && pendenciesCount <= 2) {
    key = CLIENT_STATUS_KEYS.PRONTO_PARA_CLIENTE;
  } else if (hadDraft && pendenciesCount > 0) {
    key = CLIENT_STATUS_KEYS.PREPROJETO_EM_ELABORACAO;
  } else if (selCount > 0 && !hadDraft) {
    key = CLIENT_STATUS_KEYS.TRIAGEM_EM_ANDAMENTO;
  } else if (topCount > 0 && selCount === 0) {
    key = CLIENT_STATUS_KEYS.CARTEIRA_PRONTA;
  } else if (trackedCount > 0 && selCount === 0) {
    key = CLIENT_STATUS_KEYS.ACOMPANHAMENTO;
  } else if (profileCompleteness < 50 && !hasBriefing) {
    key = CLIENT_STATUS_KEYS.PRECISA_BRIEFING;
  } else if (profileCompleteness < 70) {
    key = CLIENT_STATUS_KEYS.PERFIL_EM_MONTAGEM;
  }

  const status = pickStatus(key);

  if (import.meta.env.DEV && input.logContext) {
    logConsultorWorkspace('client_status_derived', {
      ...input.logContext,
      status_key: status.key,
      profileCompleteness,
      hasBriefing,
      topCount,
      selCount,
      hadDraft,
      pendenciesCount,
      trackedCount,
    });
  }

  return status;
}

/**
 * Versão leve para a lista lateral (sem Radar nem seleção ativa).
 * @param {object|null} cliente
 */
export function deriveConsultorClientStatusLight(cliente) {
  if (!cliente) return pickStatus(CLIENT_STATUS_KEYS.EM_ANALISE);

  const profileCompleteness = calculateClientProfileCompleteness(cliente).score;
  const hasBriefing = hasBriefingContent(cliente);
  const precadSummary = getClientPrecadSummary(cliente, { useSessionContext: false });
  const clienteId = cliente.id_cliente ?? cliente.id;
  const storedTracked = loadStoredTrackedItems(clienteId).length;
  const radarFav = loadRadarFavoritoIdsForCliente(clienteId).size;
  const trackedCount = storedTracked + (radarFav > 0 ? radarFav : 0);

  return deriveConsultorClientStatus({
    profileCompleteness,
    hasBriefing,
    topMatches: [],
    selectedOpportunities: [],
    precadSummary,
    trackedCount,
    logContext: { mode: 'light', id_cliente: clienteId },
  });
}

/** @deprecated Use status.primaryActionType do catálogo */
export function primaryActionHintForStatus(statusKey) {
  return pickStatus(statusKey).primaryActionType ?? null;
}
