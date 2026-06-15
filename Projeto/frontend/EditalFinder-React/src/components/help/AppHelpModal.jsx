import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { HELP_NAV_GROUPS, filterHelpSections, getSectionById } from './helpContent';

function HelpSectionBody({ section }) {
  return (
    <article className="app-help-article">
      {section.objective && (
        <p className="app-help-lead">
          <strong>Objetivo:</strong> {section.objective}
        </p>
      )}
      {section.whenToUse && (
        <p>
          <strong>Quando usar:</strong> {section.whenToUse}
        </p>
      )}
      {section.steps?.length > 0 && (
        <>
          <h3 className="app-help-h3">Passo a passo</h3>
          <ol className="app-help-steps">
            {section.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </>
      )}
      {section.blocks?.map((block) => (
        <div key={block.title} className="app-help-block">
          <h3 className="app-help-h3">{block.title}</h3>
          <p>{block.body}</p>
        </div>
      ))}
      {section.tips?.length > 0 && (
        <>
          <h3 className="app-help-h3">Dicas</h3>
          <ul className="app-help-tips">
            {section.tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </>
      )}
      {section.commonErrors?.length > 0 && (
        <>
          <h3 className="app-help-h3">Erros comuns</h3>
          <ul className="app-help-errors">
            {section.commonErrors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </>
      )}
    </article>
  );
}

export default function AppHelpModal({ activeSectionId, onSectionChange, onClose }) {
  const [query, setQuery] = useState('');
  const titleId = useId();
  const searchRef = useRef(null);
  const section = getSectionById(activeSectionId);

  const filtered = useMemo(() => filterHelpSections(query), [query]);

  const grouped = useMemo(() => {
    const map = new Map();
    for (const g of HELP_NAV_GROUPS) map.set(g, []);
    for (const s of filtered) {
      const list = map.get(s.group) || [];
      list.push(s);
      map.set(s.group, list);
    }
    return HELP_NAV_GROUPS.map((g) => ({ label: g, items: map.get(g) || [] })).filter(
      (x) => x.items.length > 0,
    );
  }, [filtered]);

  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    searchRef.current?.focus();
    return () => {
      document.body.style.overflow = prev;
    };
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  useEffect(() => {
    if (!query) return;
    const stillVisible = filtered.some((s) => s.id === activeSectionId);
    if (!stillVisible && filtered[0]) onSectionChange(filtered[0].id);
  }, [query, filtered, activeSectionId, onSectionChange]);

  const node = (
    <div
      className="app-help-overlay"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="app-help-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="app-help-panel-header">
          <div>
            <h2 id={titleId} className="app-help-panel-title">
              Ajuda — EditalFinder
            </h2>
            <p className="app-help-panel-sub">Tutorial de uso do sistema</p>
          </div>
          <button
            type="button"
            className="app-help-close"
            onClick={onClose}
            aria-label="Fechar ajuda"
          >
            ×
          </button>
        </header>

        <div className="app-help-search-wrap">
          <label className="app-help-search-label" htmlFor="app-help-search">
            Buscar no tutorial
          </label>
          <input
            ref={searchRef}
            id="app-help-search"
            type="search"
            className="app-help-search"
            placeholder="Buscar no tutorial… (ex.: briefing, radar, prazo)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div className="app-help-body">
          <nav className="app-help-nav" aria-label="Seções do tutorial">
            {grouped.map((group) => (
              <div key={group.label} className="app-help-nav-group">
                <p className="app-help-nav-group-label">{group.label}</p>
                <ul>
                  {group.items.map((item) => (
                    <li key={item.id}>
                      <button
                        type="button"
                        className={`app-help-nav-link ${
                          item.id === activeSectionId ? 'app-help-nav-link--active' : ''
                        }`}
                        onClick={() => onSectionChange(item.id)}
                      >
                        {item.title}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            {filtered.length === 0 && (
              <p className="app-help-empty">Nenhuma seção encontrada para “{query}”.</p>
            )}
          </nav>

          <div className="app-help-content">
            <h2 className="app-help-content-title">{section.title}</h2>
            <HelpSectionBody section={section} />
          </div>
        </div>
      </div>
    </div>
  );

  if (typeof document !== 'undefined') {
    return createPortal(node, document.body);
  }
  return node;
}
