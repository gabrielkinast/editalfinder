import { calculateClientProfileCompleteness } from '../cliente/calculateClientProfileCompleteness';
import { getDeadlineAlertStatus, parsePrazoEnvio } from '../deadlineAlerts';
import { rowDisplayFields } from './consultorOpportunityRowDisplay';
import { resolveAnalyzedOpportunityCount } from './resolveAnalyzedOpportunityCount';
import {
  pickPrimaryOpportunity,
  partitionSelectedOpportunities,
} from './opportunitySelection';

const PROXIMOS_PASSOS = [
  'Confirmar interesse do cliente nas oportunidades priorizadas.',
  'Revisar regulamentos e editais das chamadas selecionadas.',
  'Reunir documentos e certidões exigidas pelo perfil do cliente.',
  'Escolher e validar a oportunidade principal com o cliente.',
  'Gerar pré-projeto consultivo a partir da seleção.',
];

const RECOMMENDATION_GROUPS = [
  { id: 'priorizar_agora', label: 'Priorizar agora' },
  { id: 'validar_cliente', label: 'Validar com o cliente' },
  { id: 'acompanhar', label: 'Acompanhar' },
  { id: 'descartar_revisar', label: 'Descartar / revisar' },
];

/**
 * Classifica uma oportunidade selecionada para o relatório de triagem.
 * @param {ReturnType<import('./opportunitySelection').normalizeSelectedOpportunity>} opp
 * @param {boolean} isPrimary
 */
const PRAZO_CURTO = ['vence_hoje', 'vence_3_dias', 'vence_7_dias'];

function opportunityHasIncompleteData(opp) {
  const ed = opp?.row?.edital || opp?.edital || {};
  const d = rowDisplayFields(opp?.row);
  if (ed.dados_incompletos || opp?.row?.dados_incompletos) return true;
  if (!d.link || d.link === '—') return true;
  if (!d.fonte || d.fonte === '—') return true;
  return false;
}

function categorizeOpportunity(opp, isPrimary) {
  const ed = opp?.row?.edital || opp?.edital || {};
  const status = getDeadlineAlertStatus(ed);
  const score = Number(opp?.scorePct) || 0;
  const compat = String(opp?.compatibilidade || 'Baixa');
  const prazoCurto = PRAZO_CURTO.includes(status);
  const semPrazo = !parsePrazoEnvio(ed) || status === 'prazo_indefinido';
  const aderenciaMedia =
    compat === 'Média' || compat === 'Media' || (score >= 42 && score < 58);

  if (status === 'encerrado') return 'descartar_revisar';

  if (isPrimary || score >= 66 || (prazoCurto && score >= 48)) {
    return 'priorizar_agora';
  }

  if (semPrazo || opportunityHasIncompleteData(opp) || aderenciaMedia) {
    return 'validar_cliente';
  }

  if (
    ['prazo_confortavel', 'vence_15_dias'].includes(status) ||
    (!prazoCurto && score >= 44 && compat !== 'Baixa')
  ) {
    return 'acompanhar';
  }

  if (compat === 'Baixa' && score < 40) return 'descartar_revisar';
  return 'validar_cliente';
}

/**
 * @param {ReturnType<import('./opportunitySelection').normalizeSelectedOpportunity>[]} opportunities
 * @param {ReturnType<import('./opportunitySelection').normalizeSelectedOpportunity>|null} primary
 */
export function buildTriageRecommendations(opportunities, primary) {
  const buckets = {
    priorizar_agora: [],
    validar_cliente: [],
    acompanhar: [],
    descartar_revisar: [],
  };

  for (const opp of opportunities || []) {
    const key = categorizeOpportunity(opp, primary?.key === opp.key);
    buckets[key].push({
      key: opp.key,
      titulo: opp.titulo,
      scorePct: opp.scorePct,
      compatibilidade: opp.compatibilidade,
      prazoLabel: rowDisplayFields(opp.row).prazoLabel,
    });
  }

  return RECOMMENDATION_GROUPS.map((g) => ({
    ...g,
    items: buckets[g.id] || [],
  })).filter((g) => g.items.length > 0);
}

