/**
 * Faixa superior do pré-cadastro: esquerda = título + meta + badges; direita = ações (Fechar + PDF + rascunho).
 */

export default function PrecadastroHeader({
  empresaNome,
  clientId,
  editalTitulo,
  aderenciaLabel,
  completudePct,
  pendencias,
  statusLabel,
  logoUrl,
  onSaveDraft,
  onExportPdf,
  onPreviewPdf,
  onClose,
}) {
  return (
    <header className="precad-header-prof">
      {logoUrl ? (
        <div className="precad-header-logo">
          <img src={logoUrl} alt="" className="precad-header-logo-img" />
        </div>
      ) : null}
      <div className="precad-header-titles">
        <h2 className="precad-header-h2">Pré-cadastro de projeto</h2>
        <p className="precad-header-meta">
          <span className="precad-header-empresa">{empresaNome}</span>
          {typeof clientId !== 'undefined' ? <span className="precad-header-id">· ID {clientId}</span> : null}
        </p>
        <div className="precad-header-chips">
          {editalTitulo ? (
            <span className="precad-chip precad-chip-edital" title="Edital de referência">
              Edital: {editalTitulo.length > 72 ? `${editalTitulo.slice(0, 72)}…` : editalTitulo}
            </span>
          ) : (
            <span className="precad-chip precad-chip-muted">Sem edital vinculado — fluxo genérico</span>
          )}
          {aderenciaLabel ? (
            <span className="precad-chip precad-chip-fit">Aderência: {aderenciaLabel}</span>
          ) : null}
          {statusLabel ? <span className="precad-chip precad-chip-status">{statusLabel}</span> : null}
          {typeof completudePct === 'number' ? (
            <span className="precad-chip precad-chip-fit" title="Completude calculada pelo assistente">
              Completude: {completudePct}%
            </span>
          ) : null}
          {pendencias ? (
            <span className="precad-chip precad-chip-muted" title="Lista detalhada na aba Visão geral">
              Pendências: {pendencias.obrigatorias} obrig. · {pendencias.recomendadas} rec.
            </span>
          ) : null}
        </div>
      </div>
      <div className="precad-header-actions" role="toolbar" aria-label="Ações do pré-cadastro">
        <button type="button" className="precad-btn precad-btn-ghost precad-header-btn-fechar" onClick={onClose}>
          Fechar
        </button>
        {onPreviewPdf ? (
          <button type="button" className="precad-btn precad-btn-secondary" onClick={onPreviewPdf}>
            Pré-visualizar PDF
          </button>
        ) : null}
        <button type="button" className="precad-btn precad-btn-primary" onClick={onSaveDraft}>
          Salvar rascunho
        </button>
        <button type="button" className="precad-btn precad-btn-outline" onClick={onExportPdf}>
          Baixar PDF
        </button>
      </div>
    </header>
  );
}
