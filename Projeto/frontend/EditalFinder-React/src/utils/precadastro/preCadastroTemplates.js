/**
 * Templates locais (sem API externa) — linguagem cautelosa, sem afirmar detalhes inexistentes.
 */

function norm(s) {
  return String(s ?? '')
    .trim()
    .toLowerCase();
}

/**
 * Agrupa texto cadastrado para classificar setor de apoio a sugestões.
 * @returns {string} chave interna (tecnologia, industria, agro, energia, saude, educacao, comercio_servicos, defesa, outros)
 */
export function classifySectorKey(cliente) {
  const s = norm(
    `${cliente?.setor || ''} ${cliente?.area_inovacao || ''} ${cliente?.interesse_temas || ''} ${cliente?.nome_empresa || ''}`,
  );
  const tests = [
    [/tecnolog|software|digital|ict|ti\b|inform[aá]tic|saas|hardware/, 'tecnologia'],
    [/ind[úu]stri|manufatur|metal|automot|automacao/, 'industria'],
    [/agro|agroneg|campo|rural/, 'agro'],
    [/energ|petr[oó]leo|oil|gas|el[eé]tric|utility/, 'energia'],
    [/sa[uú]de|hospital|cl[ií]nic|medic|farma/, 'saude'],
    [/educa|capacita|ensino/, 'educacao'],
    [/defesa|milit/, 'defesa'],
    [/aeron[aá]ut|aeroespac/, 'aeroespacial'],
    [/nuclear/, 'nuclear'],
    [/sustent[aá]|esg/, 'sustentabilidade'],
    [/com[eé]rcio|varejo|servi[cç]/, 'comercio_servicos'],
  ];
  for (const [re, k] of tests) {
    if (re.test(s)) return k;
  }
  return 'outros';
}

/**
 * Exemplos orientativos de impactos (não marca checkboxes automaticamente).
 * @returns {{ economicos: string[]; sociais: string[]; ambientais: string[] }}
 */
export function hintImpactsForSector(sectorKey) {
  const map = {
    tecnologia: {
      economicos: ['automacao/digitalizacao', 'eficiencia de processos', 'novos mercados'],
      sociais: ['capacitação relacionada ao uso das solucoes'],
      ambientais: ['economia digital pode reduzir desperdício de papel/transporte (avaliar caso a caso)'],
    },
    agro: {
      economicos: ['produtividade', 'menor desperdício na cadeia'],
      sociais: ['geracao de ocupacao na cadeia (quando aplicavel)'],
      ambientais: ['uso mais eficiente de insumos e agua'],
    },
    energia: {
      economicos: ['eficiencia operacional'],
      sociais: ['acesso a infraestrutura (quando aplicavel)'],
      ambientais: ['reducao de emissões / eficiência energética'],
    },
    saude: {
      economicos: ['qualidade e produtividade de processos'],
      sociais: ['melhoria de acesso ou qualidade (depende da proposta)'],
      ambientais: ['melhor uso de recursos/evitar desperdicio'],
    },
    educacao: {
      economicos: ['capacidade de entrega/formatos escalaveis'],
      sociais: ['educação e inclusão'],
      ambientais: ['formatos menos impactantes quando digitais forem opcao'],
    },
    industria: {
      economicos: ['qualidade automacao producao capacidade'],
      sociais: ['ambiente laboral seguranca'],
      ambientais: ['consumo materiais eficiência'],
    },
    comercio_servicos: {
      economicos: ['competividade receita modelo de negócio'],
      sociais: ['acesso inclusao trabalho formal'],
      ambientais: ['logistica menor impacto quando couber'],
    },
    outros: {
      economicos: ['competividade e eficiencia'],
      sociais: ['efeitos socioeconomicos esperados pela proposta'],
      ambientais: ['efeitos ambientais quando pertinentes ao escopo'],
    },
  };

  const o = map[sectorKey] || map.outros;
  if (sectorKey === 'defesa' || sectorKey === 'aeroespacial' || sectorKey === 'nuclear')
    return {
      economicos: ['desenvolvimento tecnologico e capacidade institucional (avaliar requisitos legais)'],
      sociais: ['impactos institucionais e de capacidades humanas quando aplicável'],
      ambientais: ['avaliacao ambiental conforme regulatorio aplicavel'],
    };
  return o;
}

