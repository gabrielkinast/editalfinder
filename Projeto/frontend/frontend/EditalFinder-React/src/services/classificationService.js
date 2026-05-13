// ─── Listas de palavras-chave ────────────────────────────────────────────────

const KEYWORDS_CREDITO = [
  'reembolsável', 'financiamento', 'financiar', 'empréstimo', 'juros',
  'carência', 'parcelas', 'amortização', 'crédito', 'linha de crédito',
  'taxa de juros', 'garantia', 'colateral', 'refinanciamento',
];

const KEYWORDS_SUBVENCAO = [
  'não reembolsável', 'nao reembolsavel', 'fundo perdido', 'subvenção',
  'subvencao', 'grant', 'auxílio', 'auxilio', 'incentivo', 'apoio financeiro',
  'apoio não reembolsável', 'bolsa', 'doação', 'doacao', 'recurso a fundo perdido',
];

// ─── Mapeamento de órgãos ────────────────────────────────────────────────────

const ORGAOS_SUBVENCAO = [
  { chaves: ['finep'], nome: 'FINEP' },
  { chaves: ['cnpq', 'conselho nacional de desenvolvimento científico'], nome: 'CNPq' },
  { chaves: ['sebrae'], nome: 'SEBRAE' },
  { chaves: ['embrapii'], nome: 'EMBRAPII' },
  { chaves: ['senai'], nome: 'SENAI' },
  { chaves: ['fapergs'], nome: 'FAPERGS' },
  { chaves: ['fapesp'], nome: 'FAPESP' },
  { chaves: ['fapemig'], nome: 'FAPEMIG' },
  { chaves: ['faperj'], nome: 'FAPERJ' },
  { chaves: ['fapesc'], nome: 'FAPESC' },
  { chaves: ['fapdf'], nome: 'FAPDF' },
  { chaves: ['capes'], nome: 'CAPES' },
  { chaves: ['mctic', 'mcti', 'ministério da ciência'], nome: 'MCTI' },
];

const ORGAOS_CREDITO = [
  { chaves: ['bndes', 'banco nacional de desenvolvimento'], nome: 'BNDES' },
  { chaves: ['brde', 'banco regional de desenvolvimento'], nome: 'BRDE' },
  { chaves: ['badesul'], nome: 'BADESUL' },
  { chaves: ['banco do nordeste', 'bnb'], nome: 'Banco do Nordeste' },
  { chaves: ['banco da amazônia', 'basa'], nome: 'Banco da Amazônia' },
  { chaves: ['banco do brasil'], nome: 'Banco do Brasil' },
  { chaves: ['caixa econômica', 'caixa economica', 'cef'], nome: 'Caixa Econômica Federal' },
];

// ─── Mapeamento de áreas ─────────────────────────────────────────────────────

const AREAS = [
  {
    nome: 'Tecnologia e Inovação',
    chaves: [
      'tecnologia', 'inovação', 'inovacao', 'software', 'inteligência artificial',
      'ia ', ' ia,', 'machine learning', 'dados', 'data', 'ti ', 'tech', 'pesquisa e desenvolvimento',
      'p&d', 'p & d', 'tic', 'biotecnologia', 'nanotecnologia', 'robótica', 'robotica',
    ],
  },
  {
    nome: 'Transformação Digital',
    chaves: [
      'transformação digital', 'transformacao digital', 'digitalização', 'digitalizacao',
      'automação', 'automacao', 'cloud', 'nuvem', 'cibersegurança', 'indústria 4.0',
      'industria 4.0', 'iot', 'internet das coisas',
    ],
  },
  {
    nome: 'Agronegócio',
    chaves: [
      'agro', 'agricultura', 'rural', 'pecuária', 'pecuaria', 'agrícola', 'agricola',
      'campo', 'lavoura', 'safra', 'irrigação', 'irrigacao', 'aquicultura', 'pesca',
      'silvicultura', 'florestal', 'alimentos', 'agroindústria', 'agroindustria',
    ],
  },
  {
    nome: 'Indústria',
    chaves: [
      'indústria', 'industria', 'industrial', 'manufatura', 'produção industrial',
      'fábrica', 'fabrica', 'processo produtivo', 'cadeia produtiva', 'setor produtivo',
    ],
  },
  {
    nome: 'Startups',
    chaves: [
      'startup', 'start-up', 'empreendedorismo', 'empreendedor', 'mei ',
      'micro empresa', 'microempresa', 'pequena empresa', 'aceleradora', 'incubadora',
      'pitch', 'venture', 'ecossistema de inovação',
    ],
  },
  {
    nome: 'Educação e Pesquisa',
    chaves: [
      'educação', 'educacao', 'pesquisa', 'ensino', 'ciência', 'ciencia',
      'acadêmico', 'academico', 'universidade', 'escola', 'graduação', 'graduacao',
      'pós-graduação', 'mestrado', 'doutorado', 'bolsa de pesquisa', 'laboratório',
    ],
  },
  {
    nome: 'Comércio e Serviços',
    chaves: [
      'comércio', 'comercio', 'serviço', 'servico', 'varejo', 'atacado',
      'logística', 'logistica', 'turismo', 'hotelaria', 'gastronomia',
    ],
  },
];

