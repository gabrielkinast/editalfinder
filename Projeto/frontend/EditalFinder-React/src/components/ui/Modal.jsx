import { useEffect } from 'react';
import { createPortal } from 'react-dom';

/**
 * Modal reutilizável (overlay + conteúdo). Usa classes `.modal` / `.modal-content` do global.css.
 * @param {{ hideCloseButton?: boolean; portal?: boolean; zIndex?: number }} props
 *   portal — renderiza em document.body (evita clipping do layout da página).
 */
export default function Modal({
  children,
  onClose,
  className = '',
  hideCloseButton = false,
  portal = false,
  zIndex,
}) {
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

  const overlayStyle =
    zIndex != null
      ? { display: 'flex', zIndex }
      : { display: 'flex' };

  const node = (
    <div
      className="modal"
      style={overlayStyle}
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

  if (portal && typeof document !== 'undefined') {
    return createPortal(node, document.body);
  }

  return node;
}
