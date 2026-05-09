import { buildProjectSuggestions } from './projectIntel';
import {
  classifySectorKey,
  suggestTituloProjeto,
  suggestResumoPublicavel,
  suggestProblemaOportunidade,
  suggestSolucaoProposta,
  suggestObjetivoGeral,
  suggestFinalidadesBlocos,
  formatEditalFinanceRefs,
  hintImpactsForSector,
} from './preCadastroTemplates';
import {
  SOURCE_AUTO,
  SOURCE_CLIENTE,
  SOURCE_EDITAL,
  SOURCE_RADAR,
  SOURCE_MANUAL,
  CONF_HIGH,
  CONF_MEDIUM,
  CONF_LOW,
  isProtectedManual,
} from './preCadastroTypes';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function normEdital(edital) {
  if (!edital) return null;
  return {
    titulo: edital.titulo ?? edital.nome ?? '',
    fonte_recurso: edital.fonte_recurso ?? edital.origem ?? edital.orgao ?? '',
    tipo_oportunidade: edital.tipo_oportunidade ?? '',
    tipo_recurso: edital.tipo_recurso ?? edital.tipo_recurso_raw ?? '',
    perfil_ideal: edital.perfil_ideal ?? edital.publico_alvo ?? '',
    prazo_envio: edital.prazo_envio ?? edital.prazo_envio_raw ?? edital.dataLimite ?? '',
    valor_maximo: edital.valor_maximo ?? edital.valorMaximo ?? '',
    linha_credito: edital.linha_credito ?? '',
    modalidade_financiamento: edital.modalidade_financiamento ?? '',
    natureza_recurso: edital.natureza_recurso ?? '',
    descricao: edital.descricao ?? '',
    taxa: edital.taxa,
    carencia: edital.carencia,
    amortizacao: edital.amortizacao,
    contrapartida: edital.contrapartida,
  };
}

/**
 * @param {string} key
 * @param {unknown} value
 * @param {import('./preCadastroTypes.js').FieldIntelSource} source
 * @param {import('./preCadastroTypes.js').FieldIntelConfidence} confidence
 * @param {string} explanation
 * @param {boolean} needsReview
 */
function intelEntry(source, confidence, explanation, needsReview = true) {
  return { source, confidence, needsReview, explanation, updatedAt: new Date().toISOString() };
}

/**
 * @param {object} params
 * @param {object|null} params.cliente
 * @param {object|null} params.edital
 * @param {object|null} params.radarMatch
 * @param {Record<string, unknown>} params.existingForm
 * @param {import('./preCadastroTypes.js').FieldIntelMap} params.existingFieldIntel
 * @param {{ overwriteManual?: boolean }} [params.options]
 */
