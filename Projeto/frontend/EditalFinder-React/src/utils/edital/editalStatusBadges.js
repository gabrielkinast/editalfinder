/**
 * FRONTEND 1.2A — Validity / Deadline / Semantic Badges.
 * FRONTEND 1.2B — getEditalStatusFilterKeys / filtros e exportação.
 *
 * Util central, resiliente e sem dependências externas, que traduz os campos
 * de validade/prazo/semântica (vindos do backend 10.1–10.3, em `extras`/colunas)
 * em badges visuais. Não altera backend nem schema.
 *
 * Regras semânticas importantes:
 * - sem_prazo NÃO é ruído;
 * - encerrado NÃO é ruído;
 * - resultado/portal_util não são necessariamente ruído;
 * - BNDES com "Resultado Final" não deve aparecer como oportunidade aberta.
 *
 * @typedef {(
 *   'open' | 'due_7' | 'due_30' | 'closed' | 'no_deadline' |
 *   'deadline_in_detail' | 'deadline_tbd' | 'permanent_line' |
 *   'result_published' | 'post_result' | 'portal_useful' | 'noise' | 'unknown'
 * )} EditalBadgeKind
 *
 * @typedef {(
 *   'aberto' | 'vencendo_7' | 'vencendo_30' | 'encerrado' | 'sem_prazo' |
 *   'prazo_em_pdf_ou_detalhe' | 'prazo_a_definir' | 'linha_permanente' |
 *   'resultado_publicado' | 'chamada_pos_resultado' | 'portal_util' |
 *   'ruido_provavel' | 'duplicata_oculta' | 'indefinido'
 * )} EditalStatusFilterKey
 *
 * @typedef {('success'|'warning'|'danger'|'neutral'|'info'|'muted')} EditalBadgeTone
 *
 * @typedef {Object} EditalStatusBadge
 * @property {EditalBadgeKind} kind
 * @property {string} label
 * @property {string} title
 * @property {number} priority
 * @property {EditalBadgeTone} tone
 */

import { getCuradoriaFront, isHiddenDuplicateCuradoria } from './editalVisibility.js';

const MS_DAY = 86400000;

/** Catálogo de badges: kind -> {label, title, priority, tone}. */
const BADGE_DEFS = {
  noise: {
    label: 'Ruído provável',
    title: 'Registro provavelmente não é uma oportunidade relevante.',
    priority: 1,
    tone: 'danger',
  },
  post_result: {
    label: 'Chamada pós-resultado',
    title: 'A chamada parece estar em fase pós-submissão ou pós-resultado.',
    priority: 2,
    tone: 'muted',
  },
  result_published: {
    label: 'Resultado publicado',
    title: 'Este registro parece ser resultado ou documento pós-edital.',
    priority: 2,
    tone: 'muted',
  },
  closed: {
    label: 'Encerrado',
    title: 'O prazo informado já passou.',
    priority: 3,
    tone: 'muted',
  },
  due_7: {
    label: 'Vencendo em 7 dias',
    title: 'Prazo próximo. Verifique o edital oficial.',
    priority: 4,
    tone: 'danger',
  },
  due_30: {
    label: 'Vencendo em 30 dias',
    title: 'Prazo dentro dos próximos 30 dias.',
    priority: 5,
    tone: 'warning',
  },
  open: {
    label: 'Aberto',
    title: 'O prazo de envio ainda está aberto.',
    priority: 6,
    tone: 'success',
  },
  deadline_in_detail: {
    label: 'Prazo em PDF/detalhe',
    title: 'O prazo pode estar no PDF ou na página de detalhe.',
    priority: 7,
    tone: 'info',
  },
  deadline_tbd: {
    label: 'Prazo a definir',
    title: 'A fonte indica que o prazo ainda será definido.',
    priority: 8,
    tone: 'neutral',
  },
  permanent_line: {
    label: 'Linha permanente',
    title: 'Oportunidade contínua ou linha permanente de financiamento.',
    priority: 9,
    tone: 'info',
  },
  no_deadline: {
    label: 'Sem prazo informado',
    title: 'Não foi encontrado prazo estruturado. Verifique o site oficial.',
    priority: 10,
    tone: 'neutral',
  },
  portal_useful: {
    label: 'Portal útil',
    title: 'Página útil para acompanhamento, mas não necessariamente uma chamada aberta.',
    priority: 11,
    tone: 'info',
  },
  unknown: {
    label: 'Status indefinido',
    title: 'Não há informações suficientes para classificar a situação.',
    priority: 99,
    tone: 'muted',
  },
};

