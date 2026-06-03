import { useMemo, useState } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { getStudySessionStats } from '../../utils/scientific/scientificStudySessionStorage';
import ScientificStudySessionsModal from './ScientificStudySessionsModal';

export default function ScientificStudySessionsCard() {
  const { studySessions = [] } = useScientificWorkspace();
  const [open, setOpen] = useState(false);

  const stats = useMemo(() => getStudySessionStats(studySessions), [studySessions]);
  const last = studySessions[0];
  const lastReflection = last?.reflection;

  return (
    <section className="scientific-sessions-card" aria-labelledby="scientific-sessions-title">
      <h3 id="scientific-sessions-title" className="scientific-route-label">
        Sessões de estudo
      </h3>
      <ul className="scientific-sessions-stats">
        <li>
          <strong>{stats.sessionCount}</strong> sessões
        </li>
        <li>
          <strong>{stats.totalMinutes}</strong> min totais
        </li>
        <li>
          <strong>{stats.totalXp}</strong> XP de sessões
        </li>
      </ul>

      {stats.topAreas?.length > 0 && (
        <p className="scientific-muted">
          Áreas mais estudadas:{' '}
          {stats.topAreas.map(([k, mins]) => `${k} (${mins} min)`).join(', ')}
        </p>
      )}

      {last && (
        <p className="scientific-muted scientific-sessions-last">
          Última: {last.title} — {last.durationMinutes} min
          {lastReflection?.learned && (
            <>
              <br />
              <em>{String(lastReflection.learned).slice(0, 120)}</em>
            </>
          )}
        </p>
      )}

      <button
        type="button"
        className="scientific-btn scientific-btn-ghost scientific-btn--sm"
        onClick={() => setOpen(true)}
      >
        Ver histórico de sessões
      </button>

      <ScientificStudySessionsModal open={open} onClose={() => setOpen(false)} />
    </section>
  );
}
