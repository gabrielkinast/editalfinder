/**
 * extras.curadoria_front — visibilidade na aba Editais (auditoria global).
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

function extrasOf(edital) {
  const ex = edital?.extras_raw ?? edital?.extras;
  return ex && typeof ex === 'object' && !Array.isArray(ex) ? ex : null;
}

export function getCuradoriaFront(edital) {
  const cf = extrasOf(edital)?.curadoria_front;
  return cf && typeof cf === 'object' ? cf : null;
}

export function isCuradoriaHidden(edital) {
  const vis = String(getCuradoriaFront(edital)?.visibility || '').toLowerCase();
  return HIDDEN.has(vis);
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
  let reviewPrazo = 0;
  let linkBroken = 0;
  const byFonteHidden = new Map();

  for (const e of list) {
    if (isCuradoriaHidden(e)) {
      hiddenCuradoria += 1;
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
    badge_revisar_prazo: reviewPrazo,
    link_indisponivel_metadado: linkBroken,
    fontes_com_mais_ocultos_no_payload: [...byFonteHidden.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([fonte, n]) => ({ fonte, n })),
    nota: 'Itens já filtrados pela view não aparecem nesta contagem.',
  });
}
