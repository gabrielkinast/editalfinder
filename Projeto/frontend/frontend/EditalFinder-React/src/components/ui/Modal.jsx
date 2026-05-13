import { useEffect } from 'react';

/**
 * Modal reutilizável (overlay + conteúdo). Usa classes `.modal` / `.modal-content` do global.css.
 * @param {{ hideCloseButton?: boolean }} props — se true, omite o botão × (ex.: quando o conteúdo já tem "Fechar").
 */
export default function Modal({ children, onClose, className = '', hideCloseButton = false }) {
  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, []);

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  return (
    <div
      className="modal"
      style={{ display: 'flex' }}
      role="presentation"
      onClick={onClose}
    >
      <div
        className={`modal-content ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        {!hideCloseButton && (
          <button type="button" className="close-modal" onClick={onClose} aria-label="Fechar">
            &times;
          </button>
        )}
        {children}
      </div>
    </div>
  );
}
