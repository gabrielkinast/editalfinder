import { buildAppFeedbackPayload } from '../feedback/buildAppFeedbackPayload';

let actionErrorHandlers = {
  showErrorToast: null,
  openFeedbackModal: null,
  setLastReportable: null,
};

/**
 * @param {{ showErrorToast?: Function; openFeedbackModal?: Function; setLastReportable?: Function }} h
 */
export function registerActionErrorHandlers(h = {}) {
  actionErrorHandlers = { ...actionErrorHandlers, ...h };
}

/**
 * @param {object} params
 */
export function createReportableActionError({
  origem = 'api_error',
  pagina,
  acao,
  error,
  extraContext,
  userMessage,
}) {
  const payload = buildAppFeedbackPayload({
    tipo: 'erro_api',
    origem,
    pagina,
    acao,
    error,
    extraContext,
  });

  const ctx = {
    payload,
    error: error instanceof Error ? error : new Error(String(error || userMessage || 'Erro')),
    origem,
    pagina,
    acao,
    userMessage: userMessage || 'Não foi possível concluir a ação.',
  };

  actionErrorHandlers.setLastReportable?.(ctx);
  return ctx;
}

/**
 * @param {object} params
 */
export function handleAppActionError(params = {}) {
  const ctx = createReportableActionError(params);
  actionErrorHandlers.showErrorToast?.(ctx.userMessage, ctx);
  return ctx;
}
