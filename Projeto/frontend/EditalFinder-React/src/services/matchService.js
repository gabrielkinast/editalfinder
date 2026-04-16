// ─── Helpers de texto ────────────────────────────────────────────────────────

function tokenizar(texto) {
  return (texto || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')       // remove acentos
    .split(/[,;\s\/\-\+\.]+/)
    .map(t => t.trim())
    .filter(t => t.length > 2);
}

function intersecao(a, b) {
  return a.filter(ta => b.some(tb => tb.includes(ta) || ta.includes(tb)));
}

function textoContem(texto, termos) {
  const t = (texto || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  return termos.some(p => t.includes(p));
}

// ─── Mapeamento de porte ──────────────────────────────────────────────────────

const PORTE_TERMOS = {
  'MEI':    ['mei', 'micro empreendedor', 'microempreendedor', 'empreendedor individual'],
  'ME':     ['micro empresa', 'microempresa', 'pequena empresa', 'mpe'],
  'EPP':    ['epp', 'empresa pequeno porte', 'pequeno porte', 'pequena', 'mpe'],
  'Média':  ['media empresa', 'empresa media', 'medio porte'],
  'Grande': ['grande empresa', 'grande porte', 'grande'],
};

const PORTE_EXCLUSOES = {
  'MEI':    ['grande', 'media empresa', 'grande porte', 'medio porte'],
  'ME':     ['grande', 'media empresa', 'grande porte'],
  'EPP':    ['grande', 'grande porte'],
  'Média':  ['mei', 'microempreendedor'],
  'Grande': ['mei', 'micro', 'pequena'],
};

// ─── Score ────────────────────────────────────────────────────────────────────

/**
 * Calcula o score de compatibilidade entre um cliente e um edital.
 * Usa exclusivamente os campos do perfil do cliente — nunca o campo score do banco.
 *
 * Critérios e peso máximo:
 *   1. Área / Temas         → até 35 pts
 *   2. Localização          → até 20 pts
 *   3. Porte / Elegibilidade→ até 20 pts
 *   4. Faixa de Valor       → até 15 pts
 *   5. Regularidade         → até 10 pts
 *   Total máximo            → 100 pts
 *
 * @param {Object} cliente - Registro da tabela `cliente`
 * @param {Object} edital  - Objeto formatado retornado pelo dataService
 * @returns {{ score: number, compatibilidade: string, razoes: string[], detalhes: Object }}
 */
export function calcularScore(cliente, edital) {
  let score = 0;
  const razoes   = [];
  const detalhes = { area: 0, localizacao: 0, porte: 0, valor: 0, regularidade: 0 };

  // ══════════════════════════════════════════════════════════════════════════
  // 1. ÁREA / TEMAS  (até 35 pts)
  //    Cruza: area_inovacao + setor + interesse_temas + descricao_projeto
  //    com:   temas + titulo + objetivo + publico_alvo + elegibilidade + area
  // ══════════════════════════════════════════════════════════════════════════
  const textoCliente = [
    cliente.area_inovacao,
    cliente.setor,
    cliente.interesse_temas,
    cliente.descricao_projeto,
  ].filter(Boolean).join(' ');

  const textoEdital = [
    edital.area,
    edital.titulo,
    edital.temas,       // campo temas do banco
    edital.objetivo,
    edital.publico_alvo,
    edital.elegibilidade,
  ].filter(Boolean).join(' ');

  const kwCliente  = tokenizar(textoCliente);
  const kwEdital   = tokenizar(textoEdital);
  const matchArea  = intersecao(kwCliente, kwEdital);
  const ptArea     = Math.min(35, matchArea.length * 7);

  if (ptArea > 0) {
    detalhes.area = ptArea;
    score += ptArea;
    razoes.push(`Área: ${[...new Set(matchArea)].slice(0, 3).join(', ')}`);
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 2. LOCALIZAÇÃO  (até 20 pts)
  //    Compara estado/regiao do cliente com estado/regiao/localidade do edital
  // ══════════════════════════════════════════════════════════════════════════
  const estadoCli   = (cliente.estado   || '').toLowerCase().trim();
  const regiaoCli   = (cliente.regiao   || '').toLowerCase().trim();
  const estadoEd    = (edital.estado    || '').toLowerCase().trim();
  const regiaoEd    = (edital.regiao    || '').toLowerCase().trim();
  const localEd     = (edital.localidade|| '').toLowerCase().trim();

  const isNacional  = !estadoEd || estadoEd === 'nacional' || localEd === 'nacional' || regiaoEd === 'nacional';
  const mesmoEstado = estadoCli && estadoEd && (estadoCli === estadoEd || estadoEd.includes(estadoCli));
  const mesmaRegiao = regiaoCli && regiaoEd  && (regiaoEd.includes(regiaoCli) || regiaoCli.includes(regiaoEd));

  let ptLocal = 0;
  if (isNacional || mesmoEstado) {
    ptLocal = 20;
    razoes.push(isNacional ? 'Abrangência nacional' : `Estado: ${cliente.estado?.toUpperCase()}`);
  } else if (mesmaRegiao) {
    ptLocal = 15;
    razoes.push(`Região: ${cliente.regiao}`);
  } else if (!estadoEd && !regiaoEd) {
    ptLocal = 10;
  }

  detalhes.localizacao = ptLocal;
  score += ptLocal;

  // ══════════════════════════════════════════════════════════════════════════
  // 3. PORTE / ELEGIBILIDADE  (até 20 pts)
  //    Verifica se o porte da empresa encaixa no público-alvo do edital
  // ══════════════════════════════════════════════════════════════════════════
  const porte           = (cliente.porte_empresa || '').trim();
  const textoElegib     = [edital.elegibilidade, edital.publico_alvo, edital.titulo, edital.area]
                            .filter(Boolean).join(' ');
  const termosPorte     = PORTE_TERMOS[porte]    || [];
  const termosExclusao  = PORTE_EXCLUSOES[porte] || [];

  const porteBate       = termosPorte.length > 0 && textoContem(textoElegib, termosPorte);
  const porteExcluido   = termosExclusao.length > 0 && textoContem(textoElegib, termosExclusao);
  const semRestricao    = !textoContem(textoElegib, [
    'mei', 'micro', 'pequena', 'grande', 'medio porte', 'grande porte',
  ]);

  let ptPorte = 0;
  if (porteBate && !porteExcluido) {
    ptPorte = 20;
    razoes.push(`Porte ${porte} compatível`);
  } else if (semRestricao || (!porteBate && !porteExcluido)) {
    ptPorte = 15;
  }

  detalhes.porte = ptPorte;
  score += ptPorte;

  // ══════════════════════════════════════════════════════════════════════════
  // 4. FAIXA DE VALOR DE INTERESSE  (até 15 pts)
  //    Compara interesse_valor_min/max do cliente com valor_minimo/maximo do edital
  // ══════════════════════════════════════════════════════════════════════════
  const cliMin  = parseFloat(cliente.interesse_valor_min) || 0;
  const cliMax  = parseFloat(cliente.interesse_valor_max) || 0;
  const edMin   = parseFloat(edital.valorMinimo)          || 0;
  const edMax   = parseFloat(edital.valorMaximo || edital.valor) || 0;

  let ptValor = 0;
  if (cliMin === 0 && cliMax === 0) {
    // Cliente não definiu faixa — neutro, não prejudica
    ptValor = 10;
  } else if (edMin === 0 && edMax === 0) {
    // Edital não tem valor definido — neutro
    ptValor = 8;
  } else {
    const overlapMin = Math.max(cliMin, edMin);
    const overlapMax = Math.min(cliMax > 0 ? cliMax : Infinity, edMax > 0 ? edMax : Infinity);
    if (overlapMax >= overlapMin) {
      // Existe sobreposição de faixas
      const rangeCliente = (cliMax > 0 ? cliMax : edMax) - cliMin;
      const overlapSize  = overlapMax - overlapMin;
      const cobertura    = rangeCliente > 0 ? overlapSize / rangeCliente : 1;
      ptValor = cobertura >= 0.5 ? 15 : 8;
      if (ptValor === 15) razoes.push('Valor dentro da faixa de interesse');
    }
  }

  detalhes.valor = ptValor;
  score += ptValor;

  // ══════════════════════════════════════════════════════════════════════════
  // 5. REGULARIDADE E ELEGIBILIDADE  (até 10 pts)
  //    Bônus por regularidade fiscal/trabalhista e disponibilidade de contrapartida
  // ══════════════════════════════════════════════════════════════════════════
  let ptReg = 0;

  if (cliente.regular_fiscal && cliente.regular_trabalhista) {
    ptReg += 4;
  } else if (cliente.regular_fiscal || cliente.regular_trabalhista) {
    ptReg += 2;
  }

  if (cliente.possui_certidao_negativa) {
    ptReg += 3;
  }

  // Bônus extra se edital exige contrapartida e cliente tem disponibilidade
  const editalExigeContrapartida = textoContem(edital.contrapartida || '', ['sim', 'obrigatoria', 'exigida', 'requerida']);
  if (cliente.disponibilidade_contrapartida) {
    ptReg += editalExigeContrapartida ? 3 : 1;
  }

  ptReg = Math.min(ptReg, 10);
  detalhes.regularidade = ptReg;
  score += ptReg;

  // ══════════════════════════════════════════════════════════════════════════
  // Classificação final
  // ══════════════════════════════════════════════════════════════════════════
  score = Math.min(Math.round(score), 100);

  let compatibilidade;
  if      (score >= 75) compatibilidade = 'Alta';
  else if (score >= 45) compatibilidade = 'Média';
  else                  compatibilidade = 'Baixa';

  return { score, compatibilidade, razoes, detalhes };
}

/**
 * Retorna lista de editais ordenada por score calculado para um cliente.
 * Nunca usa o campo score do banco de dados.
 *
 * @param {Object}   cliente
 * @param {Object[]} editais
 * @returns {Array<{ edital, score, compatibilidade, razoes, detalhes }>}
 */
export function recomendarEditais(cliente, editais) {
  return editais
    .map(edital => ({ edital, ...calcularScore(cliente, edital) }))
    .sort((a, b) => b.score - a.score);
}
