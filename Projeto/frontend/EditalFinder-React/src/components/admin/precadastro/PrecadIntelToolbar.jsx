/**
 * Assistente de preenchimento — modo compacto e recolhível.
 */

export default function PrecadIntelToolbar({
  defaultOpen = false,
  onSmartDraft,
  onFillLacunas,
  onLimparAutos,
  onRevisarPendencias,
  onScrollProject,
}) {
  return (
    <details className="precad-intel-toolbar precad-intel-toolbar--compact" open={defaultOpen}>
      <summary className="precad-intel-summary">
        <span className="precad-intel-summary-title">Assistente</span>
        <span className="precad-intel-summary-hint">Sugestões locais. Revise antes de salvar.</span>
      </summary>
      <div className="precad-intel-body">
        <div className="precad-intel-actions precad-intel-actions--primary">
          <button type="button" className="precad-btn precad-btn-secondary precad-btn-sm" onClick={onSmartDraft}>
            Gerar sugestões
          </button>
          <button type="button" className="precad-btn precad-btn-secondary precad-btn-sm" onClick={onFillLacunas}>
            Preencher lacunas
          </button>
          <button type="button" className="precad-btn precad-btn-ghost precad-btn-sm" onClick={onRevisarPendencias}>
            Revisar pendências
          </button>
        </div>
        <details className="precad-intel-more">
          <summary>Mais ações</summary>
          <div className="precad-intel-actions">
            <button type="button" className="precad-btn precad-btn-ghost precad-btn-sm" onClick={onLimparAutos}>
              Limpar sugestões
            </button>
            <button type="button" className="precad-btn precad-btn-ghost precad-btn-sm" onClick={onScrollProject}>
              Ir ao projeto / escopo
            </button>
          </div>
        </details>
        <p className="precad-intel-footnote precad-muted small">
          Origem das sugestões aparece nos campos da aba Contexto com badges.
        </p>
      </div>
    </details>
  );
}
