import { NavLink, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { usePermissions } from '../../hooks/usePermissions';
import { useSettings } from '../../contexts/SettingsContext';
import { ENABLE_CONCURSOS, ENABLE_CONSULTOR_WORKSPACE } from '../../config/env';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';
import Modal from '../ui/Modal';
import SettingsForm from '../admin/SettingsForm';

export default function Header({ onSearch, searchPlaceholder = 'Buscar editais...' }) {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const permissions = usePermissions();
  const { settings } = useSettings();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const workspaceMenuVisible =
    ENABLE_CONSULTOR_WORKSPACE && Boolean(permissions.canViewCadastros);

  useEffect(() => {
    logConsultorWorkspace('menu_gate', {
      ENABLE_CONSULTOR_WORKSPACE,
      canViewCadastros: permissions.canViewCadastros,
      userRole: user?.tipo ?? user?.tipo_usuario ?? null,
      menuVisible: workspaceMenuVisible,
    });
  }, [
    permissions.canViewCadastros,
    user?.tipo,
    user?.tipo_usuario,
    workspaceMenuVisible,
  ]);

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo-header">
            {settings.logoImage ? (
              <img src={settings.logoImage} alt="Logo" className="logo-header-img" />
            ) : (
              <span>{settings.logoText}</span>
            )}
          </div>
          <button
            type="button"
            className="menu-toggle-mobile"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-expanded={isMenuOpen}
            aria-controls="main-nav"
          >
            {isMenuOpen ? 'Fechar' : 'Menu'}
          </button>
        </div>

        <nav id="main-nav" className={`main-nav header-nav ${isMenuOpen ? 'open' : ''}`}>
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Editais
          </NavLink>
          {permissions.canViewCadastros && (
            <NavLink
              to="/cadastros"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Cadastros
            </NavLink>
          )}
          {ENABLE_CONSULTOR_WORKSPACE && permissions.canViewCadastros && (
            <NavLink
              to="/workspace-consultor"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Workspace
            </NavLink>
          )}
          <NavLink
            to="/radar-fomento"
            title="Radar de Fomento"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Radar
          </NavLink>
          {import.meta.env.VITE_ENABLE_INDICE === 'true' && (
            <NavLink
              to="/indice"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Índice
            </NavLink>
          )}
          <NavLink
            to="/noticias"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Notícias
          </NavLink>
          <NavLink
            to="/pesquisas"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Pesquisas
          </NavLink>
          <NavLink
            to="/portais-estrategicos"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Portais
          </NavLink>
          {ENABLE_CONCURSOS && (
            <NavLink
              to="/concursos"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Concursos
            </NavLink>
          )}
        </nav>

        <div className={`header-actions header-right ${isMenuOpen ? 'open' : ''}`}>
          {onSearch && (
            <input
              type="text"
              id="globalSearch"
              placeholder={searchPlaceholder}
              className="search-input-header"
              onChange={(e) => onSearch(e.target.value)}
            />
          )}
          {permissions.canManageUsers && (
            <button
              type="button"
              onClick={() => {
                setIsSettingsOpen(true);
                setIsMenuOpen(false);
              }}
              className="btn-logout btn-header-settings"
            >
              Configurações
            </button>
          )}
          <button type="button" onClick={handleLogout} className="btn-logout">
            Sair
          </button>
        </div>
      </div>

      {isSettingsOpen && (
        <Modal onClose={() => setIsSettingsOpen(false)}>
          <div className="modal-header">
            <h2>Configurações do Sistema</h2>
          </div>
          <SettingsForm onCancel={() => setIsSettingsOpen(false)} />
        </Modal>
      )}
    </header>
  );
}
