import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import AdminTable from '../components/admin/AdminTable';
import UserForm from '../components/admin/UserForm';
import ClientForm from '../components/admin/ClientForm';
import ProjetoPrecadastroForm from '../components/admin/ProjetoPrecadastroForm';
import { readPreProjetoContext } from '../utils/precadastro/openPreProjetoFromOpportunity';
import EditalForm from '../components/admin/EditalForm';
import Modal from '../components/ui/Modal';
import { dataService } from '../services/dataService';
import { supabase, isSupabaseConfigured } from '../services/api';
import { formatCurrency, formatDate } from '../utils/formatters';
import { usePermissions } from '../hooks/usePermissions';
import { useAuth } from '../contexts/AuthContext';
import {
  attachOwnerToClientPayload,
  canEditClient,
  canViewClient,
  isAdminUser,
  sanitizeClientWritePayload,
  sessionUserId,
} from '../utils/permissions';
import {
  clientPayloadFromFormState,
  mergeClientWritePayload,
} from '../utils/cliente/clientePerfilConsultivo';
import {
  buildInitialPrecadastroState,
  loadPrecadEnvelope,
} from '../utils/precadastroProjetoInitialState';
import { calculatePreCadastroCompleteness } from '../utils/precadastro/calculatePreCadastroCompleteness';

function formatCnpjDisplay(v) {
  if (v == null || v === '') return '—';
  const d = String(v).replace(/\D/g, '');
  if (d.length !== 14) return String(v);
  return d.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
}

function cellStr(v) {
  if (v == null || v === '') return '—';
  return String(v);
}

/** @param {{ hadDraft?: boolean; status?: string } | undefined} info */
function precadBadgeDisplay(info) {
  if (!info || !info.hadDraft) {
    return { label: 'Não iniciado', cls: 'cad-precad-none' };
  }
  const s = String(info.status || 'rascunho').toLowerCase();
  if (s === 'pronto') return { label: 'Completo', cls: 'cad-precad-ready' };
  if (s === 'revisao') return { label: 'Em andamento', cls: 'cad-precad-wip' };
  return { label: 'Rascunho', cls: 'cad-precad-draft' };
}

