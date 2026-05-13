import { normalizeText } from './normalizeText';
import { prazoVencido, diasAtePrazoDashboard, isPrazoVencidoEdital } from './dates';
import { isTituloRuidoso } from './noise';
import { editalMatchesAllSearchTokens } from './search';
import { coerceStringArray } from './coerceArrays';
import { editalTemPdf, isSuspeitoValidacao, getFonte } from './editalFieldHelpers';

export const INITIAL_SIDEBAR_FILTERS = () => ({
  resourceTypeLegacy: '',
  tipoOportunidade: '',
  tipoRecurso: '',
  regiaoLegacy: '',
  areas: {},
  pais: '',
  uf: '',
  cidadeBusca: '',
  fonteBusca: '',
  fontesSelectedKeys: {},
  valorMin: '',
  valorMax: '',
  valorPreset: '',
  prazoPreset: '',
  perfil_ideal: {},
  setor_estrategico: {},
  area_tecnologica: {},
  docComPdf: false,
  docSemPdf: false,
  docComCodigo: false,
  docComLink: false,
  qualAlta: false,
  qualMedia: false,
  qualBaixa: false,
  qualIncomplete: false,
  qualSuspeitos: false,
  qualLimited: false,
  statusSelections: {},
  toggleIncluirEncerrados: false,
  toggleIncluirSuspeitos: false,
  toggleMostrarInativos: false,
  /** Só aplica se o usuário marcar explicitamente */
  toggleSoPdf: false,
  toggleAltaQualidade: false,
  toggleSomenteFavoritos: false,
});

function prazoReferencia(e) {
  return e.prazo_envio_raw ?? e.fim_inscricao_raw ?? e.dataLimite ?? null;
}

export function summarizeCatalogFlags(editals) {
  const list = editals ?? [];
  let abertos = 0;
  let encerrados = 0;
  let pdf = 0;
  let altaQ = 0;
  let semPrazo = 0;
  for (const e of list) {
    const p = prazoReferencia(e);
    if (!p) semPrazo++;
    else if (isPrazoVencidoEdital(e)) encerrados++;
    else abertos++;
    if (editalTemPdf(e)) pdf++;
    const q = Number(e.qualidade_dado_raw ?? 0);
    if (!Number.isNaN(q) && q >= 70) altaQ++;
  }
  return { abertos, encerrados, comPdf: pdf, altaQualidade: altaQ, semPrazo };
}

/** Conta quantos itens do catálogo seriam afetados por cada regra (com toggles atuais). */
export function computeHiddenHints(catalog, sidebar, pagePrefs) {
  let suspOcultos = 0;
  let encerradosOcultos = 0;
  let ruidosOcultos = 0;
  let inativosOcultos = 0;
  let semPdfOcultos = 0;
  let baixaQualOcultos = 0;

  for (const e of catalog ?? []) {
    if (!sidebar.toggleMostrarInativos && e.ativo === false) inativosOcultos++;
    if (!(pagePrefs.showRuidos ?? false) && isTituloRuidoso(e.titulo_original_raw ?? e.titulo)) ruidosOcultos++;
    if (!sidebar.toggleIncluirSuspeitos && isSuspeitoValidacao(e)) suspOcultos++;
    if (!sidebar.toggleIncluirEncerrados && isPrazoVencidoEdital(e)) encerradosOcultos++;
    if (sidebar.toggleSoPdf && !editalTemPdf(e)) semPdfOcultos++;
    if (sidebar.toggleAltaQualidade) {
      const q = Number(e.qualidade_dado_raw ?? e.qualidade_dado ?? NaN);
      if (!Number.isFinite(q) || q < 70) baixaQualOcultos++;
    }
  }
  return {
    suspOcultos,
    encerradosOcultos,
    ruidosOcultos,
    inativosOcultos,
    semPdfOcultos,
    baixaQualOcultos,
  };
}

export function rollupFacet(list, accessor) {
  const m = new Map();
  for (const e of list) {
    const raw = accessor(e);
    const label = String(raw ?? '').trim() || '— não informado';
    m.set(label, (m.get(label) || 0) + 1);
  }
  return [...m.entries()].sort((a, b) => {
    const c = b[1] - a[1];
    return c !== 0 ? c : a[0].localeCompare(b[0], 'pt-BR');
  });
}

