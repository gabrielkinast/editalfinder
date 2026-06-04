import { logScientificWorkspace } from './scientificWorkspaceLog';
import { resolveCanonicalInterest } from './scientificInterestAliases';

/** Grupos canônicos para matching de rotas legadas. */
const CANONICAL_CLUSTERS = {
  nuclear_cluster: ['nuclear', 'engenharia_nuclear', 'quimica_nuclear'],
  materials_cluster: ['materiais', 'engenharia_fisica'],
  compute_cluster: ['computacao_cientifica', 'monte_carlo', 'hpc'],
  aero_defense_cluster: ['engenharia_aeroespacial', 'espaco', 'engenharia_defesa', 'sistemas_autonomos', 'robotica'],
  radiation_cluster: ['dosimetria', 'protecao_radiologica', 'medicina_nuclear'],
  fusion_cluster: ['plasmas_fusao'],
  molecular_cluster: ['dinamica_molecular', 'fisico_quimica'],
};

function canonicalSet(active) {
  return new Set(active.map(resolveCanonicalInterest).filter(Boolean));
}

function hasAnyCanonical(canonicals, keys) {
  return keys.some((k) => canonicals.has(k));
}

function countClusterCanonical(canonicals, clusterKey) {
  const keys = CANONICAL_CLUSTERS[clusterKey] || [];
  return keys.filter((k) => canonicals.has(k)).length;
}

const ROUTE_TEMPLATES = [
  {
    id: 'nuclear-materials-compute',
    label: 'Nuclear · Materiais · Computação',
    match: (c) =>
      countClusterCanonical(c, 'nuclear_cluster') >= 1 &&
      countClusterCanonical(c, 'materials_cluster') >= 1 &&
      countClusterCanonical(c, 'compute_cluster') >= 1,
    steps: [
      'Python científico',
      'Decaimento radioativo',
      'Interação radiação-matéria',
      'Estrutura cristalina',
      'Métodos numéricos',
      'Monte Carlo',
      'Simulação de blindagem',
      'Materiais sob radiação',
    ],
  },
  {
    id: 'aero-defense-autonomy',
    label: 'Aeroespacial · Defesa · Autonomia',
    match: (c) => countClusterCanonical(c, 'aero_defense_cluster') >= 2,
    steps: [
      'Mecânica clássica',
      'Controle',
      'Sensores e instrumentação',
      'Navegação',
      'Aerodinâmica básica',
      'Sistemas embarcados',
      'Robótica e autonomia',
      'Tecnologias estratégicas',
    ],
  },
  {
    id: 'fusion-plasmas',
    label: 'Fusão e plasmas',
    match: (c) => countClusterCanonical(c, 'fusion_cluster') >= 1,
    steps: [
      'Física de plasmas intro',
      'Confinamento magnético',
      'Critério de Lawson',
      'Materiais para fusão',
      'Termo-hidráulica básica',
      'Diagnósticos de plasma',
      'Monte Carlo (transporte)',
      'Revisão ITER/DEMO',
    ],
  },
  {
    id: 'radiation-health',
    label: 'Radiação e saúde',
    match: (c) => countClusterCanonical(c, 'radiation_cluster') >= 2,
    steps: [
      'Radiação ionizante',
      'Dosimetria e grandezas',
      'ALARA e proteção',
      'Detectores',
      'Medicina nuclear (PET/SPECT)',
      'Radioquímica intro',
      'Blindagem aplicada',
      'Regulamentação básica',
    ],
  },
  {
    id: 'molecular-compute',
    label: 'Química computacional',
    match: (c) =>
      countClusterCanonical(c, 'molecular_cluster') >= 1 &&
      countClusterCanonical(c, 'compute_cluster') >= 1,
    steps: [
      'Termodinâmica',
      'Mecânica molecular',
      'Python científico',
      'Modelagem molecular (MM/DFT conceitos)',
      'Dinâmica molecular',
      'Análise de trajetória',
      'Cinética química computacional',
      'Visualização e validação',
    ],
  },
  {
    id: 'strategic-tech',
    label: 'Tecnologias estratégicas',
    match: (active) => active.includes('tecnologias_estrategicas'),
    steps: [
      'Soberania tecnológica',
      'Mapeamento de cadeias',
      'Nuclear e energia na geopolítica',
      'Defesa e dual-use',
      'Semicondutores e dados',
      'Observatório de editais/fontes',
      'Síntese no caderno',
      'Perguntas ao orientador',
    ],
  },
];

const DEFAULT_ROUTE = {
  id: 'exploratory',
  label: 'Exploratória',
  steps: [
    'Consolidar fundamentos do catálogo',
    'Salvar 3 itens do feed no caderno',
    'Escolher um projeto prático básico',
    'Revisar trilha do interesse principal',
    'Definir pergunta para o professor',
  ],
};

/**
 * @param {string[]} activeInterests
 */
export function buildSuggestedStudyRoute(activeInterests = []) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  const canonicals = canonicalSet(active);
  const template = ROUTE_TEMPLATES.find((t) => t.match(canonicals)) || DEFAULT_ROUTE;

  const route = {
    id: template.id,
    label: template.label,
    steps: template.steps,
    interestCount: active.length,
  };

  logScientificWorkspace('suggested_route_generated', {
    routeId: route.id,
    interests: active.length,
  });

  return route;
}
