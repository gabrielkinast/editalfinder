import Header from '../components/layout/Header';
import { usePermissions } from '../hooks/usePermissions';
import { useDashboardData } from '../hooks/useDashboardData';
import DashboardMetricCard from '../components/dashboard/home/DashboardMetricCard';
import DashboardPriorityPanel from '../components/dashboard/home/DashboardPriorityPanel';
import DashboardQuickActions from '../components/dashboard/home/DashboardQuickActions';
import DashboardRecentEditais from '../components/dashboard/home/DashboardRecentEditais';
import DashboardExpiringEditais from '../components/dashboard/home/DashboardExpiringEditais';
import DashboardRecentContent from '../components/dashboard/home/DashboardRecentContent';
import DashboardChartCard from '../components/dashboard/home/DashboardChartCard';
import DashboardRadarSummary from '../components/dashboard/home/DashboardRadarSummary';
import DashboardScopeFilter from '../components/dashboard/home/DashboardScopeFilter';
import DashboardDataQualityPanel from '../components/dashboard/home/DashboardDataQualityPanel';
import EmptyOrErrorState from '../components/common/EmptyOrErrorState';
import AppReportProblemButton from '../components/feedback/AppReportProblemButton';
import HelpPageLink from '../components/help/HelpPageLink';
import {
  buildDashboardCountContexts,
  DASHBOARD_COUNT_HELP_TEXT,
} from '../utils/dashboard/dashboardCountSemantics';
import '../styles/dashboard.css';

function formatUpdatedAt(date) {
  if (!date) return 'Atualizado agora';
  try {
    return `Atualizado ${date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })}`;
  } catch {
    return 'Atualizado agora';
  }
}

