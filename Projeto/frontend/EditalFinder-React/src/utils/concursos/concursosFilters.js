import { labelStatus, labelTipoSelecao, listTipoSelecaoOptions } from './concursosLabels.js';

export const TAB_DEFS = [
  { id: 'all', label: 'Todos', tipos: null },
  {
    id: 'concurso_publico',
    label: 'Concursos públicos',
    tipos: ['concurso_publico', 'processo_seletivo'],
  },
  { id: 'professor', label: 'Professores', tipos: ['professor'] },
  { id: 'tecnico_administrativo', label: 'Técnicos/Administrativos', tipos: ['tecnico_administrativo'] },
  { id: 'vestibulares', label: 'Vestibulares', tipos: ['vestibular', 'programa_ingresso'] },
  { id: 'residencia', label: 'Residências', tipos: ['residencia'] },
  { id: 'bolsa_estudo', label: 'Bolsas', tipos: ['bolsa_estudo'] },
];

/** Select fixo de fontes/bancas (poucas opções estáveis). */
export const FONTE_BANCA_OPTIONS = [
  { value: 'quadrix', label: 'Quadrix' },
  { value: 'legalle', label: 'Legalle' },
  { value: 'objetiva', label: 'Objetiva' },
  { value: 'fundatec', label: 'Fundatec' },
  { value: 'ibfc', label: 'IBFC' },
  { value: 'pci_concursos', label: 'PCI Concursos' },
  { value: 'aocp', label: 'AOCP' },
  { value: 'fgv', label: 'FGV' },
  { value: 'cebraspe', label: 'Cebraspe' },
  { value: 'comvest', label: 'Comvest' },
  { value: 'ufrgs_cv', label: 'UFRGS' },
  { value: 'coperve', label: 'Coperve' },
  { value: 'fuvest', label: 'Fuvest' },
];

export const TIPO_INSTITUICAO_OPTIONS = [
  { value: 'prefeitura', label: 'Prefeitura / Município' },
  { value: 'camara', label: 'Câmara Municipal' },
  { value: 'conselho', label: 'Conselho' },
  { value: 'universidade', label: 'Universidade' },
  { value: 'governo_federal', label: 'Governo Federal' },
  { value: 'governo_estadual', label: 'Governo Estadual' },
  { value: 'seguranca_defesa', label: 'Segurança / Defesa' },
  { value: 'empresa_publica', label: 'Empresa pública' },
  { value: 'outros', label: 'Outros' },
];

export function getInitialConcursosFilters() {
  return {
    search: '',
    fonte: '',
    tipoSelecao: '',
    status: '',
    estado: '',
    municipio: '',
    instituicaoOrgao: '',
    tipoInstituicao: '',
    escolaridade: '',
    areaCargo: '',
    comEdital: false,
    comDataFimInscricao: false,
    inscricoesAbertas: false,
    provaProxima: false,
    comSalarioBolsa: false,
    comTaxa: false,
    somenteValidos: false,
  };
}

function normalizeInstBlob(row) {
  return [row?.orgao, row?.instituicao, row?.titulo]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{M}/gu, '');
}

/**
 * Heurística simples de tipo de instituição (client-side).
 * @returns {string} id em TIPO_INSTITUICAO_OPTIONS
 */
export function inferTipoInstituicao(row) {
  const blob = normalizeInstBlob(row);
  if (!blob.trim()) return 'outros';

  if (
    /\b(exercito|exército|marinha|aeronautica|aeronáutica|policia penal|polícia penal|pmgo|cbm|policia militar|polícia militar)\b/i.test(
      blob
    )
  ) {
    return 'seguranca_defesa';
  }
  if (/\b(governo federal|ministerio|ministério)\b/i.test(blob)) {
    return 'governo_federal';
  }
  if (
    /\bsecretaria\b/i.test(blob) &&
    (/\b(governo do estado|estado de|estadual)\b/i.test(blob) ||
      /\b(ac|al|ap|am|ba|ce|df|es|go|ma|mt|ms|mg|pa|pb|pr|pe|pi|rj|rn|rs|ro|rr|sc|sp|se|to)\b/i.test(
        blob
      ) ||
      Boolean(row?.estado))
  ) {
    return 'governo_estadual';
  }
  if (
    /\b(universidade|unicamp|ufrgs|ufsc|ufmg|ufpr|ufba|ufpe|ufg|ufc|unifesp|usp|universidade de)\b/i.test(
      blob
    )
  ) {
    return 'universidade';
  }
  if (
    /\bconselho\b/i.test(blob) ||
    /\b(cref|crea|creci|coren|crm|crf|crn|crp|crtr|conter|core|crt|cfm|cfn)\b/i.test(blob)
  ) {
    return 'conselho';
  }
  if (/\b(prefeitura|municipio|município)\b/i.test(blob)) {
    return 'prefeitura';
  }
  if (/\bcamara\b|\bcâmara\b/i.test(blob)) {
    return 'camara';
  }
  if (
    /\b(companhia|autarquia|empresa publica|empresa pública|sanasa|sabesp|copasa|cedae|cesama)\b/i.test(
      blob
    )
  ) {
    return 'empresa_publica';
  }
  return 'outros';
}

