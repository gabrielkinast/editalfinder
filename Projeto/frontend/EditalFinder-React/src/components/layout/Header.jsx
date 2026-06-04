import { NavLink, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { usePermissions } from '../../hooks/usePermissions';
import { useSettings } from '../../contexts/SettingsContext';
import { ENABLE_CONSULTOR_WORKSPACE } from '../../config/env';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';
import { logConsultorWorkspaceAvailabilityCheck } from '../../utils/consultorWorkspaceAvailability';
import Modal from '../ui/Modal';
import SettingsForm from '../admin/SettingsForm';
import AppReportProblemButton from '../feedback/AppReportProblemButton';
import AppNavigationMenu from './AppNavigationMenu';
import AppHelpButton from '../help/AppHelpButton';

export default function Header({ onSearch, searchPlaceholder = 'Buscar editais...' }) {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const permissions = usePermissions();
  const { settings } = useSettings();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const workspaceMenuVisible =
    ENABLE_CONSULTOR_WORKSPACE && Boolean(permissions.canViewCadastros);

  useEffect(() => {
    logConsultorWorkspaceAvailabilityCheck({
      canViewCadastros: permissions.canViewCadastros,
      userRole: user?.tipo ?? user?.tipo_usuario ?? null,
      menuVisible: workspaceMenuVisible,
    });
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
    <header className="header app-header">
      <div className="header-content header-content--toolbar">
        <div className="header-left">
          <AppNavigationMenu onOpenSettings={() => setIsSettingsOpen(true)} />
          <NavLink to="/dashboard" className="logo-header logo-header-link" title="Ir para o Dashboard">
            {settings.logoImage ? (
              <img src={settings.logoImage} alt="Logo" className="logo-header-img" />
            ) : (
              <span>{settings.logoText || 'EditalFinder'}</span>
            )}
          </NavLink>
        </div>

        {onSearch && (
          <div className="header-center">
            <input
              type="search"
              id="globalSearch"
              placeholder={searchPlaceholder}
              className="search-input-header"
              onChange={(e) => onSearch(e.target.value)}
              aria-label={searchPlaceholder}
            />
          </div>
        )}

        <div className="header-actions header-right">
          <AppHelpButton variant="icon" />
          <AppHelpButton variant="header" />
          <AppReportProblemButton
            origem="user_report"
            tipo="outro"
            label="Reportar problema"
            variant="link"
            className="header-report-problem"
          />
          {permissions.canManageUsers && (
            <button
              type="button"
              onClick={() => setIsSettingsOpen(true)}
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
