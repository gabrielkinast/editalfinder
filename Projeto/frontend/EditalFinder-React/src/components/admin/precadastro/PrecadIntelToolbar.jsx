/**
 * Botões do assistente: gerar lacunas / regeneração / limpar sugestões automáticas.
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
      <p className="precad-muted small precad-intel-lead">
        Use as ações abaixo para gerar sugestões locais (sem API externa). Campos que você editou manualmente não são
        sobrescritos sem confirmação.
      </p>
      <div className="precad-intel-actions">
        <button type="button" className="precad-btn precad-btn-secondary" onClick={onSmartDraft}>
          Gerar rascunho inteligente
        </button>
        <button type="button" className="precad-btn precad-btn-secondary" onClick={onFillLacunas}>
          Preencher lacunas (sugerido)
        </button>
        <button type="button" className="precad-btn precad-btn-secondary" onClick={onLimparAutos}>
          Limpar apenas sugestões automáticas
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
