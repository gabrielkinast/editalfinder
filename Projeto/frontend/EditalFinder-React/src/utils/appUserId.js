/**
 * Resolve id_usuario (bigint em public.usuario) a partir do perfil da app (AuthContext.user).
 * Nunca usar auth.users.id (UUID).
 */

/**
 * @param {object|null|undefined} appUser — perfil interno (AuthContext `user`)
 * @param {number|string|null|undefined} [override] — id explícito (ex. hook de favoritos)
 * @returns {number|null}
 */
export function resolveAppUserId(appUser, override) {
  if (override != null && override !== '') {
    const o = Number(override);
    if (Number.isFinite(o) && o > 0) return o;
  }

  if (!appUser || typeof appUser !== 'object') return null;

  const raw = appUser.id_usuario ?? appUser.idUsuario ?? appUser.usuario_id;
  if (raw != null && raw !== '' && Number.isFinite(Number(raw)) && Number(raw) > 0) {
    return Number(raw);
  }

  if (import.meta.env.DEV) {
    const d = Number(import.meta.env.VITE_DEV_FAVORITOS_USER_ID);
    if (Number.isFinite(d) && d > 0) return d;
  }

  return null;
}

/** Chaves úteis para diagnóstico DEV (sem valores sensíveis). */
export function appUserDiagKeys(appUser) {
  if (!appUser || typeof appUser !== 'object') return [];
  return Object.keys(appUser).filter((k) => !/senha|password|token/i.test(k));
}