export default function Dashboard() {
  const permissions = usePermissions();
  const data = useDashboardData();

  const {
    loading,
    error,
    errors,
    metrics,
    priorities,
    recentEditais,
    expiringEditais,
    recentNoticias,
    recentPesquisas,
    charts,
    radarSummary,
    lastUpdated,
    refresh,
    truncatedEditais,
    scopeFilter,
    setScopeFilter,
    dataQualityAudit,
  } = data;

  const ctx = buildDashboardCountContexts(metrics, { truncated: truncatedEditais });

  return (
    <>
      <Header searchPlaceholder="Buscar editais…" />
      <div className="page-wrapper home-dashboard-page" data-testid="dashboard-page">
        <header className="home-dash-header home-dash-header--executive">
          <div className="home-dash-header-text">
            <p className="home-dash-eyebrow">Central executiva</p>
            <h1 className="home-dash-title">Dashboard</h1>
            <p className="home-dash-subtitle">Resumo recente do EditalFinder</p>
            <HelpPageLink sectionId="dashboard" label="Como usar o Dashboard?" />
            <p className="home-dash-updated">{formatUpdatedAt(lastUpdated)}</p>
          </div>
          <div className="home-dash-header-actions">
            <button
              type="button"
              className="home-dash-btn home-dash-btn--primary"
              onClick={refresh}
              disabled={loading}
              data-testid="dashboard-refresh-button"
            >
              {loading ? 'Atualizando…' : 'Atualizar dados'}
            </button>
            <AppReportProblemButton
              origem="dashboard"
              pagina="Dashboard"
              componente="Dashboard"
              acao="reportar_problema_header"
              label="Reportar problema"
              variant="link"
              className="home-dash-report-link"
            />
          </div>
        </header>

        {error && !loading ? (
          <EmptyOrErrorState
            title="Não foi possível carregar o resumo de editais."
            message={error?.message || 'Verifique a conexão ou tente novamente.'}
            origem="dashboard"
            pagina="Dashboard"
            acao="load_editais"
            componente="Dashboard"
            error={error}
            onRetry={refresh}
          />
        ) : (
          <div className="home-dash-flow">
            <section className="home-dash-metrics home-dash-block" aria-label="Métricas">
              <DashboardMetricCard
                label={ctx.monitoredLabel}
                value={metrics.totalEditais.toLocaleString('pt-BR')}
                context={ctx.monitored}
                loading={loading}
                accent
              />
              <DashboardMetricCard
                label="Oportunidades ativas/prováveis"
                value={(metrics.oportunidadesProvavelmenteAbertas ?? metrics.openEditais).toLocaleString(
                  'pt-BR',
                )}
                context={ctx.open}
                loading={loading}
              />
              <DashboardMetricCard
                label="Vencendo em 7 dias"
                value={metrics.expiringSoon.toLocaleString('pt-BR')}
                context={ctx.expiring}
                loading={loading}
                accent={metrics.expiringSoon > 0}
              />
              <DashboardMetricCard
                label="Notícias recentes"
                value={metrics.totalNoticiasRecentes.toLocaleString('pt-BR')}
                context={ctx.noticias}
                loading={loading}
              />
              <DashboardMetricCard
                label="Pesquisas recentes"
                value={metrics.totalPesquisasRecentes.toLocaleString('pt-BR')}
                context={ctx.pesquisas}
                loading={loading}
              />
              <DashboardMetricCard
                label="Relatos pendentes"
                value={metrics.reportedProblemsPending.toLocaleString('pt-BR')}
                context={ctx.reports}
                loading={loading}
              />
            </section>

            <p className="home-dash-metrics-note" role="note">
              {DASHBOARD_COUNT_HELP_TEXT}
            </p>

            <div className="home-dash-block">
              <DashboardPriorityPanel priorities={priorities} loading={loading} />
            </div>

            <div className="home-dash-block">
              <DashboardQuickActions permissions={permissions} />
            </div>

            <div className="home-dash-block home-dash-scope-block">
              <DashboardScopeFilter
                value={scopeFilter}
                onChange={setScopeFilter}
                disabled={loading}
              />
            </div>

            <section className="home-dash-charts-grid home-dash-block" aria-label="Gráficos">
              <DashboardChartCard
                title="Editais por fonte"
                subtitle={charts.fonteChartSubtitle}
                data={charts.editaisByFonte}
                totalAnalyzed={charts.totalAnalyzed}
                emptyMessage="Sem editais para agrupar por fonte."
                showScopeBadges
              />
              <DashboardChartCard
                title={charts.tipoChartTitle || 'Editais por modalidade'}
                subtitle={charts.tipoChartSubtitle}
                data={charts.editaisByTipo}
                totalAnalyzed={charts.totalAnalyzed}
                emptyMessage="Sem editais para classificar por modalidade."
              />
              <DashboardChartCard
                title="Situação de prazos"
                data={charts.editaisByPrazo}
                totalAnalyzed={charts.totalAnalyzed}
                emptyMessage="Sem dados de prazo."
                dataQualityWarning={charts.prazoDataQualityWarning}
              />
            </section>

            <section className="home-dash-two-col home-dash-block">
              <DashboardRecentEditais items={recentEditais} loading={loading && !recentEditais.length} />
              <DashboardExpiringEditais
                items={expiringEditais}
                loading={loading && !expiringEditais.length}
                scopeFilter={scopeFilter}
              />
            </section>

            <section className="home-dash-two-col home-dash-block">
              <DashboardRecentContent
                title="Notícias recentes"
                items={recentNoticias}
                loading={loading && !recentNoticias.length}
                error={errors.noticias}
                moreLink="/noticias"
                pagina="Dashboard"
                sectionKey="noticias"
                onRetry={refresh}
                emptyTitle="Nenhuma notícia recente cadastrada."
              />
              <DashboardRecentContent
                title="Pesquisas recentes"
                items={recentPesquisas}
                loading={loading && !recentPesquisas.length}
                error={errors.pesquisas}
                moreLink="/pesquisas"
                pagina="Dashboard"
                sectionKey="pesquisas"
                onRetry={refresh}
                emptyTitle="Nenhuma pesquisa recente cadastrada."
              />
            </section>

            <div className="home-dash-block">
              <DashboardRadarSummary
                radarSummary={radarSummary}
                loading={loading && permissions.canViewCadastros}
                canViewCadastros={permissions.canViewCadastros}
              />
            </div>

            <DashboardDataQualityPanel audit={dataQualityAudit} metrics={metrics} />
          </div>
        )}
      </div>
    </>
  );
}
