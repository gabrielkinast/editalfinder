import { computeCompletion, buildProjectSuggestions, buildProjectSummary } from '../../utils/precadastro/projectIntel';
import { calculatePreCadastroCompleteness } from '../../utils/precadastro/calculatePreCadastroCompleteness.js';
import {
  stripUnsafePdfChars,
  valEssential,
  valExecutive,
  valOptional,
  isNaoInformado,
  LABEL_NAO_INFORMADO,
} from './pdfFormatters';
import { clienteEnrichedForApps } from '../../utils/cliente/clientePerfilConsultivo';
import { partitionSelectedOpportunities, pickPrimaryOpportunity } from '../../utils/consultor/opportunitySelection';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function moneyRange(c) {
  const min = c?.interesse_valor_min;
  const max = c?.interesse_valor_max;
  if ((min == null || min === '') && (max == null || max === '')) return null;
  if (Number(min) > 0 && Number(max) > 0)
    return `Faixa declarada: R$ ${Number(min).toLocaleString('pt-BR')} a R$ ${Number(max).toLocaleString('pt-BR')}`;
  if (Number(max) > 0) return `Ate R$ ${Number(max).toLocaleString('pt-BR')}`;
  return null;
}

/**
 * @param {{
 *   cliente?: object | null;
 *   edital?: { titulo?: string; fonte_recurso?: string; tipo_recurso?: string; tipo_oportunidade?: string; valor_maximo?: string; prazo_envio?: string } | null;
 *   radarMatch?: { tituloEdital?: string; scorePct?: number } | null;
 *   formData: Record<string, unknown>;
 * }} input
 */
