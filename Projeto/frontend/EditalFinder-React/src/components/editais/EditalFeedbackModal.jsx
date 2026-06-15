import { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  EDITAL_FEEDBACK_REASONS,
  EDITAL_FEEDBACK_COMMENT_MAX,
  EDITAL_FEEDBACK_COMMENT_MIN_OUTRO,
  getEditalFeedbackReason,
} from '../../constants/editalFeedbackReasons';
import { buildEditalFeedbackPayload } from '../../utils/edital/buildEditalFeedbackPayload';
import { resolveAppUserId } from '../../utils/appUserId';
import {
  MSG_FEEDBACK_AUTH_LOADING,
  MSG_FEEDBACK_NO_INTERNAL_PROFILE,
  MSG_FEEDBACK_NOT_AUTHENTICATED,
  submitEditalFeedback,
} from '../../services/editalFeedbackService';
import { logEditalFeedback } from '../../utils/edital/editalFeedbackLog';
import { getReportProblemGuidanceText } from '../../utils/feedback/appFeedbackGuidance';

const MSG_OUTRO_MIN =
  'Descreva o problema encontrado com pelo menos 10 caracteres.';
const MSG_SUCCESS = 'Obrigado! Seu reporte foi enviado para revisão.';
const MSG_ERROR = 'Não foi possível enviar o reporte agora. Tente novamente.';

function validateForm(motivo, comentario) {
  if (!motivo) {
    return { valid: false, field: 'motivo', message: 'Selecione um motivo.' };
  }
  const trimmed = (comentario || '').trim();
  if (motivo === 'outro') {
    if (trimmed.length < EDITAL_FEEDBACK_COMMENT_MIN_OUTRO) {
      return { valid: false, field: 'comentario', message: MSG_OUTRO_MIN };
    }
  }
  if (trimmed.length > EDITAL_FEEDBACK_COMMENT_MAX) {
    return {
      valid: false,
      field: 'comentario',
      message: `O comentário deve ter no máximo ${EDITAL_FEEDBACK_COMMENT_MAX} caracteres.`,
    };
  }
  return { valid: true };
}

function stopInnerPointer(e) {
  e.stopPropagation();
}

/**
 * Modal de reporte — lê perfil interno de AuthContext (`user` = public.usuario na app).
 * @param {{
 *   edital: object;
 *   isOpen: boolean;
 *   onClose: () => void;
 *   onSubmitted?: (payload: object) => void;
 * }} props
 */
