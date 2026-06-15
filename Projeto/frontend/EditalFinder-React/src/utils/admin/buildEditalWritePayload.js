import {
  MANUAL_CADASTRO_FONTE_FALLBACK,
  mergeManualCadastroExtras,
  parseEditalExtras,
} from './manualCadastroEdital.js';

/** Colunas reais de `public.edital` usadas pelo formulário admin (schema_current.sql). */
const EDITAL_ADMIN_WRITE_FIELDS = new Set([
  'titulo',
  'descricao',
  'objetivo',
  'temas',
  'publico_alvo',
  'fonte_recurso',
  'valor_maximo',
  'data_publicacao',
  'prazo_envio',
  'situacao',
  'pdf_url',
  'link',
  'orgao_responsavel',
  'id_organizacao',
  'estado',
  'ativo',
]);

const OPTIONAL_TEXT_FIELDS = new Set([
  'descricao',
  'objetivo',
  'temas',
  'publico_alvo',
  'fonte_recurso',
  'pdf_url',
  'orgao_responsavel',
  'estado',
]);

function dateInputValue(raw) {
  if (raw == null || raw === '') return '';
  const s = String(raw);
  return s.length >= 10 ? s.slice(0, 10) : s;
}

function normalizeOptionalText(value) {
  if (value == null) return null;
  const s = String(value).trim();
  return s.length ? s : null;
}

/**
 * Estado inicial / edição — só campos do formulário (ignora join `organizacao` e colunas extras).
 */
export function normalizeEditalFormInitialData(row) {
  if (!row || typeof row !== 'object') return {};

  const statusFromRow =
    row.ativo === false || String(row.status || '').toLowerCase() === 'inativo' ? 'Inativo' : 'Ativo';

  return {
    titulo: row.titulo ?? '',
    descricao: row.descricao ?? '',
    objetivo: row.objetivo ?? '',
    temas: row.temas ?? '',
    publico_alvo: row.publico_alvo ?? '',
    fonte_recurso: row.fonte_recurso ?? '',
    valor_maximo: row.valor_maximo ?? 0,
    data_publicacao: dateInputValue(row.data_publicacao),
    prazo_envio: dateInputValue(row.prazo_envio),
    situacao: row.situacao ?? 'Aberto',
    pdf_url: row.pdf_url ?? '',
    link: row.link ?? '',
    status: statusFromRow,
    id_organizacao: row.id_organizacao ?? '',
    orgao_responsavel: row.orgao_responsavel ?? '',
    estado: row.estado ?? '',
  };
}

/**
 * Payload seguro para insert/update em `public.edital`.
 * Remove `organizacao`, `organizacao_responsavel`, `status` e demais campos inexistentes.
 * @param {object} [options]
 * @param {boolean} [options.manualCadastro] — marca extras + fallback de fonte (Cadastros)
 */
export function buildEditalWritePayload(formData, options = {}) {
  const { manualCadastro = false } = options;
  const raw = formData && typeof formData === 'object' ? { ...formData } : {};

  delete raw.organizacao;
  delete raw.organizacao_responsavel;
  delete raw.id_edital;

  const statusLabel = raw.status;
  delete raw.status;

  const payload = {};

  for (const key of EDITAL_ADMIN_WRITE_FIELDS) {
    if (!(key in raw)) continue;
    payload[key] = raw[key];
  }

  if (statusLabel != null && payload.ativo === undefined) {
    payload.ativo = String(statusLabel).toLowerCase() !== 'inativo';
  }

  if ('id_organizacao' in payload) {
    const idRaw = payload.id_organizacao;
    if (idRaw === '' || idRaw == null) {
      delete payload.id_organizacao;
    } else {
      const n = Number(idRaw);
      if (Number.isFinite(n)) payload.id_organizacao = n;
      else delete payload.id_organizacao;
    }
  }

  if ('valor_maximo' in payload) {
    const n = Number(payload.valor_maximo);
    payload.valor_maximo = Number.isFinite(n) ? n : null;
  }

  for (const key of OPTIONAL_TEXT_FIELDS) {
    if (key in payload) {
      payload[key] = normalizeOptionalText(payload[key]);
    }
  }

  if ('link' in payload) {
    const link = normalizeOptionalText(payload.link);
    if (link) payload.link = link;
    else delete payload.link;
  }

  if ('data_publicacao' in payload && payload.data_publicacao === '') {
    payload.data_publicacao = null;
  }
  if ('prazo_envio' in payload && payload.prazo_envio === '') {
    payload.prazo_envio = null;
  }

  if (manualCadastro) {
    payload.extras = mergeManualCadastroExtras(parseEditalExtras(raw.extras));
    if (!payload.fonte_recurso) {
      payload.fonte_recurso = MANUAL_CADASTRO_FONTE_FALLBACK;
    }
  }

  const entries = Object.entries(payload).filter(
    ([key]) => EDITAL_ADMIN_WRITE_FIELDS.has(key) || (manualCadastro && key === 'extras'),
  );

  return Object.fromEntries(entries);
}
