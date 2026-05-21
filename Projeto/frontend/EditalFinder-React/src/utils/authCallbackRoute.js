import { AUTH_CALLBACK_URL, PUBLIC_SITE_URL } from '../config/env';

/** Caminho da rota de retorno do Supabase Auth (relativo ao basename do Router). */
export const AUTH_CALLBACK_ROUTE = '/auth/callback';

const IS_DEV = import.meta.env.DEV;
const IS_PROD = import.meta.env.PROD;

function trimSlashEnd(s) {
  return String(s || '').replace(/\/+$/, '');
}

function trimSlashBoth(s) {
  return trimSlashEnd(String(s || '').replace(/\/+/g, '/'));
}

/**
 * @param {string} url
 */
export function urlContainsLocalhost(url) {
  if (!url) return false;
  try {
    const host = new URL(url).hostname.toLowerCase();
    return host === 'localhost' || host === '127.0.0.1' || host === '[::1]';
  } catch {
    return /localhost|127\.0\.0\.1/i.test(String(url));
  }
}

/**
 * URL pública base da app (com basename /editalfinder, sem barra final).
 * Produção: exige VITE_PUBLIC_SITE_URL (nunca localhost).
 */
export function getPublicSiteUrl() {
  const fromEnv = trimSlashEnd(PUBLIC_SITE_URL);
  if (fromEnv) {
    if (IS_PROD && urlContainsLocalhost(fromEnv)) {
      console.error(
        '[auth-signup] VITE_PUBLIC_SITE_URL aponta para localhost em produção. Configure o domínio real.',
      );
    }
    return fromEnv;
  }

  if (typeof window !== 'undefined') {
    const origin = trimSlashEnd(window.location.origin);
    const base = trimSlashEnd(import.meta.env.BASE_URL || '/editalfinder');
    const built = `${origin}${base.startsWith('/') ? base : `/${base}`}`;
    if (IS_PROD && urlContainsLocalhost(built)) {
      console.error(
        '[auth-signup] Site URL derivada de window.location é localhost em produção. Defina VITE_PUBLIC_SITE_URL.',
      );
    }
    return built;
  }

  if (IS_PROD) {
    console.error('[auth-signup] VITE_PUBLIC_SITE_URL ausente em build de produção.');
    return '';
  }

  return 'http://localhost:5173/editalfinder';
}

/**
 * URL absoluta para emailRedirectTo (signUp).
 * Deve estar em Supabase → Authentication → Redirect URLs.
 */
export function getAuthCallbackRedirectUrl() {
  let url = trimSlashBoth(AUTH_CALLBACK_URL);

  if (!url) {
    const site = getPublicSiteUrl();
    url = site ? `${site}${AUTH_CALLBACK_ROUTE}` : undefined;
  }

  if (!url && typeof window !== 'undefined') {
    const origin = trimSlashEnd(window.location.origin);
    const base = trimSlashEnd(import.meta.env.BASE_URL || '/editalfinder');
    url = `${origin}${base.startsWith('/') ? base : `/${base}`}${AUTH_CALLBACK_ROUTE}`;
  }

  if (!url) return undefined;

  if (IS_PROD && urlContainsLocalhost(url)) {
    const site = getPublicSiteUrl();
    if (site && !urlContainsLocalhost(site)) {
      const safe = `${site}${AUTH_CALLBACK_ROUTE}`;
      console.error(
        '[auth-signup] emailRedirectTo corrigido: localhost bloqueado em produção.',
        { rejected: url, used: safe },
      );
      url = safe;
    } else {
      console.error(
        '[auth-signup] emailRedirectTo ainda contém localhost em produção. Configure VITE_AUTH_CALLBACK_URL.',
        { url },
      );
    }
  }

  if (IS_DEV && urlContainsLocalhost(url)) {
    console.info('[auth-signup] emailRedirectTo (dev localhost)', { url });
  }

  return url;
}

/**
 * Metadados para logs DEV no signUp.
 */
export function getAuthRedirectLogMeta(redirectUrl) {
  return {
    emailRedirectTo: redirectUrl ?? null,
    environment: import.meta.env.MODE,
    isProd: IS_PROD,
    containsLocalhost: redirectUrl ? urlContainsLocalhost(redirectUrl) : null,
    publicSiteUrl: getPublicSiteUrl() || null,
  };
}

/**
 * Detecta se o pathname actual é a rota de callback (com ou sem basename /editalfinder).
 */
export function isAuthCallbackPath(pathname) {
  const path =
    pathname ??
    (typeof window !== 'undefined' ? window.location.pathname : '');
  return path.includes(AUTH_CALLBACK_ROUTE);
}
