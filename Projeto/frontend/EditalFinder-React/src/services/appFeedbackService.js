import {
  TABLE_APP_FEEDBACK,
  APP_FEEDBACK_EMAIL_FUNCTION,
  ENABLE_APP_FEEDBACK_MAILTO,
  MSG_APP_FEEDBACK_VALIDATION,
  MSG_APP_FEEDBACK_FAILED,
} from '../constants/appFeedbackConfig';
import {
  buildAppFeedbackPayload,
  validateAppFeedbackPayload,
  mapToRemoteAppFeedbackRow,
  sanitizeAppFeedbackForLog,
} from '../utils/feedback/appFeedbackPayload.js';
import {
  readAppFeedbackQueue,
  saveAppFeedbackLocal,
  writeAppFeedbackQueue,
} from '../utils/feedback/appFeedbackQueue.js';
import {
  openSupportEmailComposer,
  openSupportMailto,
} from '../utils/feedback/appFeedbackMailto.js';
import {
  classifyAppFeedbackRemoteError,
} from '../utils/feedback/postgrestFeedbackErrors.js';
import {
  executeAppFeedbackSubmit,
  executeFlushPendingAppFeedback,
} from '../utils/feedback/appFeedbackSubmitFlow.js';
import { logAppFeedback } from '../utils/feedback/appFeedbackLog';

function buildEmailInvokeBody(payload) {
  return {
    id_local: payload.id_local,
    tipo: payload.tipo ?? payload.tipo_feedback,
    tipo_label: payload.tipo_label ?? null,
    tipo_feedback: payload.tipo_feedback,
    categoria: payload.categoria,
    runtime: payload.runtime ?? null,
    platform_context: payload.platform_context ?? null,
    severidade: payload.severidade,
    descricao: payload.descricao ?? payload.comentario,
    comentario: payload.comentario ?? payload.descricao,
    email_contato: payload.email_contato ?? null,
    pagina_url: payload.pagina_url ?? payload.metadata?.pagina_url ?? null,
    rota: payload.rota,
    pagina: payload.pagina,
    origem: payload.origem,
    user_agent: payload.user_agent,
    app_version: payload.app_version,
    app_env: payload.app_env,
    is_desktop: payload.is_desktop,
    created_at: payload.created_at,
    mensagem_erro: payload.mensagem_erro,
    stack_erro: payload.stack_erro,
    metadata: payload.metadata ?? {},
  };
}

/**
 * Edge Function + Resend — opcional/futuro (não é o fluxo principal).
 */
export async function sendAppFeedbackEmail(payload) {
  const { supabase, isSupabaseConfigured } = await import('./api');

  if (!isSupabaseConfigured) {
    const err = new Error('Supabase not configured');
    err.code = 'supabase_not_configured';
    throw err;
  }

  const { data, error } = await supabase.functions.invoke(APP_FEEDBACK_EMAIL_FUNCTION, {
    body: buildEmailInvokeBody(payload),
  });

  if (error) throw error;

  if (!data?.ok) {
    const err = new Error(data?.message || 'Feedback email failed');
    err.code = data?.status || 'email_failed';
    throw err;
  }

  return data;
}

/**
 * Insert remoto em app_feedback (opcional / best-effort).
 */
export async function sendAppFeedbackRemote(payload, options = {}) {
  const { appUser = null, authUserId = null } = options;
  const { supabase, isSupabaseConfigured } = await import('./api');

  if (!isSupabaseConfigured) {
    const err = new Error('Supabase not configured');
    err.code = 'supabase_not_configured';
    throw err;
  }

  const row = mapToRemoteAppFeedbackRow(payload, appUser, authUserId);
  const { data, error } = await supabase
    .from(TABLE_APP_FEEDBACK)
    .insert([row])
    .select('id_feedback')
    .single();

  if (error) throw error;
  return data;
}

export { saveAppFeedbackLocal };

const submitDeps = {
  openEmailComposer: ENABLE_APP_FEEDBACK_MAILTO
    ? openSupportEmailComposer
    : async () => ({ ok: false, reason: 'email_composer_disabled' }),
  saveLocal: saveAppFeedbackLocal,
  flushPending: (options) => flushPendingAppFeedback(options),
};

/**
 * Função principal — UI deve chamar apenas esta.
 * Prioridade: Gmail Web Compose → mailto → fila local. Edge Function/Supabase não são obrigatórios.
 */
export async function submitAppFeedback(input = {}, context = {}, options = {}) {
  const payload = buildAppFeedbackPayload(input ?? {}, context ?? {});
  const validation = validateAppFeedbackPayload(payload);

  if (!validation.valid) {
    if (import.meta.env.DEV) {
      logAppFeedback('submit_invalid_payload', { errors: validation.errors });
    }
    return {
      ok: false,
      status: 'invalid_payload',
      errors: validation.errors,
      message: MSG_APP_FEEDBACK_VALIDATION,
      technicalReason: validation.errors,
    };
  }

  logAppFeedback('submit_start', sanitizeAppFeedbackForLog(payload));

  const result = await executeAppFeedbackSubmit(payload, options, submitDeps);

  if (result.ok) {
    logAppFeedback('submit_success', {
      status: result.status,
      id_local: payload.id_local,
      method: result.method,
    });
  } else if (import.meta.env.DEV) {
    logAppFeedback('submit_failed', {
      status: result.status,
      reason: result.reason,
    });
  }

  return result;
}

/** @deprecated Use submitAppFeedback — alias de compatibilidade. */
export async function createAppFeedback(payload, options = {}) {
  return submitAppFeedback(
    {
      tipo: payload?.tipo_feedback ?? payload?.tipo,
      descricao: payload?.comentario ?? payload?.descricao,
      comment: payload?.comentario ?? payload?.descricao,
    },
    { payload },
    options,
  );
}

export function createAppFeedbackFromError(error, context = {}) {
  const ctx = context ?? {};
  return buildAppFeedbackPayload({
    tipo: ctx.tipo || 'browser_error',
    origem: ctx.origem || 'user_report',
    pagina: ctx.pagina,
    componente: ctx.componente,
    acao: ctx.acao,
    error,
    errorInfo: ctx.errorInfo,
    comment: ctx.comment,
    extraContext: ctx.extraContext,
  });
}

/** @deprecated Use saveAppFeedbackLocal via queue module. */
export function savePendingAppFeedback(payload) {
  saveAppFeedbackLocal(payload, 'legacy_api');
}

/**
 * Reenvia fila local — tenta abrir mailto por item pendente.
 */
export async function flushPendingAppFeedback(_options = {}) {
  const queue = readAppFeedbackQueue();
  const flushResult = await executeFlushPendingAppFeedback(queue, {}, {
    openEmailComposer: openSupportEmailComposer,
  });

  writeAppFeedbackQueue(flushResult.remaining);
  logAppFeedback('pending_flush', {
    sent: flushResult.sent,
    remaining: flushResult.remaining.length,
    channel: 'mailto',
  });

  return flushResult;
}

/** Compat: buildAppFeedbackRow para imports antigos. */
export function buildAppFeedbackRow(payload, appUser, authUserId = null) {
  return mapToRemoteAppFeedbackRow(payload, appUser, authUserId);
}

export {
  executeAppFeedbackSubmit,
  executeFlushPendingAppFeedback,
  openSupportEmailComposer,
  openSupportMailto,
};
