export default function DashboardMetricCard({
  label,
  value,
  context,
  hint,
  loading,
  accent = false,
}) {
  return (
    <div className={`home-dash-metric-card ${accent ? 'home-dash-metric-card--accent' : ''}`}>
      <span className="home-dash-metric-label">{label}</span>
      <span className="home-dash-metric-value">{loading ? '—' : value}</span>
      {context && <span className="home-dash-metric-context">{context}</span>}
      {hint && !context && <span className="home-dash-metric-hint">{hint}</span>}
    </div>
  );
}