export function buildPreCadastroPdfModel({ cliente = null, edital = null, radarMatch = null, formData = {} }) {
  const c = clienteEnrichedForApps(cliente || {});
  const f = formData || {};
  const sug = buildProjectSuggestions(c, edital, radarMatch);
  const completion = computeCompletion(f);
  const fullComplete = calculatePreCadastroCompleteness(f);

  const editalTitulo = f.bloco_estr_edital_ref_titulo || edital?.titulo || radarMatch?.tituloEdital || '';

  const empresaNome = stripUnsafePdfChars(c.nome_empresa || c.razao_social || f.bloco1_nome_fantasia || 'Cliente');

  const linhaPrincipalSel = !!f.bloco1_linha_credito_principal;
  const linhaTelecomSel = !!f.bloco1_linha_credito_telecom;
  const linhaReco = sug.linhaRecomendadaLabel;

  const linhasAlt = [];
  if (linhaPrincipalSel) linhasAlt.push({ nome: 'Linha principal (credito inovacao - produto institucional)', tipo: 'principal', sel: true, badge: sug.linhasMeta.principal.badge });
  else linhasAlt.push({ nome: 'Linha principal (credito inovacao)', tipo: 'principal', sel: false, badge: sug.linhasMeta.principal.badge });
  if (linhaTelecomSel) linhasAlt.push({ nome: 'Linha com aderencia a telecomunicacoes', tipo: 'telecom', sel: true, badge: sug.linhasMeta.telecom.badge });
  else linhasAlt.push({ nome: 'Linha telecomunicacoes', tipo: 'telecom', sel: false, badge: sug.linhasMeta.telecom.badge });

  const tipoRecurso =
    valOptional(edital?.tipo_recurso) ||
    valOptional(f.bloco_estr_tipo_recurso_pdf) ||
    (editalTitulo ? 'A definir conforme edital' : 'Cadastro geral / multiplas linhas');

  const fonteOrgao =
    valOptional(edital?.fonte_recurso) || valOptional(c.regiao) || (editalTitulo ? 'Conforme regulamento do edital' : null);

  const perfilIdealHint = stripUnsafePdfChars(
    [c.interesse_temas, c.area_inovacao].filter(Boolean).join(' | '),
  );

  const radarBadge =
    typeof radarMatch?.scorePct === 'number'
      ? `Radar: aderencia estimada ${Math.round(radarMatch.scorePct)}%`
      : editalTitulo
        ? 'Aderencia orientada ao perfil do cadastro'
        : null;

  const intro =
    `Este relatorio consolida as informacoes iniciais da empresa ${empresaNome} para avaliacao de aderencia ` +
    `a linhas de fomento, credito ou editais de inovacao. Os campos foram pre-preenchidos com base no cadastro ` +
    `do cliente e podem ser complementados pela equipe responsavel.`;

  const pendenciasCliente = [];

  function execRow(label, rawValue) {
    const value = valExecutive(rawValue);
    if (value == null) {
      pendenciasCliente.push(`${label} a completar com o cliente.`);
      return null;
    }
    return { label, value, essential: true };
  }

  const executiveRows = [
    execRow('Empresa', empresaNome),
    execRow('Setor', f.bloco1_setor_empresa || c.setor),
    execRow('Porte', f.bloco1_porte_empresa || c.porte_empresa),
    execRow(
      'Localizacao',
      [f.bloco1_municipio || c.cidade, (f.bloco1_uf || c.estado || '').toString().toUpperCase()]
        .filter(Boolean)
        .join(' / '),
    ),
    execRow('Linha / produto destacado', linhaReco),
    execRow('Tipo de recurso (referencia)', tipoRecurso),
    execRow('Valor de interesse', moneyRange(c) || f.bloco2_recursos_adicionais_valor),
    execRow(
      'Prazo / limite (referencia)',
      valOptional(edital?.prazo_envio) ||
        (Array.isArray(f.bloco2_metas_fisicas) &&
          f.bloco2_metas_fisicas.map((r) => r?.fim).filter(Boolean)[0]),
    ),
    execRow('Principais pontos de aderencia', f.bloco_estr_principais_aderencias || sug.principaisAderencias),
    execRow('Pendencias principais', f.bloco_estr_pontos_complementar || f.bloco_estr_pendencias || sug.pontosComplementar),
  ].filter(Boolean);

  /** Geracao de pendencias criticas */
  const alertasEssenciais = [];
  if (!hasText(f.bloco1_cnpj)) alertasEssenciais.push('CNPJ nao informado no formulario.');
  if (!hasText(f.bloco1_razao_social) && !hasText(c.razao_social)) alertasEssenciais.push('Razao social nao informada.');
  if (!hasText(f.bloco2_resumo_publicavel) && !hasText(f.bloco_estr_resumo_executivo)) alertasEssenciais.push('Resumo do projeto ainda pendente.');
  if (!hasText(f.bloco1_email_contato)) alertasEssenciais.push('E-mail de contato nao informado.');
  if (completion.score < 70) alertasEssenciais.push(`Completude do formulario: ${completion.score}% (${completion.level}).`);
  if (fullComplete.requiredMissing.length)
    alertasEssenciais.push(
      `Itens obrigatorios pendentes (assistente): ${fullComplete.requiredMissing.slice(0, 14).join('; ')}`,
    );

  const autoAderenciaBullets = [];
  if (normSetor(c.setor, edital)) {
    autoAderenciaBullets.push(
      'Perfil setorial compativel com linhas de inovacao e desenvolvimento tecnologico (cadastro).',
    );
  }
  if (String(edital?.tipo_recurso || '').toLowerCase().includes('cred') || String(tipoRecurso).toLowerCase().includes('cred')) {
    autoAderenciaBullets.push(
      'Oportunidade com caracteristica de credito/financiamento: avaliar garantias, contrapartida e capacidade de pagamento.',
    );
  }

  function consultorPair(label, raw) {
    const value = valExecutive(raw);
    if (value == null) {
      pendenciasCliente.push(`${label} a completar com o cliente.`);
      return null;
    }
    return [label, value];
  }

  const consultorSections = [
    consultorPair('Resumo executivo', f.bloco_estr_resumo_executivo || f.bloco2_resumo_publicavel || intro),
    consultorPair('Aderencia ao edital', f.bloco_estr_motivo_recomendacao || sug.motivoRecomendacao),
    consultorPair(
      'Escopo inicial',
      [f.bloco_estr_problema_oportunidade, f.bloco_estr_solucao_proposta, f.bloco_estr_diferencial_inovador]
        .filter((x) => hasText(x))
        .join('\n\n'),
    ),
    consultorPair('Plano de trabalho', f.bloco_estr_plano_trabalho),
    consultorPair(
      'Orcamento preliminar',
      f.bloco_estr_orcamento_resumo || f.bloco2_recursos_adicionais_valor || moneyRange(c),
    ),
    consultorPair(
      'Documentos necessarios',
      f.bloco_estr_docs_recomendados ||
        [f.bloco_estr_docs_cliente, f.bloco_estr_docs_tecnicos, f.bloco_estr_docs_financeiros]
          .filter((x) => hasText(x))
          .join('\n'),
    ),
    consultorPair('Riscos e pendencias', f.bloco_estr_riscos_pendencias || f.bloco_estr_lacunas),
    consultorPair('Proximos passos', f.bloco_estr_proximos_passos || sug.proximosPassos),
  ].filter(Boolean);

  const oportunidadesPdf = buildOportunidadesPdfTable(f.bloco_estr_oportunidades_selecionadas);

  const pendenciasSecao = [
    ...pendenciasCliente,
    ...alertasEssenciais,
  ];
  if (!hasText(f.bloco2_compromiso_social) && !hasText(f.bloco2_imp_eco_outros_txt)) {
    /* nao forca - opcional */
  }

  return {
    meta: {
      clientName: empresaNome,
      stem: `precadastro-projeto_${empresaNome.replace(/[^\wÀ-ú\- ]/gi, '_').slice(0, 48)}`,
      dataGerado: new Date().toLocaleString('pt-BR'),
      dataFilename: new Date().toISOString().split('T')[0],
    },
    cover: {
      tituloPrincipal: 'Relatorio preliminar de oportunidades de fomento',
      subtituloDoc: 'Pre-enquadramento consultivo para tomada de decisao',
      empresa: empresaNome,
      editalOuLinha: editalTitulo || 'Nenhum edital especifico associado (pre-cadastro geral)',
      dataGeracao: new Date().toLocaleString('pt-BR'),
      statusCompletude: `${completion.level} (${completion.score}%)`,
      radarBadge,
      intro,
    },
    executiveCard: {
      intro,
      linhas: executiveRows,
    },
    consultorSections,
    oportunidadesPdf,
    pendenciasCliente,
    enquadramento: {
      linhas: linhasAlt,
      editalTitulo: editalTitulo || null,
      fonteOrgao: fonteOrgao || 'Nao informado',
      tipoOportunidade: valOptional(edital?.tipo_oportunidade) || 'Nao informado',
      tipoRecurso: valEssential(tipoRecurso),
      perfilIdeal: valEssential(perfilIdealHint || sug.principaisAderencias),
      requisitosResumo: valEssential(f.bloco_estr_requisitos_atendidos || sug.requisitosAtendidos),
      aderenciaEstimada: stripUnsafePdfChars(f.bloco_estr_aderencia_nivel || sug.aderenciaNivel),
      motivoRecomendacao: valEssential(f.bloco_estr_motivo_recomendacao || sug.motivoRecomendacao),
      autoBullets: autoAderenciaBullets,
      proximosPassos: valEssential(f.bloco_estr_proximos_passos || sug.proximosPassos),
    },
    empresa: {
      cnpj: valEssential(f.bloco1_cnpj || c.cnpj),
      razao: valEssential(f.bloco1_razao_social || c.razao_social),
      fantasia: valEssential(f.bloco1_nome_fantasia || c.nome_empresa),
      dataConst: valEssential(f.bloco1_data_constituicao || c.data_abertura),
      inicioOp: valEssential(f.bloco1_data_inicio_operacao),
      sede: {
        logradouro: valEssential(f.bloco1_logradouro),
        numero: valOptional(f.bloco1_numero),
        complemento: valOptional(f.bloco1_complemento),
        bairro: valOptional(f.bloco1_bairro),
        municipio: valEssential(f.bloco1_municipio || c.cidade),
        uf: valEssential((f.bloco1_uf || c.estado || '').toString().toUpperCase()),
        cep: valOptional(f.bloco1_cep),
      },
      site: valOptional(f.bloco1_site),
      contato: {
        nome: valEssential(f.bloco1_nome_contato),
        cpf: valOptional(f.bloco1_cpf_contato),
        cargo: valOptional(f.bloco1_cargo_contato),
        email: valEssential(f.bloco1_email_contato),
        telefone: valOptional(f.bloco1_telefone_contato),
      },
    },
    economicoLinhas: buildEconomicoLinhasPdf(c, f),
    economicoEmptyMessage: 'Dados economicos ainda nao informados.',
    projeto: {
      titulo: valEssential(f.bloco2_titulo_projeto),
      resumoPublicavel: valEssential(f.bloco2_resumo_publicavel || f.bloco_estr_resumo_executivo || buildProjectSummary(c, edital, radarMatch)),
      problema: valEssential(f.bloco_estr_problema_oportunidade || f.bloco2_finalidade_a),
      objetivo: valEssential(f.bloco_estr_objetivo_geral || f.bloco2_finalidade_b),
      solucao: valEssential(f.bloco_estr_solucao_proposta),
      aplicacao: valEssential(f.bloco2_finalidade_b || f.bloco_estr_publico_mercado),
      desafiosTec: valEssential(f.bloco2_finalidade_c),
      ict: valEssential(f.bloco2_finalidade_d),
      resultados: valEssential(f.bloco_estr_resultados_esperados || f.bloco2_finalidade_e),
      concorrentes: valEssential(f.bloco2_finalidade_f),
      diferencial: valEssential(f.bloco_estr_diferencial_inovador),
      produtoProcessoServico: valEssential(f.bloco2_finalidade_g),
      comentarios: valOptional(f.bloco2_comentarios_adicionais),
      cnaeProjeto: valOptional(f.bloco2_cnae_projeto),
      ufProjeto: valOptional(f.bloco2_uf_projeto),
    },
    innovacion: {
      infra: valOptional(f.bloco1_pdi_infraestrutura),
      equipe: valOptional(f.bloco1_pdi_detalhe_pessoas),
      parIctSim: valOptional(f.bloco1_pdi_parceria_ict_sim),
      parIctTxt: valOptional(f.bloco1_pdi_parceria_ict_txt),
      parEmpSim: valOptional(f.bloco1_pdi_parceria_empresas_sim),
      parEmpTxt: valOptional(f.bloco1_pdi_parceria_empresas_txt),
      piSim: valOptional(f.bloco1_pdi_pi_3anos_sim),
      piTxt: valOptional(f.bloco1_pdi_pi_3anos_txt),
      contratos: valOptional(f.bloco1_pdi_contratos_inpi_sim),
      contratosTxt: valOptional(f.bloco1_pdi_contratos_inpi_txt),
      outrasAg: valOptional(f.bloco1_pdi_outras_agencias_sim),
      outrasAgTxt: valOptional(f.bloco1_pdi_outras_agencias_txt),
      checks: [
        ['Novo produto', !!f.bloco2_tp_inov_novo_produto],
        ['Novo processo', !!f.bloco2_tp_inov_novo_processo],
        ['Melhoria significativa de produto', !!f.bloco2_tp_inov_melhoria_produto],
        ['Melhoria significativa de processo', !!f.bloco2_tp_inov_melhoria_processo],
        ['Inovacao nivel empresa', !!f.bloco2_nivel_empresa],
        ['Inovacao nivel regiao', !!f.bloco2_nivel_regiao],
        ['Inovacao nivel Brasil', !!f.bloco2_nivel_brasil],
        ['Inovacao nivel mundo', !!f.bloco2_nivel_mundo],
      ],
      aspectosSim: valOptional(f.bloco2_aspectos_regulatorios_sim),
      aspectosTxt: valOptional(f.bloco2_aspectos_regulatorios_txt),
      rowsOpcional: filterOptionalRows([
        ['Infraestrutura PD&I', valOptional(f.bloco1_pdi_infraestrutura)],
        ['Equipe / pessoas (ref.)', valOptional(f.bloco1_pdi_detalhe_pessoas)],
        ['Parceria ICT', valOptional(`${f.bloco1_pdi_parceria_ict_sim || ''} ${f.bloco1_pdi_parceria_ict_txt || ''}`.trim())],
        ['Parcerias empresas', valOptional(`${f.bloco1_pdi_parceria_empresas_sim || ''} ${f.bloco1_pdi_parceria_empresas_txt || ''}`.trim())],
        ['PI / registros recentes', valOptional(`${f.bloco1_pdi_pi_3anos_sim || ''} ${f.bloco1_pdi_pi_3anos_txt || ''}`.trim())],
      ]),
    },
    usosFontes: buildUsosFontes(f.bloco2_uso_fontes),
    impacts: null, /** preenchido no render a partir das constantes + form */
    licencas: {
      texto: valEssential(f.bloco2_licencas),
      aspectos: valEssential(f.bloco2_aspectos_regulatorios_txt || f.bloco2_aspectos_regulatorios_sim),
      obs: valOptional(f.bloco2_justifica_import_obs),
    },
    condiciones: {
      pctIcts: valOptional(f.bloco2_pct_icts),
      recursosAdicionais: valOptional(`${f.bloco2_recursos_adicionais_sim || ''} ${f.bloco2_recursos_adicionais_valor || ''}`.trim()),
      importacaoChecks: [
        ['Nao similar nacional (importacao)', !!f.bloco2_justifica_import_naosimilar],
        ['Importacao por qualidade superior', !!f.bloco2_justifica_import_qualidade],
        ['Importacao por preco inferior', !!f.bloco2_justifica_import_preco],
        ['Projeto sem equipamentos importados', !!f.bloco2_justifica_sem_importados],
      ],
      compromissoSocial: valOptional(f.bloco2_compromiso_social),
      cronogramaResumo:
        Array.isArray(f.bloco2_metas_fisicas) &&
        f.bloco2_metas_fisicas.some((x) => hasText(x?.ini) || hasText(x?.fim))
          ? f.bloco2_metas_fisicas.map((x) => [x.ini, x.fim].filter(Boolean).join(' -> ')).filter(Boolean)[0]
          : null,
    },
    declaracao: {
      texto: hasText(f.bloco_estr_declaracao_custom)
        ? stripUnsafePdfChars(f.bloco_estr_declaracao_custom)
        : 'Declaro que as informacoes apresentadas neste pre-cadastro refletem os dados disponiveis no momento da geracao do relatorio e poderao ser complementadas para submissao formal ao edital ou linha de fomento.',
      localData: `[Local] ${new Date().toLocaleDateString('pt-BR')}`,
      responsavel:
        hasText(f.bloco1_nome_contato) ? stripUnsafePdfChars(f.bloco1_nome_contato) : LABEL_NAO_INFORMADO,
      cargo:
        hasText(f.bloco1_cargo_contato)
          ? stripUnsafePdfChars(f.bloco1_cargo_contato)
          : LABEL_NAO_INFORMADO,
    },
    pendenciasLista: pendenciasSecao.length ? pendenciasSecao : ['Nenhuma pendencia critica automatica detectada.'],
    alertasEssenciais,
    projetoResumoGerado: buildProjectSummary(c, edital, radarMatch),
    completion,
    rawForm: f,
    rodapeTituloCurto: 'Relatorio preliminar de fomento',
  };
}

