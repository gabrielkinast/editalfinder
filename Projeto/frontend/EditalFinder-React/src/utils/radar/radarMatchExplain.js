/**
 * Camada de explicabilidade do Radar — apenas apresentação (não altera score).
 * Deriva textos a partir de `hit.criterios` já calculados em radarMatch.js.
 */

const DIMENSOES = [
  { key: 'afinidade', label: 'Afinidade temática', max: 30 },
  { key: 'tipo', label: 'Modalidade / recurso', max: 15 },
  { key: 'perfil', label: 'Área, setor e perfil', max: 20 },
  { key: 'localizacao', label: 'Localização', max: 10 },
  { key: 'prazo', label: 'Prazo', max: 10 },
  { key: 'valor', label: 'Valor e porte', max: 5 },
];

const GENERIC_TITLE_RE =
  /^[\s\-–—]*(edital|chamada|resultado|retificacao|retificação|comunicado|aviso|publicacao|publicação)[\s\-–—.!?:]*$/i;

function nivelFromPct(pct, ausente) {
  if (ausente) return 'ausente';
  if (pct >= 70) return 'alto';
  if (pct >= 40) return 'medio';
  return 'baixo';
}

function textoAfinidade(c) {
  if (c.ausenteCliente && c.ausenteEdital) {
    return 'Poucos temas cadastrados no cliente e no edital para comparar.';
  }
  if (c.ausenteCliente) {
    return 'Cliente sem áreas/temas no cadastro — afinidade limitada ao texto do edital.';
  }
  if (c.ausenteEdital) {
    return 'Edital com pouca descrição de área/temas — use o título e a fonte como referência.';
  }
  const m = (c.matches || []).slice(0, 5);
  if (m.length) {
    return `Cruzamento de temas: ${m.join(', ')}.`;
  }
  return c.detalhe || 'Afinidade temática calculada a partir do cadastro.';
}

function textoTipo(c) {
  if (c.ausenteCliente) {
    return 'Cliente sem preferência de modalidade — pontuação neutra.';
  }
  if (c.ausenteEdital) {
    return 'Tipo de recurso pouco explícito no edital.';
  }
  const m = (c.matches || []).slice(0, 4);
  if (m.length) {
    return `Modalidades alinhadas: ${m.join(', ')}.`;
  }
  return c.detalhe || 'Modalidade/recurso fora das preferências declaradas.';
}

function textoPerfil(c) {
  const m = (c.motivos || []).filter(Boolean);
  if (c.ausentePerfilEdital) {
    return 'Público-alvo do edital pouco estruturado; perfil avaliado com cautela.';
  }
  if (m.length) {
    return m.slice(0, 3).join(' · ');
  }
  return 'Perfil e elegibilidade compatíveis com o público descrito.';
}

function textoLocalizacao(c) {
  if (c.indefinido) {
    return c.motivo || 'Abrangência geográfica pouco clara no edital.';
  }
  return c.motivo || 'Localização compatível com o cadastro do cliente.';
}

function textoPrazo(c, prazoInfoCard) {
  if (prazoInfoCard?.rotulo === 'curto' && prazoInfoCard?.dias != null) {
    return `Prazo em ${prazoInfoCard.dias} dia(s) — atenção ao calendário.`;
  }
  if (c.ausente) {
    return 'Data limite não informada no edital.';
  }
  return c.motivo || 'Situação de prazo considerada no score.';
}

function textoValor(c) {
  if (c.ausente || c.ausenteCliente || c.ausenteEdital) {
    return c.motivo || 'Valor ou faixa de interesse não comparáveis.';
  }
  return c.motivo || 'Faixa de valor compatível com o interesse do cliente.';
}

function buildTextoDimensao(key, c, prazoInfoCard) {
  switch (key) {
    case 'afinidade':
      return textoAfinidade(c);
    case 'tipo':
      return textoTipo(c);
    case 'perfil':
      return textoPerfil(c);
    case 'localizacao':
      return textoLocalizacao(c);
    case 'prazo':
      return textoPrazo(c, prazoInfoCard);
    case 'valor':
      return textoValor(c);
    default:
      return '';
  }
}

