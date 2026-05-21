import { getCuradoriaFront } from './editalVisibility';
import { getDeadlineAlertStatus, parsePrazoEnvio } from '../deadlineAlerts';
import { getEditalFeedbackReason } from '../../constants/editalFeedbackReasons';

function extrasOf(edital) {
  const ex = edital?.extras_raw ?? edital?.extras;
  return ex && typeof ex === 'object' && !Array.isArray(ex) ? ex : null;
}

function pickIdEdital(edital) {
  if (!edital) return null;
  const raw = edital.id_edital ?? edital.idNumerico ?? edital.id;
  if (raw == null || raw === '') return null;
  const s = String(raw).replace(/^manual-/, '');
  const n = Number(s);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function pickLink(edital) {
  return (
    edital?.linkOriginal ??
    edital?.link_raw ??
    edital?.link ??
    edital?.link_inscricao ??
    null
  );
}

function pickPdf(edital) {
  return edital?.pdfUrl ?? edital?.pdf_url ?? null;
}

function pickUrlDocumento(edital) {
  const ex = extrasOf(edital);
  if (ex?.url_documento) return String(ex.url_documento);
  const docs = edital?.documentos;
  if (Array.isArray(docs) && docs[0]?.url) return String(docs[0].url);
  if (docs && typeof docs === 'object' && docs.url) return String(docs.url);
  return null;
}

function pickUser(user) {
  if (!user) return {};
  const authUid = user.auth_user_id ?? null;
  return {
    auth_user_id: authUid,
    nome_email: user.nome_email ?? user.email ?? null,
    email_usuario: user.email ?? user.nome_email ?? null,
  };
}

/**
 * Monta payload de reporte (sem tokens/senha).
 * @param {object} edital — card dashboard ou linha de detalhe
 * @param {{ motivo: string; comentario?: string }} report
 * @param {object|null} user — perfil interno AuthContext (`user`), só metadados não sensíveis em extras
 */
export function buildEditalFeedbackPayload(edital, report, user = null) {
  const reason = getEditalFeedbackReason(report.motivo);
  const ex = extrasOf(edital);
  const prazoRaw = parsePrazoEnvio(edital);

  const payload = {
    id_edital: pickIdEdital(edital),
    titulo: edital?.titulo ?? edital?.titulo_original_raw ?? null,
    fonte_recurso: edital?.fonte_recurso_display ?? edital?.fonte_recurso ?? edital?.orgao ?? null,
    fonte: edital?.fonte_raw ?? edital?.fonte ?? null,
    link: pickLink(edital),
    link_edital: pickLink(edital),
    pdf_url: pickPdf(edital),
    url_documento: pickUrlDocumento(edital),
    prazo_envio: prazoRaw,
    status_prazo: getDeadlineAlertStatus(edital),
    validacao_status: edital?.validacao_status_raw ?? edital?.validacao_status ?? null,
    qualidade_dado: edital?.qualidade_dado_raw ?? edital?.qualidade_dado ?? null,
    motivo: report.motivo,
    motivo_label: reason?.label ?? report.motivo,
    comentario: (report.comentario || '').trim() || null,
    current_url: typeof window !== 'undefined' ? window.location.href : null,
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : null,
    created_at: new Date().toISOString(),
    extras_curadoria_front: getCuradoriaFront(edital) ?? ex?.curadoria_front ?? null,
    extras_link_health: ex?.link_health ?? null,
    ...pickUser(user),
  };

  return payload;
}

/** Campos seguros para log DEV após submit. */
export function sanitizeEditalFeedbackForLog(payload) {
  if (!payload || typeof payload !== 'object') return {};
  return {
    id_edital: payload.id_edital,
    titulo: payload.titulo,
    fonte_recurso: payload.fonte_recurso,
    motivo: payload.motivo,
    tem_comentario: Boolean(payload.comentario),
    id_usuario: payload.id_usuario,
    current_url: payload.current_url,
  };
}
