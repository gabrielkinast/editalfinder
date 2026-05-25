const CHART_SUBTITLES = {
  'Editais por fonte': 'Top fontes da base atual (badge = escopo estimado)',
  'Editais por modalidade': 'Classificação estimada a partir dos campos disponíveis.',
  'Editais por classificação estimada':
    'Classificação estimada a partir dos campos disponíveis.',
  'Situação de prazos': 'Distribuição por urgência e qualidade do campo de prazo',
};

export default function DashboardChartCard({
  title,
  subtitle,
  data = [],
  totalAnalyzed = 0,
  emptyMessage = 'Sem dados para exibir.',
  dataQualityWarning = null,
  showScopeBadges = false,
}) {
  const sub = subtitle || CHART_SUBTITLES[title] || '';
  const max = Math.max(1, ...data.map((d) => d.value || 0));
  const total = data.reduce((n, d) => n + (d.value || 0), 0);

  return (
    <div className="home-dash-panel home-dash-chart-card">
      <div className="home-dash-chart-head">
        <h3 className="home-dash-panel-title">{title}</h3>
        {sub && <p className="home-dash-chart-sub">{sub}</p>}
        {totalAnalyzed > 0 && (
          <p className="home-dash-chart-meta">
            {totalAnalyzed.toLocaleString('pt-BR')} editais analisados · top {data.length}{' '}
            {total > 0 ? `(${total.toLocaleString('pt-BR')} neste gráfico)` : ''}
          </p>
        )}
        {dataQualityWarning && (
          <p className="home-dash-chart-warning" role="status">
            {dataQualityWarning}
          </p>
        )}
      </div>
      {!data.length ? (
        <p className="home-dash-muted">{emptyMessage}</p>
      ) : (
        <ul className="home-dash-bar-chart" aria-label={title}>
          {data.map((row) => (
            <li
              key={`${row.label}-${row.scope || ''}-${row.value}`}
              className="home-dash-bar-row"
            >
              <span className="home-dash-bar-label-wrap">
                <span className="home-dash-bar-label" title={row.fullLabel || row.label}>
                  {row.label}
                </span>
                {showScopeBadges && row.scopeLabel && (
                  <span
                    className={`home-dash-badge home-dash-badge--scope home-dash-badge--scope-${row.scope || 'unknown'}`}
                  >
                    {row.scopeLabel}
                  </span>
                )}
              </span>
              <div className="home-dash-bar-track" aria-hidden="true">
                <div
                  className="home-dash-bar-fill"
                  style={{ width: `${Math.round((row.value / max) * 100)}%` }}
                />
              </div>
              <span className="home-dash-bar-value">{row.value.toLocaleString('pt-BR')}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
