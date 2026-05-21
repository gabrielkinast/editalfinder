import { useCallback, useRef, useState } from 'react';
import { logEditalFeedback } from '../../utils/edital/editalFeedbackLog';
import EditalFeedbackModal from './EditalFeedbackModal';

/** Ignora cliques fantasma após fechar o modal (click-through no mesmo gesto). */
const CLICK_GUARD_MS = 450;

/**
 * Botão discreto + modal de reporte (reutilizável no card, modal de detalhes e página).
 * @param {{
 *   edital: object;
 *   className?: string;
 *   variant?: 'card' | 'inline' | 'details';
 * }} props
 */
export default function EditalReportProblemButton({
  edital,
  className = '',
  variant = 'card',
}) {
  const [open, setOpen] = useState(false);
  const ignoreOpenUntilRef = useRef(0);

  const handleClose = useCallback(() => {
    ignoreOpenUntilRef.current = Date.now() + CLICK_GUARD_MS;
    setOpen(false);
  }, []);

  const handleOpen = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (Date.now() < ignoreOpenUntilRef.current) {
        logEditalFeedback('click_stop_propagation', { reason: 'post_close_guard' });
        return;
      }
      logEditalFeedback('modal_open', {
        source: variant,
        id_edital: edital?.id_edital ?? edital?.idNumerico ?? null,
      });
      setOpen(true);
    },
    [edital, variant],
  );

  const handlePointerDown = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const btnClass = [
    'edital-report-problem-btn',
    `edital-report-problem-btn--${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <>
      <button
        type="button"
        className={btnClass}
        onMouseDown={handlePointerDown}
        onPointerDown={handlePointerDown}
        onClick={handleOpen}
        title="Reportar problema"
        aria-label="Reportar problema neste edital"
        aria-haspopup="dialog"
        aria-expanded={open}
      >
        {variant === 'card' ? (
          <>
            <span className="edital-report-problem-icon" aria-hidden="true">
              ⚑
            </span>
            <span className="edital-report-problem-text">Reportar problema</span>
          </>
        ) : (
          'Reportar problema'
        )}
      </button>

      {open ? (
        <EditalFeedbackModal edital={edital} isOpen={open} onClose={handleClose} />
      ) : null}
    </>
  );
}
