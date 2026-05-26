import { cleanScientificTitle } from './cleanScientificTitle';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { sanitizeScientificNotebookEntry } from './sanitizeScientificNotebookEntry';
import { withStudyProgressOnNotebookEntry } from './buildStudyProgressSummary';

const LAYER_LABELS = {
  foundations: 'Fundamentos',
  intermediate: 'Intermediário',
  advanced: 'Avançado',
  researchLevel: 'Pesquisa/Mestrado',
  math: 'Matemática',
  physics: 'Física',
  chemistry: 'Química',
  computation: 'Computação',
};

/**
 * @param {object} payload
 * @param {string} payload.areaLabel
 * @param {string} payload.layer
 * @param {string[]} payload.topics
 * @param {string} [payload.interestId]
 * @param {string} [payload.canonicalKey]
 */
export function notebookEntryFromTheory({
  areaLabel,
  layer,
  topics = [],
  interestId,
  canonicalKey,
  studyProgressStatus,
}) {
  const layerName = LAYER_LABELS[layer] || layer;
  const titulo = cleanScientificTitle(`Teoria — ${areaLabel}: ${layerName}`) || 'Bloco de teoria';
  const topicList = Array.isArray(topics) ? topics : [];
  const interest = canonicalKey || interestId;

  const draft = {
    contentCategory: 'teoria',
    tipo: 'teoria',
    titulo,
    interesses: interest ? [interest] : [],
    theoryLayer: layer,
  };
  const stableKey = getScientificNotebookEntryKey(draft);

  return withStudyProgressOnNotebookEntry(
    sanitizeScientificNotebookEntry({
      id: `theory-${stableKey.replace(/\|/g, '_').slice(0, 80)}`,
      contentCategory: 'teoria',
      notebookGroup: 'teoria',
      tipo: 'teoria',
      titulo,
      title: titulo,
      theoryLayer: layer,
      theoryLayerLabel: layerName,
      areaLabel,
      conceitos: topicList,
      fonte: 'Catálogo profundo',
      resumo: `${areaLabel} · ${layerName} · ${topicList.length} tópico(s)`,
      interesses: interest ? [interest] : [],
      notes: topicList.length ? topicList.join('\n') : undefined,
      savedAt: new Date().toISOString(),
    }),
    studyProgressStatus,
  );
}

export function theoryNotebookTitle(areaLabel, layer) {
  const layerName = LAYER_LABELS[layer] || layer;
  return `Teoria — ${areaLabel}: ${layerName}`;
}