/**
 * Monta o modelo do relatório de triagem (somente dados já disponíveis no Workspace).
 * @param {object} params
 * @param {object} params.cliente
 * @param {number} [params.totalMatches]
 * @param {object[]} [params.allMatches] — fallback para total analisado
 * @param {ReturnType<import('./opportunitySelection').normalizeSelectedOpportunity>[]} params.selectedOpportunities
 * @param {object} [params.deadlineSummary] — resumo global da carteira (opcional)
 */
export function buildTriageReportModel({
  cliente,
  totalMatches = 0,
  allMatches = [],
  selectedOpportunities = [],
  deadlineSummary = null,
}) {
  const completeness = cliente ? calculateClientProfileCompleteness(cliente) : { score: 0, level: 'inicial' };
  const primary = pickPrimaryOpportunity(selectedOpportunities);
  const part = partitionSelectedOpportunities(selectedOpportunities, primary);

  let venceCritico = 0;
  let semPrazoSel = 0;
  let prazoConfortavelSel = 0;

  const tableRows = (selectedOpportunities || []).map((opp) => {
    const d = rowDisplayFields(opp.row);
    const ed = opp.row?.edital || {};
    const prazoStatus = getDeadlineAlertStatus(ed);
    if (PRAZO_CURTO.includes(prazoStatus)) venceCritico += 1;
    if (!parsePrazoEnvio(ed) || prazoStatus === 'prazo_indefinido') semPrazoSel += 1;
    if (prazoStatus === 'prazo_confortavel' || prazoStatus === 'vence_15_dias') {
      prazoConfortavelSel += 1;
    }

    return {
      key: opp.key,
      titulo: d.titulo,
      fonte: d.fonte,
      prazo: d.prazoLabel,
      tipoApoio: d.tipoApoio,
      compatibilidade: d.compatibilidade,
      scorePct: d.score,
      observacao: d.observacoes,
      link: d.link,
      isPrimary: primary?.key === opp.key,
    };
  });

  const segmento = [cliente?.porte_empresa, cliente?.setor, cliente?.estado, cliente?.regiao]
    .filter(Boolean)
    .join(' · ');

  const nomeCliente = cliente?.nome_empresa || cliente?.razao_social || '—';
  const totalAnalisado = resolveAnalyzedOpportunityCount({ totalMatches, allMatches });
  const selecionadas = selectedOpportunities.length;
  const semPrazo = semPrazoSel;
  const prazoConfortavel = prazoConfortavelSel;
  const venceCriticoFinal = venceCritico;

  const carteiraResumoParts = [
    `${totalAnalisado} oportunidades analisadas`,
    `${selecionadas} selecionadas`,
    `${semPrazo} sem prazo informado`,
    `${prazoConfortavel} com prazo confortável`,
  ];

  const aberturaExecutiva = `Este relatório apresenta uma triagem preliminar de oportunidades de fomento para ${nomeCliente}, com ${selecionadas} oportunidade${selecionadas === 1 ? '' : 's'} selecionada${selecionadas === 1 ? '' : 's'} para validação. A recomendação principal foi definida pela maior compatibilidade do Radar, mas deve ser confirmada pelo consultor antes de qualquer submissão.`;

  return {
    cliente: {
      nome: nomeCliente,
      razaoSocial: cliente?.razao_social || '',
      segmento: segmento || '—',
      completudePct: completeness.score,
      completudeLevel: completeness.level,
    },
    aberturaExecutiva,
    carteira: {
      totalAnalisado,
      selecionadas,
      principalTitulo: primary?.titulo || null,
      principalScore: primary?.scorePct ?? null,
      venceCritico: venceCriticoFinal,
      semPrazo,
      prazoConfortavel,
      resumoLinha: carteiraResumoParts.join(' · '),
      complementares: part.complementares.length,
      emObservacao: part.observacao.length,
    },
    tableRows: tableRows.sort((a, b) => {
      if (a.isPrimary !== b.isPrimary) return a.isPrimary ? -1 : 1;
      return (b.scorePct || 0) - (a.scorePct || 0);
    }),
    recommendations: buildTriageRecommendations(selectedOpportunities, primary),
    proximosPassos: PROXIMOS_PASSOS,
    generatedAt: new Date().toISOString(),
  };
}
