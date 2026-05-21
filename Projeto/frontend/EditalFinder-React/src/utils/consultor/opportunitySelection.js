import { radarRowToPrecadPayload } from './radarRowToPrecad';
import {
  MAX_PREPROJECT_OPPORTUNITIES,
  MULTI_OPPORTUNITY_COMPLEMENTARY_LIMIT,
} from './consultorWorkspaceConstants';

export { MAX_PREPROJECT_OPPORTUNITIES, MULTI_OPPORTUNITY_COMPLEMENTARY_LIMIT };

/**
 * Chave estável para seleção: id_edital → link → título+fonte.
 * @param {object} row — linha do Radar
 */
export function getOpportunitySelectionKey(row) {
  const ed = row?.edital || {};
  const id = ed.id ?? ed.id_edital ?? row?.id;
  if (id != null && `${id}` !== '') return `id:${id}`;
  const link = ed.linkOriginal || ed.link || ed.linkInscricao || ed.link_edital;
  if (link && String(link).trim()) return `link:${String(link).trim()}`;
  const titulo = String(ed.titulo || '').trim();
  const fonte = String(ed.orgao || ed.fonte_recurso || '').trim();
  return `hash:${titulo}|${fonte}`.slice(0, 160);
}

function scoreFromRow(row, radarMatch) {
  const n = Number(row?.score);
  if (Number.isFinite(n)) return Math.round(n);
  const p = Number(radarMatch?.scorePct);
  if (Number.isFinite(p)) return Math.round(p);
  return 0;
}

/**
 * Normaliza linha Radar para payload de pré-projeto + metadados de seleção.
 * @param {object} row
 */
export function normalizeSelectedOpportunity(row) {
  const { edital, radarMatch } = radarRowToPrecadPayload(row);
  const ed = row?.edital || {};
  const key = getOpportunitySelectionKey(row);
  const scorePct = scoreFromRow(row, radarMatch);
  const prazo =
    edital.prazo_envio ??
    ed.prazo_envio_raw ??
    ed.dataLimite ??
    '';
  const link = edital.link || '';
  const fonte = edital.fonte_recurso || ed.orgao || '';

  return {
    key,
    row,
    edital,
    radarMatch: { ...radarMatch, scorePct },
    scorePct,
    compatibilidade: row?.compatibilidade || radarMatch?.compatibilidade,
    titulo: edital.titulo || radarMatch?.tituloEdital || '',
    fonte_recurso: fonte,
    prazo_envio: prazo,
    link,
    valor_maximo: edital.valor_maximo,
    matchLinha: row?.matchLinha,
    razoesPositivas: row?.razoesPositivas ?? row?.razoes,
    alertas: row?.alertas ?? radarMatch?.radar_penalidades,
  };
}

/**
 * @param {ReturnType<normalizeSelectedOpportunity>[]} opportunities
 * @param {string} [primaryOpportunityId] — key da principal (opcional)
 */
export function pickPrimaryOpportunity(opportunities, primaryOpportunityId) {
  if (!Array.isArray(opportunities) || opportunities.length === 0) return null;
  if (primaryOpportunityId) {
    const found = opportunities.find((o) => o.key === primaryOpportunityId);
    if (found) return found;
  }
  if (opportunities.length === 1) return opportunities[0];
  return [...opportunities].sort((a, b) => (b.scorePct || 0) - (a.scorePct || 0))[0];
}

/**
 * @param {ReturnType<normalizeSelectedOpportunity>[]} opportunities
 * @param {ReturnType<normalizeSelectedOpportunity>} primary
 */
export function relatedOpportunities(opportunities, primary) {
  if (!primary) return [];
  return opportunities.filter((o) => o.key !== primary.key);
}

/**
 * Agrupa oportunidades para pré-projeto legível (principal + até 5 complementares + observação).
 * @param {ReturnType<normalizeSelectedOpportunity>[]} opportunities
 * @param {ReturnType<normalizeSelectedOpportunity>|null} primary
 */
export function partitionSelectedOpportunities(opportunities, primary) {
  const prim =
    primary || (Array.isArray(opportunities) && opportunities.length ? pickPrimaryOpportunity(opportunities) : null);
  const related = relatedOpportunities(opportunities, prim).sort(
    (a, b) => (b.scorePct || 0) - (a.scorePct || 0),
  );
  return {
    primary: prim,
    complementares: related.slice(0, MULTI_OPPORTUNITY_COMPLEMENTARY_LIMIT),
    observacao: related.slice(MULTI_OPPORTUNITY_COMPLEMENTARY_LIMIT),
    all: opportunities || [],
  };
}

/**
 * Metadados para a barra de seleção no Workspace.
 * @param {ReturnType<normalizeSelectedOpportunity>[]} normalizedList
 */
export function summarizeSelectionForBar(normalizedList) {
  if (!normalizedList?.length) {
    return {
      primary: null,
      primaryTitulo: null,
      primaryScore: null,
      closestDays: null,
      closestTitulo: null,
      semPrazo: 0,
    };
  }
  const primary = pickPrimaryOpportunity(normalizedList);
  let closestDays = null;
  let closestTitulo = null;
  let semPrazo = 0;

  normalizedList.forEach((o) => {
    if (!String(o.prazo_envio || '').trim()) semPrazo += 1;
    const d = o.row?.diasAtePrazo ?? o.radarMatch?.diasAtePrazo;
    if (typeof d === 'number' && d >= 0) {
      if (closestDays === null || d < closestDays) {
        closestDays = d;
        closestTitulo = o.titulo;
      }
    }
  });

  let closestPrazoLabel = null;
  if (closestDays != null) {
    const closestOpp = normalizedList.find((o) => {
      const d = o.row?.diasAtePrazo ?? o.radarMatch?.diasAtePrazo;
      return typeof d === 'number' && d === closestDays;
    });
    const raw = String(closestOpp?.prazo_envio || '').trim();
    if (raw) closestPrazoLabel = raw;
  }

  return {
    primary,
    primaryTitulo: primary?.titulo,
    primaryScore: primary?.scorePct,
    closestDays,
    closestTitulo,
    closestPrazoLabel,
    semPrazo,
  };
}