export default function Cadastros() {
  const navigate = useNavigate();
  const permissions = usePermissions();
  const { user, loading: authLoading } = useAuth();
  const adminCadastros = isAdminUser(user);
  const showClientesTab = adminCadastros;
  const [activeTab, setActiveTab] = useState(() => {
    if (permissions.canManageUsers) return 'usuarios';
    if (isAdminUser(user)) return 'clientes';
    return 'editais-cadastrados';
  });
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPrecadModalOpen, setIsPrecadModalOpen] = useState(false);
  const [precadCliente, setPrecadCliente] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [selectedOrgs, setSelectedOrgs] = useState([]);
  const [filterMinInteresse, setFilterMinInteresse] = useState(0);
  const [filterMaxInteresse, setFilterMaxInteresse] = useState(100000000);
  const [filterPorte, setFilterPorte] = useState('');
  const [filterSetor, setFilterSetor] = useState('');

  const precadContext = useMemo(() => {
    const id = precadCliente?.id_cliente;
    if (id == null) return { editalAssociado: null, radarMatch: null };
    return readPreProjetoContext(id);
  }, [precadCliente?.id_cliente]);

  useEffect(() => {
    if (!showClientesTab && activeTab === 'clientes') {
      setActiveTab(permissions.canManageUsers ? 'usuarios' : 'editais-cadastrados');
    }
  }, [showClientesTab, activeTab, permissions.canManageUsers]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (isSupabaseConfigured && (activeTab === 'clientes' || activeTab === 'usuarios')) {
        const { data: sessWrap, error: sessErr } = await supabase.auth.getSession();
        if (import.meta.env.DEV && sessErr) {
          console.warn('[Cadastros] supabase.auth.getSession()', sessErr.message || sessErr);
        }
        if (import.meta.env.DEV && !sessWrap?.session?.access_token) {
          console.warn(
            '[Cadastros] Sem access_token na sessão antes de carregar dados; verifique login Supabase e persistência da sessão.',
          );
        }
      }

      let result = [];
      if (activeTab === 'usuarios') result = await dataService.getUsers();
      else if (activeTab === 'clientes') result = await dataService.getClients({ user });
      else if (activeTab === 'editais-cadastrados') result = await dataService.getAllEditaisAdmin();
      setData(result);
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('[Cadastros] loadData falhou', {
          tab: activeTab,
          message: error?.message,
          code: error?.code,
          details: error?.details,
          hint: error?.hint,
        });
      }
      console.error('Erro ao carregar dados:', error);
      alert('Erro ao carregar dados.');
    } finally {
      setLoading(false);
    }
  }, [activeTab, user]);

  useEffect(() => {
    if (authLoading) return;
    loadData();
    setSearchTerm('');
    setFilterType('');
    setFilterStatus('');
    setSelectedOrgs([]);
    setFilterMinInteresse(0);
    setFilterMaxInteresse(100000000);
    setFilterPorte('');
    setFilterSetor('');
  }, [loadData, authLoading]);

  const setoresDisponiveis = useMemo(() => {
    if (activeTab !== 'clientes') return [];
    const s = new Set();
    data.forEach((c) => {
      if (c?.setor) s.add(String(c.setor).trim());
    });
    return [...s].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  }, [data, activeTab]);

  const availableOrgs = useMemo(() => {
    if (activeTab !== 'editais-cadastrados') return [];
    const orgs = new Set();
    data.forEach((item) => {
      if (item.fonte_recurso) {
        orgs.add(item.fonte_recurso.toUpperCase());
      }
    });
    return Array.from(orgs).sort();
  }, [data, activeTab]);

  const filteredData = useMemo(() => {
    return data.filter((item) => {
      const s = searchTerm.toLowerCase();

      let matchesSearch = true;
      if (activeTab === 'usuarios') {
        matchesSearch =
          (item.nome?.toLowerCase() || '').includes(s) || (item.nome_email?.toLowerCase() || '').includes(s);
      } else if (activeTab === 'clientes') {
        matchesSearch =
          (item.nome_empresa?.toLowerCase() || '').includes(s) || (item.cnpj || '').includes(s);
      } else if (activeTab === 'editais-cadastrados') {
        matchesSearch =
          (item.titulo?.toLowerCase() || '').includes(s) ||
          (item.fonte_recurso?.toLowerCase() || '').includes(s);
      }

      const matchesType = !filterType || (activeTab === 'usuarios' ? item.tipo_usuario === filterType : true);
      const matchesStatus =
        activeTab === 'editais-cadastrados' ? true : !filterStatus || item.status === filterStatus;

      const matchesOrg =
        activeTab === 'editais-cadastrados'
          ? selectedOrgs.length === 0 || selectedOrgs.includes(item.fonte_recurso?.toUpperCase())
          : true;

      let matchesClientFilters = true;
      if (activeTab === 'clientes') {
        const valMin = item.interesse_valor_min || 0;
        const valMax = item.interesse_valor_max || 0;
        const porteMatch = !filterPorte || item.porte_empresa === filterPorte;
        const valueMatch = valMax >= filterMinInteresse && valMin <= filterMaxInteresse;
        const setorMatch =
          !filterSetor || String(item.setor || '').toLowerCase() === filterSetor.toLowerCase();
        matchesClientFilters = porteMatch && valueMatch && setorMatch;
      }

      return matchesSearch && matchesType && matchesStatus && matchesOrg && matchesClientFilters;
    });
  }, [
    data,
    searchTerm,
    filterType,
    filterStatus,
    selectedOrgs,
    filterMinInteresse,
    filterMaxInteresse,
    filterPorte,
    filterSetor,
    activeTab,
  ]);

  const clientPrecadById = useMemo(() => {
    if (activeTab !== 'clientes') return {};
    const m = {};
    for (const c of data) {
      const id = c?.id_cliente;
      if (id == null) continue;
      try {
        const initial = buildInitialPrecadastroState(c, {});
        const env = loadPrecadEnvelope(id, initial, 'geral');
        const comp = calculatePreCadastroCompleteness(env.form);
        m[id] = {
          hadDraft: env.hadStoredDraft,
          status: env.form?.bloco_estr_status_precadastro || 'rascunho',
          score: comp.score,
        };
      } catch {
        m[id] = { hadDraft: false, status: 'rascunho', score: 0 };
      }
    }
    return m;
  }, [data, activeTab]);

  const clientesStats = useMemo(() => {
    if (activeTab !== 'clientes') return null;
    const total = data.length;
    const ativos = data.filter((i) => String(i.status || '').toLowerCase() === 'ativo').length;
    const withPrecad = data.filter((c) => clientPrecadById[c.id_cliente]?.hadDraft).length;
    const scores = data.map((c) => clientPrecadById[c.id_cliente]?.score ?? 0);
    const avgCompleteness = total ? Math.round(scores.reduce((a, b) => a + b, 0) / total) : 0;
    const maxInteresse = total ? Math.max(0, ...data.map((c) => Number(c.interesse_valor_max) || 0)) : 0;
    return { total, ativos, withPrecad, avgCompleteness, maxInteresse };
  }, [activeTab, data, clientPrecadById]);

  const usuariosStats = useMemo(() => {
    if (activeTab !== 'usuarios') return null;
    return {
      total: data.length,
      ativos: data.filter((u) => u.status === 'Ativo').length,
    };
  }, [activeTab, data]);

  const clearClientFilters = useCallback(() => {
    setSearchTerm('');
    setFilterStatus('');
    setFilterPorte('');
    setFilterSetor('');
    setFilterMinInteresse(0);
    setFilterMaxInteresse(100000000);
  }, []);

  const handleSave = async (formData) => {
    try {
      if (activeTab === 'usuarios') {
        if (editingItem) await dataService.updateUser(editingItem.id_usuario, formData);
        else await dataService.createUser(formData);
      } else if (activeTab === 'clientes') {
        if (editingItem) {
          if (!canEditClient(user, editingItem)) {
            alert('Você não tem permissão para editar este cliente.');
            return;
          }
          const patch = sanitizeClientWritePayload(
            user,
            mergeClientWritePayload(editingItem, formData),
          );
          await dataService.updateClient(editingItem.id_cliente, patch, { user });
        } else {
          if (!isAdminUser(user) && sessionUserId(user) == null) {
            alert('Sua sessão não tem id_usuario. Faça login novamente para cadastrar clientes.');
            return;
          }
          const payload = attachOwnerToClientPayload(user, clientPayloadFromFormState(formData));
          await dataService.createClient(payload, { user });
        }
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
      else if (activeTab === 'clientes') await dataService.deleteClient(id, { user });
      else if (activeTab === 'editais-cadastrados') await dataService.deleteEdital(id);
      loadData();
    } catch (error) {
      alert('Erro ao excluir: ' + error.message);
    }
  };

  const openPrecad = (item) => {
    if (!canViewClient(user, item)) {
      alert('Você não tem permissão para acessar este cliente.');
      return;
    }
    setPrecadCliente(item);
    setIsPrecadModalOpen(true);
  };

  const columns = useMemo(() => {
    if (activeTab === 'usuarios') {
      return [
        { key: 'id_usuario', label: 'ID' },
        { key: 'nome', label: 'Nome' },
        { key: 'nome_email', label: 'Email' },
        {
          key: 'tipo_usuario',
          label: 'Tipo',
          render: (v) => (
            <span className="cad-badge cad-badge-type">{v || '—'}</span>
          ),
        },
        { key: 'nivel_acesso', label: 'Nível' },
        {
          key: 'status',
          label: 'Status',
          render: (v) => {
            const ativo = v === 'Ativo';
            return (
              <span className={`cad-badge cad-badge-status ${ativo ? 'cad-badge-ativo' : 'cad-badge-inativo'}`}>
                {v || '—'}
              </span>
            );
          },
        },
      ];
    }
    if (activeTab === 'clientes') {
      return [
        {
          key: 'nome_empresa',
          label: 'Cliente',
          render: (_, item) => (
            <div className="cad-cell-cliente">
              <span className="cad-cell-cliente-name">{item.nome_empresa || '—'}</span>
              {(item.setor || item.cnae) && (
                <span className="cad-cell-cliente-meta">
                  {[item.setor, item.cnae].filter(Boolean).join(' · ')}
                </span>
              )}
            </div>
          ),
        },
        { key: 'cnpj', label: 'CNPJ', render: (v) => formatCnpjDisplay(v) },
        { key: 'setor', label: 'Setor', render: (v) => cellStr(v) },
        { key: 'porte_empresa', label: 'Porte', render: (v) => cellStr(v) },
        {
          key: 'status',
          label: 'Status',
          render: (v) => {
            const ativo = String(v || '').toLowerCase() === 'ativo';
            return (
              <span className={`cad-badge cad-badge-status ${ativo ? 'cad-badge-ativo' : 'cad-badge-inativo'}`}>
                {ativo ? 'Ativo' : 'Inativo'}
              </span>
            );
          },
        },
        {
          key: 'precad',
          label: 'Pré-projeto',
          render: (_, item) => {
            const info = clientPrecadById[item.id_cliente];
            const { label, cls } = precadBadgeDisplay(info);
            return <span className={`cad-badge cad-badge-precad ${cls}`}>{label}</span>;
          },
        },
      ];
    }
    if (activeTab === 'editais-cadastrados') {
      return [
        { key: 'id_edital', label: 'ID' },
        { key: 'titulo', label: 'Título' },
        { key: 'fonte_recurso', label: 'Fonte' },
        { key: 'valor_maximo', label: 'Valor Máx.', render: (v) => formatCurrency(v) },
        { key: 'prazo_envio', label: 'Prazo', render: (v) => (v ? formatDate(v) : '-') },
        { key: 'status', label: 'Status' },
      ];
    }
    return [];
  }, [activeTab, clientPrecadById, user]);

  const renderForm = () => {
    const props = { initialData: editingItem, onSave: handleSave, onCancel: () => setIsModalOpen(false) };
    if (activeTab === 'usuarios') return <UserForm {...props} />;
    if (activeTab === 'clientes') return <ClientForm {...props} />;
    if (activeTab === 'editais-cadastrados') return <EditalForm {...props} />;
    return null;
  };

  const hasClientFilters =
    activeTab === 'clientes' &&
    (searchTerm ||
      filterStatus ||
      filterPorte ||
      filterSetor ||
      filterMinInteresse > 0 ||
      filterMaxInteresse < 100000000);

  return (
    <div className="admin-body">
      <Header />
      <div className="admin-container">
        <aside className="admin-sidebar">
          <h2 className="sidebar-title">Cadastros</h2>
          <nav className="sidebar-nav">
            {permissions.canManageUsers && (
              <button
                type="button"
                className={`sidebar-link ${activeTab === 'usuarios' ? 'active' : ''}`}
                onClick={() => setActiveTab('usuarios')}
              >
                <span className="icon">👤</span> Usuários
              </button>
            )}
            {showClientesTab ? (
              <button
                type="button"
                className={`sidebar-link ${activeTab === 'clientes' ? 'active' : ''}`}
                onClick={() => setActiveTab('clientes')}
              >
                <span className="icon">🏢</span> Clientes
              </button>
            ) : null}
            <button
              type="button"
              className={`sidebar-link ${activeTab === 'editais-cadastrados' ? 'active' : ''}`}
              onClick={() => setActiveTab('editais-cadastrados')}
            >
              <span className="icon">📄</span> Editais
            </button>
          </nav>
        </aside>
        <main className="admin-main">
          <section className="admin-section active">
            {!adminCadastros && (
              <div className="cad-workspace-redirect-banner" role="status">
                <div>
                  <strong>Gestão de clientes no Workspace</strong>
                  <p className="cad-hero-sub" style={{ margin: '6px 0 0' }}>
                    A gestão de clientes e pré-projetos agora fica no Workspace do Consultor. Cadastros
                    permanece focado em administração (usuários e editais).
                  </p>
                </div>
                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => navigate('/workspace-consultor')}
                >
                  Ir para Workspace
                </button>
              </div>
            )}

            {activeTab === 'clientes' && showClientesTab && (
              <>
                <div className="cad-hero cad-hero-clientes">
                  <div className="cad-hero-text">
                    <h2 className="cad-hero-title">Clientes</h2>
                    <p className="cad-hero-sub">
                      Acesso administrativo legado. O fluxo principal de clientes e pré-projetos está no{' '}
                      <button
                        type="button"
                        className="cad-inline-link"
                        onClick={() => navigate('/workspace-consultor')}
                      >
                        Workspace do Consultor
                      </button>
                      .
                    </p>
                  </div>
                  {permissions.canCreate && (
                    <button
                      type="button"
                      className="btn-primary cad-hero-cta"
                      onClick={() => {
                        setEditingItem(null);
                        setIsModalOpen(true);
                      }}
                    >
                      + Novo cliente
                    </button>
                  )}
                </div>
                {!loading && clientesStats && (
                  <div className="cad-stat-cards" aria-label="Resumo de clientes">
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{clientesStats.total}</span>
                      <span className="cad-stat-label">Total de clientes</span>
                    </div>
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{clientesStats.ativos}</span>
                      <span className="cad-stat-label">Ativos</span>
                    </div>
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{clientesStats.withPrecad}</span>
                      <span className="cad-stat-label">Com pré-cadastro</span>
                    </div>
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{clientesStats.avgCompleteness}%</span>
                      <span className="cad-stat-label">Completude média (est.)</span>
                    </div>
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{formatCurrency(clientesStats.maxInteresse)}</span>
                      <span className="cad-stat-label">Interesse máximo configurado</span>
                    </div>
                  </div>
                )}
              </>
            )}

            {activeTab === 'usuarios' && (
              <>
                <div className="cad-hero cad-hero-users">
                  <div className="cad-hero-text">
                    <h2 className="cad-hero-title">Usuários</h2>
                    <p className="cad-hero-sub">Contas com acesso ao EditalFinder e permissões por perfil.</p>
                  </div>
                  {permissions.canManageUsers && permissions.canCreate && (
                    <button
                      type="button"
                      className="btn-primary cad-hero-cta"
                      onClick={() => {
                        setEditingItem(null);
                        setIsModalOpen(true);
                      }}
                    >
                      + Novo usuário
                    </button>
                  )}
                </div>
                {!loading && usuariosStats && (
                  <div className="cad-stat-cards cad-stat-cards-compact" aria-label="Resumo de usuários">
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{usuariosStats.total}</span>
                      <span className="cad-stat-label">Total</span>
                    </div>
                    <div className="cad-stat-card">
                      <span className="cad-stat-value">{usuariosStats.ativos}</span>
                      <span className="cad-stat-label">Ativos</span>
                    </div>
                  </div>
                )}
              </>
            )}

            {activeTab === 'editais-cadastrados' && (
              <div className="cad-hero cad-hero-editais">
                <div className="cad-hero-text">
                  <h2 className="cad-hero-title">Editais cadastrados</h2>
                  <p className="cad-hero-sub">Registros manuais ou complementares ao catálogo principal.</p>
                </div>
                {permissions.canCreate && (
                  <button
                    type="button"
                    className="btn-primary cad-hero-cta"
                    onClick={() => {
                      setEditingItem(null);
                      setIsModalOpen(true);
                    }}
                  >
                    + Novo edital
                  </button>
                )}
              </div>
            )}

            {activeTab === 'clientes' && showClientesTab ? (
              <div className="cad-filters-panel">
                <div className="cad-filters-grid">
                  <label className="cad-filter-field cad-filter-grow">
                    <span className="cad-filter-label">Buscar cliente</span>
                    <input
                      type="search"
                      placeholder="Nome ou CNPJ…"
                      className="filter-input-large"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      autoComplete="off"
                    />
                  </label>
                  <label className="cad-filter-field">
                    <span className="cad-filter-label">Status</span>
                    <select className="filter-select-small" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                      <option value="">Todos</option>
                      <option value="Ativo">Ativo</option>
                      <option value="Inativo">Inativo</option>
                    </select>
                  </label>
                  <label className="cad-filter-field">
                    <span className="cad-filter-label">Porte</span>
                    <select className="filter-select-small" value={filterPorte} onChange={(e) => setFilterPorte(e.target.value)}>
                      <option value="">Todos os portes</option>
                      <option value="MEI">MEI</option>
                      <option value="ME">ME</option>
                      <option value="EPP">EPP</option>
                      <option value="Média">Média</option>
                      <option value="Grande">Grande</option>
                    </select>
                  </label>
                  <label className="cad-filter-field">
                    <span className="cad-filter-label">Setor</span>
                    <select className="filter-select-small" value={filterSetor} onChange={(e) => setFilterSetor(e.target.value)}>
                      <option value="">Todos</option>
                      {setoresDisponiveis.map((se) => (
                        <option key={se} value={se}>
                          {se}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="cad-filters-slider-row">
                  <label className="cad-filter-field cad-filter-slider">
                    <span className="cad-filter-label">Interesse até (filtro por faixa)</span>
                    <div className="cad-range-line">
                      <span className="cad-range-value">{formatCurrency(filterMaxInteresse)}</span>
                      <input
                        type="range"
                        min="0"
                        max="50000000"
                        step="5000"
                        className="range-slider cad-range-input"
                        value={filterMaxInteresse}
                        onChange={(e) => setFilterMaxInteresse(Number(e.target.value))}
                        aria-valuetext={formatCurrency(filterMaxInteresse)}
                      />
                    </div>
                  </label>
                  <button
                    type="button"
                    className={`cad-filters-clear ${hasClientFilters ? 'is-visible' : ''}`}
                    onClick={clearClientFilters}
                    disabled={!hasClientFilters}
                  >
                    Limpar filtros
                  </button>
                </div>
              </div>
            ) : (
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
                </div>

                {activeTab === 'editais-cadastrados' && availableOrgs.length > 0 && (
                  <div className="cad-org-filters">
                    <span className="cad-org-filters-title">Filtrar por órgão financiador</span>
                    {availableOrgs.map((org) => (
                      <label key={org}>
                        <input
                          type="checkbox"
                          checked={selectedOrgs.includes(org)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedOrgs([...selectedOrgs, org]);
                            } else {
                              setSelectedOrgs(selectedOrgs.filter((o) => o !== org));
                            }
                          }}
                        />
                        {org}
                      </label>
                    ))}
                    {selectedOrgs.length > 0 && (
                      <button type="button" className="cad-org-filters-clear" onClick={() => setSelectedOrgs([])}>
                        Limpar filtros
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}

            {loading ? (
              <div className="cad-loading-placeholder">
                <h3>Carregando dados...</h3>
              </div>
            ) : (
              <AdminTable
                columns={columns}
                data={filteredData}
                wrapClassName={activeTab === 'usuarios' ? 'cad-table-users' : undefined}
                rowIdKey={
                  activeTab === 'usuarios'
                    ? 'id_usuario'
                    : activeTab === 'clientes'
                      ? 'id_cliente'
                      : 'id_edital'
                }
                onEdit={(item) => {
                  if (activeTab === 'clientes' && !canEditClient(user, item)) {
                    alert('Você não tem permissão para editar este cliente.');
                    return;
                  }
                  setEditingItem(item);
                  setIsModalOpen(true);
                }}
                onDelete={handleDelete}
                extraRowActions={
                  activeTab === 'clientes' && (permissions.canEdit || permissions.canCreate)
                    ? (item, { onEdit, onDelete, idKey }) => (
                        <div className="cad-client-actions">
                          {(permissions.canEdit || permissions.canCreate) && canViewClient(user, item) && (
                            <button type="button" className="cad-btn-precad-primary" onClick={() => openPrecad(item)}>
                              Abrir pré-cadastro
                            </button>
                          )}
                          <div className="cad-client-actions-row">
                            {permissions.canEdit && canEditClient(user, item) && (
                              <button type="button" className="cad-btn-text" onClick={() => onEdit(item)}>
                                Editar
                              </button>
                            )}
                            {permissions.canDelete && canEditClient(user, item) && (
                              <button type="button" className="cad-btn-text cad-btn-text-danger" onClick={() => onDelete(item[idKey])}>
                                Excluir
                              </button>
                            )}
                          </div>
                        </div>
                      )
                    : undefined
                }
              />
            )}
          </section>
        </main>
      </div>
      {isModalOpen && (
        <Modal
          onClose={() => setIsModalOpen(false)}
          className={
            activeTab === 'clientes'
              ? 'modal-large modal-client-form'
              : activeTab === 'editais-cadastrados'
                ? 'modal-large'
                : ''
          }
        >
          <div className="modal-header">
            <h2>
              {editingItem ? 'Editar' : 'Cadastrar'}{' '}
              {activeTab === 'usuarios' ? 'Usuário' : activeTab === 'clientes' ? 'Cliente' : 'Edital'}
            </h2>
          </div>
          {renderForm()}
        </Modal>
      )}
      {isPrecadModalOpen && precadCliente && (
        <Modal
          onClose={() => {
            setIsPrecadModalOpen(false);
            setPrecadCliente(null);
          }}
          className="modal-large modal-precad"
          hideCloseButton
        >
          <ProjetoPrecadastroForm
            key={precadCliente.id_cliente}
            cliente={precadCliente}
            editalAssociado={precadContext.editalAssociado}
            radarMatch={precadContext.radarMatch}
            onCancel={() => {
              setIsPrecadModalOpen(false);
              setPrecadCliente(null);
            }}
          />
        </Modal>
      )}
    </div>
  );
}
