/**
 * Textos e estruturas consultivas para autofill do pré-projeto (sem alterar score do Radar).
 */

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function nomeCliente(c) {
  return String(c?.nome_empresa || c?.razao_social || 'o cliente').trim();
}

/** @returns {string[]} */
export function collectRadarPositiveReasons(radarMatch) {
  if (!radarMatch) return [];
  const out = [];
  if (hasText(radarMatch.matchLinha)) out.push(String(radarMatch.matchLinha));
  const pos = radarMatch.razoesPositivas ?? radarMatch.razoes_positivas;
  if (Array.isArray(pos)) pos.forEach((r) => hasText(r) && out.push(String(r)));
  const raz = radarMatch.razoes;
  if (Array.isArray(raz)) raz.forEach((r) => hasText(r) && out.push(String(r)));
  return [...new Set(out)].slice(0, 6);
}

/** @returns {string[]} */
export function collectRadarAlerts(radarMatch) {
  if (!radarMatch) return [];
  const out = [];
  const pens = radarMatch.radar_penalidades ?? radarMatch.penalidades;
  if (Array.isArray(pens)) pens.forEach((p) => hasText(p) && out.push(String(p)));
  else if (pens && typeof pens === 'object') {
    const mot = pens.motivos ?? pens.items;
    if (Array.isArray(mot)) mot.forEach((p) => hasText(p) && out.push(String(p)));
  }
  if (Array.isArray(radarMatch.alertas)) {
    radarMatch.alertas.forEach((a) => hasText(a) && out.push(String(a)));
  }
  if (hasText(radarMatch.alertaPrazo)) out.push(`Prazo: ${radarMatch.alertaPrazo}`);
  return [...new Set(out)].slice(0, 8);
}

/**
 * Narrativa consultiva de aderência (não afirma elegibilidade legal).
 */
export function buildConsultorFitNarrative(cliente, edital, radarMatch) {
  const ne = nomeCliente(cliente);
  const setor = cliente?.setor ? String(cliente.setor) : 'setor cadastrado';
  const temas = cliente?.interesse_temas || cliente?.area_inovacao || 'temas de interesse do cadastro';
  const edTit = (edital?.titulo || radarMatch?.tituloEdital || '').trim();
  const razoes = collectRadarPositiveReasons(radarMatch);

  let intro =
    `Esta oportunidade parece aderente ao perfil de ${ne} porque há alinhamento entre ${temas} e o contexto de atuação em ${setor}.`;
  if (edTit) {
    intro += ` A referência "${edTit.slice(0, 100)}${edTit.length > 100 ? '…' : ''}" foi considerada na análise preliminar.`;
  }
  if (typeof radarMatch?.scorePct === 'number') {
    intro += ` O Radar de Fomento indicou compatibilidade aproximada de ${Math.round(radarMatch.scorePct)}% — use apenas como referência interna até validação técnica e leitura do regulamento.`;
  }
  if (razoes.length) {
    intro += `\n\nPontos que reforçam a aderência:\n• ${razoes.join('\n• ')}`;
  }
  return intro;
}

export function buildConsultorExecutiveSummary(cliente, edital, radarMatch) {
  const ne = nomeCliente(cliente);
  const edTit = (edital?.titulo || radarMatch?.tituloEdital || '').trim();
  const porte = cliente?.porte_empresa ? `, porte ${cliente.porte_empresa}` : '';
  const local = [cliente?.cidade, cliente?.estado].filter(Boolean).join(' — ');
  let bloco = `Resumo consultivo para ${ne}${porte}${local ? ` (${local})` : ''}.`;
  if (edTit) {
    bloco += ` Objetivo inicial: estruturar proposta alinhada à oportunidade "${edTit.slice(0, 90)}${edTit.length > 90 ? '…' : ''}".`;
  } else {
    bloco += ' Objetivo inicial: consolidar narrativa de projeto antes de vincular a um edital específico.';
  }
  bloco +=
    ' Valores, prazos e requisitos oficiais devem ser confirmados no regulamento e com o cliente antes de qualquer submissão.';
  return bloco;
}

