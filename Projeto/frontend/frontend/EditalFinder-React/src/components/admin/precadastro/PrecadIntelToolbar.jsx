/**
 * Painel compacto do assistente de preenchimento (sugestões locais).
 */

export default function PrecadIntelToolbar({
  onSmartDraft,
  onFillLacunas,
  onLimparAutos,
  onRevisarPendencias,
  onScrollProject,
}) {
  return (
    <section className="precad-intel-toolbar" aria-label="Assistente de preenchimento">
      <h3 className="precad-assistente-titulo">Assistente de preenchimento</h3>
      <p className="precad-muted small precad-intel-lead">
        Sugestões locais no navegador. Alterações manuais não são sobrescritas sem confirmação no “Gerar rascunho
        inteligente”.
      </p>
      <div className="precad-intel-actions">
        <button type="button" className="precad-btn precad-btn-secondary" onClick={onSmartDraft}>
          Gerar rascunho inteligente
        </button>
        <button type="button" className="precad-btn precad-btn-secondary" onClick={onFillLacunas}>
          Preencher lacunas
        </button>
        <button type="button" className="precad-btn precad-btn-secondary" onClick={onLimparAutos}>
          Limpar sugestões
        </button>
        <button type="button" className="precad-btn precad-btn-ghost" onClick={onRevisarPendencias}>
          Revisar pendências
        </button>
        <button type="button" className="precad-btn precad-btn-ghost" onClick={onScrollProject}>
          Ir ao projeto / escopo
        </button>
      </div>
    </section>
  );
}
