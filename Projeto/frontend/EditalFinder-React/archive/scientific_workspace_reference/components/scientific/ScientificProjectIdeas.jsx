import { useMemo, useState } from 'react';
import { buildScientificProjectIdeas } from '../../utils/scientific/buildScientificProjectIdeas';
import { buildScientificBasicToMasters } from '../../utils/scientific/buildScientificBasicToMasters';
import { buildScientificProfessorQuestions } from '../../utils/scientific/buildScientificProfessorQuestions';
import { pickRecommendedProject } from '../../utils/scientific/pickRecommendedProject';
import {
  rankAndLimitProjectIdeas,
  pickProjectsByLevelTier,
} from '../../utils/scientific/rankScientificProjectIdeas';
import {
  PROJECT_LEVELS,
  PROJECT_LEVEL_FILTER_ALL,
  levelLabel,
  projectMaturityFromLevel,
} from '../../utils/scientific/scientificProjectLevels';
import {
  loadProjectLevelFilter,
  saveProjectLevelFilter,
} from '../../utils/scientific/scientificProjectLevelStorage';
import { interestLabelById, SCIENTIFIC_INTERESTS } from '../../utils/scientific/scientificInterestsConfig';
import { notebookEntryFromProjectIdea } from '../../utils/scientific/notebookEntryFromProjectIdea';
import { notebookEntryFromProfessorQuestion } from '../../utils/scientific/notebookEntryFromProfessorQuestion';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';
import ScientificTitleLine from './ScientificTitleLine';
import ScientificSaveButton from './ScientificSaveButton';

const IDEAS_PAGE = 9;

