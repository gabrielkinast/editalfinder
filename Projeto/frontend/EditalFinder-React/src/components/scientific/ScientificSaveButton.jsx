import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { getScientificNotebookEntryKey } from '../../utils/scientific/getScientificNotebookEntryKey';

const FLASH_LABEL = {
  saved: 'Salvo ✓',
  updated: 'Atualizado ✓',
  unchanged: 'Já salvo',
};

export default function ScientificSaveButton({
  entry,
  label = 'Salvar no caderno',
  action = 'save_notebook',
  variant = 'secondary',
  size = '',
  className = '',
  disabled = false,
  title,
}) {
  const ctx = useScientificWorkspace(); // fallback seguro se fora do Provider
  const entryKey = getScientificNotebookEntryKey(entry);
  const flash = ctx?.getSaveFlash?.(entry);
  const inNotebook = !flash && ctx?.isInNotebook?.(entry);

  let text = label;
  if (flash) text = FLASH_LABEL[flash] || 'Salvo ✓';
  else if (inNotebook) text = 'Já salvo';

  const variantClass =
    flash === 'saved' || flash === 'updated'
      ? 'scientific-btn-success'
      : inNotebook
        ? 'scientific-btn-secondary scientific-btn-saved-idle'
        : `scientific-btn-${variant}`;

  const handleClick = () => {
    if (inNotebook && !flash) {
      ctx?.showToast?.('Item já está no caderno', 'info');
      return;
    }
    ctx?.saveToNotebook?.(entry, { action, label });
  };

  return (
    <button
      type="button"
      className={`scientific-btn ${variantClass} ${size} ${className}`.trim()}
      disabled={disabled || !ctx}
      title={title || (inNotebook ? 'Este item já está no caderno' : undefined)}
      onClick={handleClick}
    >
      {text}
    </button>
  );
}
