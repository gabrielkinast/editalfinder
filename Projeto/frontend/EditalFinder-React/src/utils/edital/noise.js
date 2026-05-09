import { normalizeText } from './normalizeText';

/** Rótulos típicos de páginas de banco/menu — ocultados por padrão na lista. */
const RUIDO_TOKENS = [
  'entre em contato',
  'fale conosco',
  'ouvidoria',
  'faq',
  'quem somos',
  'trabalhe conosco',
  'conta pj',
  'conta digital',
  'internet banking',
  'acesse sua conta',
  'abra sua conta',
];

export function isTituloRuidoso(titulo) {
  const t = normalizeText(titulo);
  if (!t || t.length < 8) return false;
  return RUIDO_TOKENS.some((x) => t.includes(x));
}
