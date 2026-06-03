import { useCallback, useEffect, useMemo, useState } from 'react';
import Header from '../components/layout/Header';
import { ScientificWorkspaceProvider, useScientificWorkspace } from '../context/ScientificWorkspaceContext';
import ScientificRouteCard from '../components/scientific/ScientificRouteCard';
import ScientificSectionNav from '../components/scientific/ScientificSectionNav';
import {
  buildRouteCardSummary,
  notebookEntryFromStudyRoute,
} from '../utils/scientific/buildRouteCardSummary';
import ScientificBriefingCard from '../components/scientific/ScientificBriefingCard';
import ScientificInterestsCard from '../components/scientific/ScientificInterestsCard';
import ScientificFeed from '../components/scientific/ScientificFeed';
import ScientificNotebookCard from '../components/scientific/ScientificNotebookCard';
import ScientificProjectIdeas from '../components/scientific/ScientificProjectIdeas';
import ScientificStudyPath from '../components/scientific/ScientificStudyPath';
import ScientificAiPlaceholder from '../components/scientific/ScientificAiPlaceholder';
import ScientificToast from '../components/scientific/ScientificToast';
import ScientificWorkspaceDiagnosticsPanel from '../components/scientific/ScientificWorkspaceDiagnosticsPanel';
import AppReportProblemButton from '../components/feedback/AppReportProblemButton';
import { buildScientificStudyPath } from '../utils/scientific/buildScientificStudyPath';
import { loadScientificFeed } from '../utils/scientific/scientificFeedLoader';
import {
  loadScientificInterests,
  saveScientificInterests,
} from '../utils/scientific/scientificInterestsStorage';
import {
  loadScientificNotebook,
  removeScientificNotebookEntry,
  updateScientificNotebookNotes,
} from '../utils/scientific/scientificNotebookStorage';
import { buildScientificProjectIdeas } from '../utils/scientific/buildScientificProjectIdeas';
import { logScientificWorkspaceDebugTable } from '../utils/scientific/scientificDevDebug';

function safeLoadNotebook() {
  try {
    const items = loadScientificNotebook();
    return Array.isArray(items) ? items : [];
  } catch {
    return [];
  }
}

