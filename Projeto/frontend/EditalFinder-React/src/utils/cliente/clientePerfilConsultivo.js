/**
 * Perfil consultivo do cliente — armazenamento em colunas existentes + extras.perfil_consultivo.
 * Compatível com registros antigos (fallback seguro).
 */

export const PERFIL_CONSULTIVO_KEY = 'perfil_consultivo';

export const TIPOS_RECURSO_FOMENTO = [
  { id: 'subvencao', label: 'Subvenção' },
  { id: 'credito', label: 'Crédito' },
  { id: 'bolsa', label: 'Bolsa' },
  { id: 'cooperacao_internacional', label: 'Cooperação internacional' },
  { id: 'licitacao', label: 'Licitação' },
  { id: 'investimento', label: 'Investimento' },
];

export function emptyPerfilConsultivo() {
  return {
    contato: {
      nome: '',
      cargo: '',
      email: '',
      telefone: '',
      cpf: '',
      observacoes: '',
    },
    localizacao: {
      pais: 'Brasil',
      unidade_execucao: '',
      data_inicio_operacao: '',
    },
    dados_economicos: {
      ebitda: '',
      grupo_economico: '',
      faixa_faturamento: '',
      contrapartida_capacidade: '',
    },
    perfil_tecnologico: {
      principais_atividades: '',
      areas_tecnologicas: '',
      descricao_projeto: '',
      temas_prioritarios: '',
      setores_estrategicos: '',
      maturidade_tecnologica: '',
      experiencia_pd: '',
      parcerias_ict: '',
      portfolio_produtos: '',
    },
    preferencias_fomento: {
      tipos_recurso: [],
      faixa_valor_interesse: '',
      criterios_aceite: [],
      aceita_internacional: null,
      aceita_licitacao: null,
      aceita_sem_prazo: null,
      prazo_minimo_confortavel_dias: '',
      fontes_preferidas: '',
      fontes_evitar: '',
    },
    documentacao: {
      contrato_social: null,
      certidoes_fiscais: null,
      regularidade_trabalhista: null,
      balanco_dre: null,
      representante_legal: null,
      documentos_tecnicos: null,
      documentos_disponiveis: [],
      observacoes: '',
    },
    diagnostico_consultor: {
      contexto_cliente: '',
      diagnostico_inicial: '',
      pontos_fortes: '',
      lacunas: '',
      riscos: '',
      proximas_acoes: '',
      observacoes_internas: '',
    },
  };
}

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function parseExtras(raw) {
  if (!raw) return {};
  if (typeof raw === 'object' && !Array.isArray(raw)) return raw;
  if (typeof raw === 'string') {
    try {
      const j = JSON.parse(raw);
      return j && typeof j === 'object' ? j : {};
    } catch {
      return {};
    }
  }
  return {};
}

function deepMerge(target, source) {
  const out = { ...target };
  for (const key of Object.keys(source || {})) {
    const sv = source[key];
    if (sv && typeof sv === 'object' && !Array.isArray(sv)) {
      out[key] = deepMerge(out[key] || {}, sv);
    } else if (sv !== undefined) {
      out[key] = sv;
    }
  }
  return out;
}

/**
 * Extrai perfil_consultivo de extras com defaults.
 */
export function parsePerfilConsultivoFromExtras(extras) {
  const ex = parseExtras(extras);
  const raw = ex[PERFIL_CONSULTIVO_KEY];
  const base = emptyPerfilConsultivo();
  if (!raw || typeof raw !== 'object') return base;
  return deepMerge(base, raw);
}

/**
 * Mescla colunas legadas do cliente no perfil (retrocompat).
 */
export function hydratePerfilFromClienteRow(cliente) {
  const c = cliente || {};
  const perfil = parsePerfilConsultivoFromExtras(c.extras);

  if (!hasText(perfil.contato.nome) && hasText(c.nome_contato)) {
    perfil.contato.nome = String(c.nome_contato);
  }
  if (!hasText(perfil.contato.email) && hasText(c.email)) perfil.contato.email = String(c.email);
  if (!hasText(perfil.contato.telefone) && hasText(c.telefone)) {
    perfil.contato.telefone = String(c.telefone);
  }
  if (!hasText(perfil.localizacao.data_inicio_operacao) && hasText(c.data_inicio_operacao)) {
    perfil.localizacao.data_inicio_operacao = String(c.data_inicio_operacao);
  }
  if (!hasText(perfil.perfil_tecnologico.principais_atividades) && hasText(c.descricao_projeto)) {
    perfil.perfil_tecnologico.principais_atividades = String(c.descricao_projeto);
  }
  if (!hasText(perfil.perfil_tecnologico.areas_tecnologicas) && hasText(c.area_inovacao)) {
    perfil.perfil_tecnologico.areas_tecnologicas = String(c.area_inovacao);
  }
  if (!hasText(perfil.dados_economicos.grupo_economico) && hasText(c.grupo_economico)) {
    perfil.dados_economicos.grupo_economico = String(c.grupo_economico);
  }
  if (!hasText(perfil.dados_economicos.ebitda) && hasText(c.ebitda)) {
    perfil.dados_economicos.ebitda = String(c.ebitda);
  }

  return perfil;
}

