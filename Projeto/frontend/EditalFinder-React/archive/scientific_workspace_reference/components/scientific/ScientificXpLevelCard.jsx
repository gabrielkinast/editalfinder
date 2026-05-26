import { useState } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import ScientificXpHistoryModal from './ScientificXpHistoryModal';

export default function ScientificXpLevelCard({ compact = false }) {
  const { levelSummary, xpState } = useScientificWorkspace();
  const [historyOpen, setHistoryOpen] = useState(false);

  if (!levelSummary?.global) return null;

  const g = levelSummary.global;

  return (
    <section
      className={`scientific-xp-card ${compact ? 'scientific-xp-card--compact' : ''}`}
      aria-labelledby="scientific-xp-title"
    >
      <div className="scientific-xp-card-head">
        <h3 id="scientific-xp-title" className="scientific-xp-card-title">
          Nível {g.level} — {g.label}
        </h3>
        <span className="scientific-xp-total">{g.totalXp} XP</span>
      </div>

      <div
        className="scientific-trail-progress-bar-track"
        role="progressbar"
        aria-valuenow={g.percentToNext}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="scientific-trail-progress-bar-fill scientific-xp-bar-fill"
          style={{ width: `${g.percentToNext}%` }}
        />
      </div>
      {g.xpToNext > 0 ? (
        <p className="scientific-muted scientific-xp-next">
          Próximo nível: {g.xpToNext} XP restantes
        </p>
      ) : (
        <p className="scientific-muted">Nível máximo da trilha global.</p>
      )}

      {levelSummary.topAreas?.length > 0 && (
        <div className="scientific-xp-areas">
          <span className="scientific-route-label">Áreas fortes</span>
          <ul className="scientific-xp-areas-list">
            {levelSummary.topAreas.map((a) => (
              <li key={a.canonicalKey}>
                {a.label}: <strong>{a.xp} XP</strong>
                <span className="scientific-muted"> (Nv. área {a.areaLevel})</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {levelSummary.lastEvent && (
        <p className="scientific-muted scientific-xp-last">
          Último ganho: +{levelSummary.lastEvent.xp} XP — {levelSummary.lastEvent.title}
        </p>
      )}

      <button
        type="button"
        className="scientific-btn scientific-btn-ghost scientific-btn--sm"
        onClick={() => setHistoryOpen(true)}
      >
        Ver histórico
      </button>

      <ScientificXpHistoryModal
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        events={xpState?.events || []}
      />
    </section>
  );
}
