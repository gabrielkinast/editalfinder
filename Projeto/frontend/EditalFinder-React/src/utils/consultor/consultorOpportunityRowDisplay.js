import {
  getDeadlineAlertLabel,
  getDeadlineAlertStatus,
} from '../deadlineAlerts';
import { getDisplayTitle } from '../displayTitle';

export function motivoCurto(row) {
  if (row?.matchLinha) return String(row.matchLinha);
  const pos = row?.razoesPositivas;
  if (Array.isArray(pos) && pos[0]) return String(pos[0]);
  const raz = row?.razoes;
  if (Array.isArray(raz) && raz[0]) return String(raz[0]);
  return null;
}

export function prazoBadgeClass(status) {
  if (status === 'vence_hoje' || status === 'vence_3_dias' || status === 'vence_7_dias') {
    return 'consultor-pipeline-prazo--urgent';
  }
  if (status === 'prazo_indefinido') return 'consultor-pipeline-prazo--muted';
  if (status === 'encerrado') return 'consultor-pipeline-prazo--closed';
  return 'consultor-pipeline-prazo--ok';
}

export function compatClass(compat) {
  const c = String(compat || 'Baixa');
  if (c === 'Alta') return 'consultor-pipeline-compat--alta';
  if (c === 'Média' || c === 'Media') return 'consultor-pipeline-compat--media';
  return 'consultor-pipeline-compat--baixa';
}

function alertasObservacao(row) {
  const parts = [];
  const raw = row?.radar_alertas ?? row?.alertas;
  if (Array.isArray(raw) && raw.length) {
    raw.slice(0, 2).forEach((a) => {
      if (typeof a === 'string' && a.trim()) parts.push(a.trim());
      else if (a?.text) parts.push(String(a.text));
      else if (a?.label) parts.push(String(a.label));
    });
  }
  const ed = row?.edital || {};
  const prazoStatus = getDeadlineAlertStatus(ed);
  if (prazoStatus === 'prazo_indefinido') parts.push('Sem prazo');
  if (prazoStatus === 'vence_7_dias' || prazoStatus === 'vence_3_dias' || prazoStatus === 'vence_hoje') {
    parts.push('Prazo curto');
  }
  if (ed.dados_incompletos || row?.dados_incompletos) parts.push('Dados incompletos');
  return parts.length ? parts.join(' · ') : '—';
}

function focoTematico(ed) {
  const bits = [
    ed.area_inovacao,
    ed.areas,
    ed.tags,
    ed.setores,
    ed.temas,
  ].filter(Boolean);
  if (!bits.length) return '—';
  const joined = bits
    .flatMap((b) => (Array.isArray(b) ? b : String(b).split(/[,;|]/)))
    .map((s) => String(s).trim())
    .filter(Boolean)
    .slice(0, 4)
    .join(', ');
  return joined || '—';
}

function tipoApoio(ed) {
  return (
    ed.tipo_recurso ||
    ed.tipo_oportunidade ||
    ed.modalidade ||
    ed.tipo_edital ||
    '—'
  );
}

export function rowDisplayFields(row) {
  const ed = row?.edital || {};
  const id = ed.id ?? ed.id_edital ?? row?.id;
  const titulo = getDisplayTitle({
    titulo: ed.titulo,
    link: ed.linkOriginal || ed.link || ed.linkInscricao,
    descricao: ed.descricao,
    fonte_recurso: ed.orgao || ed.fonte_recurso,
  });
  const prazoStatus = getDeadlineAlertStatus(ed);
  const prazoLabel = getDeadlineAlertLabel(prazoStatus);
  const score = Number.isFinite(Number(row?.score)) ? Math.round(Number(row.score)) : 0;
  const link = ed.linkOriginal || ed.link || ed.linkInscricao || ed.link_edital || '';
  return {
    ed,
    id,
    titulo,
    prazoStatus,
    prazoLabel,
    motivo: motivoCurto(row),
    score,
    compatibilidade: row?.compatibilidade || 'Baixa',
    fonte: ed.orgao || ed.fonte_recurso || '—',
    tipoApoio: tipoApoio(ed),
    focoTematico: focoTematico(ed),
    observacoes: alertasObservacao(row),
    link,
  };
}
