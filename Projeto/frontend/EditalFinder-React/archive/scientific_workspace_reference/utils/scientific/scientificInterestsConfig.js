/**
 * Interesses científicos (Fase 1 + 2B).
 * Itens antigos mantidos para compatibilidade com localStorage.
 */
export const SCIENTIFIC_INTERESTS = [
  { id: 'nuclear', label: 'Nuclear' },
  { id: 'fisico_quimica', label: 'Físico-química' },
  { id: 'materiais', label: 'Materiais' },
  { id: 'defesa', label: 'Defesa' },
  { id: 'espaco', label: 'Espaço' },
  { id: 'energia', label: 'Energia' },
  { id: 'quantica', label: 'Quântica' },
  { id: 'computacao_cientifica', label: 'Computação científica' },
  { id: 'ia_cientifica', label: 'IA científica' },
  { id: 'aeroespacial', label: 'Aeroespacial' },
  { id: 'ciencia_dados', label: 'Ciência dos dados' },
  { id: 'robotica', label: 'Robótica' },
  { id: 'biotecnologia', label: 'Biotecnologia' },
  { id: 'medicina_nuclear', label: 'Medicina nuclear' },
  { id: 'engenharia_fisica', label: 'Engenharia física' },
  { id: 'engenharia_nuclear', label: 'Engenharia nuclear' },
  { id: 'quimica_nuclear', label: 'Química nuclear' },
  { id: 'radioquimica', label: 'Radioquímica' },
  { id: 'engenharia_defesa', label: 'Engenharia de defesa' },
  { id: 'engenharia_aeroespacial', label: 'Engenharia aeroespacial' },
  { id: 'plasmas', label: 'Física de plasmas' },
  { id: 'fusao', label: 'Fusão nuclear' },
  { id: 'dosimetria', label: 'Dosimetria' },
  { id: 'protecao_radiologica', label: 'Proteção radiológica' },
  { id: 'instrumentacao', label: 'Instrumentação' },
  { id: 'hpc', label: 'HPC' },
  { id: 'modelagem_molecular', label: 'Modelagem molecular' },
  { id: 'dinamica_molecular', label: 'Dinâmica molecular' },
  { id: 'monte_carlo', label: 'Monte Carlo' },
  { id: 'sistemas_autonomos', label: 'Sistemas autônomos' },
  { id: 'tecnologias_estrategicas', label: 'Tecnologias estratégicas' },
];

/** Agrupamento visual (Fase 2B). */
export const INTEREST_CATEGORIES = [
  {
    id: 'fisica_quimica',
    label: 'Física e Química',
    interestIds: [
      'fisico_quimica',
      'engenharia_fisica',
      'quantica',
      'plasmas',
      'fusao',
      'modelagem_molecular',
      'dinamica_molecular',
    ],
  },
  {
    id: 'nuclear',
    label: 'Nuclear',
    interestIds: [
      'nuclear',
      'engenharia_nuclear',
      'quimica_nuclear',
      'radioquimica',
      'fusao',
      'plasmas',
    ],
  },
  {
    id: 'computacao',
    label: 'Computação',
    interestIds: [
      'computacao_cientifica',
      'hpc',
      'monte_carlo',
      'ia_cientifica',
      'ciencia_dados',
      'modelagem_molecular',
      'dinamica_molecular',
    ],
  },
  {
    id: 'defesa_aero',
    label: 'Defesa e Aeroespacial',
    interestIds: [
      'defesa',
      'engenharia_defesa',
      'espaco',
      'aeroespacial',
      'engenharia_aeroespacial',
      'sistemas_autonomos',
      'robotica',
      'tecnologias_estrategicas',
    ],
  },
  {
    id: 'saude_radiacao',
    label: 'Saúde e Radiação',
    interestIds: ['medicina_nuclear', 'dosimetria', 'protecao_radiologica'],
  },
  {
    id: 'materiais_eng',
    label: 'Materiais e Engenharia',
    interestIds: ['materiais', 'energia', 'engenharia_fisica', 'instrumentacao', 'biotecnologia'],
  },
];

export const DEFAULT_SCIENTIFIC_INTEREST_IDS = ['nuclear', 'materiais', 'computacao_cientifica'];

export function interestLabelById(id) {
  return SCIENTIFIC_INTERESTS.find((i) => i.id === id)?.label || id.replace(/_/g, ' ');
}

/** Interesses agrupados para UI (cada interesse aparece uma vez). */
export function interestsByCategory() {
  const seen = new Set();
  const groups = [];
  for (const cat of INTEREST_CATEGORIES) {
    const items = [];
    for (const id of cat.interestIds) {
      if (seen.has(id)) continue;
      const meta = SCIENTIFIC_INTERESTS.find((i) => i.id === id);
      if (meta) {
        seen.add(id);
        items.push(meta);
      }
    }
    if (items.length) groups.push({ ...cat, items });
  }
  const uncategorized = SCIENTIFIC_INTERESTS.filter((i) => !seen.has(i.id));
  if (uncategorized.length) {
    groups.push({ id: 'outros', label: 'Outros', items: uncategorized });
  }
  return groups;
}
