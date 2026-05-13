/**
 * Portais estratégicos — previsto para `vw_fornecedores_front` / `vw_investimentos_front`
 * ou `portal_estrategico` (contrato depende do cluster).
 *
 * @typedef {Object} PortalEstrategicoRow
 * @property {string|number} [id]
 * @property {string} [titulo]
 * @property {string} [link]
 * @property {string} [portal_tipo]
 * @property {string} [frontend_section]
 * @property {boolean} [mostrar_no_radar]
 * @property {string} [validacao_status]
 * @property {string} [acesso_tipo]
 * @property {Record<string, unknown>} [extras]
 */

export const PORTAL_ESTRATEGICO_SHAPE_EXAMPLE = {
  titulo: '',
  link: '',
  mostrar_no_radar: false,
  extras: {},
};
