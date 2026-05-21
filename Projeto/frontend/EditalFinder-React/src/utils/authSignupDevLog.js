/**
 * Logs seguros do fluxo de cadastro (somente DEV).
 * Nunca registra senha nem tokens completos.
 */
const IS_DEV = import.meta.env?.DEV;

export function authSignupDevLog(phase, payload = {}) {
  if (!IS_DEV) return;
  const safe = { ...payload };
  delete safe.password;
  delete safe.senha;
  delete safe.access_token;
  if (safe.session) {
    safe.session = {
      exists: true,
      expires_at: safe.session.expires_at ?? null,
    };
  }
  console.info(`[auth-signup] ${phase}`, safe);
}

export function formatSupabaseError(err) {
  if (!err) return {};
  return {
    code: err.code ?? null,
    message: err.message ?? null,
    details: err.details ?? null,
    hint: err.hint ?? null,
  };
}
