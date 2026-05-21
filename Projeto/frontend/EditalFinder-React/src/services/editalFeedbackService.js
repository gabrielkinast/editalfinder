import { supabase, isSupabaseConfigured } from './api';
import {
  EDITAL_FEEDBACK_ENDPOINT,
  EDITAL_FEEDBACK_MOCK_DEV,
  SUPPORT_EMAIL,
} from '../config/env';
import { TABLE_EDITAL_FEEDBACK } from '../constants/editalFeedbackConfig';
import { buildEditalFeedbackEmailBody, buildEditalFeedbackEmailSubject } from './editalFeedbackEmailTemplate';
import { appUserDiagKeys, resolveAppUserId } from '../utils/appUserId';
import { logEditalFeedback } from '../utils/edital/editalFeedbackLog';
import { sanitizeEditalFeedbackForLog } from '../utils/edital/buildEditalFeedbackPayload';

export const MSG_FEEDBACK_AUTH_LOADING = 'Carregando sua conta…';
export const MSG_FEEDBACK_NOT_AUTHENTICATED = 'Entre na sua conta para reportar problemas.';
export const MSG_FEEDBACK_NO_INTERNAL_PROFILE =
  'Não encontramos seu perfil interno. Saia e entre novamente para continuar.';
const ERR_GENERIC = 'Não foi possível enviar o reporte agora. Tente novamente.';
const ERR_NETWORK = 'Não foi possível enviar o reporte agora. Tente novamente.';
const ERR_SUPABASE = 'Não foi possível enviar o reporte agora. Tente novamente.';

function endpointConfigured() {
  return Boolean(EDITAL_FEEDBACK_ENDPOINT && String(EDITAL_FEEDBACK_ENDPOINT).trim());
}

/** @deprecated Use resolveAppUserId — alias para testes/imports antigos. */
export function resolveFeedbackAppUserId(appUser) {
  return resolveAppUserId(appUser);
}

/**
 * Diagnóstico DEV no submit (sem tokens).
 * @param {object|null} appUser
 * @param {boolean} authenticated
 */
export function logFeedbackSubmitAuthDiag(appUser, authenticated) {
  const authUserId = appUser?.auth_user_id ?? null;
  const looksLikeUuid =
    typeof authUserId === 'string' &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(authUserId);

  logEditalFeedback('submit_auth_diag', {
    has_auth_user: !!appUser,
    authenticated: !!authenticated,
    auth_user_id: authUserId,
    looks_like_auth_uuid: looksLikeUuid,
    appUser_id_usuario: resolveAppUserId(appUser),
    appUser_keys: appUserDiagKeys(appUser),
  });
}

function resolveSubmitUserError(appUser, authenticated, authLoading) {
  if (authLoading) {
    return { error: MSG_FEEDBACK_AUTH_LOADING, code: 'auth_loading' };
  }
  if (resolveAppUserId(appUser) != null) {
    return null;
  }
  logEditalFeedback('missing_internal_profile', {
    authenticated: !!authenticated,
    appUser_id_usuario: appUser?.id_usuario ?? null,
    appUser_keys: appUserDiagKeys(appUser),
  });
  if (!authenticated) {
    return { error: MSG_FEEDBACK_NOT_AUTHENTICATED, code: 'not_authenticated' };
  }
  return { error: MSG_FEEDBACK_NO_INTERNAL_PROFILE, code: 'missing_internal_profile' };
}

/**
 * @param {string} motivo
 * @returns {'alta'|'normal'}
 */
export function prioridadeFromMotivo(motivo) {
  if (motivo === 'link_quebrado' || motivo === 'nao_e_oportunidade') return 'alta';
  return 'normal';
}

function pickEditalLink(payload) {
  return payload?.link ?? payload?.link_edital ?? payload?.url_documento ?? payload?.pdf_url ?? null;
}

/** Payload seguro para coluna extras (sem tokens). */
function buildExtrasJson(payload) {
  const {
    id_edital,
    titulo,
    fonte_recurso,
    fonte,
    link,
    link_edital,
    pdf_url,
    url_documento,
    prazo_envio,
    status_prazo,
    validacao_status,
    qualidade_dado,
    motivo,
    motivo_label,
    comentario,
    current_url,
    user_agent,
    created_at,
    extras_curadoria_front,
    extras_link_health,
    nome_email,
    email_usuario,
    auth_user_id,
  } = payload || {};

  return {
    payload_original: {
      id_edital,
      titulo,
      fonte_recurso,
      fonte,
      link,
      link_edital,
      pdf_url,
      url_documento,
      prazo_envio,
      status_prazo,
      validacao_status,
      qualidade_dado,
      motivo,
      motivo_label,
      comentario,
      current_url,
      user_agent,
      created_at,
      extras_curadoria_front,
      extras_link_health,
      auth_user_id,
      nome_email,
      email_usuario,
    },
    current_url: current_url ?? null,
    user_agent: user_agent ?? null,
    link_health: extras_link_health ?? null,
    curadoria_front: extras_curadoria_front ?? null,
    support_email: SUPPORT_EMAIL,
  };
}

/**
 * @param {Record<string, unknown>} payload
 * @param {object|null|undefined} appUser
 */
