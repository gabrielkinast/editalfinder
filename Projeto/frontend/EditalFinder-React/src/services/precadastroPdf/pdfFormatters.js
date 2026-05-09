/**
 * Saida compativel com fonte Helvetica padrao do jsPDF (evita simbolos Unicode que viram "?").
 */

export const LABEL_NAO_INFORMADO = 'Nao informado';

/** Marca opcao marcada/desmarcada somente ASCII */
export function checkAscii(checked) {
  return checked ? '[x]' : '[ ]';
}

export function stripUnsafePdfChars(text) {
  if (text == null) return '';
  return String(text)
    .replace(/\u2013|\u2014/g, '-')
    .replace(/\u2026/g, '...')
    .replace(/[\u2600-\u27BF]/g, '') // assorted symbols
    .replace(/\r\n/g, '\n');
}

/**
 * Texto principal: vazio -> Nao informado (evita "?" e tracos repetidos).
 * @param {*} v
 */
export function valEssential(v) {
  const s = stripUnsafePdfChars(v);
  if (s.trim() === '') return LABEL_NAO_INFORMADO;
  return s;
}

/** Opcional vazio -> null (omitir linha na tabela) */
export function valOptional(v) {
  const s = stripUnsafePdfChars(v);
  const t = s.trim();
  if (t === '') return null;
  return s;
}

export function yesNoLabel(v) {
  if (v === true || v === 'sim' || v === 'Sim' || v === 'SIM') return 'Sim';
  if (v === false || v === 'nao' || v === 'Nao' || v === 'NAO') return 'Nao';
  const s = stripUnsafePdfChars(v).trim();
  return s === '' ? null : s;
}
