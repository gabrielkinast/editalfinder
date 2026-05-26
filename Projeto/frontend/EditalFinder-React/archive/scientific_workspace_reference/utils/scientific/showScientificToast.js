/** @typedef {'success'|'info'|'warning'|'error'} ScientificToastType */

/**
 * Monta payload de toast para o contexto React.
 * @param {string} message
 * @param {ScientificToastType} [type='success']
 */
export function showScientificToastPayload(message, type = 'success') {
  return { message, type };
}

export const SCIENTIFIC_TOAST_MESSAGES = {
  saved: 'Salvo no caderno',
  updated: 'Item atualizado no caderno',
  alreadySaved: 'Item já está no caderno',
  scrollTrilha: 'Indo para Trilha de estudo',
  scrollProjetos: 'Indo para Ideias de projeto',
  scrollCaderno: 'Indo para Caderno',
  scrollFeed: 'Indo para Feed',
  scrollInteresses: 'Indo para Interesses',
  scrollRota: 'Indo para Minha rota',
  briefingRecalc: 'Briefing recalculado',
  modalOpen: 'Caderno aberto',
};
