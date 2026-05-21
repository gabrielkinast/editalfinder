import { buildPortfolioTriageSummary } from '../../utils/consultor/portfolioTriageSummary';

/**
 * Resumo consultivo de triagem — linha horizontal compacta.
 */
export default function ConsultorPortfolioSummary({
  totalMatches = 0,
  quickViewCount = 20,
  selectedCount = 0,
  selectionBarSummary = null,
  deadlineSummary = null,
  principalTitulo = null,
  filteredCount = null,
}) {
  const s = buildPortfolioTriageSummary({
    totalMatches,
    quickViewCount,
    selectedCount,
    selectionBarSummary,
    deadlineSummary,
    topMatchTitulo: principalTitulo,
  });

  const parts = [
    `${s.totalMatches} analisadas`,
    `${s.quickViewCount} na visão rápida`,
    `${s.selectedCount} selecionadas`,
  ];

  if (filteredCount != null && filteredCount !== s.totalMatches) {
    parts.push(`${filteredCount} após filtros`);
  }
  if (s.semPrazo > 0) parts.push(`${s.semPrazo} sem prazo`);
  if (s.venceAte7 > 0) {
    parts.push(`${s.venceAte7} vence${s.venceAte7 === 1 ? '' : 'm'} em 7 dias`);
  }

  return (
    <section className="consultor-portfolio-summary consultor-portfolio-summary--inline" aria-label="Triagem deste cliente">
      <p className="consultor-portfolio-summary-line">
        <span className="consultor-portfolio-summary-label">Triagem:</span>
        {parts.join(' · ')}
      </p>
      {s.principalTitulo ? (
        <p className="consultor-portfolio-summary-principal">
          Principal sugerida: <span className="consultor-portfolio-summary-em">{s.principalTitulo}</span>
        </p>
      ) : null}
    </section>
  );
}
