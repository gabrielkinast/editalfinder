import {
  MSG_APP_FEEDBACK_SUCCESS_GMAIL,
  MSG_APP_FEEDBACK_SUCCESS_LOCAL,
  MSG_APP_FEEDBACK_SUCCESS_MAILTO,
  MSG_APP_FEEDBACK_FAILED,
} from '../../constants/appFeedbackConfig.js';
import { buildManualSupportInstructions } from './appFeedbackClipboard.js';
import {
  SUPPORT_EMAIL,
  buildSupportEmailBody,
  buildSupportEmailSubject,
} from './appFeedbackMailto.js';
import { sanitizePayloadForSupportEmail } from './appFeedbackSensitive.js';

export function buildSupportMailtoParts(payload = {}) {
  const safe = sanitizePayloadForSupportEmail(payload);
  const subject = buildSupportEmailSubject(safe);
  const body = buildSupportEmailBody(safe);
  return { subject, body };
}

function enrichSubmitResult(base, payload) {
  const mailtoParts = buildSupportMailtoParts(payload);
  return {
    ...base,
    support_email: SUPPORT_EMAIL,
    email_subject: mailtoParts.subject,
    email_body: mailtoParts.body,
    manual_report_text: buildManualSupportInstructions({
      supportEmail: SUPPORT_EMAIL,
      subject: mailtoParts.subject,
      body: mailtoParts.body,
    }),
  };
}

function successMessageForMethod(method) {
  if (method === 'gmail_compose') return MSG_APP_FEEDBACK_SUCCESS_GMAIL;
  return MSG_APP_FEEDBACK_SUCCESS_MAILTO;
}

/**
 * Orquestração testável: Gmail → mailto → fila local.
 * Edge Function / Supabase ficam opcionais (não chamados aqui).
 */
export async function executeAppFeedbackSubmit(payload, _options, deps) {
  const { openEmailComposer, openMailto, saveLocal, flushPending } = deps;
  const openComposer = openEmailComposer || openMailto;
  const mailtoParts = buildSupportMailtoParts(payload);

  const composerResult = await openComposer(payload);

  if (composerResult?.ok) {
    flushPending?.().catch(() => {});
    return enrichSubmitResult(
      {
        ok: true,
        status: 'opened_email_client',
        message: successMessageForMethod(composerResult.method),
        method: composerResult.method,
      },
      payload,
    );
  }

  try {
    saveLocal(payload, composerResult?.reason || 'email_composer_failed');
    return enrichSubmitResult(
      {
        ok: true,
        status: 'saved_local',
        fallback_reason: composerResult?.reason || 'email_composer_failed',
        message: MSG_APP_FEEDBACK_SUCCESS_LOCAL,
        pending: true,
      },
      payload,
    );
  } catch (localError) {
    return {
      ok: false,
      status: 'failed',
      fallback_reason: composerResult?.reason || 'email_composer_failed',
      error: composerResult?.gmailError || composerResult?.mailtoError || composerResult?.error,
      localError,
      message: MSG_APP_FEEDBACK_FAILED,
      support_email: SUPPORT_EMAIL,
      email_subject: mailtoParts.subject,
      email_body: mailtoParts.body,
    };
  }
}

/**
 * Flush da fila: tenta abrir mailto por item; remove os que abriram com sucesso.
 */
export async function executeFlushPendingAppFeedback(queue, _options, deps) {
  const { openEmailComposer, openMailto } = deps;
  const openComposer = openEmailComposer || openMailto;

  if (!queue.length) {
    return { ok: true, sent: 0, remaining: 0 };
  }

  let sent = 0;
  const remaining = [];

  for (const entry of queue) {
    try {
      const result = await openComposer(entry.payload);
      if (result?.ok) {
        sent += 1;
      } else {
        remaining.push({
          ...entry,
          attempts: (entry.attempts || 0) + 1,
          last_attempt_at: new Date().toISOString(),
          last_error_reason: result?.reason || 'email_composer_failed',
        });
      }
    } catch {
      remaining.push({
        ...entry,
        attempts: (entry.attempts || 0) + 1,
        last_attempt_at: new Date().toISOString(),
        last_error_reason: 'email_composer_failed',
      });
    }
  }

  return { ok: true, sent, remaining, flushed: sent };
}