/**
 * Estado unificado do formulário (colunas + perfil).
 */
export function clientFormStateFromCliente(cliente) {
  const c = cliente || {};
  const perfil = hydratePerfilFromClienteRow(c);

  return {
    nome_empresa: c.nome_empresa ?? '',
    razao_social: c.razao_social ?? '',
    cnpj: c.cnpj ?? '',
    setor: c.setor ?? '',
    porte_empresa: c.porte_empresa ?? 'MEI',
    status: c.status ?? 'Ativo',
    site: c.site ?? perfil.site ?? '',
    interesse_temas: c.interesse_temas ?? '',
    interesse_valor_min: c.interesse_valor_min ?? 0,
    interesse_valor_max: c.interesse_valor_max ?? 0,
    cidade: c.cidade ?? '',
    estado: c.estado ?? '',
    regiao: c.regiao ?? '',
    data_abertura: c.data_abertura ?? '',
    cnae_principal: c.cnae_principal ?? '',
    faturamento_anual: c.faturamento_anual ?? '',
    numero_funcionarios: c.numero_funcionarios ?? '',
    area_inovacao: c.area_inovacao ?? perfil.perfil_tecnologico.areas_tecnologicas ?? '',
    descricao_projeto:
      c.descricao_projeto ?? perfil.perfil_tecnologico.principais_atividades ?? '',
    perfil,
  };
}

export const CLIENT_FORM_DEFAULT_STATE = clientFormStateFromCliente(null);

/**
 * Payload para insert/update Supabase (colunas conhecidas + extras.perfil_consultivo).
 */
export function clientPayloadFromFormState(form) {
  const f = form || {};
  const perfil = f.perfil && typeof f.perfil === 'object' ? f.perfil : emptyPerfilConsultivo();

  if (hasText(f.area_inovacao)) {
    perfil.perfil_tecnologico.areas_tecnologicas = String(f.area_inovacao).trim();
  }
  if (hasText(f.descricao_projeto)) {
    perfil.perfil_tecnologico.principais_atividades = String(f.descricao_projeto).trim();
  }
  if (hasText(f.site)) perfil.site = String(f.site).trim();

  const payload = {
    nome_empresa: f.nome_empresa,
    razao_social: f.razao_social || null,
    cnpj: f.cnpj || null,
    setor: f.setor || null,
    porte_empresa: f.porte_empresa || null,
    status: f.status || 'Ativo',
    interesse_temas: f.interesse_temas || null,
    interesse_valor_min: f.interesse_valor_min ?? 0,
    interesse_valor_max: f.interesse_valor_max ?? 0,
    cidade: f.cidade || null,
    estado: f.estado || null,
    regiao: f.regiao || null,
    data_abertura: f.data_abertura || null,
    cnae_principal: f.cnae_principal || null,
    faturamento_anual: f.faturamento_anual === '' ? null : f.faturamento_anual,
    numero_funcionarios: f.numero_funcionarios === '' ? null : f.numero_funcionarios,
    area_inovacao: f.area_inovacao || null,
    descricao_projeto: f.descricao_projeto || null,
    extras: {
      [PERFIL_CONSULTIVO_KEY]: perfil,
    },
  };

  return payload;
}

/**
 * Preserva chaves existentes em extras ao editar.
 */
export function mergeClientWritePayload(existingCliente, formState) {
  const next = clientPayloadFromFormState(formState);
  const prevExtras = parseExtras(existingCliente?.extras);
  next.extras = {
    ...prevExtras,
    ...next.extras,
    [PERFIL_CONSULTIVO_KEY]: next.extras[PERFIL_CONSULTIVO_KEY],
  };
  return next;
}

/** Campos achatados para Radar / pré-projeto (sem alterar score). */
export function clienteEnrichedForApps(cliente) {
  if (!cliente) return cliente;
  const perfil = cliente.perfilConsultivo || hydratePerfilFromClienteRow(cliente);
  const contato = cliente.contatoPrincipal || perfil.contato || {};
  const eco = cliente.dadosEconomicos || perfil.dados_economicos || {};
  const tec = cliente.perfilTecnologico || perfil.perfil_tecnologico || {};
  const pref = cliente.preferenciasFomento || perfil.preferencias_fomento || {};

  return {
    ...cliente,
    email: cliente.email || contato.email,
    telefone: cliente.telefone || contato.telefone,
    nome_contato: cliente.nome_contato || contato.nome,
    site: cliente.site || perfil.site,
    ebitda: cliente.ebitda || eco.ebitda,
    grupo_economico: cliente.grupo_economico || eco.grupo_economico,
    interesse_temas:
      cliente.interesse_temas || tec.areas_tecnologicas || cliente.area_inovacao,
    area_inovacao: cliente.area_inovacao || tec.areas_tecnologicas,
    descricao_projeto:
      cliente.descricao_projeto || tec.principais_atividades,
    preferencias_fomento_tipos: pref.tipos_recurso,
    preferencias_fomento: pref,
    perfilConsultivo: perfil,
  };
}
