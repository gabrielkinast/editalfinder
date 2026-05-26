import { Link } from 'react-router-dom';
import { useAppFeedback } from '../../../contexts/AppFeedbackContext';
import {
  ENABLE_CONCURSOS,
  ENABLE_CONSULTOR_WORKSPACE,
} from '../../../config/env';

function ActionGroup({ title, children }) {
  return (
    <div className="home-dash-quick-group">
      <p className="home-dash-quick-group-label">{title}</p>
      <div className="home-dash-quick-group-links">{children}</div>
    </div>
  );
}

function QuickLink({ to, children }) {
  return (
    <Link to={to} className="home-dash-quick-chip">
      {children}
    </Link>
  );
}

/**
 * @param {object} props
 * @param {object} props.permissions
 */
export default function DashboardQuickActions({ permissions = {} }) {
  const { openAppFeedbackModal } = useAppFeedback();

  return (
    <section className="home-dash-panel home-dash-quick-actions">
      <h3 className="home-dash-panel-title">Atalhos rápidos</h3>
      <div className="home-dash-quick-groups">
        <ActionGroup title="Operação">
          <QuickLink to="/editais">Ver editais</QuickLink>
          <QuickLink to="/radar-fomento">Abrir Radar</QuickLink>
          {permissions.canViewCadastros && <QuickLink to="/cadastros">Cadastros</QuickLink>}
        </ActionGroup>

        {ENABLE_CONSULTOR_WORKSPACE && permissions.canViewCadastros ? (
          <ActionGroup title="Workspaces">
            <QuickLink to="/workspace-consultor">Workspace do Consultor</QuickLink>
          </ActionGroup>
        ) : null}

        <ActionGroup title="Conteúdo">
          <QuickLink to="/noticias">Notícias</QuickLink>
          <QuickLink to="/pesquisas">Pesquisas</QuickLink>
          {ENABLE_CONCURSOS && <QuickLink to="/concursos">Concursos</QuickLink>}
        </ActionGroup>

        <ActionGroup title="Sistema">
          <button
            type="button"
            className="home-dash-quick-chip home-dash-quick-chip--outline"
            onClick={() =>
              openAppFeedbackModal({
                origem: 'dashboard',
                pagina: 'Dashboard',
                componente: 'DashboardQuickActions',
                acao: 'reportar_problema_atalho',
                tipo: 'outro',
              })
            }
          >
            Reportar problema
          </button>
        </ActionGroup>
      </div>
    </section>
  );
}
