import {
  APP_FEEDBACK_COMMENT_MAX,
  APP_FEEDBACK_ERROR_MSG_MAX,
  APP_FEEDBACK_STACK_MAX,
} from '../../constants/appFeedbackConfig';

const SENSITIVE_PATTERN =
  /(access_token|refresh_token|authorization|apikey|api_key|secret|password|bearer\s|jwt\s)/i;

const RELEVANT_LS_PREFIXES = [
  'scientific_workspace_',
  'consultor_',
  'radar_',
  'editalfinder_',
  'app_feedback_',
];

function truncate(str, max) {
  const s = String(str || '');
  if (s.length <= max) return s;
  return `${s.slice(0, max)}…`;
}

function redactText(text) {
  if (!text) return null;
  let out = String(text);
  if (SENSITIVE_PATTERN.test(out)) {
    out = out.replace(/[^\s]+/g, (token) => (SENSITIVE_PATTERN.test(token) ? '[REDACTED]' : token));
  }
  return truncate(out, APP_FEEDBACK_STACK_MAX);
}

function inferRoute() {
  try {
    const { pathname, search, hash } = window.location;
    return `${pathname || ''}${search || ''}${hash || ''}`.slice(0, 500) || null;
  } catch {
    return null;
  }
}

function inferPagina(rota) {
  const r = rota || inferRoute() || '';
  if (r.includes('workspace-cientifico')) return 'workspace_cientifico';
  if (r.includes('workspace-consultor')) return 'workspace_consultor';
  if (r.includes('radar-fomento')) return 'radar_fomento';
  if (r.includes('cadastros')) return 'cadastros';
  if (r.includes('noticias')) return 'noticias';
  if (r.includes('pesquisas')) return 'pesquisas';
  if (r.includes('portais-estrategicos')) return 'portais';
  if (r.includes('concursos')) return 'concursos';
  if (r.includes('edital/')) return 'edital_detalhes';
  if (r.includes('dashboard')) return 'dashboard';
  if (r.includes('login')) return 'login';
  return 'app';
}

function listRelevantLocalStorageKeys() {
  try {
    const keys = [];
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      if (!key) continue;
      if (RELEVANT_LS_PREFIXES.some((p) => key.startsWith(p)) || key.includes('feedback')) {
        keys.push(key);
      }
    }
    return keys.sort().slice(0, 40);
  } catch {
    return [];
  }
}

function normalizeError(error) {
  if (!error) return { message: null, stack: null, name: null };
  if (typeof error === 'string') {
    return { message: truncate(error, APP_FEEDBACK_ERROR_MSG_MAX), stack: null, name: 'string' };
  }
  const message = truncate(error.message || String(error), APP_FEEDBACK_ERROR_MSG_MAX);
  const stack = redactText(error.stack);
  return { message, stack, name: error.name || null };
}

/**
 * @param {object} input
 */
export function buildAppFeedbackPayload(input = {}) {
  const {
    tipo = 'outro',
    origem = 'user_report',
    pagina,
    componente,
    acao,
    error,
    errorInfo,
    comment,
    extraContext,
    tipo_feedback,
    rota: rotaIn,
  } = input;

  const rota = rotaIn || inferRoute();
  const { message, stack, name } = normalizeError(error);
  const componentStack = errorInfo?.componentStack
    ? redactText(String(errorInfo.componentStack))
    : null;

  const extras = {
    href: typeof window !== 'undefined' ? window.location.href?.split('?')[0]?.slice(0, 300) : null,
    timestamp: new Date().toISOString(),
    errorName: name,
    componentStack,
    extraContext: extraContext && typeof extraContext === 'object' ? extraContext : null,
    localStorageKeysRelevant: listRelevantLocalStorageKeys(),
  };

  return {
    tipo_feedback: tipo_feedback || tipo,
    origem,
    rota,
    pagina: pagina || inferPagina(rota),
    componente: componente || null,
    acao: acao || null,
    mensagem_erro: message,
    stack_erro: stack || componentStack,
    comentario: truncate((comment || '').trim(), APP_FEEDBACK_COMMENT_MAX) || null,
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent?.slice(0, 500) : null,
    app_version:
      typeof import.meta !== 'undefined' && import.meta.env?.VITE_APP_VERSION
        ? String(import.meta.env.VITE_APP_VERSION)
        : 'web',
    extras,
  };
}

export function sanitizeAppFeedbackForLog(payload) {
  return {
    tipo_feedback: payload?.tipo_feedback,
    origem: payload?.origem,
    pagina: payload?.pagina,
    rota: payload?.rota?.slice?.(0, 120),
    has_stack: Boolean(payload?.stack_erro),
    has_comment: Boolean(payload?.comentario),
  };
}
