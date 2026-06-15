import { supabase, isSupabaseConfigured } from './supabaseClient';
import {
  VIEW_EDITAIS,
  VIEW_NOTICIAS,
  VIEW_PESQUISAS,
  VIEW_FORNECEDORES,
  VIEW_INVESTIMENTOS,
  ENABLE_DEBUG_PIPELINE,
  APP_ENV,
} from '../config/env';
import { normalizeClienteRow } from '../utils/normalizeCliente';
import {
  attachOwnerToClientPayload,
  isAdminUser,
  sanitizeClientWritePayload,
} from '../utils/permissions';
import { mapRawEditalRow } from '../utils/edital/editalRowMapper';
import { buildEditalWritePayload } from '../utils/admin/buildEditalWritePayload';
import {
  CREATE_EDITAL_RETURN_COLUMNS,
  buildManualEditalOrFilter,
  filterManualCadastroEditais,
  logCadastrosDebug,
  mergeCadastrosEditalRows,
} from '../utils/admin/manualCadastroEdital';
import { logEditalDataCounts } from '../utils/debugDataCounts';
import {
  lookupEditalForDetail,
  lookupAnexosForDetail,
} from '../utils/edital/editalDetailLookup';
import { filterPublicVisibleEditais } from '../utils/edital/editalVisibility';

const IS_DEV = import.meta.env.DEV;

/** Ordenações a tentar quando a view não expõe a primeira coluna. */
const ORDER_FALLBACKS = [
  ['criado_em', false],
  ['atualizado_em', false],
  ['id', false],
  ['id_edital', false],
];

function logDevEditais(payload) {
  if (!IS_DEV) return;
  const { view, count, phase, errorMessage } = payload;
  const line = { view, count, phase };
  if (errorMessage) line.supabaseError = errorMessage;
  if (ENABLE_DEBUG_PIPELINE || APP_ENV === 'local' || count === 0 || errorMessage) {
    console.info('[dataService.getEditais]', line);
  }
}

function logDevFeed(label, payload) {
  if (!IS_DEV) return;
  if (ENABLE_DEBUG_PIPELINE || APP_ENV === 'local' || payload.count === 0 || payload.errorMessage) {
    console.info(`[dataService.${label}]`, payload);
  }
}

/** Supabase limita respostas; busca em páginas até esgotar linhas (respeitando RLS). */
async function fetchAllTableRows(tableName, orderColumn = 'criado_em', ascending = false) {
  if (!isSupabaseConfigured) return [];
  const PAGE = 800;
  const all = [];
  let from = 0;
  for (;;) {
    const { data, error } = await supabase
      .from(tableName)
      .select('*')
      .order(orderColumn, { ascending, nullsFirst: false })
      .range(from, from + PAGE - 1);

    if (error) throw error;
    if (!data?.length) break;
    all.push(...data);
    if (data.length < PAGE) break;
    from += PAGE;
  }
  return all;
}