// ─── Funções auxiliares ───────────────────────────────────────────────────────

function textoBase(edital) {
  return [
    edital.titulo,
    edital.descricao,
    edital.objetivo,
    edital.temas,
    edital.fonte_recurso,
    edital.publico_alvo,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
}

function contarOcorrencias(texto, palavras) {
  return palavras.reduce((acc, p) => acc + (texto.includes(p) ? 1 : 0), 0);
}

function detectarOrgao(texto) {
  for (const o of [...ORGAOS_SUBVENCAO, ...ORGAOS_CREDITO]) {
    if (o.chaves.some(c => texto.includes(c))) return o.nome;
  }
  return null;
}

function orgaoEhSubvencao(orgaoNome) {
  return ORGAOS_SUBVENCAO.some(o => o.nome === orgaoNome);
}

function orgaoEhCredito(orgaoNome) {
  return ORGAOS_CREDITO.some(o => o.nome === orgaoNome);
}

function detectarAreas(texto) {
  return AREAS.filter(a => a.chaves.some(c => texto.includes(c))).map(a => a.nome);
}

// ─── Classificador principal ──────────────────────────────────────────────────

/**
 * Classifica um edital com base em regras de palavras-chave.
 * @param {Object} edital - Objeto com campos: titulo, descricao, objetivo, temas, fonte_recurso, publico_alvo
 * @returns {{ tipo: string, orgao: string|null, area: string[], nivel_confianca: number, justificativa: string }}
 */
export function classificarEdital(edital) {
  const texto = textoBase(edital);

  const pontosCredito = contarOcorrencias(texto, KEYWORDS_CREDITO);
  const pontosSubvencao = contarOcorrencias(texto, KEYWORDS_SUBVENCAO);
  const orgaoDetectado = detectarOrgao(texto);
  const areas = detectarAreas(texto);

  let tipo = '';
  let confianca = 0;
  let justificativa = '';

  // Decide o tipo com base no órgão (mais confiável) ou nas palavras-chave
  if (orgaoDetectado && orgaoEhSubvencao(orgaoDetectado) && orgaoEhCredito(orgaoDetectado) === false) {
    tipo = 'Subvenção econômica';
    confianca = 85;
    justificativa = `Órgão "${orgaoDetectado}" é reconhecido como financiador de subvenção econômica.`;
  } else if (orgaoDetectado && orgaoEhCredito(orgaoDetectado)) {
    tipo = 'Linha de crédito';
    confianca = 85;
    justificativa = `Órgão "${orgaoDetectado}" é reconhecido como instituição de crédito.`;
  } else if (pontosSubvencao > 0 && pontosCredito === 0) {
    tipo = 'Subvenção econômica';
    confianca = 70 + Math.min(pontosSubvencao * 5, 20);
    justificativa = `${pontosSubvencao} termo(s) de subvenção identificados no texto (ex: "não reembolsável", "fundo perdido").`;
  } else if (pontosCredito > 0 && pontosSubvencao === 0) {
    tipo = 'Linha de crédito';
    confianca = 70 + Math.min(pontosCredito * 5, 20);
    justificativa = `${pontosCredito} termo(s) de crédito identificados no texto (ex: "reembolsável", "juros").`;
  } else if (pontosSubvencao > 0 && pontosCredito > 0) {
    tipo = 'Híbrido';
    confianca = 60;
    justificativa = `Termos de subvenção (${pontosSubvencao}) e crédito (${pontosCredito}) encontrados — modalidade mista.`;
  } else {
    tipo = 'Subvenção econômica';
    confianca = 30;
    justificativa = 'Nenhum termo específico encontrado. Classificação padrão aplicada.';
  }

  return {
    tipo,
    orgao: orgaoDetectado,
    area: areas.length > 0 ? areas : ['Tecnologia e Inovação'],
    nivel_confianca: confianca,
    justificativa,
  };
}
