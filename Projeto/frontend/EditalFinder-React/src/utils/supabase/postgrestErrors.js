/**
 * Detecta erro PostgREST quando tabela/view não está no schema cache (staging comum).
 */
export function isMissingPostgrestTableError(error) {
  if (!error) return false;
  const code = String(error.code || '');
  if (code === 'PGRST205') return true;
  const msg = String(error.message || '').toLowerCase();
  return (
    msg.includes('could not find') &&
    (msg.includes('schema cache') || msg.includes('relation') || msg.includes('table'))
  );
}