function parseOportunidadesJson(raw) {
  if (!raw || !String(raw).trim()) return [];
  try {
    const j = JSON.parse(raw);
    return Array.isArray(j) ? j : [];
  } catch {
    return [];
  }
}

function buildOportunidadesPdfTable(rawJson) {
  const list = parseOportunidadesJson(rawJson).map((o) => ({
    key: o.key,
    titulo: o.titulo || 'Oportunidade',
    scorePct: o.score ?? o.scorePct,
    compatibilidade: o.compatibilidade,
    fonte_recurso: o.fonte_recurso,
    prazo_envio: o.prazo ?? o.prazo_envio,
    link: o.link,
  }));
  if (!list.length) return { hasRows: false, principal: [], complementares: [], observacao: [] };

  const primary = pickPrimaryOpportunity(list, list.find((o) => o.principal)?.key);
  const part = partitionSelectedOpportunities(list, primary);

  const rowPdf = (o) => [
    stripUnsafePdfChars(o.titulo || '—'),
    `${o.scorePct ?? '—'}%`,
    stripUnsafePdfChars(o.compatibilidade || '—'),
    stripUnsafePdfChars(o.fonte_recurso || '—'),
    stripUnsafePdfChars(o.prazo_envio || '—'),
  ];

  return {
    hasRows: true,
    principal: part.primary ? [rowPdf(part.primary)] : [],
    complementares: part.complementares.map(rowPdf),
    observacao: part.observacao.map(rowPdf),
  };
}