export function buildInstituicaoOrgaoBlob(row) {
  return normalizeInstBlob(row);
}

export function uniqSorted(values) {
  const set = new Set(
    (values || [])
      .map((v) => (v == null ? '' : String(v).trim()))
      .filter(Boolean)
  );
  return [...set].sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

export function filterByTab(rows, tabId) {
  const def = TAB_DEFS.find((t) => t.id === tabId);
  if (!def || !def.tipos) return rows;
  const allow = new Set(def.tipos);
  return rows.filter((r) => allow.has(String(r?.tipo_selecao || '').trim()));
}

function hasEdital(row) {
  const u = row?.link_edital;
  return typeof u === 'string' && u.trim().length > 0;
}

function hasDataFim(row) {
  const d = row?.data_fim_inscricao;
  return d != null && String(d).trim() !== '';
}

function hasSalarioBolsa(row) {
  const min = Number(row?.salario_min);
  const max = Number(row?.salario_max);
  return (Number.isFinite(min) && min > 0) || (Number.isFinite(max) && max > 0);
}

function hasTaxa(row) {
  const t = Number(row?.taxa_inscricao);
  return Number.isFinite(t) && t > 0;
}

/** Texto unificado para busca (Fase 2). */
export function buildConcursoSearchBlob(row) {
  const tags = Array.isArray(row?.tags) ? row.tags.join(' ') : '';
  return [
    row?.titulo,
    row?.orgao,
    row?.instituicao,
    row?.banca,
    row?.cargo,
    row?.curso,
    row?.area,
    row?.municipio,
    row?.estado,
    row?.fonte,
    tags,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
}

export function applyConcursosFilters(rows, filters) {
  let out = rows;

  if (filters.fonte) {
    out = out.filter((r) => String(r?.fonte || '').trim() === filters.fonte);
  }
  if (filters.tipoSelecao) {
    out = out.filter((r) => String(r?.tipo_selecao || '') === filters.tipoSelecao);
  }
  if (filters.status) {
    out = out.filter((r) => String(r?.status || '').trim() === filters.status);
  }
  if (filters.estado) {
    out = out.filter((r) => String(r?.estado || '').trim() === filters.estado);
  }
  if (filters.municipio) {
    out = out.filter((r) => String(r?.municipio || '').trim() === filters.municipio);
  }
  if (filters.instituicaoOrgao) {
    const q = filters.instituicaoOrgao.trim().toLowerCase();
    out = out.filter((r) => buildInstituicaoOrgaoBlob(r).includes(q));
  }
  if (filters.tipoInstituicao) {
    out = out.filter((r) => inferTipoInstituicao(r) === filters.tipoInstituicao);
  }
  if (filters.escolaridade) {
    out = out.filter((r) => String(r?.nivel_escolaridade || '').trim() === filters.escolaridade);
  }

  if (filters.areaCargo) {
    const q = filters.areaCargo.trim().toLowerCase();
    out = out.filter((r) => {
      const blob = [r?.area, r?.cargo, r?.curso]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return blob.includes(q);
    });
  }

  if (filters.comEdital) {
    out = out.filter(hasEdital);
  }
  if (filters.comDataFimInscricao) {
    out = out.filter(hasDataFim);
  }
  if (filters.inscricoesAbertas) {
    out = out.filter((r) => r?.inscricoes_abertas === true);
  }
  if (filters.provaProxima) {
    out = out.filter((r) => r?.prova_proxima === true);
  }
  if (filters.comSalarioBolsa) {
    out = out.filter(hasSalarioBolsa);
  }
  if (filters.comTaxa) {
    out = out.filter(hasTaxa);
  }
  if (filters.somenteValidos) {
    out = out.filter((r) => String(r?.validacao_status || '').trim() === 'valido');
  }

  const q = (filters.search || '').trim().toLowerCase();
  if (q) {
    out = out.filter((r) => buildConcursoSearchBlob(r).includes(q));
  }

  return out;
}

export function sortConcursos(rows) {
  return [...rows].sort((a, b) => {
    const da = a?.data_fim_inscricao;
    const db = b?.data_fim_inscricao;
    if (da && db) return String(da).localeCompare(String(db), 'en-CA');
    if (da && !db) return -1;
    if (!da && db) return 1;
    return (Number(b?.id_concurso) || 0) - (Number(a?.id_concurso) || 0);
  });
}

export function buildFilterOptions(rows) {
  const tiposPresent = new Set(rows.map((r) => String(r?.tipo_selecao || '').trim()).filter(Boolean));
  const fontesPresent = new Set(rows.map((r) => String(r?.fonte || '').trim()).filter(Boolean));
  const tiposInstPresent = new Set(rows.map((r) => inferTipoInstituicao(r)));

  return {
    fonte: FONTE_BANCA_OPTIONS.filter((o) => fontesPresent.has(o.value)),
    fonteAll: FONTE_BANCA_OPTIONS,
    tipoSelecao: listTipoSelecaoOptions().filter((o) => tiposPresent.has(o.value)),
    status: uniqSorted(rows.map((r) => r?.status)),
    estado: uniqSorted(rows.map((r) => r?.estado)),
    municipio: uniqSorted(rows.map((r) => r?.municipio)),
    tipoInstituicao: TIPO_INSTITUICAO_OPTIONS.filter((o) => tiposInstPresent.has(o.value)),
    escolaridade: uniqSorted(rows.map((r) => r?.nivel_escolaridade)),
  };
}

export function labelFonteBanca(fonte) {
  const hit = FONTE_BANCA_OPTIONS.find((o) => o.value === fonte);
  return hit?.label || String(fonte || '').replace(/_/g, ' ');
}

export function computeConcursosStats(rows) {
  const vestIngresso = rows.filter((r) =>
    ['vestibular', 'programa_ingresso'].includes(String(r?.tipo_selecao || '').trim())
  ).length;
  return {
    total: rows.length,
    inscricoesAbertas: rows.filter((r) => r?.inscricoes_abertas).length,
    comEdital: rows.filter(hasEdital).length,
    dadosValidos: rows.filter((r) => String(r?.validacao_status || '').trim() === 'valido').length,
    provasProximas: rows.filter((r) => r?.prova_proxima).length,
    vestibularesIngresso: vestIngresso,
    concursosPublicos: rows.filter((r) =>
      ['concurso_publico', 'processo_seletivo'].includes(String(r?.tipo_selecao || '').trim())
    ).length,
  };
}

const CHIP_DEFS = [
  { key: 'search', label: 'Busca', format: (v) => `«${v}»` },
  { key: 'fonte', label: 'Fonte/Banca', format: (v) => labelFonteBanca(v) },
  { key: 'tipoSelecao', label: 'Tipo', format: (v) => labelTipoSelecao(v) },
  { key: 'status', label: 'Status', format: (v) => labelStatus(v) },
  { key: 'estado', label: 'Estado', format: (v) => v },
  { key: 'municipio', label: 'Município', format: (v) => v },
  { key: 'instituicaoOrgao', label: 'Instituição/órgão', format: (v) => v },
  {
    key: 'tipoInstituicao',
    label: 'Tipo de instituição',
    format: (v) => TIPO_INSTITUICAO_OPTIONS.find((o) => o.value === v)?.label || v,
  },
  { key: 'escolaridade', label: 'Escolaridade', format: (v) => v },
  { key: 'areaCargo', label: 'Área/cargo', format: (v) => v },
  { key: 'comEdital', label: 'Com edital', format: () => 'sim' },
  { key: 'comDataFimInscricao', label: 'Com fim de inscrição', format: () => 'sim' },
  { key: 'inscricoesAbertas', label: 'Inscrições abertas', format: () => 'sim' },
  { key: 'provaProxima', label: 'Prova próxima', format: () => 'sim' },
  { key: 'comSalarioBolsa', label: 'Com salário/bolsa', format: () => 'sim' },
  { key: 'comTaxa', label: 'Com taxa', format: () => 'sim' },
  { key: 'somenteValidos', label: 'Dados válidos', format: () => 'sim' },
];

export function getActiveFilterChips(filters, tabId) {
  const chips = [];
  const initial = getInitialConcursosFilters();

  for (const def of CHIP_DEFS) {
    const val = filters[def.key];
    const init = initial[def.key];
    if (typeof val === 'boolean') {
      if (val && !init) {
        chips.push({ key: def.key, label: def.label, display: def.format(true) });
      }
    } else if (val && val !== init) {
      chips.push({ key: def.key, label: def.label, display: def.format(val) });
    }
  }

  if (tabId && tabId !== 'all') {
    const tab = TAB_DEFS.find((t) => t.id === tabId);
    if (tab) {
      chips.push({ key: '__tab', label: 'Aba', display: tab.label, locked: true });
    }
  }

  return chips;
}

export function countActiveFilters(filters, tabId) {
  return getActiveFilterChips(filters, tabId).filter((c) => !c.locked).length;
}

/** Mensagem de estado vazio com filtros ativos. */
export function describeConcursosEmptyHint(filters, tabId, { tabCount, filteredCount }) {
  const chips = getActiveFilterChips(filters, tabId).filter((c) => !c.locked);
  const parts = chips.map((c) => `${c.label}: ${c.display}`);
  const tab = TAB_DEFS.find((t) => t.id === tabId);
  const lines = [];

  if (tab && tabId !== 'all') {
    lines.push(`Aba «${tab.label}» (${tabCount} registo(s) na aba).`);
  }
  if (parts.length) {
    lines.push(`Filtros ativos: ${parts.join(' · ')}.`);
  } else if (tabId !== 'all') {
    lines.push('Nenhum filtro lateral aplicado; só a aba restringe os resultados.');
  } else {
    lines.push('Nenhum filtro aplicado.');
  }
  if (filteredCount === 0 && tabCount > 0) {
    lines.push('Experimente remover filtros ou mudar de aba.');
  }
  return lines.join(' ');
}

export function removeFilterKey(filters, key) {
  const next = { ...filters };
  const initial = getInitialConcursosFilters();
  if (key in initial) {
    next[key] = initial[key];
  }
  return next;
}