function isDimensaoAusente(key, c, criterioMeta) {
  if (key === 'afinidade') {
    return !!(c.ausenteCliente && c.ausenteEdital);
  }
  if (key === 'perfil') {
    return !!c.ausentePerfilEdital;
  }
  if (key === 'tipo') {
    return !!(c.ausenteCliente && c.ausenteEdital);
  }
  if (key === 'localizacao') {
    return !!c.indefinido;
  }
  if (key === 'prazo') {
    return !!c.ausente;
  }
  if (key === 'valor') {
    return !!(c.ausente || c.ausenteCliente || c.ausenteEdital);
  }
  return !!criterioMeta?.[key]?.ausente;
}

function collectPositivos(criterios, prazoInfoCard) {
  const out = [];

  const af = criterios.afinidade;
  if ((af?.matches || []).length >= 2) {
    out.push({
      dimensao: 'afinidade',
      text: `Temas em comum: ${af.matches.slice(0, 4).join(', ')}.`,
    });
  } else if ((af?.matches || []).length === 1) {
    out.push({
      dimensao: 'afinidade',
      text: `Tema relacionado: ${af.matches[0]}.`,
    });
  }

  if (criterios.perfil?.pontos >= 12 && (criterios.perfil.motivos || []).length) {
    const positivosPerfil = criterios.perfil.motivos.filter(
      (m) => !/fora do encaixe|possivelmente fora|não é o foco/i.test(m),
    );
    positivosPerfil.slice(0, 2).forEach((m) => {
      out.push({ dimensao: 'perfil', text: m });
    });
  }

  if ((criterios.tipo?.matches || []).length) {
    out.push({
      dimensao: 'tipo',
      text: `Recurso/modalidade desejada: ${criterios.tipo.matches.slice(0, 3).join(', ')}.`,
    });
  }

  if (criterios.localizacao?.pontos >= 6 && criterios.localizacao?.motivo) {
    out.push({ dimensao: 'localizacao', text: criterios.localizacao.motivo });
  }

  if (criterios.prazo?.pontos >= 8 && criterios.prazo?.motivo && !criterios.prazo?.urgente) {
    out.push({ dimensao: 'prazo', text: criterios.prazo.motivo });
  }

  if (criterios.valor?.pontos >= 3 && criterios.valor?.motivo) {
    const v = criterios.valor.motivo;
    if (!/abaixo|acima|fora|vagos/i.test(v)) {
      out.push({ dimensao: 'valor', text: v });
    }
  }

  if (criterios.qualidade?.pontos >= 6 && (criterios.qualidade.motivos || []).length) {
    const qm = criterios.qualidade.motivos.find((m) => /válido|pdf/i.test(m));
    if (qm) out.push({ dimensao: 'qualidade', text: qm });
  }

  return out.slice(0, 6);
}

function collectAlertas(hit, criterios, editalFmt, prazoInfoCard) {
  const alertas = [];
  const seen = new Set();

  const add = (key, label, text) => {
    if (!text || seen.has(key)) return;
    seen.add(key);
    alertas.push({ key, label, text });
  };

  if (prazoInfoCard?.rotulo === 'curto' || criterios.prazo?.urgente) {
    const dias = prazoInfoCard?.dias ?? criterios.prazo?.dias;
    add(
      'prazo_curto',
      'Prazo curto',
      dias != null
        ? `Faltam cerca de ${dias} dia(s) para o envio — priorize a análise.`
        : 'Prazo de inscrição muito próximo.',
    );
  }

  const titulo = String(editalFmt?.titulo ?? '').trim();
  if (titulo && (GENERIC_TITLE_RE.test(titulo) || titulo.length < 12)) {
    add(
      'titulo_generico',
      'Título genérico',
      'O título do edital é vago — confira o link e a descrição antes de recomendar ao cliente.',
    );
  }

  const pen = hit.penalidades?.motivos || [];
  pen.forEach((m) => {
    const s = String(m);
    if (/suspeit/i.test(s)) add('suspeito', 'Validação suspeita', s);
    else if (/institucional|página/i.test(s)) add('institucional', 'Possível página institucional', s);
    else if (/ampl/i.test(s)) add('classificacao_ampla', 'Classificação ampla', s);
    else if (!seen.has('penalidade')) add('penalidade', 'Atenção no match', s);
  });

  if (
    criterios.qualidade?.ausenteQualidadeDeclarada ||
    (criterios.qualidade?.motivos || []).some((m) => /incomplet/i.test(m))
  ) {
    add(
      'dados_incompletos',
      'Dados incompletos',
      'Faltam indicadores de qualidade ou campos estruturados — valide manualmente no site do edital.',
    );
  }

  if ((criterios.qualidade?.motivos || []).some((m) => /acesso limitado/i.test(m))) {
    add('acesso_limitado', 'Acesso limitado', 'A fonte sinaliza acesso limitado ao conteúdo completo.');
  }

  DIMENSOES.forEach(({ key, label, max }) => {
    const c = criterios[key];
    if (!c) return;
    const ausente = isDimensaoAusente(key, c, {});
    const pontos = Number(c.pontos) || 0;
    const pct = max > 0 ? Math.round((100 * pontos) / max) : 0;
    if (!ausente && pct > 0 && pct < 35) {
      add(
        `baixa_${key}`,
        `Baixa aderência — ${label}`,
        `${label} com pouca contribuição (${pontos}/${max} pts) — pode não ser o melhor encaixe nesta dimensão.`,
      );
    }
  });

  if (criterios.perfil?.motivos?.some((m) => /fora do encaixe|não é o foco/i.test(m))) {
    add(
      'perfil_fraco',
      'Perfil em atenção',
      'O perfil do cliente pode não ser o foco principal deste edital.',
    );
  }

  if (criterios.prazo?.pontos <= 3 && !criterios.prazo?.ausente && criterios.prazo?.motivo) {
    add('prazo_fraco', 'Prazo em atenção', criterios.prazo.motivo);
  }

  return alertas.slice(0, 8);
}

