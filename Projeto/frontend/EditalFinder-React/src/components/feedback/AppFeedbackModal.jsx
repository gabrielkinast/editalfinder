import { useEffect, useId, useMemo, useRef, useState } from 'react';
import Modal from '../ui/Modal';
import {
  APP_FEEDBACK_COMMENT_MAX,
  APP_FEEDBACK_COMMENT_MIN,
  APP_FEEDBACK_PROBLEM_TYPES,
  APP_FEEDBACK_SEVERITY_LEVELS,
  DEFAULT_APP_FEEDBACK_SEVERITY_VALUE,
  MSG_APP_FEEDBACK_FAILED,
  MSG_APP_FEEDBACK_FALLBACK_BODY,
  MSG_APP_FEEDBACK_FALLBACK_TITLE,
  MSG_APP_FEEDBACK_MODAL_HINT,
  MSG_APP_FEEDBACK_SUCCESS_GMAIL,
  MSG_APP_FEEDBACK_SUCCESS_MAILTO,
  MSG_APP_FEEDBACK_VALIDATION,
} from '../../constants/appFeedbackConfig';
import {
  getFeedbackProblemType,
  mapContextToDefaultTipo,
} from '../../utils/feedback/appFeedbackTaxonomy';
import { DEFAULT_APP_FEEDBACK_TYPE_VALUE } from '../../constants/appFeedbackConfig';
import { getFeedbackSeverity } from '../../utils/feedback/appFeedbackSeverity';
import {
  buildManualSupportInstructions,
  copyTextToClipboard,
} from '../../utils/feedback/appFeedbackClipboard';
import { SUPPORT_EMAIL } from '../../utils/feedback/appFeedbackMailto';
import { getRuntimeContext, getRuntimeDisplayLabel } from '../../utils/feedback/runtimeContext';
import { getReportProblemGuidanceText } from '../../utils/feedback/appFeedbackGuidance';

function ContextSummary({ context }) {
  const p = context?.payload;
  if (!p && !context?.error) {
    return <p className="app-feedback-muted">Descreva o que aconteceu. O contexto da página será anexado automaticamente.</p>;
  }

  return (
    <div className="app-feedback-context-summary">
      <p className="app-feedback-context-title">Contexto automático</p>
      <ul className="app-feedback-context-list">
        {p?.pagina && <li><strong>Página:</strong> {p.pagina}</li>}
        {p?.rota && <li><strong>Rota:</strong> {p.rota}</li>}
        {p?.acao && <li><strong>Ação:</strong> {p.acao}</li>}
        {p?.componente && <li><strong>Componente:</strong> {p.componente}</li>}
        {p?.origem && <li><strong>Origem:</strong> {p.origem}</li>}
        {p?.mensagem_erro && (
          <li>
            <strong>Erro:</strong> {p.mensagem_erro.slice(0, 200)}
            {p.mensagem_erro.length > 200 ? '…' : ''}
          </li>
        )}
        {p?.user_agent && (
          <li>
            <strong>Navegador:</strong> {p.user_agent.slice(0, 80)}…
          </li>
        )}
      </ul>
    </div>
  );
}

function ManualFallbackPanel({
  manualFallback,
  copyStatus,
  onCopyReport,
  onCopyEmail,
  onRetryMailto,
  retrying,
}) {
  return (
    <div className="app-feedback-fallback" data-testid="app-feedback-fallback">
      <p className="app-feedback-fallback-title">{MSG_APP_FEEDBACK_FALLBACK_TITLE}</p>
      <p className="app-feedback-muted">{MSG_APP_FEEDBACK_FALLBACK_BODY}</p>
      <p className="app-feedback-fallback-email">
        <strong>{manualFallback.supportEmail}</strong>
      </p>

      <div className="app-feedback-fallback-actions">
        <button type="button" className="btn-secondary" onClick={onCopyReport}>
          Copiar reporte
        </button>
        <button type="button" className="btn-secondary" onClick={onCopyEmail}>
          Copiar e-mail de suporte
        </button>
        <button type="button" className="btn-primary" onClick={onRetryMailto} disabled={retrying}>
          {retrying ? 'Abrindo Gmail…' : 'Tentar abrir Gmail novamente'}
        </button>
      </div>

      {copyStatus === 'report_copied' && (
        <p className="app-feedback-copy-ok" role="status">Reporte copiado.</p>
      )}
      {copyStatus === 'email_copied' && (
        <p className="app-feedback-copy-ok" role="status">E-mail copiado.</p>
      )}
      {copyStatus === 'copy_failed' && (
        <p className="app-feedback-error" role="alert">
          Não foi possível copiar. Selecione o texto abaixo manualmente.
        </p>
      )}

      <label className="app-feedback-label">
        Texto do reporte
        <textarea
          className="app-feedback-textarea app-feedback-fallback-preview"
          readOnly
          rows={8}
          value={manualFallback.manualText}
        />
      </label>
    </div>
  );
}

