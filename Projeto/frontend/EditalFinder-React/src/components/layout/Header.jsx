import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { usePermissions } from '../../hooks/usePermissions';
import { useSettings } from '../../contexts/SettingsContext';
import Modal from '../ui/Modal';
import SettingsForm from '../admin/SettingsForm';

export default function Header({ onSearch }) {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const permissions = usePermissions();
  const { settings } = useSettings();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-top-mobile">
          <div className="logo-header" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {settings.logoImage ? (
              <img src={settings.logoImage} alt="Logo" style={{ maxHeight: '70px', width: 'auto' }} />
            ) : (
              <span>{settings.logoText}</span>
            )}
          </div>
          
          <button 
            className="menu-toggle-mobile" 
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Menu"
          >
            {isMenuOpen ? '✕' : '☰'}
          </button>
        </div>

        <nav className={`main-nav ${isMenuOpen ? 'open' : ''}`}>
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Editais
          </NavLink>
          {/* Permissão para acessar a página de cadastros */}
          {permissions.canViewCadastros && (
            <NavLink 
              to="/cadastros" 
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Cadastros
            </NavLink>
          )}
          <NavLink
            to="/radar-fomento"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            🎯 Radar de Fomento
          </NavLink>
          <NavLink
            to="/indice"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            📊 Índice
          </NavLink>
        </nav>

        <div className={`header-right ${isMenuOpen ? 'open' : ''}`}>
          {onSearch && (
            <input
              type="text"
              id="globalSearch"
              placeholder="Buscar editais..."
              className="search-input-header"
              onChange={(e) => onSearch(e.target.value)}
            />
          )}
          {permissions.canManageUsers && (
            <button 
              onClick={() => {
                setIsSettingsOpen(true);
                setIsMenuOpen(false);
              }} 
              className="btn-logout" 
              style={{ borderColor: 'var(--primary-blue)', color: 'var(--primary-blue)' }}
            >
              ⚙️ Configurações
            </button>
          )}
          <button onClick={handleLogout} className="btn-logout">Sair</button>
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

