import { useMemo } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { buildAreaGoalsForActiveInterests } from '../../utils/scientific/buildScientificAreaGoals';

export default function ScientificAreaGoalsCard({ activeInterests = [], studyBlocks = [] }) {
  const ctx = useScientificWorkspace();

  const blocksByKey = useMemo(() => {
    const map = {};
    for (const b of studyBlocks) {
      const k = b.canonicalKey || b.interestId;
      if (k) map[k] = b;
    }
    return map;
  }, [studyBlocks]);

  const areaGoals = useMemo(
    () =>
      buildAreaGoalsForActiveInterests(activeInterests, blocksByKey, {
        studyProgress: ctx.studyProgress,
        studySessions: ctx.studySessions,
        notebookItems: ctx.notebookItems,
        bookProgress: ctx.bookProgress,
        xpState: ctx.xpState,
      }),
    [
      activeInterests,
      blocksByKey,
      ctx.studyProgress,
      ctx.studySessions,
      ctx.notebookItems,
      ctx.bookProgress,
      ctx.xpState,
    ],
  );

  if (!areaGoals.length) return null;

  return (
    <section className="scientific-area-goals-wrap" aria-labelledby="scientific-area-goals-title">
      <h3 id="scientific-area-goals-title" className="scientific-route-label">
        Próximo nível por área
      </h3>
      {areaGoals.map((area) => (
        <article key={area.canonicalKey} className="scientific-area-goals-card">
          <h4 className="scientific-area-goals-head">
            Próximo nível em {area.areaLabel}
            <span className="scientific-muted">
              {' '}
              (Nv. {area.currentAreaLevel} → {area.nextAreaLevel})
            </span>
          </h4>
          <ul className="scientific-area-goals-list">
            {area.goals.map((g) => {
              const done = g.current >= g.target;
              return (
                <li key={g.id} className={done ? 'scientific-area-goal--done' : ''}>
                  <span aria-hidden>{done ? '✓' : '○'}</span> {g.label}
                  <span className="scientific-muted">
                    {' '}
                    ({Math.min(g.current, g.target)}/{g.target})
                  </span>
                </li>
              );
            })}
          </ul>
        </article>
      ))}
    </section>
  );
}
