import { useMemo, useState } from 'react';
import ScientificNotebookModal from './ScientificNotebookModal';
import { displayScientificTitle } from '../../utils/scientific/cleanScientificTitle';
import { notebookDisplayTag } from '../../utils/scientific/notebookDisplayTag';
import { buildNotebookPreview } from '../../utils/scientific/buildNotebookPreview';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { SCIENTIFIC_TOAST_MESSAGES } from '../../utils/scientific/showScientificToast';
import { scientificButtonClick } from '../../utils/scientific/scientificButtonClick';
import ScientificSaveButton from './ScientificSaveButton';

function formatSavedAt(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  } catch {
    return '';
  }
}

export default function ScientificNotebookCard({
  items = [],
  onRemove,
  onUpdateNotes,
  routeEntry = null,
}) {
  const { showToast } = useScientificWorkspace() || {};
  const [modalOpen, setModalOpen] = useState(false);
  const isEmpty = items.length === 0;

  const previewGroups = useMemo(() => buildNotebookPreview(items), [items]);

  const openModal = () => {
    setModalOpen(true);
    scientificButtonClick({ action: 'open_notebook_modal', label: 'Ver caderno completo' });
    showToast?.(SCIENTIFIC_TOAST_MESSAGES.modalOpen, 'info');
  };

  return (
    <section
      id="scientific-notebook"
      className={`scientific-card scientific-notebook-card ${isEmpty ? 'scientific-notebook-card--empty' : ''}`}
    >
      <h2 className="scientific-card-title">Caderno científico</h2>

      {isEmpty ? (
        <div className="scientific-notebook-empty">
          <p className="scientific-empty-hint">
            Salve projetos, livros, blocos de teoria ou fontes para montar sua formação científica.
          </p>
          <div className="scientific-notebook-empty-actions">
            <button
              type="button"
              className="scientific-btn scientific-btn-secondary"
              onClick={openModal}
            >
              Ver caderno completo
            </button>
            {routeEntry && (
              <ScientificSaveButton
                entry={routeEntry}
                label="Salvar rota no caderno"
                action="save_route"
                variant="primary"
              />
            )}
          </div>
        </div>
      ) : (
        <>
          <p className="scientific-card-meta">
            Total: <strong>{items.length}</strong>
          </p>
          <div className="scientific-notebook-groups-preview">
            {previewGroups.map((g) => (
              <div key={g.id} className="scientific-notebook-group-preview">
                <span className="scientific-notebook-group-label">
                  {g.label} ({g.total})
                </span>
                <ul className="scientific-notebook-list scientific-notebook-list--compact">
                  {g.items.map((item) => {
                    const { title, titleFull } = displayScientificTitle(item);
                    return (
                      <li key={item.id} className="scientific-notebook-item scientific-notebook-item--compact">
                        <span className="scientific-feed-title scientific-text-clamp-2" title={titleFull}>
                          {title}
                        </span>
                        <span className="scientific-notebook-display-tag">{notebookDisplayTag(item)}</span>
                        <p className="scientific-muted">{formatSavedAt(item.savedAt)}</p>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </div>
          <div className="scientific-notebook-empty-actions">
            <button
              type="button"
              className="scientific-btn scientific-btn-primary"
              onClick={openModal}
            >
              Ver caderno completo
            </button>
            {routeEntry && (
              <ScientificSaveButton
                entry={routeEntry}
                label="Salvar rota no caderno"
                action="save_route"
                variant="secondary"
              />
            )}
          </div>
        </>
      )}

      <ScientificNotebookModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        items={items}
        onRemove={onRemove}
        onUpdateNotes={onUpdateNotes}
      />
    </section>
  );
}
