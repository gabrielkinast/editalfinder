import { useCallback, useMemo, useState } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { buildScientificStudyPath } from '../../utils/scientific/buildScientificStudyPath';
import { buildScientificGoalRoutes } from '../../utils/scientific/buildScientificGoalRoutes';
import { buildScientificProjectIdeas } from '../../utils/scientific/buildScientificProjectIdeas';
import { getBooksForInterests } from '../../utils/scientific/scientificBookCatalog';
import { downloadScientificRouteMarkdown } from '../../utils/scientific/exportScientificRouteMarkdown';
import {
  buildTrailProgressSummary,
  matchesStudyProgressFilter,
} from '../../utils/scientific/buildStudyProgressSummary';
import { notebookEntryFromBook } from '../../utils/scientific/notebookEntryFromBook';
import { notebookEntryFromGoalRoute } from '../../utils/scientific/notebookEntryFromGoalRoute';
import { notebookEntryFromProfessorQuestion } from '../../utils/scientific/notebookEntryFromProfessorQuestion';
import { notebookEntryFromTheory, theoryNotebookTitle } from '../../utils/scientific/notebookEntryFromTheory';
import { searchStudyPathBlocks, highlightTextParts } from '../../utils/scientific/searchStudyPathBlocks';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';
import { LEVEL_DESCRIPTIONS } from '../../utils/scientific/scientificProjectLevels';
import { STUDY_PROGRESS_FILTER_OPTIONS } from '../../utils/scientific/scientificStudyProgressConstants';
import { buildBookProgressKey } from '../../utils/scientific/scientificBookProgressStorage';
import { buildRouteStepProgressKey, buildStudyProgressKey } from '../../utils/scientific/scientificStudyProgressKeys';
import ScientificSaveButton from './ScientificSaveButton';
import ScientificStudyProgressSelect from './ScientificStudyProgressSelect';
import ScientificStudyProgressGlobal from './ScientificStudyProgressGlobal';
import ScientificPowerIdeasPanel from './ScientificPowerIdeasPanel';
import ScientificXpLevelCard from './ScientificXpLevelCard';
import ScientificBadgesCard from './ScientificBadgesCard';
import ScientificStartStudySessionButton from './ScientificStartStudySessionButton';

const TABS = [
  { id: 'overview', label: 'Visão geral' },
  { id: 'prerequisites', label: 'Pré-requisitos' },
  { id: 'theory', label: 'Teoria' },
  { id: 'powerIdeas', label: 'Teoremas & Ideias' },
  { id: 'books', label: 'Livros' },
  { id: 'projects', label: 'Projetos' },
  { id: 'questions', label: 'Perguntas' },
];

function HighlightedText({ text, query }) {
  const parts = highlightTextParts(text, query);
  return (
    <>
      {parts.map((p, i) =>
        p.match ? (
          <mark key={i} className="scientific-search-highlight">
            {p.text}
          </mark>
        ) : (
          <span key={i}>{p.text}</span>
        ),
      )}
    </>
  );
}

function matchesQuery(text, q) {
  if (!q) return true;
  return String(text || '').toLowerCase().includes(q);
}

function filterTopics(items, q) {
  if (!q) return items || [];
  return (items || []).filter((t) => matchesQuery(t, q));
}

function countBooks(block) {
  const deep = block.deep;
  if (!deep?.books) return block.books?.length || 0;
  return Object.values(deep.books).reduce((n, arr) => n + (arr?.length || 0), 0);
}

function countProjects(block) {
  const tracks = block.deep?.projectTracks;
  if (!tracks) return 0;
  return Object.values(tracks).reduce((n, arr) => n + (arr?.length || 0), 0);
}

function trailCountsLine(block) {
  const tc = block.theoryCounts || {};
  const parts = [
    `Fundamentos ${tc.foundations ?? 0}`,
    `Intermediário ${tc.intermediate ?? 0}`,
    `Avançado ${tc.advanced ?? 0}`,
    `Pesquisa ${tc.researchLevel ?? 0}`,
    `Projetos ${countProjects(block)}`,
    `Livros ${countBooks(block)}`,
  ];
  return parts.join(' · ');
}

