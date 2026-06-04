import { resolveCanonicalInterest } from './scientificInterestAliases';
import { logScientificWorkspace } from './scientificWorkspaceLog';

function hasCanonical(active, keys) {
  const set = new Set(active.map(resolveCanonicalInterest));
  return keys.some((k) => set.has(k));
}

function pickProjects(projectIdeas, keywords, limit = 3) {
  const kw = keywords.map((k) => k.toLowerCase());
  return (projectIdeas || [])
    .filter((p) => {
      const blob = `${p.title} ${p.why || ''} ${(p.interests || []).join(' ')}`.toLowerCase();
      return kw.some((k) => blob.includes(k));
    })
    .slice(0, limit)
    .map((p) => p.title);
}

function pickBooks(books, limit = 3) {
  return (books || []).slice(0, limit).map((b) =>
    b.author ? `${b.author} — ${b.title}` : b.title || String(b),
  );
}

const GOAL_ROUTE_TEMPLATES = [
  {
    id: 'nuclear_computational',
    title: 'Nuclear computacional',
    description:
      'Formação em física nuclear com métodos numéricos, Monte Carlo e transporte — ideal para blindagem e simulação.',
    match: (c) =>
      hasCanonical(c, ['nuclear']) &&
      hasCanonical(c, ['monte_carlo', 'computacao_cientifica']),
    steps: [
      'Python científico',
      'Probabilidade e estatística',
      'Decaimento radioativo',
      'Interação radiação-matéria',
      'Monte Carlo',
      'Blindagem',
      'Transporte de partículas',
      'OpenMC/Geant4 conceitual',
    ],
    projectKeywords: ['monte carlo', 'blindagem', 'nuclear', 'transporte'],
    bookKeywords: ['Krane', 'Knoll', 'Monte Carlo'],
  },
  {
    id: 'phys_chem_computational',
    title: 'Físico-química computacional',
    description:
      'Termodinâmica e simulação molecular com Python — da base estatística a enhanced sampling.',
    match: (c) =>
      hasCanonical(c, ['fisico_quimica']) &&
      hasCanonical(c, ['dinamica_molecular', 'monte_carlo']),
    steps: [
      'Termodinâmica',
      'Mecânica estatística',
      'Química quântica introdutória',
      'Python científico',
      'Dinâmica molecular',
      'Monte Carlo molecular',
      'Simulação de líquidos',
      'Enhanced sampling',
    ],
    projectKeywords: ['molecular', 'fisico', 'monte carlo', 'liquido'],
    bookKeywords: ['Atkins', 'Frenkel', 'McQuarrie'],
  },
  {
    id: 'reactor_materials',
    title: 'Materiais para reatores',
    description:
      'Ciência de materiais aplicada a nuclear: defeitos, radiação, blindagem e simulação atomística.',
    match: (c) =>
      hasCanonical(c, ['materiais']) &&
      hasCanonical(c, ['nuclear', 'engenharia_nuclear']),
    steps: [
      'Estrutura cristalina',
      'Defeitos',
      'Difusão',
      'Interação radiação-matéria',
      'Materiais sob radiação',
      'Blindagem',
      'Materiais nucleares',
      'Simulação atomística',
    ],
    projectKeywords: ['materiais', 'blindagem', 'radiacao', 'nuclear'],
    bookKeywords: ['Callister', 'Porter', 'Knoll'],
  },
  {
    id: 'aero_defense',
    title: 'Aeroespacial e defesa',
    description:
      'Fluidos, sistemas embarcados, sensores e autonomia para aplicações aeroespaciais e de defesa.',
    match: (c) =>
      hasCanonical(c, ['engenharia_aeroespacial']) && hasCanonical(c, ['engenharia_defesa']),
    steps: [
      'Mecânica dos fluidos',
      'Aerodinâmica',
      'Sistemas embarcados',
      'Sensores',
      'Controle',
      'Materiais aeroespaciais',
      'Sistemas autônomos',
      'Tecnologias estratégicas',
    ],
    projectKeywords: ['aero', 'defesa', 'uav', 'sensor'],
    bookKeywords: ['Anderson', 'Skolnik', 'Siciliano'],
  },
  {
    id: 'nuclear_medicine_dosimetry',
    title: 'Medicina nuclear e dosimetria',
    description:
      'Radiofármacos, imagem PET/SPECT e dosimetria clínica com base em detecção e Monte Carlo.',
    match: (c) =>
      hasCanonical(c, ['medicina_nuclear', 'dosimetria']),
    steps: [
      'Decaimento radioativo',
      'Detectores',
      'Radiofármacos',
      'Dosimetria',
      'PET/SPECT',
      'Imagem',
      'Monte Carlo',
      'Dosimetria personalizada',
    ],
    projectKeywords: ['medicina', 'dosimetria', 'pet', 'radio'],
    bookKeywords: ['Cherry', 'Saha', 'Attix', 'Knoll'],
  },
  {
    id: 'radiation_protection',
    title: 'Proteção radiológica e segurança',
    description:
      'ALARA, blindagem, monitoração e cultura de segurança para laboratório e instalações.',
    match: (c) =>
      hasCanonical(c, ['protecao_radiologica']) &&
      hasCanonical(c, ['dosimetria', 'nuclear', 'engenharia_nuclear']),
    steps: [
      'Radiação ionizante',
      'Grandezas dosimétricas',
      'ALARA',
      'Blindagem',
      'Monitoração',
      'Avaliação de risco',
      'Emergência radiológica',
      'Regulamentação',
    ],
    projectKeywords: ['protecao', 'blindagem', 'dose', 'monitor'],
    bookKeywords: ['Cember', 'Shultis', 'Knoll'],
  },
  {
    id: 'space_systems',
    title: 'Sistemas espaciais',
    description: 'Mecânica orbital, satélites e subsistemas — trilha espacial distinta de voo atmosférico.',
    match: (c) => hasCanonical(c, ['espaco']),
    steps: [
      'Mecânica orbital',
      'Leis de Kepler',
      'Subsistemas de satélite',
      'Telecomando e telemetria',
      'CubeSat',
      'Sensoriamento remoto',
      'Ambiente espacial',
      'Missão espacial',
    ],
    projectKeywords: ['espaco', 'orbita', 'cubesat', 'satelite'],
    bookKeywords: ['Curtis', 'Wertz', 'Vallado'],
  },
];

