import { coerceStringArray } from '../edital/coerceArrays.js';
import { getFonte } from '../edital/editalFieldHelpers.js';
import {
  getEditalStatusDetailLabels,
  getEditalStatusLabel,
} from '../edital/editalStatusBadges.js';
import { formatCurrency, formatDateLoose } from '../formatters.js';

export function safeText(value, fallback = '-') {
  if (value === null || value === undefined) return fallback;

  if (Array.isArray(value)) {
    const clean = value.filter(Boolean).map(String);
    return clean.length ? clean.join(', ') : fallback;
  }

  if (typeof value === 'object') {
    return fallback;
  }

  const text = String(value).trim();
  return text || fallback;
}

export function truncateForPdf(value, max = 80) {
  const text = safeText(value);
  if (text.length <= max) return text;
  return `${text.slice(0, Math.max(0, max - 1)).trim()}…`;
}

export function formatAreaForPdf(item = {}) {
  const areas = [
    ...coerceStringArray(item.area_tecnologica_raw),
    ...coerceStringArray(item.setor_estrategico_raw),
    ...coerceStringArray(item.area),
    ...coerceStringArray(item.perfil_ideal_raw),
  ]
    .map((a) => String(a).trim())
    .filter(Boolean);

  const unique = [...new Set(areas)];
  if (!unique.length) return '-';
  return truncateForPdf(unique.slice(0, 3).join(', '), 55);
}

export function formatLocationForPdf(item = {}) {
  const uf = safeText(item.uf_raw || item.estado_raw || item.estado, '').replace(/^-$/, '');
  const pais = safeText(item.pais_raw || item.pais, '').replace(/^-$/, '');

  if (uf && pais && uf !== pais) return truncateForPdf(`${uf} / ${pais}`, 28);
  if (uf) return truncateForPdf(uf, 28);
  if (pais) return truncateForPdf(pais, 28);

  const regiao = safeText(item.regiao_raw || item.regiao, '');
  if (regiao !== '-') return truncateForPdf(regiao, 28);
  return '-';
}

export function formatSituacaoForPdf(item = {}) {
  const parts = [item.validacao_status_raw, item.situacao_raw]
    .filter((v) => v != null && String(v).trim() !== '')
    .map(String);
  return truncateForPdf(parts.length ? parts.join(' / ') : '-', 40);
}

export function formatPrazoForPdf(item = {}) {
  const raw =
    item.prazo_envio_raw ??
    item.fim_inscricao ??
    item.prazo ??
    item.validade_data ??
    item.data_limite ??
    item.dataLimite;

  if (raw == null || raw === '') return 'Sem prazo';

  const formatted = formatDateLoose(raw);
  return formatted === '-' ? 'Sem prazo' : formatted;
}

export function formatValorForPdf(item = {}) {
  const num = item.valor_principal_num ?? item.valor ?? item.valor_maximo ?? item.valor_total;
  if (num != null && !Number.isNaN(Number(num)) && Number(num) !== 0) {
    return truncateForPdf(formatCurrency(Number(num)), 22);
  }

  const text = safeText(
    item.valor_recurso_raw ?? item.valor_raw ?? item.valor_texto ?? '',
    '',
  );
  return text ? truncateForPdf(text, 22) : '-';
}

export function formatQualidadeForPdf(item = {}) {
  const q = item.qualidade_dado_raw ?? item.qualidade_dado ?? item.quality_score;
  if (q == null || q === '') return '-';
  return truncateForPdf(String(q), 12);
}

export function formatTipoForPdf(item = {}) {
  const tipo =
    item.tipo_oportunidade_raw ||
    item.tipo_oportunidade ||
    item.tipo_recurso_raw ||
    item.tipoRecurso ||
    item.tipo ||
    '';

  return truncateForPdf(tipo, 38);
}

export function formatFonteForPdf(item = {}) {
  const fonte = getFonte(item);
  if (!fonte || fonte === 'Fonte não informada') return '-';
  return truncateForPdf(fonte, 38);
}

export function formatStatusForPdf(item = {}, now = new Date()) {
  return truncateForPdf(getEditalStatusLabel(item, now), 32);
}

export function formatStatusDetailForPdf(item = {}, now = new Date()) {
  return truncateForPdf(getEditalStatusDetailLabels(item, now), 48);
}

export function buildEditaisPdfColumns() {
  return [
    { header: 'Título', dataKey: 'titulo' },
    { header: 'Status', dataKey: 'status' },
    { header: 'Fonte', dataKey: 'fonte' },
    { header: 'Tipo', dataKey: 'tipo' },
    { header: 'Área', dataKey: 'area' },
    { header: 'Local', dataKey: 'local' },
    { header: 'Situação', dataKey: 'situacao' },
    { header: 'Prazo', dataKey: 'prazo' },
    { header: 'Valor', dataKey: 'valor' },
    { header: 'Qual.', dataKey: 'qualidade' },
  ];
}

export function buildEditaisPdfRows(editais = [], now = new Date()) {
  return (Array.isArray(editais) ? editais : []).map((item) => ({
    titulo: truncateForPdf(item?.titulo || item?.title || 'Sem título', 90),
    status: formatStatusForPdf(item, now),
    fonte: formatFonteForPdf(item),
    tipo: formatTipoForPdf(item),
    area: formatAreaForPdf(item),
    local: formatLocationForPdf(item),
    situacao: formatSituacaoForPdf(item),
    prazo: formatPrazoForPdf(item),
    valor: formatValorForPdf(item),
    qualidade: formatQualidadeForPdf(item),
  }));
}

/**
 * Resumo legível dos filtros (uma linha; sem JSON bruto).
 */
export function buildPdfFiltersSummary(filterLines = []) {
  if (!Array.isArray(filterLines) || filterLines.length === 0) {
    return 'Filtros: nenhum filtro aplicado';
  }

  const cleaned = filterLines
    .map((ln) => String(ln || '').trim())
    .filter(
      (ln) =>
        ln &&
        !ln.toLowerCase().includes('nenhum filtro adicional') &&
        !ln.toLowerCase().includes('nenhum filtro aplicado'),
    );

  if (!cleaned.length) return 'Filtros: nenhum filtro aplicado';

  const joined = cleaned.join('; ');
  if (joined.length > 240) {
    return `Filtros: ${joined.slice(0, 220).trim()}…`;
  }
  return `Filtros: ${joined}`;
}
