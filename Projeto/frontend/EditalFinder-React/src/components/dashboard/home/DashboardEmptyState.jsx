export default function DashboardEmptyState({ title, message, action }) {
  return (
    <div className="home-dash-empty">
      <p className="home-dash-empty-title">{title}</p>
      {message && <p className="home-dash-empty-msg">{message}</p>}
      {action && <div className="home-dash-empty-action">{action}</div>}
    </div>
  );
}