export function loosenSidebarForFacet(sidebar, omit) {
  const s = { ...sidebar };
  if (omit === 'tipoRecurso') s.tipoRecurso = '';
  if (omit === 'tipoOportunidade') s.tipoOportunidade = '';
  if (omit === 'fontes') {
    s.fontesSelectedKeys = {};
    s.fonteBusca = '';
  }
  if (omit === 'areas') s.areas = {};
  if (omit === 'perfil') s.perfil_ideal = {};
  if (omit === 'setor') s.setor_estrategico = {};
  if (omit === 'area_tecnologica') s.area_tecnologica = {};
  return s;
}

function hasCodigoOuNumero(e) {
  return !!(
    (e.codigo_oportunidade_raw && String(e.codigo_oportunidade_raw).trim()) ||
    (e.numero_edital_raw && String(e.numero_edital_raw).trim()) ||
    (e.numero_chamada_raw && String(e.numero_chamada_raw).trim())
  );
}

/** Inativo só por cadastro — não usar substring genérica em texto de situação. */
function inactiveCadastro(e) {
  return e.ativo === false;
}

function matchStatusKey(e, key) {
  const vs = String(e.validacao_status_raw || '').toLowerCase();
  const ia = inactiveCadastro(e);
  const p = prazoReferencia(e);

  switch (key) {
    case 'ativo':
      return e.ativo !== false && !ia;
    case 'inativo':
      return ia;
    case 'sem_prazo':
      return !p;
    case 'encerrado':
      return isPrazoVencidoEdital(e);
    case 'aberto':
      return !!(p && !isPrazoVencidoEdital(e));
    case 'validado':
      return vs === 'valido' || vs === 'validado';
    case 'suspeito':
      return vs === 'suspeito';
    case 'incompleto':
      return vs === 'incompleto';
    case 'acesso_limitado':
      return vs === 'acesso_limitado';
    default:
      return false;
  }
}

function anyBox(obj) {
  if (!obj || typeof obj !== 'object') return false;
  return Object.values(obj).some(Boolean);
}

function keysChecked(obj) {
  if (!obj) return [];
  return Object.entries(obj)
    .filter(([, v]) => v)
    .map(([k]) => normalizeText(k));
}

function checkboxOrMatches(tokenListNorm, checkboxObj) {
  if (!anyBox(checkboxObj)) return true;
  const wanted = keysChecked(checkboxObj);
  if (!wanted.length) return true;
  if (!tokenListNorm.length) return false;
  return wanted.some((w) => tokenListNorm.some((ln) => ln.includes(w) || w.includes(ln)));
}

function passesQualidadeBlock(e, f) {
  const flags = [
    f.qualAlta && Number(e.qualidade_dado_raw ?? 0) >= 70,
    f.qualMedia && Number(e.qualidade_dado_raw ?? 0) >= 40 && Number(e.qualidade_dado_raw ?? 0) < 70,
    f.qualBaixa && Number(e.qualidade_dado_raw ?? 0) > 0 && Number(e.qualidade_dado_raw ?? 0) < 40,
    f.qualIncomplete && String(e.validacao_status_raw || '').toLowerCase() === 'incompleto',
    f.qualSuspeitos && String(e.validacao_status_raw || '').toLowerCase() === 'suspeito',
    f.qualLimited && String(e.validacao_status_raw || '').toLowerCase() === 'acesso_limitado',
  ];
  if (!flags.some(Boolean)) return true;
  return flags.some(Boolean);
}

function passesDocBlock(e, f) {
  const pdf = editalTemPdf(e);
  const link = !!(e.link_raw || e.linkOriginal);
  const checks = [
    !f.docComPdf || pdf,
    !f.docSemPdf || !pdf,
    !f.docComCodigo || hasCodigoOuNumero(e),
    !f.docComLink || link,
  ];
  return checks.every(Boolean);
}

