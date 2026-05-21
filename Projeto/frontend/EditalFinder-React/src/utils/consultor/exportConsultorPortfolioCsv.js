import { rowDisplayFields } from './consultorOpportunityRowDisplay';

const CSV_HEADERS = [
  'Programa / Edital',
  'Fonte',
  'Prazo',
  'Tipo de apoio',
  'Foco temático',
  'Observações',
  'Compatibilidade',
  'Link',
];

/**
 * Escapa valor para célula CSV (RFC 4180).
 * @param {unknown} value
 */
export function escapeCsvCell(value) {
  const s = value == null || value === undefined ? '' : String(value);
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

/**
 * @param {object} row — linha Radar (mesma da tabela da carteira)
 */
export function portfolioRowToCsvCells(row) {
  const d = rowDisplayFields(row);
  const compat =
    d.score > 0 ? `${d.compatibilidade} (${d.score}%)` : String(d.compatibilidade || '—');
  return [
    d.titulo || '—',
    d.fonte || '—',
    d.prazoLabel || '—',
    d.tipoApoio || '—',
    d.focoTematico || '—',
    d.observacoes || '—',
    compat,
    d.link || '',
  ];
}

/**
 * @param {object[]} matches
 */
export function buildPortfolioCsvContent(matches = []) {
  const rows = Array.isArray(matches) ? matches : [];
  const lines = [CSV_HEADERS.map(escapeCsvCell).join(',')];
  for (const row of rows) {
    lines.push(portfolioRowToCsvCells(row).map(escapeCsvCell).join(','));
  }
  return `\uFEFF${lines.join('\r\n')}`;
}

/**
 * @param {string} name
 */
export function sanitizePortfolioCsvClientSlug(name) {
  const base = String(name || 'cliente')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
  return (base || 'cliente').slice(0, 48);
}

/**
 * @param {string} [clienteNome]
 * @param {string} [prefix] — ex.: carteira, carteira_top20, carteira_selecionadas
 */
export function buildPortfolioCsvFilename(clienteNome, prefix = 'carteira') {
  const slug = sanitizePortfolioCsvClientSlug(clienteNome);
  const date = new Date().toISOString().slice(0, 10);
  const safePrefix = String(prefix || 'carteira').replace(/[^a-zA-Z0-9_]+/g, '_').slice(0, 32);
  return `${safePrefix}_${slug}_${date}.csv`;
}

/**
 * Dispara download do CSV no navegador.
 * @param {object} params
 * @param {object[]} params.matches
 * @param {string} [params.clienteNome]
 * @param {string} [params.filenamePrefix]
 */
export function downloadConsultorPortfolioCsv({ matches, clienteNome, filenamePrefix = 'carteira' }) {
  const list = Array.isArray(matches) ? matches : [];
  if (!list.length) {
    throw new Error('Nenhuma oportunidade para exportar.');
  }
  const content = buildPortfolioCsvContent(list);
  const filename = buildPortfolioCsvFilename(clienteNome, filenamePrefix);
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.style.display = 'none';
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
  return { filename, rowCount: list.length };
}
