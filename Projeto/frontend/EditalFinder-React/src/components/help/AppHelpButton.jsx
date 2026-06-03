import { useAppHelpOptional } from '../../contexts/AppHelpContext';

/**
 * Botão global de Ajuda (header e menu).
 * @param {{ variant?: 'header' | 'menu' | 'icon'; className?: string; sectionId?: string }} props
 */
export default function AppHelpButton({
  variant = 'header',
  className = '',
  sectionId,
  label = 'Ajuda',
}) {
  const help = useAppHelpOptional();
  if (!help) return null;

  const handleClick = () => {
    if (sectionId) help.openHelp(sectionId);
    else help.openHelp('getting-started');
  };

  if (variant === 'icon') {
    return (
      <button
        type="button"
        className={`app-help-btn app-help-btn--icon ${className}`.trim()}
        onClick={handleClick}
        aria-label="Abrir ajuda e tutorial"
        title="Ajuda"
      >
        ?
      </button>
    );
  }

  if (variant === 'menu') {
    return (
      <button
        type="button"
        role="menuitem"
        className={`app-nav-link app-nav-link--button ${className}`.trim()}
        onClick={handleClick}
      >
        {label}
      </button>
    );
  }

  return (
    <button
      type="button"
      className={`btn-logout app-help-btn-header ${className}`.trim()}
      onClick={handleClick}
      aria-label="Abrir ajuda e tutorial"
    >
      {label}
    </button>
  );
}
