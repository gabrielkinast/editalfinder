import { supabase, isSupabaseConfigured } from './api';
import { authService } from './authService';
import { authCallbackLog } from '../utils/authCallbackDevLog';
import { runAuthCallbackExchange } from '../auth/authCallbackCoordinator';

const LOCK_ERROR_RE = /Lock broken by another request/i;
const PKCE_VERIFIER_RE = /PKCE code verifier not found|code verifier not found/i;
const FLOW_STATE_RE = /invalid flow state|flow state/i;
const EXPIRED_LINK_RE =
  /expired|otp_expired|email link is invalid|invalid.*link|already been used|already used/i;

export const EMAIL_CONFIRMED_LOGIN_MESSAGE =
  'Seu e-mail foi confirmado. Faça login para continuar.';

export const EMAIL_CONFIRMED_SUCCESS_MESSAGE = 'E-mail confirmado com sucesso.';

export const EMAIL_CONFIRMED_SUCCESS_HINT = 'Agora você já pode entrar na sua conta.';

export const CALLBACK_TIMEOUT_MESSAGE =
  'Não conseguimos finalizar automaticamente. Tente fazer login.';

export const LINK_EXPIRED_MESSAGE =
  'Este link de confirmação expirou ou já foi usado. Tente fazer login ou solicite um novo e-mail.';

const CALLBACK_TIMEOUT_MS = 8000;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseCallbackUrl(href) {
  const url = new URL(href, window.location.origin);
  const code = url.searchParams.get('code');
  const hashRaw = url.hash?.startsWith('#') ? url.hash.slice(1) : url.hash || '';
  const hashParams = new URLSearchParams(hashRaw);
  return {
    code,
    access_token: hashParams.get('access_token'),
    refresh_token: hashParams.get('refresh_token'),
    type: hashParams.get('type') || url.searchParams.get('type'),
    error:
      hashParams.get('error_description') ||
      hashParams.get('error') ||
      url.searchParams.get('error_description') ||
      url.searchParams.get('error'),
    hasHashTokens: Boolean(
      hashParams.get('access_token') && hashParams.get('refresh_token'),
    ),
    hasHashOnly: Boolean(hashRaw && hashParams.get('access_token')),
  };
}

/** Remove code, tokens e hash da barra de endereço. */
export function stripAuthParamsFromUrl() {
  if (typeof window === 'undefined') return;
  const path = window.location.pathname;
  window.history.replaceState({}, document.title, path);
}

function isTechnicalAuthError(message) {
  const msg = String(message || '');
  return (
    PKCE_VERIFIER_RE.test(msg) ||
    LOCK_ERROR_RE.test(msg) ||
    FLOW_STATE_RE.test(msg) ||
    /session missing/i.test(msg)
  );
}

/**
 * @returns {{ status: 'manual_login'|'expired'; message: string } | null}
 */
function mapCallbackFailure(message) {
  const msg = String(message || '').trim();
  if (!msg) return null;
  if (EXPIRED_LINK_RE.test(msg)) {
    return { status: 'expired', message: LINK_EXPIRED_MESSAGE };
  }
  if (isTechnicalAuthError(msg)) {
    authCallbackLog('exchange_error', { message: msg, mapped: 'manual_login' });
    return { status: 'manual_login', message: EMAIL_CONFIRMED_LOGIN_MESSAGE };
  }
  return null;
}

async function withLockRetry(operation, label) {
  try {
    return await operation();
  } catch (e) {
    const msg = e?.message || String(e);
    if (!LOCK_ERROR_RE.test(msg)) throw e;
    authCallbackLog('exchange_lock_retry', { label });
    await sleep(450);
    return await operation();
  }
}

async function exchangePkceCode(code) {
  authCallbackLog('exchange_start', { mode: 'pkce', has_code: true });
  const result = await withLockRetry(
    () => supabase.auth.exchangeCodeForSession(code),
    'exchangeCodeForSession',
  );
  if (result.error) throw result.error;
  authCallbackLog('exchange_success', { userId: result.data?.session?.user?.id ?? null });
  return result.data;
}

async function applyHashSession(access_token, refresh_token) {
  authCallbackLog('implicit_set_session', {});
  const result = await withLockRetry(
    () => supabase.auth.setSession({ access_token, refresh_token }),
    'setSession',
  );
  if (result.error) throw result.error;
  return result.data?.session ?? null;
}

async function waitForSession(maxMs = 6000) {
  const started = Date.now();
  while (Date.now() - started < maxMs) {
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    if (data.session?.access_token && data.session?.user?.id) {
      return data.session;
    }
    await sleep(200);
  }
  return null;
}

