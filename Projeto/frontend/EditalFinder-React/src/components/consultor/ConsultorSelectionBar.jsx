import { MAX_PREPROJECT_OPPORTUNITIES } from '../../utils/consultor/opportunitySelection';

function tituloCurto(t, max = 56) {
  const s = String(t || '').trim();
  if (!s) return '—';
  return s.length > max ? `${s.slice(0, max)}…` : s;
}

/**
 * Barra de seleção compartilhada (painel + modal).
 * @param {{ variant?: 'default'|'compact'|'sticky' }} props
 */
export default function ConsultorSelectionBar({
  selectedCount = 0,
  selectionBarSummary = null,
  onGerarPreProjetoSelecionados,
  onGerarRelatorioTriagem,
  onClearOpportunitySelection,
  variant = 'default',
}) {
  if (selectedCount <= 0) return null;

  const summary = selectionBarSummary;
  const compact = variant === 'compact' || variant === 'sticky';
  const metaParts = [];

  if (summary?.primaryTitulo) {
    metaParts.push(`Principal: ${tituloCurto(summary.primaryTitulo, 48)}`);
  }
  if (summary?.semPrazo > 0) {
    metaParts.push(`Sem prazo: ${summary.semPrazo}`);
  }
  if (summary?.closestPrazoLabel) {
    metaParts.push(`Prazo mais próximo: ${summary.closestPrazoLabel}`);
  } else if (summary?.closestDays != null) {
    const prazoTxt = summary.closestDays === 0 ? 'hoje' : `${summary.closestDays}d`;
    metaParts.push(`Prazo mais próximo: ${prazoTxt}`);
  }

  return (
    <div
      className={`consultor-selection-bar consultor-selection-bar--${variant}`}
      role="region"
      aria-label="Oportunidades selecionadas"
    >
      <div className="consultor-selection-bar-inner">
        <div className="consultor-selection-bar-copy">
          <p className="consultor-selection-bar-line1">
            Selecionadas: <strong>{selectedCount}</strong> / {MAX_PREPROJECT_OPPORTUNITIES}
          </p>
          {metaParts.length > 0 ? (
            <p className="consultor-selection-bar-line2">{metaParts.join(' · ')}</p>
          ) : null}
          {!compact && selectedCount > 1 ? (
            <p className="consultor-selection-bar-hint">
              Maior compatibilidade = principal no pré-projeto.
            </p>
          ) : null}
        </div>
        <div className="consultor-selection-bar-actions">
          {onGerarRelatorioTriagem ? (
            <button type="button" className="btn-detalhes dash-action-outline" onClick={onGerarRelatorioTriagem}>
              Relatório de triagem
            </button>
          ) : null}
          <button type="button" className="btn-view" onClick={onGerarPreProjetoSelecionados}>
            Gerar pré-projeto consultivo
          </button>
          <button type="button" className="btn-detalhes dash-action-outline" onClick={onClearOpportunitySelection}>
            Limpar
          </button>
        </div>
      </div>
    </div>
  );
}

export { MAX_PREPROJECT_OPPORTUNITIES };
