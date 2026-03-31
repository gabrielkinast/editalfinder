/* ============================================
   EDITAL FINDER - SCRIPT PRINCIPAL
   Lógica de Login, Filtros Dinâmicos e Exportação
   ============================================ */

// ============================================
// DADOS DE EDITAIS (20 editais fictícios)
// ============================================

const editais = [
    {
        id: 1,
        titulo: "Edital de Inovação Agro 2026",
        orgao: "FINEP",
        area: "Agro",
        valor: 5000000,
        localidade: "Nacional",
        estado: "SP",
        dataLimite: "2026-10-30",
        tipoRecurso: "Subvenção econômica"
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
        tipoRecurso: "Bolsa pesquisa"
    },
    {
        id: 3,
        titulo: "Investimento em Startups de Tecnologia",
        orgao: "CORDIS",
        area: "Tecnologia",
        valor: 12000000,
        localidade: "Internacional",
        estado: "SP",
        dataLimite: "2026-11-20",
        tipoRecurso: "Investimento"
    },
    {
        id: 4,
        titulo: "Linha de Crédito para Educação",
        orgao: "BNDES",
        area: "Educação",
        valor: 3500000,
        localidade: "Nacional",
        estado: "MG",
        dataLimite: "2026-08-30",
        tipoRecurso: "Linha de crédito"
    },
    {
        id: 5,
        titulo: "Programa de Energia Renovável",
        orgao: "FINEP",
        area: "Energia",
        valor: 15000000,
        localidade: "Nacional",
        estado: "BA",
        dataLimite: "2026-12-10",
        tipoRecurso: "Fomento à inovação"
    },
    {
        id: 6,
        titulo: "Subvenção para Indústria 4.0",
        orgao: "FAPERGS",
        area: "Indústria",
        valor: 6500000,
        localidade: "Nacional",
        estado: "RS",
        dataLimite: "2026-07-25",
        tipoRecurso: "Subvenção econômica"
    },
    {
        id: 7,
        titulo: "Bolsa de Pesquisa em Agrotecnologia",
        orgao: "FINEP",
        area: "Agro",
        valor: 2500000,
        localidade: "Nacional",
        estado: "GO",
        dataLimite: "2026-09-30",
        tipoRecurso: "Bolsa pesquisa"
    },
    {
        id: 8,
        titulo: "Investimento em Biotecnologia",
        orgao: "CORDIS",
        area: "Saúde",
        valor: 20000000,
        localidade: "Internacional",
        estado: "SP",
        dataLimite: "2026-10-15",
        tipoRecurso: "Investimento"
    },
    {
        id: 9,
        titulo: "Fomento à Inovação em Educação Digital",
        orgao: "BNDES",
        area: "Educação",
        valor: 4200000,
        localidade: "Nacional",
        estado: "SP",
        dataLimite: "2026-08-20",
        tipoRecurso: "Fomento à inovação"
    },
    {
        id: 10,
        titulo: "Linha de Crédito para Energia Solar",
        orgao: "FINEP",
        area: "Energia",
        valor: 7800000,
        localidade: "Nacional",
        estado: "MG",
        dataLimite: "2026-11-05",
        tipoRecurso: "Linha de crédito"
    },
    {
        id: 11,
        titulo: "Subvenção para Startups de Saúde",
        orgao: "FAPERGS",
        area: "Saúde",
        valor: 3800000,
        localidade: "Nacional",
        estado: "RJ",
        dataLimite: "2026-09-10",
        tipoRecurso: "Subvenção econômica"
    },
    {
        id: 12,
        titulo: "Programa de Inovação Agrícola",
        orgao: "FINEP",
        area: "Agro",
        valor: 9500000,
        localidade: "Nacional",
        estado: "PR",
        dataLimite: "2026-10-25",
        tipoRecurso: "Fomento à inovação"
    },
    {
        id: 13,
        titulo: "Investimento em Tecnologia Verde",
        orgao: "CORDIS",
        area: "Energia",
        valor: 18000000,
        localidade: "Internacional",
        estado: "SP",
        dataLimite: "2026-11-30",
        tipoRecurso: "Investimento"
    },
    {
        id: 14,
        titulo: "Bolsa de Pesquisa em Indústria",
        orgao: "BNDES",
        area: "Indústria",
        valor: 2800000,
        localidade: "Nacional",
        estado: "SC",
        dataLimite: "2026-08-15",
        tipoRecurso: "Bolsa pesquisa"
    },
    {
        id: 15,
        titulo: "Fomento à Educação Profissional",
        orgao: "FAPERGS",
        area: "Educação",
        valor: 5500000,
        localidade: "Nacional",
        estado: "RS",
        dataLimite: "2026-09-20",
        tipoRecurso: "Fomento à inovação"
    },
    {
        id: 16,
        titulo: "Linha de Crédito para Tecnologia",
        orgao: "FINEP",
        area: "Tecnologia",
        valor: 11000000,
        localidade: "Nacional",
        estado: "SP",
        dataLimite: "2026-10-10",
        tipoRecurso: "Linha de crédito"
    },
    {
        id: 17,
        titulo: "Subvenção para Pesquisa em Saúde",
        orgao: "BNDES",
        area: "Saúde",
        valor: 6800000,
        localidade: "Nacional",
        estado: "MG",
        dataLimite: "2026-11-15",
        tipoRecurso: "Subvenção econômica"
    },
    {
        id: 18,
        titulo: "Investimento em Agritech",
        orgao: "CORDIS",
        area: "Agro",
        valor: 14000000,
        localidade: "Internacional",
        estado: "GO",
        dataLimite: "2026-12-01",
        tipoRecurso: "Investimento"
    },
    {
        id: 19,
        titulo: "Programa de Inovação em Indústria",
        orgao: "FAPERGS",
        area: "Indústria",
        valor: 7200000,
        localidade: "Nacional",
        estado: "RS",
        dataLimite: "2026-10-05",
        tipoRecurso: "Fomento à inovação"
    },
    {
        id: 20,
        titulo: "Bolsa de Pesquisa em Energia",
        orgao: "FINEP",
        area: "Energia",
        valor: 3200000,
        localidade: "Nacional",
        estado: "BA",
        dataLimite: "2026-09-25",
        tipoRecurso: "Bolsa pesquisa"
    }
];

// ============================================
// LÓGICA DE LOGIN
// ============================================

