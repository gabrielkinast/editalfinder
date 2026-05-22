import { SCIENTIFIC_INTERESTS } from './scientificInterestsConfig';

/** Palavras-chave por interesse (Fase 1 — heurística local). */
const INTEREST_KEYWORDS = {
  nuclear: [
    'nuclear',
    'radiação',
    'radiacao',
    'reator',
    'urânio',
    'uranio',
    'radionuclídeo',
    'radionuclideo',
    'fissão',
    'fissao',
    'fusão',
    'fusao',
    'cnen',
    'iaea',
    'doe',
    'energia nuclear',
  ],
  fisico_quimica: [
    'físico-química',
    'fisico-quimica',
    'química física',
    'termodinâmica',
    'termodinamica',
    'cinética',
    'cinetica',
    'espectroscopia',
    'molecular',
    'simulação molecular',
    'simulacao molecular',
  ],
  materiais: [
    'materiais',
    'material',
    'ligas',
    'cerâmicas',
    'ceramicas',
    'polímeros',
    'polimeros',
    'semicondutor',
    'compósito',
    'composito',
    'nanomaterial',
  ],
  defesa: [
    'defesa',
    'militar',
    'army',
    'navy',
    'air force',
    'darpa',
    'afrl',
    'dod',
    'nato',
    'weapon',
    'aerospace',
    'security',
  ],
  espaco: [
    'space',
    'espaço',
    'espaco',
    'satélite',
    'satelite',
    'satellite',
    'nasa',
    'esa',
    'space force',
    'orbital',
  ],
  energia: [
    'energia',
    'hydrogen',
    'hidrogênio',
    'hidrogenio',
    'bateria',
    'solar',
    'eólica',
    'eolica',
    'nuclear energy',
    'grid',
  ],
  quantica: [
    'quantum',
    'quântico',
    'quantico',
    'quântica',
    'quantica',
    'qubit',
    'qst',
    'quantum computing',
  ],
  computacao_cientifica: [
    'simulação',
    'simulacao',
    'modelagem',
    'computational',
    'hpc',
    'monte carlo',
    'numerical',
    'python',
    'c++',
    'algoritmo',
  ],
  ia_cientifica: [
    'artificial intelligence',
    'machine learning',
    'deep learning',
    'autonomy',
    'scientific ai',
    ' ia ',
    'inteligência artificial',
    'inteligencia artificial',
  ],
  aeroespacial: ['aeroespacial', 'aerospace', 'aviação', 'aviacao', 'aeronáutica', 'aeronautica'],
  ciencia_dados: ['ciência dos dados', 'ciencia dos dados', 'data science', 'big data', 'analytics'],
  robotica: ['robótica', 'robotica', 'robotics', 'automação', 'automacao'],
  biotecnologia: ['biotecnologia', 'biotechnology', 'bioengenharia', 'genômica', 'genomica'],
  medicina_nuclear: [
    'medicina nuclear',
    'radioterapia',
    'pet',
    'spect',
    'pet-scan',
    'radiofármaco',
    'radiofarmaco',
    'terapia radionuclídica',
    'diagnóstico nuclear',
  ],
  engenharia_fisica: [
    'engenharia física',
    'applied physics',
    'instrumentação',
    'instrumentacao',
    'sensores',
    'modelagem',
    'simulação',
    'simulacao',
    'materiais',
    'energia',
  ],
  engenharia_nuclear: [
    'engenharia nuclear',
    'combustível nuclear',
    'combustivel nuclear',
    'termo-hidráulica',
    'termo-hidraulica',
    'neutrônica',
    'neutronica',
    'segurança nuclear',
    'seguranca nuclear',
    'blindagem',
    'reator',
  ],
  quimica_nuclear: [
    'química nuclear',
    'quimica nuclear',
    'radioquímica',
    'radioquimica',
    'radionuclídeo',
    'radionuclideo',
    'separação isotópica',
    'separacao isotopica',
    'actinídeos',
    'actinideos',
    'radioisótopos',
    'radioisotopos',
  ],
  radioquimica: [
    'radioquímica',
    'radioquimica',
    'radiotraçador',
    'radiotracer',
    'radioisótopo',
    'radioisotopo',
    'marcação radioativa',
    'marcacao radioativa',
    'radionuclídeo',
  ],
  engenharia_defesa: [
    'engenharia de defesa',
    'sistemas de armas',
    'radar',
    'mísseis',
    'misseis',
    'c4isr',
    'dual use',
    'dual-use',
    'segurança nacional',
  ],
  engenharia_aeroespacial: [
    'engenharia aeroespacial',
    'aeronáutica',
    'aeronautica',
    'propulsão',
    'propulsao',
    'foguete',
    'hypersonic',
    'hipersônico',
  ],
  plasmas: [
    'plasma',
    'física de plasmas',
    'fisica de plasmas',
    'tokamak',
    'confinamento magnético',
    'confinamento magnetico',
    'mhd',
  ],
  fusao: [
    'fusão nuclear',
    'fusao nuclear',
    'fusion',
    'stellarator',
    'iter',
    'deuterium',
    'deutério',
    'tritium',
    'trítio',
  ],
  dosimetria: [
    'dosimetria',
    'dose',
    'alara',
    'radiação ionizante',
    'radiacao ionizante',
    'detector de dose',
  ],
  protecao_radiologica: [
    'proteção radiológica',
    'protecao radiologica',
    'blindagem radiológica',
    'monitoramento radiológico',
    'área controlada',
  ],
  instrumentacao: [
    'instrumentação',
    'instrumentacao',
    'detector',
    'aquisição de dados',
    'aquisicao de dados',
    'labview',
    'eletrônica',
    'eletronica',
    'daq',
  ],
  hpc: [
    'hpc',
    'supercomputação',
    'supercomputacao',
    'paralelização',
    'paralelizacao',
    'cuda',
    'mpi',
    'openmp',
    'gpu',
    'cluster',
  ],
  modelagem_molecular: [
    'modelagem molecular',
    'química computacional',
    'quimica computacional',
    'dft',
    'molecular modeling',
    'potencial molecular',
  ],
  dinamica_molecular: [
    'dinâmica molecular',
    'dinamica molecular',
    'molecular dynamics',
    'lammps',
    'gromacs',
    'interação molecular',
    'interacao molecular',
  ],
  monte_carlo: [
    'monte carlo',
    'amostragem estocástica',
    'amostragem estocastica',
    'transporte de partículas',
    'transporte de particulas',
    'mcnp',
    'geant4',
    'simulação estatística',
  ],
  sistemas_autonomos: [
    'sistemas autônomos',
    'sistemas autonomos',
    'autonomia',
    'uav',
    'drone',
    'navegação autônoma',
    'navegacao autonoma',
  ],
  tecnologias_estrategicas: [
    'tecnologia estratégica',
    'tecnologia estrategica',
    'soberania tecnológica',
    'soberania tecnologica',
    'dual use',
    'semicondutores',
    'cadeia de suprimentos',
  ],
};