/** Tenta várias colunas de ordenação até uma funcionar no cluster. */
async function fetchAllWithOrderFallbacks(tableName) {
  if (!isSupabaseConfigured) return [];
  let lastErr;
  for (const [col, asc] of ORDER_FALLBACKS) {
    try {
      const rows = await fetchAllTableRows(tableName, col, asc);
      return rows;
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error(`fetch ${tableName}`);
}

export const dataService = {
  // --- EDITAIS ---
  async getEditais() {
    if (!isSupabaseConfigured) {
      logDevEditais({ view: VIEW_EDITAIS, count: 0, phase: 'skip', errorMessage: 'supabase_not_configured' });
      return [];
    }
    const PAGE = 1000;
    const fetchPaged = async (table, orderCol) => {
      const all = [];
      let from = 0;
      for (;;) {
        const q = await supabase
          .from(table)
          .select('*')
          .order(orderCol, { ascending: false, nullsFirst: false })
          .range(from, from + PAGE - 1);

        if (q.error) throw q.error;
        if (!q.data?.length) break;
        all.push(...q.data);
        if (q.data.length < PAGE) break;
        from += PAGE;
      }
      return all;
    };

    const viewName = VIEW_EDITAIS;
    let rows;
    let lastViewError;

    try {
      rows = await fetchPaged(viewName, 'atualizado_em');
      logDevEditais({ view: viewName, count: rows?.length ?? 0, phase: 'view_atualizado_em' });
    } catch (viewErrAtualizado) {
      lastViewError = viewErrAtualizado?.message || String(viewErrAtualizado);
      logDevEditais({
        view: viewName,
        count: 0,
        phase: 'view_atualizado_em_failed',
        errorMessage: lastViewError,
      });
      try {
        rows = await fetchPaged(viewName, 'id_edital');
        logDevEditais({ view: viewName, count: rows?.length ?? 0, phase: 'view_id_edital' });
      } catch (viewErr) {
        rows = [];
        const msg = viewErr?.message || String(viewErr);
        logDevEditais({ view: viewName, count: 0, phase: 'view_failed', errorMessage: msg });
        console.warn('[dataService.getEditais] view:', viewErrAtualizado?.message || viewErrAtualizado);
      }
    }

    if (!rows?.length) {
      try {
        rows = await fetchPaged('edital', 'atualizado_em');
        logDevEditais({ view: 'edital', count: rows?.length ?? 0, phase: 'fallback_edital_atualizado_em' });
      } catch {
        try {
          rows = await fetchPaged('edital', 'id_edital');
          logDevEditais({ view: 'edital', count: rows?.length ?? 0, phase: 'fallback_edital_id' });
        } catch (e2) {
          console.warn('[dataService.getEditais] edital fallback:', e2?.message || e2);
          rows = [];
          logDevEditais({
            view: viewName,
            count: 0,
            phase: 'all_failed',
            errorMessage: e2?.message || String(e2),
          });
        }
      }
    }

    const mapped = filterPublicVisibleEditais((rows || []).map(mapRawEditalRow));
    if (IS_DEV) {
      logDevEditais({ view: viewName, count: mapped.length, phase: 'final_mapped' });
    }
    // Diagnóstico opcional (web vs desktop/Tauri): só roda com VITE_DEBUG_DATA_COUNTS.
    try {
      await logEditalDataCounts({ supabase, viewName, catalogCount: mapped.length });
    } catch (dbgErr) {
      if (IS_DEV) console.warn('[dataService.getEditais] data-count debug falhou:', dbgErr?.message || dbgErr);
    }
    return mapped;
  },

  async createEdital(data) {
    const row = buildEditalWritePayload(data, { manualCadastro: true });
    logCadastrosDebug('create payload keys', { keys: Object.keys(row) });

    const { data: inserted, error } = await supabase
      .from('edital')
      .insert([row])
      .select(CREATE_EDITAL_RETURN_COLUMNS)
      .single();

    if (error) throw error;

    logCadastrosDebug('insert success id_edital', { id_edital: inserted?.id_edital ?? null });
    return inserted;
  },

  async updateEdital(id, data) {
    const row = buildEditalWritePayload(data, { manualCadastro: true });
    const { data: updated, error } = await supabase
      .from('edital')
      .update(row)
      .eq('id_edital', id)
      .select(CREATE_EDITAL_RETURN_COLUMNS)
      .single();
    if (error) throw error;
    return updated;
  },

  async deleteEdital(id) {
    const { error } = await supabase.from('edital').delete().eq('id_edital', id);
    if (error) throw error;
  },

  /**
   * Lookup robusto: base (.maybeSingle) → fallback view → errorKind classificado.
   */
  async getEditalById(idEdital) {
    return lookupEditalForDetail(supabase, {
      routeParam: idEdital,
      viewName: VIEW_EDITAIS,
      isConfigured: isSupabaseConfigured,
    });
  },

  /**
   * Anexos com retorno estruturado — falha não lança (detalhe continua renderizando).
   * @param {unknown} idEdital
   */
  async getAnexosByEditalSafe(idEdital) {
    return lookupAnexosForDetail(supabase, idEdital, {
      isConfigured: isSupabaseConfigured,
    });
  },

  /** @deprecated Preferir getAnexosByEditalSafe — mantido para compatibilidade. */
  async getAnexosByEdital(idEdital) {
    const result = await lookupAnexosForDetail(supabase, idEdital, {
      isConfigured: isSupabaseConfigured,
    });
    if (!result.ok) throw result.error || new Error('anexos_fetch_failed');
    return result.data;
  },

  async getAllEditaisAdmin(options = {}) {
    if (!isSupabaseConfigured) return [];
    const { pinRows = [] } = options;
    const orFilter = buildManualEditalOrFilter();

    logCadastrosDebug('list filters', { orFilter, pinCount: pinRows.length });

    let rows = [];
    const filteredQuery = await supabase
      .from('edital')
      .select(CREATE_EDITAL_RETURN_COLUMNS)
      .or(orFilter)
      .order('id_edital', { ascending: false });

    if (filteredQuery.error) {
      if (IS_DEV) {
        console.warn('[dataService.getAllEditaisAdmin] filtered query failed:', filteredQuery.error.message);
      }
      const fallback = await supabase
        .from('edital')
        .select(CREATE_EDITAL_RETURN_COLUMNS)
        .order('id_edital', { ascending: false })
        .limit(800);
      if (fallback.error) throw fallback.error;
      rows = filterManualCadastroEditais(fallback.data);
    } else {
      rows = filteredQuery.data || [];
      rows = filterManualCadastroEditais(rows);
    }

    const merged = mergeCadastrosEditalRows(rows, pinRows);
    logCadastrosDebug('reload list count', { remote: rows.length, merged: merged.length });
    return merged;
  },

  // --- USUÁRIOS ---
  async getUsers() {
    if (!isSupabaseConfigured) return [];
    const { data, error } = await supabase.from('usuario').select('*').order('id_usuario', { ascending: true });
    if (error) throw error;
    return data;
  },

  async updateUser(id, data) {
    const { error } = await supabase.from('usuario').update(data).eq('id_usuario', id);
    if (error) throw error;
  },

  async createUser(data) {
    const { error } = await supabase.from('usuario').insert([data]);
    if (error) throw error;
  },

  async deleteUser(id) {
    const { error } = await supabase.from('usuario').delete().eq('id_usuario', id);
    if (error) throw error;
  },

  // --- CLIENTES (isolamento por id_usuario; admin vê todos) ---
  async getClients(options = {}) {
    if (!isSupabaseConfigured) return [];
    const { user } = options;

    const { data: sessionData, error: sessionErr } = await supabase.auth.getSession();
    if (sessionErr && IS_DEV) {
      console.warn('[dataService.getClients] getSession', sessionErr.message || sessionErr);
    }
    if (IS_DEV && !sessionData?.session?.user) {
      console.warn(
        '[dataService.getClients] Sem sessão Supabase Auth antes da query; com RLS em `cliente` o PostgREST pode devolver erro ou zero linhas.',
      );
    }

    let q = supabase.from('cliente').select('*').order('id_cliente', { ascending: true });
    if (!isAdminUser(user)) {
      const uid = user?.id_usuario;
      if (uid == null || uid === '') return [];
      q = q.eq('id_usuario', Number(uid));
    }
    const { data, error } = await q;
    if (error) {
      if (IS_DEV) {
        console.error('[dataService.getClients] supabase', {
          message: error.message,
          code: error.code,
          details: error.details,
          hint: error.hint,
        });
      }
      throw error;
    }
    return (data || []).map(normalizeClienteRow);
  },

  async createClient(data, options = {}) {
    if (!isSupabaseConfigured) return;
    const { user } = options;
    const row = attachOwnerToClientPayload(user, { ...(data || {}) });
    const { error } = await supabase.from('cliente').insert([row]);
    if (error) throw error;
  },

  async updateClient(id, data, options = {}) {
    if (!isSupabaseConfigured) return;
    const { user } = options;
    const patch = sanitizeClientWritePayload(user, data || {});
    let q = supabase.from('cliente').update(patch).eq('id_cliente', id);
    if (!isAdminUser(user) && user?.id_usuario != null && user.id_usuario !== '') {
      q = q.eq('id_usuario', Number(user.id_usuario));
    }
    const { error } = await q;
    if (error) throw error;
  },

  async deleteClient(id, options = {}) {
    if (!isSupabaseConfigured) return;
    const { user } = options;
    let q = supabase.from('cliente').delete().eq('id_cliente', id);
    if (!isAdminUser(user) && user?.id_usuario != null && user.id_usuario !== '') {
      q = q.eq('id_usuario', Number(user.id_usuario));
    }
    const { error } = await q;
    if (error) throw error;
  },

  // --- ORGANIZAÇÕES ---
  async getOrganizations() {
    if (!isSupabaseConfigured) return [];
    const { data, error } = await supabase.from('organizacao').select('*').order('id_organizacao', { ascending: true });
    if (error) throw error;
    return data || [];
  },

  async createOrganization(data) {
    const { error } = await supabase.from('organizacao').insert([data]);
    if (error) throw error;
  },

  async updateOrganization(id, data) {
    const { error } = await supabase.from('organizacao').update(data).eq('id_organizacao', id);
    if (error) throw error;
  },

  async deleteOrganization(id) {
    const { error } = await supabase.from('organizacao').delete().eq('id_organizacao', id);
    if (error) throw error;
  },

  /**
   * Preferência: view `VIEW_NOTICIAS`; se falhar, tabela `noticia`.
   */
  async getNoticias() {
    if (!isSupabaseConfigured) {
      logDevFeed('getNoticias', { view: VIEW_NOTICIAS, count: 0, errorMessage: 'supabase_not_configured' });
      return [];
    }
    try {
      const rows = await fetchAllWithOrderFallbacks(VIEW_NOTICIAS);
      logDevFeed('getNoticias', { view: VIEW_NOTICIAS, count: rows.length });
      return rows;
    } catch (e) {
      const msg = e?.message || String(e);
      logDevFeed('getNoticias', { view: VIEW_NOTICIAS, count: 0, errorMessage: msg, fallback: 'noticia' });
      try {
        const rows = await fetchAllWithOrderFallbacks('noticia');
        logDevFeed('getNoticias', { view: 'noticia', count: rows.length, phase: 'fallback_table' });
        return rows;
      } catch (e2) {
        console.warn('[dataService.getNoticias]', e2?.message || e2);
        logDevFeed('getNoticias', { view: 'noticia', count: 0, errorMessage: e2?.message || String(e2) });
        return [];
      }
    }
  },

  /**
   * Preferência: view `VIEW_PESQUISAS`; se falhar, tabela `pesquisa`.
   */
  async getPesquisas() {
    if (!isSupabaseConfigured) {
      logDevFeed('getPesquisas', { view: VIEW_PESQUISAS, count: 0, errorMessage: 'supabase_not_configured' });
      return [];
    }
    try {
      const rows = await fetchAllWithOrderFallbacks(VIEW_PESQUISAS);
      logDevFeed('getPesquisas', { view: VIEW_PESQUISAS, count: rows.length });
      return rows;
    } catch (e) {
      const msg = e?.message || String(e);
      logDevFeed('getPesquisas', { view: VIEW_PESQUISAS, count: 0, errorMessage: msg, fallback: 'pesquisa' });
      try {
        const rows = await fetchAllWithOrderFallbacks('pesquisa');
        logDevFeed('getPesquisas', { view: 'pesquisa', count: rows.length, phase: 'fallback_table' });
        return rows;
      } catch (e2) {
        console.warn('[dataService.getPesquisas]', e2?.message || e2);
        logDevFeed('getPesquisas', { view: 'pesquisa', count: 0, errorMessage: e2?.message || String(e2) });
        return [];
      }
    }
  },

  /**
   * Views de portais estratégicos (aba Fornecedores) — para consumo futuro / services dedicados.
   */
  async getPortaisFornecedoresFront() {
    if (!isSupabaseConfigured) return [];
    try {
      const rows = await fetchAllWithOrderFallbacks(VIEW_FORNECEDORES);
      logDevFeed('getPortaisFornecedoresFront', { view: VIEW_FORNECEDORES, count: rows.length });
      return rows;
    } catch (e) {
      console.warn('[dataService.getPortaisFornecedoresFront]', e?.message || e);
      logDevFeed('getPortaisFornecedoresFront', {
        view: VIEW_FORNECEDORES,
        count: 0,
        errorMessage: e?.message || String(e),
      });
      return [];
    }
  },

  /**
   * Views de portais estratégicos (aba Investimentos) — para consumo futuro / services dedicados.
   */
  async getPortaisInvestimentosFront() {
    if (!isSupabaseConfigured) return [];
    try {
      const rows = await fetchAllWithOrderFallbacks(VIEW_INVESTIMENTOS);
      logDevFeed('getPortaisInvestimentosFront', { view: VIEW_INVESTIMENTOS, count: rows.length });
      return rows;
    } catch (e) {
      console.warn('[dataService.getPortaisInvestimentosFront]', e?.message || e);
      logDevFeed('getPortaisInvestimentosFront', {
        view: VIEW_INVESTIMENTOS,
        count: 0,
        errorMessage: e?.message || String(e),
      });
      return [];
    }
  },
};
