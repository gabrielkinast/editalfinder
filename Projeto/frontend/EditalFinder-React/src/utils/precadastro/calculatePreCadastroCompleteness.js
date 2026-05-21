/**
 * Completude estruturada: obrigatorios, recomendados, opcionais + pendências consultivas.
 */

function has(v) {
  if (v === null || v === undefined) return false;
  if (typeof v === 'boolean') return true;
  return String(v).trim() !== '';
}

/**
 * @typedef {object} PreCadCompleteness
 * @property {number} score
 * @property {'incompleto'|'basico'|'bom'|'pronto_pdf'} status
 * @property {string[]} requiredMissing
 * @property {string[]} recommendedMissing
 * @property {string[]} optionalMissing
 * @property {string[]} consultivePendencies
 * @property {Record<string, boolean>} checks
 * @property {Record<string, boolean>} sections
 */

/**
 * @param {Record<string, unknown>} form
 * @returns {PreCadCompleteness}
 */
export function calculatePreCadastroCompleteness(form) {
  const f = form || {};

  const sections = {
    resumoExecutivo:
      has(f.bloco_estr_resumo_executivo) ||
      has(f.bloco2_resumo_publicavel) ||
      has(f.bloco_estr_edital_ref_titulo),
    aderencia:
      has(f.bloco_estr_motivo_recomendacao) ||
      has(f.bloco_estr_principais_aderencias) ||
      has(f.bloco_estr_por_que_linha),
    escopo:
      has(f.bloco_estr_problema_oportunidade) &&
      (has(f.bloco_estr_solucao_proposta) || has(f.bloco_estr_objetivo_geral)),
    documentos:
      has(f.bloco_estr_docs_recomendados) ||
      has(f.bloco_estr_docs_cliente) ||
      has(f.bloco_estr_docs_tecnicos),
    riscos: has(f.bloco_estr_riscos_pendencias) || has(f.bloco_estr_lacunas),
    proximosPassos: has(f.bloco_estr_proximos_passos),
    orcamento:
      has(f.bloco_estr_orcamento_resumo) ||
      has(f.bloco2_recursos_adicionais_valor) ||
      !!f.bloco2_valor_projeto_sem_def,
    cronograma:
      has(f.bloco_estr_plano_trabalho) ||
      (Array.isArray(f.bloco2_metas_fisicas) &&
        f.bloco2_metas_fisicas.some((m) => has(m?.ini) || has(m?.fim) || has(m?.meta))),
  };

  const requiredDefs = [
    {
      id: 'nome_empresa',
      label: 'Identificação da empresa (nome ou razão social)',
      ok: has(f.bloco1_nome_fantasia) || has(f.bloco1_razao_social),
    },
    { id: 'cnpj', label: 'CNPJ para validação cadastral', ok: has(f.bloco1_cnpj) },
    { id: 'setor', label: 'Setor de atuação', ok: has(f.bloco1_setor_empresa) },
    { id: 'porte', label: 'Porte da empresa', ok: has(f.bloco1_porte_empresa) },
    {
      id: 'titulo',
      label: 'Título do projeto (comunicação com o cliente)',
      ok: has(f.bloco2_titulo_projeto),
    },
    {
      id: 'resumo',
      label: 'Resumo executivo para apresentação',
      ok: has(f.bloco2_resumo_publicavel) || has(f.bloco_estr_resumo_executivo),
    },
    {
      id: 'objetivo',
      label: 'Objetivo geral do projeto',
      ok: has(f.bloco_estr_objetivo_geral) || has(f.bloco2_finalidade_b),
    },
    {
      id: 'valor_ou_declaracao',
      label: 'Valor estimado ou declaração de “ainda não definido”',
      ok: has(f.bloco2_recursos_adicionais_valor) || !!f.bloco2_valor_projeto_sem_def || has(f.bloco_estr_orcamento_resumo),
    },
    {
      id: 'linha',
      label: 'Linha ou produto de fomento selecionado',
      ok: !!(f.bloco1_linha_credito_principal || f.bloco1_linha_credito_telecom),
    },
    {
      id: 'contato',
      label: 'Contato do responsável (nome e e-mail)',
      ok: has(f.bloco1_nome_contato) && has(f.bloco1_email_contato),
    },
  ];

  const recommendedDefs = [
    {
      id: 'aderencia_narrativa',
      label: 'Narrativa de aderência ao edital (por que combina)',
      ok: sections.aderencia,
    },
    {
      id: 'escopo_completo',
      label: 'Escopo inicial (problema + solução ou objetivo)',
      ok: sections.escopo,
    },
    {
      id: 'faturamento_rec',
      label: 'Indicadores econômicos (faturamento ou receita)',
      ok: has(f.bloco1_receita_rob_ultimo),
    },
    { id: 'empregados', label: 'Quadro de empregados', ok: has(f.bloco1_total_empregados) },
    {
      id: 'resultados',
      label: 'Resultados esperados e entregáveis',
      ok: has(f.bloco_estr_resultados_esperados) || has(f.bloco2_finalidade_e),
    },
    { id: 'impactos', label: 'Impactos declarados (econômico/social/ambiental)', ok: impactoAlgumMarcado(f) },
    { id: 'cronograma', label: 'Plano de trabalho ou cronograma preliminar', ok: sections.cronograma },
    {
      id: 'orcamento',
      label: 'Orçamento preliminar estruturado',
      ok: sections.orcamento,
    },
    {
      id: 'documentos',
      label: 'Lista de documentos necessários',
      ok: sections.documentos,
    },
    {
      id: 'riscos',
      label: 'Riscos e pendências mapeados',
      ok: sections.riscos,
    },
    {
      id: 'proximos',
      label: 'Próximos passos com o cliente',
      ok: sections.proximosPassos,
    },
  ];

  const optionalDefs = [
    {
      id: 'edital_ref',
      label: 'Oportunidade/edital de referência',
      ok: has(f.bloco_estr_edital_ref_titulo),
    },
    {
      id: 'oportunidade_meta',
      label: 'Fonte, prazo ou link da oportunidade',
      ok:
        has(f.bloco_estr_oportunidade_fonte) ||
        has(f.bloco_estr_oportunidade_prazo) ||
        has(f.bloco_estr_oportunidade_link),
    },
    { id: 'quadro_fontes', label: 'Quadro usos/fontes preenchido', ok: quadroUsosPreenchido(f) },
    { id: 'pdi', label: 'Capacidade de PD&I descrita', ok: has(f.bloco1_pdi_infraestrutura) || has(f.bloco1_pdi_detalhe_pessoas) },
    { id: 'checklist', label: 'Checklist inicial de acompanhamento', ok: has(f.bloco_estr_checklist_inicial) },
  ];

  const requiredMissing = requiredDefs.filter((x) => !x.ok).map((x) => x.label);
  const recommendedMissing = recommendedDefs.filter((x) => !x.ok).map((x) => x.label);
  const optionalMissing = optionalDefs.filter((x) => !x.ok).map((x) => x.label);

  const consultivePendencies = [];
  if (!sections.resumoExecutivo) {
    consultivePendencies.push('Completar resumo executivo para apresentar ao cliente.');
  }
  if (!sections.aderencia) {
    consultivePendencies.push('Descrever aderência: por que a oportunidade combina com o perfil.');
  }
  if (!sections.escopo) {
    consultivePendencies.push('Detalhar escopo: problema/oportunidade e solução proposta.');
  }
  if (!sections.documentos) {
    consultivePendencies.push('Listar documentos necessários (cliente, técnico, financeiro, edital).');
  }
  if (!sections.riscos) {
    consultivePendencies.push('Registrar riscos e pendências (prazo, elegibilidade, dados faltantes).');
  }
  if (!sections.proximosPassos) {
    consultivePendencies.push('Definir próximos passos com o cliente (validação, reunião, submissão).');
  }
  if (!sections.orcamento) {
    consultivePendencies.push('Preencher orçamento preliminar ou marcar valor como indefinido.');
  }
  if (!sections.cronograma) {
    consultivePendencies.push('Esboçar plano de trabalho ou cronograma com marcos.');
  }

  const reqOk = requiredDefs.filter((x) => x.ok).length;
  const recOk = recommendedDefs.filter((x) => x.ok).length;
  const optOk = optionalDefs.filter((x) => x.ok).length;
  const secOk = Object.values(sections).filter(Boolean).length;
  const secTotal = Object.keys(sections).length;

  const score = Math.min(
    100,
    Math.round(
      (reqOk / requiredDefs.length) * 50 +
        (recOk / recommendedDefs.length) * 30 +
        (optOk / optionalDefs.length) * 8 +
        (secOk / secTotal) * 12,
    ),
  );

  let status = 'incompleto';
  if (score >= 88 && requiredMissing.length === 0 && secOk >= 6) status = 'pronto_pdf';
  else if (score >= 68) status = 'bom';
  else if (score >= 38) status = 'basico';

  const checks = {
    dadosEmpresa: requiredDefs.find((d) => d.id === 'nome_empresa')?.ok && requiredDefs.find((d) => d.id === 'cnpj')?.ok,
    linha: requiredDefs.find((d) => d.id === 'linha')?.ok,
    titulo: requiredDefs.find((d) => d.id === 'titulo')?.ok,
    resumo: requiredDefs.find((d) => d.id === 'resumo')?.ok,
    objetivo: requiredDefs.find((d) => d.id === 'objetivo')?.ok,
    escopo: sections.escopo,
    aderencia: sections.aderencia,
    documentos: sections.documentos,
    riscos: sections.riscos,
    orcamento: sections.orcamento,
    cronograma: sections.cronograma,
  };

  return {
    score,
    status,
    requiredMissing,
    recommendedMissing,
    optionalMissing,
    consultivePendencies,
    checks,
    sections,
  };
}

function impactoAlgumMarcado(f) {
  const keys = Object.keys(f).filter((k) => k.startsWith('bloco2_imp_') && !k.endsWith('_txt'));
  return keys.some((k) => f[k] === true);
}

function quadroUsosPreenchido(f) {
  const arr = f.bloco2_uso_fontes;
  if (!Array.isArray(arr) || !arr.length) return false;
  return arr.some((row) => row && Object.values(row).some((cell) => has(cell)));
}

/**
 * Compativel com `computeCompletion` legado (abas antigas / PDF).
 * @param {Record<string, unknown>} form
 */
export function toLegacyCompletionShape(form) {
  const c = calculatePreCadastroCompleteness(form);
  const done = Object.values(c.checks).filter(Boolean).length;
  const total = Object.keys(c.checks).length;
  const levelMap = { pronto_pdf: 'pronto', bom: 'bom', basico: 'basico', incompleto: 'incompleto' };
  return {
    score: c.score,
    level: levelMap[c.status] || 'incompleto',
    checks: c.checks,
    done,
    total,
  };
}
