import { SUPPORT_EMAIL } from '../config/env';

/**
 * Template de e-mail para suporte (Edge Function / backend).
 * Não envia e-mail no browser — apenas formata texto.
 * Destino padrão: SUPPORT_EMAIL (VITE_SUPPORT_EMAIL ou editalfinder@gmail.com).
 */
export function getSupportEmailForFeedback() {
  return SUPPORT_EMAIL;
}

export function buildEditalFeedbackEmailSubject(payload) {
  const label = payload?.motivo_label || payload?.motivo || 'problema';
  return `[EditalFinder] Reporte de problema em edital: ${label}`;
}

/**
 * @param {Record<string, unknown>} payload
 * @returns {string}
 */
export function buildEditalFeedbackEmailBody(payload) {
  const p = payload || {};
  const cur = p.extras_curadoria_front;
  const lh = p.extras_link_health;

  return [
    'Novo reporte de problema em edital',
    '',
    `Destino suporte: ${getSupportEmailForFeedback()}`,
    '',
    'Usuário:',
    `- Nome/e-mail: ${p.nome_email ?? p.email_usuario ?? '—'}`,
    `- id_usuario: ${p.id_usuario ?? '—'}`,
    `- auth_user_id: ${p.auth_user_id ?? '—'}`,
    '',
    'Edital:',
    `- id_edital: ${p.id_edital ?? '—'}`,
    `- Título: ${p.titulo ?? '—'}`,
    `- Fonte: ${p.fonte ?? '—'}`,
    `- Fonte recurso: ${p.fonte_recurso ?? '—'}`,
    `- Link: ${p.link ?? p.link_edital ?? '—'}`,
    `- PDF: ${p.pdf_url ?? '—'}`,
    `- URL documento: ${p.url_documento ?? '—'}`,
    `- Prazo: ${p.prazo_envio ?? '—'}`,
    `- Status prazo: ${p.status_prazo ?? '—'}`,
    `- Validação: ${p.validacao_status ?? '—'}`,
    `- Qualidade: ${p.qualidade_dado ?? '—'}`,
    '',
    'Reporte:',
    `- Motivo: ${p.motivo_label ?? p.motivo ?? '—'}`,
    `- Comentário: ${p.comentario ?? '(sem comentário)'}`,
    `- URL atual: ${p.current_url ?? '—'}`,
    `- User agent: ${p.user_agent ?? '—'}`,
    `- Data/hora: ${p.created_at ?? '—'}`,
    '',
    'Curadoria:',
    `- extras.curadoria_front: ${cur != null ? JSON.stringify(cur) : '—'}`,
    `- extras.link_health: ${lh != null ? JSON.stringify(lh) : '—'}`,
    '',
    'Ação sugerida:',
    '- revisar item no Supabase;',
    '- verificar crawler/fonte;',
    '- decidir se deve ocultar, corrigir link, marcar duplicado ou manter.',
  ].join('\n');
}