export function buildEditalFeedbackRow(payload, appUser) {
  const idUsuario = resolveFeedbackAppUserId(appUser);
  return {
    id_edital: payload.id_edital ?? null,
    id_usuario: idUsuario,
    tipo_feedback: payload.motivo,
    comentario: payload.comentario || null,
    status: 'novo',
    prioridade: prioridadeFromMotivo(String(payload.motivo || '')),
    fonte_recurso: payload.fonte_recurso ?? null,
    edital_titulo: payload.titulo ?? null,
    edital_link: pickEditalLink(payload),
    extras: buildExtrasJson(payload),
  };
}

function logSupabaseError(scope, error) {
  logEditalFeedback('submit_db_error', {
    scope,
    code: error?.code ?? null,
    message: error?.message ?? null,
    details: error?.details ?? null,
    hint: error?.hint ?? null,
  });
  if (import.meta.env.DEV && error) {
    console.error(`[edital-feedback] ${scope}`, {
      code: error.code,
      message: error.message,
      details: error.details,
      hint: error.hint,
    });
  }
}

async function submitViaEndpoint(payload) {
  const url = String(EDITAL_FEEDBACK_ENDPOINT).trim();
  const body = {
    ...payload,
    email_subject: buildEditalFeedbackEmailSubject(payload),
    email_body: buildEditalFeedbackEmailBody(payload),
  };

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    logEditalFeedback('submit_error', {
      channel: 'endpoint',
      status: res.status,
      ...sanitizeEditalFeedbackForLog(payload),
      detail: text.slice(0, 200),
    });
    return { ok: false, error: ERR_NETWORK, code: `http_${res.status}` };
  }

  logEditalFeedback('submit_success', { channel: 'endpoint', ...sanitizeEditalFeedbackForLog(payload) });
  return { ok: true, channel: 'endpoint' };
}

async function submitViaDatabase(payload, appUser) {
  const idUsuario = resolveAppUserId(appUser);
  if (idUsuario == null) {
    logEditalFeedback('missing_internal_profile', sanitizeEditalFeedbackForLog(payload));
    return { ok: false, error: MSG_FEEDBACK_NO_INTERNAL_PROFILE, code: 'missing_internal_profile' };
  }

  if (!isSupabaseConfigured) {
    logEditalFeedback('submit_db_error', { scope: 'supabase_not_configured' });
    return { ok: false, error: ERR_SUPABASE, code: 'supabase_not_configured' };
  }

  const row = buildEditalFeedbackRow(payload, appUser);

  logEditalFeedback('submit_db_start', {
    ...sanitizeEditalFeedbackForLog(payload),
    id_usuario: idUsuario,
    tipo_feedback: row.tipo_feedback,
    prioridade: row.prioridade,
  });

  const { data, error } = await supabase
    .from(TABLE_EDITAL_FEEDBACK)
    .insert([row])
    .select('id_feedback')
    .single();

  if (error) {
    logSupabaseError('insert', error);
    return { ok: false, error: ERR_GENERIC, code: error.code || 'insert_failed' };
  }

  logEditalFeedback('submit_db_success', {
    ...sanitizeEditalFeedbackForLog(payload),
    id_feedback: data?.id_feedback ?? null,
  });

  return { ok: true, channel: 'supabase', id_feedback: data?.id_feedback ?? null };
}

/**
 * Envia reporte de problema em edital.
 * Prioridade: endpoint HTTP (se configurado) → insert Supabase → mock DEV.
 *
 * @param {Record<string, unknown>} payload — de buildEditalFeedbackPayload
 * @param {{ appUser?: object|null; authenticated?: boolean; authLoading?: boolean }} [options]
 * @returns {Promise<{ ok: boolean; error?: string; code?: string; mock?: boolean; channel?: string; id_feedback?: string }>}
 */
export async function submitEditalFeedback(payload, options = {}) {
  const { appUser = null, authenticated = false, authLoading = false } = options;

  logEditalFeedback('submit_start', sanitizeEditalFeedbackForLog(payload));
  logFeedbackSubmitAuthDiag(appUser, authenticated);

  const userErr = resolveSubmitUserError(appUser, authenticated, authLoading);
  if (userErr) {
    return { ok: false, ...userErr };
  }

  try {
    if (endpointConfigured()) {
      return await submitViaEndpoint(payload);
    }

    if (isSupabaseConfigured) {
      return await submitViaDatabase(payload, appUser);
    }

    if (import.meta.env.DEV && EDITAL_FEEDBACK_MOCK_DEV) {
      logEditalFeedback('submit_success', { ...sanitizeEditalFeedbackForLog(payload), mock: true });
      return { ok: true, mock: true, channel: 'mock' };
    }

    logEditalFeedback('submit_db_error', { scope: 'no_channel' });
    return { ok: false, error: ERR_SUPABASE, code: 'no_channel' };
  } catch (e) {
    logEditalFeedback('submit_error', {
      ...sanitizeEditalFeedbackForLog(payload),
      message: e?.message || String(e),
    });
    return { ok: false, error: ERR_GENERIC, code: 'unexpected_error' };
  }
}
