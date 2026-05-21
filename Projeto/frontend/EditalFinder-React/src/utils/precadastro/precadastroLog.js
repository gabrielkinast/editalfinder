/**
 * Logs DEV do módulo pré-projeto (Cadastros).
 */
export function logPrecadastro(event, payload = {}) {
  if (!import.meta.env.DEV) return;
  console.info('[precadastro]', event, payload);
}
