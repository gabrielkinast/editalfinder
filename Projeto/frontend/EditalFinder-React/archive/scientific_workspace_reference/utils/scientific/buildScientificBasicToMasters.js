import { buildScientificProjectIdeas } from './buildScientificProjectIdeas';
import { getDeepStudyArea } from './scientificDeepStudyCatalog';
import { levelLabel, normalizeProjectLevel } from './scientificProjectLevels';
import { interestLabelById } from './scientificInterestsConfig';

const SEQUENCE = [
  { level: 'basico', trackKey: 'basic', label: 'Básico' },
  { level: 'intermediario', trackKey: 'intermediate', label: 'Intermediário' },
  { level: 'avancado', trackKey: 'advanced', label: 'Avançado' },
  { level: 'ic_tcc', trackKey: 'ictcc', label: 'IC/TCC' },
  { level: 'mestrado', trackKey: 'masters', label: 'Mestrado' },
];

/**
 * Monta sequência "Do básico ao mestrado" para interesses ativos.
 * @param {string[]} activeInterests
 * @param {Array} [notebookItems]
 */
export function buildScientificBasicToMasters(activeInterests = [], notebookItems = []) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  if (!active.length) return { steps: [], title: null };

  const ideas = buildScientificProjectIdeas(active, notebookItems);
  const primary = active[0];
  const area = getDeepStudyArea(primary);
  const tracks = area?.projectTracks || {};

  const steps = SEQUENCE.map((tier) => {
    const match = ideas.find((i) => normalizeProjectLevel(i.level) === tier.level);
    const trackTitle = tracks[tier.trackKey]?.[0];
    return {
      level: tier.level,
      levelLabel: levelLabel(tier.level),
      tierLabel: tier.label,
      title: match?.title || trackTitle || `Projeto ${tier.label.toLowerCase()} em ${interestLabelById(primary)}`,
      idea: match || null,
      fromCatalog: Boolean(trackTitle && !match),
    };
  });

  const labels = active.slice(0, 3).map(interestLabelById);
  const title = labels.length
    ? `Do básico ao mestrado: ${labels.join(' + ')}`
    : 'Do básico ao mestrado';

  return { steps, title, primaryInterest: primary, areaLabel: area?.label };
}