/** kind (1.2A) → chave de filtro/export (1.2B). */
export const BADGE_KIND_TO_FILTER_KEY = {
  open: 'aberto',
  due_7: 'vencendo_7',
  due_30: 'vencendo_30',
  closed: 'encerrado',
  no_deadline: 'sem_prazo',
  deadline_in_detail: 'prazo_em_pdf_ou_detalhe',
  deadline_tbd: 'prazo_a_definir',
  permanent_line: 'linha_permanente',
  result_published: 'resultado_publicado',
  post_result: 'chamada_pos_resultado',
  portal_useful: 'portal_util',
  noise: 'ruido_provavel',
  unknown: 'indefinido',
};

/** Opções públicas da sidebar (sem duplicata_oculta). */
export const SEMANTIC_STATUS_FILTER_OPTIONS = [
  { id: 'aberto', label: 'Aberto' },
  { id: 'vencendo_7', label: 'Vencendo em 7 dias' },
  { id: 'vencendo_30', label: 'Vencendo em 30 dias' },
  { id: 'encerrado', label: 'Encerrado' },
  { id: 'sem_prazo', label: 'Sem prazo' },
  { id: 'prazo_em_pdf_ou_detalhe', label: 'Prazo em PDF/detalhe' },
  { id: 'prazo_a_definir', label: 'Prazo a definir' },
  { id: 'linha_permanente', label: 'Linha permanente' },
  { id: 'resultado_publicado', label: 'Resultado publicado' },
  { id: 'chamada_pos_resultado', label: 'Chamada pós-resultado' },
  { id: 'portal_util', label: 'Portal útil' },
  { id: 'ruido_provavel', label: 'Ruído provável' },
  { id: 'indefinido', label: 'Indefinido' },
];

/** @param {EditalBadgeKind} kind @returns {EditalStatusBadge} */
function makeBadge(kind) {
  const def = BADGE_DEFS[kind] || BADGE_DEFS.unknown;
  return { kind, label: def.label, title: def.title, priority: def.priority, tone: def.tone };
}

function isPlainObject(v) {
  return v != null && typeof v === 'object' && !Array.isArray(v);
}

/** Extras resilientes: aceita `extras_raw` (mapper do front) ou `extras` (backend cru). */
function getExtras(edital) {
  if (!isPlainObject(edital)) return {};
  const ex = edital.extras_raw ?? edital.extras;
  return isPlainObject(ex) ? ex : {};
}

function firstString(...vals) {
  for (const v of vals) {
    if (v == null) continue;
    const s = String(v).trim();
    if (s) return s;
  }
  return '';
}

function lower(v) {
  return String(v ?? '').toLowerCase();
}

/** Parse tolerante de datas (ISO, yyyy-mm-dd, epoch). Datas inválidas → null. */
function parseDateSafe(raw) {
  if (raw == null || raw === '') return null;
  if (raw instanceof Date) return Number.isNaN(raw.getTime()) ? null : raw;
  const s = String(raw).trim();
  if (!s) return null;
  if (/^\d{10,13}$/.test(s)) {
    const n = Number(s);
    const d = new Date(n < 1e11 ? n * 1000 : n);
    return Number.isNaN(d.getTime()) ? null : d;
  }
  const d = s.includes('T') ? new Date(s) : new Date(`${s.slice(0, 10)}T12:00:00`);
  return Number.isNaN(d.getTime()) ? null : d;
}

function startOfDay(d) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

/**
 * Resolve a data de prazo, priorizando `prazo_envio` sobre `fim_inscricao`.
 * @returns {Date|null}
 */
export function resolveDeadlineDate(edital) {
  if (!isPlainObject(edital)) return null;
  const ex = getExtras(edital);
  const prazo = parseDateSafe(
    firstString(edital.prazo_envio_raw, edital.prazo_envio, ex.prazo_envio),
  );
  if (prazo) return prazo;
  const fim = parseDateSafe(
    firstString(
      edital.fim_inscricao_raw,
      edital.fim_inscricao,
      edital.dataLimite,
      ex.fim_inscricao,
      ex.grants_close_date,
      ex.closeDate,
    ),
  );
  return fim;
}