function IdeaCard({ idea }) {
  const maturityLabel = idea.maturity || projectMaturityFromLevel(idea.level).label;
  const entry = notebookEntryFromProjectIdea(idea);
  const hasTheory =
    idea.prerequisites?.length ||
    idea.theoryTopics?.length ||
    idea.possibleDeliverables?.length ||
    idea.professorQuestions?.length;

  return (
    <article className="scientific-idea-card">
      <div className="scientific-idea-card-head">
        <span className="scientific-level-badge">{idea.levelLabel || levelLabel(idea.level)}</span>
        <span className="scientific-maturity-badge">{maturityLabel}</span>
        <span className="scientific-tag scientific-tag--sm scientific-idea-type">{idea.type}</span>
        {idea.relevanceScore > 0 && (
          <span className="scientific-score-badge" title="Aderência">
            +{idea.relevanceScore}
          </span>
        )}
      </div>
      <ScientificTitleLine item={idea} />
      <p className="scientific-idea-field scientific-idea-field--why">{idea.why}</p>
      {idea.expectedOutput && (
        <p className="scientific-idea-output">
          <strong>Produto esperado:</strong> {idea.expectedOutput}
        </p>
      )}
      {hasTheory && (
        <details className="scientific-idea-details scientific-idea-theory-details">
          <summary>Ver teoria necessária</summary>
          {idea.prerequisites?.length > 0 && (
            <div className="scientific-idea-theory-block">
              <strong>Pré-requisitos</strong>
              <ul className="scientific-study-ul">
                {idea.prerequisites.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          )}
          {idea.theoryTopics?.length > 0 && (
            <div className="scientific-idea-theory-block">
              <strong>Tópicos teóricos</strong>
              <ul className="scientific-study-ul">
                {idea.theoryTopics.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          )}
          {idea.tools?.length > 0 && (
            <p className="scientific-muted">Ferramentas: {idea.tools.join(' · ')}</p>
          )}
          {idea.duration && <p className="scientific-muted">Duração sugerida: {idea.duration}</p>}
          {idea.nextSteps?.length > 0 && (
            <div className="scientific-idea-theory-block">
              <strong>Próximos passos</strong>
              <ol className="scientific-study-ol">
                {idea.nextSteps.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ol>
            </div>
          )}
          {idea.possibleDeliverables?.length > 0 && (
            <div className="scientific-idea-theory-block">
              <strong>Entregáveis</strong>
              <ul className="scientific-study-ul">
                {idea.possibleDeliverables.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          )}
          {idea.professorQuestions?.length > 0 && (
            <div className="scientific-idea-theory-block">
              <strong>Perguntas para professor</strong>
              <ul className="scientific-study-ul">
                {idea.professorQuestions.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </details>
      )}
      <details className="scientific-idea-details">
        <summary>Mais detalhes</summary>
        {idea.disciplines?.length > 0 && (
          <p className="scientific-muted">Disciplinas: {idea.disciplines.join(' · ')}</p>
        )}
        {!hasTheory && idea.tools?.length > 0 && (
          <p className="scientific-muted">Ferramentas: {idea.tools.join(' · ')}</p>
        )}
        {!hasTheory && idea.nextSteps?.length > 0 && (
          <ol className="scientific-study-ol">
            {idea.nextSteps.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>
        )}
      </details>
      <ScientificSaveButton
        entry={entry}
        label="Salvar no caderno"
        action="save_project_idea"
        variant="secondary"
        size="scientific-btn--xs"
      />
    </article>
  );
}

export default function ScientificProjectIdeas({
  activeInterests = [],
  notebookItems = [],
}) {
  const [levelFilter, setLevelFilter] = useState(() => loadProjectLevelFilter());
  const [interestFilter, setInterestFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [ideasLimit, setIdeasLimit] = useState(IDEAS_PAGE);

  const allIdeas = useMemo(
    () => buildScientificProjectIdeas(activeInterests, notebookItems),
    [activeInterests, notebookItems],
  );

  const recommended = useMemo(
    () => pickRecommendedProject(allIdeas, activeInterests),
    [allIdeas, activeInterests],
  );

  const byLevel = useMemo(
    () => pickProjectsByLevelTier(allIdeas, activeInterests, notebookItems),
    [allIdeas, activeInterests, notebookItems],
  );

  const rankedFull = useMemo(
    () =>
      rankAndLimitProjectIdeas(allIdeas, activeInterests, notebookItems, {
        limit: 200,
        levelFilter,
        interestFilter: interestFilter || undefined,
        searchQuery,
      }),
    [allIdeas, activeInterests, notebookItems, levelFilter, interestFilter, searchQuery],
  );

  const displayed = rankedFull.items.slice(0, ideasLimit);
  const hasMoreIdeas = rankedFull.items.length > ideasLimit;

  const professorQuestions = useMemo(
    () => buildScientificProfessorQuestions(activeInterests),
    [activeInterests],
  );

  const basicToMasters = useMemo(
    () => buildScientificBasicToMasters(activeInterests, notebookItems),
    [activeInterests, notebookItems],
  );

  const handleLevelFilter = (id) => {
    setLevelFilter(id);
    setIdeasLimit(IDEAS_PAGE);
    saveProjectLevelFilter(id);
    logScientificWorkspace('button_click', { action: 'project_level_filter', level: id });
    logScientificWorkspace('project_level_filter_changed', { level: id });
  };

  const levelFilters = [
    { id: PROJECT_LEVEL_FILTER_ALL, label: 'Todos' },
    ...PROJECT_LEVELS.map((l) => ({ id: l.id, label: l.label })),
  ];

  const interestOptions = activeInterests.length
    ? activeInterests.map((id) => ({ id, label: interestLabelById(id) }))
    : SCIENTIFIC_INTERESTS.slice(0, 12).map((i) => ({ id: i.id, label: i.label }));

  const recommendedEntry = recommended ? notebookEntryFromProjectIdea(recommended) : null;

  return (
    <section id="scientific-projects" className="scientific-card scientific-card--wide scientific-ideas-section">
      <h2 className="scientific-card-title">Ideias de projeto</h2>

      {activeInterests.length === 0 && (
        <p className="scientific-empty-hint">
          Selecione interesses para gerar ideias de projeto alinhadas à sua rota.
        </p>
      )}

      {recommended && recommendedEntry && (
        <div className="scientific-week-strip">
          <span className="scientific-week-strip-label">Semana</span>
          <ScientificTitleLine item={recommended} maxLen={72} className="scientific-week-strip-title" as="span" />
          <span className="scientific-level-badge scientific-level-badge--sm">{recommended.levelLabel}</span>
          <ScientificSaveButton
            entry={recommendedEntry}
            label="Salvar no caderno"
            action="save_week_project"
            variant="secondary"
            size="scientific-btn--xs"
          />
        </div>
      )}

      {basicToMasters.steps?.length > 0 && activeInterests.length > 0 && (
        <div className="scientific-basic-masters-strip">
          <h3 className="scientific-recommended-title">{basicToMasters.title}</h3>
          <ol className="scientific-basic-masters-list">
            {basicToMasters.steps.map((step) => (
              <li key={step.level} className="scientific-basic-masters-item">
                <span className="scientific-level-badge scientific-level-badge--sm">{step.tierLabel}</span>
                <span className="scientific-basic-masters-title">{step.title}</span>
                {step.idea && (
                  <ScientificSaveButton
                    entry={notebookEntryFromProjectIdea(step.idea)}
                    label="Salvar"
                    action="save_basic_masters_step"
                    variant="secondary"
                    size="scientific-btn--xs"
                  />
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      {(byLevel.basico || byLevel.intermediario || byLevel.avancadoOuIc) && (
        <div className="scientific-level-picks">
          <span className="scientific-level-picks-label">Por nível:</span>
          {byLevel.basico && (
            <button type="button" className="scientific-tag scientific-tag--sm" onClick={() => handleLevelFilter('basico')}>
              Básico
            </button>
          )}
          {byLevel.intermediario && (
            <button
              type="button"
              className="scientific-tag scientific-tag--sm"
              onClick={() => handleLevelFilter('intermediario')}
            >
              Intermediário
            </button>
          )}
          {byLevel.avancadoOuIc && (
            <button
              type="button"
              className="scientific-tag scientific-tag--sm"
              onClick={() => handleLevelFilter('avancado')}
            >
              Avançado/IC
            </button>
          )}
        </div>
      )}

      <div className="scientific-project-toolbar">
        <input
          type="search"
          className="scientific-search-input"
          placeholder="Buscar ideias…"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setIdeasLimit(IDEAS_PAGE);
          }}
          aria-label="Buscar ideias de projeto"
        />
        <label className="scientific-filter-select-label">
          Área
          <select
            value={interestFilter}
            onChange={(e) => {
              setInterestFilter(e.target.value);
              setIdeasLimit(IDEAS_PAGE);
            }}
          >
            <option value="">Todas</option>
            {interestOptions.map((o) => (
              <option key={o.id} value={o.id}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="scientific-level-filters" role="group" aria-label="Filtrar por nível">
        {levelFilters.map((f) => (
          <button
            key={f.id}
            type="button"
            className={`scientific-tag scientific-tag--toggle ${levelFilter === f.id ? 'scientific-tag--on' : ''}`}
            aria-pressed={levelFilter === f.id}
            onClick={() => handleLevelFilter(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <p className="scientific-card-meta">
        {displayed.length} de {rankedFull.totalMatched} ideias compatíveis
      </p>

      {displayed.length === 0 ? (
        <p className="scientific-empty-hint">
          {activeInterests.length === 0
            ? 'Selecione interesses para ver projetos.'
            : 'Nenhum projeto neste filtro. Tente outro nível ou limpe a busca.'}
        </p>
      ) : (
        <div className="scientific-ideas-grid">
          {displayed.map((idea) => (
            <IdeaCard key={idea.id} idea={idea} />
          ))}
        </div>
      )}

      {hasMoreIdeas && (
        <button
          type="button"
          className="scientific-btn scientific-btn-secondary"
          onClick={() => {
            setIdeasLimit((n) => n + IDEAS_PAGE);
            logScientificWorkspace('button_click', { action: 'ideas_show_more' });
          }}
        >
          Ver mais ideias ({rankedFull.items.length - ideasLimit} restantes)
        </button>
      )}

      {professorQuestions.length > 0 && (
        <div className="scientific-professor-questions-block">
          <h3 className="scientific-professor-questions-title">Perguntas para professor</h3>
          <ul className="scientific-professor-questions-list">
            {professorQuestions.slice(0, 8).map((q) => (
              <li key={`${q.interestId}-${q.question}`} className="scientific-professor-question-card">
                <span className="scientific-tag scientific-tag--sm">{q.label}</span>
                <p className="scientific-professor-question-text">{q.question}</p>
                <ScientificSaveButton
                  entry={notebookEntryFromProfessorQuestion(q)}
                  label="Salvar pergunta no caderno"
                  action="save_professor_question"
                  variant="secondary"
                  size="scientific-btn--xs"
                />
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