function normSetor(setor, edital) {
  const s = `${setor || ''}`.toLowerCase();
  const e = `${edital?.titulo || ''}`.toLowerCase();
  return /tecnolog|inov|digital|software|ict/i.test(s) || /tecnolog|inov|digital/i.test(e);
}

function filterOptionalRows(rows) {
  return rows.filter(([, val]) => val != null && String(val).trim() !== '');
}

function buildEconomicoLinhasPdf(c, f) {
  const eco = c.dadosEconomicos || {};
  const candidates = [
    ['CNAE principal', valExecutive(f.bloco1_cnae || c.cnae_principal)],
    [
      'Receita operacional (ultimo exercicio)',
      valExecutive(f.bloco1_receita_rob_ultimo || c.faturamento_anual),
    ],
    ['EBITDA', valExecutive(f.bloco1_ebitda || eco.ebitda)],
    ['Total empregados (quadro)', valExecutive(f.bloco1_total_empregados || c.numero_funcionarios)],
    ['Grupo economico', valExecutive(f.bloco1_parte_grupo_economico || eco.grupo_economico)],
    ['Faixa de faturamento', valExecutive(eco.faixa_faturamento)],
    ['Capacidade de contrapartida', valExecutive(eco.contrapartida_capacidade)],
    ...filterOptionalRows([
      ['Faturamento grupo', valOptional(f.bloco1_faturamento_grupo)],
      ['Data referencia receita/EBITDA', valOptional(f.bloco1_data_ref_receita)],
      ['Principais atividades', valExecutive(f.bloco1_principais_atividades || c.descricao_projeto)],
    ]),
  ];
  return candidates.filter(([, val]) => val != null && !isNaoInformado(val));
}

