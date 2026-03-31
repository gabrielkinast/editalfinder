import { useState, useEffect, useMemo } from 'react';
import Header from '../components/layout/Header';
import AdminTable from '../components/admin/AdminTable';
import UserForm from '../components/admin/UserForm';
import ClientForm from '../components/admin/ClientForm';
import OrgForm from '../components/admin/OrgForm';
import EditalForm from '../components/admin/EditalForm';
import Modal from '../components/ui/Modal';
import { dataService } from '../services/dataService';
import { formatCurrency, formatDate } from '../utils/formatters';
import { usePermissions } from '../hooks/usePermissions';

export default function Cadastros() {
  const permissions = usePermissions();
  // Se não puder gerenciar usuários, começa na aba de clientes
  const [activeTab, setActiveTab] = useState(permissions.canManageUsers ? 'usuarios' : 'clientes');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [selectedOrgs, setSelectedOrgs] = useState([]);
  const [filterMinInteresse, setFilterMinInteresse] = useState(0);
  const [filterMaxInteresse, setFilterMaxInteresse] = useState(100000000);
  const [filterPorte, setFilterPorte] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      let result = [];
      if (activeTab === 'usuarios') result = await dataService.getUsers();
      else if (activeTab === 'clientes') result = await dataService.getClients();
      else if (activeTab === 'organizacoes') result = await dataService.getOrganizations();
      else if (activeTab === 'editais-cadastrados') result = await dataService.getAllEditaisAdmin();
      setData(result);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      alert('Erro ao carregar dados.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    setSearchTerm('');
    setFilterType('');
    setFilterStatus('');
    setSelectedOrgs([]);
    setFilterMinInteresse(0);
    setFilterMaxInteresse(100000000);
    setFilterPorte('');
  }, [activeTab]);

  const availableOrgs = useMemo(() => {
    if (activeTab !== 'editais-cadastrados') return [];
    const orgs = new Set();
    data.forEach(item => {
      if (item.fonte_recurso) {
        orgs.add(item.fonte_recurso.toUpperCase());
      }
    });
    return Array.from(orgs).sort();
  }, [data, activeTab]);

  const filteredData = useMemo(() => {
    return data.filter(item => {
      const s = searchTerm.toLowerCase();
      
      let matchesSearch = true;
      if (activeTab === 'usuarios') {
        matchesSearch = (item.nome?.toLowerCase() || '').includes(s) || (item.nome_email?.toLowerCase() || '').includes(s);
      } else if (activeTab === 'clientes') {
        matchesSearch = (item.nome_empresa?.toLowerCase() || '').includes(s) || (item.cnpj || '').includes(s);
      } else if (activeTab === 'organizacoes') {
        matchesSearch = (item.nome?.toLowerCase() || '').includes(s) || (item.tipo?.toLowerCase() || '').includes(s);
      } else if (activeTab === 'editais-cadastrados') {
        matchesSearch = (item.titulo?.toLowerCase() || '').includes(s) || (item.fonte_recurso?.toLowerCase() || '').includes(s);
      }

      const matchesType = !filterType || (activeTab === 'usuarios' ? item.tipo_usuario === filterType : true);
      const matchesStatus = activeTab === 'editais-cadastrados' ? true : (!filterStatus || item.status === filterStatus);
      
      const matchesOrg = activeTab === 'editais-cadastrados' 
        ? (selectedOrgs.length === 0 || selectedOrgs.includes(item.fonte_recurso?.toUpperCase()))
        : true;

      let matchesClientFilters = true;
      if (activeTab === 'clientes') {
        const valMin = item.interesse_valor_min || 0;
        const valMax = item.interesse_valor_max || 0;
        const porteMatch = !filterPorte || item.porte_empresa === filterPorte;
        const valueMatch = (valMax >= filterMinInteresse) && (valMin <= filterMaxInteresse);
        matchesClientFilters = porteMatch && valueMatch;
      }

      return matchesSearch && matchesType && matchesStatus && matchesOrg && matchesClientFilters;
    });
  }, [data, searchTerm, filterType, filterStatus, selectedOrgs, filterMinInteresse, filterMaxInteresse, filterPorte, activeTab]);

  const handleSave = async (formData) => {
    try {
      if (activeTab === 'usuarios') {
        if (editingItem) await dataService.updateUser(editingItem.id_usuario, formData);
        else await dataService.createUser(formData);
      } else if (activeTab === 'clientes') {
        if (editingItem) await dataService.updateClient(editingItem.id_cliente, formData);
        else await dataService.createClient(formData);
      } else if (activeTab === 'organizacoes') {
        if (editingItem) await dataService.updateOrganization(editingItem.id_organizacao, formData);
        else await dataService.createOrganization(formData);
      } else if (activeTab === 'editais-cadastrados') {
        if (editingItem) await dataService.updateEdital(editingItem.id_edital, formData);
        else await dataService.createEdital(formData);
      }
      setIsModalOpen(false);
      setEditingItem(null);
      loadData();
    } catch (error) {
      alert('Erro ao salvar: ' + error.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Deseja realmente excluir este item?')) return;
    try {
      if (activeTab === 'usuarios') await dataService.deleteUser(id);
      else if (activeTab === 'clientes') await dataService.deleteClient(id);
      else if (activeTab === 'organizacoes') await dataService.deleteOrganization(id);
      else if (activeTab === 'editais-cadastrados') await dataService.deleteEdital(id);
      loadData();
    } catch (error) {
      alert('Erro ao excluir: ' + error.message);
    }
  };

  const columns = useMemo(() => {
    if (activeTab === 'usuarios') return [
      { key: 'id_usuario', label: 'ID' },
      { key: 'nome', label: 'Nome' },
      { key: 'nome_email', label: 'Email' },
      { key: 'tipo_usuario', label: 'Tipo' },
      { key: 'nivel_acesso', label: 'Nível' },
      { key: 'status', label: 'Status' },
    ];
    if (activeTab === 'clientes') return [
      { key: 'id_cliente', label: 'ID' },
      { key: 'nome_empresa', label: 'Empresa' },
      { key: 'cnpj', label: 'CNPJ' },
      { key: 'setor', label: 'Setor' },
      { key: 'porte_empresa', label: 'Porte' },
      { key: 'status', label: 'Status' },
    ];
    if (activeTab === 'organizacoes') return [
      { key: 'id_organizacao', label: 'ID' },
      { key: 'nome', label: 'Nome' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'estado', label: 'UF' },
      { key: 'status', label: 'Status' },
    ];
    if (activeTab === 'editais-cadastrados') return [
      { key: 'id_edital', label: 'ID' },
      { key: 'titulo', label: 'Título' },
      { key: 'fonte_recurso', label: 'Fonte' },
      { key: 'valor_maximo', label: 'Valor Máx.', render: (v) => formatCurrency(v) },
      { key: 'prazo_envio', label: 'Prazo', render: (v) => v ? formatDate(v) : '-' },
      { key: 'status', label: 'Status' },
    ];
    return [];
  }, [activeTab]);

  const renderForm = () => {
    const props = { initialData: editingItem, onSave: handleSave, onCancel: () => setIsModalOpen(false) };
    if (activeTab === 'usuarios') return <UserForm {...props} />;
    if (activeTab === 'clientes') return <ClientForm {...props} />;
    if (activeTab === 'organizacoes') return <OrgForm {...props} />;
    if (activeTab === 'editais-cadastrados') return <EditalForm {...props} />;
    return null;
  };

  return (
    <>
      <Header />
      <div className="admin-container">
        <aside className="admin-sidebar">
          <h2 className="sidebar-title">Cadastros</h2>
          <nav className="sidebar-nav">
            {permissions.canManageUsers && (
              <button className={`sidebar-link ${activeTab === 'usuarios' ? 'active' : ''}`} onClick={() => setActiveTab('usuarios')}>
                <span className="icon">👤</span> Usuários
              </button>
            )}
            <button className={`sidebar-link ${activeTab === 'clientes' ? 'active' : ''}`} onClick={() => setActiveTab('clientes')}>
              <span className="icon">🏢</span> Clientes
            </button>
            <button className={`sidebar-link ${activeTab === 'organizacoes' ? 'active' : ''}`} onClick={() => setActiveTab('organizacoes')}>
              <span className="icon">🏛️</span> Organizações
            </button>
            <button className={`sidebar-link ${activeTab === 'editais-cadastrados' ? 'active' : ''}`} onClick={() => setActiveTab('editais-cadastrados')}>
              <span className="icon">📄</span> Editais
            </button>
          </nav>
        </aside>
        <main className="admin-main">
          <section className="admin-section active">
            <div className="section-header">
              <h2>{activeTab === 'usuarios' ? 'Cadastro de Usuários' : activeTab === 'clientes' ? 'Cadastro de Clientes' : activeTab === 'organizacoes' ? 'Cadastro de Organizações' : 'Cadastro de Editais'}</h2>
              {/* Somente exibe o botão Novo se tiver permissão de criação. Se for na aba usuários, precisa de permissão canManageUsers */}
              {permissions.canCreate && (activeTab !== 'usuarios' || permissions.canManageUsers) && (
                <button className="btn-primary" onClick={() => { setEditingItem(null); setIsModalOpen(true); }}>
                  + Novo {activeTab === 'usuarios' ? 'Usuário' : activeTab === 'clientes' ? 'Cliente' : activeTab === 'organizacoes' ? 'Organização' : 'Edital'}
                </button>
              )}
            </div>

            <div className="filters-bar" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '10px', width: '100%', flexWrap: 'wrap' }}>
                <input 
                  type="text" 
                  placeholder="Buscar..." 
                  className="filter-input-large"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                {activeTab === 'usuarios' && (
                  <select className="filter-select-small" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                    <option value="">Todos os tipos</option>
                    <option value="Administrador">Administrador</option>
                    <option value="Consultor">Consultor</option>
                    <option value="Funcionário">Funcionário</option>
                  </select>
                )}
                {activeTab !== 'editais-cadastrados' && (
                  <select className="filter-select-small" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                    <option value="">Todos os status</option>
                    <option value="Ativo">Ativo</option>
                    <option value="Inativo">Inativo</option>
                  </select>
                )}
                {activeTab === 'clientes' && (
                  <>
                    <select className="filter-select-small" value={filterPorte} onChange={(e) => setFilterPorte(e.target.value)}>
                      <option value="">Todos os portes</option>
                      <option value="MEI">MEI</option>
                      <option value="ME">ME</option>
                      <option value="EPP">EPP</option>
                      <option value="Média">Média</option>
                      <option value="Grande">Grande</option>
                    </select>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minWidth: '200px' }}>
                      <span style={{ fontSize: '13px', fontWeight: '500' }}>Interesse até: <strong>{formatCurrency(filterMaxInteresse)}</strong></span>
                      <input 
                        type="range" 
                        min="0" 
                        max="50000000" 
                        step="5000"
                        className="range-slider"
                        value={filterMaxInteresse} 
                        onChange={(e) => setFilterMaxInteresse(Number(e.target.value))} 
                      />
                    </div>
                  </>
                )}
              </div>

              {activeTab === 'editais-cadastrados' && availableOrgs.length > 0 && (
                <div className="org-filters" style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '8px', width: '100%' }}>
                  <span style={{ fontWeight: '600', color: 'var(--primary-color)', width: '100%', marginBottom: '5px' }}>Filtrar por Órgão Financiador:</span>
                  {availableOrgs.map(org => (
                    <label key={org} style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer', fontSize: '14px' }}>
                      <input 
                        type="checkbox" 
                        checked={selectedOrgs.includes(org)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedOrgs([...selectedOrgs, org]);
                          } else {
                            setSelectedOrgs(selectedOrgs.filter(o => o !== org));
                          }
                        }}
                      />
                      {org}
                    </label>
                  ))}
                  {selectedOrgs.length > 0 && (
                    <button 
                      onClick={() => setSelectedOrgs([])}
                      style={{ border: 'none', background: 'none', color: '#e74c3c', cursor: 'pointer', fontSize: '12px', textDecoration: 'underline', marginLeft: 'auto' }}
                    >
                      Limpar Filtros
                    </button>
                  )}
                </div>
              )}
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '50px' }}><h3>Carregando dados...</h3></div>
            ) : (
              <AdminTable 
                columns={columns} 
                data={filteredData} 
                onEdit={(item) => { setEditingItem(item); setIsModalOpen(true); }} 
                onDelete={handleDelete} 
              />
            )}
          </section>
        </main>
      </div>
      {isModalOpen && (
        <Modal 
          onClose={() => setIsModalOpen(false)} 
          className={activeTab === 'clientes' || activeTab === 'editais-manuais' ? 'modal-large' : ''}
        >
          <div className="modal-header">
            <h2>{editingItem ? 'Editar' : 'Cadastrar'} {activeTab === 'usuarios' ? 'Usuário' : activeTab === 'clientes' ? 'Cliente' : activeTab === 'organizacoes' ? 'Organização' : 'Edital'}</h2>
          </div>
          {renderForm()}
        </Modal>
      )}
    </>
  );
}