export default function AppFeedbackModal({
  open,
  context,
  onClose,
  onSubmit,
  onSuccess,
  authBlockMessage,
}) {
  const tipoId = useId();
  const severidadeId = useId();
  const comentarioId = useId();
  const comentarioRef = useRef(null);

  const runtimeCtx = useMemo(() => getRuntimeContext(), [open]);
  const safeContext = context ?? {};

  const defaultTipo = useMemo(() => mapContextToDefaultTipo(context), [context]);

  const [tipo, setTipo] = useState(() => defaultTipo || DEFAULT_APP_FEEDBACK_TYPE_VALUE);
  const [severidade, setSeveridade] = useState(DEFAULT_APP_FEEDBACK_SEVERITY_VALUE);
  const [comentario, setComentario] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [retryingMailto, setRetryingMailto] = useState(false);
  const [error, setError] = useState(null);
  const [manualFallback, setManualFallback] = useState(null);
  const [copyStatus, setCopyStatus] = useState(null);
  const [lastSubmitPayload, setLastSubmitPayload] = useState(null);

  useEffect(() => {
    if (!open) return;
    setTipo(defaultTipo);
    setSeveridade(DEFAULT_APP_FEEDBACK_SEVERITY_VALUE);
    setComentario('');
    setError(null);
    setManualFallback(null);
    setCopyStatus(null);
    setLastSubmitPayload(null);
    window.setTimeout(() => comentarioRef.current?.focus(), 100);
  }, [open, defaultTipo]);

  const handleClose = () => {
    if (submitting || retryingMailto) return;
    const draft = comentario.trim();
    if (draft.length > 0 && !manualFallback) {
      const ok = window.confirm('Descartar o comentário e fechar?');
      if (!ok) return;
    }
    onClose?.();
  };

  const applySubmitResult = (result) => {
    if (result?.ok && result.status === 'opened_email_client') {
      onSuccess?.(
        result.message ||
          (result.method === 'gmail_compose'
            ? MSG_APP_FEEDBACK_SUCCESS_GMAIL
            : MSG_APP_FEEDBACK_SUCCESS_MAILTO),
      );
      return true;
    }
    if (result?.ok && result.status === 'saved_local') {
      setManualFallback({
        supportEmail: result.support_email || SUPPORT_EMAIL,
        subject: result.email_subject,
        body: result.email_body,
        manualText:
          result.manual_report_text ||
          buildManualSupportInstructions({
            supportEmail: result.support_email || SUPPORT_EMAIL,
            subject: result.email_subject,
            body: result.email_body,
          }),
      });
      setCopyStatus(null);
      return true;
    }
    return false;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (authBlockMessage) {
      setError(authBlockMessage);
      return;
    }
    const trimmed = comentario.trim();
    if (trimmed.length < APP_FEEDBACK_COMMENT_MIN) {
      setError(`Descreva o problema com pelo menos ${APP_FEEDBACK_COMMENT_MIN} caracteres.`);
      return;
    }
    if (trimmed.length > APP_FEEDBACK_COMMENT_MAX) {
      setError(`Máximo ${APP_FEEDBACK_COMMENT_MAX} caracteres.`);
      return;
    }

    setSubmitting(true);
    setError(null);
    setManualFallback(null);
    setCopyStatus(null);
    try {
      setLastSubmitPayload({ tipo, severidade, comment: trimmed, context: safeContext });
      const result = await onSubmit?.({
        tipo,
        severidade,
        comment: trimmed,
        context: safeContext,
      });
      if (applySubmitResult(result)) return;
      if (result?.status === 'invalid_payload') {
        const fieldError =
          result.errors?.descricao ||
          result.errors?.email_contato ||
          Object.values(result.errors || {})[0];
        setError(fieldError || result.message || MSG_APP_FEEDBACK_VALIDATION);
        return;
      }
      setError(result?.message || MSG_APP_FEEDBACK_FAILED);
    } catch {
      setError(MSG_APP_FEEDBACK_FAILED);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetryMailto = async () => {
    if (!lastSubmitPayload) return;
    setRetryingMailto(true);
    setError(null);
    try {
      const result = await onSubmit?.({
        tipo: lastSubmitPayload.tipo,
        severidade: lastSubmitPayload.severidade ?? DEFAULT_APP_FEEDBACK_SEVERITY_VALUE,
        comment: lastSubmitPayload.comment,
        context: lastSubmitPayload.context,
      });
      if (applySubmitResult(result)) {
        if (result?.status === 'opened_email_client') return;
      } else if (result && !result.ok) {
        setError(result.message || MSG_APP_FEEDBACK_FAILED);
      }
    } catch {
      setError(MSG_APP_FEEDBACK_FAILED);
    } finally {
      setRetryingMailto(false);
    }
  };

  const handleCopyReport = async () => {
    if (!manualFallback?.manualText) return;
    const result = await copyTextToClipboard(manualFallback.manualText);
    setCopyStatus(result.ok ? 'report_copied' : 'copy_failed');
  };

  const handleCopyEmail = async () => {
    if (!manualFallback?.supportEmail) return;
    const result = await copyTextToClipboard(manualFallback.supportEmail);
    setCopyStatus(result.ok ? 'email_copied' : 'copy_failed');
  };

  const selectedType = getFeedbackProblemType(tipo);
  const selectedSeverity = getFeedbackSeverity(severidade);

  if (!open) return null;

  return (
    <Modal
      onClose={handleClose}
      className="app-feedback-modal"
      portal
      zIndex={1300}
      closeButtonTestId="report-problem-close"
    >
      <div className="app-feedback-modal-inner" onClick={(e) => e.stopPropagation()} data-testid="report-problem-modal">
        <h2 id="app-feedback-title">Reportar problema</h2>
        <p className="app-feedback-muted">
          Relate um problema da aplicação (não confundir com reporte de um edital específico).
        </p>
        {!manualFallback && (
          <p className="app-feedback-muted app-feedback-mailto-hint">{MSG_APP_FEEDBACK_MODAL_HINT}</p>
        )}

        <ContextSummary context={safeContext} />

        <p
          className="app-feedback-muted app-feedback-runtime-badge"
          data-testid="app-feedback-runtime-badge"
        >
          Ambiente detectado: {getRuntimeDisplayLabel(runtimeCtx)}
        </p>
        <p
          className="app-feedback-muted app-feedback-guidance"
          data-testid="app-feedback-guidance"
        >
          {getReportProblemGuidanceText(runtimeCtx)}
        </p>

        {manualFallback ? (
          <>
            <ManualFallbackPanel
              manualFallback={manualFallback}
              copyStatus={copyStatus}
              onCopyReport={handleCopyReport}
              onCopyEmail={handleCopyEmail}
              onRetryMailto={handleRetryMailto}
              retrying={retryingMailto}
            />
            <div className="app-feedback-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={handleClose}
                data-testid="report-problem-close"
              >
                Fechar
              </button>
            </div>
          </>
        ) : (
          <form onSubmit={handleSubmit} className="app-feedback-form">
            <label className="app-feedback-label" htmlFor={tipoId}>
              Tipo do problema
              <select
                id={tipoId}
                className="app-feedback-input"
                value={selectedType.value}
                onChange={(e) => setTipo(e.target.value)}
                disabled={submitting}
              >
                {APP_FEEDBACK_PROBLEM_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="app-feedback-label" htmlFor={severidadeId}>
              Severidade
              <select
                id={severidadeId}
                className="app-feedback-input"
                value={selectedSeverity.value}
                onChange={(e) => setSeveridade(e.target.value)}
                disabled={submitting}
              >
                {APP_FEEDBACK_SEVERITY_LEVELS.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label} — {level.description}
                  </option>
                ))}
              </select>
            </label>
            <p className="app-feedback-muted app-feedback-severity-hint">
              {selectedSeverity.description}
            </p>

            <label className="app-feedback-label" htmlFor={comentarioId}>
              O que aconteceu?
              <textarea
                id={comentarioId}
                ref={comentarioRef}
                className="app-feedback-textarea"
                rows={4}
                value={comentario}
                onChange={(e) => setComentario(e.target.value)}
                disabled={submitting}
                placeholder="Descreva o que você estava fazendo e o que esperava ver."
                maxLength={APP_FEEDBACK_COMMENT_MAX}
              />
            </label>

            {authBlockMessage && <p className="app-feedback-error">{authBlockMessage}</p>}
            {error && <p className="app-feedback-error" role="alert">{error}</p>}

            <div className="app-feedback-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={handleClose}
                disabled={submitting}
                data-testid="report-problem-close"
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={submitting} data-testid="app-feedback-submit">
                {submitting ? 'Abrindo Gmail…' : 'Abrir Gmail com reporte'}
              </button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
}
