/**
 * Semântica dos contadores do Dashboard (FRONTEND 1.1H).
 *
 * Evita confundir:
 * - catálogo recebido (total carregado do banco/view, ex.: 1051);
 * - subconjunto priorizado/escopado do Dashboard (ex.: 437);
 * - oportunidades com prazo confirmado.
 *
 * Funções puras (sem React) para serem testáveis em Node.
 */

/** Texto de ajuda padrão do Dashboard sobre a diferença entre catálogo e subconjunto. */
export const DASHBOARD_COUNT_HELP_TEXT =
  'O Dashboard mostra um subconjunto priorizado dos editais. Para ver o catálogo completo, ' +
  'acesse a tela de Editais, que indica quantos registros foram recebidos do banco e quantos ' +
  'permanecem visíveis após os filtros.';

/** Rótulo do card principal — "priorizados" deixa claro que não é o total bruto. */
export const DASHBOARD_MONITORED_LABEL = 'Editais priorizados';

export function formatCount(n) {
  return Number(n ?? 0).toLocaleString('pt-BR');
}

/**
 * Constrói os textos de contexto dos cards do Dashboard, incluindo a referência
 * ao total recebido no catálogo quando disponível.
 *
 * @param {Record<string, number>} [metrics]
 * @param {{ truncated?: boolean }} [opts]
 */
export function buildDashboardCountContexts(metrics = {}, opts = {}) {
  const truncated = Boolean(opts.truncated);
  const truncNote = truncated ? ' (amostra da base)' : '';

  const sem = metrics.semPrazoEstruturado ?? metrics.semPrazo ?? 0;
  const confirmados = metrics.prazoConfirmado ?? 0;
  const monitored = metrics.totalEditais ?? 0;
  const catalog = metrics.catalogEditais;

  const hasCatalog = catalog != null && Number.isFinite(Number(catalog));
  const catalogDiffersFromMonitored = hasCatalog && Number(catalog) !== Number(monitored);

  // Subtexto do card principal: sempre comunica que é subconjunto; cita o catálogo
  // recebido quando conhecido.
  const monitoredParts = [];
  if (hasCatalog) {
    monitoredParts.push(
      catalogDiffersFromMonitored
        ? `De ${formatCount(catalog)} recebidos no catálogo`
        : `${formatCount(catalog)} recebidos no catálogo`,
    );
  }
  monitoredParts.push(`subconjunto priorizado do Dashboard${truncNote}`);
  if (confirmados > 0) {
    monitoredParts.push(`${formatCount(confirmados)} com prazo confirmado`);
  }

  return {
    monitoredLabel: DASHBOARD_MONITORED_LABEL,
    /** Card principal "Editais priorizados". */
    monitored: monitoredParts.join(' · '),
    /** Mantido por compatibilidade com chamadas existentes. */
    total: `${formatCount(confirmados)} com prazo confirmado${truncNote}`,
    open: `Com prazo futuro válido · ${formatCount(sem)} sem prazo estruturado`,
    expiring:
      (metrics.expiringSoon ?? 0) > 0
        ? 'Requer atenção imediata'
        : (metrics.expiring30 ?? 0) > 0
          ? `${formatCount(metrics.expiring30)} vencem em até 30 dias`
          : 'Nenhum prazo crítico em 7 dias',
    noticias: 'Últimos 30 dias · filtro Brasil/Internacional abaixo',
    pesquisas: 'Últimos 30 dias · filtro Brasil/Internacional abaixo',
    reports:
      (metrics.reportedProblemsPending ?? 0) > 0
        ? 'Na fila local de envio'
        : 'Fila local em dia',
  };
}