function safeLoadInterests() {
  try {
    const list = loadScientificInterests();
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function ScientificWorkspaceContent({ notebookItems, reloadNotebook }) {
  const safeNotebook = Array.isArray(notebookItems) ? notebookItems : [];
  const [activeInterests, setActiveInterests] = useState(() => safeLoadInterests());
  const [feedItems, setFeedItems] = useState([]);
  const [feedLoading, setFeedLoading] = useState(true);
  const ctx = useScientificWorkspace();
  const toast = ctx?.toast;
  const saveToNotebook = ctx?.saveToNotebook ?? (() => ({ status: 'unchanged' }));

  useEffect(() => {
    let cancelled = false;
    setFeedLoading(true);
    loadScientificFeed(activeInterests, { limit: 40 })
      .then((rows) => {
        if (!cancelled) setFeedItems(Array.isArray(rows) ? rows : []);
      })
      .catch(() => {
        if (!cancelled) setFeedItems([]);
      })
      .finally(() => {
        if (!cancelled) setFeedLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeInterests]);

  const handleToggleInterest = useCallback((id) => {
    setActiveInterests((prev) => {
      const base = Array.isArray(prev) ? prev : [];
      const next = base.includes(id) ? base.filter((x) => x !== id) : [...base, id];
      saveScientificInterests(next);
      return next;
    });
  }, []);

  const handleRemoveNotebook = useCallback(
    (id) => {
      removeScientificNotebookEntry(id);
      reloadNotebook();
    },
    [reloadNotebook],
  );

  const handleUpdateNotes = useCallback(
    (id, notes) => {
      updateScientificNotebookNotes(id, notes);
      reloadNotebook();
    },
    [reloadNotebook],
  );

  const routeEntry = useMemo(() => {
    try {
      return notebookEntryFromStudyRoute(
        buildRouteCardSummary({
          activeInterests,
          feedItems,
          notebookItems: safeNotebook,
        }),
        activeInterests,
      );
    } catch {
      return null;
    }
  }, [activeInterests, feedItems, safeNotebook]);

  const shared = {
    activeInterests,
    feedItems,
    notebookItems: safeNotebook,
    onSaveToNotebook: saveToNotebook,
  };

  const studyBlocksForFeedback = useMemo(
    () => buildScientificStudyPath(activeInterests, { feedItems, notebookItems: safeNotebook }),
    [activeInterests, feedItems, safeNotebook],
  );

  const feedbackStats = useMemo(
    () => ({
      interestsCount: activeInterests.length,
      studyBlocksCount: studyBlocksForFeedback.length,
      notebookCount: safeNotebook.length,
      progressCount: Object.keys(ctx?.studyProgress || {}).length,
      sessionsCount: (ctx?.studySessions || []).length,
    }),
    [activeInterests.length, studyBlocksForFeedback.length, safeNotebook.length, ctx?.studyProgress, ctx?.studySessions],
  );

  return (
    <div className="page-wrapper scientific-workspace-page">
      <Header searchPlaceholder="Buscar no app…" />
      <ScientificToast toast={toast} />
      <div className="scientific-workspace-below-header">
        <header className="scientific-hero">
          <h1>Workspace Científico</h1>
          <p>
            Sua rota de estudo e projeto: interesses, ideias por nível, trilha e fontes do EditalFinder.
          </p>
          <ScientificAiPlaceholder compact />
        </header>

        <div className="scientific-page-layout">
          <div className="scientific-page-main">
            <ScientificRouteCard {...shared} />
            <ScientificSectionNav />
            <ScientificBriefingCard {...shared} />
            <ScientificInterestsCard
              activeInterests={activeInterests}
              onToggle={handleToggleInterest}
            />
            <ScientificProjectIdeas
              activeInterests={activeInterests}
              notebookItems={safeNotebook}
            />
            <ScientificStudyPath
              activeInterests={activeInterests}
              feedItems={feedItems}
              notebookItems={safeNotebook}
            />
            <ScientificNotebookCard
              items={safeNotebook}
              onRemove={handleRemoveNotebook}
              onUpdateNotes={handleUpdateNotes}
              routeEntry={routeEntry}
            />
          </div>
        </div>

        <ScientificFeed
          activeInterests={activeInterests}
          items={feedItems}
          loading={feedLoading}
        />

        {import.meta.env.DEV && (
          <ScientificWorkspaceDiagnosticsPanel
            activeInterests={activeInterests}
            feedItems={feedItems}
            notebookItems={safeNotebook}
          />
        )}

        <footer className="scientific-workspace-footer">
          <AppReportProblemButton
            origem="workspace_cientifico"
            pagina="Workspace Científico"
            componente="ScientificWorkspace"
            acao="reportar_problema_workspace"
            tipo="outro"
            label="Reportar problema neste Workspace"
            variant="link"
            extraContext={feedbackStats}
          />
        </footer>
      </div>
    </div>
  );
}

function ScientificWorkspaceInner() {
  const [retryKey, setRetryKey] = useState(0);
  const [notebookItems, setNotebookItems] = useState(() => {
    const items = safeLoadNotebook();
    if (import.meta.env.DEV) {
      try {
        const rawIdeas = buildScientificProjectIdeas(safeLoadInterests(), items);
        logScientificWorkspaceDebugTable({
          notebookCount: items.length,
          ideasCount: rawIdeas?.length ?? 0,
        });
      } catch {
        /* debug only */
      }
    }
    return items;
  });

  const reloadNotebook = useCallback(() => {
    setNotebookItems(safeLoadNotebook());
  }, []);

  return (
    <div key={retryKey}>
      <ScientificWorkspaceProvider notebookItems={notebookItems} onNotebookChange={reloadNotebook}>
        <ScientificWorkspaceContent notebookItems={notebookItems} reloadNotebook={reloadNotebook} />
      </ScientificWorkspaceProvider>
    </div>
  );
}

export default function ScientificWorkspace() {
  return <ScientificWorkspaceInner />;
}