function normalizeText(item) {
  const parts = [
    item?.titulo,
    item?.resumo,
    item?.descricao,
    item?.fonte,
    item?.fonte_recurso,
    item?.area,
    item?.tipo_conteudo,
    Array.isArray(item?.tags) ? item.tags.join(' ') : item?.tags,
    Array.isArray(item?.eixos) ? item.eixos.join(' ') : item?.eixos,
    Array.isArray(item?.setores_estrategicos) ? item.setores_estrategicos.join(' ') : '',
  ];
  return parts
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function interestLabel(id) {
  return SCIENTIFIC_INTERESTS.find((i) => i.id === id)?.label || id;
}

/**
 * @param {object} item — item normalizado do feed
 * @param {string[]} activeInterests — ids de interesses ativos
 */
export function matchScientificItemToInterests(item, activeInterests = []) {
  const interests = Array.isArray(activeInterests) ? activeInterests : [];
  if (!interests.length) {
    return { score: 0, matchedInterests: [], reasons: [] };
  }

  const title = String(item?.titulo || '').toLowerCase();
  const blob = normalizeText(item);
  const matched = new Set();
  let score = 0;
  const reasons = [];

  for (const interestId of interests) {
    const keywords = INTEREST_KEYWORDS[interestId] || [];
    let hits = 0;
    let inTitle = false;
    for (const kw of keywords) {
      const k = kw
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
      if (!k || !blob.includes(k)) continue;
      hits += 1;
      if (title.includes(k)) {
        score += 2;
        inTitle = true;
      } else {
        score += 1;
      }
    }
    if (hits > 0) {
      matched.add(interestId);
      const label = interestLabel(interestId);
      reasons.push(
        inTitle
          ? `Termos de ${label} no título.`
          : `Relacionado ao interesse em ${label}.`,
      );
    }
  }

  const matchedInterests = [...matched];
  const reasonText =
    matchedInterests.length > 0
      ? `Relacionado a: ${matchedInterests.map(interestLabel).join(', ')}. ${reasons[0] || ''}`.trim()
      : '';

  return {
    score,
    matchedInterests,
    reasons: reasonText ? [reasonText] : [],
  };
}
