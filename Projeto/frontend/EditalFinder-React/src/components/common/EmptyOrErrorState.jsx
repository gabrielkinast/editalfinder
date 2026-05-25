import AppReportProblemButton from '../feedback/AppReportProblemButton';

export default function EmptyOrErrorState({
  title = 'Não foi possível carregar',
  message = 'Tente novamente ou reporte o problema.',
  origem = 'api_error',
  pagina,
  acao,
  componente,
  error,
  extraContext,
  retryLabel = 'Tentar novamente',
  onRetry,
}) {
  return (
    <div className="empty-or-error-state" role="alert">
      <h3 className="empty-or-error-title">{title}</h3>
      <p className="app-feedback-muted">{message}</p>
      <div className="empty-or-error-actions">
        {onRetry && (
          <button type="button" className="btn-primary" onClick={onRetry}>
            {retryLabel}
          </button>
        )}
        <AppReportProblemButton
          origem={origem}
          pagina={pagina}
          acao={acao}
          componente={componente}
          error={error}
          extraContext={extraContext}
          tipo={error ? 'erro_api' : 'outro'}
          label="Reportar problema"
          variant="secondary"
        />
      </div>
    </div>
  );
}
