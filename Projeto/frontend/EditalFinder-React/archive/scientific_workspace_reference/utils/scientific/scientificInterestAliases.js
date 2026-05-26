/**
 * Canonicalização de interesses (Fase 2H / 2H-A–E).
 * Um interesse de UI → uma chave de catálogo/trilha.
 */

/** @type {Record<string, string>} interestId → canonicalKey */
export const SCIENTIFIC_INTEREST_CANONICAL = {
  nuclear: 'nuclear',
  fisica_nuclear: 'nuclear',
  engenharia_nuclear: 'engenharia_nuclear',
  quimica_nuclear: 'quimica_nuclear',
  radioquimica: 'quimica_nuclear',

  fisico_quimica: 'fisico_quimica',
  quimica_fisica: 'fisico_quimica',
  quantica: 'quantica',

  materiais: 'materiais',

  computacao_cientifica: 'computacao_cientifica',
  scientific_computing: 'computacao_cientifica',
  monte_carlo: 'monte_carlo',
  simulacao_monte_carlo: 'monte_carlo',
  hpc: 'hpc',
  supercomputacao: 'hpc',
  computacao_alto_desempenho: 'hpc',

  modelagem_molecular: 'dinamica_molecular',
  dinamica_molecular: 'dinamica_molecular',

  plasmas: 'plasmas_fusao',
  plasmas_fusao: 'plasmas_fusao',
  fusao: 'plasmas_fusao',
  fusao_nuclear: 'plasmas_fusao',
  fisica_plasmas: 'plasmas_fusao',

  aeroespacial: 'engenharia_aeroespacial',
  engenharia_aeroespacial: 'engenharia_aeroespacial',
  aerospace: 'engenharia_aeroespacial',
  aeronautica: 'engenharia_aeroespacial',

  espaco: 'espaco',
  space: 'espaco',
  satelites: 'espaco',
  orbital: 'espaco',

  defesa: 'engenharia_defesa',
  engenharia_defesa: 'engenharia_defesa',
  defense_engineering: 'engenharia_defesa',

  instrumentacao: 'instrumentacao',
  sensores: 'instrumentacao',
  detectores: 'instrumentacao',
  instrumentacao_cientifica: 'instrumentacao',
  dosimetria: 'dosimetria',
  dosimetry: 'dosimetria',
  dose: 'dosimetria',
  protecao_radiologica: 'protecao_radiologica',
  radiological_protection: 'protecao_radiologica',
  radioprotecao: 'protecao_radiologica',
  seguranca_radiologica: 'protecao_radiologica',
  medicina_nuclear: 'medicina_nuclear',
  nuclear_medicine: 'medicina_nuclear',
  radiofarmacos: 'medicina_nuclear',
  radiofarmacia: 'medicina_nuclear',

  ia_cientifica: 'ia_cientifica',
  machine_learning_cientifico: 'ia_cientifica',
  ml_cientifico: 'ia_cientifica',
  ciencia_dados: 'ciencia_dados',
  data_science: 'ciencia_dados',

  energia: 'energia',
  sistemas_energia: 'energia',
  energia_nuclear_aplicada: 'energia',
  engenharia_fisica: 'engenharia_fisica',
  fisica_aplicada: 'engenharia_fisica',
  applied_physics: 'engenharia_fisica',
  sistemas_autonomos: 'sistemas_autonomos',
  autonomia: 'sistemas_autonomos',
  tecnologias_estrategicas: 'tecnologias_estrategicas',
  dual_use: 'tecnologias_estrategicas',
  soberania_tecnologica: 'tecnologias_estrategicas',
  critical_technologies: 'tecnologias_estrategicas',
  robotica: 'robotica',
  robotics: 'robotica',
  biotecnologia: 'biotecnologia',
  biotech: 'biotecnologia',
  bioengenharia: 'biotecnologia',
};

/** Chaves com catálogo profundo obrigatório */
export const ALL_DEEP_CATALOG_CANONICAL_KEYS = [
  'nuclear',
  'engenharia_nuclear',
  'quimica_nuclear',
  'fisico_quimica',
  'materiais',
  'computacao_cientifica',
  'monte_carlo',
  'dinamica_molecular',
  'plasmas_fusao',
  'engenharia_aeroespacial',
  'espaco',
  'engenharia_defesa',
  'instrumentacao',
  'dosimetria',
  'protecao_radiologica',
  'medicina_nuclear',
  'ia_cientifica',
  'energia',
  'quantica',
  'engenharia_fisica',
  'hpc',
  'sistemas_autonomos',
  'tecnologias_estrategicas',
  'robotica',
  'biotecnologia',
  'ciencia_dados',
];

/**
 * @param {string} interestId
 * @returns {string}
 */
export function resolveCanonicalInterest(interestId) {
  if (!interestId) return '';
  if (SCIENTIFIC_INTEREST_CANONICAL[interestId]) {
    return SCIENTIFIC_INTEREST_CANONICAL[interestId];
  }
  return interestId;
}

/**
 * Todos os interestIds que mapeiam para a mesma chave.
 * @param {string} canonicalKey
 */
export function interestIdsForCanonical(canonicalKey) {
  return Object.entries(SCIENTIFIC_INTEREST_CANONICAL)
    .filter(([, k]) => k === canonicalKey)
    .map(([id]) => id);
}

/**
 * @param {string[]} activeInterests
 * @returns {{ canonicalKeys: string[], interestByCanonical: Record<string, string[]> }}
 */
export function groupActiveInterestsByCanonical(activeInterests = []) {
  const interestByCanonical = {};
  const order = [];

  for (const id of activeInterests) {
    const key = resolveCanonicalInterest(id);
    if (!key) continue;
    if (!interestByCanonical[key]) {
      interestByCanonical[key] = [];
      order.push(key);
    }
    if (!interestByCanonical[key].includes(id)) {
      interestByCanonical[key].push(id);
    }
  }

  return { canonicalKeys: order, interestByCanonical };
}
