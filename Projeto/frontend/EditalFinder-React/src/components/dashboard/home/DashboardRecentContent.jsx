import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import EmptyOrErrorState from '../../common/EmptyOrErrorState';
import DashboardEmptyState from './DashboardEmptyState';
import { classifyContentScope } from '../../../utils/dashboard/dashboardClassification';

const LIMIT = 5;

const CONTENT_SCOPE_OPTIONS = [
  { id: 'all', label: 'Todos' },
  { id: 'brasil', label: 'Brasil' },
  { id: 'internacional', label: 'Internacional' },
];

function itemTitle(item) {
  return item.titulo || item.title || item.nome || 'Sem título';
}

function itemDate(item) {
  const raw = item.data_publicacao || item.publicado_em || item.atualizado_em;
  if (!raw) return '';
  try {
    return new Date(raw).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return String(raw);
  }
}

function itemSource(item) {
  return (
    item.fonte ||
    item.source ||
    item.orgao ||
    item.instituicao ||
    item.publisher ||
    ''
  );
}

function itemTag(item) {
  return item.categoria || item.area || item.tipo || item.disciplina || '';
}

function pickDefaultContentScope(items) {
  const list = Array.isArray(items) ? items : [];
  let br = 0;
  for (const item of list) {
    if (classifyContentScope(item) === 'brasil') br += 1;
  }
  if (br >= Math.max(3, Math.floor(list.length * 0.2))) return 'brasil';
  return 'all';
}

export default function DashboardRecentContent({
  title,
  items = [],
  loading,
  error,
  moreLink,
  pagina,
  sectionKey,
  onRetry,
  emptyTitle,
}) {
  const defaultScope = useMemo(() => pickDefaultContentScope(items), [items]);
  const [scope, setScope] = useState(defaultScope);

  const counts = useMemo(() => {
    let br = 0;
    let intl = 0;
    for (const item of items) {
      const s = classifyContentScope(item);
      if (s === 'brasil') br += 1;
      if (s === 'internacional') intl += 1;
    }
    return { br, intl, total: items.length };
  }, [items]);

  const filtered = useMemo(() => {
    if (scope === 'all') return items;
    return items.filter((item) => classifyContentScope(item) === scope);
  }, [items, scope]);

  const visible = filtered.slice(0, LIMIT);
  const predominanceNote =
    scope === 'all' && counts.intl > counts.br * 2 && counts.total > 5
      ? 'Predominância internacional na base atual.'
      : null;

  return (
    <div className="home-dash-panel home-dash-list-panel">
      <div className="home-dash-panel-head">
        <h3 className="home-dash-panel-title">{title}</h3>
        {moreLink && (
          <Link to={moreLink} className="home-dash-panel-link">
            Ver todos
          </Link>
        )}
      </div>
      <div className="home-dash-content-scope" role="group" aria-label={`Filtro ${title}`}>
        {CONTENT_SCOPE_OPTIONS.map((opt) => (
          <button
            key={opt.id}
            type="button"
            className={`home-dash-scope-chip home-dash-scope-chip--sm ${scope === opt.id ? 'home-dash-scope-chip--active' : ''}`}
            onClick={() => setScope(opt.id)}
            aria-pressed={scope === opt.id}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {predominanceNote && (
        <p className="home-dash-content-scope-note">{predominanceNote}</p>
      )}
      {error ? (
        <EmptyOrErrorState
          title={`Não foi possível carregar ${title.toLowerCase()}.`}
          message={error?.message || 'Tente novamente.'}
          origem="dashboard"
          pagina={pagina}
          acao={`load_${sectionKey}`}
          componente="DashboardRecentContent"
          error={error}
          onRetry={onRetry}
        />
      ) : loading ? (
        <p className="home-dash-muted">Carregando…</p>
      ) : !visible.length ? (
        <DashboardEmptyState
          title={
            scope === 'brasil'
              ? 'Nenhum item nacional recente neste recorte.'
              : scope === 'internacional'
                ? 'Nenhum item internacional recente neste recorte.'
                : emptyTitle
          }
          message={
            scope !== 'all'
              ? 'Altere o filtro para Todos ou cadastre mais conteúdo.'
              : undefined
          }
        />
      ) : (
        <ul className="home-dash-content-list home-dash-content-list--rich">
          {visible.map((item, i) => {
            const src = itemSource(item);
            const tag = itemTag(item);
            const date = itemDate(item);
            const itemScope = classifyContentScope(item);
            const scopeLabel =
              itemScope === 'brasil'
                ? 'Brasil'
                : itemScope === 'internacional'
                  ? 'Internacional'
                  : null;
            return (
              <li key={item.id || item.id_noticia || item.id_pesquisa || i} className="home-dash-content-row">
                <div className="home-dash-content-row-main">
                  <span className="home-dash-content-title">{itemTitle(item)}</span>
                  <div className="home-dash-content-tags">
                    {date && <span className="home-dash-badge home-dash-badge--date">{date}</span>}
                    {src && (
                      <span className="home-dash-badge home-dash-badge--muted">{src}</span>
                    )}
                    {tag && <span className="home-dash-badge home-dash-badge--info">{tag}</span>}
                    {scopeLabel && (
                      <span
                        className={`home-dash-badge home-dash-badge--scope home-dash-badge--scope-${itemScope}`}
                      >
                        {scopeLabel}
                      </span>
                    )}
                  </div>
                </div>
                {moreLink && (
                  <Link to={moreLink} className="home-dash-content-open">
                    Ver
                  </Link>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