export function formatOportunidadeMeta(edital, radarMatch) {
  const e = edital || {};
  return {
    fonte: hasText(e.fonte_recurso) ? String(e.fonte_recurso) : hasText(e.origem) ? String(e.origem) : '',
    prazo: hasText(e.prazo_envio)
      ? String(e.prazo_envio)
      : hasText(e.prazo_envio_raw)
        ? String(e.prazo_envio_raw)
        : hasText(e.dataLimite)
          ? String(e.dataLimite)
          : hasText(radarMatch?.prazoEdital)
            ? String(radarMatch.prazoEdital)
            : '',
    link: hasText(e.link) ? String(e.link) : hasText(e.url) ? String(e.url) : hasText(e.link_edital) ? String(e.link_edital) : '',
  };
}

export function formatScoreCompatLabel(radarMatch) {
  if (typeof radarMatch?.scorePct !== 'number' || Number.isNaN(radarMatch.scorePct)) return '';
  const pct = Math.round(radarMatch.scorePct);
  const compat = radarMatch.compatibilidade || radarMatch.compat || '';
  return compat ? `${pct}% — ${compat} (Radar)` : `${pct}% (Radar — referência interna)`;
}

export function buildStructuredDocumentsChecklist(cliente, edital, radarMatch) {
  const edTit = (edital?.titulo || radarMatch?.tituloEdital || '').trim();
  const clienteDocs = [
    'Documentação societária atualizada (contrato social ou equivalente).',
    'Comprovantes de regularidade fiscal e trabalhista, quando exigidos.',
    'Identificação e poderes dos representantes legais.',
    cliente?.cnpj ? `CNPJ ${cliente.cnpj} — conferir situação cadastral.` : 'CNPJ e situação cadastral a validar.',
  ].filter(Boolean);

  const tecnicos = [
    'Descrição técnica do projeto e cronograma preliminar.',
    'Currículo da empresa e equipe envolvida no desenvolvimento.',
    'Evidências de capacidade de execução (portfólio, contratos, certificações).',
  ];

  const financeiros = [
    'Demonstrações financeiras recentes, se o produto/edital exigir.',
    'Orçamento detalhado e plano de aplicação de recursos.',
    'Declarações sobre contrapartida e capacidade de pagamento (crédito), quando aplicável.',
  ];

  const editalDocs = edTit
    ? [
        `Checklist oficial do edital "${edTit.slice(0, 80)}${edTit.length > 80 ? '…' : ''}" (anexos, declarações, formulários do portal).`,
        'Regulamento completo e eventuais retificações publicadas.',
      ]
    : ['Vincular edital e baixar checklist oficial do portal da oportunidade.'];

  return {
    cliente: clienteDocs.join('\n'),
    tecnicos: tecnicos.join('\n'),
    financeiros: financeiros.join('\n'),
    edital: editalDocs.join('\n'),
    agregado: [
      '— Documentos do cliente —',
      ...clienteDocs,
      '',
      '— Documentos técnicos —',
      ...tecnicos,
      '',
      '— Documentos financeiros / jurídicos —',
      ...financeiros,
      '',
      '— Documentos do edital —',
      ...editalDocs,
    ].join('\n'),
  };
}

export function buildConsultorRisks(cliente, edital, radarMatch) {
  const risks = [];
  const meta = formatOportunidadeMeta(edital, radarMatch);
  if (meta.prazo) {
    const dias = radarMatch?.diasAtePrazo ?? radarMatch?.dias_ate_prazo;
    if (typeof dias === 'number' && dias <= 7) {
      risks.push(`Prazo curto: envio em até ${dias} dia(s) — priorizar validação com o cliente.`);
    } else {
      risks.push(`Confirmar prazo oficial (${meta.prazo}) e margem interna para montagem da proposta.`);
    }
  } else {
    risks.push('Prazo da oportunidade não informado na base — verificar no portal do edital.');
  }
  if (!hasText(cliente?.cnpj)) risks.push('CNPJ ausente ou incompleto no cadastro.');
  if (!hasText(cliente?.descricao_projeto)) risks.push('Descrição do projeto no cadastro ainda genérica — agendar reunião para detalhar escopo.');
  if (!meta.link) risks.push('Link do edital não disponível na ficha — localizar URL oficial antes da submissão.');
  collectRadarAlerts(radarMatch).forEach((a) => risks.push(`Alerta Radar: ${a}`));
  if (typeof radarMatch?.scorePct === 'number' && radarMatch.scorePct < 40) {
    risks.push('Compatibilidade Radar baixa — revisar elegibilidade antes de investir tempo em proposta completa.');
  }
  return risks.join('\n');
}

