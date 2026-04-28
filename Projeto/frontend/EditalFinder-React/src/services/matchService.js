// ─── Helpers de texto ────────────────────────────────────────────────────────

// Palavras muito genéricas que aparecem em quase todo edital e não ajudam a diferenciar afinidade temática.
const STOPWORDS = new Set([
  'projeto', 'projetos', 'proposta', 'propostas',
  'participa', 'participar', 'participacao', 'participante', 'participantes',
  'edital', 'editais', 'chamada', 'chamadas',
  'programa', 'programas', 'apoio', 'apoios',
  'fundo', 'fundos', 'fundacao', 'fundacoes',
  'publico', 'publica', 'publicas', 'publicos',
  'empresa', 'empresas', 'instituicao', 'instituicoes', 'organizacao', 'organizacoes',
  'fomento', 'desenvolvimento', 'desenvolver', 'desenvolvida', 'desenvolvido',
  'area', 'areas', 'setor', 'setores', 'tema', 'temas',
  'brasil', 'brasileiro', 'brasileira', 'brasileiros', 'brasileiras',
  'nacional', 'nacionais', 'regional', 'regionais', 'estadual', 'estaduais',
  'federal', 'federais', 'municipal', 'municipais', 'estado', 'estados',
  'processo', 'processos', 'selecao', 'selecoes',
  'geral', 'geraes', 'geralmente', 'especifico', 'especifica',
  'recurso', 'recursos', 'investimento', 'investimentos', 'investir',
  'pessoa', 'pessoas', 'pessoal', 'pessoais',
  'novo', 'nova', 'novos', 'novas',
  'melhor', 'melhores', 'maior', 'maiores', 'menor', 'menores',
  'brasil', 'pais', 'paises', 'regiao', 'regioes',
  'formato', 'modalidade', 'modalidades',
  'entidade', 'entidades', 'outros', 'outras',
  'informacao', 'informacoes', 'dados',
  'trabalho', 'trabalhos', 'atividade', 'atividades',
  'conforme', 'portanto', 'sobre', 'atraves', 'demais',
]);

