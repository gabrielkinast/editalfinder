/**
 * Edge Function — envio seguro de feedback geral do app por e-mail.
 *
 * Secrets (Supabase Dashboard → Edge Functions):
 *   RESEND_API_KEY          — obrigatório para envio real
 *   FEEDBACK_EMAIL_TO       — default: editalfinder@gmail.com
 *   FEEDBACK_EMAIL_FROM     — remetente verificado no provedor
 *
 * Deploy: supabase functions deploy send-app-feedback-email
 */

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import {
  buildFeedbackEmail,
  validateFeedbackPayload,
} from '../_shared/appFeedbackEmailLogic.js';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

function json(body: Record<string, unknown>, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  });
}

function serializeSafeError(error: unknown) {
  if (error instanceof Error) return { message: error.message, name: error.name };
  return { message: String(error) };
}

async function sendEmailViaResend(params: {
  to: string;
  from: string;
  subject: string;
  text: string;
  html: string;
}) {
  const apiKey = Deno.env.get('RESEND_API_KEY') ?? '';
  if (!apiKey) {
    throw new Error('RESEND_API_KEY not configured');
  }

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: params.from,
      to: [params.to],
      subject: params.subject,
      text: params.text,
      html: params.html,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Resend API ${response.status}: ${detail.slice(0, 500)}`);
  }

  return response.json();
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: CORS_HEADERS });
  }

  if (req.method !== 'POST') {
    return json({ ok: false, status: 'method_not_allowed', message: 'Method not allowed' }, 405);
  }

  let payload: Record<string, unknown>;

  try {
    payload = await req.json();
  } catch {
    return json({ ok: false, status: 'invalid_json', message: 'Invalid JSON body' }, 400);
  }

  const validation = validateFeedbackPayload(payload);
  if (!validation.valid) {
    return json(
      {
        ok: false,
        status: 'invalid_payload',
        errors: validation.errors,
        message: 'Invalid feedback payload',
      },
      400,
    );
  }

  const emailContent = buildFeedbackEmail(payload);
  const to =
    Deno.env.get('FEEDBACK_EMAIL_TO') ??
    Deno.env.get('SUPPORT_EMAIL') ??
    'editalfinder@gmail.com';
  const from =
    Deno.env.get('FEEDBACK_EMAIL_FROM') ??
    Deno.env.get('RESEND_FROM') ??
    'EditalFinder <onboarding@resend.dev>';

  try {
    await sendEmailViaResend({
      to,
      from,
      subject: emailContent.subject,
      text: emailContent.text,
      html: emailContent.html,
    });

    return json({
      ok: true,
      status: 'sent_email',
      message: 'Feedback email sent.',
    });
  } catch (error) {
    console.error('send-app-feedback-email failed', serializeSafeError(error));
    return json(
      {
        ok: false,
        status: 'email_failed',
        message: 'Could not send feedback email.',
      },
      502,
    );
  }
});