function passesValorPreset(e, f, n) {
  if (!f.valorPreset) return true;
  const unknown = !(n > 0);
  switch (f.valorPreset) {
    case 'ate50k':
      return n > 0 && n <= 50000;
    case '50_500k':
      return n > 50000 && n <= 500000;
    case '500k_5m':
      return n > 500000 && n <= 5000000;
    case 'acima5m':
      return n > 5000000;
    case 'naoInformado':
      return unknown;
    default:
      return true;
  }
}

function passesPrazoQuick(e, f) {
  if (!f.prazoPreset) return true;
  const p = prazoReferencia(e);
  if (f.prazoPreset === 'sem') return !p;
  if (f.prazoPreset === 'encerrados') return !!(p && isPrazoVencidoEdital(e));

  const d = diasAtePrazoDashboard(p);
  if (d == null) return false;
  if (f.prazoPreset === 'd7') return d >= 0 && d <= 7;
  if (f.prazoPreset === 'd30') return d >= 0 && d <= 30;
  if (f.prazoPreset === 'd90') return d >= 0 && d <= 90;
  return true;
}

function valorNum(e) {
  return Number(e.valor_principal_num ?? e.valorMaximo ?? e.valor ?? 0);
}

/** Filtros detalhados da sidebar (além das regras base). */
function passAdvancedSidebar(e, sidebar) {
  const f = sidebar;
  const nVal = valorNum(e);

  if (f.resourceTypeLegacy) {
    const tgt = normalizeText(f.resourceTypeLegacy);
    const cur = normalizeText(`${e.tipoRecurso || ''} ${e.tipo_recurso_raw || ''}`);
    const hit = tgt.split(/\s/).some((frag) => cur.includes(frag));
    if (!hit) return false;
  }

  if (f.tipoOportunidade) {
    const t = normalizeText(f.tipoOportunidade.replace(/-/g, '_'));
    const v = normalizeText((e.tipo_oportunidade_raw || '').replace(/-/g, '_'));
    if (v !== t && !v.includes(t)) return false;
  }

  if (f.tipoRecurso) {
    const tgt = normalizeText(f.tipoRecurso.replace(/-/g, '_'));
    const cur = normalizeText(`${e.tipo_recurso_raw || ''} ${e.tipoRecurso || ''}`);
    if (!(cur.includes(tgt) || tgt.includes(cur))) return false;
  }

  if (f.regiaoLegacy) {
    const r = normalizeText(`${e.regiao_raw || ''} ${e.regiao || ''}`);
    if (!r.includes(normalizeText(f.regiaoLegacy))) return false;
  }

  if (f.pais) {
    const py = normalizeText(e.pais_raw || '');
    if (!py.includes(normalizeText(f.pais))) return false;
  }
  if (f.uf) {
    const u = String(e.uf_raw || e.estado_raw || '').toUpperCase();
    if (u !== String(f.uf).toUpperCase()) return false;
  }
  if (f.cidadeBusca) {
    if (!normalizeText(e.cidade_raw || '').includes(normalizeText(f.cidadeBusca))) return false;
  }

  const fonteHay = normalizeText(getFonte(e));
  if (anyBox(f.fontesSelectedKeys)) {
    const keysSel = keysChecked(f.fontesSelectedKeys);
    if (!keysSel.some((k) => fonteHay.includes(k))) return false;
  } else if (f.fonteBusca) {
    const fq = normalizeText(f.fonteBusca);
    if (!fonteHay.includes(fq)) return false;
  }

  const vmin = parseFloat(String(f.valorMin).replace(',', '.'));
  const vmax = parseFloat(String(f.valorMax).replace(',', '.'));
  if (!Number.isNaN(vmin) && nVal < vmin) return false;
  if (!Number.isNaN(vmax) && vmax > 0 && nVal > vmax) return false;
  if (!passesValorPreset(e, f, nVal)) return false;

  if (!passesPrazoQuick(e, f)) return false;

  const areaChunks = coerceStringArray(e.area).map(normalizeText);
  const areaExtra = coerceStringArray(e.area_cientifica_raw).map(normalizeText);
  if (!checkboxOrMatches([...areaChunks, ...areaExtra].filter(Boolean), f.areas)) return false;

  const perfilChunks = coerceStringArray(e.perfil_ideal_raw).map(normalizeText);
  const pas = coerceStringArray(e.publico_alvo_arr_raw).map(normalizeText);
  const pub = normalizeText(e.publico_alvo_raw || '');
  if (!checkboxOrMatches([...perfilChunks, ...pas, pub].filter(Boolean), f.perfil_ideal)) return false;

  const setNorm = coerceStringArray(e.setor_estrategico_raw).map(normalizeText);
  const setFlat = normalizeText(e.setor_estrategico_flat || '');
  if (!checkboxOrMatches(setNorm.concat(setFlat ? [setFlat] : []), f.setor_estrategico)) return false;

  const atNorm = coerceStringArray(e.area_tecnologica_raw).map(normalizeText);
  const atFlat = normalizeText(e.area_tecnologica_flat || '');
  if (!checkboxOrMatches(atNorm.concat(atFlat ? [atFlat] : []), f.area_tecnologica)) return false;

  if (!passesQualidadeBlock(e, f)) return false;
  if (!passesDocBlock(e, f)) return false;

  return true;
}

