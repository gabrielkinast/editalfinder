import { supabase } from './api';
import { classificarEdital } from './classificationService';

export const dataService = {
  // --- EDITAIS ---
  async getEditais() {
    const { data: manuais, error } = await supabase
      .from('edital')
      .select('*')
      .order('id_edital', { ascending: false });

    if (error) throw error;

    const manuaisFormatados = manuais.map(m => {
        const estado = m.estado || '';
        const isInternacional = estado.toLowerCase().includes('internacional') || estado === 'Exterior';
        const classificacao = classificarEdital(m);

        return {
            id: `manual-${m.id_edital}`,
            titulo: m.titulo,
            orgao: m.fonte_recurso || 'Manual',
            area: m.temas || classificacao.area.join(', '),
            valor: m.valor_maximo || 0,
            localidade: isInternacional ? 'Internacional' : 'Nacional',
            estado: estado,
            dataLimite: m.prazo_envio,
            tipoRecurso: classificacao.tipo,
            isManual: true,
            linkOriginal: m.link,
            pdfUrl: m.pdf_url,
            orgSite: null,
            // Campos brutos do edital (Radar / calcularScore)
            temas:         m.temas || null,
            objetivo:      m.objetivo || null,
            publico_alvo:  m.publico_alvo || null,
            descricao:     m.descricao || null,
            // Campos inteligentes do banco
            score:          m.score || 0,
            scoreDetalhado: m.score_detalhado || {},
            justificativa:  m.justificativa || null,
            compatibilidade: m.compatibilidade != null ? m.compatibilidade : null,
            recomendacao:   m.recomendacao || null,
            valorMinimo:    m.valor_minimo || 0,
            valorMaximo:    m.valor_maximo || 0,
            elegibilidade:  m.elegibilidade || null,
            contrapartida:  m.contrapartida || null,
            ods:            m.ods || null,
            contato:        m.contato || null,
            linkInscricao:  m.link_inscricao || null,
            regiao:         m.regiao || null,
            situacao:       m.situacao || null,
            status:         m.status || null,
            temAnexos:      !!(m.pdf_url),
        };
    });

    return manuaisFormatados;
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
