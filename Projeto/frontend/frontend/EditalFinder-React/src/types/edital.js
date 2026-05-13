/**
 * Modelo de referência — linha típica após `mapRawEditalRow` / uso na UI.
 * Os nomes reais vêm de `vw_editais_front` ou `edital`; campos opcionais conforme RLS/fonte.
 *
 * @typedef {Object} EditalUiModel
 * @property {string|number} [id]
 * @property {string} [titulo]
 * @property {string} [descricao]
 * @property {string} [linkOriginal]
 * @property {string} [fonte_recurso_display]
 * @property {string|null} [prazo_envio_raw]
 * @property {boolean} [ativo]
 * @property {string} [validacao_status_raw]
 * @property {string|null} [tipo_oportunidade_raw]
 */

/** Exemplo mínimo só para documentação / testes manuais de forma. */
export const EDITAL_SHAPE_EXAMPLE = {
  id: undefined,
  titulo: '',
  descricao: '',
  linkOriginal: '',
  ativo: true,
};
