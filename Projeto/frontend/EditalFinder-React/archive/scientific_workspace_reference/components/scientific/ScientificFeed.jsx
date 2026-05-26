import { useMemo, useState } from 'react';
import { FEED_TYPE_LABEL } from '../../utils/scientific/scientificFeedLoader';
import { interestLabelById } from '../../utils/scientific/scientificInterestsConfig';
import { buildFeedRouteConnection } from '../../utils/scientific/buildFeedRouteConnection';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';
import ScientificSaveButton from './ScientificSaveButton';

const INITIAL_VISIBLE = 10;
const PAGE_SIZE = 10;

function formatDate(value) {
  if (!value) return null;
  try {
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return null;
    return d.toLocaleDateString('pt-BR');
  } catch {
    return null;
  }
}

function shortWhy(text) {
  if (!text) return '';
  const t = text.replace(/^Relacionado a:[^.]*\.\s*/i, '').trim();
  return t.length > 100 ? `${t.slice(0, 100)}…` : t;
}

function feedNotebookEntry(item) {
  return {
    id: `feed-${item.feedType}-${item.id}`,
    contentCategory: 'feed',
    tipo: FEED_TYPE_LABEL[item.feedType] || item.feedType,
    titulo: item.titulo,
    fonte: item.fonte,
    link: item.link,
    resumo: item.resumo,
    interesses: item.matchedInterests || [],
    feedId: item.id,
  };
}

export default function ScientificFeed({
  activeInterests = [],
  items = [],
  loading = false,
  error = null,
}) {
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE);
  const [filterType, setFilterType] = useState('');
  const [filterInterest, setFilterInterest] = useState('');
  const [filterFonte, setFilterFonte] = useState('');

  const fontes = useMemo(
    () => [...new Set(items.map((i) => i.fonte).filter(Boolean))].slice(0, 20),
    [items],
  );

  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (filterType && item.feedType !== filterType) return false;
      if (filterInterest && !(item.matchedInterests || []).includes(filterInterest)) return false;
      if (filterFonte && item.fonte !== filterFonte) return false;
      return true;
    });
  }, [items, filterType, filterInterest, filterFonte]);

  const visible = filtered.slice(0, visibleCount);
  const hasMore = filtered.length > visibleCount;

  const handleShowMore = () => {
    setVisibleCount((n) => n + PAGE_SIZE);
    logScientificWorkspace('button_click', { action: 'feed_show_more' });
    logScientificWorkspace('feed_show_more', { visible: visibleCount + PAGE_SIZE, total: filtered.length });
  };

  return (
    <section
      id="scientific-feed"
      className="scientific-card scientific-card--wide scientific-feed-section"
    >
      <h2 className="scientific-card-title">Feed científico</h2>
      <p className="scientific-card-desc">
        {filtered.length} itens relevantes · exibindo {visible.length}
      </p>

      {activeInterests.length === 0 && (
        <p className="scientific-empty-hint">Selecione interesses para personalizar o feed.</p>
      )}

      <div className="scientific-feed-filters">
        <label>
          Tipo
          <select
            value={filterType}
            onChange={(e) => {
              setFilterType(e.target.value);
              logScientificWorkspace('button_click', { action: 'feed_filter_type' });
            }}
          >
            <option value="">Todos</option>
            {Object.entries(FEED_TYPE_LABEL).map(([k, label]) => (
              <option key={k} value={k}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Interesse
          <select
            value={filterInterest}
            onChange={(e) => {
              setFilterInterest(e.target.value);
              logScientificWorkspace('button_click', { action: 'feed_filter_interest' });
            }}
          >
            <option value="">Todos</option>
            {activeInterests.map((id) => (
              <option key={id} value={id}>
                {interestLabelById(id)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Fonte
          <select
            value={filterFonte}
            onChange={(e) => {
              setFilterFonte(e.target.value);
              logScientificWorkspace('button_click', { action: 'feed_filter_fonte' });
            }}
          >
            <option value="">Todas</option>
            {fontes.map((f) => (
              <option key={f} value={f}>
                {f.length > 28 ? `${f.slice(0, 28)}…` : f}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <p className="scientific-muted">Carregando fontes…</p>}
      {error && <p className="scientific-error">{error}</p>}
      {!loading && !error && items.length === 0 && activeInterests.length > 0 && (
        <p className="scientific-empty-hint">Nenhuma fonte encontrada para seus interesses no momento.</p>
      )}
      {!loading && !error && filtered.length === 0 && items.length > 0 && (
        <p className="scientific-empty-hint">Nenhum item com esses filtros.</p>
      )}

      <ul className="scientific-feed-list scientific-feed-list--compact">
        {visible.map((item) => {
          const dateStr = formatDate(item.data);
          const why = shortWhy(item.matchReasons?.[0]);
          const routeLine = buildFeedRouteConnection(item, activeInterests);
          const typeLabel = FEED_TYPE_LABEL[item.feedType] || item.feedType;
          const entry = feedNotebookEntry(item);

          return (
            <li key={`${item.feedType}-${item.id}`} className="scientific-feed-item scientific-feed-item--compact">
              <div className="scientific-feed-item-top">
                <span className="scientific-tag">{typeLabel}</span>
                {item.matchScore > 0 && (
                  <span className="scientific-score-badge">+{item.matchScore}</span>
                )}
                {(item.matchedInterests || []).slice(0, 4).map((id) => (
                  <span key={id} className="scientific-tag scientific-tag--sm">
                    {interestLabelById(id)}
                  </span>
                ))}
              </div>
              <h3 className="scientific-feed-title">{item.titulo}</h3>
              <p className="scientific-feed-meta-inline">
                <span>{typeLabel}</span>
                {item.fonte && <span>{item.fonte}</span>}
                {dateStr && <span>{dateStr}</span>}
              </p>
              {item.resumo && (
                <p className="scientific-feed-resumo scientific-feed-resumo--short">
                  {item.resumo.length > 140 ? `${item.resumo.slice(0, 140)}…` : item.resumo}
                </p>
              )}
              {why && (
                <p className="scientific-feed-why-short">
                  <strong>Por que pode interessar:</strong> {why}
                </p>
              )}
              {routeLine && <p className="scientific-feed-route-line">{routeLine}</p>}
              <div className="scientific-feed-actions scientific-feed-actions--compact">
                <ScientificSaveButton
                  entry={entry}
                  label="Salvar fonte"
                  action="save_feed"
                  variant="secondary"
                  size="scientific-btn--xs"
                />
                {item.link ? (
                  <a
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="scientific-btn scientific-btn-ghost scientific-btn--xs"
                    onClick={() => logScientificWorkspace('button_click', { action: 'open_feed_link' })}
                  >
                    Abrir fonte
                  </a>
                ) : (
                  <span
                    className="scientific-btn scientific-btn-disabled scientific-btn--xs"
                    title="Esta fonte não possui link externo"
                  >
                    Sem link
                  </span>
                )}
              </div>
            </li>
          );
        })}
      </ul>

      {hasMore && (
        <button type="button" className="scientific-btn scientific-btn-secondary" onClick={handleShowMore}>
          Mostrar mais ({filtered.length - visible.length} restantes)
        </button>
      )}
    </section>
  );
}
