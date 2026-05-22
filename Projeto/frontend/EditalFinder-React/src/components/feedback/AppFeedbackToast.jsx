import { createPortal } from 'react-dom';

export default function AppFeedbackToast({ toast, onAction, onDismiss }) {
  if (!toast?.message) return null;

  const node = (
    <div
      className={`app-feedback-toast app-feedback-toast--${toast.type || 'error'}`}
      role="status"
      aria-live="polite"
    >
      <span className="app-feedback-toast-message">{toast.message}</span>
      {toast.actionLabel && onAction && (
        <button type="button" className="app-feedback-toast-action" onClick={onAction}>
          {toast.actionLabel}
        </button>
      )}
      <button
        type="button"
        className="app-feedback-toast-dismiss"
        onClick={onDismiss}
        aria-label="Fechar"
      >
        ×
      </button>
    </div>
  );

  return createPortal(node, document.body);
}
