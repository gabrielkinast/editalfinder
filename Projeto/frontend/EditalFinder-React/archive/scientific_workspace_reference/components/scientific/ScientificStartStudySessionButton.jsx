import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';

export default function ScientificStartStudySessionButton({
  studyBlocks = [],
  activeInterests = [],
  goalRoutes = [],
  notebookItems = [],
  initial = {},
  label = 'Iniciar sessão de estudo',
  variant = 'secondary',
  size = '',
}) {
  const ctx = useScientificWorkspace();
  const { openStudySessionModal } = ctx;

  return (
    <button
      type="button"
      className={`scientific-btn scientific-btn-${variant} ${size}`.trim()}
      onClick={() =>
        openStudySessionModal?.({
          ...initial,
          studyBlocks,
          activeInterests: initial.activeInterests || activeInterests,
          goalRoutes: initial.goalRoutes || goalRoutes,
          notebookItems: initial.notebookItems || notebookItems || ctx.notebookItems,
        })
      }
    >
      {label}
    </button>
  );
}
