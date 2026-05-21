import { calculateClientProfileCompleteness } from './calculateClientProfileCompleteness';
import {
  clientFormStateFromCliente,
  emptyPerfilConsultivo,
  hydratePerfilFromClienteRow,
} from './clientePerfilConsultivo';
import {
  BRIEFING_CRITERIOS_ACEITE,
  BRIEFING_DOCUMENTOS,
  BRIEFING_FAIXA_VALOR,
  BRIEFING_TIPOS_RECURSO,
} from './clienteBriefingConfig';

function hasText(v) {
  return v != null && String(v).trim() !== '';
}

function parseTags(text) {
  if (!hasText(text)) return [];
  return String(text)
    .split(/[,;|\n]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function tagsToText(tags) {
  return Array.isArray(tags) ? tags.join(', ') : '';
}

function docIdsFromPerfil(doc) {
  const ids = Array.isArray(doc?.documentos_disponiveis) ? [...doc.documentos_disponiveis] : [];
  if (ids.length) return ids;
  const out = [];
  for (const def of BRIEFING_DOCUMENTOS) {
    if (!def.docKey) continue;
    if (doc?.[def.docKey] === true) out.push(def.id);
  }
  if (!out.length && doc?.contrato_social === false) return ['nenhum'];
  return out;
}

function applyDocIdsToPerfil(doc, ids) {
  const next = { ...doc, documentos_disponiveis: [...ids] };
  const hasNenhum = ids.includes('nenhum');
  for (const def of BRIEFING_DOCUMENTOS) {
    if (!def.docKey) continue;
    if (hasNenhum) {
      next[def.docKey] = false;
    } else {
      next[def.docKey] = ids.includes(def.id) ? true : next[def.docKey];
    }
  }
  return next;
}

function criteriosToFlags(criterios) {
  const set = new Set(Array.isArray(criterios) ? criterios : []);
  return {
    aceita_internacional: set.has('internacional') ? true : null,
    aceita_licitacao: set.has('licitacao') ? true : null,
    aceita_sem_prazo: set.has('fluxo_continuo') ? true : null,
  };
}

function flagsToCriterios(pref) {
  const out = [];
  if (Array.isArray(pref?.criterios_aceite) && pref.criterios_aceite.length) {
    return [...pref.criterios_aceite];
  }
  if (pref?.aceita_internacional) out.push('internacional');
  if (pref?.aceita_licitacao) out.push('licitacao');
  if (pref?.aceita_sem_prazo) out.push('fluxo_continuo');
  return out;
}

function faixaFromCliente(c, perfil) {
  const id = perfil?.preferencias_fomento?.faixa_valor_interesse;
  if (id) return id;
  const min = Number(c?.interesse_valor_min);
  const max = Number(c?.interesse_valor_max);
  if (!min && max === 50000) return 'ate_50k';
  if (min === 50000 && max === 250000) return '50k_250k';
  if (min === 250000 && max === 1000000) return '250k_1m';
  if (min >= 1000000) return 'acima_1m';
  if (!min && !max) return 'indefinido';
  return '';
}

/**
 * Estado do formulário de briefing a partir do cliente normalizado.
 * @param {object|null} cliente
 */
export function briefingStateFromCliente(cliente) {
  const c = cliente || {};
  const perfil = hydratePerfilFromClienteRow(c);
  const diag = perfil.diagnostico_consultor || {};
  const tec = perfil.perfil_tecnologico || {};
  const pref = perfil.preferencias_fomento || {};
  const doc = perfil.documentacao || {};

  const temasRaw =
    tec.temas_prioritarios ||
    tec.areas_tecnologicas ||
    c.area_inovacao ||
    c.interesse_temas ||
    '';

  return {
    contexto_cliente: diag.contexto_cliente || tec.principais_atividades || '',
    descricao_projeto:
      tec.descricao_projeto || c.descricao_projeto || tec.principais_atividades || '',
    temas_prioritarios: temasRaw,
    tipos_recurso: Array.isArray(pref.tipos_recurso) ? [...pref.tipos_recurso] : [],
    faixa_valor_interesse: faixaFromCliente(c, perfil),
    criterios_aceite: flagsToCriterios(pref),
    documentos_disponiveis: docIdsFromPerfil(doc),
    observacoes_internas: diag.observacoes_internas || '',
  };
}

export function emptyBriefingState() {
  return briefingStateFromCliente(null);
}

function mergeText(existing, incoming) {
  if (!hasText(incoming)) return existing;
  return String(incoming).trim();
}

/**
 * Aplica briefing ao form state do ClientForm (merge em perfil + colunas legadas).
 * @param {object} formState — saída de clientFormStateFromCliente
 * @param {ReturnType<briefingStateFromCliente>} briefing
 */
export function applyBriefingToFormState(formState, briefing) {
  const b = briefing || {};
  const next = { ...formState, perfil: { ...emptyPerfilConsultivo(), ...(formState?.perfil || {}) } };
  const perfil = next.perfil;

  perfil.diagnostico_consultor = {
    ...perfil.diagnostico_consultor,
    contexto_cliente: mergeText(perfil.diagnostico_consultor?.contexto_cliente, b.contexto_cliente),
    observacoes_internas: mergeText(
      perfil.diagnostico_consultor?.observacoes_internas,
      b.observacoes_internas,
    ),
  };

  const temas = hasText(b.temas_prioritarios) ? String(b.temas_prioritarios).trim() : '';
  perfil.perfil_tecnologico = {
    ...perfil.perfil_tecnologico,
    descricao_projeto: mergeText(perfil.perfil_tecnologico?.descricao_projeto, b.descricao_projeto),
    temas_prioritarios: temas || perfil.perfil_tecnologico?.temas_prioritarios || '',
    principais_atividades: mergeText(
      perfil.perfil_tecnologico?.principais_atividades,
      b.contexto_cliente,
    ),
    areas_tecnologicas: temas || perfil.perfil_tecnologico?.areas_tecnologicas || '',
  };

  if (hasText(b.descricao_projeto)) {
    next.descricao_projeto = String(b.descricao_projeto).trim();
  }
  if (temas) {
    next.area_inovacao = temas;
    next.interesse_temas = temas;
  }

  const prefFlags = criteriosToFlags(b.criterios_aceite);
  perfil.preferencias_fomento = {
    ...perfil.preferencias_fomento,
    tipos_recurso:
      Array.isArray(b.tipos_recurso) && b.tipos_recurso.length
        ? [...b.tipos_recurso]
        : perfil.preferencias_fomento?.tipos_recurso || [],
    faixa_valor_interesse: b.faixa_valor_interesse || perfil.preferencias_fomento?.faixa_valor_interesse || '',
    criterios_aceite: Array.isArray(b.criterios_aceite) ? [...b.criterios_aceite] : [],
    ...prefFlags,
  };

  if (b.faixa_valor_interesse && b.faixa_valor_interesse !== 'indefinido') {
    const faixa = BRIEFING_FAIXA_VALOR.find((f) => f.id === b.faixa_valor_interesse);
    if (faixa) {
      next.interesse_valor_min = faixa.min ?? 0;
      next.interesse_valor_max = faixa.max ?? 0;
      perfil.dados_economicos = {
        ...perfil.dados_economicos,
        faixa_faturamento: faixa.label,
      };
    }
  }

  perfil.documentacao = applyDocIdsToPerfil(
    perfil.documentacao || {},
    Array.isArray(b.documentos_disponiveis) ? b.documentos_disponiveis : [],
  );

  next.perfil = perfil;
  return next;
}

/**
 * @param {object|null} cliente
 * @param {ReturnType<briefingStateFromCliente>} briefingDraft
 */
export function estimateCompletenessAfterBriefing(cliente, briefingDraft) {
  const merged = applyBriefingToFormState(clientFormStateFromCliente(cliente), briefingDraft);
  const simulated = {
    ...cliente,
    ...merged,
    extras: {
      ...(cliente?.extras && typeof cliente.extras === 'object' ? cliente.extras : {}),
      perfil_consultivo: merged.perfil,
    },
    perfilConsultivo: merged.perfil,
    contatoPrincipal: merged.perfil.contato,
    dadosEconomicos: merged.perfil.dados_economicos,
    perfilTecnologico: merged.perfil.perfil_tecnologico,
    preferenciasFomento: merged.perfil.preferencias_fomento,
    documentacao: merged.perfil.documentacao,
    diagnosticoConsultor: merged.perfil.diagnostico_consultor,
    area_inovacao: merged.area_inovacao,
    descricao_projeto: merged.descricao_projeto,
    interesse_temas: merged.interesse_temas,
    interesse_valor_min: merged.interesse_valor_min,
    interesse_valor_max: merged.interesse_valor_max,
  };
  return calculateClientProfileCompleteness(simulated).score;
}

export {
  BRIEFING_TIPOS_RECURSO,
  BRIEFING_FAIXA_VALOR,
  BRIEFING_CRITERIOS_ACEITE,
  BRIEFING_DOCUMENTOS,
  parseTags,
  tagsToText,
};
