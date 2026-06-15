import { openExternalUrl } from '../externalActions/openExternalUrl.js';
import {
  formatFeedbackDateForEmail,
  getCategoryLabel,
  getProblemTypeLabel,
  normalizeRouteForEmail,
} from './appFeedbackLabels.js';
import { getFeedbackSeverity } from './appFeedbackSeverity.js';
import { getRuntimeDisplayLabel } from './runtimeContext.js';
import { REPORT_GUIDANCE_EMAIL_BODY } from './appFeedbackGuidance.js';
import {
  redactSensitiveFeedbackValue,
  sanitizePayloadForSupportEmail,
} from './appFeedbackSensitive.js';

export const SUPPORT_EMAIL = 'Suporte.EditalFinder@gmail.com';

export const GMAIL_COMPOSE_BASE = 'https://mail.google.com/mail/';
export const GMAIL_BODY_MAX = 6000;
export const GMAIL_COMPOSE_URL_MAX = 12000;

const MAILTO_URL_MAX = 7500;
const MAILTO_BODY_MAX = 6500;
const FIELD_TRUNCATE = 1000;
const USER_AGENT_MAX = 400;

export function truncateMailtoText(value, max = FIELD_TRUNCATE) {
  const text = String(value ?? '');
  if (text.length <= max) return text;
  return `${text.slice(0, max)}... [truncado]`;
}

function redactSensitive(value, key = '') {
  if (value == null || value === '') return '';
  return String(redactSensitiveFeedbackValue(key, value));
}

function ambienteLabel(payload) {
  if (payload.runtime === 'desktop_tauri' || payload.is_desktop) return 'Desktop/EXE (Tauri)';
  return 'Navegador (Web)';
}

/**
 * Assunto do e-mail — severidade + tipo + rota (FRONTEND 1.1C.5).
 */
export function buildSupportEmailSubject(payload = {}) {
  const safe = payload && typeof payload === 'object' ? payload : {};
  const severity = getFeedbackSeverity(safe.severidade);
  const typeLabel = getProblemTypeLabel(safe) || 'Problema reportado';
  const route = normalizeRouteForEmail(safe.rota);

  return `[EditalFinder][${severity.emailPrefix}] Reporte — ${typeLabel} — ${route}`;
}

/**
 * Corpo em texto plano (sem segredos).
 */
export function buildSupportEmailBody(payload = {}, options = {}) {
  const maxBody = options.maxBody ?? MAILTO_BODY_MAX;
  const safe = sanitizePayloadForSupportEmail(payload);
  const ctx = safe.platform_context && typeof safe.platform_context === 'object'
    ? safe.platform_context
    : {};

  const severity = getFeedbackSeverity(safe.severidade);
  const typeLabel = getProblemTypeLabel(safe);
  const categoryLabel = safe.categoria_label || getCategoryLabel(safe.categoria);
  const route = normalizeRouteForEmail(safe.rota);
  const paginaLabel = safe.pagina ? String(safe.pagina).replace(/_/g, ' ') : '—';

  const lines = [
    'Reporte de problema — EditalFinder',
    '',
    'Resumo',
    '------',
    `Severidade: ${redactSensitive(safe.severidade_label || severity.label, 'severidade_label')}`,
    `Tipo do problema: ${redactSensitive(typeLabel, 'tipo_label')}`,
    `Categoria: ${redactSensitive(categoryLabel, 'categoria_label')}`,
    `Data: ${formatFeedbackDateForEmail(safe.created_at || new Date().toISOString())}`,
    `Ambiente: ${ambienteLabel(safe)}`,
    `Versão: ${redactSensitive(safe.app_version || '—', 'app_version')}`,
    '',
    'Descrição',
    '---------',
    redactSensitive(safe.descricao || safe.comentario || '—', 'descricao'),
    '',
    'Localização',
    '-----------',
    `Página: ${redactSensitive(paginaLabel, 'pagina')}`,
    `Rota: ${redactSensitive(route, 'rota')}`,
    `URL: ${redactSensitive(safe.pagina_url || safe.metadata?.pagina_url || '—', 'pagina_url')}`,
    '',
    'Contexto técnico',
    '----------------',
    `Runtime: ${redactSensitive(safe.runtime || ctx.runtime || '—', 'runtime')}`,
    `Desktop/EXE: ${safe.is_desktop ? 'Sim' : 'Não'}`,
    `Sistema/navegador: ${truncateMailtoText(redactSensitive(safe.user_agent || ctx.user_agent, 'user_agent'), USER_AGENT_MAX)}`,
    `Plataforma: ${truncateMailtoText(redactSensitive(ctx.platform || '—', 'platform'), 120)}`,
    `ID local: ${redactSensitive(safe.id_local || '—', 'id_local')}`,
  ];

  if (safe.mensagem_erro) {
    lines.push('', 'Erro capturado:', truncateMailtoText(redactSensitive(safe.mensagem_erro, 'mensagem_erro'), 800));
  }

  if (safe.metadata && typeof safe.metadata === 'object') {
    const metaSummary = {
      origem: safe.origem,
      componente: safe.componente,
      acao: safe.acao,
    };
    lines.push('', 'Metadata (resumo):', truncateMailtoText(JSON.stringify(metaSummary), 600));
  }

  lines.push(
    '',
    'Observação',
    '----------',
    'Este e-mail foi gerado automaticamente pelo sistema de reporte do EditalFinder.',
    'Revise o conteúdo e clique em Enviar no Gmail ou no seu cliente de e-mail.',
    REPORT_GUIDANCE_EMAIL_BODY,
  );

  let body = lines.join('\n');
  if (body.length > maxBody) {
    body = `${body.slice(0, maxBody)}... [corpo truncado por limite mailto]`;
  }
  return body;
}

