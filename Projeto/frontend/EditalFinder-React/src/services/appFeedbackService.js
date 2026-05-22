import { TABLE_APP_FEEDBACK, APP_FEEDBACK_PENDING_KEY } from '../constants/appFeedbackConfig';
import { buildAppFeedbackPayload, sanitizeAppFeedbackForLog } from '../utils/feedback/buildAppFeedbackPayload';
import { resolveAppUserId } from '../utils/appUserId';
import { logAppFeedback } from '../utils/feedback/appFeedbackLog';

export const MSG_APP_FEEDBACK_AUTH_LOADING = 'Carregando sua conta…';
export const MSG_APP_FEEDBACK_NOT_AUTHENTICATED = 'Entre na sua conta para enviar o relatório.';
export const MSG_APP_FEEDBACK_NO_PROFILE =
  'Não encontramos seu perfil interno. Saia e entre novamente.';
const ERR_GENERIC = 'Não foi possível enviar o relatório agora. Tente novamente.';

function loadPending() {
  try {
    const raw = localStorage.getItem(APP_FEEDBACK_PENDING_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function savePending(list) {
  try {
    localStorage.setItem(APP_FEEDBACK_PENDING_KEY, JSON.stringify(list.slice(0, 20)));
  } catch {
    /* ignore */
  }
}

export function savePendingAppFeedback(payload) {
  const list = loadPending();
  list.unshift({ ...payload, _pendingAt: new Date().toISOString() });
  savePending(list);
  logAppFeedback('pending_saved', sanitizeAppFeedbackForLog(payload));
}

/**
 * @param {object|null} appUser
 * @param {boolean} authenticated
 */
export function buildAppFeedbackRow(payload, appUser, authUserId = null) {
  const idUsuario = resolveAppUserId(appUser);
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
    comentario: payload.comentario ?? null,
    status: 'novo',
    prioridade: payload.tipo_feedback === 'erro_pagina' || payload.tipo_feedback === 'erro_global' ? 'alta' : 'normal',
    user_agent: payload.user_agent ?? null,
    app_version: payload.app_version ?? null,
    extras: payload.extras ?? {},
  };
}

/**
 * @param {object} payload — saída de buildAppFeedbackPayload
 * @param {{ appUser?: object|null; authenticated?: boolean; authLoading?: boolean; authUserId?: string|null }} [options]
 */
export async function createAppFeedback(payload, options = {}) {
  const { appUser = null, authenticated = false, authLoading = false, authUserId = null } = options;

  logAppFeedback('submit_start', sanitizeAppFeedbackForLog(payload));

  if (authLoading) {
    return { ok: false, error: MSG_APP_FEEDBACK_AUTH_LOADING, code: 'auth_loading' };
  }

  if (!authenticated && resolveAppUserId(appUser) == null) {
    return { ok: false, error: MSG_APP_FEEDBACK_NOT_AUTHENTICATED, code: 'not_authenticated' };
  }

  const { supabase, isSupabaseConfigured } = await import('./api');

  if (!isSupabaseConfigured) {
    savePendingAppFeedback(payload);
    return {
      ok: false,
      error: ERR_GENERIC,
      code: 'supabase_not_configured',
      pending: true,
    };
  }

  const row = buildAppFeedbackRow(payload, appUser, authUserId);

  const { data, error } = await supabase
    .from(TABLE_APP_FEEDBACK)
    .insert([row])
    .select('id_feedback')
    .single();

  if (error) {
    logAppFeedback('submit_db_error', {
      code: error.code,
      message: error.message,
    });
    savePendingAppFeedback(payload);
    return { ok: false, error: ERR_GENERIC, code: error.code || 'insert_failed', pending: true };
  }

  logAppFeedback('submit_success', { id_feedback: data?.id_feedback });
  return { ok: true, id_feedback: data?.id_feedback };
}

/**
 * @param {Error|unknown} error
 * @param {object} context
 */
export function createAppFeedbackFromError(error, context = {}) {
  const payload = buildAppFeedbackPayload({
    tipo: context.tipo || 'erro_global',
    origem: context.origem || 'user_report',
    pagina: context.pagina,
    componente: context.componente,
    acao: context.acao,
    error,
    errorInfo: context.errorInfo,
    comment: context.comment,
    extraContext: context.extraContext,
  });
  return payload;
}

/**
 * Reenvia fila local (best-effort).
 */
export async function flushPendingAppFeedback(options = {}) {
  const pending = loadPending();
  if (!pending.length) return { flushed: 0 };

  let flushed = 0;
  const remaining = [];

  for (const item of pending) {
    const { _pendingAt, ...payload } = item;
    const result = await createAppFeedback(payload, options);
    if (result.ok) flushed += 1;
    else remaining.push(item);
  }

  savePending(remaining);
  logAppFeedback('pending_flush', { flushed, remaining: remaining.length });
  return { flushed, remaining: remaining.length };
}
