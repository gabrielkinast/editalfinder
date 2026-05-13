import { normalizeText } from './normalizeText';
import { coerceStringArray } from './coerceArrays';
import { getFonte } from './editalFieldHelpers';

export function tokenizeSearchQuery(q) {
  if (!q || typeof q !== 'string') return [];
  return normalizeText(q)
    .split(/\s+/)
    .filter((t) => t.length >= 2);
}

function joinHaystack(edital) {
  const parts = [
    edital.titulo_original_raw ?? '',
    edital.titulo,
    edital.descricao,
    getFonte(edital),
    edital.fonte_recurso_display,
    edital.fonte_raw,
    edital.tipo_oportunidade_raw,
    edital.tipo_recurso_raw,
    edital.tipo_recurso_label,
    edital.area,
    edital.area_cientifica_raw,
    edital.area_tecnologica_list?.join?.(' ') ?? '',
    edital.setor_estrategico_list?.join?.(' ') ?? '',
    coerceStringArray(edital.perfil_ideal_raw).join(' '),
    edital.publico_alvo_raw,
    edital.codigo_oportunidade_raw,
    edital.numero_edital_raw,
    edital.numero_chamada_raw,
    ...coerceStringArray(edital.publico_alvo_arr_raw),
    edital.setor_estrategico_flat,
    edital.area_tecnologica_flat,
  ];

  const block = normalizeText(parts.filter(Boolean).join(' | '));
  return block;
}

/** Todas as palavras devem aparecer em algum lugar do “texto combinado”. */
export function editalMatchesAllSearchTokens(edital, tokens) {
  if (!tokens.length) return true;
  const hay = joinHaystack(edital);
  return tokens.every((t) => hay.includes(t));
}
