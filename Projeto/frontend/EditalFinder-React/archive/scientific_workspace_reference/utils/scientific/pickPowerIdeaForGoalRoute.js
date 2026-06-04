import { getPowerIdeaById, getPowerIdeasForArea } from './getPowerIdeasForArea';
import { resolveCanonicalInterest } from './scientificInterestAliases';

/** Rota por objetivo → ideia poderosa prioritária. */
const ROUTE_POWER_IDEA_PICKS = {
  nuclear_computational: { area: 'nuclear', ideaId: 'transport-equation' },
  phys_chem_computational: { area: 'fisico_quimica', ideaId: 'partition-function' },
  reactor_materials: { area: 'materiais', ideaId: 'materiais-radiation-damage' },
  aero_defense: { area: 'engenharia_aeroespacial', ideaId: 'aero-mach' },
  nuclear_medicine_dosimetry: { area: 'medicina_nuclear', ideaId: 'med-nuclear-effective-half-life' },
  radiation_protection: { area: 'protecao_radiologica', ideaId: 'prot-rad-alara' },
  space_systems: { area: 'espaco', ideaId: 'espaco-hohmann' },
};

/**
 * @param {object} input
 * @param {object} [input.goalRoute]
 * @param {string[]} [input.activeInterests]
 */
export function pickPowerIdeaForGoalRoute({ goalRoute, activeInterests = [] } = {}) {
  if (goalRoute?.id && ROUTE_POWER_IDEA_PICKS[goalRoute.id]) {
    const { area, ideaId } = ROUTE_POWER_IDEA_PICKS[goalRoute.id];
    const idea = getPowerIdeaById(area, ideaId);
    if (idea) return { idea, areaKey: area };
  }

  const canonicals = [...new Set(activeInterests.map(resolveCanonicalInterest).filter(Boolean))];
  for (const key of canonicals) {
    const ideas = getPowerIdeasForArea(key);
    if (ideas.length) return { idea: ideas[0], areaKey: key };
  }

  return null;
}
