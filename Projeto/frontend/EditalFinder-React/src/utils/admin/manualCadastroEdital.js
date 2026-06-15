/** Marcadores de cadastro manual na aba Cadastros → Editais (FRONTEND 1.1I). */

export const MANUAL_CADASTRO_FONTE_FALLBACK = 'Cadastro Manual';

export const MANUAL_CADASTRO_EXTRAS = {
  origem_cadastro: 'manual_admin',
  created_via: 'cadastros_page',
  manual_entry: true,
};

const DEBUG_KEY = 'editalfinder:debug:cadastros';
const SECRET_KEYS = new Set([
  'access_token',
  'refresh_token',
  'service_role',
  'anon_key',
  'password',
  'apikey',
  'authorization',
]);
const SECRET_PATTERNS = [
  /access_token/i,
  /refresh_token/i,
  /service_role/i,
  /anon_key/i,
  /password/i,
  /eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+\./,
];

export function isCadastrosDebugEnabled() {
  try {
    return globalThis.localStorage?.getItem(DEBUG_KEY) === '1';
  } catch {
    return false;
  }
}

/** @param {unknown} value */
export function parseEditalExtras(value) {
  if (value == null || value === '') return {};
  if (typeof value === 'object' && !Array.isArray(value)) return { ...value };
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value);
      return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? { ...parsed } : {};
    } catch {
      return {};
    }
  }
  return {};
}

/**
 * Mescla marcadores de cadastro manual preservando chaves existentes em extras.
 * @param {unknown} existingExtras
 */
export function mergeManualCadastroExtras(existingExtras) {
  const base = parseEditalExtras(existingExtras);
  return {
    ...base,
    origem_cadastro: base.origem_cadastro || MANUAL_CADASTRO_EXTRAS.origem_cadastro,
    created_via: base.created_via || MANUAL_CADASTRO_EXTRAS.created_via,
    manual_entry: true,
  };
}

/**
 * Critério de listagem Cadastros → Editais (manuais / complementares).
 * @param {Record<string, unknown> | null | undefined} row
 */
export function isManualCadastroEdital(row) {
  if (!row || typeof row !== 'object') return false;

  const extras = parseEditalExtras(row.extras);
  if (extras.manual_entry === true) return true;
  if (extras.origem_cadastro === MANUAL_CADASTRO_EXTRAS.origem_cadastro) return true;
  if (extras.created_via === MANUAL_CADASTRO_EXTRAS.created_via) return true;

  const fonte = String(row.fonte_recurso ?? '').trim();
  if (fonte === MANUAL_CADASTRO_FONTE_FALLBACK) return true;

  return false;
}

/**
 * @param {Array<Record<string, unknown>> | null | undefined} rows
 */
export function filterManualCadastroEditais(rows) {
  return (rows || []).filter(isManualCadastroEdital);
}

/**
 * Une lista remota com linhas recém-inseridas (evita sumir após reload vazio).
 * @param {Array<Record<string, unknown>>} remoteRows
 * @param {Array<Record<string, unknown>>} pinRows
 */
export function mergeCadastrosEditalRows(remoteRows, pinRows = []) {
  const byId = new Map();
  for (const row of remoteRows || []) {
    const id = row?.id_edital;
    if (id != null) byId.set(Number(id), row);
  }
  for (const row of pinRows || []) {
    const id = row?.id_edital;
    if (id != null) byId.set(Number(id), row);
  }
  return [...byId.values()].sort((a, b) => Number(b.id_edital) - Number(a.id_edital));
}

/** Filtro PostgREST OR para editais manuais (reduz payload quando RLS permite SELECT). */
export function buildManualEditalOrFilter() {
  return [
    'extras->manual_entry.eq.true',
    'extras->origem_cadastro.eq.manual_admin',
    'extras->created_via.eq.cadastros_page',
    `fonte_recurso.eq.${MANUAL_CADASTRO_FONTE_FALLBACK}`,
  ].join(',');
}

export const CREATE_EDITAL_RETURN_COLUMNS =
  'id_edital,titulo,link,fonte_recurso,orgao_responsavel,prazo_envio,ativo,criado_em,atualizado_em,extras,valor_maximo,situacao';

/**
 * Log seguro — ativar com localStorage.setItem('editalfinder:debug:cadastros', '1')
 * @param {string} label
 * @param {Record<string, unknown>} [payload]
 */
export function logCadastrosDebug(label, payload = {}) {
  if (!isCadastrosDebugEnabled()) return;
  const safeObj = JSON.parse(
    JSON.stringify(payload, (key, value) => {
      if (key && SECRET_KEYS.has(String(key).toLowerCase())) return '[redacted]';
      if (typeof value === 'string' && SECRET_PATTERNS.some((re) => re.test(value))) {
        return '[redacted]';
      }
      return value;
    }),
  );
  const suffix =
    safeObj && typeof safeObj === 'object' && Object.keys(safeObj).length
      ? ` ${JSON.stringify(safeObj)}`
      : '';
  console.info(`[EditalFinder][Cadastros] ${label}${suffix}`);
}
