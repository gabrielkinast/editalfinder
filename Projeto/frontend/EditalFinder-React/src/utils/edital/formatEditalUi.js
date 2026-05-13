import { coerceStringArray } from './coerceArrays';
import { formatDateLoose } from '../formatters';
import { humanizeTechnicalLabel } from '../portaisDisplayLabels';

const TIPO_SHOW = new Map([
  ['subvencao', 'Subvenção'],
  ['subvenção econômica', 'Subvenção'],
  ['credito', 'Crédito'],
  ['financiamento', 'Financiamento'],
  ['grant', 'Grant'],
  ['oportunidade_fornecedor', 'Fornecedor'],
  ['licitação', 'Licitação'],
  ['licitacao', 'Licitação'],
]);

/** Lista de slugs/snake_case (array, JSON, CSV) → texto legível para cards e resumos. */
export function humanizeTaxonomyList(val) {
  const parts = coerceStringArray(val)
    .map((s) => humanizeTechnicalLabel(s))
    .filter((s) => s && s !== '—');
  return parts.length ? parts.join(', ') : '';
}

export function formatTipoAmigavel(key) {
  if (!key) return '';
  const k = String(key).toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_');
  if (TIPO_SHOW.has(k)) return TIPO_SHOW.get(k);
  return String(key).replace(/_/g, ' ');
}

export function getValorRepresentativoNumerico(edital) {
  const v =
    edital.valor_estimado_raw ??
    edital.valor_total_raw ??
    edital.valor_maximo_raw ??
    edital.valorMaximo ??
    edital.valor;
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

export function resumirEdital(edital) {
  const partes = [];
  const tipoR = formatTipoAmigavel(edital.tipo_recurso_raw || edital.tipoRecurso);
  if (tipoR) partes.push(tipoR);

  const perf = coerceStringArray(edital.perfil_ideal_raw);
  if (perf.length) partes.push(`Para ${perf.slice(0, 2).join(', ')}`);

  const setorHum = humanizeTaxonomyList(edital.setor_estrategico_raw ?? edital.setor_estrategico_list);
  if (setorHum) partes.push(`Setor: ${setorHum.split(', ').slice(0, 2).join(', ')}`);

  const prazo = edital.prazo_envio_raw || edital.dataLimite;
  if (prazo) partes.push(`Prazo: ${formatDateLoose(prazo)}`);
  else partes.push('Prazo não informado');

  return partes.join(' • ');
}
