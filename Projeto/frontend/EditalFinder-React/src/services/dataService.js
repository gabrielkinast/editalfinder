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
import { mapRawEditalRow } from '../utils/edital/editalRowMapper';

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

    const mapped = (rows || []).map(mapRawEditalRow);
    if (IS_DEV) {
      logDevEditais({ view: viewName, count: mapped.length, phase: 'final_mapped' });
    }
    return mapped;
  },

  async createEdital(data) {
    const { error } = await supabase.from('edital').insert([data]);
    if (error) throw error;
  },

  async updateEdital(id, data) {
    const { error } = await supabase.from('edital').update(data).eq('id_edital', id);
    if (error) throw error;
  },

  async deleteEdital(id) {
    const { error } = await supabase.from('edital').delete().eq('id_edital', id);
    if (error) throw error;
  },

  async getEditalById(idEdital) {
    if (!isSupabaseConfigured) return null;
    const { data, error } = await supabase
      .from('edital')
      .select('*')
      .eq('id_edital', idEdital)
      .single();
    if (error) throw error;
    return data;
  },

  async getAnexosByEdital(idEdital) {
    if (!isSupabaseConfigured) return [];
    const { data, error } = await supabase
      .from('edital_anexo')
      .select('*')
      .eq('id_edital', idEdital)
      .order('criado_em', { ascending: true });
    if (error) throw error;
    return data || [];
  },

  async getAllEditaisAdmin() {
    if (!isSupabaseConfigured) return [];
    const { data, error } = await supabase
      .from('edital')
      .select('*')
      .order('id_edital', { ascending: true });
    if (error) throw error;
    return data;
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

  // --- CLIENTES ---
  async getClients() {
    if (!isSupabaseConfigured) return [];
    const { data, error } = await supabase.from('cliente').select('*').order('id_cliente', { ascending: true });
    if (error) throw error;
    return (data || []).map(normalizeClienteRow);
  },

  async createClient(data) {
    const { error } = await supabase.from('cliente').insert([data]);
    if (error) throw error;
  },

  async updateClient(id, data) {
    const { error } = await supabase.from('cliente').update(data).eq('id_cliente', id);
    if (error) throw error;
  },

  async deleteClient(id) {
    const { error } = await supabase.from('cliente').delete().eq('id_cliente', id);
    if (error) throw error;
  },

  // --- ORGANIZAÇÕES ---
  async getOrganizations() {
    if (!isSupabaseConfigured) return [];
    const { data, error } = await supabase.from('organizacao').select('*').order('id_organizacao', { ascending: true });
    if (error) throw error;
    return data;
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