function tokenizar(texto) {
  return (texto || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .split(/[,;\s\/\-\+\.()[\]{}]+/)
    .map(t => t.trim())
    .filter(t => t.length > 2);
}

function tokenizarUtil(texto) {
  return tokenizar(texto).filter(t => !STOPWORDS.has(t));
}

/**
 * Interseção forte entre dois conjuntos de tokens:
 * - casamento exato, ou
 * - prefixo/sufixo apenas quando ambos os tokens são longos (≥ 6 chars),
 *   evitando que "tic" (sinônimo de tecnologia) case com "politica", "critica" etc.
 */
function intersecaoForte(a, b) {
  const setB = new Set(b);
  const fortes = b.filter(t => t.length >= 6);
  const matches = [];
  for (const ta of a) {
    if (setB.has(ta)) { matches.push(ta); continue; }
    if (ta.length >= 6) {
      const hit = fortes.find(tb => tb !== ta && (tb.startsWith(ta) || ta.startsWith(tb)));
      if (hit) matches.push(ta);
    }
  }
  return matches;
}

function textoContem(texto, termos) {
  const t = (texto || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  return termos.some(p => t.includes(p));
}

function normalizarChave(s) {
  return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
}

// ─── Dicionário leve de sinônimos temáticos ──────────────────────────────────
// Mapeia um conceito-base (sem acento) para sinônimos que costumam aparecer nos editais.

const SINONIMOS = {
  tecnologia:      ['ti', 'tic', 'tech', 'digital', 'software', 'hardware', 'informatica', 'computacao', 'tecnologico', 'tecnologica', 'tecnologicos', 'tecnologicas'],
  inovacao:        ['inovador', 'inovadora', 'inovadores', 'inovadoras', 'inovacoes', 'pesquisa', 'pesquisas', 'desenvolvimento', 'pd', 'startup', 'startups'],
  saude:           ['hospital', 'hospitalar', 'medicina', 'medicinal', 'clinico', 'clinica', 'clinicas', 'medico', 'medica', 'farmaceutico', 'farmaceutica', 'sanitario', 'sanitaria', 'sus', 'saudavel', 'saudaveis'],
  esporte:         ['esportes', 'esportivo', 'esportiva', 'esportivos', 'esportivas', 'desporto', 'desportivo', 'desportiva', 'atletismo', 'atleta', 'atletas', 'paradesporto'],
  educacao:        ['ensino', 'pedagogia', 'pedagogico', 'pedagogica', 'escola', 'escolas', 'escolar', 'educacional', 'educacionais', 'educativo', 'educativa', 'educativos', 'educativas', 'aprendizagem', 'formacao'],
  energia:         ['energetica', 'energetico', 'renovavel', 'renovaveis', 'solar', 'eolica', 'fotovoltaica', 'biocombustivel', 'biocombustiveis'],
  agro:            ['agronegocio', 'agropecuaria', 'agricola', 'agricolas', 'rural', 'rurais', 'agricultura', 'pecuaria', 'fazenda', 'fazendas'],
  social:          ['socioambiental', 'comunitario', 'comunitaria', 'terceirosetor', 'ong', 'assistencia', 'assistencial', 'assistenciais'],
  sustentabilidade:['sustentavel', 'sustentaveis', 'ambiental', 'ambientais', 'verde', 'ecologico', 'ecologica', 'climatico', 'climatica'],
  industria:       ['industrial', 'industriais', 'manufatura', 'manufatureiro', 'fabril', 'producao', 'automacao', 'automatizada'],
  cultura:         ['cultural', 'culturais', 'artistico', 'artistica', 'arte', 'artes', 'patrimonio', 'criativo', 'criativa'],
  turismo:         ['turistico', 'turistica', 'hotelaria', 'hoteleiro', 'hoteleira'],
  biotec:          ['biotecnologia', 'biotecnologica', 'biotech', 'bioeconomia', 'biologico', 'biologica'],
};

/**
 * Expande tokens com sinônimos apenas quando há correspondência exata entre o token
 * e a chave (ou um sinônimo listado). Ignora stopwords para evitar poluição.
 */
function tokenizarComSinonimos(texto) {
  const base = tokenizarUtil(texto);
  const set = new Set(base);
  for (const t of base) {
    for (const [chave, syns] of Object.entries(SINONIMOS)) {
      if (t === chave || syns.includes(t)) {
        set.add(chave);
        for (const s of syns) if (s.length > 2) set.add(s);
      }
    }
  }
  return [...set];
}

// ─── Helpers de avaliação temporal / maturidade / idade ──────────────────────

function idadeAnos(dataAbertura) {
  if (!dataAbertura) return null;
  const d = new Date(dataAbertura);
  if (Number.isNaN(d.getTime())) return null;
  return (Date.now() - d.getTime()) / (365.25 * 24 * 3600 * 1000);
}

function diasParaPrazo(edital) {
  const p = edital.dataLimite || edital.prazo_envio;
  if (!p) return null;
  const d = new Date(p);
  if (Number.isNaN(d.getTime())) return null;
  return Math.floor((d.getTime() - Date.now()) / (24 * 3600 * 1000));
}

/**
 * Avalia viabilidade temporal do edital.
 * @returns {{ pts: number, rotulo: ('expirado'|'curto'|'medio'|'longo'|null), expirado: boolean, dias: (number|null) }}
 */
export function avaliarPrazo(edital) {
  const dias = diasParaPrazo(edital);
  const status = (edital.status || '').toLowerCase();
  const situacao = (edital.situacao || '').toLowerCase();
  const statusInativo = status && status !== 'ativo';
  const situacaoEncerrada = /encerr|finaliz|fechad|concluid/.test(situacao);

  if (statusInativo || situacaoEncerrada) {
    return { pts: 0, rotulo: 'expirado', expirado: true, dias };
  }
  if (dias == null) return { pts: 3, rotulo: null, expirado: false, dias: null };
  if (dias < 0)     return { pts: 0, rotulo: 'expirado', expirado: true, dias };
  if (dias < 7)     return { pts: 1, rotulo: 'curto',   expirado: false, dias };
  if (dias <= 30)   return { pts: 3, rotulo: 'medio',   expirado: false, dias };
  return               { pts: 5, rotulo: 'longo',   expirado: false, dias };
}

const MATURIDADE_TERMOS = {
  'Ideação':   ['ideacao', 'ideia', 'concepcao', 'pre-seed', 'preseed', 'incubacao', 'incubadora', 'prototipacao'],
  'Validação': ['validacao', 'prova de conceito', 'mvp', 'poc', 'prototipo', 'piloto', 'teste'],
  'Operação':  ['operacao', 'crescimento', 'tracao', 'aceleracao', 'seed', 'acelera'],
  'Escala':    ['escala', 'scale', 'scaleup', 'internacionalizacao', 'series a', 'series b'],
};

function avaliarMaturidade(cliente, edital) {
  const nivel = cliente.nivel_maturidade;
  const termos = MATURIDADE_TERMOS[nivel] || null;
  const textoE = [
    edital.objetivo, edital.publico_alvo, edital.elegibilidade, edital.descricao, edital.titulo,
  ].filter(Boolean).join(' ');

  let pts = 5; // neutro se não houver referência explícita
  let matched = false;
  if (termos && textoContem(textoE, termos)) {
    pts = 10;
    matched = true;
  }
  if (cliente.tem_projeto_inovacao && textoContem(textoE, ['inovacao', 'pesquisa', 'p&d', 'pd', 'desenvolvimento', 'inovador'])) {
    pts += 3;
  }
  return { pts: Math.min(pts, 10), matched };
}

function avaliarIdade(cliente, edital) {
  const textoE = [edital.elegibilidade, edital.publico_alvo, edital.descricao]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
  const match = textoE.match(/m[ií]?nim[oa]\s+de?\s+(\d+)\s+anos?/);
  if (!match) return { pts: 3, exigencia: null, cumpre: null };
  const exig = parseInt(match[1], 10);
  if (!Number.isFinite(exig)) return { pts: 3, exigencia: null, cumpre: null };
  const idade = idadeAnos(cliente.data_abertura);
  if (idade == null) return { pts: 1, exigencia: exig, cumpre: null };
  if (idade >= exig) return { pts: 5, exigencia: exig, cumpre: true };
  return { pts: 0, exigencia: exig, cumpre: false };
}

// ─── JSON `compatibilidade` do edital ─────────────────────────────────────────

/**
 * Converte o JSONB `compatibilidade` do edital em mapa perfil → 0..100.
 */
export function parseCompatibilidadePerfis(raw) {
  if (raw == null) return null;
  let o = raw;
  if (typeof raw === 'string') {
    try { o = JSON.parse(raw); } catch { return null; }
  }
  if (typeof o !== 'object' || o === null || Array.isArray(o)) return null;
  const out = {};
  for (const [k, v] of Object.entries(o)) {
    const key = String(k).trim();
    if (!key) continue;
    const num = typeof v === 'number' ? v : parseFloat(String(v).replace(',', '.'));
    if (!Number.isFinite(num)) continue;
    out[key] = Math.min(100, Math.max(0, Math.round(num)));
  }
  return Object.keys(out).length > 0 ? out : null;
}

/**
 * Escolhe uma chave do JSON `compatibilidade` que **realmente** corresponde ao cadastro do cliente.
 */
function escolherPerfilNoMapa(cliente, mapa) {
  const keys = Object.keys(mapa);
  if (keys.length === 0) return null;

  const candidatos = [
    cliente.perfil,
    cliente.tipo_perfil,
    cliente.categoria_empresa,
    cliente.natureza_juridica,
    cliente.setor,
    cliente.cnae_principal,
  ].filter(Boolean).map(String);

  const nCand = candidatos.map(normalizarChave).filter(Boolean);

  for (const key of keys) {
    const nk = normalizarChave(key);
    for (const nc of nCand) {
      if (nk === nc || nc.includes(nk) || nk.includes(nc)) return key;
    }
  }

  const porte = normalizarChave(cliente.porte_empresa);
  for (const key of keys) {
    if (normalizarChave(key) === porte) return key;
  }

  const blob = normalizarChave(
    [cliente.setor, cliente.cnae_principal, cliente.interesse_temas, cliente.area_inovacao, cliente.descricao_projeto]
      .filter(Boolean)
      .join(' ')
  );
  let bestKey = null;
  let bestHits = 0;
  for (const key of keys) {
    const nk = normalizarChave(key);
    const partes = nk.split(/[\s/\-+]+/).filter(p => p.length > 2);
    let hits = 0;
    for (const p of partes) if (blob.includes(p)) hits++;
    if (hits > bestHits) { bestHits = hits; bestKey = key; }
  }
  return bestHits > 0 ? bestKey : null;
}

/** Pesos do índice final do Radar (JSON × cálculo do cadastro). */
const RADAR_PESO_JSON = 0.35;
const RADAR_PESO_CADASTRO = 0.65;

// ─── Mapeamento de porte ─────────────────────────────────────────────────────

const PORTE_TERMOS = {
  'MEI':    ['mei', 'micro empreendedor', 'microempreendedor', 'empreendedor individual'],
  'ME':     ['micro empresa', 'microempresa', 'pequena empresa', 'mpe'],
  'EPP':    ['epp', 'empresa pequeno porte', 'pequeno porte', 'pequena', 'mpe'],
  'Média':  ['media empresa', 'empresa media', 'medio porte'],
  'Grande': ['grande empresa', 'grande porte', 'grande'],
};

const PORTE_EXCLUSOES = {
  'MEI':    ['grande', 'media empresa', 'grande porte', 'medio porte'],
  'ME':     ['grande', 'media empresa', 'grande porte'],
  'EPP':    ['grande', 'grande porte'],
  'Média':  ['mei', 'microempreendedor'],
  'Grande': ['mei', 'micro', 'pequena'],
};

// ─── Texto base: área / temas (cliente × edital) ─────────────────────────────

function textoClienteAreaTemas(cliente) {
  return [
    cliente.area_inovacao,
    cliente.setor,
    cliente.cnae_principal,
    cliente.interesse_temas,
    cliente.descricao_projeto,
  ].filter(Boolean).join(' ');
}

function textoEditalAreaTemas(edital) {
  return [
    edital.area,
    edital.titulo,
    edital.temas,
    edital.objetivo,
    edital.publico_alvo,
    edital.elegibilidade,
    edital.descricao,
    edital.ods,
  ].filter(Boolean).join(' ');
}

export function editalTemSobreposicaoAreaComCliente(cliente, edital) {
  const raw = textoClienteAreaTemas(cliente).trim();
  const kwCliente = tokenizarComSinonimos(textoClienteAreaTemas(cliente));
  if (!raw || kwCliente.length === 0) return true;
  const kwEdital = tokenizarComSinonimos(textoEditalAreaTemas(edital));
  return intersecaoForte(kwCliente, kwEdital).length > 0;
}

export function tiposRecursoEditaisNaAreaDoCliente(cliente, editais) {
  const tipos = new Set();
  for (const e of editais) {
    if (!editalTemSobreposicaoAreaComCliente(cliente, e)) continue;
    const t = (e.tipoRecurso || '').trim();
    if (t) tipos.add(t);
  }
  return [...tipos].sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

// ─── Novo motor de score: 8 critérios (100 pts) ──────────────────────────────

/**
 * Rótulos e pesos máximos dos critérios (usados na UI como legenda/mini-barras).
 */
export const CRITERIOS = [
  { key: 'afinidade',    label: 'Afinidade temática',    max: 30 },
  { key: 'localizacao',  label: 'Localização',            max: 15 },
  { key: 'porte',        label: 'Porte e elegibilidade',  max: 15 },
  { key: 'maturidade',   label: 'Maturidade do projeto',  max: 10 },
  { key: 'valor',        label: 'Faixa de valor',         max: 10 },
  { key: 'regularidade', label: 'Regularidade',           max: 10 },
  { key: 'prazo',        label: 'Prazo e situação',       max: 5  },
  { key: 'idade',        label: 'Idade da empresa',       max: 5  },
];

/**
 * Calcula o score do cadastro (cliente × edital) com 8 critérios, total 100 pts.
 *
 * @param {Object} cliente  Registro da tabela `cliente`
 * @param {Object} edital   Objeto formatado pelo dataService
 * @returns {{ score: number, compatibilidade: string, razoes: string[], detalhes: Object, prazoInfo: Object, expirado: boolean }}
 */
export function calcularScore(cliente, edital) {
  let score = 0;
  const razoes = [];
  const detalhes = {
    afinidade: 0, localizacao: 0, porte: 0, maturidade: 0,
    valor: 0, regularidade: 0, prazo: 0, idade: 0,
  };

  // C1. AFINIDADE TEMÁTICA (até 30 pts)
  // Estratégia em duas camadas para ter ordenação mais precisa:
  //   (a) Núcleo conceitual: tokens do SETOR/ÁREA do cliente (setor + cnae_principal + area_inovacao)
  //       cruzam com os campos centrais do edital (temas + titulo + area + objetivo + publico_alvo).
  //       Cada casamento único vale mais (até 20 pts).
  //   (b) Interesses e descrição do projeto vs. descrição/elegibilidade do edital (até 10 pts).
  const kwNucleoCli = tokenizarComSinonimos(
    [cliente.setor, cliente.cnae_principal, cliente.area_inovacao].filter(Boolean).join(' ')
  );
  const kwNucleoEd  = tokenizarComSinonimos(
    [edital.temas, edital.titulo, edital.area, edital.objetivo, edital.publico_alvo].filter(Boolean).join(' ')
  );
  const matchNucleo = [...new Set(intersecaoForte(kwNucleoCli, kwNucleoEd))];

  const kwInterCli = tokenizarComSinonimos(
    [cliente.interesse_temas, cliente.descricao_projeto].filter(Boolean).join(' ')
  );
  const kwInterEd  = tokenizarComSinonimos(
    [edital.descricao, edital.elegibilidade, edital.publico_alvo, edital.objetivo].filter(Boolean).join(' ')
  );
  const matchInter = [...new Set(intersecaoForte(kwInterCli, kwInterEd))];

  let ptNucleo  = Math.min(20, matchNucleo.length * 5);
  let ptInteres = Math.min(10, matchInter.length * 2);

  // Bônus ODS ×interesse_temas (máx +3, dentro do teto de 30)
  let bonusOds = 0;
  const odsEd    = (edital.ods || '').toString();
  const temasCli = (cliente.interesse_temas || '').toString();
  if (odsEd && temasCli) {
    const odsTokens = tokenizar(odsEd).filter(t => !STOPWORDS.has(t));
    const temasNorm = normalizarChave(temasCli);
    if (odsTokens.some(t => t.length >= 4 && temasNorm.includes(t))) bonusOds = 3;
  }

  let ptAfin = Math.min(30, ptNucleo + ptInteres + bonusOds);
  detalhes.afinidade = ptAfin;
  score += ptAfin;

  const razoesAfin = [...matchNucleo, ...matchInter.filter(t => !matchNucleo.includes(t))].slice(0, 3);
  if (razoesAfin.length > 0) razoes.push(`Afinidade: ${razoesAfin.join(', ')}`);
  else if (ptAfin === 0) razoes.push('Sem afinidade direta com a área do cliente');

  // C2. LOCALIZAÇÃO (até 15 pts)
  const estadoCli = (cliente.estado || '').toLowerCase().trim();
  const regiaoCli = (cliente.regiao || '').toLowerCase().trim();
  const estadoEd  = (edital.estado || '').toLowerCase().trim();
  const regiaoEd  = (edital.regiao || '').toLowerCase().trim();
  const localEd   = (edital.localidade || '').toLowerCase().trim();

  const isNacional  = !estadoEd || estadoEd === 'nacional' || localEd === 'nacional' || regiaoEd === 'nacional';
  const mesmoEstado = estadoCli && estadoEd && (estadoCli === estadoEd || estadoEd.includes(estadoCli));
  const mesmaRegiao = regiaoCli && regiaoEd && (regiaoEd.includes(regiaoCli) || regiaoCli.includes(regiaoEd));

  let ptLocal = 0;
  if (isNacional || mesmoEstado) {
    ptLocal = 15;
    razoes.push(isNacional ? 'Abrangência nacional' : `Estado: ${cliente.estado?.toUpperCase?.()}`);
  } else if (mesmaRegiao) {
    ptLocal = 10;
    razoes.push(`Região: ${cliente.regiao}`);
  } else if (!estadoEd && !regiaoEd) {
    ptLocal = 10;
  }
  detalhes.localizacao = ptLocal;
  score += ptLocal;

  // C3. PORTE E ELEGIBILIDADE (até 15 pts)
  const porte = (cliente.porte_empresa || '').trim();
  const textoElegib = [
    edital.elegibilidade, edital.publico_alvo, edital.temas,
    edital.objetivo, edital.titulo, edital.area,
  ].filter(Boolean).join(' ');
  const termosPorte    = PORTE_TERMOS[porte]    || [];
  const termosExclusao = PORTE_EXCLUSOES[porte] || [];
  const porteBate      = termosPorte.length > 0 && textoContem(textoElegib, termosPorte);
  const porteExcluido  = termosExclusao.length > 0 && textoContem(textoElegib, termosExclusao);
  const semRestricao   = !textoContem(textoElegib, [
    'mei', 'micro', 'pequena', 'grande', 'medio porte', 'grande porte',
  ]);

  let ptPorte = 0;
  if (porteExcluido && !porteBate) {
    ptPorte = 0;
  } else if (porteBate) {
    ptPorte = 15;
    razoes.push(`Porte ${porte} compatível`);
  } else if (semRestricao) {
    ptPorte = 10;
  } else {
    ptPorte = 10;
  }
  const cnae = (cliente.cnae_principal || '').trim();
  if (cnae && textoElegib && textoElegib.toLowerCase().includes(cnae.toLowerCase())) {
    ptPorte = Math.min(15, ptPorte + 5);
    razoes.push(`CNAE ${cnae} citado`);
  }
  detalhes.porte = ptPorte;
  score += ptPorte;

  // C4. MATURIDADE DO PROJETO (até 10 pts)
  const matur = avaliarMaturidade(cliente, edital);
  detalhes.maturidade = matur.pts;
  score += matur.pts;
  if (matur.matched && cliente.nivel_maturidade) {
    razoes.push(`Maturidade «${cliente.nivel_maturidade}» alinhada`);
  }

  // C5. FAIXA DE VALOR (até 10 pts)
  const cliMin = parseFloat(cliente.interesse_valor_min) || 0;
  const cliMax = parseFloat(cliente.interesse_valor_max) || 0;
  const edMin  = parseFloat(edital.valorMinimo)          || 0;
  const edMax  = parseFloat(edital.valorMaximo || edital.valor) || 0;

  let ptValor = 0;
  if (cliMin === 0 && cliMax === 0)      ptValor = 5;
  else if (edMin === 0 && edMax === 0)   ptValor = 5;
  else {
    const overlapMin = Math.max(cliMin, edMin);
    const overlapMax = Math.min(cliMax > 0 ? cliMax : Infinity, edMax > 0 ? edMax : Infinity);
    if (overlapMax >= overlapMin) {
      const rangeCliente = (cliMax > 0 ? cliMax : edMax) - cliMin;
      const overlapSize  = overlapMax - overlapMin;
      const cobertura    = rangeCliente > 0 ? overlapSize / rangeCliente : 1;
      ptValor = cobertura >= 0.5 ? 8 : 5;
      if (ptValor === 8) razoes.push('Valor dentro da faixa de interesse');
    }
  }
  const fatAnual = parseFloat(cliente.faturamento_anual) || 0;
  if (fatAnual > 0 && edMax > 0 && fatAnual >= edMax * 0.33) {
    ptValor = Math.min(10, ptValor + 2);
  }
  detalhes.valor = ptValor;
  score += ptValor;

  // C6. REGULARIDADE E CONTRAPARTIDA (até 10 pts)
  let ptReg = 0;
  if (cliente.regular_fiscal && cliente.regular_trabalhista) ptReg += 4;
  else if (cliente.regular_fiscal || cliente.regular_trabalhista) ptReg += 2;
  if (cliente.possui_certidao_negativa) ptReg += 3;
  const editalExigeContrapartida = textoContem(edital.contrapartida || '', ['sim', 'obrigatoria', 'exigida', 'requerida']);
  if (cliente.disponibilidade_contrapartida) ptReg += editalExigeContrapartida ? 3 : 1;
  ptReg = Math.min(ptReg, 10);
  detalhes.regularidade = ptReg;
  score += ptReg;
  if (ptReg >= 7) razoes.push('Regularidade completa');

  // C7. PRAZO E SITUAÇÃO (até 5 pts)
  const prazo = avaliarPrazo(edital);
  detalhes.prazo = prazo.pts;
  score += prazo.pts;
  if (prazo.expirado)                razoes.push('Edital expirado');
  else if (prazo.rotulo === 'longo') razoes.push('Prazo confortável');
  else if (prazo.rotulo === 'curto') razoes.push('Prazo curto — urgência');

  // C8. IDADE DA EMPRESA (até 5 pts)
  const idade = avaliarIdade(cliente, edital);
  detalhes.idade = idade.pts;
  score += idade.pts;
  if (idade.cumpre === true)       razoes.push(`Idade ≥ ${idade.exigencia} anos cumprida`);
  else if (idade.cumpre === false) razoes.push(`Edital exige ${idade.exigencia}+ anos de CNPJ`);

  score = Math.min(Math.round(score), 100);

  // Teto por afinidade: sem sobreposição com a área do cliente, o edital não pode ser "Alta".
  // Garante que a ordenação reflita o perfil da empresa mesmo quando o edital tem prazo longo,
  // abrangência nacional e faixa de valor aberta.
  const temInputAfinidade = (
    (cliente.setor || cliente.cnae_principal || cliente.area_inovacao ||
     cliente.interesse_temas || cliente.descricao_projeto || '').toString().trim().length > 0
  );
  if (temInputAfinidade) {
    if (ptAfin === 0)      score = Math.min(score, 40);
    else if (ptAfin < 10)  score = Math.min(score, 70);
  }

  let compatibilidade;
  if      (score >= 75) compatibilidade = 'Alta';
  else if (score >= 45) compatibilidade = 'Média';
  else                  compatibilidade = 'Baixa';

  return {
    score,
    compatibilidade,
    razoes,
    detalhes,
    prazoInfo: prazo,
    expirado: prazo.expirado,
  };
}

/**
 * Radar: combina o percentual do perfil no JSON `compatibilidade` do edital com o cálculo do cadastro.
 * Só usa o JSON quando existe uma chave correspondente ao perfil do cliente.
 */
export function resolverRadarMatch(cliente, edital) {
  const mapa   = parseCompatibilidadePerfis(edital.compatibilidade);
  const legado = calcularScore(cliente, edital);
  const leg    = Number.isFinite(legado.score) ? legado.score : 0;

  const classif = (s) => (s >= 75 ? 'Alta' : s >= 45 ? 'Média' : 'Baixa');

  if (mapa) {
    const perfil = escolherPerfilNoMapa(cliente, mapa);
    if (perfil == null) {
      return {
        ...legado,
        score: leg,
        compatibilidade: classif(leg),
        matchLinha: `Match de ${leg}% pelo seu cadastro (o edital traz índices por perfil, mas nenhum corresponde ao seu cadastro)`,
        perfilMatch: null,
        fonteMatch: 'calculado',
      };
    }
    const jRaw = mapa[perfil];
    const jNum = Math.min(100, Math.max(0, Math.round(Number.isFinite(jRaw) ? jRaw : 0)));
    const scoreRounded = Math.min(
      100,
      Math.max(0, Math.round(RADAR_PESO_JSON * jNum + RADAR_PESO_CADASTRO * leg))
    );
    return {
      ...legado,
      score: scoreRounded,
      compatibilidade: classif(scoreRounded),
      matchLinha: `Match de ${scoreRounded}% — perfil «${perfil}» no edital (${jNum}%) + cadastro (${leg}%)`,
      perfilMatch: perfil,
      fonteMatch: 'hibrido',
    };
  }

  return {
    ...legado,
    score: leg,
    compatibilidade: classif(leg),
    matchLinha: `Match de ${leg}% estimado pelo seu cadastro`,
    perfilMatch: null,
    fonteMatch: 'calculado',
  };
}

/**
 * Lista editais ordenada por compatibilidade.
 * Desempate: prazo mais próximo entre editais válidos; expirados ficam no final.
 */
export function recomendarEditais(cliente, editais) {
  const now = Date.now();
  return editais
    .map(edital => ({ edital, ...resolverRadarMatch(cliente, edital) }))
    .sort((a, b) => {
      const expA = a.expirado ? 1 : 0;
      const expB = b.expirado ? 1 : 0;
      if (expA !== expB) return expA - expB;
      if (b.score !== a.score) return b.score - a.score;
      const tA = new Date(a.edital.dataLimite || 0).getTime();
      const tB = new Date(b.edital.dataLimite || 0).getTime();
      const vA = tA >= now ? tA - now : Number.POSITIVE_INFINITY;
      const vB = tB >= now ? tB - now : Number.POSITIVE_INFINITY;
      return vA - vB;
    });
}