function initLogin() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = document.getElementById('email').value;
            const passwordInput = document.getElementById('password').value;
            const btnLogin = loginForm.querySelector('.btn-login');
            const originalText = btnLogin.textContent;

            try {
                btnLogin.textContent = 'Verificando...';
                btnLogin.disabled = true;

                // 1. Tenta buscar o usuário no Supabase
                const { data: usuario, error } = await supabaseClient
                    .from('usuario')
                    .select('*')
                    .eq('nome_email', emailInput)
                    .single();

                if (error && error.code !== 'PGRST116') { // PGRST116 é o erro de "nenhum resultado encontrado"
                    throw error;
                }

                // 2. Verifica se o usuário existe e se a senha coincide
                if (usuario && usuario.senha === passwordInput) {
                    // Armazenar sessão no localStorage
                    localStorage.setItem('editalFinderUser', JSON.stringify({
                        email: usuario.nome_email,
                        nome: usuario.nome,
                        tipo: usuario.tipo_usuario,
                        loginTime: new Date().toISOString()
                    }));
                    
                    // Redirecionar para dashboard
                    window.location.href = 'dashboard.html';
                } 
                // 3. Fallback para o usuário admin estático (para garantir que você não perca acesso se o banco falhar)
                else if (emailInput === 'admin@finder.com' && passwordInput === '123456') {
                    localStorage.setItem('editalFinderUser', JSON.stringify({
                        email: emailInput,
                        nome: 'Administrador',
                        loginTime: new Date().toISOString()
                    }));
                    window.location.href = 'dashboard.html';
                } else {
                    alert('Credenciais inválidas. Verifique seu e-mail e senha.');
                }

            } catch (error) {
                console.error('Erro no login:', error);
                alert('Erro ao tentar fazer login: ' + (error.message || 'Erro de conexão com o servidor.'));
            } finally {
                btnLogin.textContent = originalText;
                btnLogin.disabled = false;
            }
        });
    }
}

// ============================================
// LÓGICA DO DASHBOARD
// ============================================

let editaisFiltrados = [];
let todosOsEditaisUnificados = []; // Lista que unifica estáticos + manuais

async function initDashboard() {
    // Verificar se usuário está logado
    const user = localStorage.getItem('editalFinderUser');
    if (!user) {
        window.location.href = 'index.html';
        return;
    }
    
    // Inicializar eventos
    setupFilterListeners();
    setupLogout();
    setupExport();
    setupUserRegistration();
    
    // Carregar dados unificados
    await carregarDadosDashboard();
}

async function carregarDadosDashboard() {
    const container = document.getElementById('editaisList');
    if (!container) return;

    try {
        container.innerHTML = '<div style="text-align:center; padding: 50px; width: 100%;"><h3>Carregando editais...</h3></div>';

        // 1. Carregar editais manuais do Supabase
        const { data: manuais, error } = await supabaseClient
            .from('edital')
            .select(`
                *,
                organizacao ( nome, site )
            `)
            .eq('status', 'Ativo');

        if (error) throw error;

        // 2. Formatar editais manuais para o padrão do dashboard
        const manuaisFormatados = manuais.map(m => ({
            id: `manual-${m.id_edital}`,
            titulo: m.titulo,
            orgao: m.organizacao ? m.organizacao.nome : (m.fonte_recurso || 'Manual'),
            area: m.temas || 'Geral',
            valor: m.valor_maximo || 0,
            localidade: 'Nacional', // Padrão para manuais por enquanto
            estado: '', 
            dataLimite: m.prazo_envio,
            tipoRecurso: m.situacao || 'Edital',
            isManual: true,
            linkOriginal: m.link,
            pdfUrl: m.pdf_url,
            orgSite: m.organizacao ? m.organizacao.site : null
        }));

        // 3. Unificar com os editais estáticos
        todosOsEditaisUnificados = [...editais, ...manuaisFormatados];
        editaisFiltrados = [...todosOsEditaisUnificados];

        // 4. Renderizar
        renderEditais(todosOsEditaisUnificados);

    } catch (error) {
        console.error('Erro ao carregar dados do dashboard:', error);
        container.innerHTML = '<div style="text-align:center; padding: 50px; width: 100%;"><h3>Erro ao carregar editais manuais. Mostrando apenas editais padrão.</h3></div>';
        todosOsEditaisUnificados = [...editais];
        editaisFiltrados = [...todosOsEditaisUnificados];
        renderEditais(todosOsEditaisUnificados);
    }
}

// ============================================
// CONFIGURAÇÃO SUPABASE
// ============================================

const SUPABASE_URL = 'https://fptjlvzzfphltuucklau.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwdGpsdnp6ZnBobHR1dWNrbGF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMyNTY0ODksImV4cCI6MjA4ODgzMjQ4OX0.u_Psx-qozH2QEBCsIxNemrhhBUEjHm-iiFJPp6R71AQ'; 
// Usamos um nome diferente para a instância do cliente para evitar conflito com a biblioteca global
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// ============================================
// LÓGICA DE ADMINISTRAÇÃO (CADASTROS)
// ============================================

function initAdminPage() {
    setupSidebarNavigation();
    loadUsers();
    loadClients();
    loadOrganizations(); // Nova função para carregar organizações
    loadManualEditais();
    setupUserRegistration();
    setupUserFilterListeners();
    setupClientRegistration();
    setupOrgRegistration(); // Nova função para configurar o modal de organizações
    setupEditalRegistration();
}

// --- GESTÃO DE ORGANIZAÇÕES ---

let todasOrganizacoes = [];

async function loadOrganizations() {
    const tableBody = document.getElementById('orgTableBody');
    if (!tableBody) return;

    try {
        const { data: orgs, error } = await supabaseClient
            .from('organizacao')
            .select('*')
            .order('id_organizacao', { ascending: true });

        if (error) throw error;

        todasOrganizacoes = orgs;
        renderOrgTable(orgs);
        updateEditalOrgSelect(orgs); // Atualiza o select no modal de editais

    } catch (error) {
        console.error('Erro ao carregar organizações:', error);
        tableBody.innerHTML = '<tr><td colspan="7">Erro ao carregar dados.</td></tr>';
    }
}

