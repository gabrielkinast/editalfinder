/**
 * Lookup robusto de edital para a tela de detalhe (FRONTEND 1.1F-DETALHE).
 *
 * Funções puras/testáveis: normalização de id, orquestração base → view,
 * classificação de erro. Sem React, sem import.meta.env direto.
 */

export const DETAIL_ERROR_KIND = {
  NOT_FOUND: 'not_found',
  SUPABASE: 'supabase',
  NETWORK: 'network',
  NOT_CONFIGURED: 'not_configured',
};

export const DETAIL_LOOKUP_MODE = {
  BASE: 'base',
  VIEW: 'view',
};

/**
 * Normaliza o parâmetro de rota em candidatos de busca (string/numérico).
 * @param {unknown} routeParam
 */
export function normalizeEditalRouteId(routeParam) {
  if (routeParam == null || routeParam === '') {
    return { routeParam: '', normalizedId: '', candidates: [] };
  }

  const raw = String(routeParam).trim();
  const stripped = raw.replace(/^manual-/i, '');
  const candidates = [];

  const add = (v) => {
    if (v == null || v === '') return;
    const s = typeof v === 'number' ? v : String(v).trim();
    if (s === '') return;
    const key = typeof s === 'number' ? `n:${s}` : `s:${s}`;
    if (candidates.some((c) => c.key === key)) return;
    candidates.push({ key, value: s });
  };

  add(raw);
  add(stripped);

  const num = Number(stripped);
  if (Number.isFinite(num) && num > 0) {
    add(num);
    add(String(num));
  }

  return {
    routeParam: raw,
    normalizedId: stripped,
    candidates: candidates.map((c) => c.value),
  };
}

/**
 * Garante campos esperados pela página de detalhe, independente da origem (base/view).
 * @param {object|null} row
 * @param {'base'|'view'} source
 */
export function normalizeEditalDetailRow(row, source = DETAIL_LOOKUP_MODE.BASE) {
  if (!row || typeof row !== 'object') return null;
  return {
    ...row,
    id_edital: row.id_edital ?? row.id ?? null,
    extras: row.extras ?? row.extras_raw ?? null,
    fonte_recurso: row.fonte_recurso ?? row.fonte ?? null,
    prazo_envio: row.prazo_envio ?? row.fim_inscricao ?? null,
    link: row.link ?? row.link_raw ?? null,
    link_inscricao: row.link_inscricao ?? row.linkInscricao ?? null,
    pdf_url: row.pdf_url ?? row.pdfUrl ?? null,
    _detailLookupSource: source,
  };
}

function isNetworkError(error) {
  const msg = String(error?.message ?? error ?? '').toLowerCase();
  return (
    msg.includes('failed to fetch') ||
    msg.includes('network') ||
    msg.includes('timeout') ||
    msg.includes('fetch')
  );
}

function classifyLookupError(error) {
  if (!error) return null;
  if (isNetworkError(error)) return DETAIL_ERROR_KIND.NETWORK;
  return DETAIL_ERROR_KIND.SUPABASE;
}

/**
 * Executa maybeSingle por candidato em id_edital e, se falhar, em id.
 * @param {object} supabase
 * @param {string} table
 * @param {unknown} candidate
 */
async function queryMaybeSingleById(supabase, table, candidate) {
  for (const column of ['id_edital', 'id']) {
    const { data, error } = await supabase
      .from(table)
      .select('*')
      .eq(column, candidate)
      .maybeSingle();

    if (error) return { data: null, error };
    if (data) return { data, error: null };
  }
  return { data: null, error: null };
}

/**
 * Busca edital na tabela base e, se necessário, na view.
 *
 * @param {object} supabase — cliente Supabase
 * @param {{ routeParam: unknown, viewName?: string, isConfigured?: boolean }} opts
 * @returns {Promise<{
 *   edital: object|null,
 *   errorKind: string|null,
 *   lookupMode: string|null,
 *   routeParam: string,
 *   normalizedId: string,
 *   lookupBaseFound: boolean,
 *   lookupViewFound: boolean,
 *   lookupError: object|null,
 * }>}
 */
