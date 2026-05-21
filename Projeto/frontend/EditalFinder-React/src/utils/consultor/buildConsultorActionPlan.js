function hasText(v) {
  return v != null && String(v).trim() !== '';
}

const PRIORITY_ORDER = { alta: 0, media: 1, baixa: 2 };

/**
 * @param {object|null} cliente
 */
export function clienteMissingEssentialFields(cliente) {
  if (!cliente) return { hasMissing: false, labels: [] };
  const contato = cliente.contatoPrincipal || {};
  const tec = cliente.perfilTecnologico || {};
  const labels = [];
  if (!hasText(contato.email)) labels.push('e-mail');
  if (!hasText(contato.nome)) labels.push('responsável');
  if (!hasText(cliente.cidade) || !hasText(cliente.estado)) labels.push('cidade/estado');
  if (
    !hasText(tec.areas_tecnologicas) &&
    !hasText(cliente.area_inovacao) &&
    !hasText(tec.temas_prioritarios)
  ) {
    labels.push('áreas tecnológicas');
  }
  return { hasMissing: labels.length > 0, labels };
}

/**
 * @typedef {'open_briefing'|'open_client_form'|'open_portfolio'|'open_triage_report'|'open_preproject'} ActionType
 */

/**
 * @param {object} input
 * @param {object|null} [input.cliente]
 * @param {number} [input.profileCompleteness]
 * @param {boolean} [input.hasBriefing]
 * @param {Array} [input.selectedOpportunities]
 * @param {Array} [input.topMatches]
 * @param {object|null} [input.precadSummary]
 * @param {object|null} [input.deadlineSummary]
 * @returns {Array<{
 *   id: string,
 *   title: string,
 *   description?: string,
 *   priority: 'alta'|'media'|'baixa',
 *   status: 'pendente'|'em_andamento'|'concluida',
 *   actionLabel: string,
 *   actionType: ActionType,
 *   reopenKey: string
 * }>}
 */
export function buildConsultorActionPlan(input = {}) {
  const {
    cliente = null,
    profileCompleteness = 0,
    hasBriefing = false,
    selectedOpportunities = [],
    topMatches = [],
    precadSummary = null,
    deadlineSummary = null,
  } = input;

  const selectedCount = Array.isArray(selectedOpportunities) ? selectedOpportunities.length : 0;
  const topCount = Array.isArray(topMatches) ? topMatches.length : 0;
  const hadDraft = Boolean(precadSummary?.hadDraft);
  const pendenciesCount = precadSummary?.pendenciesCount ?? 0;
  const venceAte7 = deadlineSummary?.venceAte7 ?? 0;

  const actions = [];

  if (profileCompleteness < 70 && !hasBriefing) {
    actions.push({
      id: 'complete_briefing',
      title: 'Completar briefing do cliente',
      description:
        'O perfil incompleto reduz a qualidade da carteira, triagem e pré-projeto.',
      priority: 'alta',
      status: 'pendente',
      actionLabel: 'Fazer briefing',
      actionType: 'open_briefing',
      reopenKey: `briefing:p${profileCompleteness}:b0`,
    });
  }

  const essentials = clienteMissingEssentialFields(cliente);
  if (essentials.hasMissing) {
    actions.push({
      id: 'complete_essential_data',
      title: 'Completar dados essenciais do cliente',
      description: `Faltam: ${essentials.labels.join(', ')}.`,
      priority: 'media',
      status: 'pendente',
      actionLabel: 'Completar cadastro',
      actionType: 'open_client_form',
      reopenKey: `ess:${essentials.labels.join('|')}`,
    });
  }

  if (topCount > 0 && selectedCount === 0) {
    actions.push({
      id: 'select_opportunities',
      title: 'Selecionar oportunidades para triagem',
      description: 'Escolha até 20 oportunidades para montar uma estratégia de fomento.',
      priority: 'alta',
      status: 'pendente',
      actionLabel: 'Explorar carteira',
      actionType: 'open_portfolio',
      reopenKey: `sel:top${topCount}:n0`,
    });
  }

  if (selectedCount > 0) {
    actions.push({
      id: 'generate_triage_report',
      title: 'Gerar relatório de triagem',
      description: 'Revise a seleção antes de transformar em pré-projeto.',
      priority: 'media',
      status: 'pendente',
      actionLabel: 'Gerar triagem',
      actionType: 'open_triage_report',
      reopenKey: `triage:sel${selectedCount}`,
    });
  }

  if (selectedCount > 0 && !hadDraft) {
    actions.push({
      id: 'generate_preproject',
      title: 'Gerar pré-projeto consultivo',
      description: 'Monte o rascunho a partir das oportunidades selecionadas.',
      priority: 'alta',
      status: 'pendente',
      actionLabel: 'Gerar pré-projeto',
      actionType: 'open_preproject',
      reopenKey: `preproject:sel${selectedCount}:draft0`,
    });
  }

  if (hadDraft && pendenciesCount > 0) {
    actions.push({
      id: 'resolve_preproject_pendencies',
      title: 'Resolver pendências do pré-projeto',
      description: 'Há campos importantes antes de apresentar ao cliente.',
      priority: 'alta',
      status: 'pendente',
      actionLabel: 'Abrir pré-projeto',
      actionType: 'open_preproject',
      reopenKey: `pend:${pendenciesCount}:fp${precadSummary?.editalFingerprint || 'geral'}`,
    });
  }

  if (venceAte7 > 0) {
    actions.push({
      id: 'validate_short_deadlines',
      title: 'Validar oportunidades com prazo curto',
      description: 'Há oportunidades vencendo em até 7 dias.',
      priority: 'alta',
      status: 'pendente',
      actionLabel: 'Ver carteira',
      actionType: 'open_portfolio',
      reopenKey: `deadline7:${venceAte7}`,
    });
  }

  const advancedReady =
    profileCompleteness >= 70 &&
    selectedCount > 0 &&
    hadDraft &&
    pendenciesCount <= 2;

  if (advancedReady) {
    actions.push({
      id: 'prepare_client_presentation',
      title: 'Preparar apresentação ao cliente',
      description: 'Revise o pré-projeto e a seleção antes da reunião.',
      priority: 'baixa',
      status: 'pendente',
      actionLabel: 'Abrir pré-projeto',
      actionType: 'open_preproject',
      reopenKey: `present:p${profileCompleteness}:s${selectedCount}:pend${pendenciesCount}`,
    });
  }

  actions.sort((a, b) => {
    const pa = PRIORITY_ORDER[a.priority] ?? 9;
    const pb = PRIORITY_ORDER[b.priority] ?? 9;
    if (pa !== pb) return pa - pb;
    return a.id.localeCompare(b.id);
  });

  return actions;
}