function renderOrgTable(lista) {
    const tableBody = document.getElementById('orgTableBody');
    if (!tableBody) return;

    if (lista.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px;">Nenhuma organização encontrada.</td></tr>';
        return;
    }

    tableBody.innerHTML = lista.map(org => `
        <tr>
            <td>${org.id_organizacao}</td>
            <td>${org.nome}</td>
            <td>${org.tipo || '-'}</td>
            <td>${org.estado || '-'}/${org.país || '-'}</td>
            <td>${org.site ? `<a href="${org.site}" target="_blank">Link</a>` : '-'}</td>
            <td>
                <select class="status-select" onchange="updateOrgStatus(${org.id_organizacao}, this.value)">
                    <option value="Ativo" ${org.status === 'Ativo' ? 'selected' : ''}>Ativo</option>
                    <option value="Inativo" ${org.status === 'Inativo' ? 'selected' : ''}>Inativo</option>
                </select>
            </td>
            <td>
                <button class="btn-action btn-edit" onclick="editOrg(${org.id_organizacao})">Editar</button>
                <button class="btn-action btn-delete" onclick="deleteOrg(${org.id_organizacao})">Deletar</button>
            </td>
        </tr>
    `).join('');
}

async function updateOrgStatus(id, newStatus) {
    try {
        const { error } = await supabaseClient
            .from('organizacao')
            .update({ status: newStatus })
            .eq('id_organizacao', id);

        if (error) throw error;
        
        const org = todasOrganizacoes.find(o => o.id_organizacao === id);
        if (org) org.status = newStatus;
        
        console.log(`Status da organização ${id} atualizado para ${newStatus}`);
    } catch (error) {
        alert('Erro ao atualizar status: ' + error.message);
        loadOrganizations();
    }
}

function setupOrgRegistration() {
    const modal = document.getElementById('orgModal');
    const openBtn = document.getElementById('btnOpenOrgModal');
    const closeBtn = document.getElementById('closeOrgModal');
    const cancelBtn = document.getElementById('cancelOrgBtn');
    const orgForm = document.getElementById('orgForm');

    if (!modal || !openBtn) return;

    openBtn.addEventListener('click', () => {
        orgForm.reset();
        document.getElementById('editOrgId').value = '';
        document.getElementById('orgModalTitle').textContent = 'Cadastrar Nova Organização';
        modal.style.display = 'flex';
    });

    const closeModal = () => {
        modal.style.display = 'none';
        orgForm.reset();
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    orgForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('editOrgId').value;
        const btnSave = document.getElementById('btnSaveOrg');
        const originalText = btnSave.textContent;

        try {
            btnSave.textContent = 'Salvando...';
            btnSave.disabled = true;

            const orgData = {
                nome: document.getElementById('org_nome').value,
                tipo: document.getElementById('org_tipo').value,
                país: document.getElementById('org_pais').value,
                estado: document.getElementById('org_estado').value,
                site: document.getElementById('org_site').value,
                status: document.getElementById('org_status').value
            };

            let result;
            if (id) {
                result = await supabaseClient.from('organizacao').update(orgData).eq('id_organizacao', id);
            } else {
                result = await supabaseClient.from('organizacao').insert([orgData]);
            }

            if (result.error) throw result.error;

            alert(id ? 'Organização atualizada!' : 'Organização cadastrada!');
            closeModal();
            loadOrganizations();
        } catch (error) {
            alert('Erro ao salvar organização: ' + error.message);
        } finally {
            btnSave.textContent = originalText;
            btnSave.disabled = false;
        }
    });
}

async function editOrg(id) {
    const modal = document.getElementById('orgModal');
    try {
        const { data: org, error } = await supabaseClient
            .from('organizacao')
            .select('*')
            .eq('id_organizacao', id)
            .single();

        if (error) throw error;

        document.getElementById('editOrgId').value = org.id_organizacao;
        document.getElementById('org_nome').value = org.nome;
        document.getElementById('org_tipo').value = org.tipo;
        document.getElementById('org_pais').value = org.país;
        document.getElementById('org_estado').value = org.estado;
        document.getElementById('org_site').value = org.site;
        document.getElementById('org_status').value = org.status || 'Ativo';

        document.getElementById('orgModalTitle').textContent = 'Editar Organização';
        modal.style.display = 'flex';
    } catch (error) {
        alert('Erro ao carregar dados: ' + error.message);
    }
}

async function deleteOrg(id) {
    if (!confirm('Excluir esta organização permanentemente?')) return;
    try {
        const { error } = await supabaseClient.from('organizacao').delete().eq('id_organizacao', id);
        if (error) throw error;
        alert('Organização removida!');
        loadOrganizations();
    } catch (error) {
        alert('Erro ao excluir: ' + error.message);
    }
}

function updateEditalOrgSelect(orgs) {
    const select = document.getElementById('edital_id_org');
    if (!select) return;

    const currentValue = select.value;
    select.innerHTML = '<option value="">Selecione uma organização...</option>' + 
        orgs.map(org => `<option value="${org.id_organizacao}">${org.nome}</option>`).join('');
    
    select.value = currentValue;
}

// --- GESTÃO DE EDITAIS MANUAIS ---

let todosEditaisManuais = [];

async function loadManualEditais() {
    const tableBody = document.getElementById('editalTableBody');
    if (!tableBody) return;

    try {
        const { data: editais, error } = await supabaseClient
            .from('edital')
            .select(`
                *,
                organizacao ( nome )
            `)
            .order('id_edital', { ascending: true });

        if (error) throw error;

        todosEditaisManuais = editais;
        renderEditalTable(editais);

    } catch (error) {
        console.error('Erro ao carregar editais manuais:', error);
        tableBody.innerHTML = '<tr><td colspan="7">Erro ao carregar dados.</td></tr>';
    }
}

function renderEditalTable(lista) {
    const tableBody = document.getElementById('editalTableBody');
    if (!tableBody) return;

    if (lista.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px;">Nenhum edital encontrado.</td></tr>';
        return;
    }

    tableBody.innerHTML = lista.map(edital => `
        <tr>
            <td>${edital.id_edital}</td>
            <td>${edital.titulo}</td>
            <td>${edital.organizacao ? edital.organizacao.nome : (edital.fonte_recurso || '-')}</td>
            <td>${formatCurrency(edital.valor_maximo || 0)}</td>
            <td>${edital.prazo_envio ? formatDate(edital.prazo_envio) : '-'}</td>
            <td>
                <select class="status-select" onchange="updateEditalStatus(${edital.id_edital}, this.value)">
                    <option value="Ativo" ${edital.status === 'Ativo' ? 'selected' : ''}>Ativo</option>
                    <option value="Inativo" ${edital.status === 'Inativo' ? 'selected' : ''}>Inativo</option>
                </select>
            </td>
            <td>
                <button class="btn-action btn-edit" onclick="editEdital(${edital.id_edital})">Editar</button>
                <button class="btn-action btn-delete" onclick="deleteEdital(${edital.id_edital})">Deletar</button>
            </td>
        </tr>
    `).join('');
}

