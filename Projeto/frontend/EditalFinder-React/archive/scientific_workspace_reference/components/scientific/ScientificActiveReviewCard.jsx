import { useMemo } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import {
  buildActiveReviewItems,
  groupActiveReviewItems,
} from '../../utils/scientific/buildActiveReviewItems';
import ScientificStartStudySessionButton from './ScientificStartStudySessionButton';

export default function ScientificActiveReviewCard({
  studyBlocks = [],
  activeInterests = [],
  goalRoutes = [],
  notebookItems = [],
}) {
  const ctx = useScientificWorkspace();

  const items = useMemo(
    () =>
      buildActiveReviewItems({
        studyBlocks,
        studyProgress: ctx.studyProgress,
        bookProgress: ctx.bookProgress,
        notebookItems,
        goalRoutes,
        activeInterests,
        limit: 24,
      }),
    [
      studyBlocks,
      ctx.studyProgress,
      ctx.bookProgress,
      notebookItems,
      goalRoutes,
      activeInterests,
    ],
  );

  const groups = useMemo(() => groupActiveReviewItems(items).slice(0, 5), [items]);
  const displayItems = items.slice(0, 8);

  if (!studyBlocks.length) return null;

  return (
    <section className="scientific-review-card" aria-labelledby="scientific-review-title">
      <h3 id="scientific-review-title" className="scientific-route-label">
        Revisão ativa
      </h3>
      <p className="scientific-muted">
        Itens em estudo, dominados há mais de 7 dias, livros em andamento, ideias, projetos e rotas.
      </p>

      {displayItems.length === 0 ? (
        <p className="scientific-muted">Nada pendente de revisão no momento.</p>
      ) : (
        <>
          {groups.map((g) => (
            <div key={g.id} className="scientific-review-group">
              <h4 className="scientific-review-group-title">{g.label}</h4>
              <ul className="scientific-review-list">
                {g.items.slice(0, 4).map((item) => (
                  <li key={item.progressKey}>
                    <strong>{item.label}</strong>
                    <span className="scientific-muted">
                      {' '}
                      — {item.reason}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </>
      )}

      <div className="scientific-review-actions">
        <ScientificStartStudySessionButton
          studyBlocks={studyBlocks}
          activeInterests={activeInterests}
          goalRoutes={goalRoutes}
          notebookItems={notebookItems}
          initial={{
            openSource: 'review',
            focus: 'review',
            quantity: 0,
            selectedProgressKeys: items.map((i) => i.progressKey),
          }}
          label="Revisar o que estou estudando"
          variant="primary"
        />
        <ScientificStartStudySessionButton
          studyBlocks={studyBlocks}
          activeInterests={activeInterests}
          goalRoutes={goalRoutes}
          notebookItems={notebookItems}
          initial={{
            openSource: 'review',
            focus: 'review',
            quantity: 20,
          }}
          label="Ver mais revisão"
          variant="secondary"
          size="scientific-btn--xs"
        />
      </div>
    </section>
  );
}
