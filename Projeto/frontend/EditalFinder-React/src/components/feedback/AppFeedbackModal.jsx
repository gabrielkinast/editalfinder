import { useEffect, useId, useMemo, useRef, useState } from 'react';
import Modal from '../ui/Modal';
import {
  APP_FEEDBACK_COMMENT_MAX,
  APP_FEEDBACK_COMMENT_MIN,
  APP_FEEDBACK_TIPOS,
} from '../../constants/appFeedbackConfig';
const MSG_SUCCESS = 'Obrigado! Seu relatório foi enviado.';
const MSG_ERROR = 'Não foi possível enviar agora. O relatório foi salvo localmente para reenvio.';

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

export default function AppFeedbackModal({
  open,
  context,
  onClose,
  onSubmit,
  onSuccess,
  authBlockMessage,
}) {
  const tipoId = useId();
  const comentarioId = useId();
  const comentarioRef = useRef(null);

  const defaultTipo = useMemo(() => {
    if (context?.tipo) return context.tipo;
    if (context?.payload?.tipo_feedback) return context.payload.tipo_feedback;
    if (context?.origem === 'window_error' || context?.origem === 'unhandled_rejection') {
      return 'erro_global';
    }
    if (context?.origem === 'error_boundary') return 'erro_pagina';
    if (context?.origem === 'api_error' || context?.origem === 'toast_error') return 'erro_api';
    return 'outro';
  }, [context]);

  const [tipo, setTipo] = useState(defaultTipo);
  const [comentario, setComentario] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) return;
    setTipo(defaultTipo);
    setComentario('');
    setError(null);
    window.setTimeout(() => comentarioRef.current?.focus(), 100);
  }, [open, defaultTipo]);

  const handleClose = () => {
    if (submitting) return;
    const draft = comentario.trim();
    if (draft.length > 0) {
      const ok = window.confirm('Descartar o comentário e fechar?');
      if (!ok) return;
    }
    onClose?.();
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
    try {
      const result = await onSubmit?.({ tipo, comment: trimmed, context });
      if (result?.ok) {
        onSuccess?.(MSG_SUCCESS);
        return;
      }
      setError(result?.error || MSG_ERROR);
    } catch {
      setError(MSG_ERROR);
    } finally {
      setSubmitting(false);
    }
  };

  if (!open) return null;

  return (
    <Modal
      onClose={handleClose}
      className="app-feedback-modal"
      portal
      zIndex={1300}
    >
      <div className="app-feedback-modal-inner" onClick={(e) => e.stopPropagation()}>
        <h2 id="app-feedback-title">Reportar problema</h2>
        <p className="app-feedback-muted">
          Relate um problema da aplicação (não confundir com reporte de um edital específico).
        </p>

        <ContextSummary context={context} />

        <form onSubmit={handleSubmit} className="app-feedback-form">
          <label className="app-feedback-label" htmlFor={tipoId}>
            Tipo do problema
            <select
              id={tipoId}
              className="app-feedback-input"
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              disabled={submitting}
            >
              {APP_FEEDBACK_TIPOS.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>

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
            >
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Enviando…' : 'Enviar relatório'}
            </button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
