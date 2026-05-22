import { getFonte } from '../edital/editalFieldHelpers';
import { collectDeadlineCandidates, extractDashboardDeadline } from './dashboardDeadlineFields';
import {
  classifyContentScope,
  getDashboardEditalType,
  getDashboardSourceScope,
} from './dashboardClassification';

const SAMPLE = 5;

/**
 * @param {Map<string, number>} map
 * @param {string} key
 * @param {number} [n=1]
 */
function bump(map, key, n = 1) {
  map.set(key, (map.get(key) || 0) + n);
}

/**
 * @param {Map<string, number>} map
 * @param {number} limit
 */
function topFromMap(map, limit = 10) {
  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([label, count]) => ({ label, count }));
}

/**
 * @param {Array<object>} editais
 * @param {Array<object>} noticias
 * @param {Array<object>} pesquisas
 */
export function auditDashboardDataQuality({ editais = [], noticias = [], pesquisas = [] } = {}) {
  const list = Array.isArray(editais) ? editais : [];
  const prazoFields = new Map();
  let withPrazo = 0;
  let withoutPrazo = 0;
  const samplesWithoutPrazo = [];
  const samplesWithPrazo = [];
  const tipoRaw = new Map();
  const tipoNormalized = new Map();
  const fonteMap = new Map();
  const scopeMap = new Map();

  for (const e of list) {
    const dl = extractDashboardDeadline(e);
    if (dl.status === 'sem_prazo' || dl.status === 'prazo_invalido') {
      withoutPrazo += 1;
      if (samplesWithoutPrazo.length < SAMPLE) {
        samplesWithoutPrazo.push({
          id: e.id_edital ?? e.id,
          titulo: (e.titulo || '').slice(0, 80),
          status: dl.status,
          candidates: collectDeadlineCandidates(e).map((c) => c.field),
        });
      }
    } else {
      withPrazo += 1;
      if (dl.sourceField) bump(prazoFields, dl.sourceField);
      if (samplesWithPrazo.length < SAMPLE) {
        samplesWithPrazo.push({
          id: e.id_edital ?? e.id,
          field: dl.sourceField,
          raw: dl.rawValue,
          status: dl.status,
        });
      }
    }

    const rawTipo = [
      e.tipo_recurso_raw,
      e.tipo_oportunidade_raw,
      e.area,
      e.tipo,
      e.modalidade_financiamento_raw,
    ]
      .filter(Boolean)
      .join(' | ');
    if (rawTipo) bump(tipoRaw, rawTipo.slice(0, 120));
    bump(tipoNormalized, getDashboardEditalType(e));

    const fonte = getFonte(e);
    bump(fonteMap, fonte.slice(0, 80));
    bump(scopeMap, getDashboardSourceScope(e));
  }

  const normalizedValues = topFromMap(tipoNormalized, 15);
  const suspiciousRepeatedLabels = normalizedValues
    .filter((x) => x.label.includes('Tecnologia e Inova') || x.label.endsWith('…'))
    .map((x) => x.label);

  const topFontes = topFromMap(fonteMap, 12);
  const intCount = scopeMap.get('internacional') || 0;
  const brCount = scopeMap.get('brasil') || 0;

  const auditNoticias = auditContentList(noticias);
  const auditPesquisas = auditContentList(pesquisas);

  const warnings = [];
  const semPrazoPct = list.length ? withoutPrazo / list.length : 0;
  if (semPrazoPct > 0.65) {
    warnings.push(
      `Muitos editais sem prazo estruturado (${Math.round(semPrazoPct * 100)}%). Verifique parser/backend.`,
    );
  }
  if (suspiciousRepeatedLabels.length) {
    warnings.push('Labels de tipo suspeitos (truncamento ou área repetida).');
  }
  if (intCount > brCount * 2 && list.length > 50) {
    warnings.push('Predominância internacional nas fontes do catálogo.');
  }

  return {
    editais: {
      total: list.length,
      prazo: {
        withPrazo,
        withoutPrazo,
        fieldsDetected: topFromMap(prazoFields, 12),
        samplesWithoutPrazo,
        samplesWithPrazo,
      },
      tipo: {
        fieldsDetected: ['tipo_recurso_raw', 'tipo_oportunidade_raw', 'tipoRecurso', 'modalidade', 'categoria', 'titulo'],
        topRawValues: topFromMap(tipoRaw, 12),
        normalizedValues,
        suspiciousRepeatedLabels,
      },
      fonte: {
        topFontes,
        possibleCountrySignals: topFromMap(scopeMap, 4),
        internationalDominance: list.length
          ? { internacional: intCount, brasil: brCount, ratio: intCount / Math.max(1, brCount) }
          : null,
      },
    },
    noticias: auditNoticias,
    pesquisas: auditPesquisas,
    warnings,
  };
}

/**
 * @param {Array<object>} items
 */
function auditContentList(items) {
  const list = Array.isArray(items) ? items : [];
  let possibleBrazilCount = 0;
  let possibleInternationalCount = 0;
  const sources = new Map();
  const tags = new Map();

  for (const item of list) {
    const scope = classifyContentScope(item);
    if (scope === 'brasil') possibleBrazilCount += 1;
    if (scope === 'internacional') possibleInternationalCount += 1;
    const src = item.fonte || item.source || item.orgao || item.publisher || '—';
    bump(sources, String(src).slice(0, 60));
    const tag = item.categoria || item.area || item.tipo || '';
    if (tag) bump(tags, String(tag).slice(0, 40));
  }

  return {
    total: list.length,
    possibleBrazilCount,
    possibleInternationalCount,
    topSources: topFromMap(sources, 8),
    topTags: topFromMap(tags, 8),
  };
}

/**
 * @param {ReturnType<typeof auditDashboardDataQuality>} audit
 */
export function logDashboardDataQualityAudit(audit) {
  if (!import.meta.env.DEV) return;
  console.info('[dashboard] data_quality_audit', audit);
}
