import { getFonte } from '../edital/editalFieldHelpers';
import { normalizeText } from '../edital/normalizeText';

/** @typedef {'brasil'|'internacional'|'multilateral'|'desconhecido'} DashboardScope */

export const DASHBOARD_SCOPE_ALL = 'all';
export const DASHBOARD_SCOPE_BRASIL = 'brasil';
export const DASHBOARD_SCOPE_INTERNACIONAL = 'internacional';
export const DASHBOARD_SCOPE_MULTILATERAL = 'multilateral';

export const DASHBOARD_SCOPE_OPTIONS = [
  { id: DASHBOARD_SCOPE_ALL, label: 'Todos' },
  { id: DASHBOARD_SCOPE_BRASIL, label: 'Brasil' },
  { id: DASHBOARD_SCOPE_INTERNACIONAL, label: 'Internacional' },
  { id: DASHBOARD_SCOPE_MULTILATERAL, label: 'Multilateral' },
];

const BR_ORGAOS = [
  'fapesc',
  'fapergs',
  'cnpq',
  'finep',
  'capes',
  'fapesp',
  'faperj',
  'fapemig',
  'bndes',
  'sebrae',
  'senai',
  'embrapii',
  'mcti',
  'mctic',
  'banco do brasil',
  'caixa',
  'badesc',
  'fundacao araucaria',
  'fundação araucária',
];

const MULTILATERAL = [
  'banco mundial',
  'world bank',
  'bid',
  'idb',
  'onu',
  'unesco',
  'oecd',
  'ocde',
  'horizon europe',
  'horizon 2020',
  'horizon',
  'european commission',
  'união europeia',
  'uniao europeia',
  'european union',
  'undp',
  'unicef',
];

const INTERNATIONAL = [
  'grants.gov',
  'grants gov',
  'nsf',
  'nih',
  'nasa',
  'darpa',
  'nato',
  'ukri',
  'uk research',
  'china international',
  'china',
  'korea',
  'japan',
  'australia',
  'canada',
  'usa',
  'u.s.',
  'united states',
  'european',
  'eu funding',
  'army',
  'defense',
  'defence',
];

const TYPE_BUCKETS = [
  {
    label: 'Fomento / chamada pública',
    re: /\b(chamada\s+p[uú]blica|chamada\s+nacional|edital\s+de\s+fomento|fomento|funding\s+opportunity|grant\s+program|call\s+for\s+proposals|research\s+grant)\b/i,
    titleRe: /\b(edital|chamada|chamada\s+p[uú]blica|fomento|grant|funding|opportunity)\b/i,
  },
  {
    label: 'Subvenção / inovação',
    re: /\b(subven[cç][aã]o|subvention|non[- ]?repayable|fundo\s+perdido|inova[cç][aã]o|innovation\s+grant|sbir|sttr)\b/i,
    titleRe: /\b(subven[cç][aã]o|inova[cç][aã]o|innovation)\b/i,
  },
  {
    label: 'Pesquisa científica',
    re: /\b(pesquisa\s+cient[ií]fica|scientific\s+research|research\s+project|p&d|p\s*&\s*d|r&d)\b/i,
    titleRe: /\b(pesquisa|cient[ií]fica|research)\b/i,
  },
  {
    label: 'Bolsas / formação',
    re: /\b(bolsa|bolsas|fellowship|scholarship|traineeship|doctoral|mestrado|doutorado)\b/i,
    titleRe: /\b(bolsa|fellowship|scholarship)\b/i,
  },
  {
    label: 'Cooperação internacional',
    re: /\b(coopera[cç][aã]o\s+internacional|international\s+cooperation|bilateral|multilateral)\b/i,
    titleRe: /\b(coopera[cç][aã]o\s+internacional|international)\b/i,
  },
  {
    label: 'Compras / licitação',
    re: /\b(licita[cç][aã]o|preg[aã]o|procurement|compra\s+p[uú]blica|tender|rfp|rfq)\b/i,
    titleRe: /\b(licita[cç][aã]o|preg[aã]o|procurement|compra)\b/i,
  },
  {
    label: 'Concurso / seleção',
    re: /\b(concurso|sele[cç][aã]o|processo\s+seletivo|competition|selection\s+process)\b/i,
    titleRe: /\b(concurso|sele[cç][aã]o|processo\s+seletivo)\b/i,
  },
  {
    label: 'Prêmio / desafio',
    re: /\b(pr[eê]mio|premio|challenge|desafio|award|prize)\b/i,
    titleRe: /\b(pr[eê]mio|challenge|desafio|award)\b/i,
  },
  {
    label: 'Evento / capacitação',
    re: /\b(webinar|workshop|evento|capacita[cç][aã]o|training|course|curso)\b/i,
    titleRe: /\b(webinar|evento|workshop|capacita[cç][aã]o)\b/i,
  },
  {
    label: 'Notícia institucional',
    re: /\b(not[ií]cia|news|announcement|comunicado|press\s+release)\b/i,
    titleRe: /\b(not[ií]cia|news|announcement|comunicado)\b/i,
  },
];

/**
 * @param {string} haystack
 * @param {typeof TYPE_BUCKETS[0]} bucket
 */
function matchesBucket(haystack, bucket) {
  return bucket.re.test(haystack) || bucket.titleRe.test(haystack);
}

/**
 * Classificação estimada de modalidade (não truncar antes de agrupar).
 * @param {Record<string, unknown>} edital
 */
