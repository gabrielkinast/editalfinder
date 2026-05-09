import { supabase } from './api';
import { normalizeClienteRow } from '../utils/normalizeCliente';
import { mapRawEditalRow } from '../utils/edital/editalRowMapper';

/** Supabase limita respostas; busca em páginas até esgotar linhas (respeitando RLS). */
async function fetchAllTableRows(tableName, orderColumn = 'criado_em', ascending = false) {
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

export const dataService = {
  // --- EDITAIS ---
  async getEditais() {
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

    let rows;
    try {
      rows = await fetchPaged('vw_editais_front', 'atualizado_em');
    } catch (viewErrAtualizado) {
      try {
        rows = await fetchPaged('vw_editais_front', 'id_edital');
      } catch (viewErr) {
        rows = [];
        console.warn('[dataService.getEditais] vw_editais_front:', viewErrAtualizado?.message || viewErrAtualizado);
      }
    }

    if (!rows?.length) {
      try {
        rows = await fetchPaged('edital', 'atualizado_em');
      } catch {
        try {
          rows = await fetchPaged('edital', 'id_edital');
        } catch (e2) {
          console.warn('[dataService.getEditais] edital fallback:', e2?.message || e2);
          rows = [];
        }
      }
    }

    return (rows || []).map(mapRawEditalRow);
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
    const { data, error } = await supabase
      .from('edital')
      .select('*')
      .eq('id_edital', idEdital)
      .single();
    if (error) throw error;
    return data;
  },

  async getAnexosByEdital(idEdital) {
    const { data, error } = await supabase
      .from('edital_anexo')
      .select('*')
      .eq('id_edital', idEdital)
      .order('criado_em', { ascending: true });
    if (error) throw error;
    return data || [];
  },

  async getAllEditaisAdmin() {
    const { data, error } = await supabase
      .from('edital')
      .select('*')
      .order('id_edital', { ascending: true });
    if (error) throw error;
    return data;
  },

  // --- USUÁRIOS ---
  async getUsers() {
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

  // --- NOTÍCIAS (tabela public.noticia) — carrega todas as linhas visíveis por RLS ---
  async getNoticias() {
    return fetchAllTableRows('noticia', 'criado_em', false);
  },

  // --- PESQUISAS (tabela public.pesquisa — ver pesquisas.txt / DDL no Supabase) ---
  async getPesquisas() {
    return fetchAllTableRows('pesquisa', 'criado_em', false);
  },
};