function step(name, arr, pred, dbg) {
  const out = arr.filter(pred);
  const removed = arr.length - out.length;
  dbg[`after_${name}`] = out.length;
  dbg[`removedBy_${name}`] = removed;
  return out;
}

/**
 * Pipeline único: retorna lista filtrada, hints de exclusão e objeto de debug (contagens).
 */
export function filterCatalog({
  catalog,
  sidebar,
  searchTokens,
  pagePrefs,
}) {
  const list = Array.isArray(catalog) ? [...catalog] : [];

  const filterDebug = {
    totalOriginal: list.length,
  };

  let pool = list;

  pool = step(
    'ativo',
    pool,
    (e) => sidebar.toggleMostrarInativos || e.ativo !== false,
    filterDebug,
  );

  pool = step(
    'suspeito',
    pool,
    (e) => sidebar.toggleIncluirSuspeitos || !isSuspeitoValidacao(e),
    filterDebug,
  );

  pool = step(
    'prazoVencido',
    pool,
    (e) => sidebar.toggleIncluirEncerrados || !isPrazoVencidoEdital(e),
    filterDebug,
  );

  pool = step(
    'tituloRuidoso',
    pool,
    (e) => (pagePrefs.showRuidos ?? false) || !isTituloRuidoso(e.titulo_original_raw ?? e.titulo),
    filterDebug,
  );

  pool = step(
    'toggleSoPdf',
    pool,
    (e) => !sidebar.toggleSoPdf || editalTemPdf(e),
    filterDebug,
  );

  pool = step(
    'toggleAltaQualidade',
    pool,
    (e) => {
      if (!sidebar.toggleAltaQualidade) return true;
      const q = Number(e.qualidade_dado_raw ?? e.qualidade_dado ?? NaN);
      return Number.isFinite(q) && q >= 70;
    },
    filterDebug,
  );

  const realKeys =
    sidebar.statusSelections && typeof sidebar.statusSelections === 'object'
      ? Object.keys(sidebar.statusSelections).filter((k) => sidebar.statusSelections[k])
      : [];
  if (realKeys.length) {
    pool = step(
      'statusPreset',
      pool,
      (e) => realKeys.some((sk) => matchStatusKey(e, sk)),
      filterDebug,
    );
  } else {
    filterDebug.after_statusPreset = pool.length;
    filterDebug.removedBy_statusPreset = 0;
  }

  pool = step(
    'buscaTokens',
    pool,
    (e) => editalMatchesAllSearchTokens(e, searchTokens),
    filterDebug,
  );

  const nAdv0 = pool.length;
  pool = pool.filter((e) => passAdvancedSidebar(e, sidebar));
  filterDebug.removedBy_advancedSidebar = nAdv0 - pool.length;
  filterDebug.after_advancedSidebar = pool.length;

  filterDebug.final = pool.length;

  const hiddenMeta = computeHiddenHints(catalog, sidebar, pagePrefs);

  return {
    filtered: pool,
    hiddenMeta,
    filterDebug,
  };
}

/** Alias para leitura clara nos componentes */
export function aplicarFiltrosEditais(...args) {
  return filterCatalog(...args);
}
