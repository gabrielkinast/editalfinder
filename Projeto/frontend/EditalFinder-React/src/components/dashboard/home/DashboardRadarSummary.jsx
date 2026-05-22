import { Link } from 'react-router-dom';
import { ENABLE_CONSULTOR_WORKSPACE } from '../../../config/env';
import DashboardEmptyState from './DashboardEmptyState';

export default function DashboardRadarSummary({
  radarSummary = { total: 0, withBriefing: 0, withProfile: 0 },
  loading,
  canViewCadastros,
}) {
  const { total, withBriefing, withProfile } = radarSummary;
  const hasClients = total > 0;

  return (
    <section className="home-dash-panel home-dash-radar-summary">
      <h3 className="home-dash-panel-title">Radar de Fomento</h3>
      {loading ? (
        <p className="home-dash-muted">Carregando resumo…</p>
      ) : !hasClients && canViewCadastros ? (
        <DashboardEmptyState
          title="Cadastre um cliente para usar o Radar de Fomento."
          message="O Radar cruza editais com o perfil consultivo de cada cliente."
          action={
            <Link to="/cadastros" className="home-dash-btn home-dash-btn--primary">
              Ir para Cadastros
            </Link>
          }
        />
      ) : (
        <>
          <p className="home-dash-radar-lead">
            {hasClients
              ? `${total.toLocaleString('pt-BR')} cliente${total === 1 ? '' : 's'} cadastrado${total === 1 ? '' : 's'}. Use o Radar para comparar oportunidades abertas com perfis consultivos.`
              : 'Compare oportunidades abertas com perfis de clientes na área Radar.'}
          </p>
          {hasClients && (
            <div className="home-dash-radar-stats">
              <div className="home-dash-radar-stat">
                <span className="home-dash-radar-stat-value">{total}</span>
                <span className="home-dash-radar-stat-label">Clientes cadastrados</span>
              </div>
              <div className="home-dash-radar-stat">
                <span className="home-dash-radar-stat-value">{withBriefing}</span>
                <span className="home-dash-radar-stat-label">Com briefing salvo</span>
              </div>
              <div className="home-dash-radar-stat">
                <span className="home-dash-radar-stat-value">{withProfile}</span>
                <span className="home-dash-radar-stat-label">Com perfil preenchido</span>
              </div>
            </div>
          )}
          <div className="home-dash-radar-actions">
            <Link to="/radar-fomento" className="home-dash-btn home-dash-btn--primary">
              Abrir Radar de Fomento
            </Link>
            {ENABLE_CONSULTOR_WORKSPACE && canViewCadastros && (
              <Link to="/workspace-consultor" className="home-dash-btn home-dash-btn--ghost">
                Workspace do Consultor
              </Link>
            )}
          </div>
          {hasClients && (
            <p className="home-dash-muted home-dash-radar-foot">
              Resumo agregado — abra o Radar para ver clientes e oportunidades em detalhe.
            </p>
          )}
        </>
      )}
    </section>
  );
}
