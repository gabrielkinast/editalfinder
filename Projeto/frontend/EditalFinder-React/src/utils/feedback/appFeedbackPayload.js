import {
  APP_FEEDBACK_COMMENT_MAX,
  APP_FEEDBACK_COMMENT_MIN,
  APP_FEEDBACK_ERROR_MSG_MAX,
  APP_FEEDBACK_STACK_MAX,
} from '../../constants/appFeedbackConfig.js';
import { resolveAppUserId } from '../appUserId.js';
import {
  getFeedbackProblemType,
  isHighPriorityProblemType,
  mapToLegacyTipoFeedback,
} from './appFeedbackTaxonomy.js';
import { getCategoryLabel } from './appFeedbackLabels.js';
import { getFeedbackSeverity, normalizeLegacySeverity } from './appFeedbackSeverity.js';
import { getRuntimeContext } from './runtimeContext.js';

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

function fallbackId() {
  return `afb_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

function createLocalId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return fallbackId();
}

function inferRoute() {
  try {
    const { pathname, search, hash } = window.location;
    return `${pathname || ''}${search || ''}${hash || ''}`.slice(0, 500) || null;
  } catch {
    return null;
  }
}

function getSafeLocationHref() {
  try {
    return window.location.href?.split('?')[0]?.slice(0, 500) || null;
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

function getAppVersionSafe() {
  try {
    if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_APP_VERSION) {
      return String(import.meta.env.VITE_APP_VERSION);
    }
  } catch {
    /* ambiente Node/teste */
  }
  return getRuntimeContext().is_desktop ? 'desktop' : 'web';
}

function getAppEnvSafe() {
  try {
    return typeof import.meta !== 'undefined' ? import.meta.env?.MODE ?? null : null;
  } catch {
    return null;
  }
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

function serializeError(error) {
  if (!error) return null;
  if (typeof error === 'string') return truncate(error, APP_FEEDBACK_ERROR_MSG_MAX);
  return truncate(error.message || String(error), APP_FEEDBACK_ERROR_MSG_MAX);
}

export function normalizeOptionalEmail(value) {
  if (value == null || value === '') return null;
  const s = String(value).trim();
  return s.length ? s : null;
}

function isValidEmail(value) {
  if (!value) return true;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value).trim());
}

function pickDescription(input = {}, context = {}) {
  const fromInput =
    input.descricao ??
    input.comment ??
    input.message ??
    context.comment ??
    context.descricao ??
    context.payload?.comentario ??
    context.payload?.descricao ??
    '';
  return String(fromInput || '').trim();
}

/**
 * Normaliza payload legado ou parcial — nunca deixa tipo/tipo_label/categoria ausentes.
 */
export function normalizeFeedbackPayload(payload = {}) {
  const base = payload && typeof payload === 'object' ? payload : {};
  const selectedType = getFeedbackProblemType(
    base.tipo ?? base.type ?? base.tipo_feedback ?? null,
  );
  const selectedSeverity = getFeedbackSeverity(base.severidade);
  const categoryGroup = base.categoria || selectedType.group;

  return {
    ...base,
    tipo: base.tipo || base.type || selectedType.value,
    tipo_label: base.tipo_label || selectedType.label,
    categoria: categoryGroup,
    categoria_label: base.categoria_label || getCategoryLabel(categoryGroup),
    tipo_feedback: base.tipo_feedback || mapToLegacyTipoFeedback(selectedType.value),
    severidade: selectedSeverity.value,
    severidade_label: base.severidade_label || selectedSeverity.label,
    severidade_email_prefix: base.severidade_email_prefix || selectedSeverity.emailPrefix,
  };
}

/**
 * Monta payload completo (local + campos compatíveis com app_feedback remoto).
 */
export function buildAppFeedbackPayload(input = {}, context = {}) {
  const safeInput = input && typeof input === 'object' ? input : {};
  const safeContext = context && typeof context === 'object' ? context : {};
  const ctxPayload =
    safeContext.payload && typeof safeContext.payload === 'object' ? safeContext.payload : {};

  const selectedType = getFeedbackProblemType(
    safeInput.tipo ??
      safeInput.type ??
      safeInput.tipo_feedback ??
      safeContext.tipo ??
      ctxPayload.tipo ??
      ctxPayload.tipo_feedback ??
      null,
  );
  const problem = selectedType;
  const severityRaw =
    safeInput.severidade ??
    ctxPayload.severidade ??
    safeContext.severidade ??
    null;
  const selectedSeverity = getFeedbackSeverity(normalizeLegacySeverity(severityRaw));
  const categoryGroup = safeInput.categoria ?? ctxPayload.categoria ?? problem.group;
  const platformContext = getRuntimeContext();

  const origem = safeInput.origem ?? safeContext.origem ?? ctxPayload.origem ?? 'user_report';
  const rota = safeInput.rota ?? safeContext.rota ?? ctxPayload.rota ?? inferRoute();
  const pagina = safeInput.pagina ?? safeContext.pagina ?? ctxPayload.pagina ?? inferPagina(rota);
  const componente = safeInput.componente ?? safeContext.componente ?? ctxPayload.componente ?? null;
  const acao = safeInput.acao ?? safeContext.acao ?? ctxPayload.acao ?? null;
  const error = safeInput.error ?? safeContext.error ?? null;
  const errorInfo = safeInput.errorInfo ?? safeContext.errorInfo ?? null;
  const extraContext =
    safeInput.extraContext ?? safeContext.extraContext ?? ctxPayload.extras?.extraContext ?? null;

  const descricao = truncate(pickDescription(safeInput, safeContext), APP_FEEDBACK_COMMENT_MAX);
  const { message, stack, name } = normalizeError(error);
  const componentStack = errorInfo?.componentStack
    ? redactText(String(errorInfo.componentStack))
    : null;

  const id_local = safeInput.id_local ?? ctxPayload.id_local ?? createLocalId();
  const now = new Date().toISOString();

  const metadata = {
    source: safeContext.source || safeInput.source || 'app_feedback_modal',
    route_title: safeContext.routeTitle ?? null,
    component: componente,
    last_error: serializeError(safeContext.lastError ?? error),
    extraContext: extraContext && typeof extraContext === 'object' ? extraContext : null,
    id_local,
    pagina_url: getSafeLocationHref(),
    is_desktop: platformContext.is_desktop,
    runtime: platformContext.runtime,
    platform_context: platformContext,
    app_env: getAppEnvSafe(),
    localStorageKeysRelevant: listRelevantLocalStorageKeys(),
  };

  const extras = {
    ...(ctxPayload.extras && typeof ctxPayload.extras === 'object' ? ctxPayload.extras : {}),
    href: getSafeLocationHref(),
    timestamp: now,
    errorName: name,
    componentStack,
    metadata,
    id_local,
    categoria: categoryGroup,
    categoria_label: getCategoryLabel(categoryGroup),
    severidade: selectedSeverity.value,
    severidade_label: selectedSeverity.label,
    severidade_email_prefix: selectedSeverity.emailPrefix,
    email_contato: normalizeOptionalEmail(
      safeInput.email_contato ?? safeInput.email ?? ctxPayload.email_contato,
    ),
    tipo_label: problem.label,
    runtime: platformContext.runtime,
    platform_context: platformContext,
  };

  return {
    id_local,
    tipo: problem.value,
    tipo_label: problem.label,
    tipo_feedback: mapToLegacyTipoFeedback(problem.value),
    categoria: categoryGroup,
    categoria_label: getCategoryLabel(categoryGroup),
    severidade: selectedSeverity.value,
    severidade_label: selectedSeverity.label,
    severidade_email_prefix: selectedSeverity.emailPrefix,
    descricao,
    comentario: descricao || null,
    email_contato: normalizeOptionalEmail(
      safeInput.email_contato ?? safeInput.email ?? ctxPayload.email_contato,
    ),
    origem,
    rota,
    pagina,
    pagina_url: getSafeLocationHref(),
    componente,
    acao,
    mensagem_erro: message ?? ctxPayload.mensagem_erro ?? null,
    stack_erro: stack || componentStack || ctxPayload.stack_erro || null,
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent?.slice(0, 500) : null,
    app_version: safeInput.app_version ?? safeContext.appVersion ?? getAppVersionSafe(),
    app_env: getAppEnvSafe(),
    is_desktop: platformContext.is_desktop,
    runtime: platformContext.runtime,
    platform_context: platformContext,
    created_at: now,
    status: 'pending',
    metadata,
    extras,
  };
}

export function validateAppFeedbackPayload(payload) {
  const errors = {};
  const descricao = String(payload?.descricao ?? payload?.comentario ?? '').trim();

  if (!descricao || descricao.length < APP_FEEDBACK_COMMENT_MIN) {
    errors.descricao = `Descreva o problema com pelo menos ${APP_FEEDBACK_COMMENT_MIN} caracteres.`;
  }

  if (descricao.length > APP_FEEDBACK_COMMENT_MAX) {
    errors.descricao = `A descrição está muito longa (máx. ${APP_FEEDBACK_COMMENT_MAX}).`;
  }

  if (payload?.email_contato && !isValidEmail(payload.email_contato)) {
    errors.email_contato = 'Informe um e-mail válido ou deixe em branco.';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Mapeia payload local para colunas de public.app_feedback (CREATE_APP_FEEDBACK.sql).
 */
export function mapToRemoteAppFeedbackRow(payload, appUser, authUserId = null) {
  const idUsuario = resolveAppUserId(appUser);

  const severityMeta = getFeedbackSeverity(payload?.severidade);
  const prioridade =
    severityMeta.value === 'critical'
      ? 'critica'
      : severityMeta.value === 'high'
        ? 'alta'
        : isHighPriorityProblemType(payload?.tipo)
          ? 'alta'
          : 'normal';

  return {
    id_usuario: idUsuario,
    user_auth_id: authUserId || appUser?.auth_user_id || null,
    tipo_feedback: payload.tipo_feedback,
    origem: payload.origem,
    rota: payload.rota ?? null,
    pagina: payload.pagina ?? null,
    componente: payload.componente ?? null,
    acao: payload.acao ?? null,
    mensagem_erro: payload.mensagem_erro ?? null,
    stack_erro: payload.stack_erro ?? null,
    comentario: payload.comentario ?? payload.descricao ?? null,
    status: 'novo',
    prioridade,
    user_agent: payload.user_agent ?? null,
    app_version: payload.app_version ?? null,
    extras: {
      ...(payload.extras && typeof payload.extras === 'object' ? payload.extras : {}),
      id_local: payload.id_local,
      metadata: payload.metadata ?? null,
      email_contato: payload.email_contato ?? null,
      categoria: payload.categoria ?? null,
      severidade: payload.severidade ?? null,
      severidade_label: payload.severidade_label ?? null,
      severidade_email_prefix: payload.severidade_email_prefix ?? null,
      categoria_label: payload.categoria_label ?? null,
      is_desktop: payload.is_desktop ?? null,
      pagina_url: payload.pagina_url ?? null,
      tipo: payload.tipo ?? null,
      tipo_label: payload.tipo_label ?? null,
      runtime: payload.runtime ?? null,
      platform_context: payload.platform_context ?? null,
    },
  };
}

export function sanitizeAppFeedbackForLog(payload) {
  return {
    id_local: payload?.id_local,
    tipo: payload?.tipo,
    tipo_label: payload?.tipo_label,
    severidade: payload?.severidade,
    severidade_label: payload?.severidade_label,
    runtime: payload?.runtime,
    tipo_feedback: payload?.tipo_feedback,
    origem: payload?.origem,
    pagina: payload?.pagina,
    rota: payload?.rota?.slice?.(0, 120),
    has_stack: Boolean(payload?.stack_erro),
    has_comment: Boolean(payload?.descricao || payload?.comentario),
  };
}
