/**
 * Pré-filtro anti-ruído do catálogo Radar (Fase 0.9A).
 * Remove itens do cálculo sem alterar banco nem regras de score dos válidos.
 */
import { RADAR_PREFILTER_VERSION } from '../../constants/radarPrefilter.js';

const STRONG_SIGNAL_TERMS = [
  'chamada publica',
  'chamada pública',
  'edital de fomento',
  'subvencao',
  'subvenção',
  'bolsa',
  'programa',
  'financiamento',
  'inovacao',
  'inovação',
  'cnpq',
  'finep',
  'capes',
  'fapergs',
  'fapesc',
  'fapesp',
  'mcti',
  'senai',
  'embrapii',
  'bndes',
  'internacional',
  'fomento',
  'credito',
  'crédito',
  'linha de credito',
];

const INVALID_TYPE_EXACT = [
  'noticia',
  'pesquisa',
  'institucional',
  'portal',
  'relatorio',
  'publicacao',
];

const GENERIC_TITLE_RE =
  /^[\s\-–—]*(edital|chamada|resultado|retificacao|retificação|comunicado)[\s\-–—.!?:]*$/i;

const MAX_REJECTED_SAMPLE = 12;

function normalizar(text) {
  return String(text ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

function diasAtePrazo(prazo) {
  if (!prazo) return null;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const data = new Date(prazo);
  if (Number.isNaN(data.getTime())) return null;
  data.setHours(0, 0, 0, 0);
  return Math.ceil((data.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));
}

function pickId(e) {
  return e?.id ?? e?.id_edital ?? null;
}

function pickTitulo(e) {
  return (e?.titulo ?? e?.titulo_original_raw ?? '').trim();
}

function pickPrazo(e) {
  return (
    e?.prazo_envio ??
    e?.prazo_envio_raw ??
    e?.dataLimite ??
    e?.fim_inscricao_raw ??
    e?.fim_inscricao ??
    null
  );
}

function pickStatusPrazo(e) {
  return normalizar(e?.status_prazo ?? e?.statusPrazo ?? '');
}

function pickLinks(e) {
  return [
    e?.link,
    e?.link_raw,
    e?.linkOriginal,
    e?.link_inscricao,
    e?.linkInscricao,
    e?.link_edital,
    e?.url_documento,
    e?.pdf_url,
    e?.pdfUrl,
    e?.pdf_url_raw,
  ].filter((x) => x != null && String(x).trim() !== '');
}

function normalizeLinkForDedup(url) {
  try {
    const s = String(url).trim();
    if (!s) return '';
    const u = new URL(s.startsWith('http') ? s : `https://${s}`);
    const host = u.hostname.replace(/^www\./, '');
    const path = u.pathname.replace(/\/+$/, '') || '/';
    return `${host}${path}${u.search}`.toLowerCase();
  } catch {
    return normalizar(String(url).replace(/\s+/g, ''));
  }
}

function normalizeTitleForDedup(titulo, fonte) {
  const t = normalizar(titulo).replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
  const f = normalizar(fonte).slice(0, 40);
  return `${t}|${f}`;
}

function pickFonte(e) {
  return (
    e?.orgao ??
    e?.fonte_recurso_display ??
    e?.fonte_recurso ??
    e?.fonte_raw ??
    e?.fonte ??
    ''
  );
}

function textoBusca(e) {
  const parts = [
    pickTitulo(e),
    e?.descricao,
    e?.objetivo,
    e?.area,
    e?.temas,
    pickFonte(e),
    e?.tipo_oportunidade_raw,
    e?.tipo_recurso_raw,
    e?.tipo_recurso,
    e?.tipoRecurso,
    e?.tags,
    e?.origem_portal_raw,
  ];
  return normalizar(parts.filter(Boolean).join(' '));
}

export function hasStrongStrategicSignals(e) {
  const blob = textoBusca(e);
  return STRONG_SIGNAL_TERMS.some((term) => blob.includes(normalizar(term)));
}

export function isStrategicSourceMarked(e) {
  if (e?.fonte_estrategica || e?.estrategica || e?.prioridade_estrategica) return true;
  const ex = e?.extras_raw ?? e?.extras;
  if (ex && typeof ex === 'object') {
    if (ex.fonte_estrategica || ex.estrategico || ex.wave_estrategica) return true;
  }
  const tags = Array.isArray(e?.tags) ? e.tags.join(' ') : String(e?.tags ?? '');
  return /estrateg/i.test(tags) || /priorit/i.test(normalizar(e?.origem_portal_raw ?? ''));
}

function hasUsefulLink(e) {
  return pickLinks(e).length > 0;
}

function hasRichDescription(e) {
  const d = String(e?.descricao ?? '').trim();
  return d.length >= 180;
}

function isExpired(e, options) {
  if (options?.includeExpired || options?.incluirEncerrados) return false;
  const st = pickStatusPrazo(e);
  if (st === 'encerrado' || st === 'expirado' || st === 'vencido') return true;
  const dias = diasAtePrazo(pickPrazo(e));
  if (dias !== null && dias < 0) return true;
  const situacao = normalizar(e?.situacao_raw ?? e?.situacao ?? e?.status_raw ?? '');
  if (/encerr|finaliz|fechad|concluid|cancelad|expirad/.test(situacao)) return true;
  if (e?.ativo === false && !options?.includeExpired) return true;
  return false;
}

function invalidTypeReason(e) {
  if (hasStrongStrategicSignals(e)) return null;
  const tipo = normalizar(
    [
      e?.tipo_oportunidade_raw,
      e?.tipo_oportunidade,
      e?.tipo_recurso_raw,
      e?.tipo_recurso,
      e?.tipoRecurso,
    ]
      .filter(Boolean)
      .join(' '),
  );
  for (const marker of INVALID_TYPE_EXACT) {
    if (
      tipo === marker ||
      tipo.startsWith(`${marker} `) ||
      tipo.endsWith(` ${marker}`) ||
      tipo.includes(` ${marker} `)
    ) {
      return marker;
    }
  }
  const blob = textoBusca(e);
  if (/\bnoticia\b/.test(blob) && !/chamada|edital|fomento|financiamento/.test(blob)) {
    return 'noticia';
  }
  return null;
}

function isLowQuality(e, options) {
  if (hasStrongStrategicSignals(e) || isStrategicSourceMarked(e)) return false;
  const vs = normalizar(e?.validacao_status ?? e?.validacao_status_raw ?? '');
  if (vs === 'incompleto') return true;
  const q = Number(e?.qualidade_dado ?? e?.qualidade_dado_raw);
  if (Number.isFinite(q) && q < 22) return true;
  const semPrazo = diasAtePrazo(pickPrazo(e)) == null && !pickPrazo(e);
  const semArea = !String(e?.area ?? e?.temas ?? '').trim();
  if (semPrazo && semArea && !hasUsefulLink(e)) return true;
  return false;
}

function isGenericTitle(e) {
  const t = pickTitulo(e);
  if (!t) return true;
  if (GENERIC_TITLE_RE.test(t)) return true;
  if (t.length < 8 && !hasStrongStrategicSignals(e)) return true;
  return false;
}

function emptyStats(catalogTotal) {
  return {
    version: RADAR_PREFILTER_VERSION,
    catalog_total: catalogTotal,
    after_existing_filters: catalogTotal,
    removed_expired: 0,
    removed_invalid_type: 0,
    removed_missing_link: 0,
    removed_duplicate: 0,
    removed_low_quality: 0,
    removed_generic_title: 0,
    sent_to_worker: catalogTotal,
  };
}

function pushSample(sample, item, reason, extra = {}) {
  if (sample.length >= MAX_REJECTED_SAMPLE) return;
  sample.push({
    id: pickId(item),
    titulo: pickTitulo(item)?.slice(0, 120),
    fonte: pickFonte(item)?.slice(0, 60),
    reason,
    ...extra,
  });
}

/**
 * @param {object[]} editais
 * @param {object} [options]
 * @param {boolean} [options.includeExpired]
 * @param {boolean} [options.incluirEncerrados]
 * @returns {{ items: object[], stats: object, rejectedSample: object[] }}
 */
export function prefilterRadarCatalog(editais, options = {}) {
  const list = Array.isArray(editais) ? editais : [];
  const stats = emptyStats(list.length);
  const rejectedSample = [];
  const seenLink = new Set();
  const seenTitleFonte = new Set();
  const seenHash = new Set();

  const viable = [];
  for (const e of list) {
    if (!e || typeof e !== 'object') continue;
    const titulo = pickTitulo(e);
    const id = pickId(e);
    if (!titulo && id == null) continue;
    if (!titulo && id != null) continue;
    viable.push(e);
  }
  stats.after_existing_filters = viable.length;

  const items = [];

  for (const e of viable) {
    let reason = null;

    if (isExpired(e, options)) {
      reason = 'expired';
      stats.removed_expired += 1;
    } else if (!hasUsefulLink(e) && !(pickId(e) && hasRichDescription(e))) {
      reason = 'missing_link';
      stats.removed_missing_link += 1;
    } else {
      const tipoInv = invalidTypeReason(e);
      if (tipoInv) {
        reason = 'invalid_type';
        stats.removed_invalid_type += 1;
        pushSample(rejectedSample, e, reason, { tipo: tipoInv });
      }
    }

    if (!reason && isGenericTitle(e) && !hasStrongStrategicSignals(e)) {
      reason = 'generic_title';
      stats.removed_generic_title += 1;
    }

    if (!reason && isLowQuality(e, options)) {
      reason = 'low_quality';
      stats.removed_low_quality += 1;
    }

    if (!reason) {
      const hashDedup =
        e?.hash_deduplicacao ??
        (e?.extras_raw && typeof e.extras_raw === 'object'
          ? e.extras_raw.hash_deduplicacao
          : null);
      const links = pickLinks(e);
      const linkKey = links.map(normalizeLinkForDedup).find(Boolean) || '';
      const titleKey = normalizeTitleForDedup(pickTitulo(e), pickFonte(e));
      const hashKey = hashDedup ? String(hashDedup) : '';

      if (hashKey && seenHash.has(hashKey)) {
        reason = 'duplicate';
      } else if (linkKey && seenLink.has(linkKey)) {
        reason = 'duplicate';
      } else if (titleKey.length > 10 && seenTitleFonte.has(titleKey)) {
        reason = 'duplicate';
      }

      if (reason === 'duplicate') {
        stats.removed_duplicate += 1;
      } else {
        if (hashKey) seenHash.add(hashKey);
        if (linkKey) seenLink.add(linkKey);
        if (titleKey.length > 10) seenTitleFonte.add(titleKey);
        items.push(e);
      }
    }

    if (reason) {
      if (reason !== 'invalid_type' || rejectedSample.length < MAX_REJECTED_SAMPLE) {
        pushSample(rejectedSample, e, reason);
      }
    }
  }

  stats.sent_to_worker = items.length;
  return { items, stats, rejectedSample };
}

/** Logs DEV [radar-noise]. */
export function logRadarCatalogNoise(stats, rejectedSample = []) {
  if (!import.meta.env?.DEV || !stats) return;
  const payload = {
    version: stats.version,
    catalog_total: stats.catalog_total,
    after_existing_filters: stats.after_existing_filters,
    removed_expired: stats.removed_expired,
    removed_invalid_type: stats.removed_invalid_type,
    removed_missing_link: stats.removed_missing_link,
    removed_duplicate: stats.removed_duplicate,
    removed_low_quality: stats.removed_low_quality,
    removed_generic_title: stats.removed_generic_title,
    sent_to_worker: stats.sent_to_worker,
    reduction_pct:
      stats.catalog_total > 0
        ? Math.round((100 * (stats.catalog_total - stats.sent_to_worker)) / stats.catalog_total)
        : 0,
  };
  console.info('[radar-noise] summary', payload);
  console.info('[radar-noise] catalog_total', stats.catalog_total);
  console.info('[radar-noise] after_existing_filters', stats.after_existing_filters);
  console.info('[radar-noise] removed_expired', stats.removed_expired);
  console.info('[radar-noise] removed_invalid_type', stats.removed_invalid_type);
  console.info('[radar-noise] removed_missing_link', stats.removed_missing_link);
  console.info('[radar-noise] removed_duplicate', stats.removed_duplicate);
  console.info('[radar-noise] removed_low_quality', stats.removed_low_quality);
  console.info('[radar-noise] sent_to_worker', stats.sent_to_worker);
  if (rejectedSample?.length) {
    console.info('[radar-noise] rejected_sample', rejectedSample);
  }
}
