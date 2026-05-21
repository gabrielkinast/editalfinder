import { isAuthCallbackPath } from '../utils/authCallbackRoute';

/** Evita corrida entre AuthContext bootstrap e AuthCallback exchange. */
let callbackHandling = false;
let exchangeMutex = null;

export function markAuthCallbackHandling(active) {
  callbackHandling = !!active;
}

export function isAuthCallbackHandling() {
  return callbackHandling;
}

/** AuthContext deve ignorar bootstrap/listener pesado na rota de callback. */
export function shouldDeferAuthBootstrap() {
  return isAuthCallbackPath() || callbackHandling;
}

/**
 * Serializa exchangeCodeForSession / setSession (um por vez).
 * @param {() => Promise<T>} fn
 * @returns {Promise<T>}
 */
export function runAuthCallbackExchange(fn) {
  if (!exchangeMutex) {
    exchangeMutex = Promise.resolve()
      .then(() => fn())
      .finally(() => {
        exchangeMutex = null;
      });
  }
  return exchangeMutex;
}
