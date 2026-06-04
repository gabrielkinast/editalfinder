import { useEffect, useMemo } from 'react';
import { buildRouteCardSummary, notebookEntryFromStudyRoute } from '../../utils/scientific/buildRouteCardSummary';
import { buildScientificStudyPath } from '../../utils/scientific/buildScientificStudyPath';
import { buildScientificGoalRoutes } from '../../utils/scientific/buildScientificGoalRoutes';
import { buildScientificProjectIdeas } from '../../utils/scientific/buildScientificProjectIdeas';
import { getBooksForInterests } from '../../utils/scientific/scientificBookCatalog';
import { displayScientificTitle } from '../../utils/scientific/cleanScientificTitle';
import { interestLabelById } from '../../utils/scientific/scientificInterestsConfig';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import ScientificSaveButton from './ScientificSaveButton';
import ScientificStudyProgressGlobal from './ScientificStudyProgressGlobal';
import ScientificStudyProgressSelect from './ScientificStudyProgressSelect';
import ScientificXpLevelCard from './ScientificXpLevelCard';
import ScientificBadgesCard from './ScientificBadgesCard';
import ScientificStartStudySessionButton from './ScientificStartStudySessionButton';
import ScientificAreaGoalsCard from './ScientificAreaGoalsCard';
import ScientificActiveReviewCard from './ScientificActiveReviewCard';
import ScientificStudySessionsCard from './ScientificStudySessionsCard';
import { notebookEntryFromPowerIdea } from '../../utils/scientific/notebookEntryFromPowerIdea';
import { buildPowerIdeaProgressKey } from '../../utils/scientific/scientificStudyProgressKeys';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

