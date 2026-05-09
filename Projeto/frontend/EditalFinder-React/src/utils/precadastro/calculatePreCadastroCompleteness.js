/**
 * Completude estruturada: obrigatorios, recomendados, opcionais.
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
 * @property {Record<string, boolean>} checks
 */

/**
 * @param {Record<string, unknown>} form
 * @returns {PreCadCompleteness}
 */
export function calculatePreCadastroCompleteness(form) {
  const f = form || {};

  const requiredDefs = [
    {
      id: 'nome_empresa',
      label: 'Nome fantasia ou razao social',
      ok: has(f.bloco1_nome_fantasia) || has(f.bloco1_razao_social),
    },
    { id: 'cnpj', label: 'CNPJ', ok: has(f.bloco1_cnpj) },
    { id: 'setor', label: 'Setor', ok: has(f.bloco1_setor_empresa) },
    { id: 'porte', label: 'Porte', ok: has(f.bloco1_porte_empresa) },
    { id: 'titulo', label: 'Titulo do projeto', ok: has(f.bloco2_titulo_projeto) },
    {
      id: 'resumo',
      label: 'Resumo publicavel',
      ok: has(f.bloco2_resumo_publicavel) || has(f.bloco_estr_resumo_executivo),
    },
    {
      id: 'objetivo',
      label: 'Objetivo geral',
      ok: has(f.bloco_estr_objetivo_geral) || has(f.bloco2_finalidade_b),
    },
    {
      id: 'valor_ou_declaracao',
      label: 'Valor solicitado ou indicacao "ainda nao definido"',
      ok: has(f.bloco2_recursos_adicionais_valor) || !!f.bloco2_valor_projeto_sem_def,
    },
    {
      id: 'linha',
      label: 'Linha / produto',
      ok: !!(f.bloco1_linha_credito_principal || f.bloco1_linha_credito_telecom),
    },
    {
      id: 'contato',
      label: 'Contato (nome e e-mail)',
      ok: has(f.bloco1_nome_contato) && has(f.bloco1_email_contato),
    },
  ];

  const recommendedDefs = [
    { id: 'faturamento_rec', label: 'Faturamento ou receita declarada', ok: has(f.bloco1_receita_rob_ultimo) },
    { id: 'empregados', label: 'Numero de empregados', ok: has(f.bloco1_total_empregados) },
    {
      id: 'desafios',
      label: 'Desafios tecnologicos',
      ok: has(f.bloco2_finalidade_c) || has(f.bloco_estr_solucao_proposta),
    },
    {
      id: 'resultados',
      label: 'Resultados esperados',
      ok: has(f.bloco_estr_resultados_esperados) || has(f.bloco2_finalidade_e),
    },
    { id: 'impactos', label: 'Algum impacto declarado', ok: impactoAlgumMarcado(f) },
    {
      id: 'cronograma',
      label: 'Cronograma ou metas',
      ok:
        Array.isArray(f.bloco2_metas_fisicas) &&
        f.bloco2_metas_fisicas.some((m) => has(m?.ini) || has(m?.fim) || has(m?.meta)),
    },
    {
      id: 'contrapartida',
      label: 'Contrapartida ou percentuais relacionados',
      ok: has(f.bloco2_pct_icts) || has(f.bloco2_uso_fontes?.[0]?.contrapartida),
    },
    { id: 'licencas', label: 'Licencas/autorizações mencionadas', ok: has(f.bloco2_licencas) },
  ];

  const optionalDefs = [
    { id: 'edital_ref', label: 'Edital de referencia preenchido', ok: has(f.bloco_estr_edital_ref_titulo) },
    { id: 'quadro_fontes', label: 'Quadro usos/fontes preenchido', ok: quadroUsosPreenchido(f) },
    { id: 'pdi', label: 'Texto de PD&I', ok: has(f.bloco1_pdi_infraestrutura) || has(f.bloco1_pdi_detalhe_pessoas) },
  ];

  const requiredMissing = requiredDefs.filter((x) => !x.ok).map((x) => x.label);
  const recommendedMissing = recommendedDefs.filter((x) => !x.ok).map((x) => x.label);
  const optionalMissing = optionalDefs.filter((x) => !x.ok).map((x) => x.label);

  const reqOk = requiredDefs.filter((x) => x.ok).length;
  const recOk = recommendedDefs.filter((x) => x.ok).length;
  const optOk = optionalDefs.filter((x) => x.ok).length;

  const score = Math.min(
    100,
    Math.round((reqOk / requiredDefs.length) * 62 + (recOk / recommendedDefs.length) * 28 + (optOk / optionalDefs.length) * 10),
  );

  let status = 'incompleto';
  if (score >= 88 && requiredMissing.length === 0) status = 'pronto_pdf';
  else if (score >= 68) status = 'bom';
  else if (score >= 38) status = 'basico';

  const checks = {
    dadosEmpresa: requiredDefs.find((d) => d.id === 'nome_empresa')?.ok && requiredDefs.find((d) => d.id === 'cnpj')?.ok,
    linha: requiredDefs.find((d) => d.id === 'linha')?.ok,
    titulo: requiredDefs.find((d) => d.id === 'titulo')?.ok,
    resumo: requiredDefs.find((d) => d.id === 'resumo')?.ok,
    objetivo: requiredDefs.find((d) => d.id === 'objetivo')?.ok,
    escopo: has(f.bloco_estr_problema_oportunidade) || has(f.bloco2_finalidade_a),
  };

  return {
    score,
    status,
    requiredMissing,
    recommendedMissing,
    optionalMissing,
    checks,
  };
}

function impactoAlgumMarcado(f) {
  const keys = Object.keys(f).filter((k) => k.startsWith('bloco2_imp_') && !k.endsWith('_txt'));
  return keys.some((k) => {
    const v = f[k];
    return v === true;
  });
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
