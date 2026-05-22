import { buildAppFeedbackPayload } from '../feedback/buildAppFeedbackPayload';
import { logAppFeedback } from '../feedback/appFeedbackLog';

const LAST_ERROR_KEY = 'app_feedback_last_error';

let handlers = {
  onReportableError: null,
  showErrorToast: null,
};

let installed = false;
let errorListener = null;
let rejectionListener = null;

function inferPaginaFromRoute() {
  try {
    const p = window.location.pathname || '';
    if (p.includes('workspace-cientifico')) return 'workspace_cientifico';
    if (p.includes('workspace-consultor')) return 'workspace_consultor';
    if (p.includes('radar')) return 'radar_fomento';
    if (p.includes('cadastros')) return 'cadastros';
    if (p.includes('noticias')) return 'noticias';
    if (p.includes('pesquisas')) return 'pesquisas';
    if (p.includes('portais')) return 'portais';
    if (p.includes('concursos')) return 'concursos';
    if (p.includes('edital')) return 'edital_detalhes';
    if (p.includes('dashboard')) return 'dashboard';
    return 'app';
  } catch {
    return 'app';
  }
}

function storeLastError(context) {
  try {
    sessionStorage.setItem(
      LAST_ERROR_KEY,
      JSON.stringify({
        ...context,
        storedAt: new Date().toISOString(),
      }),
    );
  } catch {
    /* ignore */
  }
}

export function getLastReportableError() {
  try {
    const raw = sessionStorage.getItem(LAST_ERROR_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function notifyReportable(context) {
  storeLastError(context);
  handlers.onReportableError?.(context);
  handlers.showErrorToast?.('Ocorreu um erro inesperado.', context);
  logAppFeedback('global_error_captured', {
    origem: context.origem,
    message: context.payload?.mensagem_erro?.slice?.(0, 120),
  });
}

function handleWindowError(event) {
  const err = event.error || new Error(event.message || 'Erro desconhecido');
  const payload = buildAppFeedbackPayload({
    tipo: 'erro_global',
    origem: 'window_error',
    pagina: inferPaginaFromRoute(),
    error: err,
    extraContext: {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    },
  });
  notifyReportable({ payload, error: err, origem: 'window_error' });
}

function handleUnhandledRejection(event) {
  const reason = event.reason;
  const err = reason instanceof Error ? reason : new Error(String(reason ?? 'Promise rejeitada'));
  const payload = buildAppFeedbackPayload({
    tipo: 'erro_global',
    origem: 'unhandled_rejection',
    pagina: inferPaginaFromRoute(),
    error: err,
    extraContext: {
      promiseReason: typeof reason === 'string' ? reason.slice(0, 500) : reason?.message,
    },
  });
  notifyReportable({ payload, error: err, origem: 'unhandled_rejection' });
}

/**
 * @param {{ onReportableError?: (ctx: object) => void; showErrorToast?: (message: string, context: object) => void }} h
 */
export function registerGlobalErrorReporterHandlers(h = {}) {
  handlers = { ...handlers, ...h };
}

export function installGlobalErrorReporter() {
  if (installed || typeof window === 'undefined') return;
  errorListener = handleWindowError;
  rejectionListener = handleUnhandledRejection;
  window.addEventListener('error', errorListener);
  window.addEventListener('unhandledrejection', rejectionListener);
  installed = true;
  logAppFeedback('global_reporter_installed', {});
}

export function uninstallGlobalErrorReporter() {
  if (!installed || typeof window === 'undefined') return;
  if (errorListener) window.removeEventListener('error', errorListener);
  if (rejectionListener) window.removeEventListener('unhandledrejection', rejectionListener);
  errorListener = null;
  rejectionListener = null;
  installed = false;
}