export default function ScientificRouteCard({
  activeInterests = [],
  feedItems = [],
  notebookItems = [],
}) {
  const { scrollToSection, studyProgress, getStudyProgressStatus } = useScientificWorkspace() || {};

  const progressBlocks = useMemo(() => {
    const path = buildScientificStudyPath(activeInterests, { feedItems, notebookItems });
    return path.allBlocks || [...path.primary, ...path.secondary];
  }, [activeInterests, feedItems, notebookItems]);

  const progressGoalRoutes = useMemo(() => {
    const projectIdeas = buildScientificProjectIdeas(activeInterests, notebookItems);
    const books = getBooksForInterests(activeInterests);
    return buildScientificGoalRoutes({
      interests: activeInterests,
      studyBlocks: progressBlocks,
      projectIdeas,
      books,
    });
  }, [activeInterests, notebookItems, progressBlocks]);

  const summary = useMemo(
    () =>
      buildRouteCardSummary({
        activeInterests,
        feedItems,
        notebookItems,
      }),
    [activeInterests, feedItems, notebookItems],
  );

  useEffect(() => {
    logScientificWorkspace('route_card_rendered', { interests: activeInterests.length });
  }, [activeInterests.length]);

  const rec = summary.recommendedProject;
  const recDisplay = rec ? displayScientificTitle(rec) : null;
  const nextAction = summary.nextAction;

  const routeEntry = useMemo(
    () => notebookEntryFromStudyRoute(summary, activeInterests),
    [summary, activeInterests],
  );

  const emptyRoute = activeInterests.length === 0;

  return (
    <section
      id="scientific-route"
      className="scientific-route-card scientific-route-card--hero"
      aria-labelledby="scientific-route-title"
    >
      <h2 id="scientific-route-title" className="scientific-route-card-title">
        Minha rota científica
      </h2>

      {emptyRoute ? (
        <p className="scientific-route-empty-hint">
          Selecione interesses para gerar uma rota mais precisa.
        </p>
      ) : (
        <>
          {summary.goalRouteTitle && (
            <p className="scientific-route-goal-headline">
              <strong>Rota sugerida:</strong> {summary.goalRouteTitle}
            </p>
          )}
          {summary.routeDescription && (
            <p className="scientific-muted scientific-text-clamp-3">{summary.routeDescription}</p>
          )}
          <div className="scientific-route-interest-chips">
            {activeInterests.slice(0, 6).map((id) => (
              <span key={id} className="scientific-tag scientific-tag--sm">
                {interestLabelById(id)}
              </span>
            ))}
            {activeInterests.length > 6 && (
              <span className="scientific-muted">+{activeInterests.length - 6}</span>
            )}
          </div>
        </>
      )}

      {!emptyRoute && (
        <>
          <ScientificXpLevelCard />
          <ScientificBadgesCard compact />
          <ScientificStudyProgressGlobal
            blocks={progressBlocks}
            progressMap={studyProgress || {}}
            goalRoutes={progressGoalRoutes}
          />
          <ScientificAreaGoalsCard
            activeInterests={activeInterests}
            studyBlocks={progressBlocks}
          />
          <ScientificActiveReviewCard
            studyBlocks={progressBlocks}
            activeInterests={activeInterests}
            goalRoutes={progressGoalRoutes}
            notebookItems={notebookItems}
          />
          <ScientificStudySessionsCard />
        </>
      )}

      {!emptyRoute && summary.powerIdea && (
        <div className="scientific-route-power-idea">
          <span className="scientific-route-label">Ideia poderosa da rota</span>
          <p className="scientific-route-highlight">{summary.powerIdea.title}</p>
          <p className="scientific-muted scientific-text-clamp-3">{summary.powerIdea.whyItMatters}</p>
          <div className="scientific-route-power-idea-actions">
            <ScientificStudyProgressSelect
              progressKey={buildPowerIdeaProgressKey(
                summary.powerIdeaAreaKey || summary.powerIdeaPick?.areaKey,
                summary.powerIdea,
              )}
              itemMeta={{
                canonicalKey: summary.powerIdeaAreaKey,
                kind: 'powerIdea',
                title: summary.powerIdea.title,
                areaLabel: summary.powerIdeaAreaLabel,
                level: summary.powerIdea.level,
                itemType: summary.powerIdea.type,
                whyItMatters: summary.powerIdea.whyItMatters,
                shortExplanation: summary.powerIdea.shortExplanation,
                relatedTopics: summary.powerIdea.relatedTopics,
              }}
            />
            <ScientificSaveButton
              entry={notebookEntryFromPowerIdea({
                idea: summary.powerIdea,
                canonicalKey: summary.powerIdeaAreaKey,
                areaLabel: summary.powerIdeaAreaLabel,
                studyProgressStatus: getStudyProgressStatus?.(
                  buildPowerIdeaProgressKey(
                    summary.powerIdeaAreaKey || '',
                    summary.powerIdea,
                  ),
                ),
              })}
              label="Salvar no caderno"
              action="save_power_idea"
              variant="secondary"
              size="scientific-btn--xs"
            />
          </div>
        </div>
      )}

      {!emptyRoute && summary.nextStepText && (
        <p className="scientific-route-next-step">
          <strong>Seu próximo passo:</strong> {summary.nextStepText}
        </p>
      )}

      {nextAction && (
        <div className="scientific-next-action">
          <span className="scientific-route-label">Próxima ação sugerida</span>
          <p className="scientific-next-action-title">{nextAction.title}</p>
          <p className="scientific-next-action-desc">{nextAction.description}</p>
          <button
            type="button"
            className="scientific-btn scientific-btn-primary"
            onClick={() => scrollToSection?.(nextAction.targetSection, 'next_action', nextAction.actionLabel)}
          >
            {nextAction.actionLabel}
          </button>
        </div>
      )}

      <div className="scientific-route-blocks">
        {summary.nextConcept && (
          <div className="scientific-route-block scientific-route-block--highlight">
            <span className="scientific-route-label">Próximo conceito</span>
            <p className="scientific-text-clamp-2" title={summary.nextConcept}>
              {summary.nextConcept}
            </p>
          </div>
        )}
        {recDisplay && (
          <div className="scientific-route-block">
            <span className="scientific-route-label">Projeto recomendado</span>
            {recDisplay.badge && (
              <span className="scientific-continuation-badge">{recDisplay.badge}</span>
            )}
            <p className="scientific-route-highlight scientific-text-clamp-2" title={recDisplay.titleFull}>
              {recDisplay.title}
            </p>
            {rec?.levelLabel && (
              <span className="scientific-level-badge scientific-level-badge--sm">{rec.levelLabel}</span>
            )}
          </div>
        )}
        {summary.routeBooks?.length > 0 && (
          <div className="scientific-route-block">
            <span className="scientific-route-label">Livro recomendado</span>
            <p className="scientific-text-clamp-2" title={summary.routeBooks[0]}>
              {summary.routeBooks[0]}
            </p>
          </div>
        )}
        {summary.professorQuestion && (
          <div className="scientific-route-block">
            <span className="scientific-route-label">Pergunta para professor</span>
            <p className="scientific-text-clamp-3">{summary.professorQuestion}</p>
          </div>
        )}
      </div>

      <div className="scientific-route-actions">
        {!emptyRoute && (
          <ScientificStartStudySessionButton
            studyBlocks={progressBlocks}
            activeInterests={activeInterests}
            goalRoutes={progressGoalRoutes}
            notebookItems={notebookItems}
            initial={{
              openSource: 'route',
              activeInterests,
              goalRouteId: progressGoalRoutes[0]?.id,
            }}
            label="Iniciar sessão de estudo"
            variant="primary"
          />
        )}
        <button
          type="button"
          className="scientific-btn scientific-btn-primary"
          onClick={() => scrollToSection?.('scientific-study-path', 'ver_trilha_completa', 'Ver trilha completa')}
        >
          Ver trilha completa
        </button>
        <button
          type="button"
          className="scientific-btn scientific-btn-secondary"
          onClick={() => scrollToSection?.('scientific-projects', 'ver_ideias', 'Ver ideias')}
        >
          Ver ideias
        </button>
        <ScientificSaveButton
          entry={routeEntry}
          label="Salvar rota no caderno"
          action="save_route"
          variant="secondary"
        />
      </div>
    </section>
  );
}