export default function EditalFeedbackModal({ edital, isOpen, onClose, onSubmitted }) {
  const { user: appUser, authenticated, loading: authLoading } = useAuth();

  const motivoId = useId();
  const comentarioId = useId();
  const motivoRef = useRef(null);
  const closingRef = useRef(false);

  const [motivo, setMotivo] = useState('');
  const [comentario, setComentario] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [fieldError, setFieldError] = useState(null);
  const [success, setSuccess] = useState(false);

  const reasonMeta = getEditalFeedbackReason(motivo);
  const isOutro = motivo === 'outro';

  const appUserId = useMemo(() => resolveAppUserId(appUser), [appUser]);

  const authBlockMessage = useMemo(() => {
    if (authLoading) return MSG_FEEDBACK_AUTH_LOADING;
    if (appUserId != null) return null;
    if (!authenticated) return MSG_FEEDBACK_NOT_AUTHENTICATED;
    return MSG_FEEDBACK_NO_INTERNAL_PROFILE;
  }, [authLoading, appUserId, authenticated]);

  const canSubmit = !authLoading && appUserId != null;
  const canDismiss = !isSubmitting;

  const resetForm = useCallback(() => {
    setMotivo('');
    setComentario('');
    setError(null);
    setFieldError(null);
    setSuccess(false);
    setIsSubmitting(false);
    closingRef.current = false;
  }, []);

  const requestClose = useCallback(
    (reason) => {
      if (closingRef.current || isSubmitting) return;
      closingRef.current = true;
      logEditalFeedback(`modal_close_${reason}`);
      onClose?.();
    },
    [onClose, isSubmitting],
  );

  useEffect(() => {
    if (!isOpen) {
      resetForm();
      return undefined;
    }

    logEditalFeedback('modal_open', {
      id_edital: edital?.id_edital ?? edital?.idNumerico ?? null,
      appUser_id_usuario: appUserId,
      authenticated,
      authLoading,
    });

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const t = window.setTimeout(() => motivoRef.current?.focus(), 50);

    return () => {
      window.clearTimeout(t);
      document.body.style.overflow = prevOverflow;
    };
  }, [isOpen, edital, resetForm, appUserId, authenticated, authLoading]);

  useEffect(() => {
    if (!isOpen || !canDismiss) return undefined;

    const onKeyDown = (e) => {
      if (e.key !== 'Escape') return;
      e.preventDefault();
      e.stopPropagation();
      requestClose('escape');
    };

    document.addEventListener('keydown', onKeyDown, true);
    return () => document.removeEventListener('keydown', onKeyDown, true);
  }, [isOpen, canDismiss, requestClose]);

  useEffect(() => {
    if (!success) return undefined;
    const t = window.setTimeout(() => {
      requestClose('success_timer');
    }, 1800);
    return () => window.clearTimeout(t);
  }, [success, requestClose]);

  const handleBackdropPointerDown = (e) => {
    if (e.target !== e.currentTarget) return;
    if (!canDismiss) return;
    e.preventDefault();
    e.stopPropagation();
    requestClose('backdrop');
  };

  const handleMotivoChange = (e) => {
    const v = e.target.value;
    setMotivo(v);
    setFieldError(null);
    setError(null);
    logEditalFeedback('reason_selected', { motivo: v });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isSubmitting || success) return;

    if (!canSubmit) {
      setError(authBlockMessage || MSG_FEEDBACK_NOT_AUTHENTICATED);
      logEditalFeedback('validation_error', {
        reason: authLoading ? 'auth_loading' : 'missing_internal_profile',
        appUser_id_usuario: appUserId,
      });
      return;
    }

    const validation = validateForm(motivo, comentario);
    if (!validation.valid) {
      setFieldError(validation.message);
      logEditalFeedback('validation_error', {
        field: validation.field,
        motivo: motivo || null,
      });
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setFieldError(null);

    const payload = buildEditalFeedbackPayload(
      edital,
      { motivo, comentario: comentario.trim() || null },
      appUser,
    );

    const res = await submitEditalFeedback(payload, {
      appUser,
      authenticated,
      authLoading,
    });
    setIsSubmitting(false);

    if (res.ok) {
      setSuccess(true);
      onSubmitted?.(payload);
      return;
    }

    setError(res.error || MSG_ERROR);
  };

  if (!isOpen || !edital) return null;

  const comentarioLabel = isOutro
    ? 'Descreva o problema encontrado'
    : 'Comentário adicional, opcional';
  const comentarioRequired = isOutro;

  return createPortal(
    <div
      className="edital-feedback-overlay"
      role="presentation"
      onMouseDown={handleBackdropPointerDown}
      onPointerDown={handleBackdropPointerDown}
    >
      <div
        className="edital-feedback-modal-panel modal-content edital-feedback-modal-wrap"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edital-feedback-title"
        onMouseDown={stopInnerPointer}
        onPointerDown={stopInnerPointer}
        onClick={stopInnerPointer}
      >
        {!success && canDismiss ? (
          <button
            type="button"
            className="close-modal edital-feedback-close-x"
            aria-label="Fechar"
            onMouseDown={stopInnerPointer}
            onClick={(e) => {
              e.stopPropagation();
              requestClose('button');
            }}
          >
            &times;
          </button>
        ) : null}

        <div className="edital-feedback-modal">
          <div className="modal-header edital-feedback-header">
            <h2 id="edital-feedback-title">Reportar problema neste edital</h2>
          </div>

          {success ? (
            <div className="edital-feedback-success" role="status">
              <p>{MSG_SUCCESS}</p>
              <button
                type="button"
                className="btn-view edital-feedback-btn-close"
                onMouseDown={stopInnerPointer}
                onClick={(e) => {
                  e.stopPropagation();
                  requestClose('button');
                }}
              >
                Fechar
              </button>
            </div>
          ) : (
            <>
              <p className="edital-feedback-intro">
                Ajude-nos a melhorar a qualidade das oportunidades. Explique o problema encontrado neste
                item.
              </p>
              <p className="edital-feedback-guidance" data-testid="edital-feedback-guidance">
                {getReportProblemGuidanceText()}
              </p>

              {authBlockMessage ? (
                <p className="edital-feedback-login-hint" role="alert">
                  {authBlockMessage}
                </p>
              ) : null}

              <p className="edital-feedback-edital-ref" title={edital.titulo}>
                <span className="edital-feedback-edital-label">Edital:</span>{' '}
                {edital.titulo || 'Sem título'}
              </p>

              <form
                className="edital-feedback-form"
                onSubmit={handleSubmit}
                noValidate
                onMouseDown={stopInnerPointer}
                onClick={stopInnerPointer}
              >
                <div className="form-group">
                  <label htmlFor={motivoId}>
                    Motivo <span className="edital-feedback-required">*</span>
                  </label>
                  <select
                    id={motivoId}
                    ref={motivoRef}
                    name="motivo"
                    value={motivo}
                    onChange={handleMotivoChange}
                    required
                    disabled={isSubmitting || !canSubmit}
                    aria-invalid={fieldError && !motivo ? 'true' : undefined}
                  >
                    <option value="">Selecione…</option>
                    {EDITAL_FEEDBACK_REASONS.map((r) => (
                      <option key={r.value} value={r.value}>
                        {r.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor={comentarioId}>
                    {comentarioLabel}
                    {comentarioRequired ? (
                      <span className="edital-feedback-required"> *</span>
                    ) : null}
                  </label>
                  <textarea
                    id={comentarioId}
                    name="comentario"
                    rows={4}
                    value={comentario}
                    onChange={(e) => {
                      setComentario(e.target.value);
                      setFieldError(null);
                      setError(null);
                    }}
                    placeholder={reasonMeta?.placeholder || 'Detalhes opcionais…'}
                    maxLength={EDITAL_FEEDBACK_COMMENT_MAX}
                    required={comentarioRequired}
                    disabled={isSubmitting || !canSubmit || !motivo}
                    aria-invalid={fieldError ? 'true' : undefined}
                    aria-describedby="edital-feedback-char-count"
                  />
                  <span id="edital-feedback-char-count" className="edital-feedback-char-count">
                    {comentario.length}/{EDITAL_FEEDBACK_COMMENT_MAX}
                  </span>
                </div>

                {fieldError ? (
                  <p className="edital-feedback-field-error" role="alert">
                    {fieldError}
                  </p>
                ) : null}
                {error ? (
                  <p className="edital-feedback-error" role="alert">
                    {error}
                  </p>
                ) : null}

                <div className="edital-feedback-actions">
                  <button
                    type="button"
                    className="btn-detalhes dash-action-outline edital-feedback-btn-cancel"
                    onMouseDown={stopInnerPointer}
                    onClick={(e) => {
                      e.stopPropagation();
                      requestClose('button');
                    }}
                    disabled={isSubmitting}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="btn-view edital-feedback-btn-submit"
                    disabled={isSubmitting || !canSubmit || !motivo}
                  >
                    {isSubmitting ? 'Enviando...' : 'Enviar reporte'}
                  </button>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
}
