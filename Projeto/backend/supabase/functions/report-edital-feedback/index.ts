/**
 * Edge Function (esqueleto) — reporte de problema em edital.
 *
 * Deploy manual. Variáveis de ambiente (Supabase secrets):
 *   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (só no servidor)
 *   SUPPORT_EMAIL — destino do e-mail (padrão: editalfinder@gmail.com)
 *   RESEND_API_KEY | SENDGRID_API_KEY | … — provider (TODO)
 *
 * Não commitar credenciais.
 */

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

const ALLOWED_MOTIVOS = new Set([
  'link_quebrado',
  'nao_e_oportunidade',
  'edital_encerrado',
  'duplicado',
  'informacao_incorreta',
  'outro',
]);

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: CORS_HEADERS });
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'method_not_allowed' }), {
      status: 405,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }

  try {
    const body = await req.json();
    const motivo = String(body?.motivo || '');
    if (!ALLOWED_MOTIVOS.has(motivo)) {
      return new Response(JSON.stringify({ error: 'invalid_motivo' }), {
        status: 400,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    if (motivo === 'outro') {
      const c = String(body?.comentario || '').trim();
      if (c.length < 10) {
        return new Response(JSON.stringify({ error: 'comentario_required' }), {
          status: 400,
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
      }
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? '';
    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '';
    const supportEmail =
      Deno.env.get('SUPPORT_EMAIL') ??
      Deno.env.get('VITE_SUPPORT_EMAIL') ??
      'editalfinder@gmail.com';

    // TODO: validar JWT do Authorization header e resolver id_usuario

    if (supabaseUrl && serviceKey) {
      const admin = createClient(supabaseUrl, serviceKey);
      const row = {
        id_edital: body.id_edital ?? null,
        id_usuario: body.id_usuario ?? null,
        tipo_feedback: motivo,
        comentario: body.comentario ?? null,
        fonte_recurso: body.fonte_recurso ?? null,
        edital_titulo: body.titulo ?? null,
        edital_link: body.link ?? body.link_edital ?? null,
        extras: {
          payload_version: 1,
          motivo_label: body.motivo_label,
          status_prazo: body.status_prazo,
          validacao_status: body.validacao_status,
          qualidade_dado: body.qualidade_dado,
          extras_curadoria_front: body.extras_curadoria_front,
          extras_link_health: body.extras_link_health,
          current_url: body.current_url,
          user_agent: body.user_agent,
          auth_user_id: body.auth_user_id,
          email_usuario: body.email_usuario,
        },
      };

      const { error: insertErr } = await admin.from('edital_feedback').insert([row]);
      if (insertErr) {
        console.warn('[report-edital-feedback] insert skipped or failed', insertErr.message);
        // Tabela pode não existir ainda — não falhar o request se e-mail for enviado
      }
    }

    // TODO: enviar e-mail via Resend/SendGrid/SES usando body.email_subject / body.email_body
    if (!supportEmail) {
      console.warn('[report-edital-feedback] SUPPORT_EMAIL not configured — email skipped');
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('[report-edital-feedback]', e);
    return new Response(JSON.stringify({ error: 'internal_error' }), {
      status: 500,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }
});
