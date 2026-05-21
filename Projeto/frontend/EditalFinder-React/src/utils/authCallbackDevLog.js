const IS_DEV = import.meta.env?.DEV;

export function authCallbackLog(event, payload = {}) {
  if (!IS_DEV) return;
  const safe = { ...payload };
  delete safe.access_token;
  delete safe.refresh_token;
  delete safe.code;
  console.info(`[auth-callback] ${event}`, safe);
}