export function buildConsultorNextSteps(cliente, edital) {
  const edTit = (edital?.titulo || '').trim();
  return [
    '1. Validar interesse do cliente e prioridade na carteira.',
    '2. Confirmar elegibilidade (porte, setor, localização, requisitos do regulamento).',
    '3. Reunir documentos listados na seção Documentos necessários.',
    '4. Escrever proposta técnica com escopo, metas e indicadores acordados.',
    '5. Revisar orçamento preliminar e contrapartida com financeiro do cliente.',
    edTit
      ? `6. Submeter no portal oficial da oportunidade (${edTit.slice(0, 60)}${edTit.length > 60 ? '…' : ''}).`
      : '6. Vincular edital e submeter no portal oficial quando o escopo estiver fechado.',
  ].join('\n');
}

export function buildConsultorWorkPlan(cliente, edital) {
  const ne = nomeCliente(cliente);
  const edTit = (edital?.titulo || '').trim();
  return [
    `Fase 1 — Alinhamento (${ne}): validar escopo, responsáveis internos e cronograma macro com o cliente.`,
    'Fase 2 — Documentação: reunir cadastro societário, regularidades e material técnico base.',
    edTit
      ? `Fase 3 — Proposta: redigir narrativa e anexos conforme "${edTit.slice(0, 70)}…".`
      : 'Fase 3 — Proposta: redigir narrativa técnica e anexos conforme edital escolhido.',
    'Fase 4 — Revisão e submissão: revisão jurídica/financeira interna e envio no portal.',
  ].join('\n');
}

export function buildConsultorBudgetSummary(cliente, edital) {
  const parts = [];
  const min = cliente?.interesse_valor_min;
  const max = cliente?.interesse_valor_max;
  if (min != null || max != null) {
    const faixa = [min, max].filter((x) => x != null && x !== '').join(' a ');
    if (faixa) parts.push(`Faixa de interesse declarada no cadastro: ${faixa} (confirmar moeda e vigência).`);
  }
  if (edital?.valor_maximo) {
    parts.push(`Valor máximo referenciado na oportunidade: ${String(edital.valor_maximo)}.`);
  }
  if (edital?.contrapartida != null && edital.contrapartida !== '') {
    parts.push(`Contrapartida mencionada na ficha: ${String(edital.contrapartida)}.`);
  }
  if (!parts.length) {
    return 'Orçamento preliminar a definir com o cliente. Indique valor total estimado, contrapartida e principais categorias de gasto na seção Orçamento.';
  }
  return parts.join('\n');
}

export function buildBudgetCategoriesHint() {
  return [
    'Pessoal / equipe própria',
    'Equipamentos e materiais',
    'Serviços de terceiros / consultoria',
    'Viagens e capacitação',
    'Software e licenças',
    'Outros custos diretos (detalhar)',
  ].join('\n');
}

export function buildInitialChecklist(cliente, edital, radarMatch) {
  const items = [
    '[ ] Reunião de alinhamento com o cliente',
    '[ ] Leitura do regulamento / edital completo',
    '[ ] Validação de elegibilidade',
    '[ ] Lista de documentos conferida',
    '[ ] Orçamento preliminar aprovado internamente',
    '[ ] Cronograma com marcos definidos',
  ];
  if ((edital?.titulo || radarMatch?.tituloEdital) && typeof radarMatch?.scorePct === 'number') {
    items.push(`[ ] Compatibilidade Radar (${Math.round(radarMatch.scorePct)}%) discutida com o cliente`);
  }
  return items.join('\n');
}