function buildDimensoes(criterios, criterioMeta, prazoInfoCard) {
  return DIMENSOES.map(({ key, label, max }) => {
    const c = criterios[key] || {};
    const pontos = Number(c.pontos) || 0;
    const ausente = isDimensaoAusente(key, c, criterioMeta);
    const pct = max > 0 ? Math.min(100, Math.round((100 * pontos) / max)) : 0;
    const nivel = nivelFromPct(pct, ausente);
    return {
      key,
      label,
      nivel,
      texto: buildTextoDimensao(key, c, prazoInfoCard),
      pontos,
      max,
      pct,
      ausente,
    };
  });
}

/**
 * Monta explicação estruturada para o card do Radar.
 * @param {object} hit — retorno de calcularMatchRadar (com criterios)
 * @param {object} editalFmt — edital no formato da UI
 * @param {object} prazoInfoCard — de prazoParaCard
 */
export function buildRadarCardExplanation(hit, editalFmt, prazoInfoCard) {
  const criterios = hit?.criterios || {};
  const pct = Number(hit?.percentual) || 0;
  const compat = hit?.compatUILabel || 'Baixa';

  const criterioMeta = {
    afinidade: {
      ausente: !!(criterios.afinidade?.ausenteCliente && criterios.afinidade?.ausenteEdital),
    },
    perfil: { ausente: !!criterios.perfil?.ausentePerfilEdital },
    tipo: {
      ausente: !!(criterios.tipo?.ausenteCliente && criterios.tipo?.ausenteEdital),
    },
    localizacao: { ausente: !!criterios.localizacao?.indefinido },
    prazo: { ausente: !!criterios.prazo?.ausente },
    valor: {
      ausente: !!(
        criterios.valor?.ausente ||
        criterios.valor?.ausenteCliente ||
        criterios.valor?.ausenteEdital
      ),
    },
  };

  const dimensoes = buildDimensoes(criterios, criterioMeta, prazoInfoCard);
  const positivos = collectPositivos(criterios, prazoInfoCard);
  const alertas = collectAlertas(hit, criterios, editalFmt, prazoInfoCard);

  const destaques = dimensoes
    .filter((d) => d.nivel === 'alto')
    .map((d) => d.label.toLowerCase());
  const resumoDestaque =
    destaques.length > 0
      ? ` Destaque em ${destaques.slice(0, 2).join(' e ')}.`
      : '';

  const resumo = `Compatibilidade ${compat} (${pct}%) com base no cadastro do cliente e nos dados do edital.${resumoDestaque}`;

  return {
    resumo,
    positivos,
    alertas,
    dimensoes,
    criterioMeta,
  };
}

export { DIMENSOES as RADAR_EXPLAIN_DIMENSOES };