async function updateEditalStatus(id, newStatus) {
    try {
        const { error } = await supabaseClient
            .from('edital')
            .update({ status: newStatus })
            .eq('id_edital', id);

        if (error) throw error;
        
        const edital = todosEditaisManuais.find(e => e.id_edital === id);
        if (edital) edital.status = newStatus;
        
        console.log(`Status do edital ${id} atualizado para ${newStatus}`);
    } catch (error) {
        alert('Erro ao atualizar status: ' + error.message);
        loadManualEditais();
    }
}

function setupEditalRegistration() {
    const modal = document.getElementById('editalModal');
    const openBtn = document.getElementById('btnOpenEditalModal');
    const closeBtn = document.getElementById('closeEditalModal');
    const cancelBtn = document.getElementById('cancelEditalBtn');
    const editalForm = document.getElementById('editalForm');

    if (!modal || !openBtn) return;

    // Configurar range de valor
    const valorRange = document.getElementById('edital_valor_max');
    const valorDisplay = document.getElementById('display_edital_valor');
    if (valorRange && valorDisplay) {
        valorRange.addEventListener('input', () => {
            valorDisplay.textContent = formatCurrency(parseFloat(valorRange.value));
        });
    }

    openBtn.addEventListener('click', () => {
        editalForm.reset();
        if (valorDisplay) valorDisplay.textContent = 'R$ 0,00';
        document.getElementById('editEditalId').value = '';
        document.getElementById('editalModalTitle').textContent = 'Cadastrar Novo Edital';
        modal.style.display = 'flex';
    });

    const closeModal = () => {
        modal.style.display = 'none';
        editalForm.reset();
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    editalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('editEditalId').value;
        const btnSave = document.getElementById('btnSaveEdital');
        const originalText = btnSave.textContent;

        try {
            btnSave.textContent = 'Salvando...';
            btnSave.disabled = true;

            const editalData = {
                titulo: document.getElementById('edital_titulo').value,
                descricao: document.getElementById('edital_descricao').value,
                objetivo: document.getElementById('edital_objetivo').value,
                temas: document.getElementById('edital_temas').value,
                publico_alvo: document.getElementById('edital_publico').value,
                fonte_recurso: document.getElementById('edital_fonte').value,
                valor_maximo: parseFloat(document.getElementById('edital_valor_max').value) || 0,
                data_publicacao: document.getElementById('edital_data_pub').value || null,
                prazo_envio: document.getElementById('edital_prazo').value || null,
                situacao: document.getElementById('edital_situacao').value,
                pdf_url: document.getElementById('edital_url_pdf').value,
                link: document.getElementById('edital_link').value,
                status: document.getElementById('edital_status').value,
                id_organizacao: parseInt(document.getElementById('edital_id_org').value) || null
            };

            let result;
            if (id) {
                result = await supabaseClient.from('edital').update(editalData).eq('id_edital', id);
            } else {
                result = await supabaseClient.from('edital').insert([editalData]);
            }

            if (result.error) throw result.error;

            alert(id ? 'Edital atualizado!' : 'Edital cadastrado com sucesso!');
            closeModal();
            loadManualEditais();
        } catch (error) {
            alert('Erro ao salvar edital: ' + error.message);
        } finally {
            btnSave.textContent = originalText;
            btnSave.disabled = false;
        }
    });
}

async function editEdital(id) {
    const modal = document.getElementById('editalModal');
    const form = document.getElementById('editalForm');

    try {
        const { data: edital, error } = await supabaseClient
            .from('edital')
            .select('*')
            .eq('id_edital', id)
            .single();

        if (error) throw error;

        document.getElementById('editEditalId').value = edital.id_edital;
        document.getElementById('edital_titulo').value = edital.titulo;
        document.getElementById('edital_descricao').value = edital.descricao;
        document.getElementById('edital_objetivo').value = edital.objetivo;
        document.getElementById('edital_temas').value = edital.temas;
        document.getElementById('edital_publico').value = edital.publico_alvo;
        document.getElementById('edital_fonte').value = edital.fonte_recurso;
        document.getElementById('edital_valor_max').value = edital.valor_maximo;
        document.getElementById('display_edital_valor').textContent = formatCurrency(edital.valor_maximo);
        document.getElementById('edital_data_pub').value = edital.data_publicacao;
        document.getElementById('edital_prazo').value = edital.prazo_envio;
        document.getElementById('edital_situacao').value = edital.situacao;
        document.getElementById('edital_url_pdf').value = edital.pdf_url;
        document.getElementById('edital_link').value = edital.link;
        document.getElementById('edital_status').value = edital.status || 'Ativo';
        document.getElementById('edital_id_org').value = edital.id_organizacao || '';

        document.getElementById('editalModalTitle').textContent = 'Editar Edital';
        modal.style.display = 'flex';
    } catch (error) {
        alert('Erro ao carregar dados: ' + error.message);
    }
}

async function deleteEdital(id) {
    if (!confirm('Excluir este edital permanentemente?')) return;
    try {
        const { error } = await supabaseClient.from('edital').delete().eq('id_edital', id);
        if (error) throw error;
        alert('Edital removido!');
        loadManualEditais();
    } catch (error) {
        alert('Erro ao excluir: ' + error.message);
    }
}

// --- GESTÃO DE CLIENTES ---

let todosClientes = [];

async function loadClients() {
    const tableBody = document.getElementById('clientTableBody');
    if (!tableBody) return;

    try {
        const { data: clientes, error } = await supabaseClient
            .from('cliente')
            .select('*')
            .order('id_cliente', { ascending: true });

        if (error) throw error;

        todosClientes = clientes;
        renderClientTable(clientes);

    } catch (error) {
        console.error('Erro ao carregar clientes:', error);
        tableBody.innerHTML = '<tr><td colspan="6">Erro ao carregar dados.</td></tr>';
    }
}

function renderClientTable(lista) {
    const tableBody = document.getElementById('clientTableBody');
    if (!tableBody) return;

    if (lista.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px;">Nenhum cliente encontrado.</td></tr>';
        return;
    }

    tableBody.innerHTML = lista.map(client => `
        <tr>
            <td>${client.id_cliente}</td>
            <td>${client.nome_empresa}</td>
            <td>${client.cnpj}</td>
            <td>${client.cidade || '-'}/${client.estado || '-'}</td>
            <td>${client.setor || '-'}</td>
            <td>
                <select class="status-select" onchange="updateClientStatus(${client.id_cliente}, this.value)">
                    <option value="Ativo" ${client.status === 'Ativo' ? 'selected' : ''}>Ativo</option>
                    <option value="Inativo" ${client.status === 'Inativo' ? 'selected' : ''}>Inativo</option>
                </select>
            </td>
            <td>
                <button class="btn-action btn-edit" onclick="editClient(${client.id_cliente})">Editar</button>
                <button class="btn-action btn-delete" onclick="deleteClient(${client.id_cliente})">Deletar</button>
            </td>
        </tr>
    `).join('');
}

