import { ENABLE_CONSULTOR_WORKSPACE } from '../../config/env';
import { DASHBOARD_SCOPE_ALL } from './dashboardClassification';
import { buildEditaisUrl, logNavigateToEditaisFilter } from '../editais/editaisQueryFilters';

/**
 * Escopo para query string (/editais?scope=…).
 * @param {string} scopeFilter
 */
function scopeForEditaisLink(scopeFilter) {
  if (
    !scopeFilter ||
    scopeFilter === DASHBOARD_SCOPE_ALL ||
    scopeFilter === 'todos'
  ) {
    return undefined;
  }
  return scopeFilter;
}

/**
 * @param {object} params
 * @returns {Array<object>}
 */
export function buildDashboardPriorities({
  metrics = {},
  expiringEditais = [],
  pendingReports = 0,
  radarSummary = {},
  canViewCadastros = false,
  scopeFilter = DASHBOARD_SCOPE_ALL,
} = {}) {
  const items = [];
  const scopeParam = scopeForEditaisLink(scopeFilter);

  if (metrics.expiringSoon > 0) {
    const n = metrics.expiringSoon;
    const nav = { prazo: 'vencendo_7', scope: scopeParam };
    logNavigateToEditaisFilter(nav);
    items.push({
      id: 'expiring',
      title: `${n} edital${n !== 1 ? 's' : ''} vence${n === 1 ? '' : 'm'} nos próximos 7 dias`,
      description: 'Priorize revisão de prazos e documentação antes do encerramento.',
      badge: 'Atenção',
      badgeVariant: 'warn',
      to: buildEditaisUrl(nav),
      ctaLabel: 'Ver editais vencendo',
    });
  }

  const openCount =
    metrics.oportunidadesProvavelmenteAbertas ?? metrics.openEditais ?? 0;
  if (openCount > 0) {
    const n = openCount;
    const hq = metrics.highQualityOpen || 0;
    const sem = metrics.semPrazoEstruturado ?? metrics.semPrazo ?? 0;
    items.push({
      id: 'open',
      title: `${n} oportunidade${n !== 1 ? 's' : ''} ativa${n !== 1 ? 's' : ''} ou provável${n !== 1 ? 'eis' : ''}`,
      description:
        hq > 0
          ? `${hq} com indicador de alta qualidade. ${sem > 0 ? `${sem} sem prazo estruturado (fora desta contagem).` : ''}`
          : sem > 0
            ? `${sem} registro${sem !== 1 ? 's' : ''} sem prazo estruturado — confira na listagem.`
            : 'Explore a listagem completa com filtros e favoritos.',
      badge: 'Operação',
      badgeVariant: 'info',
      to: buildEditaisUrl({ scope: scopeParam }),
      ctaLabel: 'Abrir editais',
    });
  }

  if (pendingReports > 0) {
    items.push({
      id: 'reports',
      title: `${pendingReports} relato${pendingReports !== 1 ? 's' : ''} pendente${pendingReports !== 1 ? 's' : ''}`,
      description: 'Itens na fila local aguardando envio ao suporte.',
      badge: 'Sistema',
      badgeVariant: 'neutral',
      to: null,
      ctaLabel: 'Reportar ou revisar',
      action: 'feedback',
    });
  }

  if (ENABLE_CONSULTOR_WORKSPACE && canViewCadastros) {
    const total = radarSummary.total || 0;
    if (total > 0) {
      items.push({
        id: 'radar',
        title: `${total} cliente${total !== 1 ? 's' : ''} no Radar`,
        description:
          radarSummary.withBriefing > 0
            ? `${radarSummary.withBriefing} com briefing/perfil consultivo salvo.`
            : 'Complete perfis para melhorar a triagem de oportunidades.',
        badge: 'Radar',
        badgeVariant: 'info',
        to: '/radar-fomento',
        ctaLabel: 'Abrir Radar',
      });
    } else {
      items.push({
        id: 'radar-empty',
        title: 'Radar sem clientes',
        description: 'Cadastre um cliente para comparar oportunidades por perfil.',
        badge: 'Radar',
        badgeVariant: 'neutral',
        to: '/cadastros',
        ctaLabel: 'Cadastrar cliente',
      });
    }
  }

  if (expiringEditais.length > 0 && !items.some((i) => i.id === 'expiring')) {
    const first = expiringEditais[0];
    const title =
      first.titulo || first.title || 'Edital com prazo próximo';
    items.unshift({
      id: 'next-deadline',
      title: `Próximo: ${title.slice(0, 48)}${title.length > 48 ? '…' : ''}`,
      description: 'Confira a lista “Vencendo em breve” abaixo.',
      badge: 'Hoje',
      badgeVariant: 'warn',
      to: first.id_edital || first.id ? `/edital/${first.id_edital || first.id}` : '/editais',
      ctaLabel: 'Abrir edital',
    });
  }

  return items.slice(0, 4);
}
