/**
 * Log DEV no clique de links da aba Editais (não altera navegação).
 */

function extrasOf(edital) {
  const ex = edital?.extras_raw ?? edital?.extras;
  return ex && typeof ex === 'object' && !Array.isArray(ex) ? ex : {};
}

/** Snapshot dos campos de URL pedidos na auditoria. */
export function editalLinkClickSnapshot(edital) {
  const ex = extrasOf(edital);
  return {
    id_edital: edital?.id_edital ?? edital?.idNumerico ?? null,
    titulo: edital?.titulo ?? edital?.titulo_original_raw ?? null,
    fonte_recurso: edital?.fonte_recurso_display ?? edital?.fonte_recurso ?? edital?.orgao ?? null,
    link: edital?.link_raw ?? edital?.link ?? edital?.linkOriginal ?? null,
    link_edital: edital?.link_edital_raw ?? edital?.link_edital ?? ex.link_edital ?? null,
    url_documento: edital?.url_documento_raw ?? edital?.url_documento ?? ex.url_documento ?? null,
    pdf_url: edital?.pdf_url_raw ?? edital?.pdfUrl ?? edital?.pdf_url ?? ex.pdf_url ?? null,
    'extras.url_detalhe': ex.url_detalhe ?? null,
    'extras.origem': ex.origem ?? null,
  };
}

/**
 * @param {object} edital
 * @param {{ campoEscolhido: string, urlFinal: string }} meta
 */
export function logEditalLinkClick(edital, { campoEscolhido, urlFinal }) {
  if (!import.meta.env.DEV) return;

  console.log('[edital-link-click]', {
    ...editalLinkClickSnapshot(edital),
    campo_escolhido: campoEscolhido,
    url_final_aberta: urlFinal,
  });
}

/** Handler para <a> — só loga; não chama preventDefault. */
export function onEditalLinkClick(edital, campoEscolhido, urlFinal) {
  return () => {
    logEditalLinkClick(edital, { campoEscolhido, urlFinal });
  };
}

/** Qual campo alimentou o botão "Site" no EditalCard (mesma prioridade do render). */
export function siteLinkCampoEscolhido(edital, actions, orgLabel, orgWebsites) {
  if (actions?.site) return 'link';
  if (!actions?.siteDisabled && edital?.orgSite) return 'orgSite';
  const key = (orgLabel || '').toUpperCase?.() || orgLabel;
  if (!actions?.siteDisabled && orgWebsites?.[key]) return 'ORG_WEBSITES_fallback';
  return 'link';
}
