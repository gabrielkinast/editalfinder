/**
 * Tipos JSDoc do assistente de pre-cadastro (sem TypeScript no projeto).
 *
 * @typedef {'manual'|'auto'|'cliente'|'edital'|'radar'} FieldIntelSource
 *
 * @typedef {'alta'|'media'|'baixa'} FieldIntelConfidence
 *
 * @typedef {object} FieldIntelEntry
 * @property {FieldIntelSource} source
 * @property {FieldIntelConfidence} confidence
 * @property {boolean} needsReview
 * @property {string} explanation
 * @property {string=} updatedAt ISO-like string opcional
 *
 * @typedef {Record<string, FieldIntelEntry>} FieldIntelMap
 *
 * @typedef {object} PrecadDraftEnvelopeMeta
 * @property {boolean} [hadStoredDraft]
 * @property {string} editalFingerprint
 * @property {string} geradoAutomaticamenteEm
 * @property {string} [ultimaEdicaoManualEm]
 *
 * @typedef {object} PrecadDraftEnvelope
 * @property {number} version
 * @property {Record<string, unknown>} form
 * @property {FieldIntelMap} fieldIntel
 * @property {PrecadDraftEnvelopeMeta} [draftMeta]
 */

export const INTEL_VERSION = 2;

export const SOURCE_MANUAL = 'manual';
export const SOURCE_AUTO = 'auto';
export const SOURCE_CLIENTE = 'cliente';
export const SOURCE_EDITAL = 'edital';
export const SOURCE_RADAR = 'radar';

export const CONF_HIGH = 'alta';
export const CONF_MEDIUM = 'media';
export const CONF_LOW = 'baixa';

/** @returns {boolean} */
export function isProtectedManual(intelEntry) {
  return !!(intelEntry && intelEntry.source === SOURCE_MANUAL);
}