/**
 * Monta URL mailto: apenas para o endereço de suporte fixo.
 */
export function buildSupportMailtoUrl(payload = {}) {
  const safe = sanitizePayloadForSupportEmail(payload);
  const subject = buildSupportEmailSubject(safe);
  let body = buildSupportEmailBody(safe);

  const encodePair = (subj, bod) => {
    const params = new URLSearchParams();
    params.set('subject', subj);
    params.set('body', bod);
    return `mailto:${SUPPORT_EMAIL}?${params.toString()}`;
  };

  let url = encodePair(subject, body);

  while (url.length > MAILTO_URL_MAX && body.length > 200) {
    body = buildSupportEmailBody(safe, { maxBody: Math.floor(body.length * 0.85) });
    url = encodePair(subject, body);
  }

  const prefix = `mailto:${SUPPORT_EMAIL}`;
  if (!url.toLowerCase().startsWith(prefix.toLowerCase())) return null;

  return url;
}

/**
 * Monta URL do Gmail Web Compose (HTTPS).
 */
export function buildGmailComposeUrl(payload = {}) {
  const safe = sanitizePayloadForSupportEmail(payload);
  const subject = buildSupportEmailSubject(safe);
  let body = buildSupportEmailBody(safe, { maxBody: GMAIL_BODY_MAX });

  const buildUrl = (bod) => {
    const params = new URLSearchParams({
      view: 'cm',
      fs: '1',
      to: SUPPORT_EMAIL,
      su: subject,
      body: bod,
    });
    return `${GMAIL_COMPOSE_BASE}?${params.toString()}`;
  };

  let url = buildUrl(body);
  while (url.length > GMAIL_COMPOSE_URL_MAX && body.length > 200) {
    body = buildSupportEmailBody(safe, { maxBody: Math.floor(body.length * 0.85) });
    url = buildUrl(body);
  }

  return url;
}

/**
 * Fluxo principal: Gmail Web Compose → mailto → falha.
 * @param {object} [deps] — injeção para testes (`openExternalUrl`).
 */
export async function openSupportEmailComposer(payload = {}, deps = {}) {
  const openUrl = deps.openExternalUrl || openExternalUrl;
  const safe = sanitizePayloadForSupportEmail(payload);
  let gmailError = null;
  let mailtoError = null;

  const gmailUrl = buildGmailComposeUrl(safe);
  try {
    const gmailOpened = await openUrl(gmailUrl, {
      actionType: 'support_feedback_gmail',
    });
    if (gmailOpened) {
      return { ok: true, method: 'gmail_compose', url: gmailUrl };
    }
    gmailError = new Error('gmail_open_failed');
  } catch (error) {
    gmailError = error;
  }

  const mailtoUrl = buildSupportMailtoUrl(safe);
  if (!mailtoUrl) {
    return {
      ok: false,
      reason: 'email_composer_failed',
      gmailError,
      mailtoError: new Error('invalid_mailto_url'),
    };
  }

  try {
    const mailtoOpened = await openUrl(mailtoUrl, {
      allowMailto: true,
      actionType: 'support_feedback_mailto',
    });
    if (mailtoOpened) {
      return { ok: true, method: 'mailto', url: mailtoUrl };
    }
    mailtoError = new Error('mailto_open_failed');
  } catch (error) {
    mailtoError = error;
  }

  return {
    ok: false,
    reason: 'email_composer_failed',
    gmailError,
    mailtoError,
  };
}

/**
 * @deprecated Use openSupportEmailComposer — mantido para compatibilidade.
 */
export async function openSupportMailto(payload = {}) {
  const mailtoUrl = buildSupportMailtoUrl(payload);
  if (!mailtoUrl) {
    return { ok: false, reason: 'invalid_mailto_url' };
  }

  try {
    const opened = await openExternalUrl(mailtoUrl, {
      allowMailto: true,
      actionType: 'support_feedback_mailto_legacy',
    });
    if (opened) {
      return { ok: true, method: 'mailto' };
    }
    return { ok: false, reason: 'mailto_failed' };
  } catch (error) {
    return { ok: false, reason: 'mailto_failed', error };
  }
}

export { getRuntimeDisplayLabel };
