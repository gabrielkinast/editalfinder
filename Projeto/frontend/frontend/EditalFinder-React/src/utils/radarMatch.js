/**
 * Motor do Radar de Fomento: matching cliente × oportunidade em etapas
 * (normalização → filtros eliminatórios → critérios → penalidades → explicações).
 *
 * Pesos (total 100): afinidade 30, perfil 20, tipo 15, localização 10,
 * prazo 10, qualidade 10, valor 5.
 */

// ─── Normalização e tokens ───────────────────────────────────────────────────

export const RADAR_STOPWORDS = new Set([
  'para', 'com', 'sem', 'uma', 'um', 'dos', 'das', 'que', 'por',
  'de', 'da', 'do', 'em', 'no', 'na', 'os', 'as', 'ao', 'aos',
  'edital', 'chamada', 'programa', 'oportunidade', 'publica',
  'the', 'and', 'for', 'with', 'from', 'this', 'that', 'call',
  'program', 'opportunity',
]);

export function normalizar(texto) {
  return String(texto ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\w\s-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function normalizarArray(valor) {
  if (!valor) return [];
  if (Array.isArray(valor)) return valor.map((x) => normalizar(String(x))).filter(Boolean);
  return String(valor)
    .split(/[,;|]/)
    .map(normalizar)
    .filter(Boolean);
}

export function tokens(texto) {
  return normalizar(texto)
    .split(/\s+/)
    .filter((t) => t.length >= 3 && !RADAR_STOPWORDS.has(t));
}

// ─── Sinônimos (expansão de conceitos para afinidade) ─────────────────────────

export const RADAR_SINONIMOS = {
  ia: ['inteligencia artificial', 'ai', 'machine learning', 'aprendizado de maquina'],
  energia: ['energia limpa', 'energia renovavel', 'hidrogenio', 'bateria', 'eficiencia energetica', 'solar', 'eolica'],
  nuclear: ['energia nuclear', 'radioisotopos', 'radiacao', 'reator', 'fissao'],
  aeroespacial: ['espaco', 'espacial', 'satelite', 'aerospace', 'space', 'aviacao'],
  materiais: ['materiais avancados', 'nanomateriais', 'compositos', 'polimeros'],
  credito: ['financiamento', 'emprestimo', 'linha de credito', 'reembolsavel'],
  subvencao: ['nao reembolsavel', 'subvencao economica', 'grant'],
  fornecedor: ['supplier', 'vendor', 'cadastro fornecedor', 'supplier portal'],
  startup: ['empresa nascente', 'empreendedor', 'scaleup', 'deep tech'],
  pesquisa: ['pdi', 'pd&i', 'pesquisa desenvolvimento inovacao', 'r&d', 'rnd'],
  tecnologia: ['ti', 'tic', 'tech', 'digital', 'software', 'inovacao'],
  saude: ['medicina', 'hospital', 'clinico', 'farmaceutico'],
  agricultura: ['agro', 'agronegocio', 'rural', 'pecuaria'],
};

export function expandirTermos(termos) {
  const base = normalizarArray(termos);
  const out = new Set(base);

  for (const termo of base) {
    for (const [chave, lista] of Object.entries(RADAR_SINONIMOS)) {
      const chaveNorm = normalizar(chave);
      const listaNorm = lista.map(normalizar);
      if (termo === chaveNorm || listaNorm.includes(termo)) {
        out.add(chaveNorm);
        listaNorm.forEach((x) => out.add(x));
      }
    }
  }
  return [...out];
}

export function jaccard(a, b) {
  const A = new Set(a);
  const B = new Set(b);
  if (A.size === 0 || B.size === 0) return 0;
  const inter = [...A].filter((x) => B.has(x)).length;
  const union = new Set([...A, ...B]).size;
  return union ? inter / union : 0;
}

// ─── Datas e prazo ───────────────────────────────────────────────────────────

export function diasAtePrazo(prazo) {
  if (!prazo) return null;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const data = new Date(prazo);
  if (Number.isNaN(data.getTime())) return null;
  data.setHours(0, 0, 0, 0);
  return Math.ceil((data.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));
}

function idadeEmpresaAnos(dataAbertura) {
  if (!dataAbertura) return null;
  const d = new Date(dataAbertura);
  if (Number.isNaN(d.getTime())) return null;
  return (Date.now() - d.getTime()) / (365.25 * 24 * 3600 * 1000);
}

// ─── Mapeamento Supabase → modelos internos ──────────────────────────────────

function splitListaCampo(val) {
  if (!val) return [];
  if (Array.isArray(val)) return val.map(String).filter(Boolean);
  return String(val)
    .split(/[,;\n|]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/** Infere tipo de recurso textual a partir da classificação + campos crus. */
export function inferTiposEditalParaMatch(e) {
  const partes = [
    e?.tipo_oportunidade,
    e?.tipo_recurso,
    e?.tipoRecurso,
    e?.natureza_recurso,
    e?.modalidade_financiamento,
    e?.linha_credito,
    e?.tipo_recurso_raw,
    e?.reembolsavel === true ? 'reembolsavel credito financiamento' : '',
    e?.reembolsavel === false ? 'nao reembolsavel subvencao grant' : '',
    e?.titulo,
    e?.descricao,
    e?.elegibilidade,
  ];
  return expandirTermos(tokens(partes.filter(Boolean).join(' ')));
}

function parseTiposInteresseCliente(clienteRow) {
  const raw = clienteRow?.tipos_interesse ?? clienteRow?.interesse_tipos_recursos;
  if (Array.isArray(raw)) return expandirTermos(raw.map(String));
  const fromStr = clienteRow?.interesse_temas
    ? expandirTermos(splitListaCampo(clienteRow.interesse_temas))
    : [];
  if (fromStr.length) return fromStr;
  return expandirTermos(['subvencao', 'chamada_publica', 'programa_inovacao', 'credito']);
}

function inferPerfilCliente(row) {
  const p = normalizar(row?.perfil || row?.tipo_perfil || '');
  if (p) return p.replace(/\s+/g, '_');
  const nat = normalizar(row?.natureza_juridica || '');
  if (nat.includes('universidade') || nat.includes('ict')) return 'ict';
  if (nat.includes('prefeit') || nat.includes('municip')) return 'municipio';
  return 'empresa';
}

/** Cliente já normalizado pela app (camelCase/snake tolerant). */
export function toRadarCliente(c) {
  if (!c) return {};
  const porteRaw = normalizar(String(c.porte_empresa || c.porte || ''));
  const porteMap = {
    mei: 'mei',
    micro: 'micro',
    me: 'micro',
    epp: 'pequena',
    pequena: 'pequena',
    media: 'media',
    grande: 'grande',
  };
  let porte = porteMap[porteRaw.replace(/\s+/g, '').toLowerCase()] || porteRaw;
  if (!porte && c.porte_empresa === 'MEI') porte = 'mei';
  if (!porte && c.porte_empresa === 'ME') porte = 'micro';
  if (!porte && c.porte_empresa === 'EPP') porte = 'pequena';
  if (!porte && c.porte_empresa === 'Média') porte = 'media';
  if (!porte && c.porte_empresa === 'Grande') porte = 'grande';

  let mat = normalizar(c.maturidade_projeto || '');
  const nm = normalizar(String(c.nivel_maturidade || '').replace(/\s+/g, ' '));
  if (nm.includes('ideacao') || nm.includes('ideia') || nm.includes('idea')) mat = mat || 'ideia';
  else if (nm.includes('valid')) mat = mat || 'prototipo';
  else if (nm.includes('oper')) mat = mat || 'tracao';
  else if (nm.includes('escala')) mat = mat || 'escala';
  mat = mat || null;

  return {
    id: c.id_cliente ?? c.id,
    nome: c.nome_empresa ?? c.nome,
    descricao: c.descricao_projeto ?? c.descricao ?? '',
    tipo_cliente: c.tipo_cliente,
    setor: c.setor,
    setores_interesse: splitListaCampo(c.setores_interesse),
    area_inovacao: c.area_inovacao,
    areas_interesse: splitListaCampo(c.areas_interesse),
    interesse_temas: splitListaCampo(c.interesse_temas),
    palavras_chave: splitListaCampo(c.palavras_chave),
    perfil: inferPerfilCliente(c),
    porte,
    maturidade_projeto: mat,
    estado: normalizar(c.estado || '').slice(0, 2),
    regiao: normalizar(c.regiao || ''),
    pais: normalizar(c.pais || 'Brasil'),
    valor_interesse_min: Number(c.interesse_valor_min ?? c.valor_interesse_min ?? 0) || 0,
    valor_interesse_max: Number(c.interesse_valor_max ?? c.valor_interesse_max ?? 0) || 0,
    idade_empresa_anos: idadeEmpresaAnos(c.data_abertura),
    regularidade: {
      cnpj_ativo: c.status !== 'Inativo',
      sem_pendencias: !!(c.regular_fiscal && c.regular_trabalhista),
      possui_certidoes: !!c.possui_certidao_negativa,
      pode_contratar_publico: !!c.pode_contratar_publico,
    },
    tipos_interesse: parseTiposInteresseCliente(c),
    _raw: c,
  };
}

/**
 * Formato já agregado (getEditais) ou linha cru do Supabase em EditalDetalhes.
 */
export function toRadarOportunidade(e) {
  if (!e) return {};
  const link =
    e.linkOriginal ||
    e.link_inscricao ||
    e.linkInscricao ||
    e.link ||
    '';
  const prazo = e.prazo_envio ?? e.dataLimite ?? null;
  const uf = normalizar(String(e.uf ?? e.estado ?? '')).slice(0, 2);

  let ativo =
    e.ativo !== undefined
      ? !!e.ativo
      : String(e.status || '').toLowerCase() !== 'inativo';
  const situacao = normalizar(e.situacao || '');
  if (/encerr|finaliz|fechad|concluid|cancelad/.test(situacao)) ativo = false;

  const publico_blob = [
    ...(Array.isArray(e.publico_alvo_arr) ? e.publico_alvo_arr : []),
    typeof e.publico_alvo === 'string' ? e.publico_alvo : '',
    e.perfil_ideal,
  ].filter(Boolean);

  return {
    id: e.id ?? e.id_edital,
    titulo: e.titulo,
    descricao: e.descricao || '',
    fonte_recurso: e.fonte_recurso || e.orgao || '',
    link,
    pdf_url: e.pdf_url ?? e.pdfUrl ?? null,
    prazo_envio: prazo,
    data_publicacao: e.data_publicacao ?? null,
    tipo_oportunidade: e.tipo_oportunidade ?? e.tipoRecurso ?? '',
    tipo_recurso_raw: e.tipo_recurso ?? e.fonte_recurso ?? '',
    perfil_ideal: normalizarArray(e.perfil_ideal),
    publico_alvo: typeof e.publico_alvo === 'string' ? e.publico_alvo : '',
    publico_alvo_arr: normalizarArray(publico_blob),
    area: e.area || '',
    area_cientifica: normalizarArray(e.area_cientifica),
    area_tecnologica: normalizarArray(e.area_tecnologica),
    setor_estrategico: normalizarArray(e.setor_estrategico),
    setor_economico: normalizarArray(e.setor_economico),
    tags: [...normalizarArray(e.tags), ...tokens([e.temas, e.objetivo].filter(Boolean).join(' '))],
    pais: normalizar(e.pais || 'brasil'),
    regiao: normalizar(e.regiao || ''),
    uf,
    cidade: normalizar(e.cidade || ''),
    valor_estimado: Number(e.valor_estimado ?? e.valor ?? e.valor_maximo ?? 0) || 0,
    valor_total: Number(e.valor_total ?? e.valorMaximo ?? e.valor_maximo ?? 0) || 0,
    valor_minimo: Number(e.valor_minimo ?? e.valorMinimo ?? 0) || 0,
    valor_maximo:
      Number(e.valor_maximo ?? e.valorMaximo ?? 0) || Number(e.valor ?? 0) || 0,
    moeda: e.moeda,
    linha_credito: e.linha_credito,
    modalidade_financiamento: e.modalidade_financiamento,
    natureza_recurso: e.natureza_recurso,
    reembolsavel: typeof e.reembolsavel === 'boolean' ? e.reembolsavel : null,
    tipoRecurso: e.tipoRecurso,
    validacao_status: e.validacao_status,
    qualidade_dado: e.qualidade_dado,
    ativo,
    situacao: e.situacao,
    temas: e.temas,
    objetivo: e.objetivo,
    elegibilidade: e.elegibilidade,
    status: e.status,
    extras: {},
  };
}

// ─── Filtro eliminatório ─────────────────────────────────────────────────────

const TITULO_RUIDO = [
  'entre em contato',
  'fale conosco',
  'ouvidoria',
  'faq',
  'quem somos',
  'trabalhe conosco',
  'conta pj',
  'conta digital',
  'internet banking',
  'acesse sua conta',
  'abra sua conta',
];

export function isOportunidadeElegivelParaRadar(oportunidade, options = {}) {
  if (oportunidade.ativo === false && !options.incluirEncerrados) {
    return { ok: false, motivo: 'inativo' };
  }

  if (!oportunidade.titulo || !String(oportunidade.link || '').trim()) {
    return { ok: false, motivo: 'sem_titulo_ou_link' };
  }

  const titulo = normalizar(oportunidade.titulo);
  if (TITULO_RUIDO.some((t) => titulo.includes(t))) {
    return { ok: false, motivo: 'titulo_ruidoso' };
  }

  if (!options.incluirSuspeitos && normalizar(oportunidade.validacao_status) === 'suspeito') {
    return { ok: false, motivo: 'suspeito' };
  }

  const dias = diasAtePrazo(oportunidade.prazo_envio);
  if (!options.incluirEncerrados && dias !== null && dias < 0) {
    return { ok: false, motivo: 'prazo_vencido' };
  }

  return { ok: true };
}

/** Eliminação extra: tipo estranhamente divergente com cliente com preferências fortes */
function tipoFortementeIncompativel(cliente, oportunidade) {
  const interesses = expandirTermos(cliente.tipos_interesse || []);
  if (interesses.length < 2) return false;
  const tiposEdital = inferTiposEditalParaMatch(oportunidade);
  if (!tiposEdital.length) return false;
  const matches = interesses.filter((i) =>
    tiposEdital.some((t) => t === i || t.includes(i) || i.includes(t)),
  );
  return matches.length === 0;
}

// ─── Critérios ───────────────────────────────────────────────────────────────

export function scoreAfinidadeTematica(cliente, oportunidade) {
  const termosCliente = expandirTermos([
    cliente.setor,
    cliente.area_inovacao,
    ...(cliente.setores_interesse || []),
    ...(cliente.areas_interesse || []),
    ...(cliente.interesse_temas || []),
    ...(cliente.palavras_chave || []),
    cliente.descricao,
  ]);

  const textoOportunidade = [
    oportunidade.titulo,
    oportunidade.descricao,
    oportunidade.area,
    oportunidade.temas,
    oportunidade.objetivo,
    ...(oportunidade.area_cientifica || []).map(normalizar),
    ...(oportunidade.area_tecnologica || []).map(normalizar),
    ...(oportunidade.setor_estrategico || []).map(normalizar),
    ...(oportunidade.setor_economico || []).map(normalizar),
    ...(oportunidade.tags || []),
  ].join(' ');

  let termosOportunidade = expandirTermos(tokens(textoOportunidade));

  /* Enriquecer com texto de elegibilidade / público (fonte forte de tema) */
  const extraBlob = normalizar([
    oportunidade.publico_alvo,
    oportunidade.elegibilidade,
    ...(oportunidade.publico_alvo_arr || []),
  ].join(' '));
  termosOportunidade = [...new Set([...termosOportunidade, ...expandirTermos(tokens(extraBlob))])];

  let ausenteCliente = termosCliente.length === 0;
  let ausenteEdital = termosOportunidade.length === 0;

  const sim = jaccard(termosCliente, termosOportunidade);
  let pontos = ausenteCliente || ausenteEdital ? 0 : Math.round(sim * 24);

  const matches = termosCliente.filter((t) =>
    termosOportunidade.some((o) => o === t || o.includes(t) || t.includes(o)),
  );

  const uniq = [...new Set(matches)].slice(0, 16);
  if (!ausenteCliente && !ausenteEdital) {
    if (uniq.length >= 4) pontos = Math.max(pontos, 26);
    else if (uniq.length === 3) pontos = Math.max(pontos, 22);
    else if (uniq.length === 2) pontos = Math.max(pontos, 14);
    else if (uniq.length === 1) pontos = Math.max(pontos, 7);
    if (uniq.length === 0) pontos = Math.min(pontos, 8);
  }

  pontos = Math.min(30, pontos);

  return {
    pontos,
    max: 30,
    matches: uniq.slice(0, 8),
    ausenteCliente,
    ausenteEdital,
    detalhe: 'áreas, setores, temas e texto do edital',
  };
}

export function scorePerfilElegibilidade(cliente, oportunidade) {
  let pontos = 0;
  const motivos = [];

  const perfilCliente = normalizar((cliente.perfil || '').replace(/_/g, ' '));

  /* Porte esperado pelo edital via texto */
  const textoElegivel = normalizar([
    oportunidade.elegibilidade,
    oportunidade.publico_alvo,
    oportunidade.objetivo,
    oportunidade.temas,
    oportunidade.titulo,
  ].join(' '));

  const PORTE_CLI = normalizar(cliente.porte || '');
  const mapaTermosPorte = {
    mei: ['mei', 'microempreendedor', 'empreendedor individual'],
    micro: ['microempresa', 'micro empresa'],
    pequena: ['pequena empresa', 'epp', 'pequeno porte'],
    media: ['media empresa', 'medio porte'],
    grande: ['grande empresa', 'grande porte'],
  };
  const exigePorte = Object.values(mapaTermosPorte).flat().some((t) => textoElegivel.includes(t));

  let porteCompat = false;
  if (PORTE_CLI && textoElegivel) {
    const termosCli = mapaTermosPorte[PORTE_CLI.replace(/\s+/g, '')] || [];
    porteCompat = termosCli.some((t) => textoElegivel.includes(t.replace(/\s+/g, '')) || textoElegivel.includes(normalizar(t)));
  }

  let ausentePerfilEdital =
    !(oportunidade.perfil_ideal || []).length &&
    !(oportunidade.publico_alvo_arr || []).length &&
    !String(oportunidade.publico_alvo || '').trim();

  /* Perfil / público */
  const perfilEdital = [
    ...(oportunidade.perfil_ideal || []),
    ...(oportunidade.publico_alvo_arr || []),
    ...tokens(oportunidade.publico_alvo || ''),
    ...tokens(textoElegivel).slice(0, 80),
  ].map(normalizar).filter(Boolean);

  const equivalencias = {
    startup: ['startup', 'empresa', 'pequena empresa', 'empreendedor', 'deep tech', 'nascente'],
    empresa: ['empresa', 'industria', 'fornecedor', 'pmes', 'pequena empresa', 'media empresa', 'mei'],
    fornecedor: ['fornecedor', 'supplier', 'vendor'],
    pesquisador: ['pesquisador', 'ict', 'universidade', 'instituicao cientifica'],
    universidade: ['universidade', 'ict'],
    ict: ['ict', 'universidade', 'pesquisador', 'instituicao'],
    produtor_rural: ['produtor rural', 'agricultor', 'cooperativa', 'agro'],
    municipio: ['municipio', 'prefeitura', 'governo local'],
    outro: ['empresa', 'instituicao'],
    pesquisa: ['pesquisa', 'p&d', 'pd&i'],
  };

  const aceitosRaw = equivalencias[perfilCliente.replace(/\s+/g, '_')] || equivalencias[perfilCliente] || [perfilCliente];
  const aceitos = aceitosRaw.map(normalizar).filter(Boolean);

  const matchPerfil = perfilEdital.some((p) =>
    aceitos.some((a) => p.includes(a) || a.includes(p)),
  );

  if (ausentePerfilEdital) {
    pontos += 5;
    motivos.push('público-alvo pouco estruturado no edital');
  } else if (matchPerfil) {
    pontos += 15;
    motivos.push('perfil próximo ao público descrito');
  } else {
    pontos -= 12;
    motivos.push('perfil pode não ser o foco do edital');
  }

  if (PORTE_CLI && textoElegivel.includes('mei') && PORTE_CLI === 'mei') {
    pontos += 3;
    motivos.push('menção explícita a MEI');
  } else if (exigePorte && porteCompat) {
    pontos += 3;
    motivos.push('porte citado compatível');
  } else if (exigePorte && !porteCompat) {
    pontos -= 4;
    motivos.push('requisitos de porte possivelmente fora do encaixe');
  }

  /* Idade mínima CNPJ se detectável */
  const m = textoElegivel.match(/minim[oa]?\s*d?e?\s*(\d+)\s*anos?/);
  if (m && cliente.idade_empresa_anos != null) {
    const exMin = Number(m[1]);
    if (cliente.idade_empresa_anos >= exMin) {
      pontos += 2;
      motivos.push(`idade da empresa ≥ ${exMin}a`);
    } else {
      pontos -= 5;
      motivos.push(`edital sugere ≥ ${exMin}a de CNPJ`);
    }
  }

  /* Regularidade (max +5 dentro dos 20) */
  let regPts = 0;
  if (cliente.regularidade?.cnpj_ativo) {
    regPts += 2;
    motivos.push('CNPJ ativo no cadastro');
  }
  if (cliente.regularidade?.sem_pendencias) {
    regPts += 2;
    motivos.push('regularidade fiscal/trabalhista declarada');
  }
  if (cliente.regularidade?.possui_certidoes) {
    regPts += 1;
    motivos.push('certidões negativas');
  }

  pontos += regPts;
  pontos = Math.max(0, Math.min(20, Math.round(pontos)));

  return {
    pontos,
    max: 20,
    motivos,
    ausentePerfilEdital,
  };
}

export function scoreTipo(cliente, oportunidade) {
  const interesses = expandirTermos(cliente.tipos_interesse || []);
  const tiposEdital = inferTiposEditalParaMatch(oportunidade);

  if (!interesses.length)
    return { pontos: 4, max: 15, matches: [], ausenteCliente: true, detalhe: 'sem preferência explícita' };

  if (!tiposEdital.length)
    return { pontos: 5, max: 15, matches: [], ausenteEdital: true, detalhe: 'tipo do edital pouco discriminável' };

  const matches = interesses.filter((i) =>
    tiposEdital.some((t) => t === i || t.includes(i) || i.includes(t)),
  );

  if (!matches.length) {
    return { pontos: 0, max: 15, matches: [], detalhe: 'tipo/recurso fora das preferências' };
  }

  return {
    pontos: Math.min(15, 6 + Math.min(matches.length, 4) * 2),
    max: 15,
    matches: [...new Set(matches)].slice(0, 10),
    detalhe: 'compatibilidade de modalidade/recurso',
  };
}

export function scoreLocalizacao(cliente, oportunidade) {
  const cUF = normalizar(cliente.estado || '').slice(0, 2);
  const eUF = normalizar(oportunidade.uf || '').slice(0, 2);

  const cRegiao = normalizar(cliente.regiao || '');
  const eRegiao = normalizar(oportunidade.regiao || '').replace(/\s+/g, ' ');

  const cPais = normalizar(cliente.pais || 'brasil');
  const ePais = normalizar(oportunidade.pais || 'brasil');

  if (!eUF && !eRegiao && (!oportunidade.pais || ePais === 'brasil')) {
    const nacional =
      /\bnacional(es)?\b|\btodo o pais\b|\bem todo o territorio nacional\b/i.test([
        oportunidade.area,
        oportunidade.descricao,
        oportunidade.elegibilidade,
        String(oportunidade.estado || ''),
      ].join(' '));

    return {
      pontos: nacional ? 6 : 4,
      max: 10,
      motivo: nacional ? 'abrangência aparentemente nacional (texto)' : 'localização indefinida no cadastro da oportunidade',
      indefinido: true,
    };
  }

  if (cUF && eUF && cUF === eUF) {
    return { pontos: 10, max: 10, motivo: 'mesmo estado (UF)', indefinido: false };
  }

  if (cRegiao && eRegiao && (eRegiao.includes(cRegiao) || cRegiao.includes(eRegiao))) {
    return { pontos: 7, max: 10, motivo: 'mesma macro-região', indefinido: false };
  }

  if (eRegiao.includes('nacional') || eRegiao.includes('todo brasil') || ePais === cPais) {
    return { pontos: 6, max: 10, motivo: 'âmbito nacional/brasil', indefinido: false };
  }

  if (eRegiao.includes('internacional') || ePais.includes('internac')) {
    return { pontos: 4, max: 10, motivo: 'oportunidade internacional', indefinido: false };
  }

  if (eUF && cUF && eUF !== cUF) {
    return {
      pontos: 3,
      max: 10,
      motivo: 'UF do edital distinta da empresa',
      indefinido: false,
    };
  }

  return {
    pontos: 4,
    max: 10,
    motivo: 'localização pouco discriminada',
    indefinido: true,
  };
}

export function scorePrazo(oportunidade, options = {}) {
  const dias = diasAtePrazo(oportunidade.prazo_envio);

  if (dias === null) {
    return { pontos: 2, max: 10, motivo: 'prazo não informado', ausente: true };
  }

  /* Com incluirEncerrados, prazos passados aparecem com 0 pontos mas não são excluídos antes */
  if (dias < 0 && !options.incluirEncerrados) {
    /* não deveria chegar aqui se filtro ativo — fallback */
    return { pontos: 0, max: 10, motivo: 'prazo encerrado' };
  }
  if (dias < 0) return { pontos: 1, max: 10, motivo: 'prazo já encerrado (modo inclusão)', expirado: true };

  if (dias <= 7) return { pontos: 4, max: 10, motivo: 'prazo muito próximo', urgente: true };
  if (dias <= 30) return { pontos: 9, max: 10, motivo: 'prazo dentro de ~1 mês' };
  if (dias <= 90) return { pontos: 8, max: 10, motivo: 'prazo confortável' };
  return { pontos: 6, max: 10, motivo: 'prazo longo ou fluxo contínuo' };
}

export function scoreQualidade(oportunidade) {
  let pontos = 0;
  const motivos = [];

  const qRaw = Number(oportunidade.qualidade_dado || 0);
  const q = Number.isFinite(qRaw) ? qRaw : 0;
  const status = normalizar(oportunidade.validacao_status || '');

  if (q >= 90) pontos += 5;
  else if (q >= 75) pontos += 4;
  else if (q >= 60) pontos += 3;
  else if (q >= 40) pontos += 1;
  else if (Number.isFinite(q) && q > 0) pontos += 0;
  /* sem qualidade informada não “premia”: neutro baixo via interpretação textual */

  if (status === 'valido') {
    pontos += 4;
    motivos.push('validação explícita: válido');
  } else if (status === 'incompleto') {
    pontos += 1;
    motivos.push('dados possivelmente incompletos');
  } else if (status === 'acesso_limitado') {
    pontos += 0;
    motivos.push('acesso limitado');
  } else if (status === 'suspeito') {
    pontos -= 6;
    motivos.push('item suspeito (validação)');
  } else if (!status || status === '-') {
    pontos += 1;
    motivos.push('qualidade/indicadores não declarados pela fonte');
  }

  if (oportunidade.pdf_url) {
    pontos += 1;
    motivos.push('documento (PDF) linkado');
  }

  pontos = Math.max(0, Math.min(10, pontos));
  const ausente = !q && !status;

  return { pontos, max: 10, motivos, ausenteQualidadeDeclarada: ausente };
}

export function scoreFaixaValor(cliente, oportunidade) {
  const minCliente = Number(cliente.valor_interesse_min || 0);
  const maxCliente = Number(cliente.valor_interesse_max || 0);

  let valor =
    Number(oportunidade.valor_maximo || 0) ||
    Number(oportunidade.valor_total || 0) ||
    Number(oportunidade.valor_estimado || 0);

  /* Quando há só valor mínimo do edital, usa como âncora */
  if (!valor && Number(oportunidade.valor_minimo) > 0) {
    valor = Number(oportunidade.valor_minimo);
  }

  const semPreferenciaCliente = !minCliente && !maxCliente;
  const semValorEdital = !valor || valor <= 0;

  if (semPreferenciaCliente && semValorEdital) {
    return { pontos: 1, max: 5, motivo: 'valor não comparável (ambos vagos)', ausente: true };
  }

  if (semPreferenciaCliente) {
    return { pontos: 2, max: 5, motivo: 'faixa de interesse não configurada pelo cliente', ausenteCliente: true };
  }

  if (semValorEdital) {
    return { pontos: 1, max: 5, motivo: 'valor da oportunidade não discriminado', ausenteEdital: true };
  }

  if (maxCliente && minCliente === 0 && valor > maxCliente) {
    return { pontos: 1, max: 5, motivo: 'valor acima do teto declarado pelo cliente' };
  }
  if (minCliente && maxCliente === 0 && valor < minCliente) {
    return { pontos: 2, max: 5, motivo: 'valor abaixo do interesse mínimo' };
  }

  const overlapMin = Math.max(minCliente, Number(oportunidade.valor_minimo) || 0);
  const overlapMaxCandidate = Math.min(
    maxCliente > 0 ? maxCliente : Number.POSITIVE_INFINITY,
    valor,
  );

  const ok =
    valor >= minCliente &&
    (!maxCliente || valor <= maxCliente) &&
    (!maxCliente || overlapMaxCandidate >= overlapMin);

  if (ok || (minCliente && maxCliente && valor >= minCliente && valor <= maxCliente)) {
    return { pontos: 5, max: 5, motivo: 'valor alinhado à faixa de interesse' };
  }

  if (minCliente && valor < minCliente)
    return { pontos: 2, max: 5, motivo: 'valor abaixo do interesse declarado' };
  return { pontos: 1, max: 5, motivo: 'valor acima ou fora da faixa' };
}

// ─── Penalidades ─────────────────────────────────────────────────────────────

export function calcularPenalidades(cliente, oportunidade, options = {}) {
  let penalidade = 0;
  const motivos = [];

  const status = normalizar(oportunidade.validacao_status);
  const titulo = normalizar(oportunidade.titulo || '');

  if (status === 'suspeito') {
    penalidade -= 18;
    motivos.push('validação marcada como suspeita');
  }

  if (oportunidade.ativo === false) {
    penalidade -= 55;
    motivos.push('oportunidade inativa/encerrada');
  }

  const dias = diasAtePrazo(oportunidade.prazo_envio);
  if (dias !== null && dias < 0 && options.incluirEncerrados) {
    penalidade -= 25;
    motivos.push('prazo já vencido (inclusão opcional)');
  }

  const setores = [...(oportunidade.setor_estrategico || []), ...(oportunidade.area_tecnologica || [])];
  const setNorm = [...new Set(setores.map(normalizar))].filter(Boolean);
  if (setNorm.length > 6) {
    penalidade -= 4;
    motivos.push('muitos eixos setoriais diferentes (lista ampla)');
  }

  if (tipoFortementeIncompativel(cliente, oportunidade)) {
    penalidade -= 12;
    motivos.push('tipo de recurso discrepa das preferências do cliente');
  }

  if (
    cliente._raw?.tem_projeto_inovacao &&
    !normalizar([oportunidade.objetivo, oportunidade.elegibilidade, oportunidade.temas].join(' ')).includes('inova')
    && !titulo.includes('ino')
    && tokens(oportunidade.descricao || '').includes('social')
    /* apenas micro-penalty se projeto inova marcado mas edital só “social genérico” */
  ) {
    /* noop — pode evoluír com mais sinais */
  }

  if (['entre em contato', 'faq', 'conta pj', 'internet banking'].some((t) => titulo.includes(t))) {
    penalidade -= 85;
    motivos.push('título sugere página institucional, não edital');
  }

  return { penalidade, motivos };
}

// ─── Explicações ─────────────────────────────────────────────────────────────

export function gerarExplicacoes(criterios, penalidades, oportunidade) {
  const out = [];

  if ((criterios.afinidade?.matches || []).length) {
    out.push(`Afinidade: ${criterios.afinidade.matches.slice(0, 4).join(', ')}`);
  }

  if (criterios.perfil?.pontos >= 12) {
    out.push(...(criterios.perfil.motivos || []).slice(0, 2));
  }

  if (criterios.tipo?.matches?.length) {
    out.push(`Modalidade/recurso: ${criterios.tipo.matches.slice(0, 4).join(', ')}`);
  }

  if (criterios.localizacao?.motivo && criterios.localizacao.pontos >= 5) {
    out.push(`${criterios.localizacao.motivo}`);
  }

  if (criterios.prazo?.motivo && criterios.prazo.pontos <= 3) {
    out.push(`${criterios.prazo.motivo}`);
  } else if (criterios.prazo?.motivo) {
    out.push(`Prazo: ${criterios.prazo.motivo}`);
  }

  if (criterios.valor?.motivo) {
    out.push(`${criterios.valor.motivo}`);
  }

  if (penalidades.motivos.length) {
    penalidades.motivos.slice(0, 4).forEach((m) => out.push(`Atenção — ${m}`));
  }

  return [...new Set(out)].slice(0, 8);
}

// ─── Principal ───────────────────────────────────────────────────────────────

export function compatRotulo(score) {
  if (score >= 85) return 'alta';
  if (score >= 62) return 'media';
  if (score >= 38) return 'baixa';
  return 'fraca';
}

export function mapCompatToUiLabel(label) {
  if (label === 'alta') return 'Alta';
  if (label === 'media') return 'Média';
  if (label === 'baixa' || label === 'fraca') return 'Baixa';
  return 'Baixa';
}

export function calcularMatchRadar(cliente, oportunidade, options = {}) {
  const eleg = {
    ...isOportunidadeElegivelParaRadar(oportunidade, options),
  };

  if (!eleg.ok) {
    return {
      score: 0,
      percentual: 0,
      compatibilidade: 'incompatível',
      compatUILabel: 'Baixa',
      excluido: true,
      motivo_exclusao: eleg.motivo,
      criterios: {},
      explicacoes: [],
      penalidades: { penalidade: 0, motivos: [] },
      brutoAntesPenalidades: 0,
    };
  }

  const criterios = {
    afinidade: scoreAfinidadeTematica(cliente, oportunidade),
    perfil: scorePerfilElegibilidade(cliente, oportunidade),
    tipo: scoreTipo(cliente, oportunidade),
    localizacao: scoreLocalizacao(cliente, oportunidade),
    prazo: scorePrazo(oportunidade, options),
    qualidade: scoreQualidade(oportunidade),
    valor: scoreFaixaValor(cliente, oportunidade),
  };

  const bruto = Object.values(criterios).reduce((s, c) => s + (Number(c?.pontos) || 0), 0);
  const pen = calcularPenalidades(cliente, oportunidade, options);
  let ajustado = Math.round(Math.max(0, Math.min(100, bruto + pen.penalidade)));

  const compat = compatRotulo(ajustado);

  let explicacoes = gerarExplicacoes(criterios, pen, oportunidade);

  return {
    score: ajustado,
    percentual: ajustado,
    compatibilidade: compat,
    compatUILabel: mapCompatToUiLabel(compat),
    excluido: false,
    motivo_exclusao: null,
    criterios,
    penalidades: pen,
    explicacoes,
    brutoAntesPenalidades: bruto,
  };
}

/** Reordena priorizando diversidade por fonte e tipo sem perder ordenação por score dentro dos blocos. */
export function diversificarResultados(resultados) {
  const sorted = [...resultados].sort((a, b) => (b._radarPct || b.radar_score) - (a._radarPct || a.radar_score));
  const final = [];
  const porFonte = {};
  const porTipo = {};
  const deferred = [];

  const fonteOf = (x) => normalizar(String(x.fonte_recurso || x.edital?.orgao || '—'));
  const tipoOf = (x) =>
    normalizar(String(x.oportunidade?.tipo_oportunidade || x.edital?.tipoRecurso || '—'));

  for (const item of sorted) {
    const f = fonteOf(item);
    const t = tipoOf(item);
    porFonte[f] ??= 0;
    porTipo[t] ??= 0;

    if (porFonte[f] < 3 && porTipo[t] < 5) {
      final.push(item);
      porFonte[f]++;
      porTipo[t]++;
    } else {
      deferred.push(item);
    }
  }
  /* recupera ordenados por score o que ficou pendente das cotas */
  deferred.sort((a, b) => (b._radarPct || b.radar_score) - (a._radarPct || a.radar_score));
  return [...final, ...deferred];
}

/**
 * Pré-filtro barato (sem score): mesma política que `calcularMatchRadar` elimina antes de pontuar.
 */
export function filtrarEditaisPreScoreRadar(editais, options = {}) {
  const list = Array.isArray(editais) ? editais : [];
  const passed = [];
  for (const e of list) {
    const op = toRadarOportunidade(e);
    if (isOportunidadeElegivelParaRadar(op, options).ok) passed.push(e);
  }
  return {
    passed,
    totalIn: list.length,
    excludedPreScore: Math.max(0, list.length - passed.length),
  };
}

/** Uma linha avaliada (mesmo shape usado pelo ranking final). */
export function avaliarEditalRadarLinha(radarCliente, edital, options, scoreMinimoExibir) {
  const oportunidade = toRadarOportunidade(edital);
  const match = calcularMatchRadar(radarCliente, oportunidade, options);

  if (!match.excluido && match.percentual < scoreMinimoExibir) {
    match.excluido = true;
    match.motivo_exclusao = 'abaixo_do_corte_basico';
  }

  return {
    edital,
    oportunidade,
    radar_match: match,
    radar_score: match.percentual,
    radar_excluido: match.excluido,
    radar_motivo_exclusao: match.motivo_exclusao,
    _radarPct: match.percentual,
    fonte_recurso: oportunidade.fonte_recurso,
  };
}

/** Cortes / diversificação / limite após lista completa de avaliações (permite calcular em lotes). */
export function finalizarRankingOportunidadesRadar(avaliadas, options = {}) {
  const cortePrincipal = options.cortePrincipal ?? 52;
  const corteFallback = options.corteFallback ?? 32;
  const limite = options.limite ?? 80;

  const pass = avaliadas.filter((x) => !x.radar_excluido).sort((a, b) => b.radar_score - a.radar_score);

  let candidatos = pass.filter((x) => x.radar_score >= cortePrincipal);
  if (candidatos.length < 5) {
    candidatos = pass.filter((x) => x.radar_score >= corteFallback);
  }
  if (candidatos.length === 0) {
    candidatos = pass;
  }

  const diversified = diversificarResultados(candidatos);

  const seen = new Set();
  const ordered = [];
  for (const it of diversified) {
    const id = it.edital?.id ?? it.oportunidade?.id;
    if (seen.has(id)) continue;
    seen.add(id);
    ordered.push(it);
    if (ordered.length >= limite) break;
  }

  if (ordered.length < limite) {
    for (const it of pass) {
      const id = it.edital?.id;
      if (seen.has(id)) continue;
      seen.add(id);
      ordered.push(it);
      if (ordered.length >= limite) break;
    }
  }

  return ordered.slice(0, limite);
}

/**
 * Lista final para o Radar: cortes dinâmicos + diversificação.
 */
export function recomendarOportunidadesRadar(cliente, editais, options = {}) {
  const radarCliente = toRadarCliente(cliente);
  const scoreMin = options.scoreMinimoExibir ?? (options.incluirAproximados ? 15 : 24);

  const avaliadas = editais.map((edital) => avaliarEditalRadarLinha(radarCliente, edital, options, scoreMin));

  return finalizarRankingOportunidadesRadar(avaliadas, options);
}

// ─── Payload legado para cards / EditalDetalhes ─────────────────────────────---

export function prazoParaCard(match, editalFmt) {
  const dias =
    diasAtePrazo(editalFmt.dataLimite || editalFmt.prazo_envio) ??
    diasAtePrazo(match?.oportunidade?.prazo_envio);
  const expirado = dias != null && dias < 0;
  let rotulo = null;
  if (expirado) rotulo = 'expirado';
  else if (dias != null && dias < 7) rotulo = 'curto';
  else if (dias != null && dias <= 30) rotulo = 'medio';
  else rotulo = 'longo';

  return { dias, rotulo, expirado };
}

/** Converte `hit` já calculado para o objeto enriquecido dos cards / detalhes. */
export function radarMatchToCardPayload(editalFmt, hit) {
  if (!hit || hit.excluido) {
    return {
      excluido: true,
      motivo_exclusao: hit?.motivo_exclusao,
      radar_raw: hit,
      score: 0,
      compatibilidade: 'Baixa',
    };
  }

  const { criterios } = hit;

  const detalhes = {
    afinidade: criterios.afinidade.pontos,
    perfil: criterios.perfil.pontos,
    tipo: criterios.tipo.pontos,
    localizacao: criterios.localizacao.pontos,
    prazo: criterios.prazo.pontos,
    qualidade: criterios.qualidade.pontos,
    valor: criterios.valor.pontos,
  };

  const criterioMeta = {
    afinidade: {
      ausente: !!(criterios.afinidade.ausenteCliente || criterios.afinidade.ausenteEdital),
    },
    perfil: { ausente: !!criterios.perfil.ausentePerfilEdital },
    tipo: { ausente: !!(criterios.tipo.ausenteCliente || criterios.tipo.ausenteEdital) },
    localizacao: { ausente: !!criterios.localizacao.indefinido },
    prazo: { ausente: !!criterios.prazo.ausente },
    qualidade: { ausente: !!criterios.qualidade.ausenteQualidadeDeclarada },
    valor: { ausente: !!(criterios.valor.ausente || criterios.valor.ausenteCliente || criterios.valor.ausenteEdital) },
  };

  const explicTail = (hit.explicacoes || []).slice(0, 5).join(' · ');
  const matchLinha = `Match de ${hit.percentual}% pelo cadastro.${explicTail ? ` ${explicTail}` : ''}`;

  const prazoInfoCard = prazoParaCard(hit, editalFmt);

  return {
    score: hit.percentual,
    compatibilidade: hit.compatUILabel,
    compatKey: hit.compatibilidade,
    razoes: hit.explicacoes,
    detalhes,
    criterioMeta,
    matchLinha,
    fonteMatch: 'radar_v2',
    prazoInfo: {
      dias: prazoInfoCard.dias,
      rotulo: prazoInfoCard.rotulo === 'expirado' ? 'expirado' : prazoInfoCard.rotulo,
      expirado: prazoInfoCard.expirado,
    },
    expirado: prazoInfoCard.expirado,
    radar_penalidades: Array.isArray(hit.penalidades?.motivos) ? hit.penalidades.motivos : [],
    radar_badges: extrairBadges(hit, prazoInfoCard),
    radar_raw: hit,
    excluido: false,
  };
}

/** Converte resultado novo → shape esperado por CardEditalRadar legado */
export function toLegacyRadarPayload(clienteRow, editalFmt, radarOptions = {}) {
  const cliente = toRadarCliente(clienteRow);
  const op = toRadarOportunidade(editalFmt);
  const hit = calcularMatchRadar(cliente, op, {
    incluirSuspeitos: radarOptions.incluirSuspeitos ?? false,
    incluirEncerrados: radarOptions.incluirEncerrados ?? false,
    incluirAproximados: radarOptions.incluirAproximados ?? false,
    scoreMinimoExibir: radarOptions.scoreMinimoExibir ?? 22,
    ...radarOptions,
  });
  if (hit.excluido) {
    return { excluido: true, motivo_exclusao: hit.motivo_exclusao, radar_raw: hit };
  }
  return radarMatchToCardPayload(editalFmt, hit);
}

function extrairBadges(hit, prazoInfoCard) {
  const b = [];
  const penMotivos = hit.penalidades?.motivos;
  const penArr = Array.isArray(penMotivos) ? penMotivos : [];
  if (penArr.some((m) => String(m).includes('suspe'))) b.push({ key: 'suspeito', label: 'Item suspeito' });
  if (penArr.some((m) => String(m).includes('ampl'))) b.push({ key: 'amplo', label: 'Classificação ampla' });
  if (
    penArr.some((m) => String(m).includes('incomplet')) ||
    (hit.criterios?.qualidade?.motivos || []).some((x) => String(x).includes('incomplet'))
  ) {
    b.push({ key: 'incompleto', label: 'Dados incompletos' });
  }
  if ((hit.criterios?.qualidade?.motivos || []).some((x) => String(x).includes('acesso')))
    b.push({ key: 'acesso_limitado', label: 'Acesso limitado' });
  if (prazoInfoCard.rotulo === 'curto') b.push({ key: 'prazo_curto', label: 'Prazo próximo' });
  if (prazoInfoCard.expirado && hit.excluido === false && prazoInfoCard.dias < 0)
    b.push({ key: 'encerrado', label: 'Prazo encerrado' });

  /* qualidade declarada zerada pela fonte */
  if (
    Number(hit.criterios?.qualidade?.pontos) <= 2 &&
    hit.criterios?.qualidade?.ausenteQualidadeDeclarada
  ) {
    b.push({ key: 'sem_qualidade_declarada', label: 'Fonte sem métricas de qualidade' });
  }
  return b;
}

// ─── Debug (dev) ─────────────────────────────────────────────────────────────

export function debugRadarCliente(cliente, editais, options = {}) {
  const clienteR = toRadarCliente(cliente);
  const todas = editais.map((e) => {
    const op = toRadarOportunidade(e);
    const m = calcularMatchRadar(clienteR, op, options);
    return { titulo: e.titulo, fonte: e.orgao ?? e.fonte_recurso, match: m };
  });

  const excluidas = todas.filter((x) => x.match.excluido);
  const porMotivo = {};
  excluidas.forEach((x) => {
    const k = x.match.motivo_exclusao || '?';
    porMotivo[k] = (porMotivo[k] || 0) + 1;
  });

  const scores = todas.filter((x) => !x.match.excluido).map((x) => x.match.percentual);

  const fontesTop = [...new Map(editais.map((e) => [e.orgao ?? e.fonte_recurso, 0])).keys()].slice(
    0,
    8,
  );

  const out = {
    cliente_id: clienteR.id,
    avaliadas: todas.length,
    excluidas: excluidas.length,
    motivos_exclusao: porMotivo,
    score_min: scores.length ? Math.min(...scores) : null,
    score_max: scores.length ? Math.max(...scores) : null,
    amostras: todas
      .filter((x) => !x.match.excluido)
      .sort((a, b) => b.match.percentual - a.match.percentual)
      .slice(0, 12)
      .map((x) => ({
        titulo: String(x.titulo || '').slice(0, 72),
        fonte: x.fonte,
        score: x.match.percentual,
        compat: x.match.compatUILabel,
      })),
    fontesDistinct: fontesTop,
  };

  if (typeof console !== 'undefined' && typeof console.table === 'function') {
    console.table(
      out.amostras.map((x) => ({
        titulo: x.titulo.substring(0, 48),
        fonte: x.fonte,
        score: x.score,
        compat: x.compat,
      })),
    );
  }
  return out;
}
