/**
 * Textos consultivos quando o pré-projeto nasce de várias oportunidades selecionadas.
 */
import { partitionSelectedOpportunities } from '../consultor/opportunitySelection';
import { MULTI_OPPORTUNITY_COMPLEMENTARY_LIMIT } from '../consultor/consultorWorkspaceConstants';
import { collectRadarAlerts, collectRadarPositiveReasons } from './consultorAutofill';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function tituloCurto(t, max = 90) {
  const s = String(t || '').trim();
  if (!s) return 'Oportunidade sem título';
  return s.length > max ? `${s.slice(0, max)}…` : s;
}

/**
 * JSON leve para bloco_estr_oportunidades_selecionadas.
 */
function grupoOportunidade(o, primaryKey, complementarKeys, observacaoKeys) {
  if (o.key === primaryKey) return 'principal';
  if (complementarKeys.has(o.key)) return 'complementar';
  if (observacaoKeys.has(o.key)) return 'observacao';
  return 'complementar';
}

export function serializeOportunidadesSelecionadas(opportunities, primaryKey) {
  const part = partitionSelectedOpportunities(
    opportunities,
    opportunities?.find((o) => o.key === primaryKey) || null,
  );
  const compKeys = new Set(part.complementares.map((o) => o.key));
  const obsKeys = new Set(part.observacao.map((o) => o.key));
  const list = (opportunities || []).map((o) => ({
    key: o.key,
    id_edital: o.edital?.id_edital ?? o.edital?.id,
    titulo: o.titulo,
    fonte_recurso: o.fonte_recurso,
    score: o.scorePct,
    compatibilidade: o.compatibilidade,
    prazo: o.prazo_envio,
    link: o.link,
    principal: o.key === primaryKey,
    grupo: grupoOportunidade(o, primaryKey, compKeys, obsKeys),
  }));
  return JSON.stringify(list, null, 2);
}

/**
 * Texto legível das oportunidades consideradas (UI + campo texto).
 */
function formatOppLine(o, index) {
  const n = index != null ? `${index}. ` : '';
  return `${n}${tituloCurto(o.titulo)} — ${o.scorePct ?? o.score ?? '—'}% (${o.compatibilidade || '—'})${o.fonte_recurso ? ` · ${o.fonte_recurso}` : ''}${o.prazo_envio || o.prazo ? ` · prazo: ${o.prazo_envio || o.prazo}` : ''}`;
}

export function formatOportunidadesConsideradasText(opportunities, primary) {
  const part = partitionSelectedOpportunities(opportunities, primary);
  const lines = [];
  const n = part.all.length;

  if (part.primary) {
    lines.push(
      `Principal (maior compatibilidade): ${formatOppLine(part.primary, null).replace(/^\d+\. /, '')}`,
    );
    if (part.primary.link) lines.push(`  Link: ${part.primary.link}`);
  }

  if (part.complementares.length) {
    lines.push(
      '',
      `Prioritárias complementares (top ${MULTI_OPPORTUNITY_COMPLEMENTARY_LIMIT} por score):`,
    );
    part.complementares.forEach((o, i) => lines.push(formatOppLine(o, i + 1)));
  }

  if (part.observacao.length) {
    lines.push(
      '',
      `Em observação (${part.observacao.length} oportunidade${part.observacao.length === 1 ? '' : 's'} — resumo):`,
    );
    part.observacao.forEach((o, i) => {
      lines.push(
        `${i + 1}. ${tituloCurto(o.titulo, 70)} — ${o.scorePct ?? o.score ?? '—'}%${o.fonte_recurso ? ` · ${o.fonte_recurso}` : ''}`,
      );
    });
  }

  if (n > 1 && !part.complementares.length && !part.observacao.length) {
    lines.push('', `${n} oportunidades no conjunto; detalhar priorização com o cliente.`);
  }

  return lines.join('\n');
}

export function buildMultiExecutiveSummary(cliente, opportunities, primary) {
  const n = opportunities?.length || 0;
  const ne = cliente?.nome_empresa || cliente?.razao_social || 'o cliente';
  const part = partitionSelectedOpportunities(opportunities, primary);
  const mainTit = tituloCurto(part.primary?.titulo);
  const mainScore = part.primary?.scorePct ?? '—';

  let texto = `Este pré-projeto foi gerado a partir de ${n} oportunidade${n === 1 ? '' : 's'} selecionada${n === 1 ? '' : 's'} para ${ne}. `;
  if (n === 1) {
    texto += `A oportunidade considerada é "${mainTit}" (compatibilidade aproximada ${mainScore}% no Radar — referência interna).`;
  } else {
    texto += `A oportunidade principal recomendada é "${mainTit}", por apresentar maior compatibilidade (${mainScore}%) com o perfil cadastrado. `;
    const nComp = part.complementares.length;
    const nObs = part.observacao.length;
    if (nComp > 0) {
      texto += `Foram detalhadas no corpo principal ${nComp} oportunidade${nComp === 1 ? '' : 's'} prioritária${nComp === 1 ? '' : 's'} complementar${nComp === 1 ? '' : 'es'}`;
      if (nObs > 0) {
        texto += ` e ${nObs} em observação (resumo compacto para manter o documento objetivo)`;
      }
      texto += '. ';
    } else {
      texto += 'As demais foram organizadas como alternativas ou complementares na estratégia de fomento. ';
    }
  }
  texto +=
    n === 1
      ? ' Recomenda-se validar interesse do cliente, prazos oficiais e documentação exigida no regulamento antes de submissão.'
      : ' Recomenda-se validar interesse do cliente, prazos oficiais e documentação exigida em cada regulamento antes de submissão.';
  return texto;
}

