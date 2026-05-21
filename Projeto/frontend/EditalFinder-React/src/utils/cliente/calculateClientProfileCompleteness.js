import { TIPOS_RECURSO_FOMENTO } from './clientePerfilConsultivo';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function hasNumber(v) {
  return v != null && v !== '' && !Number.isNaN(Number(v));
}

function triFilled(v) {
  return v === true || v === false || v === 'sim' || v === 'nao';
}

/**
 * @param {object} cliente — já normalizado (com perfilConsultivo etc.)
 */
export function calculateClientProfileCompleteness(cliente) {
  const c = cliente || {};
  const contato = c.contatoPrincipal || {};
  const eco = c.dadosEconomicos || {};
  const tec = c.perfilTecnologico || {};
  const pref = c.preferenciasFomento || {};
  const doc = c.documentacao || {};
  const diag = c.diagnosticoConsultor || {};

  const sections = {
    basicos: {
      label: 'Dados básicos',
      weight: 18,
      score: 0,
      max: 6,
      filled: 0,
      missing: [],
    },
    contato: {
      label: 'Contato',
      weight: 14,
      score: 0,
      max: 4,
      filled: 0,
      missing: [],
    },
    localizacao: {
      label: 'Localização',
      weight: 12,
      score: 0,
      max: 4,
      filled: 0,
      missing: [],
    },
    economico: {
      label: 'Dados econômicos',
      weight: 14,
      score: 0,
      max: 5,
      filled: 0,
      missing: [],
    },
    tecnologico: {
      label: 'Perfil tecnológico',
      weight: 16,
      score: 0,
      max: 4,
      filled: 0,
      missing: [],
    },
    preferencias: {
      label: 'Preferências de fomento',
      weight: 14,
      score: 0,
      max: 5,
      filled: 0,
      missing: [],
    },
    documentacao: {
      label: 'Documentação',
      weight: 6,
      score: 0,
      max: 3,
      filled: 0,
      missing: [],
    },
    diagnostico: {
      label: 'Diagnóstico consultor',
      weight: 6,
      score: 0,
      max: 3,
      filled: 0,
      missing: [],
    },
  };

  const bump = (key, ok, missingLabel) => {
    if (ok) sections[key].filled += 1;
    else if (missingLabel) sections[key].missing.push(missingLabel);
  };

  bump('basicos', hasText(c.nome_empresa) || hasText(c.razao_social), 'Nome ou razão social');
  bump('basicos', hasText(c.cnpj), 'CNPJ');
  bump('basicos', hasText(c.setor), 'Setor principal');
  bump('basicos', hasText(c.porte_empresa), 'Porte');
  bump('basicos', hasText(c.status), 'Status');
  bump('basicos', hasText(c.site), 'Site');

  bump('contato', hasText(contato.nome), 'Nome do responsável');
  bump('contato', hasText(contato.email), 'E-mail');
  bump('contato', hasText(contato.telefone), 'Telefone');
  bump('contato', hasText(contato.cargo), 'Cargo');

  bump('localizacao', hasText(c.cidade), 'Cidade');
  bump('localizacao', hasText(c.estado), 'Estado');
  bump('localizacao', hasText(c.regiao), 'Região de atuação');
  bump('localizacao', hasText(c.data_abertura), 'Data de constituição');

  bump('economico', hasText(c.cnae_principal), 'CNAE principal');
  bump('economico', hasNumber(c.faturamento_anual), 'Receita operacional');
  bump('economico', hasText(eco.ebitda), 'EBITDA');
  bump('economico', hasNumber(c.numero_funcionarios), 'Número de empregados');
  bump('economico', hasNumber(c.interesse_valor_min) || hasNumber(c.interesse_valor_max), 'Valor de interesse');

  bump('tecnologico', hasText(tec.areas_tecnologicas) || hasText(c.area_inovacao) || hasText(tec.temas_prioritarios), 'Áreas tecnológicas');
  bump('tecnologico', hasText(c.interesse_temas) || hasText(tec.temas_prioritarios), 'Temas de interesse');
  bump(
    'tecnologico',
    hasText(tec.principais_atividades) ||
      hasText(c.descricao_projeto) ||
      hasText(tec.descricao_projeto),
    'Principais atividades',
  );
  bump('tecnologico', hasText(tec.setores_estrategicos), 'Setores estratégicos');

  const tipos = Array.isArray(pref.tipos_recurso) ? pref.tipos_recurso : [];
  bump('preferencias', tipos.length > 0, 'Tipo de recurso desejado');
  bump(
    'preferencias',
    hasText(pref.faixa_valor_interesse) ||
      hasNumber(c.interesse_valor_min) ||
      hasNumber(c.interesse_valor_max),
    'Faixa de valor',
  );
  bump(
    'preferencias',
    (Array.isArray(pref.criterios_aceite) && pref.criterios_aceite.length > 0) ||
      triFilled(pref.aceita_internacional),
    'Aceita internacional',
  );
  bump('preferencias', hasText(pref.fontes_preferidas), 'Fontes preferidas');
  bump('preferencias', hasText(pref.prazo_minimo_confortavel_dias), 'Prazo mínimo confortável');

  const docFields = [
    doc.contrato_social,
    doc.certidoes_fiscais,
    doc.balanco_dre,
    doc.representante_legal,
    doc.documentos_tecnicos,
  ];
  const docFilled = docFields.filter(triFilled).length;
  sections.documentacao.filled = Math.min(3, docFilled);
  if (docFilled < 2) sections.documentacao.missing.push('Situação documental');

  bump('diagnostico', hasText(diag.contexto_cliente), 'Contexto do cliente');
  bump('diagnostico', hasText(diag.diagnostico_inicial) || hasText(diag.observacoes_internas), 'Diagnóstico inicial');
  bump('diagnostico', hasText(diag.proximas_acoes), 'Próximas ações');

  let totalWeight = 0;
  let weighted = 0;
  for (const s of Object.values(sections)) {
    s.score = s.max > 0 ? Math.round((s.filled / s.max) * 100) : 0;
    totalWeight += s.weight;
    weighted += (s.filled / s.max) * s.weight;
  }

  const score = totalWeight > 0 ? Math.round(weighted) : 0;
  const level = score >= 75 ? 'bom' : score >= 45 ? 'parcial' : 'inicial';

  const recommendedMissing = [];
  if (!hasText(contato.email)) recommendedMissing.push('e-mail de contato');
  if (!hasText(c.cnpj)) recommendedMissing.push('CNPJ');
  if (!hasText(c.cidade) || !hasText(c.estado)) recommendedMissing.push('cidade/estado');
  if (!hasText(tec.areas_tecnologicas) && !hasText(c.area_inovacao)) {
    recommendedMissing.push('áreas tecnológicas');
  }
  if (!hasNumber(c.interesse_valor_min) && !hasNumber(c.interesse_valor_max)) {
    recommendedMissing.push('valor de interesse');
  }
  if (tipos.length === 0) recommendedMissing.push('tipo de recurso desejado');

  const radarHints = [
    'áreas tecnológicas',
    'valor de interesse',
    'tipo de recurso',
    'localização (UF/região)',
    'preferência por internacional/licitação',
  ].filter((h) => recommendedMissing.some((m) => m.includes(h.split(' ')[0]) || m.includes(h)));

  return {
    score,
    level,
    sections,
    recommendedMissing,
    radarImprovementHint:
      radarHints.length > 0
        ? `Dados que mais melhoram o Radar: ${radarHints.slice(0, 3).join(', ')}.`
        : 'Perfil suficiente para recomendações iniciais; refine preferências de fomento.',
    canSaveMinimal: hasText(c.nome_empresa) || hasText(c.razao_social),
    tiposRecursoLabels: TIPOS_RECURSO_FOMENTO,
  };
}
