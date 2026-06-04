import { useAppHelpOptional } from '../../contexts/AppHelpContext';

/**
 * Link discreto “?” em páginas — abre o tutorial na seção indicada.
 */
export default function HelpPageLink({ sectionId, label = 'Ajuda nesta página' }) {
  const help = useAppHelpOptional();
  if (!help || !sectionId) return null;

  return (
    <button
      type="button"
      className="app-help-page-link"
      onClick={() => help.openHelp(sectionId)}
      aria-label={label}
    >
      <span className="app-help-page-link-icon" aria-hidden="true">
        ?
      </span>
      <span className="app-help-page-link-text">{label}</span>
    </button>
  );
}