export function buildPreCadastroDraft({
  cliente = null,
  edital = null,
  radarMatch = null,
  existingForm = {},
  existingFieldIntel = {},
  options = {},
}) {
  const overwriteManual = !!options.overwriteManual;
  /** Exceto quando `overwriteManual`, nunca sobrescreve valor já preenchido (string ou boolean). */
  const onlyFillEmpty = !overwriteManual;
  const c = cliente || {};
  const e = normEdital(edital);
  const editalTitulo = `${e?.titulo || ''}`.trim() || `${radarMatch?.tituloEdital || ''}`.trim();

  let form = { ...existingForm };
  let fieldIntel = { ...existingFieldIntel };

  const pendencias = [];
  const autogerados = [];
  const saltadosManual = [];
  const precisaConfirmacao = [];

  const canWrite = (fieldKey) => {
    if (overwriteManual) return true;
    const ent = fieldIntel[fieldKey];
    if (isProtectedManual(ent)) return false;
    return true;
  };

  const assign = (fieldKey, value, meta) => {
    if (value === undefined || value === null) return;
    if (!canWrite(fieldKey)) {
      saltadosManual.push(fieldKey);
      return;
    }
    const cur = form[fieldKey];
    const empty = cur === '' || cur === null || cur === undefined;
    if (onlyFillEmpty && !empty) return;
    if (typeof value === 'string' && !hasText(value)) return;
    form[fieldKey] = value;
    fieldIntel[fieldKey] = intelEntry(
      meta.source,
      meta.confidence,
      meta.explanation,
      meta.needsReview !== undefined ? meta.needsReview : true,
    );
    autogerados.push(fieldKey);
  };

  /** ---- A) Cliente: somente dados existentes no cadastro (sem inventar) ---- */
  const setCliente = (k, v, expl) => {
    if (!hasText(v)) {
      if (['bloco1_cnpj', 'bloco1_razao_social', 'bloco1_nome_fantasia', 'bloco1_setor_empresa', 'bloco1_porte_empresa'].includes(k))
        pendencias.push(`Cadastro: ${k} ausente — completar manualmente ou no cadastro do cliente.`);
      return;
    }
    if (!canWrite(k)) return;
    const cur = form[k];
    const empty = !hasText(cur);
    if (onlyFillEmpty && !empty) return;
    form[k] = String(v);
    fieldIntel[k] = intelEntry(SOURCE_CLIENTE, CONF_HIGH, expl, false);
  };

  setCliente('bloco1_cnpj', c.cnpj, 'CNPJ copiado do cadastro do cliente.');
  setCliente('bloco1_razao_social', c.razao_social, 'Razao social do cadastro.');
  setCliente('bloco1_nome_fantasia', c.nome_empresa, 'Nome fantasia do cadastro.');
  setCliente('bloco1_data_constituicao', c.data_abertura, 'Data de constituicao do cadastro.');
  setCliente('bloco1_municipio', c.cidade, 'Municipio do cadastro.');
  setCliente('bloco1_uf', c.estado ? String(c.estado).toUpperCase() : '', 'UF do cadastro.');
  setCliente('bloco1_cnae', c.cnae_principal, 'CNAE principal do cadastro.');
  setCliente('bloco1_porte_empresa', c.porte_empresa, 'Porte do cadastro.');
  setCliente('bloco1_setor_empresa', c.setor, 'Setor do cadastro.');

  if (c.faturamento_anual != null && c.faturamento_anual !== '' && canWrite('bloco1_receita_rob_ultimo')) {
    const empty = !hasText(form.bloco1_receita_rob_ultimo);
    if ((!onlyFillEmpty || empty)) {
      form.bloco1_receita_rob_ultimo = String(c.faturamento_anual);
      fieldIntel.bloco1_receita_rob_ultimo = intelEntry(
        SOURCE_CLIENTE,
        CONF_HIGH,
        'Valor informado no cadastro do cliente (receita/faturamento anual) — confirme se ainda e valido.',
        true,
      );
      autogerados.push('bloco1_receita_rob_ultimo');
    }
  }

  if (c.numero_funcionarios != null && c.numero_funcionarios !== '' && canWrite('bloco1_total_empregados')) {
    const empty = !hasText(form.bloco1_total_empregados);
    if ((!onlyFillEmpty || empty)) {
      form.bloco1_total_empregados = String(c.numero_funcionarios);
      fieldIntel.bloco1_total_empregados = intelEntry(
        SOURCE_CLIENTE,
        CONF_HIGH,
        'Total de empregados vindo do cadastro — verificar atualidade.',
        true,
      );
      autogerados.push('bloco1_total_empregados');
    }
  }

  /** ---- B) Edital (referencia, sem garantir exatidao legal) ---- */
  if (e) {
    if (hasText(e.titulo) && canWrite('bloco_estr_edital_ref_titulo')) {
      const empty = !hasText(form.bloco_estr_edital_ref_titulo);
      if (!onlyFillEmpty || empty) {
        form.bloco_estr_edital_ref_titulo = String(e.titulo);
        fieldIntel.bloco_estr_edital_ref_titulo = intelEntry(
          SOURCE_EDITAL,
          CONF_HIGH,
          'Titulo da oportunidade/edital selecionado.',
          false,
        );
        autogerados.push('bloco_estr_edital_ref_titulo');
      }
    }
    const tipoRec = `${e.tipo_recurso || ''}`.trim();
    if (tipoRec && canWrite('bloco_estr_tipo_recurso_pdf')) {
      const empty = !hasText(form.bloco_estr_tipo_recurso_pdf);
      if (!onlyFillEmpty || empty) {
        form.bloco_estr_tipo_recurso_pdf = tipoRec;
        fieldIntel.bloco_estr_tipo_recurso_pdf = intelEntry(
          SOURCE_EDITAL,
          CONF_MEDIUM,
          'Tipo de recurso informado na ficha da oportunidade — conferir no regulamento.',
          true,
        );
        autogerados.push('bloco_estr_tipo_recurso_pdf');
      }
    }
    const finRefs = formatEditalFinanceRefs(e);
    if (finRefs && canWrite('bloco_estr_ref_fin_texto')) {
      const empty = !hasText(form.bloco_estr_ref_fin_texto);
      if (!onlyFillEmpty || empty) {
        form.bloco_estr_ref_fin_texto = finRefs;
        fieldIntel.bloco_estr_ref_fin_texto = intelEntry(
          SOURCE_EDITAL,
          CONF_MEDIUM,
          'Texto agregado apenas com campos explicitamente presentes na oportunidade (sem inventar).',
          true,
        );
        autogerados.push('bloco_estr_ref_fin_texto');
      }
    }
  }

  /** Interesse do cliente (nao e inventado — vem do cadastro) */
  const interMin = c.interesse_valor_min;
  const interMax = c.interesse_valor_max;
  if ((interMin != null && interMin !== '') || (interMax != null && interMax !== '')) {
    const sug = [interMin, interMax].filter((x) => x != null && x !== '').join(' — ');
    if (canWrite('bloco2_recursos_adicionais_valor') && (!onlyFillEmpty || !hasText(form.bloco2_recursos_adicionais_valor))) {
      assign('bloco2_recursos_adicionais_valor', sug, {
        source: SOURCE_CLIENTE,
        confidence: CONF_MEDIUM,
        explanation:
          'Faixa de valor de interesse declarada no cadastro do cliente (nao inventada). Revisar antes de submissao.',
        needsReview: true,
      });
    }
  }

  /** ---- C) Radar ---- */
  if (radarMatch) {
    if (typeof radarMatch.scorePct === 'number' && canWrite('bloco_estr_aderencia_nivel')) {
      const lbl =
        radarMatch.scorePct >= 70 ? 'alta' : radarMatch.scorePct >= 40 ? 'media' : 'baixa';
      const empty = !hasText(form.bloco_estr_aderencia_nivel);
      if (!onlyFillEmpty || empty) {
        form.bloco_estr_aderencia_nivel = lbl;
        fieldIntel.bloco_estr_aderencia_nivel = intelEntry(
          SOURCE_RADAR,
          CONF_MEDIUM,
          'Nivel derivado da pontuacao numerica do Radar (referencia interna).',
          true,
        );
        autogerados.push('bloco_estr_aderencia_nivel');
      }
    }
    const razoes = Array.isArray(radarMatch.razoes) ? radarMatch.razoes : [];
    const explRadar = [...razoes.slice(0, 4)].join('\n• ');
    if (explRadar && canWrite('bloco_estr_principais_aderencias')) {
      const base = hasText(form.bloco_estr_principais_aderencias)
        ? `${form.bloco_estr_principais_aderencias}\n\n`
        : '';
      const block = `${base}[Radar]\n• ${explRadar}`;
      if (!onlyFillEmpty || !hasText(form.bloco_estr_principais_aderencias)) {
        form.bloco_estr_principais_aderencias = block;
        fieldIntel.bloco_estr_principais_aderencias = intelEntry(
          SOURCE_RADAR,
          CONF_MEDIUM,
          'Trechos vindos das explicacoes do Radar (quando disponiveis).',
          true,
        );
        autogerados.push('bloco_estr_principais_aderencias');
      }
    }
    const pens = radarMatch.radar_penalidades || radarMatch.penalidades;
    const penArr = Array.isArray(pens) ? pens : Array.isArray(pens?.motivos) ? pens.motivos : [];
    if (
      penArr.length &&
      canWrite('bloco_estr_lacunas')
    ) {
      const textoPen = `\nPossiveis alertas do Radar: ${penArr.slice(0, 5).join('; ')}.`;
      if (!onlyFillEmpty || !String(form.bloco_estr_lacunas || '').includes('Possiveis alertas')) {
        form.bloco_estr_lacunas = `${String(form.bloco_estr_lacunas || '').trim()}${textoPen}`.trim();
        fieldIntel.bloco_estr_lacunas = intelEntry(
          SOURCE_RADAR,
          CONF_LOW,
          'Alertas ou penalidades do motor de Radar — revisar antes de decisao.',
          true,
        );
        autogerados.push('bloco_estr_lacunas');
      }
    }
  }

  /** ---- Sugestões textuais (auto) sobre projectIntel + templates ---- */
  const sug = buildProjectSuggestions(c, e || (editalTitulo ? { titulo: editalTitulo } : null), radarMatch);
  const sectorKey = classifySectorKey(c);
  const titTpl = suggestTituloProjeto(c, editalTitulo, sectorKey);
  const resTpl = suggestResumoPublicavel(c, e, radarMatch, sectorKey);
  const probTpl = suggestProblemaOportunidade(c);
  const solTpl = suggestSolucaoProposta(c, sectorKey);
  const objTpl = suggestObjetivoGeral(c, e, radarMatch);
  const fin = suggestFinalidadesBlocos(c, sectorKey);

  const pushAuto = (key, val, expl, conf = CONF_MEDIUM) =>
    assign(key, val, { source: SOURCE_AUTO, confidence: conf, explanation: expl, needsReview: true });

  pushAuto('bloco2_titulo_projeto', titTpl.texto, titTpl.explanation);
  pushAuto('bloco2_resumo_publicavel', resTpl.texto, resTpl.explanation);
  pushAuto('bloco_estr_resumo_executivo', resTpl.texto, 'Resumo sintetico espelhado no campo estrategico (para consistencia nas abas).');
  pushAuto('bloco_estr_problema_oportunidade', probTpl.texto, probTpl.explanation);
  pushAuto('bloco_estr_solucao_proposta', solTpl.texto, solTpl.explanation);
  pushAuto('bloco_estr_objetivo_geral', objTpl.texto, objTpl.explanation);
  pushAuto('bloco2_finalidade_a', fin.a, 'Orientacao inicial Finep-inspired (what) — revise com detalhes reais.', CONF_LOW);
  pushAuto('bloco2_finalidade_b', fin.b, 'Orientacao inicial para aplicacao — precise com o publico efetivo.');
  pushAuto('bloco2_finalidade_c', fin.c, 'Lembrete neutro sobre desafios tecnologicos — liste os verdadeiros.', CONF_LOW);
  pushAuto('bloco2_finalidade_d', fin.d, 'ICT/parcerias — confirmar com a empresa.');
  pushAuto('bloco2_finalidade_e', fin.e, 'Resultados esperados — substituir por metas quando a equipe definir KPIs.', CONF_LOW);
  pushAuto('bloco2_finalidade_f', fin.f, 'Diferencial competitivo — evitar hype; usar fatos quando possivel.', CONF_LOW);
  pushAuto('bloco2_finalidade_g', fin.g, 'Entrega em produto/processo/servico — detalhar no corpo técnico.');
  pushAuto('bloco_estr_motivo_recomendacao', sug.motivoRecomendacao, 'Gerado por heuristica do modulo de sugestoes (cadastro/edital/Radar).');
  if (!hasText(form.bloco_estr_principais_aderencias)) {
    pushAuto('bloco_estr_principais_aderencias', sug.principaisAderencias, 'Pontos heuristicos vindos cadastro cliente / edital (sem garantia legal).');
  }
  pushAuto('bloco_estr_pontos_complementar', sug.pontosComplementar, 'Texto inicial de pontos por completar segundo cadastro.');
  pushAuto('bloco_estr_por_que_linha', sug.porQueLinha, 'Explicacao generica sobre escolhas de linha institucional.');
  pushAuto('bloco_estr_requisitos_atendidos', sug.requisitosAtendidos, 'Indicadores do cadastro; complementar checklist do edital real.');
  if (!hasText(form.bloco_estr_lacunas)) {
    pushAuto('bloco_estr_lacunas', sug.lacunas, 'Lacunas modeladas pela heuristica — nao substitui revisao tecnica/legal.');
  }
  pushAuto('bloco_estr_docs_recomendados', sug.docsRecomendados, 'Lista modelo de documentos sugeridos.');
  pushAuto('bloco_estr_proximos_passos', sug.proximosPassos, 'Lista sugerida de proximos passos internos.');
  pushAuto('bloco_estr_diferencial_inovador', sug.diferencialInovador, 'Diferencial orientativos do motor atual.');
  pushAuto('bloco_estr_publico_mercado', sug.publicoMercado, 'Publico inicial baseado cadastro quando possivel.');
  pushAuto('bloco_estr_resultados_esperados', sug.resultadosEsperados, 'Orientacao geral sobre resultados esperados.');
  pushAuto('bloco_estr_maturidade', sug.maturidade, 'Estagio de maturidade sugerido pela heuristica (ajustar caso a caso).', CONF_LOW);

  /** Linhas de credito sugeridas */
  const noLinha = !form.bloco1_linha_credito_principal && !form.bloco1_linha_credito_telecom;
  if (noLinha) {
    if (canWrite('bloco1_linha_credito_principal') && sug.suggestCheckPrincipal) {
      form.bloco1_linha_credito_principal = true;
      fieldIntel.bloco1_linha_credito_principal = intelEntry(
        SOURCE_AUTO,
        CONF_MEDIUM,
        'Marcado automaticamente pelo perfil — desmarque se nao for o caso.',
        true,
      );
      autogerados.push('bloco1_linha_credito_principal');
    }
    if (canWrite('bloco1_linha_credito_telecom') && sug.suggestCheckTelecom) {
      form.bloco1_linha_credito_telecom = true;
      fieldIntel.bloco1_linha_credito_telecom = intelEntry(
        SOURCE_AUTO,
        CONF_LOW,
        'Telecom sugerida por termos no cadastro — revisar.',
        true,
      );
      autogerados.push('bloco1_linha_credito_telecom');
    }
  }

  const sugestaoImpactos = hintImpactsForSector(sectorKey);

  return {
    mergedForm: form,
    mergedFieldIntel: fieldIntel,
    report: {
      pendencias,
      autogerados,
      saltadosManual,
      precisaConfirmacao,
      sugestaoImpactos,
      sectorKey,
      editalTitulo: editalTitulo || null,
    },
  };
}

/**
 * Remove apenas entradas `source === auto` e zera valores string/bool suaves.
 * @param {Record<string, unknown>} form
 * @param {import('./preCadastroTypes.js').FieldIntelMap} fieldIntel
 */
export function clearAutoSuggestions(form, fieldIntel) {
  const f = clone(form);
  const fi = { ...fieldIntel };
  const keys = Object.keys(fi);
  for (const k of keys) {
    if (fi[k]?.source !== SOURCE_AUTO) continue;
    delete fi[k];
    const v = f[k];
    if (typeof v === 'boolean') f[k] = false;
    else if (typeof v === 'string') f[k] = '';
    else f[k] = '';
  }
  return { form: f, fieldIntel: fi };
}

/**
 * Marca campo como editado manualmente (protege contra regeneracao).
 */
export function markFieldManual(fieldIntel, fieldKey, explanation = 'Editado manualmente pelo usuario.') {
  return {
    ...fieldIntel,
    [fieldKey]: intelEntry(SOURCE_MANUAL, CONF_HIGH, explanation, false),
  };
}
