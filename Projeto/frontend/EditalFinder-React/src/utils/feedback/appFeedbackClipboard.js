export async function copyTextToClipboard(text) {
  if (!text || typeof text !== 'string') {
    return { ok: false, reason: 'empty_text' };
  }

  try {
    if (typeof navigator !== 'undefined' && navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return { ok: true, method: 'navigator_clipboard' };
    }
  } catch {
    // fallback abaixo
  }

  if (typeof document === 'undefined') {
    return { ok: false, reason: 'clipboard_failed', message: 'no_document' };
  }

  try {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    textarea.style.pointerEvents = 'none';

    document.body.appendChild(textarea);
    textarea.select();

    const copied = document.execCommand('copy');
    document.body.removeChild(textarea);

    if (copied) {
      return { ok: true, method: 'exec_command' };
    }

    return { ok: false, reason: 'exec_command_failed' };
  } catch (error) {
    return {
      ok: false,
      reason: 'clipboard_failed',
      message: error?.message || String(error),
    };
  }
}

export function buildManualSupportInstructions({ supportEmail, subject, body }) {
  return [
    `Para: ${supportEmail}`,
    '',
    `Assunto: ${subject}`,
    '',
    'Mensagem:',
    body,
  ].join('\n');
}