async function updateClientStatus(id, newStatus) {
    try {
        const { error } = await supabaseClient
            .from('cliente')
            .update({ status: newStatus })
            .eq('id_cliente', id);

        if (error) throw error;
        
        // Sincroniza local
        const client = todosClientes.find(c => c.id_cliente === id);
        if (client) client.status = newStatus;
        
        console.log(`Status do cliente ${id} atualizado para ${newStatus}`);
    } catch (error) {
        alert('Erro ao atualizar status: ' + error.message);
        loadClients();
    }
}

function setupClientRegistration() {
    const modal = document.getElementById('clientModal');
    const openBtn = document.getElementById('btnOpenClientModal');
    const closeBtn = document.getElementById('closeClientModal');
    const cancelBtn = document.getElementById('cancelClientBtn');
    const clientForm = document.getElementById('clientForm');

    if (!modal || !openBtn) return;

    // Configurar atualização dos displays dos ranges financeiros
    const ranges = [
        { id: 'faturamento_anual', display: 'display_faturamento' },
        { id: 'capital_social', display: 'display_capital' },
        { id: 'interesse_valor_min', display: 'display_min' },
        { id: 'interesse_valor_max', display: 'display_max' }
    ];

    ranges.forEach(range => {
        const input = document.getElementById(range.id);
        const display = document.getElementById(range.display);
        if (input && display) {
            input.addEventListener('input', () => {
                display.textContent = formatCurrency(parseFloat(input.value));
            });
        }
    });

    openBtn.addEventListener('click', () => {
        clientForm.reset();
        // Resetar displays
        ranges.forEach(range => {
            const display = document.getElementById(range.display);
            if (display) display.textContent = 'R$ 0,00';
        });
        document.getElementById('editClientId').value = '';
        document.getElementById('clientModalTitle').textContent = 'Cadastrar Novo Cliente';
        modal.style.display = 'flex';
    });

    const closeModal = () => {
        modal.style.display = 'none';
        clientForm.reset();
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Enviar formulário para o Supabase
    clientForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('editClientId').value;
        const btnSave = document.getElementById('btnSaveClient');
        const originalText = btnSave.textContent;

        try {
            btnSave.textContent = 'Salvando...';
            btnSave.disabled = true;

            const clientData = {
                nome_empresa: document.getElementById('nome_empresa').value,
                razao_social: document.getElementById('razao_social').value,
                cnpj: document.getElementById('cnpj').value,
                data_abertura: document.getElementById('data_abertura').value || null,
                natureza_juridica: document.getElementById('natureza_juridica').value,
                porte_empresa: document.getElementById('porte_empresa').value,
                setor: document.getElementById('setor').value,
                cnae_principal: document.getElementById('cnae_principal').value,
                pais: document.getElementById('pais').value,
                estado: document.getElementById('estado').value,
                cidade: document.getElementById('cidade').value,
                regiao: document.getElementById('regiao').value,
                faturamento_anual: parseFloat(document.getElementById('faturamento_anual').value) || 0,
                numero_funcionarios: parseInt(document.getElementById('numero_funcionarios').value) || 0,
                capital_social: parseFloat(document.getElementById('capital_social').value) || 0,
                area_inovacao: document.getElementById('area_inovacao').value,
                tem_projeto_inovacao: document.getElementById('tem_projeto_inovacao').checked,
                descricao_projeto: document.getElementById('descricao_projeto').value,
                nivel_maturidade: document.getElementById('nivel_maturidade').value,
                possui_certidao_negativa: document.getElementById('possui_certidao_negativa').checked,
                regular_fiscal: document.getElementById('regular_fiscal').checked,
                regular_trabalhista: document.getElementById('regular_trabalhista').checked,
                interesse_temas: document.getElementById('interesse_temas').value,
                interesse_valor_min: parseFloat(document.getElementById('interesse_valor_min').value) || 0,
                interesse_valor_max: parseFloat(document.getElementById('interesse_valor_max').value) || 0,
                disponibilidade_contrapartida: document.getElementById('disponibilidade_contrapartida').checked,
                status: document.getElementById('newClientStatus').value
            };

            let result;
            if (id) {
                result = await supabaseClient.from('cliente').update(clientData).eq('id_cliente', id);
            } else {
                result = await supabaseClient.from('cliente').insert([clientData]);
            }

            if (result.error) throw result.error;

            alert(id ? 'Cliente atualizado com sucesso!' : 'Cliente cadastrado com sucesso!');
            closeModal();
            loadClients();
        } catch (error) {
            alert('Erro ao salvar cliente: ' + error.message);
        } finally {
            btnSave.textContent = originalText;
            btnSave.disabled = false;
        }
    });
}

