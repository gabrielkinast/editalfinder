/**
 * Normalização e validação do shape das linhas do Radar (cards / cache / worker).
 */
import { radarPerfPreWorker } from '../radarPerfLog';
import { radarRenderPerfEvent } from '../radarRenderPerfLog';

/** Objeto edital mínimo para CardEditalRadar. */
export function normalizeRadarCardEdital(edital) {
  if (!edital || typeof edital !== 'object') {
    return {
      id: 'unknown',
      titulo: 'Oportunidade sem título',
      orgao: '',
      area: '',
      tipoRecurso: '',
      estado: '',
      link: '',
      linkOriginal: '',
      linkInscricao: '',
      descricao: '',
      objetivo: '',
      temas: '',
      pdfUrl: null,
    };
  }

  const id = edital.id ?? edital.id_edital ?? 'unknown';
  const link =
    edital.link ??
    edital.linkOriginal ??
    edital.link_inscricao ??
    edital.linkInscricao ??
    '';

  return {
    ...edital,
    id,
    titulo: edital.titulo || 'Oportunidade sem título',
    orgao: edital.orgao ?? edital.fonte_recurso ?? edital.fonte ?? '',
    fonte_recurso: edital.fonte_recurso ?? edital.orgao ?? '',
    area: edital.area ?? '',
    tipoRecurso:
      edital.tipoRecurso ??
      edital.tipo_oportunidade ??
      edital.tipo_recurso ??
      '',
    estado: edital.estado ?? edital.uf ?? '',
    dataLimite: edital.dataLimite ?? edital.prazo_envio ?? null,
    prazo_envio: edital.prazo_envio ?? edital.dataLimite ?? null,
    link,
    linkOriginal: edital.linkOriginal ?? link,
    linkInscricao: edital.linkInscricao ?? edital.link_inscricao ?? link,
    descricao: edital.descricao ?? '',
    objetivo: edital.objetivo ?? '',
    temas: edital.temas ?? edital.area ?? '',
    pdfUrl: edital.pdfUrl ?? edital.pdf_url ?? null,
    extras: edital.extras && typeof edital.extras === 'object' ? edital.extras : {},
  };
}

function isValidRadarRow(row) {
  if (!row || typeof row !== 'object') return false;
  if (!row.edital || typeof row.edital !== 'object') return false;
  const id = row.edital.id ?? row.edital.id_edital;
  if (id == null || id === '') return false;
  return true;
}

/**
 * @param {unknown} rows
 * @param {{ source?: string, logInvalid?: boolean }} [opts]
 * @returns {object[]}
 */
export function sanitizeRadarResults(rows, opts = {}) {
  if (!Array.isArray(rows)) {
    if (import.meta.env?.DEV && opts.logInvalid !== false) {
      radarPerfPreWorker('results_shape', {
        source: opts.source ?? 'unknown',
        invalid: true,
        reason: 'not_array',
      });
    }
    return [];
  }

  const out = [];
  let invalid = 0;

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (!isValidRadarRow(row)) {
      invalid += 1;
      if (import.meta.env?.DEV) {
        radarRenderPerfEvent('invalid_item', {
          index: i,
          source: opts.source ?? 'unknown',
          has_edital: !!(row && row.edital),
        });
      }
      continue;
    }

    const score = Number(row.score);
    out.push({
      ...row,
      score: Number.isFinite(score) ? score : 0,
      compatibilidade: row.compatibilidade || 'Baixa',
      razoes: Array.isArray(row.razoes) ? row.razoes : [],
      detalhes: row.detalhes && typeof row.detalhes === 'object' ? row.detalhes : {},
      criterioMeta:
        row.criterioMeta && typeof row.criterioMeta === 'object' ? row.criterioMeta : {},
      radar_badges: Array.isArray(row.radar_badges) ? row.radar_badges : [],
      radar_alertas: Array.isArray(row.radar_alertas) ? row.radar_alertas : [],
      radar_dimensoes: Array.isArray(row.radar_dimensoes) ? row.radar_dimensoes : [],
      razoesPositivas: Array.isArray(row.razoesPositivas)
        ? row.razoesPositivas
        : Array.isArray(row.razoes)
          ? row.razoes.filter((r) => !String(r).startsWith('Atenção'))
          : [],
      radar_penalidades: Array.isArray(row.radar_penalidades) ? row.radar_penalidades : [],
      edital: normalizeRadarCardEdital(row.edital),
    });
  }

  if (import.meta.env?.DEV && (invalid > 0 || opts.logInvalid)) {
    radarPerfPreWorker('results_shape', {
      source: opts.source ?? 'unknown',
      render_results_count: out.length,
      invalid_result_count: invalid,
      input_count: rows.length,
    });
  }

  return out;
}

/** Valida entrada de sessionStorage antes de hidratar UI. */
export function isValidRadarCacheEntry(entry) {
  if (!entry || typeof entry !== 'object') return false;
  if (entry.partial !== false) return false;
  if (!Array.isArray(entry.items) || entry.items.length === 0) return false;
  const validCount = entry.items.filter((it) => isValidRadarRow(it)).length;
  if (validCount === 0) return false;
  if (entry.items.length > 2 && validCount < entry.items.length * 0.5) return false;
  return true;
}
