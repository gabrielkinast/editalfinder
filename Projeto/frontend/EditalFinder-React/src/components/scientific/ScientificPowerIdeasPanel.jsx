import { useMemo, useState } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { matchesStudyProgressFilter } from '../../utils/scientific/buildStudyProgressSummary';
import { notebookEntryFromPowerIdea } from '../../utils/scientific/notebookEntryFromPowerIdea';
import {
  POWER_IDEA_LEVEL_LABELS,
  POWER_IDEA_TYPE_LABELS,
} from '../../utils/scientific/scientificPowerIdeasHelpers';
import { buildPowerIdeaProgressKey } from '../../utils/scientific/scientificStudyProgressKeys';
import { highlightTextParts } from '../../utils/scientific/searchStudyPathBlocks';
import ScientificSaveButton from './ScientificSaveButton';
import ScientificStudyProgressSelect from './ScientificStudyProgressSelect';

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

/**
 * @param {object} props
 * @param {object} props.block — bloco de trilha profunda
 * @param {string} [props.searchQ]
 * @param {string} [props.progressFilter]
 */
export default function ScientificPowerIdeasPanel({ block, searchQ = '', progressFilter = '' }) {
  const { getStudyProgressStatus } = useScientificWorkspace();
  const [levelFilter, setLevelFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const canonicalKey = block.canonicalKey || block.interestId;
  const ideas = block.powerIdeas || block.deep?.powerIdeas || [];
  const q = searchQ.trim().toLowerCase();

  const filtered = useMemo(() => {
    return ideas.filter((idea) => {
      if (levelFilter && idea.level !== levelFilter) return false;
      if (typeFilter && idea.type !== typeFilter) return false;
      const progressKey = buildPowerIdeaProgressKey(canonicalKey, idea);
      if (progressFilter && !matchesStudyProgressFilter(getStudyProgressStatus(progressKey), progressFilter)) {
        return false;
      }
      if (!q) return true;
      const blob = [
        idea.title,
        idea.type,
        idea.level,
        idea.whyItMatters,
        idea.shortExplanation,
        ...(idea.useFor || []),
        ...(idea.prerequisites || []),
        ...(idea.relatedTopics || []),
        ...(idea.projectIdeas || []),
        ...(idea.professorQuestions || []),
      ]
        .join(' ')
        .toLowerCase();
      return blob.includes(q);
    });
  }, [ideas, levelFilter, typeFilter, progressFilter, q, canonicalKey, getStudyProgressStatus]);

  const levels = useMemo(() => [...new Set(ideas.map((i) => i.level).filter(Boolean))], [ideas]);
  const types = useMemo(() => [...new Set(ideas.map((i) => i.type).filter(Boolean))], [ideas]);

  if (!ideas.length) {
    return <p className="scientific-muted">Nenhuma ideia poderosa catalogada para esta área.</p>;
  }

  return (
    <div className="scientific-power-ideas-panel">
      <div className="scientific-power-ideas-filters">
        <label>
          Nível
          <select
            className="scientific-search-input"
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
          >
            <option value="">Todos</option>
            {levels.map((lvl) => (
              <option key={lvl} value={lvl}>
                {POWER_IDEA_LEVEL_LABELS[lvl] || lvl}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tipo
          <select
            className="scientific-search-input"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="">Todos</option>
            {types.map((t) => (
              <option key={t} value={t}>
                {POWER_IDEA_TYPE_LABELS[t] || t}
              </option>
            ))}
          </select>
        </label>
      </div>

      {filtered.length === 0 ? (
        <p className="scientific-muted">Nenhuma ideia corresponde aos filtros.</p>
      ) : (
        <ul className="scientific-power-ideas-list">
          {filtered.map((idea) => {
            const progressKey = buildPowerIdeaProgressKey(canonicalKey, idea);
            const status = getStudyProgressStatus(progressKey);
            return (
              <li key={idea.id} className="scientific-power-idea-card">
                <div className="scientific-power-idea-card-head">
                  <div className="scientific-power-idea-card-titles">
                    <strong className="scientific-power-idea-title">
                      {q && matchesQuery(idea.title, q) ? (
                        <HighlightedText text={idea.title} query={q} />
                      ) : (
                        idea.title
                      )}
                    </strong>
                    <span className="scientific-tag scientific-tag--sm">
                      {POWER_IDEA_TYPE_LABELS[idea.type] || idea.type}
                    </span>
                    <span className="scientific-tag scientific-tag--sm scientific-tag--muted">
                      {POWER_IDEA_LEVEL_LABELS[idea.level] || idea.level}
                    </span>
                  </div>
                  <ScientificStudyProgressSelect
                    progressKey={progressKey}
                    itemMeta={{
                      canonicalKey,
                      kind: 'powerIdea',
                      title: idea.title,
                      areaLabel: block.label,
                      level: idea.level,
                      itemType: idea.type,
                      relatedTopics: idea.relatedTopics,
                      whyItMatters: idea.whyItMatters,
                      shortExplanation: idea.shortExplanation,
                    }}
                  />
                </div>
                <p className="scientific-power-idea-why">
                  {q && matchesQuery(idea.whyItMatters, q) ? (
                    <HighlightedText text={idea.whyItMatters} query={q} />
                  ) : (
                    idea.whyItMatters
                  )}
                </p>
                <details className="scientific-power-idea-details">
                  <summary>Ver explicação e detalhes</summary>
                  <p className="scientific-muted">{idea.shortExplanation}</p>
                  {idea.useFor?.length > 0 && (
                    <>
                      <p className="scientific-route-label">Usado para</p>
                      <ul className="scientific-study-ul">
                        {idea.useFor.map((u) => (
                          <li key={u}>{u}</li>
                        ))}
                      </ul>
                    </>
                  )}
                  {idea.prerequisites?.length > 0 && (
                    <>
                      <p className="scientific-route-label">Pré-requisitos</p>
                      <ul className="scientific-study-ul">
                        {idea.prerequisites.map((p) => (
                          <li key={p}>{p}</li>
                        ))}
                      </ul>
                    </>
                  )}
                  {idea.relatedTopics?.length > 0 && (
                    <>
                      <p className="scientific-route-label">Tópicos relacionados</p>
                      <p className="scientific-muted">{idea.relatedTopics.join(' · ')}</p>
                    </>
                  )}
                  {idea.projectIdeas?.length > 0 && (
                    <>
                      <p className="scientific-route-label">Projetos sugeridos</p>
                      <ul className="scientific-study-ul">
                        {idea.projectIdeas.map((p) => (
                          <li key={p}>{p}</li>
                        ))}
                      </ul>
                    </>
                  )}
                  {idea.professorQuestions?.length > 0 && (
                    <>
                      <p className="scientific-route-label">Perguntas ao professor</p>
                      <ul className="scientific-study-ul">
                        {idea.professorQuestions.map((pq) => (
                          <li key={pq}>{pq}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </details>
                <ScientificSaveButton
                  entry={notebookEntryFromPowerIdea({
                    idea,
                    canonicalKey,
                    areaLabel: block.label,
                    studyProgressStatus: status,
                  })}
                  label="Salvar no caderno"
                  action="save_power_idea"
                  variant="secondary"
                  size="scientific-btn--xs"
                />
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
