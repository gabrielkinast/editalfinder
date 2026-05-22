import { useEffect, useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import { SCIENTIFIC_INTERESTS } from '../../utils/scientific/scientificInterestsConfig';
import { PROJECT_LEVELS } from '../../utils/scientific/scientificProjectLevels';
import {
  NOTEBOOK_GROUP_FILTER_OPTIONS,
  NOTEBOOK_DISPLAY_GROUPS,
  getNotebookDisplayGroup,
} from '../../utils/scientific/scientificNotebookGroups';
import { displayScientificTitle } from '../../utils/scientific/cleanScientificTitle';
import { notebookDisplayTag } from '../../utils/scientific/notebookDisplayTag';
import { getScientificNotebookEntryKey } from '../../utils/scientific/getScientificNotebookEntryKey';
import { scientificButtonClick } from '../../utils/scientific/scientificButtonClick';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

function interestLabel(id) {
  return SCIENTIFIC_INTERESTS.find((i) => i.id === id)?.label || id.replace(/_/g, ' ');
}

export default function ScientificNotebookModal({
  open,
  onClose,
  items = [],
  onRemove,
  onUpdateNotes,
}) {
  const [filterInterest, setFilterInterest] = useState('');
  const [filterGroup, setFilterGroup] = useState('');
  const [filterLevel, setFilterLevel] = useState('');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    if (open) {
      scientificButtonClick({ action: 'modal_open', label: 'Caderno completo' });
      logScientificWorkspace('modal_open', { count: items.length });
    }
  }, [open, items.length]);

  const handleClose = () => {
    scientificButtonClick({ action: 'modal_close' });
    logScientificWorkspace('modal_close', {});
    onClose?.();
  };

  const uniqueItems = useMemo(() => {
    const map = new Map();
    for (const item of items) {
      const key = getScientificNotebookEntryKey(item);
      if (!map.has(key)) map.set(key, item);
    }
    return [...map.values()];
  }, [items]);

  const interesses = useMemo(
    () => [...new Set(uniqueItems.flatMap((i) => i.interesses || []))],
    [uniqueItems],
  );

  const groupCounts = useMemo(() => {
    const counts = Object.fromEntries(NOTEBOOK_DISPLAY_GROUPS.map((g) => [g.id, 0]));
    for (const item of uniqueItems) {
      const g = getNotebookDisplayGroup(item);
      if (counts[g] != null) counts[g] += 1;
    }
    return counts;
  }, [uniqueItems]);

  const filtered = useMemo(() => {
    const q = searchText.trim().toLowerCase();
    return uniqueItems.filter((i) => {
      if (filterGroup && getNotebookDisplayGroup(i) !== filterGroup) return false;
      if (filterLevel && i.level !== filterLevel) return false;
      if (filterInterest && !(i.interesses || []).includes(filterInterest)) return false;
      if (q) {
        const blob = [
          i.titulo,
          i.title,
          i.resumo,
          i.notes,
          i.fonte,
          ...(i.conceitos || []),
          ...(i.projetos || []),
        ]
          .join(' ')
          .toLowerCase();
        if (!blob.includes(q)) return false;
      }
      return true;
    });
  }, [uniqueItems, filterInterest, filterGroup, filterLevel, searchText]);

  if (!open) return null;

  return (
    <Modal onClose={handleClose} className="scientific-notebook-modal">
      <div className="scientific-notebook-modal-inner">
        <div className="modal-header scientific-notebook-modal-header">
          <h2>Caderno científico completo</h2>
          <p className="scientific-muted">{filtered.length} de {uniqueItems.length} itens</p>
        </div>

        <div className="scientific-notebook-group-counts">
          {NOTEBOOK_DISPLAY_GROUPS.map((g) =>
            groupCounts[g.id] > 0 ? (
              <span key={g.id} className="scientific-tag scientific-tag--sm">
                {g.label}: {groupCounts[g.id]}
              </span>
            ) : null,
          )}
        </div>

        <div className="scientific-notebook-filters scientific-notebook-filters--modal">
          <label className="scientific-notebook-search-label">
            Buscar no caderno
            <input
              type="search"
              className="scientific-search-input"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Título, notas, conceitos…"
            />
          </label>
          <label>
            Grupo
            <select
              value={filterGroup}
              onChange={(e) => {
                setFilterGroup(e.target.value);
                logScientificWorkspace('notebook_group_filter_changed', { group: e.target.value || 'all' });
              }}
            >
              {NOTEBOOK_GROUP_FILTER_OPTIONS.map((o) => (
                <option key={o.id || 'all'} value={o.id}>
                  {o.label}
                  {o.id && groupCounts[o.id] != null ? ` (${groupCounts[o.id]})` : ''}
                </option>
              ))}
            </select>
          </label>
          <label>
            Nível
            <select value={filterLevel} onChange={(e) => setFilterLevel(e.target.value)}>
              <option value="">Todos</option>
              {PROJECT_LEVELS.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Interesse
            <select value={filterInterest} onChange={(e) => setFilterInterest(e.target.value)}>
              <option value="">Todos</option>
              {interesses.map((id) => (
                <option key={id} value={id}>
                  {interestLabel(id)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="scientific-notebook-modal-body">
          <ul className="scientific-notebook-modal-list">
            {filtered.length === 0 && (
              <li className="scientific-muted">Nenhum item com esses filtros.</li>
            )}
            {filtered.map((item) => {
              const { title, titleFull } = displayScientificTitle(item);
              return (
                <li key={item.id} className="scientific-notebook-modal-item">
                  <div className="scientific-notebook-item-head">
                    <strong className="scientific-text-clamp-2" title={titleFull}>
                      {title}
                    </strong>
                    <span className="scientific-notebook-display-tag">{notebookDisplayTag(item)}</span>
                  </div>
                  {item.fonte && <p className="scientific-muted">Fonte: {item.fonte}</p>}
                  {item.tools?.length > 0 && (
                    <details className="scientific-notebook-modal-details">
                      <summary>Ferramentas</summary>
                      <p className="scientific-muted">{item.tools.join(' · ')}</p>
                    </details>
                  )}
                  {item.nextSteps?.length > 0 && (
                    <details className="scientific-notebook-modal-details">
                      <summary>Próximos passos</summary>
                      <ol className="scientific-study-ol">
                        {item.nextSteps.map((s) => (
                          <li key={s}>{s}</li>
                        ))}
                      </ol>
                    </details>
                  )}
                  {item.resumo && <p className="scientific-feed-resumo">{item.resumo}</p>}
                  <label className="scientific-note-label">
                    Anotação
                    <textarea
                      className="scientific-note-textarea"
                      rows={3}
                      value={item.notes || ''}
                      placeholder="Notas curtas sobre este item…"
                      onChange={(e) => onUpdateNotes?.(item.id, e.target.value)}
                    />
                  </label>
                  <div className="scientific-notebook-modal-actions">
                    {item.link ? (
                      <a
                        href={item.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="scientific-btn scientific-btn-ghost"
                      >
                        Abrir fonte
                      </a>
                    ) : null}
                    <button
                      type="button"
                      className="scientific-btn scientific-btn-secondary"
                      onClick={() => {
                        scientificButtonClick({ action: 'remove_notebook_item', itemId: item.id });
                        onRemove?.(item.id);
                      }}
                    >
                      Remover
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </Modal>
  );
}
