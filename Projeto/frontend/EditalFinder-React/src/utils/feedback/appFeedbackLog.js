/**
 * Logs DEV do sistema app_feedback.
 */
export function logAppFeedback(event, payload = {}) {
  if (!import.meta.env.DEV) return;
  console.info('[app-feedback]', event, payload);
}
