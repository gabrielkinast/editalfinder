import { useMemo, useState } from 'react';
import { buildScientificBriefing } from '../../utils/scientific/buildScientificBriefing';
import { displayScientificTitle, truncateDisplayTitle } from '../../utils/scientific/cleanScientificTitle';
import { notebookEntryFromProjectIdea } from '../../utils/scientific/notebookEntryFromProjectIdea';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { SCIENTIFIC_TOAST_MESSAGES } from '../../utils/scientific/showScientificToast';
import { scientificButtonClick } from '../../utils/scientific/scientificButtonClick';
import ScientificAiPlaceholder from './ScientificAiPlaceholder';
import ScientificSaveButton from './ScientificSaveButton';

function formatLastUpdate(ts) {
  try {
    return new Date(ts).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return 'agora';
  }
}

export default function ScientificBriefingCard({
  activeInterests = [],
  feedItems = [],
  notebookItems = [],
}) {
  const { showToast } = useScientificWorkspace() || {};
  const [refreshAt, setRefreshAt] = useState(() => Date.now());
  const [expanded, setExpanded] = useState(false);
  const [recalcNote, setRecalcNote] = useState(null);

  const briefing = useMemo(
    () =>
      buildScientificBriefing({
        activeInterests,
        feedItems,
        notebookItems,
        refreshAt,
      }),
    [activeInterests, feedItems, notebookItems, refreshAt],
  );

  const rec = briefing.recommendedProject;
  const recDisplay = rec ? displayScientificTitle(rec) : null;
  const topFeed = briefing.topItems?.[0];
  const conceitosShort = (briefing.conceitos || []).slice(0, 2).join(', ');
  const hasInterests = activeInterests.length > 0;

  const handleRecalculate = () => {
    const now = Date.now();
    setRefreshAt(now);
    setRecalcNote('Briefing recalculado com base nos interesses, caderno e feed atuais.');
    scientificButtonClick({ action: 'recalculate_briefing', label: 'Recalcular briefing' });
    showToast?.(SCIENTIFIC_TOAST_MESSAGES.briefingRecalc, 'success');
    logScientificWorkspace('briefing_recalculated', {
      interests: activeInterests.length,
      feed: feedItems.length,
      notebook: notebookItems.length,
    });
    logScientificWorkspace('briefing_recalculated_feedback', { at: now });
    window.setTimeout(() => setRecalcNote(null), 4000);
  };

  const projectMiniText = () => {
    if (!hasInterests) {
      return 'Selecione interesses para personalizar o briefing.';
    }
    if (!recDisplay) {
      return 'Selecione interesses ou salve itens no caderno para gerar um projeto recomendado.';
    }
    return truncateDisplayTitle(recDisplay.title, 52);
  };

  return (
    <section className="scientific-card scientific-briefing-compact">
      <div className="scientific-briefing-compact-head">
        <h2 className="scientific-card-title">Briefing científico</h2>
        <button
          type="button"
          className="scientific-btn scientific-btn-secondary scientific-btn--sm"
          title="Atualiza o resumo com base nos interesses, caderno e feed atuais."
          onClick={handleRecalculate}
        >
          Recalcular briefing
        </button>
      </div>

      <p className="scientific-briefing-local-hint">
        O briefing é gerado localmente a partir dos seus interesses, caderno e feed.
      </p>
      <p className="scientific-briefing-updated">
        Última atualização: <strong>{formatLastUpdate(refreshAt)}</strong>
      </p>
      {recalcNote && <p className="scientific-briefing-recalc-note">{recalcNote}</p>}
      <ScientificAiPlaceholder compact />

      <div className="scientific-briefing-mini-grid">
        <div className="scientific-briefing-mini-card">
          <span className="scientific-briefing-mini-label">Interesses</span>
          <p>
            {briefing.activeInterests?.length
              ? briefing.activeInterests.slice(0, 4).join(', ')
              : '—'}
          </p>
        </div>
        <div className="scientific-briefing-mini-card scientific-briefing-mini-card--project">
          <span className="scientific-briefing-mini-label">Projeto</span>
          {recDisplay?.badge && (
            <span className="scientific-continuation-badge scientific-continuation-badge--sm">
              {recDisplay.badge}
            </span>
          )}
          <p className="scientific-text-clamp-2" title={recDisplay?.titleFull}>
            {projectMiniText()}
          </p>
          {rec?.levelLabel && (
            <span className="scientific-level-badge scientific-level-badge--sm">{rec.levelLabel}</span>
          )}
        </div>
        <div className="scientific-briefing-mini-card">
          <span className="scientific-briefing-mini-label">Teoria da semana</span>
          <p className="scientific-text-clamp-2" title={briefing.theoryOfWeek}>
            {briefing.theoryOfWeek || conceitosShort || (hasInterests ? 'Veja a trilha' : '—')}
          </p>
        </div>
        <div className="scientific-briefing-mini-card">
          <span className="scientific-briefing-mini-label">Livro</span>
          <p className="scientific-text-clamp-2" title={briefing.bookSuggestion?.text}>
            {briefing.bookSuggestion?.text || '—'}
          </p>
        </div>
        <div className="scientific-briefing-mini-card">
          <span className="scientific-briefing-mini-label">Feed</span>
          <p>
            {topFeed
              ? truncateDisplayTitle(`[${topFeed.tipo}] ${topFeed.titulo}`, 40)
              : `${briefing.feedCount} itens`}
          </p>
        </div>
      </div>

      <details
        className="scientific-briefing-details"
        open={expanded}
        onToggle={(e) => {
          const open = e.target.open;
          setExpanded(open);
          if (open) logScientificWorkspace('briefing_expanded', {});
        }}
      >
        <summary>Ver briefing completo</summary>
        <div className="scientific-briefing-details-body">
          <ul className="scientific-briefing-lines">
            {briefing.summaryLines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>

          {briefing.suggestedRoute?.steps?.length > 0 && (
            <div className="scientific-briefing-block">
              <h3>Rota sugerida</h3>
              <ol className="scientific-study-ol">
                {briefing.suggestedRoute.steps.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ol>
            </div>
          )}

          {rec && (
            <ScientificSaveButton
              entry={notebookEntryFromProjectIdea(rec)}
              label="Salvar projeto recomendado"
              action="save_recommended_project"
              variant="secondary"
            />
          )}
        </div>
      </details>
    </section>
  );
}
