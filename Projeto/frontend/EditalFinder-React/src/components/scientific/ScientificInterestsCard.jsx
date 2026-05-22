import { useState } from 'react';
import { interestsByCategory, interestLabelById } from '../../utils/scientific/scientificInterestsConfig';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

export default function ScientificInterestsCard({ activeInterests = [], onToggle }) {
  const [expanded, setExpanded] = useState(false);
  const count = activeInterests.length;
  const groups = interestsByCategory();
  const activeLabels = activeInterests.map(interestLabelById);

  const toggleExpanded = () => {
    setExpanded((v) => {
      const next = !v;
      if (next) logScientificWorkspace('interests_expanded', { count });
      return next;
    });
  };

  return (
    <section id="scientific-interests" className="scientific-card scientific-interests-card">
      <div className="scientific-interests-head">
        <h2 className="scientific-card-title">Meus interesses</h2>
        <button type="button" className="scientific-btn scientific-btn-secondary scientific-btn--sm" onClick={toggleExpanded}>
          {expanded ? 'Recolher' : 'Editar interesses'}
        </button>
      </div>

      {!expanded ? (
        <div className="scientific-interests-compact">
          <p className="scientific-card-meta">
            Interesses ativos: <strong>{count}</strong>
          </p>
          <p className="scientific-interests-active-line">
            {activeLabels.length ? activeLabels.join(', ') : 'Nenhum selecionado — clique em Editar interesses.'}
          </p>
        </div>
      ) : (
        <>
          <p className="scientific-card-desc">
            Marque temas para personalizar feed, ideias e trilha ({count} ativos).
          </p>
          {groups.map((group) => (
            <details key={group.id} className="scientific-interest-category" open={false}>
              <summary className="scientific-interest-group-label">{group.label}</summary>
              <div className="scientific-interest-chips" role="group" aria-label={group.label}>
                {group.items.map((item) => {
                  const on = activeInterests.includes(item.id);
                  return (
                    <button
                      key={item.id}
                      type="button"
                      className={`scientific-tag scientific-tag--toggle ${on ? 'scientific-tag--on' : ''}`}
                      aria-pressed={on}
                      onClick={() => onToggle?.(item.id)}
                    >
                      {item.label}
                    </button>
                  );
                })}
              </div>
            </details>
          ))}
        </>
      )}
    </section>
  );
}