/**
 * Rotas heurísticas por objetivo (Fase 2H-F).
 * @param {object} input
 */
export function buildScientificGoalRoutes({
  interests = [],
  studyBlocks = [],
  projectIdeas = [],
  books = [],
} = {}) {
  const canonical = [...new Set(interests.map(resolveCanonicalInterest).filter(Boolean))];
  const routes = [];

  for (const template of GOAL_ROUTE_TEMPLATES) {
    if (!template.match(canonical)) continue;

    const relatedBlocks = studyBlocks.filter((b) =>
      template.match([b.canonicalKey, ...(b.matchedInterests || [])].map(resolveCanonicalInterest)),
    );

    const routeBooks = pickBooks(books, 4);
    if (!routeBooks.length) {
      for (const b of relatedBlocks) {
        routeBooks.push(...(b.books || []).slice(0, 2));
        if (routeBooks.length >= 4) break;
      }
    }

    routes.push({
      id: template.id,
      title: template.title,
      description: template.description,
      steps: template.steps,
      suggestedProjects: pickProjects(projectIdeas, template.projectKeywords, 4),
      suggestedBooks: routeBooks.slice(0, 4),
      relatedCanonicalKeys: relatedBlocks.map((b) => b.canonicalKey),
    });
  }

  if (import.meta.env.DEV) {
    logScientificWorkspace('goal_routes_generated', {
      count: routes.length,
      ids: routes.map((r) => r.id),
    });
  }

  return routes;
}

/**
 * Melhor rota por objetivo para briefing/card.
 * @param {object} input
 */
export function pickPrimaryGoalRoute(input) {
  const routes = buildScientificGoalRoutes(input);
  return routes[0] || null;
}
