/**
 * Sugestões e texto de contexto para o pré-cadastro (sempre editáveis pelo usuário).
 */

function norm(s) {
  return String(s ?? '')
    .trim()
    .toLowerCase();
}

function joinSentences(parts) {
  return parts.filter(Boolean).join(' ');
}

/**
 * Texto corrido útil para cartão “Contexto”.
 * @param {Record<string, unknown>} cliente
 * @param {{ titulo?: string } | null} edital
 * @param {{ tituloEdital?: string; scorePct?: number } | null} radarMatch
 */
export function buildProjectSummary(cliente, edital, radarMatch) {
  const nome = cliente?.nome_empresa || cliente?.razao_social || 'a empresa';
  const porte = cliente?.porte_empresa ? `de porte ${cliente.porte_empresa}` : '';
  const setorTxt = cliente?.setor ? `atuando em ${String(cliente.setor)}` : '';
  const uf = cliente?.estado ? String(cliente.estado).toUpperCase() : '';
  const local = [cliente?.cidade, uf].filter(Boolean).join(', ');
  const localTxt = local ? `sediada em ${local}` : '';

  const editalTitulo = edital?.titulo || radarMatch?.tituloEdital || '';
  const linhaRef = editalTitulo ? `com foco no edital “${editalTitulo.slice(0, 120)}${editalTitulo.length > 120 ? '…' : ''}”` : 'em linhas de crédito para inovação';

  const temas = cliente?.interesse_temas ? ` Temas de interesse registrados: ${cliente.interesse_temas}.` : '';
  const area = cliente?.area_inovacao ? ` Área de inovação: ${cliente.area_inovacao}.` : '';

  let scoreTxt = '';
  if (typeof radarMatch?.scorePct === 'number' && !Number.isNaN(radarMatch.scorePct)) {
    scoreTxt = ` Indicador de aderência ao radar: ${Math.round(radarMatch.scorePct)}%.`;
  }

  return joinSentences([
    `${nome} é uma organização ${porte} ${setorTxt} ${localTxt}, ${linhaRef}.`.replace(/\s+/g, ' ').trim(),
    temas,
    area,
    scoreTxt,
  ]);
}

import { toLegacyCompletionShape } from './calculatePreCadastroCompleteness.js';

/**
 * @returns {{ key: string; badge: 'recomendada'|'compativel'|'alternativa'; aderencia: 'alta'|'media'|'baixa'; motivo: string }}
 */
function scoreLinhaPrincipal(cliente) {
  const hay = norm(
    `${cliente?.setor} ${cliente?.area_inovacao} ${cliente?.interesse_temas} ${cliente?.descricao_projeto}`,
  );
  const temInov =
    /inov|produt|pesquisa|desenvolvimento|p&d|pd&i|tecnolog/i.test(hay) || !!cliente?.tem_projeto_inovacao;
  const aderencia = temInov ? 'alta' : 'media';
  const badge = temInov ? 'recomendada' : 'compativel';
  return {
    key: 'bloco1_linha_credito_principal',
    badge,
    aderencia,
    motivo:
      'Linha voltada a crédito para inovação em produto institucional; combina com organizações que declaram atuação em inovação e desenvolvimento tecnológico.',
  };
}

function scoreLinhaTelecom(cliente) {
  const hay = norm(
    `${cliente?.setor} ${cliente?.area_inovacao} ${cliente?.interesse_temas} ${cliente?.descricao_projeto}`,
  );
  const hit = /telecom|conect|5g|fibra|rede|ti\b|software|digital|ict/i.test(hay);
  const aderencia = hit ? 'alta' : 'baixa';
  const badge = hit ? 'recomendada' : 'alternativa';
  return {
    key: 'bloco1_linha_credito_telecom',
    badge,
    aderencia,
    motivo:
      'Indicada quando há aderência explícita a telecomunicações, conectividade ou soluções digitais no cadastro da empresa.',
  };
}

