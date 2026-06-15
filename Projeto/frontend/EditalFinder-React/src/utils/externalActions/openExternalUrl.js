import { IS_TAURI_BUILD } from '../../config/routerBase.js';
import { normalizeExternalUrl } from './normalizeExternalUrl.js';

function isTauriRuntime() {
  if (typeof window === 'undefined') return false;
  if (IS_TAURI_BUILD) return true;
  return Boolean(window.__TAURI_INTERNALS__ || window.__TAURI__);
}

function hasDocument() {
  return typeof document !== 'undefined' && document?.body != null;
}

async function openMailtoUrl(mailtoUrl) {
  if (!hasDocument()) return false;

  if (isTauriRuntime()) {
    try {
      const { openUrl } = await import('@tauri-apps/plugin-opener');
      await openUrl(mailtoUrl);
      return true;
    } catch {
      return false;
    }
  }

  try {
    const anchor = document.createElement('a');
    anchor.href = mailtoUrl;
    anchor.rel = 'noopener noreferrer';
    anchor.style.display = 'none';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    return true;
  } catch {
    return false;
  }
}

async function openHttpsUrl(url) {
  if (isTauriRuntime()) {
    const { openUrl } = await import('@tauri-apps/plugin-opener');
    await openUrl(url);
    return true;
  }

  const opened = window.open(url, '_blank', 'noopener,noreferrer');
  if (!opened) {
    window.location.assign(url);
  }
  return true;
}

/**
 * Abre URL no navegador do sistema (Tauri opener) ou nova aba (web).
 * mailto: só é permitido com `options.allowMailto === true`.
 * @returns {Promise<boolean>} true se abriu
 */
export async function openExternalUrl(raw, options = {}) {
  const url = normalizeExternalUrl(raw);
  if (!url) {
    if (import.meta.env.DEV) {
      console.warn('[externalActions] URL inválida ou vazia', {
        raw,
        actionType: options.actionType ?? null,
      });
    }
    return false;
  }

  let protocol = 'https:';
  try {
    protocol = new URL(url).protocol;
  } catch {
    return false;
  }

  if (protocol === 'mailto:' && !options.allowMailto) {
    if (import.meta.env.DEV) {
      console.warn('[externalActions] mailto bloqueado — use allowMailto: true', {
        actionType: options.actionType ?? null,
      });
    }
    return false;
  }

  try {
    const opened =
      protocol === 'mailto:' ? await openMailtoUrl(url) : await openHttpsUrl(url);

    if (import.meta.env.DEV && opened) {
      console.info('[externalActions] open', {
        url: protocol === 'mailto:' ? 'mailto:…' : url,
        actionType: options.actionType ?? null,
        tauri: isTauriRuntime(),
      });
    }
    return opened;
  } catch (err) {
    console.error('[externalActions] falha ao abrir URL', protocol === 'mailto:' ? 'mailto:…' : url, err);
    try {
      if (protocol === 'mailto:') {
        return openMailtoUrl(url);
      }
      window.open(url, '_blank', 'noopener,noreferrer');
      return true;
    } catch {
      return false;
    }
  }
}
