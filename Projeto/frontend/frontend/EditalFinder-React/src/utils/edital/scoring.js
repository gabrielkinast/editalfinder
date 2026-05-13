import { prazoVencido } from './dates';

/**
 * Pontuação de relevância para ordenação “Mais relevantes”.
 * Mantém proporções próximas à especificação do produto (aberto × validação × prazo × completude).
 */
export function calcularPrioridadeEdital(edital, prefs = {}) {
  let score = 0;

  if (edital.ativo !== false) score += 30;
  else score -= 80;

  const prazoRaw = edital.prazo_envio_raw ?? edital.dataLimite;
  if (!prazoRaw) score += 0;
  else if (!prazoVencido(prazoRaw)) score += 20;
  else score -= 50;

  const vs = String(edital.validacao_status_raw || '').toLowerCase();
  if (vs === 'validado' || vs === 'valido') score += 20;
  if (vs === 'incompleto') score += 5;
  if (vs === 'acesso_limitado') score -= 5;
  if (vs === 'suspeito') score -= 30;

  const q = Number(edital.qualidade_dado_raw ?? edital.qualidade_dado ?? 0);
  if (!Number.isNaN(q)) score += Math.min(q, 100) / 5;

  const pdfOk = !!(edital.pdf_url_raw ?? edital.pdfUrl);
  if (pdfOk) score += prefs.preferPdf ? 10 : 5;
  const linkOk = !!(edital.link_raw ?? edital.linkOriginal);
  if (prazoRaw) score += 5;
  const vnum =
    edital.valor_estimado_raw ??
    edital.valor_total_raw ??
    edital.valor_maximo_raw ??
    edital.valorMaximo ??
    edital.valor;
  if (vnum != null && Number(vnum) > 0) score += 3;

  const paisN = normalizeTextMini(edital.pais_raw || '');
  const intl = paisN && !/(^br$|brasil|brazil)/.test(paisN);
  if (prefs.preferInternacional && intl) score += 6;
  if (prefs.preferNacional && (!paisN || /(^br$|brasil|brazil)/.test(paisN))) score += 4;

  return score;
}

function normalizeTextMini(s) {
  return String(s || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

export const SORT_OPTIONS = [
  { id: 'relevantes', label: 'Mais relevantes' },
  { id: 'prazo', label: 'Prazo mais próximo' },
  { id: 'recentes', label: 'Mais recentes (publicação)' },
  { id: 'valor', label: 'Maior valor' },
  { id: 'qualidade', label: 'Melhor qualidade' },
  { id: 'fonte', label: 'Fonte (A-Z)' },
  { id: 'tipo', label: 'Tipo de recurso' },
  { id: 'regiao', label: 'Região' },
];

function cmpStr(a, b) {
  return String(a || '').localeCompare(String(b || ''), 'pt-BR', { sensitivity: 'base' });
}

export function sortEditais(list, sortId, prefs) {
  const arr = [...list];
  switch (sortId) {
    case 'prazo': {
      return arr.sort((a, b) => {
        const da = parseTime(a.prazo_envio_raw || a.dataLimite);
        const db = parseTime(b.prazo_envio_raw || b.dataLimite);
        if (da == null && db == null) return 0;
        if (da == null) return 1;
        if (db == null) return -1;
        const va = da < startOfToday() ? Infinity : da;
        const vb = db < startOfToday() ? Infinity : db;
        return va - vb;
      });
    }
    case 'recentes':
      return arr.sort((a, b) => (parseTime(b.data_publicacao_raw) || 0) - (parseTime(a.data_publicacao_raw) || 0));
    case 'valor': {
      return arr.sort(
        (a, b) => Number(b.valor_principal_num ?? 0) - Number(a.valor_principal_num ?? 0),
      );
    }
    case 'qualidade':
      return arr.sort((a, b) => Number(b.qualidade_dado_raw ?? 0) - Number(a.qualidade_dado_raw ?? 0));
    case 'fonte':
      return arr.sort((a, b) => cmpStr(a.fonte_display, b.fonte_display));
    case 'tipo':
      return arr.sort((a, b) => cmpStr(a.tipo_recurso_raw, b.tipo_recurso_raw));
    case 'regiao':
      return arr.sort((a, b) => cmpStr(a.regiao_raw || a.regiao, b.regiao_raw || b.regiao));
    case 'relevantes':
    default:
      return arr.sort(
        (a, b) =>
          calcularPrioridadeEdital(b, prefs) - calcularPrioridadeEdital(a, prefs),
      );
  }
}

function parseTime(v) {
  if (v == null || v === '') return null;
  const d = String(v).includes('T') ? new Date(v) : new Date(`${String(v).slice(0, 10)}T12:00:00`);
  if (Number.isNaN(d.getTime())) return null;
  return d.getTime();
}

function startOfToday() {
  const n = new Date();
  n.setHours(0, 0, 0, 0);
  return n.getTime();
}