function nomeEmpresaSafe(c) {
  return String(c?.nome_empresa || c?.razao_social || 'a empresa').trim();
}

function tipoRecursoSafe(edital) {
  const t = `${edital?.tipo_recurso ?? edital?.tipo_recurso_raw ?? ''}`.trim().toLowerCase();
  if (!t) return 'oportunidade de fomento';
  return t.includes('cred') ? 'credito/financiamento' : edital?.tipo_recurso || edital?.tipo_recurso_raw || t;
}

/**
 * @returns {{ texto: string; explanation: string }}
 */
export function suggestTituloProjeto(cliente, editalTitulo, sectorKey) {
  const ne = nomeEmpresaSafe(cliente);
  const edTit = `${editalTitulo || ''}`.trim();

  let texto = '';
  if (edTit) {
    texto = `Projeto de inovacao e fortalecimento tecnologico de ${ne} — alinhamento a oportunidade / edital relacionado (${edTit.slice(0, 72)}${edTit.length > 72 ? '…' : ''})`;
  } else {
    texto = `${ne} — proposta inicial de projeto de inovacao (${sectorKey.replace(/_/g, ' ')})`;
  }

  return {
    texto,
    explanation:
      'Sugestao automatica modelo: combinacao do nome cadastral/setor inferido + referencia opcional ao edital. Avalie se o titulo comunica bem o projeto real.',
  };
}

export function suggestResumoPublicavel(cliente, edital, radarMatch, sectorKey) {
  const ne = nomeEmpresaSafe(cliente);
  const setorCliente = cliente?.setor || 'setor de atuação declarado no cadastro';
  const tema = cliente?.area_inovacao || cliente?.interesse_temas || 'temas relacionados ao negocio';
  const edTit = (edital?.titulo || editalTituloRadar(edital, radarMatch) || '').trim();
  const tipoOp = tipoRecursoSafe(edital);
  const areas = `${setorCliente}, ${tema}`.replace(/\s+/g, ' ');
  let radarNote = '';
  if (typeof radarMatch?.scorePct === 'number' && !Number.isNaN(radarMatch.scorePct)) {
    radarNote = ` Um indicativo de compatibilidade (Radar de Fomento) apontou aproximadamente ${Math.round(radarMatch.scorePct)}%; trata-se apenas de referência interna até validação técnica.`;
  }

  let blocoOp = '';
  if (edTit) {
    blocoOp = ` A proposta busca dialogar com a oportunidade identificada como "${edTit.slice(0, 110)}…" (tipo de recurso referenciado como ${tipoOp}).`;
  } else {
    blocoOp = ` A empresa pode usar este espaco para deixar o resumo especifico antes de direcionar a um edital.`;
  }

  const texto = `Este relatorio inicial consolida a intencao de ${ne} em avancar com iniciativas de inovacao vinculadas a ${areas}. O projeto podera envolver aprimoramento de capacidades tecnologicas, organizacionais e de mercado, conforme o escopo for detalhado pela equipe.${blocoOp} Recomenda-se revisar valores, garantias e requisitos oficiais no regulamento antes de qualquer envio.${radarNote}`;

  return {
    texto,
    explanation:
      'Texto modelo seguro usando cadastro da empresa + edital (se existir) + Radar (se pontuacao existir); nao afirma entregáveis especificos nem numeros financiários.',
  };
}

function editalTituloRadar(edital, radar) {
  return edital?.titulo || radar?.tituloEdital || '';
}

export function suggestProblemaOportunidade(cliente) {
  if (cliente?.descricao_projeto && String(cliente.descricao_projeto).trim()) {
    return {
      texto: `${String(cliente.descricao_projeto).slice(0, 700)}`,
      explanation: 'Texto inicial extraido da descricao de projeto atual no cadastro do cliente.',
    };
  }
  return {
    texto:
      'O projeto podera responder a uma oportunidade de eficiência, nova oferta ao mercado ou fortalecimento tecnologico observada pela empresa. Recomenda-se detalhar o problema quantificando limitacoes atuais (custos prazos ou qualidade) e o resultado desejado.',
    explanation:
      'Nao havia descricao rica suficiente no cadastro — texto orientativo neutro para preenchimento manual.',
  };
}