/** @returns {string} actionability/bucket normalizado em lowercase ou ''. */
function resolveActionabilityType(edital) {
  const ex = getExtras(edital);
  return lower(
    firstString(
      ex.actionability_type,
      ex.classification_by_actionability_type,
      edital.actionability_type,
    ),
  );
}

/** @returns {string|null} sem_prazo_kind ou null. */
export function resolveSemPrazoKind(edital) {
  const ex = getExtras(edital);
  const v = firstString(ex.sem_prazo_kind, edital.sem_prazo_kind);
  return v || null;
}

/** Status de validade pronto do backend, ou derivado do prazo. */
export function resolveValidityStatus(edital, now = new Date()) {
  const ex = getExtras(edital);
  const ready = lower(firstString(ex.validade_status, edital.validade_status));
  if (ready) return ready;
  const date = resolveDeadlineDate(edital);
  if (!date) return 'sem_prazo';
  const days = Math.round((startOfDay(date) - startOfDay(now)) / MS_DAY);
  if (days < 0) return 'encerrado';
  if (days <= 30) return 'vencendo';
  return 'aberto';
}

function semanticBlob(edital) {
  const ex = getExtras(edital);
  return lower(
    [
      edital.titulo,
      edital.descricao,
      ex.sem_prazo_reason,
      ex.bndes_classification,
      ex.noise_type,
    ]
      .map((v) => String(v ?? ''))
      .join(' ')
      .slice(0, 4000),
  );
}

const RESULT_TEXT_RE = /resultado\s+final|resultado\s+publicad|homologa[cç][aã]o|resultado\s+da\s+sele[cç][aã]o/i;
const POST_RESULT_TEXT_RE =
  /resultado\s+final\s+divulgad|resultado\s+final\s+da\s+chamada|processo\s+de\s+sele[cç][aã]o\s+conclu[ií]d|dilig[eê]ncia|classifica[cç][aã]o\s+final/i;

export function isResultPublished(edital) {
  if (!isPlainObject(edital)) return false;
  if (resolveActionabilityType(edital) === 'resultado') return true;
  const ex = getExtras(edital);
  if (lower(ex.bndes_classification).includes('resultado')) return true;
  return RESULT_TEXT_RE.test(semanticBlob(edital));
}

function isBndes(edital) {
  const fonte = lower(
    firstString(
      edital?.fonte,
      edital?.fonte_recurso,
      edital?.fonte_recurso_display,
      edital?.orgao,
      getExtras(edital).fonte,
    ),
  );
  return fonte.includes('bndes');
}

export function isPostResultCall(edital) {
  if (!isPlainObject(edital)) return false;
  if (!isBndes(edital)) return false;
  const ex = getExtras(edital);
  const cls = lower(ex.bndes_classification);
  if (cls.includes('post_result') || cls.includes('pos_resultado') || cls.includes('resultado_final')) {
    return true;
  }
  return POST_RESULT_TEXT_RE.test(semanticBlob(edital));
}

export function isPortalUseful(edital) {
  if (!isPlainObject(edital)) return false;
  const t = resolveActionabilityType(edital);
  if (t === 'portal_util' || t === 'portal_useful') return true;
  const ex = getExtras(edital);
  return lower(firstString(ex.bucket, ex.actionability_bucket)) === 'portal_util';
}

function isNoise(edital) {
  const ex = getExtras(edital);
  return ex.is_noise === true || edital.is_noise === true;
}

function isPermanentLine(edital) {
  const ex = getExtras(edital);
  const tipo = lower(firstString(edital.tipo_oportunidade_raw, edital.tipo_oportunidade, ex.tipo_oportunidade));
  if (tipo.includes('permanente') || tipo.includes('continu')) return true;
  return /linha\s+permanente|fluxo\s+cont[ií]nuo|cont[ií]nuo|permanent\s+funding/i.test(semanticBlob(edital));
}

/**
 * Calcula os badges de status de um edital/oportunidade, ordenados por prioridade.
 * @param {unknown} edital
 * @param {Date} [now]
 * @returns {EditalStatusBadge[]}
 */
