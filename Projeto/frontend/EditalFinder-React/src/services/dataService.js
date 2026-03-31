import { supabase } from './api';

const staticEditais = [
    {
        id: 1,
        titulo: "Edital de Inovação Agro 2026",
        orgao: "FINEP",
        area: "Agro",
        valor: 5000000,
        localidade: "Nacional",
        estado: "SP",
        dataLimite: "2026-10-30",
        tipoRecurso: "Subvenção econômica",
        linkOriginal: "https://www.finep.gov.br",
        pdfUrl: "https://www.finep.gov.br"
    },
    {
        id: 2,
        titulo: "Fomento à Pesquisa em Saúde",
        orgao: "BNDES",
        area: "Saúde",
        valor: 8500000,
        localidade: "Nacional",
        estado: "RJ",
        dataLimite: "2026-09-15",
        tipoRecurso: "Bolsa pesquisa",
        linkOriginal: "https://www.bndes.gov.br",
        pdfUrl: "https://www.bndes.gov.br"
    },
];

export const dataService = {
  // --- EDITAIS ---
  async getEditais() {
    const { data: manuais, error } = await supabase
      .from('edital')
      .select(`
          *,
          organizacao ( nome, site )
      `)
      .eq('status', 'Ativo');

    if (error) throw error;

    const manuaisFormatados = manuais.map(m => {
        const estado = m.estado || '';
        const isInternacional = estado.toLowerCase().includes('internacional') || estado === 'Exterior';
        
        return {
            id: `manual-${m.id_edital}`,
            titulo: m.titulo,
            orgao: m.fonte_recurso || (m.organizacao ? m.organizacao.nome : 'Manual'),
            area: m.temas || 'Geral',
            valor: m.valor_maximo || 0,
            localidade: isInternacional ? 'Internacional' : 'Nacional',
            estado: estado,
            dataLimite: m.prazo_envio,
            tipoRecurso: m.situacao || 'Edital',
            isManual: true,
            linkOriginal: m.link,
            pdfUrl: m.pdf_url,
            orgSite: m.organizacao ? m.organizacao.site : null
        };
    });

    return [...staticEditais, ...manuaisFormatados];
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

  async getAllEditaisAdmin() {
    const { data, error } = await supabase
      .from('edital')
      .select(`*, organizacao ( nome )`)
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
    return data;
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
};