export async function lookupEditalForDetail(supabase, opts = {}) {
  const { routeParam, viewName = 'vw_editais_front', isConfigured = true } = opts;
  const norm = normalizeEditalRouteId(routeParam);

  const baseResult = {
    edital: null,
    errorKind: null,
    lookupMode: null,
    routeParam: norm.routeParam,
    normalizedId: norm.normalizedId,
    lookupBaseFound: false,
    lookupViewFound: false,
    lookupError: null,
  };

  if (!isConfigured) {
    return { ...baseResult, errorKind: DETAIL_ERROR_KIND.NOT_CONFIGURED };
  }

  if (!norm.candidates.length) {
    return { ...baseResult, errorKind: DETAIL_ERROR_KIND.NOT_FOUND };
  }

  let lastError = null;

  // 1) Tabela base `edital`
  for (const candidate of norm.candidates) {
    const { data, error } = await queryMaybeSingleById(supabase, 'edital', candidate);
    if (error) {
      lastError = error;
      continue;
    }
    if (data) {
      return {
        ...baseResult,
        edital: normalizeEditalDetailRow(data, DETAIL_LOOKUP_MODE.BASE),
        lookupMode: DETAIL_LOOKUP_MODE.BASE,
        lookupBaseFound: true,
      };
    }
  }

  // 2) Fallback view (mesma origem da listagem)
  for (const candidate of norm.candidates) {
    const { data, error } = await queryMaybeSingleById(supabase, viewName, candidate);
    if (error) {
      lastError = error;
      continue;
    }
    if (data) {
      return {
        ...baseResult,
        edital: normalizeEditalDetailRow(data, DETAIL_LOOKUP_MODE.VIEW),
        lookupMode: DETAIL_LOOKUP_MODE.VIEW,
        lookupViewFound: true,
      };
    }
  }

  if (lastError) {
    return {
      ...baseResult,
      errorKind: classifyLookupError(lastError),
      lookupError: { message: lastError.message, code: lastError.code },
    };
  }

  return { ...baseResult, errorKind: DETAIL_ERROR_KIND.NOT_FOUND };
}

/**
 * Busca anexos sem derrubar o detalhe — retorno estruturado (não lança).
 * @param {object} supabase
 * @param {unknown} routeParam
 * @param {{ isConfigured?: boolean }} [opts]
 */
export async function lookupAnexosForDetail(supabase, routeParam, opts = {}) {
  const { isConfigured = true } = opts;
  const norm = normalizeEditalRouteId(routeParam);

  if (!isConfigured) {
    return { ok: false, data: [], error: { message: 'not_configured' } };
  }

  let lastError = null;

  for (const candidate of norm.candidates) {
    const { data, error } = await supabase
      .from('edital_anexo')
      .select('*')
      .eq('id_edital', candidate)
      .order('criado_em', { ascending: true });

    if (error) {
      lastError = error;
      continue;
    }
    return { ok: true, data: data || [], error: null };
  }

  return {
    ok: false,
    data: [],
    error: lastError
      ? { message: lastError.message, code: lastError.code }
      : { message: 'anexos_not_found' },
  };
}

/**
 * Mensagem amigável para a UI conforme errorKind.
 * @param {string|null} errorKind
 */
export function getEditalDetailErrorMessage(errorKind) {
  switch (errorKind) {
    case DETAIL_ERROR_KIND.NOT_FOUND:
      return 'Não encontramos este edital no catálogo atual.';
    case DETAIL_ERROR_KIND.NETWORK:
    case DETAIL_ERROR_KIND.SUPABASE:
      return 'Não foi possível carregar os dados do edital agora.';
    case DETAIL_ERROR_KIND.NOT_CONFIGURED:
      return 'Não foi possível carregar os dados do edital agora.';
    default:
      return 'Não foi possível carregar os dados do edital.';
  }
}
