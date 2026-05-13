/**
 * Notícias — alinhado a `vw_noticias_front` ou tabela `noticia`.
 *
 * @typedef {Object} NoticiaRow
 * @property {string|number} [id]
 * @property {string} [titulo]
 * @property {string} [resumo]
 * @property {string} [link]
 * @property {string} [fonte_recurso]
 * @property {string} [fonte]
 * @property {string[]} [tags]
 * @property {boolean} [ativo]
 * @property {string} [validacao_status]
 * @property {string|null} [data_publicacao]
 * @property {string|null} [prazo_envio]
 */

export const NOTICIA_SHAPE_EXAMPLE = {
  titulo: '',
  link: '',
  ativo: true,
};
