import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { usePermissions } from '../../hooks/usePermissions';
import { useAppFeedback } from '../../contexts/AppFeedbackContext';
import {
  buildAppNavigationSections,
  isNavItemActive,
} from './appNavigationConfig';
import AppHelpButton from '../help/AppHelpButton';
import { APP_VERSION_LABEL } from '../../config/appVersion';

function HamburgerIcon() {
  return (
    <span className="app-nav-toggle-icon" aria-hidden="true">
      <span />
      <span />
      <span />
    </span>
  );
}

/**
 * Menu principal (hambúrguer + drawer) — substitui abas horizontais no header.
 * @param {object} props
 * @param {() => void} [props.onOpenSettings]
 */
export default function AppNavigationMenu({ onOpenSettings }) {
  const [open, setOpen] = useState(false);
  const toggleRef = useRef(null);
  const panelRef = useRef(null);
  const drawerId = useId();
  const location = useLocation();
  const permissions = usePermissions();
  const { openAppFeedbackModal } = useAppFeedback();

  const sections = buildAppNavigationSections(permissions);

  const close = useCallback(() => setOpen(false), []);

  const openMenu = useCallback(() => setOpen(true), []);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === 'Escape') close();
    };
    document.addEventListener('keydown', onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const t = window.setTimeout(() => {
      const first = panelRef.current?.querySelector('a, button');
      first?.focus();
    }, 0);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prevOverflow;
      window.clearTimeout(t);
    };
  }, [open, close]);

  useEffect(() => {
    close();
  }, [location.pathname, close]);

  useEffect(() => {
    if (!open) return undefined;
    const onPointer = (e) => {
      const panel = panelRef.current;
      const toggle = toggleRef.current;
      if (!panel || !toggle) return;
      if (panel.contains(e.target) || toggle.contains(e.target)) return;
      close();
    };
    document.addEventListener('mousedown', onPointer);
    return () => document.removeEventListener('mousedown', onPointer);
  }, [open, close]);

  const handleCloseAndFocusToggle = () => {
    close();
    window.requestAnimationFrame(() => toggleRef.current?.focus());
  };

  const handleReport = () => {
    openAppFeedbackModal({
      origem: 'user_report',
      pagina: 'Menu de navegação',
      componente: 'AppNavigationMenu',
      acao: 'reportar_problema_menu',
      tipo: 'outro',
    });
    handleCloseAndFocusToggle();
  };

  const handleSettings = () => {
    onOpenSettings?.();
    handleCloseAndFocusToggle();
  };

  return (
    <>
      <button
        ref={toggleRef}
        type="button"
        className="app-nav-toggle"
        aria-label={open ? 'Fechar menu de navegação' : 'Abrir menu de navegação'}
        aria-expanded={open}
        aria-controls={drawerId}
        onClick={() => (open ? handleCloseAndFocusToggle() : openMenu())}
      >
        <HamburgerIcon />
      </button>

      {open && (
        <>
          <div
            className="app-nav-overlay"
            role="presentation"
            aria-hidden="true"
            onClick={handleCloseAndFocusToggle}
          />

          <aside
            ref={panelRef}
            id={drawerId}
            className="app-nav-drawer app-nav-drawer--open"
            role="dialog"
            aria-modal="true"
            aria-label="Menu de navegação"
          >
        <div className="app-nav-drawer-header">
          <span className="app-nav-drawer-title">Navegação</span>
          <button
            type="button"
            className="app-nav-drawer-close"
            aria-label="Fechar menu"
            onClick={handleCloseAndFocusToggle}
          >
            ×
          </button>
        </div>

        <nav className="app-nav-drawer-nav" role="navigation" aria-label="Principal">
          {sections.map((section) => (
            <div key={section.id} className="app-nav-group">
              <p className="app-nav-group-label">{section.label}</p>
              <ul className="app-nav-list" role="menu">
                {section.items.map((item) => {
                  const active = isNavItemActive(location.pathname, item);
                  return (
                    <li key={item.id} role="none">
                      <NavLink
                        to={item.to}
                        end={item.end}
                        role="menuitem"
                        className={`app-nav-link ${active ? 'app-nav-link--active' : ''}`}
                        onClick={handleCloseAndFocusToggle}
                      >
                        {item.label}
                      </NavLink>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}

          <div className="app-nav-group app-nav-group--system">
            <p className="app-nav-group-label">Sistema</p>
            <ul className="app-nav-list" role="menu">
              <li role="none">
                <AppHelpButton variant="menu" />
              </li>
              {permissions.canManageUsers && (
                <li role="none">
                  <button
                    type="button"
                    role="menuitem"
                    className="app-nav-link app-nav-link--button"
                    onClick={handleSettings}
                  >
                    Configurações
                  </button>
                </li>
              )}
              <li role="none">
                <button
                  type="button"
                  role="menuitem"
                  className="app-nav-link app-nav-link--button"
                  onClick={handleReport}
                >
                  Reportar problema
                </button>
              </li>
            </ul>
          </div>
          <p className="app-nav-version" aria-label="Versão do aplicativo">
            {APP_VERSION_LABEL}
          </p>
        </nav>
          </aside>
        </>
      )}
    </>
  );
}