export function suggestSolucaoProposta(cliente, sectorKey) {
  const area = cliente?.area_inovacao || 'areas de desenvolvimento da empresa';
  return {
    texto: `Em linha com o perfil (${sectorKey}) e a diretriz de inovacao (${area}), a solucao proposta deve descrever as entregas tecnicas, marcos intermediarios e recursos criticos envolvidos. O escopo tecnico precisa ser validado pela equipe interna antes da submissao formal.`,
    explanation: 'Orientacao textual generica orientada pelo setor e area de inovacao quando existentes.',
  };
}

export function suggestObjetivoGeral(cliente, edital, radarMatch) {
  const ne = nomeEmpresaSafe(cliente);
  const edTit = editalTituloRadar(edital, radarMatch).trim();

  let texto =
    edTit.length > 0
      ? `Estruturar e comunicar uma proposta alinhada a oportunidade citada (${edTit.slice(0, 80)}…), fortalecendo a base de PD&I e inovacao de ${ne}.`
      : `Formalizar projeto de inovacao compativel com o porte e o setor de ${ne}, com metas e indicadores a serem detalhados.`;

  return {
    texto,
    explanation: edTit
      ? 'Sugestao baseada na existencia de edital/oportunidade de referencia.'
      : 'Sugestao generica usando nome cadastrado onde disponivel.',
  };
}

/** Finalidades A–G (Finep-inspired) como orientacao, sem afirmar entregável concreto. */
export function suggestFinalidadesBlocos(cliente, sectorKey) {
  const ne = nomeEmpresaSafe(cliente);
  const temas = cliente?.interesse_temas || 'demandas relacionadas ao negocio';
  return {
    a: `${ne} descrevera o que sera desenvolvido ou aprimorado no projeto — por exemplo iniciativas em ${temas}. O nivel de detalhe deve aumentar antes da submissao oficial.`,
    b: `Aplicacao esperada deve ser especificada (mercados segmentos processos usuarios internos ou externos). O setor (${sectorKey}) ajuda como guia inicial.`,
    c: 'Desafios tecnologicos e incertezas precisam ser listados objetivamente pela equipe; este campo indica apenas que eles devem ser documentados.',
    d: 'Se houver necessidade de ICT parceiro laboratorio ou co-desenvolvimento indicar aqui quando for confirmado pela empresa.',
    e: `Resultados socioeconomicos ou de desempenho devem aparecer como metas revisaveis; nada numerico sera inventado sem base no cadastro.`,
    f: `O diferencial deve comparar solucoes existentes versus a proposta; evitar hype — focar fatos.`,
    g: `Produto processo ou servico resultante sera definido quando o escopo ficar consolidado.`,
  };
}

export function formatEditalFinanceRefs(edital) {
  const parts = [];
  if (edital?.valor_maximo) parts.push(`Valor referencial citado pela fonte/oportunidade: ${String(edital.valor_maximo)}`);
  if (edital?.prazo_envio || edital?.prazo_envio_raw || edital?.dataLimite) {
    parts.push(`Prazo comunicado pela oportunidade: ${String(edital.prazo_envio || edital.prazo_envio_raw || edital.dataLimite)}`);
  }
  if (edital?.taxa != null && edital.taxa !== '') parts.push(`Taxa mencionada: ${String(edital.taxa)}`);
  if (edital?.carencia != null && edital.carencia !== '') parts.push(`Carencia: ${String(edital.carencia)}`);
  if (edital?.amortizacao != null && edital.amortizacao !== '') parts.push(`Amortizacao: ${String(edital.amortizacao)}`);
  if (edital?.contrapartida != null && edital.contrapartida !== '') parts.push(`Contrapartida indicada: ${String(edital.contrapartida)}`);
  return parts.filter(Boolean).join('\n');
}