function buildUsosFontes(listaRaw) {
  const padrao = [
    { item: 'Obras civis / instalacoes', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Equipamentos nacionais', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Equipamentos importados', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Software / licencas', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Materias-primas / consumo', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Equipe propria / RH direto', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Treinamentos', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Consultoria / STT', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Viagens / diarias', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
    { item: 'Outros', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' },
  ];

  const lista = Array.isArray(listaRaw) ? listaRaw : [];
  const temValor = lista.some((r) => r && Object.values(r).some((v) => hasText(v)));
  if (!temValor) {
    return {
      empty: true,
      rows: padrao,
      message: 'Orcamento preliminar ainda nao preenchido.',
    };
  }

  /** Mescla primeiro as linhas do usuario, limita linhas extras */
  const merged = [...lista.map((r) => ({
    item: stripUnsafePdfChars(r?.item || ''),
    lib1: stripUnsafePdfChars(r?.lib1 || ''),
    lib2: stripUnsafePdfChars(r?.lib2 || ''),
    libN: stripUnsafePdfChars(r?.libN || ''),
    totalFin: stripUnsafePdfChars(r?.totalFin || ''),
    contrapartida: stripUnsafePdfChars(r?.contrapartida || ''),
  }))];
  while (merged.length < 10) merged.push({ item: '', lib1: '', lib2: '', libN: '', totalFin: '', contrapartida: '' });

  return { empty: false, rows: merged.slice(0, 22) };
}
