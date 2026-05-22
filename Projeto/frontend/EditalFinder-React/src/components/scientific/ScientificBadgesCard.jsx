import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';

export default function ScientificBadgesCard({ compact = false }) {
  const { badges } = useScientificWorkspace();
  if (!badges?.length) return null;

  const unlocked = badges.filter((b) => b.unlocked);
  const locked = badges.filter((b) => !b.unlocked);

  return (
    <section className={`scientific-badges-card ${compact ? 'scientific-badges-card--compact' : ''}`}>
      <h3 className="scientific-badges-title">Conquistas</h3>
      <p className="scientific-muted">
        {unlocked.length} de {badges.length} desbloqueadas
      </p>
      <ul className="scientific-badges-list">
        {unlocked.map((b) => (
          <li key={b.id} className="scientific-badge scientific-badge--unlocked" title={b.description}>
            <span className="scientific-badge-icon">{b.icon}</span>
            <span className="scientific-badge-label">{b.label}</span>
          </li>
        ))}
        {!compact &&
          locked.slice(0, 4).map((b) => (
            <li key={b.id} className="scientific-badge scientific-badge--locked" title={b.description}>
              <span className="scientific-badge-icon">🔒</span>
              <span className="scientific-badge-label">{b.label}</span>
            </li>
          ))}
      </ul>
    </section>
  );
}