async function editClient(id) {
    const modal = document.getElementById('clientModal');
    const form = document.getElementById('clientForm');

    try {
        const { data: client, error } = await supabaseClient
            .from('cliente')
            .select('*')
            .eq('id_cliente', id)
            .single();

        if (error) throw error;

        document.getElementById('editClientId').value = client.id_cliente;
        document.getElementById('nome_empresa').value = client.nome_empresa;
        document.getElementById('razao_social').value = client.razao_social;
        document.getElementById('cnpj').value = client.cnpj;
        document.getElementById('data_abertura').value = client.data_abertura;
        document.getElementById('natureza_juridica').value = client.natureza_juridica;
        document.getElementById('porte_empresa').value = client.porte_empresa;
        document.getElementById('setor').value = client.setor;
        document.getElementById('cnae_principal').value = client.cnae_principal;
        document.getElementById('pais').value = client.pais;
        document.getElementById('estado').value = client.estado;
        document.getElementById('cidade').value = client.cidade;
        document.getElementById('regiao').value = client.regiao;
        document.getElementById('faturamento_anual').value = client.faturamento_anual;
        document.getElementById('display_faturamento').textContent = formatCurrency(client.faturamento_anual);
        document.getElementById('numero_funcionarios').value = client.numero_funcionarios;
        document.getElementById('capital_social').value = client.capital_social;
        document.getElementById('display_capital').textContent = formatCurrency(client.capital_social);
        document.getElementById('area_inovacao').value = client.area_inovacao;
        document.getElementById('tem_projeto_inovacao').checked = client.tem_projeto_inovacao;
        document.getElementById('descricao_projeto').value = client.descricao_projeto;
        document.getElementById('nivel_maturidade').value = client.nivel_maturidade;
        document.getElementById('possui_certidao_negativa').checked = client.possui_certidao_negativa;
        document.getElementById('regular_fiscal').checked = client.regular_fiscal;
        document.getElementById('regular_trabalhista').checked = client.regular_trabalhista;
        document.getElementById('interesse_temas').value = client.interesse_temas;
        document.getElementById('interesse_valor_min').value = client.interesse_valor_min;
        document.getElementById('display_min').textContent = formatCurrency(client.interesse_valor_min);
        document.getElementById('interesse_valor_max').value = client.interesse_valor_max;
        document.getElementById('display_max').textContent = formatCurrency(client.interesse_valor_max);
        document.getElementById('disponibilidade_contrapartida').checked = client.disponibilidade_contrapartida;
        document.getElementById('newClientStatus').value = client.status || 'Ativo';

        document.getElementById('clientModalTitle').textContent = 'Editar Cliente';
        modal.style.display = 'flex';
    } catch (error) {
        alert('Erro ao carregar dados: ' + error.message);
    }
}

async function deleteClient(id) {
    if (!confirm('Excluir este cliente permanentemente?')) return;
    try {
        const { error } = await supabaseClient.from('cliente').delete().eq('id_cliente', id);
        if (error) throw error;
        alert('Cliente removido!');
        loadClients();
    } catch (error) {
        alert('Erro ao excluir: ' + error.message);
    }
}

// --- GESTÃO DE USUÁRIOS ---

let todosUsuarios = []; // Armazena a lista completa para filtragem local

function setupUserFilterListeners() {
    const searchInput = document.getElementById('searchUser');
    const typeFilter = document.getElementById('filterType');
    const statusFilter = document.getElementById('filterUserStatus');
    
    if (searchInput) searchInput.addEventListener('input', applyUserFilters);
    if (typeFilter) typeFilter.addEventListener('change', applyUserFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyUserFilters);
}

function applyUserFilters() {
    const searchTerm = document.getElementById('searchUser').value.toLowerCase();
    const typeTerm = document.getElementById('filterType').value;
    const statusTerm = document.getElementById('filterUserStatus').value;

    const usuariosFiltrados = todosUsuarios.filter(user => {
        const matchesSearch = user.nome.toLowerCase().includes(searchTerm) || 
                            user.nome_email.toLowerCase().includes(searchTerm);
        const matchesType = typeTerm === "" || user.tipo_usuario === typeTerm;
        const matchesStatus = statusTerm === "" || user.status === statusTerm;
        
        return matchesSearch && matchesType && matchesStatus;
    });

    renderUserTable(usuariosFiltrados);
}

async function loadUsers() {
    const tableBody = document.getElementById('userTableBody');
    if (!tableBody) return;

    try {
        const { data: usuarios, error } = await supabaseClient
            .from('usuario')
            .select('*')
            .order('id_usuario', { ascending: true });

        if (error) throw error;

        todosUsuarios = usuarios; // Guarda na global
        renderUserTable(usuarios);

    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        tableBody.innerHTML = '<tr><td colspan="6">Erro ao carregar dados.</td></tr>';
    }
}

function renderUserTable(lista) {
    const tableBody = document.getElementById('userTableBody');
    if (!tableBody) return;

    if (lista.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px;">Nenhum usuário encontrado.</td></tr>';
        return;
    }

    tableBody.innerHTML = lista.map(user => `
        <tr>
            <td>${user.id_usuario}</td>
            <td>${user.nome}</td>
            <td>${user.nome_email}</td>
            <td>${user.tipo_usuario}</td>
            <td>${user.nivel_acesso}</td>
            <td>
                <select class="status-select" onchange="updateUserStatus(${user.id_usuario}, this.value)">
                    <option value="Ativo" ${user.status === 'Ativo' ? 'selected' : ''}>Ativo</option>
                    <option value="Inativo" ${user.status === 'Inativo' ? 'selected' : ''}>Inativo</option>
                </select>
            </td>
            <td>
                <button class="btn-action btn-edit" onclick="editUser(${user.id_usuario})">Editar</button>
                <button class="btn-action btn-delete" onclick="deleteUser(${user.id_usuario})">Deletar</button>
            </td>
        </tr>
    `).join('');
}

async function updateUserStatus(id, newStatus) {
    try {
        const { error } = await supabaseClient
            .from('usuario')
            .update({ status: newStatus })
            .eq('id_usuario', id);

        if (error) throw error;
        
        // Atualiza a lista local para manter sincronizado
        const user = todosUsuarios.find(u => u.id_usuario === id);
        if (user) user.status = newStatus;
        
        console.log(`Status do usuário ${id} atualizado para ${newStatus}`);
    } catch (error) {
        alert('Erro ao atualizar status: ' + error.message);
        loadUsers(); // Recarrega em caso de erro
    }
}

function setupSidebarNavigation() {
    const links = document.querySelectorAll('.sidebar-link');
    const sections = document.querySelectorAll('.admin-section');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('data-target');

            // Atualiza links
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Atualiza seções
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === `section-${target}`) {
                    section.classList.add('active');
                }
            });
        });
    });
}

async function deleteUser(id) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;

    try {
        const { error } = await supabaseClient
            .from('usuario')
            .delete()
            .eq('id_usuario', id);

        if (error) throw error;

        alert('Usuário excluído com sucesso!');
        loadUsers();
    } catch (error) {
        alert('Erro ao excluir: ' + error.message);
    }
}

async function editUser(id) {
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('userModalTitle') || document.getElementById('modalTitle');
    const form = document.getElementById('userForm');

    try {
        const { data: user, error } = await supabaseClient
            .from('usuario')
            .select('*')
            .eq('id_usuario', id)
            .single();

        if (error) throw error;

        // Preenche o formulário
        document.getElementById('editUserId').value = user.id_usuario;
        document.getElementById('newUserName').value = user.nome;
        document.getElementById('newUserEmail').value = user.nome_email;
        document.getElementById('newUserPassword').value = user.senha;
        const roleField = document.getElementById('newUserType') || document.getElementById('newUserRole');
        if (roleField) roleField.value = user.tipo_usuario;
        document.getElementById('newUserLevel').value = user.nivel_acesso;
        document.getElementById('newUserStatus').value = user.status || 'Ativo';

        if (modalTitle) modalTitle.textContent = 'Editar Usuário';
        modal.style.display = 'flex';
    } catch (error) {
        alert('Erro ao carregar dados do usuário: ' + error.message);
    }
}

