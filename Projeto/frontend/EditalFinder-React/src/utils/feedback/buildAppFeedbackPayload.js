/** Re-export — implementação em appFeedbackPayload.js (FRONTEND 1.1C). */
export {
  buildAppFeedbackPayload,
  validateAppFeedbackPayload,
  sanitizeAppFeedbackForLog,
  normalizeOptionalEmail,
  normalizeFeedbackPayload,
} from './appFeedbackPayload.js';
export { getFeedbackProblemType } from './appFeedbackTaxonomy.js';
export { getFeedbackSeverity, normalizeLegacySeverity } from './appFeedbackSeverity.js';
export {
  getCategoryLabel,
  normalizeRouteForEmail,
  formatFeedbackDateForEmail,
} from './appFeedbackLabels.js';