export function buildMultiFitNarrative(cliente, opportunities, primary, related) {
  const ne = cliente?.nome_empresa || 'o cliente';
  const razoes = collectRadarPositiveReasons(primary?.radarMatch);
  let intro = `Para ${ne}, o conjunto de ${opportunities.length} oportunidades selecionadas sugere uma estratégia de fomento com foco em "${tituloCurto(primary?.titulo)}" como eixo principal.`;
  if (razoes.length) {
    intro += `\n\nPontos fortes da oportunidade principal:\n• ${razoes.slice(0, 5).join('\n• ')}`;
  }
  const fontes = [...new Set(related.map((o) => o.fonte_recurso).filter(Boolean))];
  if (fontes.length) {
    intro += `\n\nFontes recorrentes nas oportunidades complementares: ${fontes.join(', ')}.`;
  }
  const temas = cliente?.interesse_temas || cliente?.area_inovacao || cliente?.setor;
  if (temas) {
    intro += ` Há alinhamento preliminar com ${temas} cadastrados no perfil do cliente.`;
  }
  return intro;
}

export function buildMultiRisks(cliente, opportunities) {
  const risks = [];
  const curtos = opportunities.filter((o) => {
    const d = o.row?.diasAtePrazo ?? o.radarMatch?.diasAtePrazo;
    return typeof d === 'number' && d <= 7;
  });
  if (curtos.length) {
    risks.push(
      `${curtos.length} oportunidade(s) com prazo curto (≤7 dias): priorizar leitura do regulamento e decisão com o cliente.`,
    );
  }
  const semPrazo = opportunities.filter((o) => !hasText(o.prazo_envio));
  if (semPrazo.length) {
    risks.push(`${semPrazo.length} oportunidade(s) sem prazo informado na base — confirmar no portal oficial.`);
  }
  const semLink = opportunities.filter((o) => !hasText(o.link));
  if (semLink.length) {
    risks.push(`${semLink.length} oportunidade(s) sem link na ficha — localizar URL antes de preparar anexos.`);
  }
  opportunities.forEach((o) => {
    collectRadarAlerts(o.radarMatch).forEach((a) => {
      risks.push(`[${tituloCurto(o.titulo, 40)}] ${a}`);
    });
  });
  if (!risks.length) {
    risks.push('Revisar elegibilidade e requisitos de cada oportunidade selecionada antes de comprometer recursos de proposta.');
  }
  return [...new Set(risks)].slice(0, 12).join('\n');
}

export function buildMultiNextSteps(opportunities, primary) {
  const n = opportunities.length;
  return [
    `1. Revisar com o cliente a oportunidade principal: ${tituloCurto(primary?.titulo)}.`,
    '2. Validar interesse e capacidade de executar propostas em paralelo ou em sequência.',
    n > 1
      ? '3. Comparar documentos exigidos entre as oportunidades selecionadas (evitar duplicar esforço).'
      : '3. Reunir documentação base do cliente.',
    '4. Priorizar submissões por prazo — oportunidades com vencimento mais próximo primeiro.',
    n > 1
      ? `5. Definir quais das ${n} oportunidades serão acompanhadas ativamente na carteira.`
      : '5. Preparar rascunho técnico e orçamento alinhados ao regulamento.',
    '6. Submeter no portal oficial após revisão interna.',
  ].join('\n');
}

export function buildMultiDocuments(cliente, opportunities, primary) {
  const part = partitionSelectedOpportunities(opportunities, primary);
  const blocks = new Set([
    'Documentação societária e regularidade do cliente.',
    'Descrição técnica e equipe (adaptar por oportunidade).',
  ]);
  if (part.primary) {
    blocks.add(`Checklist prioritário — principal: ${tituloCurto(part.primary.titulo, 60)}.`);
  }
  part.complementares.forEach((o) => {
    blocks.add(`Checklist complementar: ${tituloCurto(o.titulo, 60)}.`);
  });
  if (part.observacao.length) {
    blocks.add(
      `Demais ${part.observacao.length} oportunidade(s) em observação — validar regulamento apenas se o cliente confirmar interesse.`,
    );
  }
  return [...blocks].join('\n');
}

export function buildMultiBudget(primary, opportunities) {
  const vals = opportunities
    .map((o) => o.valor_maximo)
    .filter((v) => hasText(v));
  if (hasText(primary?.valor_maximo)) {
    let t = `Valor de referência da oportunidade principal: ${primary.valor_maximo}.`;
    if (vals.length > 1) {
      t += ' Outras oportunidades selecionadas apresentam valores distintos — detalhar por edital no orçamento final.';
    }
    return t;
  }
  if (vals.length > 1) {
    return 'Valores máximos variam entre as oportunidades selecionadas — confirmar no regulamento de cada uma e consolidar orçamento com o cliente.';
  }
  return 'Orçamento preliminar a definir com o cliente conforme a oportunidade principal escolhida para submissão.';
}