// Modificar a função setupUserRegistration original para suportar edição
function setupUserRegistration() {
    const modal = document.getElementById('userModal');
    const openBtn = document.getElementById('userRegisterLink');
    const closeBtn = document.getElementById('closeUserModal') || document.querySelector('.close-modal');
    const cancelBtn = document.getElementById('cancelUserBtn') || document.getElementById('cancelBtn');
    const userForm = document.getElementById('userForm');
    const modalTitle = document.getElementById('userModalTitle') || document.getElementById('modalTitle');

    if (!modal || !openBtn) return;

    // Abrir modal para NOVO cadastro
    openBtn.addEventListener('click', (e) => {
        e.preventDefault();
        userForm.reset();
        document.getElementById('editUserId').value = '';
        if (modalTitle) modalTitle.textContent = 'Cadastrar Novo Usuário';
        modal.style.display = 'flex';
    });

    const closeModal = () => {
        modal.style.display = 'none';
        userForm.reset();
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    userForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('editUserId').value;
        const name = document.getElementById('newUserName').value;
        const emailValue = document.getElementById('newUserEmail').value;
        const password = document.getElementById('newUserPassword').value;
        const role = (document.getElementById('newUserType') || document.getElementById('newUserRole')).value;
        const level = parseInt(document.getElementById('newUserLevel').value);
        const status = document.getElementById('newUserStatus').value;

        const btnSave = document.getElementById('btnSaveUser') || userForm.querySelector('.btn-save');
        const originalText = btnSave.textContent;
        
        try {
            btnSave.textContent = 'Salvando...';
            btnSave.disabled = true;

            const userData = { 
                nome: name, 
                nome_email: emailValue,
                senha: password, 
                tipo_usuario: role, 
                nivel_acesso: level,
                status: status
            };

            let result;
            if (id) {
                // Modo Edição
                result = await supabaseClient
                    .from('usuario')
                    .update(userData)
                    .eq('id_usuario', id);
            } else {
                // Modo Novo Cadastro
                result = await supabaseClient
                    .from('usuario')
                    .insert([userData]);
            }

            if (result.error) throw result.error;

            alert(id ? 'Usuário atualizado!' : 'Usuário cadastrado com sucesso!');
            closeModal();
            loadUsers(); // Recarregar a lista
        } catch (error) {
            console.error('Erro ao salvar usuário:', error);
            alert('Erro ao salvar: ' + (error.message || 'Erro desconhecido'));
        } finally {
            btnSave.textContent = originalText;
            btnSave.disabled = false;
        }
    });
}

function setupFilterListeners() {
    const filters = [
        'stateFilter',
        'nacionalFilter',
        'internacionalFilter',
        'keywordFilter',
        'resourceTypeFilter',
        'creditRange',
        'startDateFilter',
        'endDateFilter',
        'areaFilter',
        'fapergFilter',
        'finepFilter',
        'bndesFilter',
        'cordisFilter'
    ];
    
    filters.forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) {
            if (filterId === 'creditRange') {
                element.addEventListener('input', applyFilters);
            } else {
                element.addEventListener('change', applyFilters);
            }
        }
    });
    
    // Busca global
    document.getElementById('globalSearch').addEventListener('input', applyFilters);
    
    // Limpar filtros
    document.getElementById('clearFiltersBtn').addEventListener('click', clearAllFilters);
}

function applyFilters() {
    // Atualizar display do range
    const creditRange = document.getElementById('creditRange');
    const creditDisplay = document.getElementById('creditDisplay');
    const value = parseInt(creditRange.value);
    creditDisplay.textContent = formatCurrency(value);
    
    // Aplicar filtros na lista UNIFICADA
    editaisFiltrados = todosOsEditaisUnificados.filter(edital => {
        // Filtro de estado
        const stateFilter = document.getElementById('stateFilter').value;
        if (stateFilter && edital.estado && edital.estado !== stateFilter) return false;
        
        // Filtro de localidade
        const nacional = document.getElementById('nacionalFilter').checked;
        const internacional = document.getElementById('internacionalFilter').checked;
        if ((nacional || internacional) && 
            !((nacional && edital.localidade === 'Nacional') || 
              (internacional && edital.localidade === 'Internacional'))) {
            return false;
        }
        
        // Filtro de palavras-chave
        const keyword = document.getElementById('keywordFilter').value.toLowerCase();
        if (keyword && !edital.titulo.toLowerCase().includes(keyword) && 
            !edital.area.toLowerCase().includes(keyword) &&
            !edital.orgao.toLowerCase().includes(keyword)) {
            return false;
        }
        
        // Filtro de tipo de recurso
        const resourceType = document.getElementById('resourceTypeFilter').value;
        if (resourceType && edital.tipoRecurso !== resourceType) return false;
        
        // Filtro de crédito
        const creditMax = parseInt(document.getElementById('creditRange').value);
        if (edital.valor > creditMax) return false;
        
        // Filtro de datas
        const startDate = document.getElementById('startDateFilter').value;
        const endDate = document.getElementById('endDateFilter').value;
        
        if (edital.dataLimite) {
            const editalDate = new Date(edital.dataLimite);
            if (startDate && new Date(startDate) > editalDate) return false;
            if (endDate && new Date(endDate) < editalDate) return false;
        }
        
        // Filtro de área
        const area = document.getElementById('areaFilter').value;
        if (area && edital.area !== area) return false;
        
        // Filtro de órgão
        const fapergs = document.getElementById('fapergFilter').checked;
        const finep = document.getElementById('finepFilter').checked;
        const bndes = document.getElementById('bndesFilter').checked;
        const cordis = document.getElementById('cordisFilter').checked;
        
        if ((fapergs || finep || bndes || cordis)) {
            const orgaoUpper = edital.orgao.toUpperCase();
            const matchesOrgao = (fapergs && orgaoUpper.includes('FAPERGS')) ||
                                (finep && orgaoUpper.includes('FINEP')) ||
                                (bndes && orgaoUpper.includes('BNDES')) ||
                                (cordis && orgaoUpper.includes('CORDIS'));
            if (!matchesOrgao) return false;
        }
        
        // Filtro de busca global
        const globalSearch = document.getElementById('globalSearch').value.toLowerCase();
        if (globalSearch && !edital.titulo.toLowerCase().includes(globalSearch) &&
            !edital.orgao.toLowerCase().includes(globalSearch) &&
            !edital.area.toLowerCase().includes(globalSearch)) {
            return false;
        }
        
        return true;
    });
    
    renderEditais(editaisFiltrados);
}