export function getEditalStatusBadges(edital, now = new Date()) {
  if (!isPlainObject(edital)) return [];
  const badges = [];

  if (isNoise(edital)) badges.push(makeBadge('noise'));

  const postResult = isPostResultCall(edital);
  const resultPub = isResultPublished(edital);
  if (postResult) badges.push(makeBadge('post_result'));
  else if (resultPub) badges.push(makeBadge('result_published'));

  const date = resolveDeadlineDate(edital);
  if (date) {
    const days = Math.round((startOfDay(date) - startOfDay(now)) / MS_DAY);
    if (days < 0) badges.push(makeBadge('closed'));
    else if (days <= 7) badges.push(makeBadge('due_7'));
    else if (days <= 30) badges.push(makeBadge('due_30'));
    else badges.push(makeBadge('open'));
  } else {
    const spk = resolveSemPrazoKind(edital);
    const ex = getExtras(edital);
    const recrawl = ex.recrawl_candidate === true || ex.recrawl_candidate === 'true';
    if (spk === 'deadline_in_pdf_or_detail' || recrawl) {
      badges.push(makeBadge('deadline_in_detail'));
    } else if (spk === 'deadline_tbd') {
      badges.push(makeBadge('deadline_tbd'));
    } else if (spk === 'permanent_funding_line' || isPermanentLine(edital)) {
      badges.push(makeBadge('permanent_line'));
    } else if (!postResult && !resultPub) {
      badges.push(makeBadge('no_deadline'));
    }
  }

  if (isPortalUseful(edital)) badges.push(makeBadge('portal_useful'));

  if (badges.length === 0) badges.push(makeBadge('unknown'));

  const seen = new Set();
  const out = [];
  for (const badge of badges.sort((a, c) => a.priority - c.priority)) {
    if (seen.has(badge.kind)) continue;
    seen.add(badge.kind);
    out.push(badge);
  }
  return out;
}

/** Primeiro badge (mais prioritário) — útil para colunas de exportação. */
export function getPrimaryEditalStatusBadge(edital, now = new Date()) {
  const list = getEditalStatusBadges(edital, now);
  return list.length ? list[0] : null;
}

/**
 * Chaves de filtro semântico para um edital (OR na sidebar).
 * @param {unknown} edital
 * @param {Date} [now]
 * @returns {string[]}
 */
export function getEditalStatusFilterKeys(edital, now = new Date()) {
  const badges = getEditalStatusBadges(edital, now);
  const kinds = new Set(badges.map((b) => b.kind));
  const keys = new Set();
  for (const badge of badges) {
    const fk = BADGE_KIND_TO_FILTER_KEY[badge.kind];
    if (fk) keys.add(fk);
  }
  // Pós-resultado/resultado publicado não devem ressuscitar aberto/vencendo (1.2A).
  if (kinds.has('post_result') || kinds.has('result_published')) {
    keys.delete('aberto');
    keys.delete('vencendo_7');
    keys.delete('vencendo_30');
  }
  const cf = getCuradoriaFront(edital);
  if (isHiddenDuplicateCuradoria(cf)) keys.add('duplicata_oculta');
  return [...keys];
}

/**
 * Status semântico primário (chave canônica).
 * @param {unknown} edital
 * @param {Date} [now]
 * @returns {string}
 */
export function getEditalStatusSemantic(edital, now = new Date()) {
  const primary = getPrimaryEditalStatusBadge(edital, now);
  if (!primary) return 'indefinido';
  return BADGE_KIND_TO_FILTER_KEY[primary.kind] || 'indefinido';
}

/**
 * Label curto do status primário (export PDF / coluna Status).
 * @param {unknown} edital
 * @param {Date} [now]
 */
export function getEditalStatusLabel(edital, now = new Date()) {
  const primary = getPrimaryEditalStatusBadge(edital, now);
  return primary?.label || BADGE_DEFS.unknown.label;
}

/**
 * Todos os labels de badges (export detalhado).
 * @param {unknown} edital
 * @param {Date} [now]
 */
export function getEditalStatusDetailLabels(edital, now = new Date()) {
  const labels = getEditalStatusBadges(edital, now).map((b) => b.label);
  return labels.length ? labels.join('; ') : BADGE_DEFS.unknown.label;
}

/**
 * OR: edital passa se alguma chave selecionada bate com getEditalStatusFilterKeys.
 * Objeto vazio / nenhum marcado → true (sem filtro por status).
 * @param {unknown} edital
 * @param {Record<string, boolean>|undefined|null} selections
 * @param {Date} [now]
 */
export function editalMatchesSemanticStatusSelection(edital, selections, now = new Date()) {
  if (!selections || typeof selections !== 'object') return true;
  const selected = Object.keys(selections).filter((k) => selections[k]);
  if (!selected.length) return true;
  const editalKeys = getEditalStatusFilterKeys(edital, now);
  return selected.some((sk) => editalKeys.includes(sk));
}
