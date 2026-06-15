import { useState } from 'react';
import AppReportProblemButton from '../feedback/AppReportProblemButton';
import { buildManualEditalReportContext } from '../../utils/admin/handleManualEditalSaveError.js';

/**
 * Painel de erro estruturado para cadastro manual de edital (FRONTEND 1.1F).
 */
export default function EditalSaveErrorPanel({
  saveError,
  pendingDraftsCount = 0,
  onDismiss,
  onCopyData,
  copyStatus = null,
}) {
  const [showTechnical, setShowTechnical] = useState(false);

  if (!saveError) return null;

  const reportContext = buildManualEditalReportContext(saveError);
  const details = saveError.safeDetails || {};

  return (
    <div
      className="login-alert login-alert--error edital-save-error-panel"
      role="alert"
      data-testid="edital-save-error-panel"
    >
      <strong data-testid="edital-save-error-title">{saveError.title}</strong>
      <p data-testid="edital-save-error-message">{saveError.message}</p>

      {pendingDraftsCount > 0 ? (
        <p className="edital-save-error-draft-hint" data-testid="edital-save-pending-count">
          Rascunhos locais pendentes: {pendingDraftsCount}
          {saveError.localDraftId ? ` (último: ${saveError.localDraftId})` : ''}
        </p>
      ) : null}

      <div className="edital-save-error-actions">
        <button type="button" className="cad-btn-text" onClick={onDismiss}>
          Tentar novamente
        </button>
        {onCopyData ? (
          <button type="button" className="cad-btn-text" onClick={onCopyData}>
            Copiar dados
          </button>
        ) : null}
        <AppReportProblemButton
          origem={reportContext.origem}
          pagina="cadastros"
          componente="Cadastros"
          acao="submit"
          tipo="cadastro"
          error={reportContext.error}
          extraContext={reportContext.extraContext}
          label="Reportar problema"
          variant="link"
          className="cad-btn-text"
        />
      </div>

      {copyStatus ? (
        <p className="edital-save-error-copy-status" role="status">
          {copyStatus}
        </p>
      ) : null}

      <button
        type="button"
        className="edital-save-error-tech-toggle"
        onClick={() => setShowTechnical((v) => !v)}
        aria-expanded={showTechnical}
      >
        {showTechnical ? 'Ocultar detalhe técnico' : 'Ver detalhe técnico'}
      </button>

      {showTechnical ? (
        <pre className="edital-save-error-tech" data-testid="edital-save-error-tech">
          {`Erro classificado: ${saveError.errorKind}\nCódigo: ${details.code || '—'}\nStatus: ${details.status ?? '—'}\nMensagem: ${details.message || '—'}`}
        </pre>
      ) : null}
    </div>
  );
}
