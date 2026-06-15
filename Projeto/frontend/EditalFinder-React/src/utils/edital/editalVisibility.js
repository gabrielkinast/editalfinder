/**
 * extras.curadoria_front — visibilidade na aba Editais (auditoria global).
 * FRONTEND 10.3C: filtro defensivo para duplicatas ocultas (boolean + visibility).
 */

const HIDDEN = new Set([
  'hidden_institutional',
  'hidden_historical',
  'hidden_resultado',
  'hidden_invalid_link',
  'hidden_not_opportunity',
  'hidden_duplicate',
  'hidden_expired',
]);

const BROKEN_LINK = new Set([
  'broken_404',
  'broken_spa_not_found',
  'timeout',
  'invalid_url',
]);

/** @param {unknown} raw */
function parseExtrasObject(raw) {
  if (raw == null || raw === '') return null;
  if (typeof raw === 'object' && !Array.isArray(raw)) return raw;
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed;
    } catch {
      return null;
    }
  }
  return null;
}

/** @param {unknown} edital */
function extrasOf(edital) {
  if (!edital || typeof edital !== 'object') return null;
  return parseExtrasObject(edital.extras_raw ?? edital.extras);
}

/** @param {unknown} val */
function isTruthyHiddenDuplicateFlag(val) {
  return val === true || val === 'true' || val === 1 || val === '1';
}

/**
 * @param {Record<string, unknown> | null | undefined} cf
 */
export function isHiddenDuplicateCuradoria(cf) {
  if (!cf || typeof cf !== 'object') return false;
  if (isTruthyHiddenDuplicateFlag(cf.hidden_duplicate)) return true;
  return String(cf.visibility || '').toLowerCase() === 'hidden_duplicate';
}

/**
 * @param {unknown} edital
 */
export function getCuradoriaFront(edital) {
  const cf = extrasOf(edital)?.curadoria_front;
  return cf && typeof cf === 'object' && !Array.isArray(cf) ? cf : null;
}

/**
 * True se o edital deve ficar oculto nas listas públicas (curadoria).
 * @param {unknown} edital
 */
export function isCuradoriaHidden(edital) {
  const cf = getCuradoriaFront(edital);
  if (!cf) return false;
  if (isHiddenDuplicateCuradoria(cf)) return true;
  const vis = String(cf.visibility || '').toLowerCase();
  return HIDDEN.has(vis);
}

/**
 * Remove editais ocultos por curadoria (duplicatas e demais flags hidden_*).
 * @param {unknown[]} catalog
 */
export function filterPublicVisibleEditais(catalog) {
  return (catalog ?? []).filter((e) => !isCuradoriaHidden(e));
}

export function showReviewPrazoBadge(edital) {
  const vis = String(getCuradoriaFront(edital)?.visibility || '').toLowerCase();
  return vis === 'review_missing_deadline';
}

export function isLinkUnavailableFromCuradoria(edital) {
  const vis = String(getCuradoriaFront(edital)?.visibility || '').toLowerCase();
  if (vis === 'hidden_invalid_link') return true;
  const lh = extrasOf(edital)?.link_health;
  const st = String(lh?.link_status || '').toLowerCase();
  return BROKEN_LINK.has(st);
}

/**
 * Log DEV após carga da view (comparar com totais da auditoria).
 */
export function logEditaisVisibilityDev(editals, { source = 'vw_editais_front' } = {}) {
  if (!import.meta.env.DEV) return;
  const list = editals ?? [];
  let hiddenCuradoria = 0;
  let hiddenDuplicate = 0;
  let reviewPrazo = 0;
  let linkBroken = 0;
  const byFonteHidden = new Map();

  for (const e of list) {
    if (isCuradoriaHidden(e)) {
      hiddenCuradoria += 1;
      if (isHiddenDuplicateCuradoria(getCuradoriaFront(e))) hiddenDuplicate += 1;
      const f = e.fonte_recurso_display || e.orgao || '—';
      byFonteHidden.set(f, (byFonteHidden.get(f) || 0) + 1);
    }
    if (showReviewPrazoBadge(e)) reviewPrazo += 1;
    if (isLinkUnavailableFromCuradoria(e)) linkBroken += 1;
  }

  console.info('[editais-visibility]', {
    source,
    total_recebido: list.length,
    visiveis_na_view: list.length,
    ocultos_por_curadoria_no_payload: hiddenCuradoria,
    ocultos_hidden_duplicate: hiddenDuplicate,
    badge_revisar_prazo: reviewPrazo,
    link_indisponivel_metadado: linkBroken,
    fontes_com_mais_ocultos_no_payload: [...byFonteHidden.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([fonte, n]) => ({ fonte, n })),
    nota: 'Itens já filtrados pela view ou getEditais não aparecem nesta contagem.',
  });
}
