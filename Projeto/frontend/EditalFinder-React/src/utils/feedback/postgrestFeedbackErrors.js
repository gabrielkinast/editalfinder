/**
 * Classifica erros remotos do fluxo app_feedback para fallback local.
 */
export function classifyAppFeedbackRemoteError(error) {
  const code = String(error?.code || '');
  const text = JSON.stringify(error || {}).toLowerCase();
  const message = String(error?.message || '').toLowerCase();

  if (
    code === 'PGRST205' ||
    text.includes('pgrst205') ||
    message.includes('could not find') ||
    message.includes('schema cache') ||
    (message.includes('app_feedback') && message.includes('relation'))
  ) {
    return 'remote_table_missing';
  }

  if (
    message.includes('failed to fetch') ||
    message.includes('networkerror') ||
    message.includes('network') ||
    message.includes('load failed') ||
    code === 'ECONNREFUSED'
  ) {
    return 'network_error';
  }

  if (
    code === '42501' ||
    message.includes('permission denied') ||
    message.includes('row-level security') ||
    message.includes('rls') ||
    code === 'PGRST301'
  ) {
    return 'permission_error';
  }

  if (code === '404' || code === '406' || message.includes('not found')) {
    return 'remote_error';
  }

  return 'remote_error';
}

export function isRemoteFallbackReason(reason) {
  return [
    'remote_table_missing',
    'network_error',
    'permission_error',
    'remote_error',
    'supabase_not_configured',
  ].includes(reason);
}
