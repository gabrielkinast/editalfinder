/** Lógica pura compartilhada (Edge Function + testes Node). */

export const FEEDBACK_DESC_MIN = 10;
export const FEEDBACK_DESC_MAX = 5000;

export function truncate(str, max) {
  const s = String(str ?? '');
  if (s.length <= max) return s;
  return `${s.slice(0, max)}…`;
}

export function isValidEmail(value) {
  if (!value) return true;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value).trim());
}

export function validateFeedbackPayload(payload) {
  const errors = {};
  const descricao = String(payload?.descricao ?? payload?.comentario ?? '').trim();

  if (!descricao || descricao.length < FEEDBACK_DESC_MIN) {
    errors.descricao = 'Descrição muito curta.';
  }

  if (descricao.length > FEEDBACK_DESC_MAX) {
    errors.descricao = 'Descrição muito longa.';
  }

  if (payload?.email_contato && !isValidEmail(payload.email_contato)) {
    errors.email_contato = 'E-mail inválido.';
  }

  if (payload?.metadata != null && typeof payload.metadata !== 'object') {
    errors.metadata = 'Metadata inválida.';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}

function shortRoute(rota) {
  if (!rota) return '—';
  const s = String(rota).trim();
  const pathOnly = s.split('?')[0].split('#')[0];
  return pathOnly.slice(0, 120) || '—';
}

function runtimeEnvLabel(p) {
  if (p.runtime === 'desktop_tauri' || p.is_desktop) return 'Desktop/Tauri';
  return 'Navegador';
}

function subjectEnvSegment(p) {
  if (p.runtime === 'desktop_tauri' || p.is_desktop) return 'Desktop/EXE';
  return 'Navegador';
}

export function buildFeedbackEmailSubject(p) {
  const route = shortRoute(p.rota);
  const env = subjectEnvSegment(p);
  const exportTypes = ['pdf_export_error', 'spreadsheet_export_error'];
  if (exportTypes.includes(p.tipo)) {
    const label = p.tipo === 'pdf_export_error' ? 'PDF export' : 'Planilha export';
    return `[EditalFinder] Reporte — ${label} — ${route}`;
  }
  return `[EditalFinder] Reporte — ${env} — ${route}`;
}

export function sanitizeFeedbackPayload(payload) {
  const descricao = truncate(
    String(payload?.descricao ?? payload?.comentario ?? '').trim(),
    FEEDBACK_DESC_MAX,
  );

  const platformContext =
    payload?.platform_context && typeof payload.platform_context === 'object'
      ? payload.platform_context
      : null;

  return {
    id_local: truncate(payload?.id_local, 120),
    tipo: truncate(payload?.tipo ?? payload?.tipo_feedback ?? 'other', 80),
    tipo_label: truncate(payload?.tipo_label, 200),
    tipo_feedback: truncate(payload?.tipo_feedback ?? payload?.tipo ?? 'outro', 80),
    categoria: truncate(payload?.categoria ?? 'geral', 80),
    severidade: truncate(payload?.severidade ?? 'normal', 40),
    descricao,
    comentario: descricao,
    email_contato: payload?.email_contato ? String(payload.email_contato).trim().slice(0, 200) : null,
    pagina_url: truncate(payload?.pagina_url ?? payload?.metadata?.pagina_url, 500),
    rota: truncate(payload?.rota, 500),
    pagina: truncate(payload?.pagina, 120),
    origem: truncate(payload?.origem, 80),
    user_agent: truncate(payload?.user_agent, 500),
    app_version: truncate(payload?.app_version, 80),
    app_env: truncate(payload?.app_env, 40),
    is_desktop: Boolean(payload?.is_desktop),
    runtime: truncate(payload?.runtime, 40),
    platform_context: platformContext,
    created_at: truncate(payload?.created_at ?? new Date().toISOString(), 40),
    mensagem_erro: truncate(payload?.mensagem_erro, 2000),
    stack_erro: truncate(payload?.stack_erro, 4000),
    metadata:
      payload?.metadata && typeof payload.metadata === 'object' && !Array.isArray(payload.metadata)
        ? payload.metadata
        : {},
  };
}

export function buildFeedbackEmail(payload) {
  const p = sanitizeFeedbackPayload(payload);
  const subject = buildFeedbackEmailSubject(p);
  const ambiente = runtimeEnvLabel(p);

  const textLines = [
    'Novo problema reportado no EditalFinder',
    '',
    `Tipo do problema: ${p.tipo_label || p.tipo || p.tipo_feedback}`,
    `Categoria: ${p.categoria}`,
    `Ambiente detectado: ${ambiente}`,
    `Runtime: ${p.runtime || '—'}`,
    `Severidade: ${p.severidade}`,
    `Data: ${p.created_at}`,
    `Versão: ${p.app_version || '—'}`,
    `App env: ${p.app_env || '—'}`,
    `Origem: ${p.origem || '—'}`,
    `Rota: ${p.rota || '—'}`,
    `Página: ${p.pagina || '—'}`,
    `URL: ${p.pagina_url || '—'}`,
    `Contato: ${p.email_contato || '—'}`,
    '',
    'Descrição:',
    p.descricao,
    '',
    'Contexto técnico:',
    `- User agent: ${p.user_agent || '—'}`,
    `- id_local: ${p.id_local || '—'}`,
  ];

  if (p.platform_context) {
    textLines.push(
      `- platform_context: ${JSON.stringify(p.platform_context).slice(0, 1500)}`,
    );
  }

  if (p.mensagem_erro) {
    textLines.push(`- Erro capturado: ${p.mensagem_erro}`);
  }

  if (p.stack_erro) {
    textLines.push(`- Stack: ${p.stack_erro.slice(0, 2000)}`);
  }

  if (p.metadata && Object.keys(p.metadata).length > 0) {
    textLines.push(`- metadata: ${JSON.stringify(p.metadata).slice(0, 3000)}`);
  }

  const text = textLines.join('\n');
  const html = `<pre style="font-family:ui-monospace,monospace;white-space:pre-wrap">${escapeHtml(text)}</pre>`;

  return { subject, text, html, sanitized: p };
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
