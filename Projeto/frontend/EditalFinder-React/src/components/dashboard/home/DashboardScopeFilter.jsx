import { DASHBOARD_SCOPE_OPTIONS } from '../../../utils/dashboard/dashboardClassification';

export default function DashboardScopeFilter({ value, onChange, disabled }) {
  return (
    <div className="home-dash-scope-filter" role="group" aria-label="Escopo do dashboard">
      <span className="home-dash-scope-filter-label">Escopo</span>
      <div className="home-dash-scope-filter-options">
        {DASHBOARD_SCOPE_OPTIONS.map((opt) => (
          <button
            key={opt.id}
            type="button"
            className={`home-dash-scope-chip ${value === opt.id ? 'home-dash-scope-chip--active' : ''}`}
            onClick={() => onChange(opt.id)}
            disabled={disabled}
            aria-pressed={value === opt.id}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
