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
  buildConsultorExecutiveSummary,
  buildConsultorFitNarrative,
  buildConsultorRisks,
  buildConsultorNextSteps,
  buildConsultorWorkPlan,
  buildConsultorBudgetSummary,
  buildBudgetCategoriesHint,
  buildStructuredDocumentsChecklist,
  buildInitialChecklist,
  collectRadarAlerts,
  collectRadarPositiveReasons,
  formatOportunidadeMeta,
  formatScoreCompatLabel,
} from './consultorAutofill';
import { logPrecadastro } from './precadastroLog';
import {
  buildMultiExecutiveSummary,
  buildMultiFitNarrative,
  buildMultiRisks,
  buildMultiNextSteps,
  buildMultiDocuments,
  buildMultiBudget,
  serializeOportunidadesSelecionadas,
} from './multiOpportunityAutofill';
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
import { clienteEnrichedForApps } from '../cliente/clientePerfilConsultivo';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function tituloCurto(t, max = 90) {
  const s = String(t || '').trim();
  return s.length > max ? `${s.slice(0, max)}…` : s;
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
 * @param {object[]} [params.oportunidadesSelecionadas]
 * @param {object|null} [params.oportunidadePrincipal]
 * @param {object[]} [params.oportunidadesRelacionadas]
 * @param {Record<string, unknown>} params.existingForm
 * @param {import('./preCadastroTypes.js').FieldIntelMap} params.existingFieldIntel
 * @param {{ overwriteManual?: boolean }} [params.options]
 */
export function buildPreCadastroDraft({
  cliente = null,
  edital = null,
  radarMatch = null,
  oportunidadesSelecionadas = [],
  oportunidadePrincipal = null,
  oportunidadesRelacionadas = [],
  existingForm = {},
  existingFieldIntel = {},
  options = {},
}) {
  const overwriteManual = !!options.overwriteManual;
  /** Exceto quando `overwriteManual`, nunca sobrescreve valor já preenchido (string ou boolean). */
  const onlyFillEmpty = !overwriteManual;
  const c = clienteEnrichedForApps(cliente || {});
  const cont = c.contatoPrincipal || {};
  const eco = c.dadosEconomicos || {};
  const loc = c.perfilConsultivo?.localizacao || {};
  const multiList = Array.isArray(oportunidadesSelecionadas) ? oportunidadesSelecionadas : [];
  const primary =
    oportunidadePrincipal ||
    (multiList.length ? multiList[0] : null);
  const related =
    oportunidadesRelacionadas?.length > 0
      ? oportunidadesRelacionadas
      : multiList.length > 1 && primary
        ? multiList.filter((o) => o.key !== primary.key)
        : [];

  let editalUse = edital;
  let radarUse = radarMatch;
  if (primary && multiList.length > 0) {
    editalUse = primary.edital ?? edital;
    radarUse = primary.radarMatch ?? radarMatch;
  }

  const e = normEdital(editalUse);
  const editalTitulo = `${e?.titulo || ''}`.trim() || `${radarUse?.tituloEdital || ''}`.trim();

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
  setCliente('bloco1_nome_contato', cont.nome || c.nome_contato, 'Contato principal do cadastro.');
  setCliente('bloco1_email_contato', cont.email || c.email, 'E-mail do cadastro do cliente.');
  setCliente('bloco1_telefone_contato', cont.telefone || c.telefone, 'Telefone do cadastro.');
  setCliente('bloco1_cargo_contato', cont.cargo, 'Cargo do responsavel no cadastro.');
  setCliente('bloco1_cpf_contato', cont.cpf, 'CPF do contato (quando informado).');
  setCliente('bloco1_site', c.site, 'Site da empresa no cadastro.');
  setCliente(
    'bloco1_data_inicio_operacao',
    loc.data_inicio_operacao,
    'Inicio de operacao informado no perfil do cliente.',
  );
  setCliente('bloco1_ebitda', eco.ebitda, 'EBITDA informado no perfil economico do cliente.');
  setCliente(
    'bloco1_parte_grupo_economico',
    eco.grupo_economico,
    'Grupo economico declarado no cadastro.',
  );
  setCliente(
    'bloco1_principais_atividades',
    c.descricao_projeto || c.perfilTecnologico?.principais_atividades,
    'Principais atividades do cadastro.',
  );

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

  const diag = c.diagnosticoConsultor || c.perfilConsultivo?.diagnostico_consultor || {};
  const tecPerfil = c.perfilTecnologico || c.perfilConsultivo?.perfil_tecnologico || {};

  if (hasText(tecPerfil.descricao_projeto) && canWrite('bloco1_principais_atividades')) {
    const empty = !hasText(form.bloco1_principais_atividades);
    if (!onlyFillEmpty || empty) {
      form.bloco1_principais_atividades = String(tecPerfil.descricao_projeto).trim();
      fieldIntel.bloco1_principais_atividades = intelEntry(
        SOURCE_CLIENTE,
        CONF_HIGH,
        'Projeto/necessidade informados no briefing consultivo do cliente.',
        true,
      );
      autogerados.push('bloco1_principais_atividades');
    }
  }

  if (hasText(diag.contexto_cliente) && canWrite('bloco1_principais_atividades')) {
    const cur = form.bloco1_principais_atividades;
    const ctx = String(diag.contexto_cliente).trim();
    const empty = !hasText(cur);
    if ((!onlyFillEmpty || empty) && !cur.includes(ctx.slice(0, 40))) {
      form.bloco1_principais_atividades = hasText(cur) ? `${cur}\n\nContexto: ${ctx}` : ctx;
      fieldIntel.bloco1_principais_atividades = intelEntry(
        SOURCE_CLIENTE,
        CONF_MEDIUM,
        'Contexto do cliente (briefing consultivo).',
        true,
      );
    }
  }

  if (hasText(diag.observacoes_internas) && canWrite('bloco_estr_obs_internas')) {
    const empty = !hasText(form.bloco_estr_obs_internas);
    if (!onlyFillEmpty || empty) {
      form.bloco_estr_obs_internas = String(diag.observacoes_internas).trim();
      fieldIntel.bloco_estr_obs_internas = intelEntry(
        SOURCE_CLIENTE,
        CONF_MEDIUM,
        'Observações internas do consultor (briefing).',
        false,
      );
      autogerados.push('bloco_estr_obs_internas');
    }
  }

  const temasBrief =
    tecPerfil.temas_prioritarios || tecPerfil.areas_tecnologicas || c.interesse_temas || c.area_inovacao;
  if (hasText(temasBrief) && canWrite('bloco_estr_principais_aderencias')) {
    const empty = !hasText(form.bloco_estr_principais_aderencias);
    if (!onlyFillEmpty || empty) {
      form.bloco_estr_principais_aderencias = `Temas prioritários (briefing): ${String(temasBrief).trim()}`;
      fieldIntel.bloco_estr_principais_aderencias = intelEntry(
        SOURCE_CLIENTE,
        CONF_MEDIUM,
        'Temas/áreas do briefing consultivo.',
        true,
      );
    }
  }

  const prefTipos = c.preferencias_fomento_tipos || c.preferenciasFomento?.tipos_recurso;
  if (Array.isArray(prefTipos) && prefTipos.length && canWrite('bloco_estr_tipo_recurso_pdf')) {
    const labels = prefTipos.join(', ');
    const empty = !hasText(form.bloco_estr_tipo_recurso_pdf);
    if (!onlyFillEmpty || empty) {
      form.bloco_estr_tipo_recurso_pdf = labels;
      fieldIntel.bloco_estr_tipo_recurso_pdf = intelEntry(
        SOURCE_CLIENTE,
        CONF_MEDIUM,
        'Tipos de recurso indicados no briefing.',
        true,
      );
    }
  }

  if (hasText(diag.lacunas) && canWrite('bloco_estr_lacunas')) {
    const empty = !hasText(form.bloco_estr_lacunas);
    if (!onlyFillEmpty || empty) {
      form.bloco_estr_lacunas = String(diag.lacunas).trim();
      fieldIntel.bloco_estr_lacunas = intelEntry(
        SOURCE_CLIENTE,
        CONF_MEDIUM,
        'Lacunas registradas no perfil consultivo do cliente.',
        true,
      );
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

  /** ---- Meta oportunidade (edital) ---- */
  if (e) {
    const meta = formatOportunidadeMeta(e, radarMatch);
    if (meta.fonte) {
      assign('bloco_estr_oportunidade_fonte', meta.fonte, {
        source: SOURCE_EDITAL,
        confidence: CONF_HIGH,
        explanation: 'Fonte/orgao informado na ficha da oportunidade.',
        needsReview: false,
      });
    }
    if (meta.prazo) {
      assign('bloco_estr_oportunidade_prazo', meta.prazo, {
        source: SOURCE_EDITAL,
        confidence: CONF_HIGH,
        explanation: 'Prazo informado na oportunidade — confirmar no portal oficial.',
        needsReview: true,
      });
    }
    if (meta.link) {
      assign('bloco_estr_oportunidade_link', meta.link, {
        source: SOURCE_EDITAL,
        confidence: CONF_MEDIUM,
        explanation: 'Link da oportunidade na base — validar se ainda esta ativo.',
        needsReview: true,
      });
    }
  }

  /** ---- C) Radar ---- */
  if (radarMatch) {
    const scoreLbl = formatScoreCompatLabel(radarMatch);
    if (scoreLbl) {
      assign('bloco_estr_score_compatibilidade', scoreLbl, {
        source: SOURCE_RADAR,
        confidence: CONF_MEDIUM,
        explanation: 'Referencia de compatibilidade do Radar (nao altera o score).',
        needsReview: true,
      });
    }
    const alertas = collectRadarAlerts(radarUse);
    if (alertas.length) {
      assign('bloco_estr_alertas_radar', alertas.map((a) => `• ${a}`).join('\n'), {
        source: SOURCE_RADAR,
        confidence: CONF_MEDIUM,
        explanation: 'Alertas e penalidades reportados pelo Radar.',
        needsReview: true,
      });
    }
    if (typeof radarUse.scorePct === 'number' && canWrite('bloco_estr_aderencia_nivel')) {
      const lbl =
        radarUse.scorePct >= 70 ? 'alta' : radarUse.scorePct >= 40 ? 'media' : 'baixa';
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
    const razoes = collectRadarPositiveReasons(radarUse);
    const explRadar = razoes.slice(0, 4).join('\n• ');
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
  const sug = buildProjectSuggestions(c, e || (editalTitulo ? { titulo: editalTitulo } : null), radarUse);
  const sectorKey = classifySectorKey(c);
  const titTpl = suggestTituloProjeto(c, editalTitulo, sectorKey);
  const resTpl = suggestResumoPublicavel(c, e, radarMatch, sectorKey);
  const probTpl = suggestProblemaOportunidade(c);
  const solTpl = suggestSolucaoProposta(c, sectorKey);
  const objTpl = suggestObjetivoGeral(c, e, radarUse);
  const fin = suggestFinalidadesBlocos(c, sectorKey);

  const pushAuto = (key, val, expl, conf = CONF_MEDIUM) =>
    assign(key, val, { source: SOURCE_AUTO, confidence: conf, explanation: expl, needsReview: true });

  pushAuto('bloco2_titulo_projeto', titTpl.texto, titTpl.explanation);
  pushAuto('bloco2_resumo_publicavel', resTpl.texto, resTpl.explanation);
  const execConsultor =
    multiList.length > 0 && primary
      ? buildMultiExecutiveSummary(c, multiList, primary)
      : buildConsultorExecutiveSummary(c, e, radarUse);
  pushAuto(
    'bloco_estr_resumo_executivo',
    execConsultor || resTpl.texto,
    multiList.length > 1
      ? 'Resumo executivo com estrategia multi-oportunidade.'
      : 'Resumo executivo consultivo (cliente + oportunidade + proximos passos de validacao).',
  );
  pushAuto(
    'bloco_estr_motivo_recomendacao',
    multiList.length > 0 && primary
      ? buildMultiFitNarrative(c, multiList, primary, related)
      : buildConsultorFitNarrative(c, e, radarUse),
    multiList.length > 1
      ? 'Aderencia consolidada das oportunidades selecionadas.'
      : 'Narrativa de aderencia em linguagem consultiva (cadastro, edital e Radar).',
  );
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
  const docsStruct = buildStructuredDocumentsChecklist(c, e, radarMatch);
  pushAuto('bloco_estr_docs_cliente', docsStruct.cliente, 'Checklist documentos do cliente.');
  pushAuto('bloco_estr_docs_tecnicos', docsStruct.tecnicos, 'Checklist documentos tecnicos.');
  pushAuto('bloco_estr_docs_financeiros', docsStruct.financeiros, 'Checklist documentos financeiros/juridicos.');
  pushAuto('bloco_estr_docs_edital_regulamento', docsStruct.edital, 'Checklist documentos do edital/regulamento.');
  pushAuto('bloco_estr_docs_recomendados', docsStruct.agregado, 'Visao agregada dos documentos (compativel com campo legado).');
  pushAuto(
    'bloco_estr_proximos_passos',
    multiList.length > 1 && primary
      ? buildMultiNextSteps(multiList, primary)
      : buildConsultorNextSteps(c, e) || sug.proximosPassos,
    'Proximos passos consultivos.',
  );
  pushAuto(
    'bloco_estr_riscos_pendencias',
    multiList.length > 1 ? buildMultiRisks(c, multiList) : buildConsultorRisks(c, e, radarUse),
    'Riscos e pendencias identificados automaticamente.',
  );
  pushAuto('bloco_estr_checklist_inicial', buildInitialChecklist(c, e, radarUse), 'Checklist inicial para acompanhamento com o cliente.');
  pushAuto('bloco_estr_plano_trabalho', buildConsultorWorkPlan(c, e), 'Plano de trabalho preliminar em fases.');
  pushAuto(
    'bloco_estr_orcamento_resumo',
    multiList.length > 1 && primary
      ? buildMultiBudget(primary, multiList)
      : buildConsultorBudgetSummary(c, e),
    'Resumo financeiro preliminar.',
  );
  pushAuto('bloco_estr_orcamento_categorias', buildBudgetCategoriesHint(), 'Categorias sugeridas de gasto para detalhar orcamento.');
  if (e?.contrapartida != null && e.contrapartida !== '') {
    pushAuto('bloco_estr_orcamento_contrapartida', String(e.contrapartida), 'Contrapartida citada na ficha da oportunidade.');
  }
  pushAuto(
    'bloco_estr_orcamento_observacoes',
    'Revisar orcamento com o cliente e anexar planilha detalhada antes da submissao. Valores finais dependem do regulamento do edital.',
    'Observacoes financeiras orientativas.',
  );
  if (!hasText(form.bloco_estr_pendencias)) {
    pushAuto(
      'bloco_estr_pendencias',
      multiList.length > 1 ? buildMultiRisks(c, multiList) : buildConsultorRisks(c, e, radarUse),
      'Pendencias criticas espelhadas na secao de riscos.',
    );
  }

  if (multiList.length > 0 && primary) {
    pushAuto(
      'bloco_estr_oportunidades_selecionadas',
      serializeOportunidadesSelecionadas(multiList, primary.key),
      'JSON leve das oportunidades selecionadas (armazenamento local).',
    );
    pushAuto(
      'bloco_estr_edital_ref_titulo',
      multiList.length > 1
        ? `${tituloCurto(primary.titulo)} (+ ${multiList.length - 1} complementar${multiList.length > 2 ? 'es' : ''})`
        : primary.titulo,
      'Titulo da oportunidade principal no conjunto selecionado.',
    );
    if (canWrite('bloco_estr_oportunidade_fonte') && primary.fonte_recurso) {
      assign('bloco_estr_oportunidade_fonte', primary.fonte_recurso, {
        source: SOURCE_EDITAL,
        confidence: CONF_HIGH,
        explanation: 'Fonte da oportunidade principal.',
        needsReview: false,
      });
    }
  }

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

  logPrecadastro('draft_autofill_success', {
    autogerados_count: autogerados.length,
    pendencias_count: pendencias.length,
    edital_titulo: editalTitulo || null,
  });

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