const ORG_WEBSITES = {
    'FINEP': 'https://www.finep.gov.br',
    'BNDES': 'https://www.bndes.gov.br',
    'CNPQ': 'https://www.cnpq.br',
    'FAPERGS': 'https://fapergs.rs.gov.br',
    'FAPESP': 'https://fapesp.br',
    'CORDIS': 'https://cordis.europa.eu',
    'MCTI': 'https://www.gov.br/mcti',
    'MAPA': 'https://www.gov.br/agricultura',
    'MEC': 'https://www.gov.br/mec',
    'MINISTÉRIO DA SAÚDE': 'https://www.gov.br/saude',
};

function renderEditais(lista) {
    const container = document.getElementById('editaisList');
    const count = document.getElementById('editalsCount');
    
    // Obter configurações do localStorage para o ícone
    let systemSettings = { logoImage: null };
    try {
        const saved = localStorage.getItem('editalFinderSettings');
        if (saved) systemSettings = JSON.parse(saved);
    } catch (e) { console.error('Erro ao ler settings:', e); }

    if (!container || !count) return;

    // Atualizar contador
    count.textContent = `Mostrando ${lista.length} edital${lista.length !== 1 ? 's' : ''}`;
    
    if (lista.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>Nenhum edital encontrado</h3>
                <p>Tente ajustar seus filtros para encontrar mais oportunidades.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = lista.map(edital => {
        const siteLink = edital.linkOriginal || edital.orgSite || ORG_WEBSITES[edital.orgao?.toUpperCase()] || null;
        const pdfLink = edital.pdfUrl || null;
        
        const siteIcon = systemSettings.logoImage 
            ? `<img src="${systemSettings.logoImage}" alt="Logo" style="max-height: 18px; width: auto;">`
            : '🌐';

        const siteIconDisabled = systemSettings.logoImage 
            ? `<img src="${systemSettings.logoImage}" alt="Logo" style="max-height: 18px; width: auto; filter: grayscale(100%);">`
            : '🌐';

        return `
        <div class="edital-card ${edital.isManual ? 'edital-card-manual' : ''}">
            <h3 class="edital-title">${edital.titulo}</h3>
            <span class="edital-badge">${edital.orgao}</span>
            
            <div class="edital-meta">
                <div class="edital-meta-row">
                    <span class="edital-meta-label">Área:</span>
                    <span>${edital.area}</span>
                </div>
                <div class="edital-meta-row">
                    <span class="edital-meta-label">Valor:</span>
                    <span class="edital-value">${formatCurrency(edital.valor)}</span>
                </div>
                <div class="edital-meta-row">
                    <span class="edital-meta-label">Localidade:</span>
                    <span>${edital.localidade}</span>
                </div>
                <div class="edital-meta-row">
                    <span class="edital-meta-label">Tipo:</span>
                    <span>${edital.tipoRecurso}</span>
                </div>
            </div>
            
            <div class="edital-date">
                📅 Limite: ${edital.dataLimite ? formatDate(edital.dataLimite) : 'Não informado'}
            </div>
            
            <div class="edital-actions" style="display: flex; gap: 8px; margin-top: 12px;">
                ${siteLink ? `
                    <a href="${siteLink}" target="_blank" class="btn-view" style="text-decoration: none; text-align: center; flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        ${siteIcon} Site
                    </a>
                ` : `
                    <span class="btn-view disabled" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        ${siteIconDisabled} Site
                    </span>
                `}
                
                ${pdfLink ? `
                    <a href="${pdfLink}" target="_blank" class="btn-pdf" style="text-decoration: none; text-align: center; flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        📄 PDF
                    </a>
                ` : `
                    <span class="btn-pdf disabled" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        📄 PDF
                    </span>
                `}
            </div>
        </div>
    `}).join('');
}

function clearAllFilters() {
    // Limpar todos os inputs
    document.getElementById('stateFilter').value = '';
    document.getElementById('nacionalFilter').checked = false;
    document.getElementById('internacionalFilter').checked = false;
    document.getElementById('keywordFilter').value = '';
    document.getElementById('resourceTypeFilter').value = '';
    document.getElementById('creditRange').value = '100000000';
    document.getElementById('startDateFilter').value = '';
    document.getElementById('endDateFilter').value = '';
    document.getElementById('areaFilter').value = '';
    document.getElementById('fapergFilter').checked = false;
    document.getElementById('finepFilter').checked = false;
    document.getElementById('bndesFilter').checked = false;
    document.getElementById('cordisFilter').checked = false;
    document.getElementById('globalSearch').value = '';
    
    // Atualizar display do range
    document.getElementById('creditDisplay').textContent = 'R$ 100 mi';
    
    // Renderizar todos os editais
    renderEditais(editais);
}

function setupLogout() {
    document.getElementById('logoutBtn').addEventListener('click', function() {
        localStorage.removeItem('editalFinderUser');
        window.location.href = 'index.html';
    });
}

function setupExport() {
    document.getElementById('exportBtn').addEventListener('click', function() {
        if (editaisFiltrados.length === 0) {
            alert('Nenhum edital para exportar. Ajuste seus filtros.');
            return;
        }
        
        // Criar CSV
        let csv = 'Título,Órgão,Área,Valor,Localidade,Data Limite,Tipo de Recurso\n';
        
        editaisFiltrados.forEach(edital => {
            csv += `"${edital.titulo}","${edital.orgao}","${edital.area}","${formatCurrency(edital.valor)}","${edital.localidade}","${formatDate(edital.dataLimite)}","${edital.tipoRecurso}"\n`;
        });
        
        // Criar blob e download
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `editais_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        alert(`${editaisFiltrados.length} edital(is) exportado(s) com sucesso!`);
    });
}

// ============================================
// FUNÇÕES UTILITÁRIAS
// ============================================

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Verificar qual página estamos
    if (document.getElementById('loginForm')) {
        initLogin();
    } else if (document.getElementById('editaisList')) {
        initDashboard();
    } else if (document.getElementById('userTableBody') || document.getElementById('clientTableBody')) {
        initAdminPage();
    }
});