function TrailProgressBar({ block, progressMap }) {
  const trail = useMemo(() => buildTrailProgressSummary(block, progressMap), [block, progressMap]);
  if (!trail.total) return null;
  return (
    <div className="scientific-trail-progress-wrap">
      <div
        className="scientific-trail-progress-bar-track"
        role="progressbar"
        aria-valuenow={trail.percentMarked}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="scientific-trail-progress-bar-fill"
          style={{ width: `${trail.percentMarked}%` }}
        />
      </div>
      <p className="scientific-trail-progress-text">{trail.line}</p>
      {trail.detailLine ? (
        <p className="scientific-muted scientific-trail-progress-detail">{trail.detailLine}</p>
      ) : null}
    </div>
  );
}

function TopicList({
  items,
  highlightQuery,
  canonicalKey,
  areaLabel,
  kind = 'theory',
  segment,
  progressFilter,
}) {
  const { getStudyProgressStatus } = useScientificWorkspace();
  const list = useMemo(() => {
    return (items || []).filter((topic) => {
      if (!progressFilter) return true;
      const key = buildStudyProgressKey(canonicalKey, kind, segment, topic);
      return matchesStudyProgressFilter(getStudyProgressStatus(key), progressFilter);
    });
  }, [items, progressFilter, canonicalKey, kind, segment, getStudyProgressStatus]);

  if (!list.length) return <p className="scientific-muted">—</p>;
  return (
    <ol className="scientific-study-ol scientific-study-ol--progress">
      {list.map((c) => {
        const progressKey = buildStudyProgressKey(canonicalKey, kind, segment, c);
        return (
          <li
            key={c}
            className={`scientific-study-topic-row ${highlightQuery && matchesQuery(c, highlightQuery) ? 'scientific-trail-match' : ''}`}
          >
            <span className="scientific-study-topic-label">
              {highlightQuery && matchesQuery(c, highlightQuery) ? (
                <HighlightedText text={c} query={highlightQuery} />
              ) : (
                c
              )}
            </span>
            <ScientificStudyProgressSelect
              progressKey={progressKey}
              itemMeta={{
                canonicalKey,
                kind,
                title: c,
                areaLabel,
                level: segment,
              }}
            />
          </li>
        );
      })}
    </ol>
  );
}

function BookList({ books, bookEntries, canonicalKey, areaLabel, searchQ, bookLevel, progressFilter }) {
  const { getStudyProgressStatus, bookProgress, openBookProgressModal } = useScientificWorkspace();
  const entries = bookEntries?.length
    ? bookEntries
    : (books || []).map((line) => {
        const parts = String(line).split(' — ');
        return {
          author: parts[0] || '',
          title: parts.slice(1).join(' — ') || line,
          level: bookLevel || 'introductory',
          area: canonicalKey,
          why: '',
          useFor: '',
        };
      });

  const filtered = entries.filter((book) => {
    const blob = `${book.author} ${book.title} ${book.why} ${book.useFor}`.toLowerCase();
    if (searchQ && !blob.includes(searchQ)) return false;
    const label = book.author ? `${book.author} — ${book.title}` : book.title;
    const progressKey = buildStudyProgressKey(canonicalKey, 'book', book.level || bookLevel, label);
    if (progressFilter && !matchesStudyProgressFilter(getStudyProgressStatus(progressKey), progressFilter)) {
      return false;
    }
    return true;
  });

  if (!filtered.length) return <p className="scientific-muted">Nenhum livro neste filtro.</p>;

  return (
    <ul className="scientific-study-ul scientific-deep-book-list">
      {filtered.map((book) => {
        const label = book.author ? `${book.author} — ${book.title}` : book.title;
        const progressKey = buildStudyProgressKey(canonicalKey, 'book', book.level || bookLevel, label);
        const bookKey = buildBookProgressKey(book, canonicalKey);
        const bp = bookProgress?.[bookKey];
        const status = getStudyProgressStatus(progressKey);
        return (
          <li key={label} className="scientific-deep-book-item">
            <div className="scientific-deep-book-head">
              <strong>
                {searchQ && matchesQuery(label, searchQ) ? (
                  <HighlightedText text={label} query={searchQ} />
                ) : (
                  label
                )}
              </strong>
              {book.level && <span className="scientific-tag scientific-tag--sm">{book.level}</span>}
              <ScientificStudyProgressSelect
                progressKey={progressKey}
                itemMeta={{
                  canonicalKey,
                  kind: 'book',
                  title: label,
                  areaLabel,
                  level: book.level || bookLevel,
                  whyItMatters: book.why,
                  shortExplanation: book.useFor,
                }}
              />
            </div>
            {bp && (
              <p className="scientific-muted scientific-book-progress-line">
                Leitura: {bp.status} · {bp.progressPercent ?? 0}%
                {bp.currentChapter ? ` · ${bp.currentChapter}` : ''}
              </p>
            )}
            <button
              type="button"
              className="scientific-btn scientific-btn-ghost scientific-btn--xs"
              onClick={() =>
                openBookProgressModal?.({
                  book,
                  bookKey,
                  canonicalKey,
                  areaLabel,
                })
              }
            >
              Atualizar leitura
            </button>
            {book.why && <p className="scientific-muted">{book.why}</p>}
            {book.useFor && <p className="scientific-muted scientific-deep-use-for">Para: {book.useFor}</p>}
            <ScientificSaveButton
              entry={notebookEntryFromBook({
                ...book,
                area: book.area || canonicalKey,
                studyProgressStatus: status,
              })}
              label="Salvar livro"
              action="save_book"
              variant="secondary"
              size="scientific-btn--xs"
            />
          </li>
        );
      })}
    </ul>
  );
}