/**
 * @param {Record<string, unknown>} cliente
 * @param {{ titulo?: string; fonte_recurso?: string } | null} edital
 * @param {{ tituloEdital?: string; scorePct?: number; motivos?: string[] } | null} radarMatch
 */
export function buildProjectSuggestions(cliente, edital, radarMatch) {
  const c = cliente || {};
  const editalTitulo = edital?.titulo || radarMatch?.tituloEdital || '';

  const linhaPrincipal = scoreLinhaPrincipal(c);
  const linhaTelecom = scoreLinhaTelecom(c);

  const tituloProjeto = editalTitulo
    ? `Projeto vinculado — ${editalTitulo.slice(0, 90)}${editalTitulo.length > 90 ? '…' : ''}`
    : `${c.nome_empresa || 'Projeto'} — Fortalecimento de capacidades de inovação`;

  const resumoExecutivo = buildProjectSummary(c, edital, radarMatch);

  const objetivoGeral = joinSentences([
    editalTitulo
      ? `Estruturar proposta alinhada aos requisitos do edital selecionado, fortalecendo a base de PD&I da ${c.nome_empresa || 'empresa'}.`
      : `Desenvolver projeto de inovação com metas claras de produto, processo ou serviço, em linha com o porte e o setor declarados.`,
  ]);

  const problema = joinSentences([
    c.descricao_projeto
      ? `Contexto da empresa: ${String(c.descricao_projeto).slice(0, 400)}${String(c.descricao_projeto).length > 400 ? '…' : ''}`
      : 'Descrever o gargalo técnico ou de mercado que o projeto se propõe a endereçar (preencher com detalhes).',
  ]);

  const solucao = joinSentences([
    c.area_inovacao
      ? `Diretriz sugerida a partir da área de inovação cadastrada (${c.area_inovacao}): detalhar entregas, marcos e indicadores.`
      : 'Detalhar a solução proposta: escopo técnico, parcerias previstas e resultados mensuráveis.',
  ]);

  const diferencial = joinSentences([
    'Explicitar o que diferencia a presente proposta frente a soluções existentes no mercado ou na própria empresa.',
  ]);

  const maturidade = c.nivel_maturidade ? String(c.nivel_maturidade) : 'Ideação';

  const publicoMercado = joinSentences([
    c.interesse_temas ? `Segmentos e temas de interesse: ${c.interesse_temas}.` : '',
    'Complementar com público-alvo e canais de comercialização previstos.',
  ]);

  const resultados = joinSentences([
    'Resultados esperados: indicadores de desempenho (KPIs), benefícios socioeconômicos e ambientais quando aplicável.',
  ]);

  const motivoRecomendacao = joinSentences([
    `Esta oportunidade parece aderente ao perfil de ${c.nome_empresa || 'a empresa'} porque há alinhamento entre o cadastro (porte, setor e temas) e o contexto do edital.`,
    editalTitulo ? ` Referência: “${editalTitulo.slice(0, 100)}${editalTitulo.length > 100 ? '…' : ''}”.` : '',
    typeof radarMatch?.scorePct === 'number'
      ? ` O Radar de Fomento indicou compatibilidade aproximada de ${Math.round(radarMatch.scorePct)}% — use como referência interna até validar elegibilidade no regulamento.`
      : '',
  ]);

  const principaisAderencias = [
    c.porte_empresa && `Porte ${c.porte_empresa} compatível com faixas típicas de financiamento.`,
    c.setor && `Setor declarado: ${c.setor}.`,
    (c.estado || c.cidade) && `Atuação em ${[c.cidade, c.estado].filter(Boolean).join('/')}.`,
    c.tem_projeto_inovacao && 'Empresa já declara ter projeto de inovação em andamento ou planejado.',
  ]
    .filter(Boolean)
    .join('\n');

  const pontosComplementar = [
    !c.cnpj && 'Validar e completar CNPJ no cadastro.',
    !c.descricao_projeto?.trim() && 'Incluir descrição mais rica do projeto atual da empresa.',
    !c.interesse_temas?.trim() && 'Registrar temas de interesse no cadastro para refinar o radar.',
    'Confirmar documentação societária e regularidade fiscal para submissão.',
  ]
    .filter(Boolean)
    .join('\n');

  const porQueLinha = joinSentences([
    linhaPrincipal.badge === 'recomendada'
      ? 'A linha principal foi priorizada pelo perfil de inovação declarado.'
      : 'A linha principal permanece como opção compatível; avalie enquadramento com o analista do banco.',
    linhaTelecom.badge === 'recomendada'
      ? 'A linha de telecomunicações foi destacada por aderência temática no cadastro.'
      : 'A linha de telecomunicações pode servir como alternativa se o projeto envolver conectividade ou ICT.',
  ]);

  const requisitosAtendidos = joinSentences([
    c.possui_certidao_negativa && 'Certidão negativa declarada.',
    c.regular_fiscal && 'Regularidade fiscal declarada.',
    c.regular_trabalhista && 'Regularidade trabalhista declarada.',
    'Demais requisitos do edital devem ser conferidos no regulamento oficial.',
  ]);

  const lacunas = pontosComplementar;

  const docsRecomendados = [
    'Documentação societária atualizada (contrato social / consolidado).',
    'Balanço e DRE recentes, se exigidos pelo produto.',
    'Curriculum da empresa e portfólio técnico do que será desenvolvido.',
    editalTitulo ? 'Checklist específico do edital selecionado (anexos e declarações).' : '',
  ]
    .filter(Boolean)
    .join('\n');

  const proximosPassos = [
    'Revisar o resumo executivo e o escopo com a equipe técnica.',
    'Validar linha de crédito com o gerente de relacionamento.',
    'Completar campos pendentes e anexar documentos no canal oficial.',
  ].join('\n');

  const aderenciaNivel =
    typeof radarMatch?.scorePct === 'number' && radarMatch.scorePct >= 70
      ? 'alta'
      : typeof radarMatch?.scorePct === 'number' && radarMatch.scorePct >= 40
        ? 'media'
        : typeof radarMatch?.scorePct === 'number'
          ? 'baixa'
          : linhaPrincipal.aderencia === 'alta'
            ? 'alta'
            : 'media';

  const linhaRecomendadaLabel =
    linhaPrincipal.badge === 'recomendada'
      ? 'Linha principal (crédito inovação — produto institucional)'
      : linhaTelecom.badge === 'recomendada'
        ? 'Linha com aderência a telecomunicações'
        : 'Linha principal (crédito inovação — produto institucional)';

  return {
    editalTitulo,
    tituloProjeto,
    resumoExecutivo,
    objetivoGeral,
    problemaOportunidade: problema,
    solucaoProposta: solucao,
    diferencialInovador: diferencial,
    maturidade,
    publicoMercado,
    resultadosEsperados: resultados,
    motivoRecomendacao,
    principaisAderencias,
    pontosComplementar,
    porQueLinha,
    requisitosAtendidos,
    lacunas,
    docsRecomendados,
    proximosPassos,
    aderenciaNivel,
    linhaRecomendadaLabel,
    linhasMeta: { principal: linhaPrincipal, telecom: linhaTelecom },
    /** Pre-check sugerido (usuário pode desmarcar) */
    suggestCheckPrincipal: linhaPrincipal.badge === 'recomendada' || linhaPrincipal.aderencia === 'alta',
    suggestCheckTelecom: linhaTelecom.badge === 'recomendada',
  };
}

/**
 * Completude (0–100): delega a `calculatePreCadastroCompleteness`, mantendo formato legado da UI.
 * @param {Record<string, unknown>} form
 */
export function computeCompletion(form) {
  return toLegacyCompletionShape(form);
}
