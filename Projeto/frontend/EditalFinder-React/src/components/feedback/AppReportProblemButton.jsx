import { useAppFeedback } from '../../contexts/AppFeedbackContext';
import { buildAppFeedbackPayload } from '../../utils/feedback/buildAppFeedbackPayload';

export default function AppReportProblemButton({
  origem = 'user_report',
  pagina,
  componente,
  acao,
  error,
  errorInfo,
  extraContext,
  tipo = 'outro',
  label = 'Reportar problema',
  variant = 'secondary',
  size = '',
  className = '',
}) {
  const { openAppFeedbackModal } = useAppFeedback();

  const handleClick = () => {
    const payload =
      error || errorInfo
        ? buildAppFeedbackPayload({
            tipo,
            origem,
            pagina,
            componente,
            acao,
            error,
            errorInfo,
            extraContext,
          })
        : null;

    openAppFeedbackModal({
      origem,
      pagina,
      componente,
      acao,
      tipo,
      error,
      errorInfo,
      extraContext,
      payload,
    });
  };

  const btnClass = [
    variant === 'link' ? 'app-feedback-link-btn' : `btn-${variant}`,
    size,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button type="button" className={btnClass} onClick={handleClick}>
      {label}
    </button>
  );
}