function TheorySection({ block, searchQ, defaultOpenLayers, progressFilter, areaLabel }) {
  const { theory, layerLabels } = block.deep;
  const canonicalKey = block.canonicalKey || block.interestId;
  const trailAreaLabel = areaLabel || block.label;
  const { getStudyProgressStatus } = useScientificWorkspace();

  const layers = [
    { key: 'foundations', label: layerLabels?.foundations || 'Fundamentos', count: block.theoryCounts?.foundations },
    { key: 'intermediate', label: layerLabels?.intermediate || 'Intermediário', count: block.theoryCounts?.intermediate },
    { key: 'advanced', label: layerLabels?.advanced || 'Avançado', count: block.theoryCounts?.advanced },
    { key: 'researchLevel', label: layerLabels?.researchLevel || 'Pesquisa / Mestrado', count: block.theoryCounts?.researchLevel },
  ];

  return (
    <div className="scientific-trail-theory">
      {layers.map(({ key, label, count }) => {
        const topics = filterTopics(theory?.[key], searchQ);
        const displayTopics = topics.length ? topics : theory?.[key] || [];
        const visibleCount = progressFilter
          ? displayTopics.filter((t) =>
              matchesStudyProgressFilter(
                getStudyProgressStatus(buildStudyProgressKey(canonicalKey, 'theory', key, t)),
                progressFilter,
              ),
            ).length
          : displayTopics.length;
        if (searchQ && topics.length === 0) return null;
        if (progressFilter && visibleCount === 0) return null;
        const open = defaultOpenLayers?.includes(key);
        return (
          <details key={key} className="scientific-study-nested" open={open}>
            <summary>
              {label}
              {count != null && <span className="scientific-trail-count"> ({count})</span>}
            </summary>
            {key === 'foundations' && (
              <p className="scientific-level-hint">{LEVEL_DESCRIPTIONS.fundamentals}</p>
            )}
            {key === 'advanced' && (
              <p className="scientific-level-hint">{LEVEL_DESCRIPTIONS.advanced_research}</p>
            )}
            {key === 'researchLevel' && (
              <p className="scientific-level-hint">{LEVEL_DESCRIPTIONS.graduate}</p>
            )}
            <TopicList
              items={displayTopics}
              highlightQuery={searchQ}
              canonicalKey={canonicalKey}
              areaLabel={trailAreaLabel}
              kind="theory"
              segment={key}
              progressFilter={progressFilter}
            />
            <ScientificSaveButton
              entry={notebookEntryFromTheory({
                areaLabel: trailAreaLabel,
                layer: key,
                topics: theory?.[key] || [],
                interestId: canonicalKey,
                canonicalKey,
              })}
              label={`Salvar bloco de teoria`}
              action="save_theory"
              variant="secondary"
              size="scientific-btn--xs"
            />
          </details>
        );
      })}
    </div>
  );
}