export function getDashboardEditalType(edital) {
  if (!edital) return 'Sem classificação';

  const fieldParts = [
    edital.tipo_recurso_raw,
    edital.tipo_recurso,
    edital.tipo_oportunidade_raw,
    edital.tipo_oportunidade,
    edital.tipoRecurso,
    edital.tipo,
    edital.modalidade_financiamento_raw,
    edital.modalidade_financiamento,
    edital.modalidade,
    edital.categoria,
    edital.linha_credito_raw,
    edital.natureza_recurso_raw,
  ]
    .filter(Boolean)
    .map((v) => String(v).trim())
    .join(' ');

  const title = String(edital.titulo || edital.titulo_original_raw || '').trim();
  const combined = `${fieldParts} ${title}`.trim();

  if (fieldParts) {
    for (const bucket of TYPE_BUCKETS) {
      if (matchesBucket(fieldParts, bucket)) return bucket.label;
    }
  }

  for (const bucket of TYPE_BUCKETS) {
    if (matchesBucket(title, bucket)) return bucket.label;
  }

  if (fieldParts) {
    const short = fieldParts.slice(0, 80);
    if (short.length < 60) return short;
  }

  return 'Sem classificação';
}

/**
 * @param {Record<string, unknown>} edital
 * @returns {DashboardScope}
 */
export function getDashboardSourceScope(edital) {
  const fonte = normalizeText(getFonte(edital));
  const link = String(edital.link_raw ?? edital.linkOriginal ?? edital.link ?? '').toLowerCase();
  const pais = normalizeText(String(edital.pais_raw ?? edital.pais ?? ''));
  const estado = normalizeText(String(edital.estado ?? edital.uf_raw ?? ''));
  const regiao = normalizeText(String(edital.regiao_raw ?? edital.regiao ?? ''));
  const origem = normalizeText(String(edital.origem_portal_raw ?? ''));
  const blob = `${fonte} ${link} ${pais} ${estado} ${regiao} ${origem}`;

  if (MULTILATERAL.some((k) => blob.includes(normalizeText(k)))) return 'multilateral';
  if (
    BR_ORGAOS.some((k) => fonte.includes(normalizeText(k))) ||
    link.includes('.br') ||
    /\b(brasil|brazil)\b/.test(pais) ||
    estado === 'nacional' ||
    (regiao && /\b(br|sul|sudeste|nordeste|norte|centro-oeste)\b/.test(regiao) && !INTERNATIONAL.some((k) => fonte.includes(normalizeText(k))))
  ) {
    return 'brasil';
  }
  if (INTERNATIONAL.some((k) => blob.includes(normalizeText(k)))) return 'internacional';
  if (pais && !/\b(brasil|brazil)\b/.test(pais)) return 'internacional';
  if (estado === 'internacional') return 'internacional';
  return 'desconhecido';
}

/**
 * @param {Record<string, unknown>} edital
 * @param {string} scopeFilter
 */
export function editalMatchesScope(edital, scopeFilter) {
  if (!scopeFilter || scopeFilter === DASHBOARD_SCOPE_ALL) return true;
  const scope = getDashboardSourceScope(edital);
  if (scopeFilter === DASHBOARD_SCOPE_BRASIL) return scope === 'brasil';
  if (scopeFilter === DASHBOARD_SCOPE_INTERNACIONAL) return scope === 'internacional';
  if (scopeFilter === DASHBOARD_SCOPE_MULTILATERAL) return scope === 'multilateral';
  return true;
}

const BR_CONTENT = [
  'brasil',
  'nacional',
  'governo federal',
  'cnpq',
  'capes',
  'finep',
  'fapesp',
  'faperj',
  'fapesc',
  'fapergs',
  'universidade',
  'ufsc',
  'ufpr',
  'usp',
  'unicamp',
];

const INT_CONTENT = [
  'nato',
  'army',
  'darpa',
  'nsf',
  'nih',
  'horizon',
  'european',
  'ukri',
  'china',
  'grants.gov',
  'defense',
  'defence',
  'international',
];

/**
 * @param {Record<string, unknown>} item
 * @returns {'brasil'|'internacional'|'desconhecido'}
 */
export function classifyContentScope(item) {
  if (!item) return 'desconhecido';
  const src = normalizeText(
    String(item.fonte || item.source || item.orgao || item.instituicao || item.publisher || ''),
  );
  const link = String(item.link || item.url || '').toLowerCase();
  const tags = Array.isArray(item.tags)
    ? item.tags.join(' ')
    : String(item.tags || item.categoria || item.area || '');
  const title = String(item.titulo || item.title || item.nome || '');
  const blob = normalizeText(`${src} ${tags} ${title}`);

  if (link.includes('.br') || BR_CONTENT.some((k) => blob.includes(normalizeText(k)))) {
    return 'brasil';
  }
  if (INT_CONTENT.some((k) => blob.includes(normalizeText(k)))) return 'internacional';
  if (/[áàâãéêíóôõúç]/i.test(title)) return 'brasil';
  if (/\b(the|and|for|with|program|funding|grant)\b/i.test(title)) return 'internacional';
  return 'desconhecido';
}

/**
 * @param {string} scope
 */
export function scopeBadgeLabel(scope) {
  switch (scope) {
    case 'brasil':
      return 'Brasil';
    case 'internacional':
      return 'Internacional';
    case 'multilateral':
      return 'Multilateral';
    default:
      return null;
  }
}
