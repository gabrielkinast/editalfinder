/**
 * Payload mínimo para postMessage do Worker (evita structured clone gigante).
 * Campos alinhados a `toRadarOportunidade` / `toRadarCliente` em radarMatch.js.
 */

const MAX_TEXT = 2400;

function trimText(value, max = MAX_TEXT) {
  if (value == null) return '';
  const s = typeof value === 'string' ? value : String(value);
  return s.length <= max ? s : `${s.slice(0, max)}…`;
}

function pickArray(v) {
  if (Array.isArray(v)) return v.slice(0, 48);
  return v;
}

/** Um edital — só campos usados no score/pré-filtro/card. */
export function compactRadarWorkerEdital(e) {
  if (!e || typeof e !== 'object') return {};
  return {
    id: e.id ?? e.id_edital,
    titulo: e.titulo,
    descricao: trimText(e.descricao || e.resumo || ''),
    orgao: e.orgao,
    fonte_recurso: e.fonte_recurso,
    tipo_recurso: e.tipo_recurso,
    tipoRecurso: e.tipoRecurso,
    tipo_oportunidade: e.tipo_oportunidade,
    link: e.link ?? e.linkOriginal ?? e.link_inscricao ?? e.linkInscricao,
    linkOriginal: e.linkOriginal,
    link_inscricao: e.link_inscricao,
    linkInscricao: e.linkInscricao,
    prazo_envio: e.prazo_envio,
    dataLimite: e.dataLimite,
    data_publicacao: e.data_publicacao,
    uf: e.uf,
    estado: e.estado,
    regiao: e.regiao,
    cidade: e.cidade,
    pais: e.pais,
    area: e.area,
    area_cientifica: pickArray(e.area_cientifica),
    area_tecnologica: pickArray(e.area_tecnologica),
    setor_estrategico: pickArray(e.setor_estrategico),
    setor_economico: pickArray(e.setor_economico),
    tags: pickArray(e.tags),
    temas: trimText(e.temas, 800),
    objetivo: trimText(e.objetivo, 800),
    elegibilidade: trimText(e.elegibilidade, 1200),
    perfil_ideal: e.perfil_ideal,
    publico_alvo: trimText(e.publico_alvo, 600),
    publico_alvo_arr: pickArray(e.publico_alvo_arr),
    valor: e.valor,
    valor_estimado: e.valor_estimado,
    valor_total: e.valor_total,
    valor_minimo: e.valor_minimo,
    valor_maximo: e.valor_maximo,
    valorMinimo: e.valorMinimo,
    valorMaximo: e.valorMaximo,
    moeda: e.moeda,
    linha_credito: e.linha_credito,
    modalidade_financiamento: e.modalidade_financiamento,
    natureza_recurso: e.natureza_recurso,
    reembolsavel: e.reembolsavel,
    validacao_status: e.validacao_status,
    qualidade_dado: e.qualidade_dado,
    ativo: e.ativo,
    situacao: e.situacao,
    status: e.status,
    pdf_url: e.pdf_url ?? e.pdfUrl,
  };
}

/** Cliente — campos de `toRadarCliente` sem `_raw` nem blobs Supabase. */
export function compactRadarWorkerCliente(c) {
  if (!c || typeof c !== 'object') return {};
  return {
    id_cliente: c.id_cliente,
    id: c.id,
    nome_empresa: c.nome_empresa,
    nome: c.nome,
    descricao_projeto: trimText(c.descricao_projeto ?? c.descricao ?? ''),
    descricao: trimText(c.descricao ?? ''),
    tipo_cliente: c.tipo_cliente,
    setor: c.setor,
    setores_interesse: c.setores_interesse,
    area_inovacao: c.area_inovacao,
    areas_interesse: c.areas_interesse,
    interesse_temas: c.interesse_temas,
    palavras_chave: c.palavras_chave,
    perfil: c.perfil,
    tipo_perfil: c.tipo_perfil,
    natureza_juridica: c.natureza_juridica,
    porte_empresa: c.porte_empresa,
    porte: c.porte,
    maturidade_projeto: c.maturidade_projeto,
    nivel_maturidade: c.nivel_maturidade,
    estado: c.estado,
    regiao: c.regiao,
    pais: c.pais,
    interesse_valor_min: c.interesse_valor_min,
    interesse_valor_max: c.interesse_valor_max,
    valor_interesse_min: c.valor_interesse_min,
    valor_interesse_max: c.valor_interesse_max,
    data_abertura: c.data_abertura,
    status: c.status,
    regular_fiscal: c.regular_fiscal,
    regular_trabalhista: c.regular_trabalhista,
    possui_certidao_negativa: c.possui_certidao_negativa,
    pode_contratar_publico: c.pode_contratar_publico,
    tipos_interesse: c.tipos_interesse,
    cnae_principal: c.cnae_principal,
  };
}

export function compactRadarWorkerPayload(cliente, editais) {
  const list = Array.isArray(editais) ? editais : [];
  const compactEditais = new Array(list.length);
  for (let i = 0; i < list.length; i++) {
    compactEditais[i] = compactRadarWorkerEdital(list[i]);
  }
  return {
    cliente: compactRadarWorkerCliente(cliente),
    editais: compactEditais,
    inputCount: list.length,
    compactCount: compactEditais.length,
  };
}

/** Estimativa de bytes do JSON (DEV). */
export function estimateRadarPayloadBytes(obj) {
  try {
    return new Blob([JSON.stringify(obj)]).size;
  } catch {
    return 0;
  }
}
