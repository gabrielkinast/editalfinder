import {
  recomendarOportunidadesRadar,
  radarMatchToCardPayload,
  toLegacyRadarPayload,
  scoreAfinidadeTematica,
  toRadarCliente,
  toRadarOportunidade,
  debugRadarCliente,
  diasAtePrazo,
} from '../utils/radarMatch';
import {
  runRadarMatchAsync,
  ordenarLinhasRadarUi,
  DEFAULT_RADAR_ASYNC_CHUNK,
  RADAR_FIRST_BATCH_MIN_PROCESSED,
  RADAR_FIRST_BATCH_TOP_N,
} from '../utils/radar/radarMatchCore';

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
  const cr = toRadarCliente(cliente);
  const tipos = new Set();
  for (const e of editais) {
    const aff = scoreAfinidadeTematica(cr, toRadarOportunidade(e));
    if (aff.pontos < 4 && editalTemSobreposicaoAreaComCliente(cliente, e) === false) continue;
    if (aff.pontos < 2) continue;
    const t = (e.tipoRecurso || '').trim();
    if (t) tipos.add(t);
  }
  return [...tipos].sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

/** Pesos máximos do novo índice (100 pts via motor em radarMatch.js). */
export const CRITERIOS = [
  { key: 'afinidade', label: 'Afinidade temática', max: 30 },
  { key: 'perfil', label: 'Perfil e elegibilidade', max: 20 },
  { key: 'tipo', label: 'Tipo de recurso', max: 15 },
  { key: 'localizacao', label: 'Localização', max: 10 },
  { key: 'prazo', label: 'Prazo e situação', max: 10 },
  { key: 'qualidade', label: 'Qualidade e confiança', max: 10 },
  { key: 'valor', label: 'Faixa de valor', max: 5 },
];

/** Retorno “zerado” com chaves esperadas pela UI quando o par não pode ser avaliado. */
function radarDetalhesZerados() {
  const o = {};
  CRITERIOS.forEach((c) => { o[c.key] = 0; });
  return o;
}

/**
 * Índice de compatibilidade (cliente × edital).
 * Delega ao motor estruturado em `radarMatch.js`.
 */
export function calcularScore(cliente, edital) {
  const p = toLegacyRadarPayload(cliente, edital, {
    incluirSuspeitos: true,
    incluirEncerrados: true,
    incluirAproximados: true,
    scoreMinimoExibir: 0,
  });
  if (p.excluido) {
    return {
      score: 0,
      compatibilidade: 'Baixa',
      razoes: ['Cadastro incompleto ou dados do edital insuficientes (ex.: falta link)'],
      detalhes: radarDetalhesZerados(),
      criterioMeta: {},
      prazoInfo: { dias: null, rotulo: null, expirado: false },
      expirado: false,
    };
  }
  return {
    score: p.score,
    compatibilidade: p.compatibilidade,
    razoes: p.razoes,
    detalhes: p.detalhes,
    criterioMeta: p.criterioMeta,
    prazoInfo: p.prazoInfo,
    expirado: p.expirado,
  };
}

/**
 * Radar (UI): mesma política da análise em etapas (`radarMatch.js`). Sem mistura artificial com JSON de perfil.
 */
export function resolverRadarMatch(cliente, edital, options = {}) {
  const p = toLegacyRadarPayload(cliente, edital, {
    incluirSuspeitos: options.incluirSuspeitos ?? false,
    incluirEncerrados: options.incluirEncerrados ?? false,
    incluirAproximados: options.incluirAproximados ?? false,
    scoreMinimoExibir: options.scoreMinimoExibir ?? 22,
    ...options,
  });
  if (p.excluido) {
    return {
      score: 0,
      compatibilidade: 'Baixa',
      razoes: [],
      detalhes: radarDetalhesZerados(),
      prazoInfo: { dias: null, rotulo: null, expirado: false },
      expirado: false,
      matchLinha: 'Oportunidade excluída pelos filtros do radar ou dados insuficientes.',
      perfilMatch: null,
      fonteMatch: 'radar_v2',
    };
  }
  return {
    score: p.score,
    compatibilidade: p.compatibilidade,
    razoes: p.razoes,
    detalhes: p.detalhes,
    criterioMeta: p.criterioMeta,
    prazoInfo: p.prazoInfo,
    expirado: p.expirado,
    matchLinha: p.matchLinha,
    radar_badges: p.radar_badges,
    radar_penalidades: p.radar_penalidades,
    perfilMatch: null,
    fonteMatch: 'radar_v2',
  };
}

