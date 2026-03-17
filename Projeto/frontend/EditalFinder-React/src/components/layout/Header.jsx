import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { authService } from '../../services/authService';
import { useSettings } from '../../contexts/SettingsContext';
import Modal from '../ui/Modal';
import SettingsForm from '../admin/SettingsForm';

export default function Header({ onSearch }) {
  const navigate = useNavigate();
  const { settings } = useSettings();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-header" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {settings.logoImage ? (
            <img src={settings.logoImage} alt="Logo" style={{ maxHeight: '45px' }} />
          ) : (
            <span>{settings.logoText}</span>
          )}
        </div>
        <nav className="main-nav">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>Editais</NavLink>
          <NavLink to="/cadastros" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>Cadastros</NavLink>
        </nav>
        <div className="header-right">
          {onSearch && (
            <input
              type="text"
              id="globalSearch"
              placeholder="Buscar editais..."
              className="search-input-header"
              onChange={(e) => onSearch(e.target.value)}
            />
          )}
          <button 
            onClick={() => setIsSettingsOpen(true)} 
            className="btn-logout" 
            style={{ borderColor: 'var(--primary-blue)', color: 'var(--primary-blue)' }}
          >
            ⚙️ Configurações
          </button>
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