async function resolveSessionImplicit(parsed) {
  authCallbackLog('implicit_wait', {
    has_hash_token: parsed.hasHashTokens,
    type: parsed.type,
  });

  await sleep(200);
  let session = await waitForSession(5500);

  if (!session && parsed.access_token && parsed.refresh_token) {
    try {
      await applyHashSession(parsed.access_token, parsed.refresh_token);
      session = await waitForSession(2500);
    } catch (e) {
      authCallbackLog('exchange_error', { message: e?.message, phase: 'setSession' });
      const mapped = mapCallbackFailure(e?.message);
      if (mapped) return { session: null, mapped };
    }
  }

  return { session, mapped: null };
}

async function buildAppUserFromSession(session) {
  const user = session.user;
  authCallbackLog('ensure_profile_start', { auth_user_id: user.id });
  let appUser = await authService.ensureInternalProfileFromAuthUser(user);
  if (!appUser) {
    const row = await authService.fetchProfileByAuthUserId(user.id);
    if (row) {
      appUser = authService.buildAppUser(row, user.id);
    }
  }
  authCallbackLog('ensure_profile_end', { id_usuario: appUser?.id_usuario ?? null });
  return appUser;
}

async function clearSessionAfterConfirmation() {
  try {
    await supabase.auth.signOut({ scope: 'local' });
  } catch {
    /* ignore */
  }
  authService.clearProfileCache();
}

async function runCallbackCore(href) {
  const parsed = parseCallbackUrl(href);

  authCallbackLog('callback_start', {
    has_code: !!parsed.code,
    has_hash_token: parsed.hasHashTokens,
    type: parsed.type,
  });

  if (parsed.error) {
    const mapped = mapCallbackFailure(parsed.error);
    if (mapped) return mapped;
    throw new Error(parsed.error);
  }

  let session = null;

  if (parsed.hasHashTokens || parsed.hasHashOnly || !parsed.code) {
    const implicit = await resolveSessionImplicit(parsed);
    if (implicit.mapped) return implicit.mapped;
    session = implicit.session;
  }

  if (!session?.access_token && parsed.code) {
    try {
      const data = await exchangePkceCode(parsed.code);
      session = data.session;
    } catch (e) {
      const msg = e?.message || String(e);
      authCallbackLog('exchange_error', { message: msg });
      const mapped = mapCallbackFailure(msg);
      if (mapped) return mapped;
      throw e;
    }
  }

  if (!session?.access_token || !session?.user?.id) {
    authCallbackLog('manual_login', {
      reason: 'no_session',
      had_code: !!parsed.code,
      had_hash: parsed.hasHashTokens,
    });
    return { status: 'manual_login', message: EMAIL_CONFIRMED_LOGIN_MESSAGE };
  }

  await buildAppUserFromSession(session);
  await clearSessionAfterConfirmation();
  stripAuthParamsFromUrl();

  authCallbackLog('exchange_success', { confirmed: true, redirect: 'login_page' });
  return {
    status: 'success',
    message: EMAIL_CONFIRMED_SUCCESS_MESSAGE,
    hint: EMAIL_CONFIRMED_SUCCESS_HINT,
  };
}

/**
 * Conclui confirmação de e-mail na rota /auth/callback.
 * Não redireciona para dashboard — retorna estado para a UI pública.
 * @returns {Promise<
 *   | { status: 'success'; message: string; hint?: string }
 *   | { status: 'manual_login'; message: string }
 *   | { status: 'expired'; message: string }
 *   | { status: 'timeout'; message: string }
 * >}
 */
export async function completeEmailAuthCallback(href = window.location.href) {
  if (!isSupabaseConfigured) {
    throw new Error('Supabase não configurado.');
  }

  return runAuthCallbackExchange(async () => {
    const timeoutPromise = sleep(CALLBACK_TIMEOUT_MS).then(() => ({
      status: 'timeout',
      message: CALLBACK_TIMEOUT_MESSAGE,
    }));

    try {
      const result = await Promise.race([runCallbackCore(href), timeoutPromise]);
      if (result?.status === 'timeout') {
        authCallbackLog('timeout', {});
        stripAuthParamsFromUrl();
        await clearSessionAfterConfirmation();
      }
      return result;
    } catch (e) {
      const msg = e?.message || String(e);
      authCallbackLog('exchange_error', { message: msg });
      const mapped = mapCallbackFailure(msg);
      if (mapped) {
        stripAuthParamsFromUrl();
        await clearSessionAfterConfirmation();
        return mapped;
      }
      stripAuthParamsFromUrl();
      await clearSessionAfterConfirmation();
      return { status: 'manual_login', message: EMAIL_CONFIRMED_LOGIN_MESSAGE };
    }
  });
}

/** Limpa estado local após falha grave (lock persistente). */
export async function resetLocalAuthAfterCallbackFailure() {
  authCallbackLog('exchange_error', { action: 'clearLocalAuth' });
  await clearSessionAfterConfirmation();
}
