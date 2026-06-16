import { EXTERNAL_ACTION_TYPES } from './actionTypes.js';
import { resolveExternalActionUrl, notifyUnsafeLinkFailure } from '../edital/getEditalActionUrls.js';
import { openExternalUrl } from './openExternalUrl.js';
import { logEditalLinkClick } from '../edital/logEditalLinkClick.js';
import { logExternalLinkDebug } from '../qa/externalLinkDebug.js';

function resolveUrl(item, actionType, urlOverride) {
  return resolveExternalActionUrl(item, actionType, urlOverride, EXTERNAL_ACTION_TYPES);
}

/**
 * Botão centralizado para links externos (web + Tauri).
 * Usa <button> para evitar navegação dentro da WebView.
 */
export default function ExternalActionButton({
  item = null,
  actionType,
  label,
  className = '',
  disabled = false,
  url: urlOverride,
  title,
  onOpened,
  onFailed,
  logEdital = false,
  logCampo = null,
  stopPropagation = true,
  type = 'button',
}) {
  const url = resolveUrl(item, actionType, urlOverride);
  const canOpen = !disabled && Boolean(url);

  const handleClick = async (e) => {
    if (stopPropagation) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!canOpen || !url) {
      notifyUnsafeLinkFailure();
      onFailed?.();
      return;
    }

    logExternalLinkDebug(item, {
      chosenUrl: url,
      fieldUsed: logCampo || actionType,
    });

    if (import.meta.env.DEV && logEdital && item) {
      logEditalLinkClick(item, {
        campoEscolhido: logCampo || actionType,
        urlFinal: url,
      });
    }

    const ok = await openExternalUrl(url, { actionType });
    if (ok) onOpened?.();
    else {
      notifyUnsafeLinkFailure();
      onFailed?.();
    }
  };

  if (!canOpen) {
    return (
      <span className={className} aria-disabled="true" title={title || 'Link indisponível'}>
        {label}
      </span>
    );
  }

  return (
    <button
      type={type}
      className={className}
      title={title || url}
      onClick={handleClick}
      data-testid={actionType === EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY ? 'edital-open-official' : undefined}
      data-qa-resolved-url={url}
    >
      {label}
    </button>
  );
}

/** Link estilizado que abre externamente (mesma lógica). */
export function ExternalActionLink({
  item = null,
  actionType,
  children,
  className = '',
  disabled = false,
  url: urlOverride,
  title,
  logEdital = false,
  logCampo = null,
}) {
  const url = resolveUrl(item, actionType, urlOverride);
  const canOpen = !disabled && Boolean(url);

  const handleClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!canOpen || !url) {
      notifyUnsafeLinkFailure();
      return;
    }

    logExternalLinkDebug(item, {
      chosenUrl: url,
      fieldUsed: logCampo || actionType,
    });

    if (import.meta.env.DEV && logEdital && item) {
      logEditalLinkClick(item, { campoEscolhido: logCampo || actionType, urlFinal: url });
    }
    const ok = await openExternalUrl(url, { actionType });
    if (!ok) notifyUnsafeLinkFailure();
  };

  if (!canOpen) {
    return (
      <span className={className} aria-disabled="true">
        {children}
      </span>
    );
  }

  return (
    <a
      href={url}
      className={className}
      title={title || url}
      onClick={handleClick}
      rel="noopener noreferrer"
      data-testid={actionType === EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY ? 'edital-open-official' : undefined}
      data-qa-resolved-url={url}
    >
      {children}
    </a>
  );
}