function DeepTrailPanel({
  block,
  defaultOpen,
  searchQ,
  forceOpen,
  progressFilter,
  studyProgress,
  allBlocks = [],
  activeInterests = [],
  goalRoutes = [],
  notebookItems = [],
}) {
  const [activeTab, setActiveTab] = useState('overview');
  const { getStudyProgressStatus } = useScientificWorkspace();
  const deep = block.deep;
  const canonicalKey = block.canonicalKey || block.interestId;
  const q = searchQ?.trim().toLowerCase() || '';
  const trailId = `trail-${canonicalKey}`;

  const hasMatchInBlock = useMemo(() => {
    if (!q) return true;
    const blobs = [
      block.label,
      block.description,
      block.formationGoal,
      ...(block.matchedInterestLabels || []),
      ...Object.values(deep?.prerequisites || {}).flat(),
      ...Object.values(deep?.theory || {}).flat(),
      ...Object.values(deep?.books || {}).flat(),
      ...Object.values(deep?.projectTracks || {}).flat(),
      ...(deep?.professorQuestions || block.professorQuestions || []),
      ...(block.powerIdeas || deep?.powerIdeas || []).flatMap((idea) => [
        idea.title,
        idea.whyItMatters,
        idea.shortExplanation,
        ...(idea.relatedTopics || []),
      ]),
    ];
    return blobs.some((t) => matchesQuery(t, q));
  }, [block, deep, q]);

  if (q && !hasMatchInBlock) return null;

  const openAccordion = defaultOpen || forceOpen || Boolean(q);

  const prereqGroups = [
    { key: 'math', label: 'Matemática' },
    { key: 'physics', label: 'Física' },
    { key: 'chemistry', label: 'Química' },
    { key: 'computation', label: 'Computação' },
  ];

  const projectTracks = [
    { key: 'basic', label: 'Básico' },
    { key: 'intermediate', label: 'Intermediário' },
    { key: 'advanced', label: 'Avançado' },
    { key: 'ictcc', label: 'IC/TCC' },
    { key: 'masters', label: 'Mestrado' },
  ];

  const mainPrereq = deep?.prerequisites
    ? [
        ...(deep.prerequisites.math || []).slice(0, 2),
        ...(deep.prerequisites.physics || []).slice(0, 2),
      ].slice(0, 4)
    : [];

  return (
    <details
      id={trailId}
      className="scientific-study-accordion scientific-study-accordion--deep"
      open={openAccordion}
    >
      <summary className="scientific-study-accordion-summary">
        <span className="scientific-trail-summary-title">
          {q && matchesQuery(block.label, q) ? (
            <HighlightedText text={block.label} query={q} />
          ) : (
            block.label
          )}
        </span>
        {block.matchedInterestLabels?.length > 1 && (
          <span className="scientific-trail-alias-hint">
            ({block.matchedInterestLabels.join(', ')})
          </span>
        )}
        <span className="scientific-trail-summary-meta">{trailCountsLine(block)}</span>
        <TrailProgressBar block={block} progressMap={studyProgress} />
      </summary>
      <div className="scientific-study-accordion-body">
        <nav className="scientific-trail-tabs" role="tablist" aria-label={`Seções de ${block.label}`}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.id}
              className={`scientific-trail-tab ${activeTab === tab.id ? 'scientific-trail-tab--active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {activeTab === 'overview' && (
          <div className="scientific-trail-panel">
            <p className="scientific-trail-goal">
              {q && matchesQuery(block.formationGoal || block.description, q) ? (
                <HighlightedText text={block.formationGoal || block.description} query={q} />
              ) : (
                block.formationGoal || block.description
              )}
            </p>
            {block.description && block.formationGoal && (
              <p className="scientific-muted">{block.description}</p>
            )}
            {mainPrereq.length > 0 && (
              <p className="scientific-muted scientific-trail-prereq-hint">
                <strong>Pré-requisitos:</strong> {mainPrereq.join(' · ')}
              </p>
            )}
            <div className="scientific-trail-session-actions">
              <ScientificStartStudySessionButton
                studyBlocks={allBlocks.length ? allBlocks : [block]}
                activeInterests={activeInterests}
                goalRoutes={goalRoutes}
                notebookItems={notebookItems}
                initial={{ openSource: 'trail', canonicalKey, activeInterests }}
                label="Iniciar sessão de estudo"
                variant="secondary"
                size="scientific-btn--xs"
              />
            </div>
            <div className="scientific-trail-counts">
              {trailCountsLine(block)
                .split(' · ')
                .map((tag) => (
                  <span key={tag} className="scientific-tag scientific-tag--sm">
                    {tag}
                  </span>
                ))}
            </div>
          </div>
        )}

        {activeTab === 'prerequisites' && (
          <div className="scientific-trail-panel">
            {prereqGroups.map(({ key, label }) => {
              const topics = filterTopics(deep?.prerequisites?.[key], q);
              if (q && !topics.length) return null;
              return (
                <details key={key} className="scientific-study-nested" open={key === 'math' && !q}>
                  <summary>{label}</summary>
                  <TopicList
                    items={topics.length ? topics : deep?.prerequisites?.[key]}
                    highlightQuery={q}
                    canonicalKey={canonicalKey}
                    areaLabel={block.label}
                    kind="theory"
                    segment={`prereq-${key}`}
                    progressFilter={progressFilter}
                  />
                  <ScientificSaveButton
                    entry={notebookEntryFromTheory({
                      areaLabel: block.label,
                      layer: key,
                      topics: deep?.prerequisites?.[key] || [],
                      canonicalKey,
                    })}
                    label={`Salvar: ${theoryNotebookTitle(block.label, key)}`}
                    action="save_theory_prereq"
                    variant="secondary"
                    size="scientific-btn--xs"
                  />
                </details>
              );
            })}
          </div>
        )}

        {activeTab === 'theory' && (
          <div className="scientific-trail-panel">
            <TheorySection
              block={block}
              searchQ={q}
              progressFilter={progressFilter}
              areaLabel={block.label}
              defaultOpenLayers={q ? ['foundations', 'intermediate', 'advanced', 'researchLevel'] : ['foundations']}
            />
          </div>
        )}

        {activeTab === 'powerIdeas' && (
          <div className="scientific-trail-panel">
            <ScientificPowerIdeasPanel block={block} searchQ={q} progressFilter={progressFilter} />
          </div>
        )}

        {activeTab === 'books' && (
          <div className="scientific-trail-panel">
            {['introductory', 'intermediate', 'advanced', 'computational'].map((lvl) => {
              const lines = filterTopics(deep?.books?.[lvl], q);
              if (q && !lines.length) return null;
              const labels = {
                introductory: 'Base / introdutório',
                intermediate: 'Graduação',
                advanced: 'Avançado',
                computational: 'Computacional',
              };
              return (
                <details key={lvl} className="scientific-study-nested" open={lvl === 'introductory' || Boolean(q)}>
                  <summary>{labels[lvl] || lvl}</summary>
                  <BookList
                    books={lines.length ? lines : deep?.books?.[lvl]}
                    bookEntries={deep?.bookEntries}
                    canonicalKey={canonicalKey}
                    areaLabel={block.label}
                    bookLevel={lvl}
                    searchQ={q}
                    progressFilter={progressFilter}
                  />
                </details>
              );
            })}
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="scientific-trail-panel">
            {projectTracks.map(({ key, label }) => {
              const topics = filterTopics(deep?.projectTracks?.[key], q);
              if (q && !topics.length) return null;
              return (
                <details key={key} className="scientific-study-nested" open={Boolean(q)}>
                  <summary>{label}</summary>
                  <TopicList
                    items={topics.length ? topics : deep?.projectTracks?.[key]}
                    highlightQuery={q}
                    canonicalKey={canonicalKey}
                    areaLabel={block.label}
                    kind="project"
                    segment={key}
                    progressFilter={progressFilter}
                  />
                </details>
              );
            })}
          </div>
        )}

        {activeTab === 'questions' && (
          <div className="scientific-trail-panel">
            <ul className="scientific-study-ul scientific-study-ol--progress">
              {(deep?.professorQuestions || block.professorQuestions || [])
                .filter((item) => {
                  if (!progressFilter) return true;
                  const pk = buildStudyProgressKey(canonicalKey, 'question', 'question', item);
                  return matchesStudyProgressFilter(getStudyProgressStatus(pk), progressFilter);
                })
                .map((item) => {
                  const progressKey = buildStudyProgressKey(canonicalKey, 'question', 'question', item);
                  const status = getStudyProgressStatus(progressKey);
                  return (
                    <li key={item} className="scientific-trail-question-item scientific-study-topic-row">
                      <span className="scientific-study-topic-label">
                        {q && matchesQuery(item, q) ? (
                          <HighlightedText text={item} query={q} />
                        ) : (
                          item
                        )}
                      </span>
                      <ScientificStudyProgressSelect
                        progressKey={progressKey}
                        itemMeta={{
                          canonicalKey,
                          kind: 'question',
                          title: item,
                          areaLabel: block.label,
                        }}
                      />
                      <ScientificSaveButton
                        entry={notebookEntryFromProfessorQuestion({
                          question: item,
                          label: block.label,
                          interestId: canonicalKey,
                          studyProgressStatus: status,
                        })}
                        label="Salvar pergunta"
                        action="save_professor_question"
                        variant="secondary"
                        size="scientific-btn--xs"
                      />
                    </li>
                  );
                })}
            </ul>
          </div>
        )}
      </div>
    </details>
  );
}

function LegacyInterestAccordion({ block, defaultOpen }) {
  return (
    <details className="scientific-study-accordion" open={defaultOpen}>
      <summary className="scientific-study-accordion-summary">{block.label}</summary>
      <div className="scientific-study-accordion-body">
        <details className="scientific-study-nested">
          <summary>Fundamentos</summary>
          <TopicList items={block.fundamentals} />
        </details>
        <details className="scientific-study-nested">
          <summary>Intermediário</summary>
          <TopicList items={block.intermediate} />
        </details>
      </div>
    </details>
  );
}

function GoalRoutesSection({ routes, activeInterests, progressFilter, studyProgress }) {
  const { getStudyProgressStatus } = useScientificWorkspace();
  if (!routes.length) return null;

  return (
    <section className="scientific-goal-routes" aria-labelledby="scientific-goal-routes-title">
      <h3 id="scientific-goal-routes-title" className="scientific-recommended-title">
        Rotas por objetivo
      </h3>
      <p className="scientific-muted">
        Sequências sugeridas a partir dos seus interesses — salve no caderno para acompanhar.
      </p>
      <div className="scientific-goal-routes-list">
        {routes.map((route) => (
          <details key={route.id} className="scientific-study-nested scientific-goal-route-card">
            <summary>
              <strong>{route.title}</strong>
            </summary>
            <div className="scientific-goal-route-body">
              <p className="scientific-muted">{route.description}</p>
              <ol className="scientific-study-ol scientific-study-ol--progress">
                {route.steps
                  .filter((step) => {
                    if (!progressFilter) return true;
                    const pk = buildRouteStepProgressKey(route.id, step);
                    return matchesStudyProgressFilter(getStudyProgressStatus(pk), progressFilter);
                  })
                  .map((step) => {
                    const progressKey = buildRouteStepProgressKey(route.id, step);
                    return (
                      <li key={step} className="scientific-study-topic-row">
                        <span className="scientific-study-topic-label">{step}</span>
                        <ScientificStudyProgressSelect
                          progressKey={progressKey}
                          itemMeta={{
                            canonicalKey: `goal::${route.id}`,
                            kind: 'route_step',
                            title: step,
                            areaLabel: route.title,
                          }}
                        />
                      </li>
                    );
                  })}
              </ol>
              {route.suggestedProjects?.length > 0 && (
                <>
                  <p className="scientific-route-label">Projetos sugeridos</p>
                  <ul className="scientific-study-ul">
                    {route.suggestedProjects.map((p) => (
                      <li key={p}>{p}</li>
                    ))}
                  </ul>
                </>
              )}
              {route.suggestedBooks?.length > 0 && (
                <>
                  <p className="scientific-route-label">Livros recomendados</p>
                  <ul className="scientific-study-ul">
                    {route.suggestedBooks.map((b) => (
                      <li key={b}>{b}</li>
                    ))}
                  </ul>
                </>
              )}
              <ScientificSaveButton
                entry={notebookEntryFromGoalRoute(route, activeInterests)}
                label="Salvar rota no caderno"
                action="save_goal_route"
                variant="secondary"
                size="scientific-btn--xs"
              />
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}

export default function ScientificStudyPath({
  activeInterests = [],
  feedItems = [],
  notebookItems = [],
}) {
  const ctx = useScientificWorkspace();
  const studyProgress = ctx?.studyProgress || {};
  const [showAllTrails, setShowAllTrails] = useState(false);
  const [trailSearch, setTrailSearch] = useState('');
  const [progressFilter, setProgressFilter] = useState('');

  const pathData = useMemo(
    () => buildScientificStudyPath(activeInterests, { feedItems, notebookItems, primaryLimit: 8 }),
    [activeInterests, feedItems, notebookItems],
  );

  const allBlocks = useMemo(
    () => pathData.allBlocks || [...pathData.primary, ...pathData.secondary],
    [pathData],
  );

  const projectIdeas = useMemo(
    () => buildScientificProjectIdeas(activeInterests, notebookItems),
    [activeInterests, notebookItems],
  );

  const books = useMemo(() => getBooksForInterests(activeInterests), [activeInterests]);

  const goalRoutes = useMemo(
    () =>
      buildScientificGoalRoutes({
        interests: activeInterests,
        studyBlocks: allBlocks,
        projectIdeas,
        books,
      }),
    [activeInterests, allBlocks, projectIdeas, books],
  );

  const primaryGoalRoute = goalRoutes[0] || null;

  const rawVisible = showAllTrails
    ? [...pathData.primary, ...pathData.secondary]
    : pathData.primary;

  const searchQ = trailSearch.trim().toLowerCase();

  const searchResult = useMemo(
    () => searchStudyPathBlocks(rawVisible, searchQ),
    [rawVisible, searchQ],
  );

  const visibleBlocks = searchResult.blocks;

  const scrollToTrail = useCallback((canonicalKey) => {
    const el = document.getElementById(`trail-${canonicalKey}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      el.classList.add('scientific-section-highlight');
      setTimeout(() => el.classList.remove('scientific-section-highlight'), 1400);
    }
    logScientificWorkspace('trail_nav_click', { canonicalKey });
  }, []);

  const handleExportMarkdown = () => {
    downloadScientificRouteMarkdown({
      activeInterests,
      goalRoute: primaryGoalRoute,
      studyBlocks: allBlocks,
      goalRoutes,
      studyProgress,
      xpState: ctx?.xpState,
      levelSummary: ctx?.levelSummary,
      badges: ctx?.badges,
      masteryChecks: ctx?.masteryChecks,
      bookProgress: ctx?.bookProgress,
      studySessions: ctx?.studySessions,
      notebookItems,
      includePowerIdeas: true,
    });
    logScientificWorkspace('markdown_exported', { interests: activeInterests.length });
  };

  const noInterests = activeInterests.length === 0;

  return (
    <section id="scientific-study-path" className="scientific-card scientific-card--wide scientific-study-section">
      <h2 className="scientific-card-title">Trilha de estudo</h2>
      <p className="scientific-card-meta">
        Formação em camadas (graduação avançada → IC/TCC → mestrado). Uma trilha por área — sem duplicatas.
      </p>

      {noInterests && (
        <p className="scientific-empty-hint">Selecione interesses para gerar sua trilha de fundamentos.</p>
      )}

      {!noInterests && (
        <>
          <ScientificXpLevelCard compact />
          <ScientificBadgesCard compact />
          <ScientificStudyProgressGlobal
            blocks={allBlocks}
            progressMap={studyProgress}
            goalRoutes={goalRoutes}
          />
          <div className="scientific-study-session-bar">
            <ScientificStartStudySessionButton
              studyBlocks={allBlocks}
              activeInterests={activeInterests}
              goalRoutes={goalRoutes}
              notebookItems={notebookItems}
              initial={{ openSource: 'study_path', activeInterests }}
              label="Iniciar sessão de estudo"
              variant="primary"
            />
          </div>
        </>
      )}

      {!noInterests && (
        <>
          <label className="scientific-trail-search-label">
            Buscar na trilha…
            <input
              type="search"
              className="scientific-search-input"
              value={trailSearch}
              onChange={(e) => setTrailSearch(e.target.value)}
              placeholder="Tópico, livro ou projeto"
              aria-label="Buscar na trilha de estudo"
            />
          </label>
          <label className="scientific-trail-filter-label">
            Status
            <select
              className="scientific-search-input scientific-progress-filter-select"
              value={progressFilter}
              onChange={(e) => {
                setProgressFilter(e.target.value);
                logScientificWorkspace('study_progress_filter_changed', { filter: e.target.value || 'all' });
              }}
            >
              {STUDY_PROGRESS_FILTER_OPTIONS.map((o) => (
                <option key={o.id || 'all'} value={o.id}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          {searchQ && (
            <p className="scientific-trail-search-meta" role="status">
              {searchResult.trailCount === 0
                ? 'Nenhum tópico encontrado. Tente outro termo.'
                : `${searchResult.matchCount} resultado${searchResult.matchCount !== 1 ? 's' : ''} em ${searchResult.trailCount} trilha${searchResult.trailCount !== 1 ? 's' : ''}`}
            </p>
          )}
        </>
      )}

      {primaryGoalRoute && !searchQ && (
        <div className="scientific-study-route-hero">
          <h3 className="scientific-recommended-title">Rota sugerida para você</h3>
          <p className="scientific-muted">
            <strong>{primaryGoalRoute.title}</strong> — {primaryGoalRoute.description}
          </p>
          <ol className="scientific-study-ol scientific-study-ol--inline">
            {primaryGoalRoute.steps.slice(0, 6).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {!noInterests && visibleBlocks.length > 0 && (
        <nav className="scientific-trail-nav" aria-label="Trilhas ativas">
          <span className="scientific-trail-nav-label">Trilhas ativas</span>
          <div className="scientific-trail-nav-chips">
            {visibleBlocks.map((block) => {
              const key = block.canonicalKey || block.interestId;
              return (
                <button
                  key={key}
                  type="button"
                  className="scientific-trail-nav-chip"
                  onClick={() => scrollToTrail(key)}
                >
                  {block.label}
                </button>
              );
            })}
          </div>
        </nav>
      )}

      {visibleBlocks.length === 0 && !noInterests && (
        <p className="scientific-empty-hint">
          {searchQ ? 'Nenhum tópico encontrado. Tente outro termo.' : 'Nenhuma trilha para os interesses atuais.'}
        </p>
      )}

      <div className="scientific-study-accordions">
        {visibleBlocks.map((block, index) =>
          block.deep ? (
            <DeepTrailPanel
              key={block.canonicalKey || block.interestId || block.label}
              block={block}
              defaultOpen={index === 0 && !searchQ}
              forceOpen={Boolean(searchQ)}
              searchQ={searchQ}
              progressFilter={progressFilter}
              studyProgress={studyProgress}
              allBlocks={allBlocks}
              activeInterests={activeInterests}
              goalRoutes={goalRoutes}
              notebookItems={notebookItems}
            />
          ) : (
            <LegacyInterestAccordion
              key={block.interestId || block.label}
              block={block}
              defaultOpen={index === 0}
            />
          ),
        )}
      </div>

      {!searchQ && (
        <GoalRoutesSection
          routes={goalRoutes}
          activeInterests={activeInterests}
          progressFilter={progressFilter}
          studyProgress={studyProgress}
        />
      )}

      <div className="scientific-study-path-actions">
        {pathData.secondary?.length > 0 && (
          <button
            type="button"
            className="scientific-btn scientific-btn-secondary"
            onClick={() => {
              setShowAllTrails((v) => !v);
              logScientificWorkspace('button_click', { action: 'toggle_all_trails' });
            }}
          >
            {showAllTrails
              ? 'Mostrar menos trilhas'
              : `Ver todas as trilhas (${pathData.primary.length + pathData.secondary.length} áreas)`}
          </button>
        )}
        {!noInterests && (
          <button
            type="button"
            className="scientific-btn scientific-btn-ghost"
            onClick={handleExportMarkdown}
          >
            Exportar rota em Markdown
          </button>
        )}
      </div>
    </section>
  );
}