export {
  DEFAULT_RADAR_ASYNC_CHUNK,
  RADAR_FIRST_BATCH_MIN_PROCESSED,
  RADAR_FIRST_BATCH_TOP_N,
};

/** Chave superficial para memoizar radar (lista enorme igual + mesmas flags). */
export function buildRadarCacheKey(clienteRow, totalEditais, headId, tailId, options) {
  const cid = String(clienteRow?.id_cliente ?? clienteRow?.id ?? '');
  return [
    cid,
    totalEditais,
    headId ?? '',
    tailId ?? '',
    options.incluirSuspeitos ? 'S' : 's',
    options.incluirEncerrados ? 'E' : 'e',
    options.incluirAproximados ? 'A' : 'a',
    options.cortePrincipal ?? '',
    options.corteFallback ?? '',
    options.scoreMinimoExibir ?? '',
  ].join('|');
}

export { ordenarLinhasRadarUi };

/**
 * Radar em lotes (main thread). Mesmo núcleo que o Web Worker (`radarMatchCore`).
 * `onPartialResults` emite até top 20 após o primeiro chunk (Fase 0.5).
 */
export async function recomendarEditaisAsync(cliente, editais, options = {}, asyncOpts = {}) {
  return runRadarMatchAsync(cliente, editais, options, {
    chunkSize: asyncOpts.chunkSize ?? DEFAULT_RADAR_ASYNC_CHUNK,
    signal: asyncOpts.signal,
    onProgress: asyncOpts.onProgress,
    onPartialResults: asyncOpts.onPartialResults,
    firstBatchMinProcessed: asyncOpts.firstBatchMinProcessed,
    firstBatchTopN: asyncOpts.firstBatchTopN,
    yieldBetweenChunks: true,
  });
}

/**
 * Lista de editais com score e metadados — diversificação e cortes no motor.
 */
export function recomendarEditais(cliente, editais, options = {}) {
  const eds = Array.isArray(editais) ? editais : [];

  const merged = {
    incluirSuspeitos: options.incluirSuspeitos ?? false,
    incluirEncerrados: options.incluirEncerrados ?? false,
    incluirAproximados: options.incluirAproximados ?? false,
    cortePrincipal: options.cortePrincipal ?? 52,
    corteFallback: options.corteFallback ?? 30,
    limite: options.limite ?? 3000,
    scoreMinimoExibir: options.scoreMinimoExibir ??
      (options.incluirAproximados ? 12 : 24),
    ...options,
  };

  try {
    const linhas = recomendarOportunidadesRadar(cliente, eds, merged);

    const now = Date.now();
    const enriquecidas = linhas
      .map((row) => {
        if (!row?.edital || !row?.radar_match) return null;
        const p = radarMatchToCardPayload(row.edital, row.radar_match);
        if (p.excluido) return null;
        return { edital: row.edital, ...p };
      })
      .filter(Boolean);

    return enriquecidas.sort((a, b) => {
      const expA = a.expirado ? 1 : 0;
      const expB = b.expirado ? 1 : 0;
      if (expA !== expB) return expA - expB;
      if (b.score !== a.score) return b.score - a.score;
      const diaA = diasAtePrazo(a.edital.dataLimite);
      const diaB = diasAtePrazo(b.edital.dataLimite);
      const tA = new Date(a.edital.dataLimite || 0).getTime();
      const tB = new Date(b.edital.dataLimite || 0).getTime();
      const vA = diaA != null && diaA >= 0 ? tA - now : Number.POSITIVE_INFINITY;
      const vB = diaB != null && diaB >= 0 ? tB - now : Number.POSITIVE_INFINITY;
      return vA - vB;
    });
  } catch (e) {
    console.error('[matchService] recomendarEditais:', e);
    return [];
  }
}

/** Debug do radar (principalmente modo desenvolvimento). */
export function debugRadar({ cliente, editais, options }) {
  return debugRadarCliente(cliente, editais, options || {});
}
