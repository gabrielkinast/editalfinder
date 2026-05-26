import { useMemo, useState } from 'react';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { auditScientificWorkspaceState } from '../../utils/scientific/auditScientificWorkspaceState';
import { repairScientificWorkspaceState } from '../../utils/scientific/repairScientificWorkspaceState';
import { buildScientificStudyPath } from '../../utils/scientific/buildScientificStudyPath';
import { buildScientificGoalRoutes } from '../../utils/scientific/buildScientificGoalRoutes';
import { clearScientificWorkspaceLocalCache } from '../../utils/scientific/clearScientificWorkspaceLocalCache';
import AppReportProblemButton from '../feedback/AppReportProblemButton';
/**
 * Painel DEV — diagnóstico e reparo local (Fase 2M).
 */
export default function ScientificWorkspaceDiagnosticsPanel({
  activeInterests = [],
  feedItems = [],
  notebookItems = [],
}) {
  const ctx = useScientificWorkspace();
  const [copyHint, setCopyHint] = useState('');

  const studyBlocks = useMemo(
    () =>
      buildScientificStudyPath(activeInterests, {
        feedItems,
        notebookItems,
      }),
    [activeInterests, feedItems, notebookItems],
  );

  const goalRoutes = useMemo(
    () =>
      buildScientificGoalRoutes({
        interests: activeInterests,
        studyBlocks,
      }),
    [activeInterests, studyBlocks],
  );

  const audit = useMemo(
    () =>
      auditScientificWorkspaceState({
        interests: activeInterests,
        studyBlocks,
        notebookItems,
        studyProgress: ctx.studyProgress,
        xpState: ctx.xpState,
        masteryChecks: ctx.masteryChecks,
        bookProgress: ctx.bookProgress,
        studySessions: ctx.studySessions,
        goalRoutes,
      }),
    [
      activeInterests,
      studyBlocks,
      notebookItems,
      ctx.studyProgress,
      ctx.xpState,
      ctx.masteryChecks,
      ctx.bookProgress,
      ctx.studySessions,
      goalRoutes,
    ],
  );

  if (!import.meta.env.DEV) return null;

  const feedbackContext = {
    interestsCount: audit.stats.interestsCount,
    studyBlocksCount: audit.stats.studyBlocksCount,
    notebookCount: audit.stats.notebookCount,
    progressCount: audit.stats.progressCount,
    sessionsCount: audit.stats.sessionsCount,
    auditOk: audit.ok,
    warningCount: audit.warnings.length,
    errorCount: audit.errors.length,
  };

  const handleCopy = async () => {
    const text = JSON.stringify(audit, null, 2);
    try {
      await navigator.clipboard.writeText(text);
      setCopyHint('Copiado!');
      setTimeout(() => setCopyHint(''), 2000);
    } catch {
      setCopyHint('Falha ao copiar');
    }
  };

  const handleRepair = () => {
    const ok = window.confirm(
      'Aplicar reparos seguros nos dados locais (dedup caderno, progresso/sessões inválidos)? Dados válidos são preservados.',
    );
    if (!ok) return;
    const { actions, reloadRecommended } = repairScientificWorkspaceState();
    window.alert(actions.join('\n'));
    if (reloadRecommended) {
      window.location.reload();
    }
  };

  const handleClearCache = () => {
    const ok = window.confirm(
      'Limpar TODO o cache local do Workspace Científico? Isso remove interesses, caderno, progresso, XP e sessões.',
    );
    if (!ok) return;
    clearScientificWorkspaceLocalCache();
    window.location.reload();
  };

  const statusLabel = audit.ok
    ? audit.warnings.length
      ? 'OK com avisos'
      : 'Saudável'
    : 'Com erros';

  return (
    <section className="scientific-card scientific-diagnostics-panel" aria-label="Diagnóstico DEV">
      <h2 className="scientific-card-title">Diagnóstico DEV</h2>
      <p className="scientific-muted">
        Status: <strong>{statusLabel}</strong>
        {copyHint ? ` · ${copyHint}` : ''}
      </p>

      <ul className="scientific-diagnostics-stats">
        <li>Interesses: {audit.stats.interestsCount}</li>
        <li>Trilhas: {audit.stats.studyBlocksCount}</li>
        <li>Caderno: {audit.stats.notebookCount}</li>
        <li>Progresso: {audit.stats.progressCount}</li>
        <li>Sessões: {audit.stats.sessionsCount}</li>
        <li>XP eventos: {audit.stats.xpEventsCount}</li>
        <li>Livros em andamento: {audit.stats.booksInProgressCount}</li>
      </ul>

      {audit.warnings.length > 0 && (
        <details className="scientific-diagnostics-details">
          <summary>Avisos ({audit.warnings.length})</summary>
          <ul>
            {audit.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </details>
      )}

      {audit.errors.length > 0 && (
        <details className="scientific-diagnostics-details scientific-diagnostics-details--error" open>
          <summary>Erros ({audit.errors.length})</summary>
          <ul>
            {audit.errors.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        </details>
      )}

      <div className="scientific-diagnostics-actions">
        <button
          type="button"
          className="scientific-btn scientific-btn-ghost scientific-btn--xs"
          onClick={handleCopy}
        >
          Copiar diagnóstico
        </button>
        <button
          type="button"
          className="scientific-btn scientific-btn-secondary scientific-btn--xs"
          onClick={handleRepair}
        >
          Reparar dados locais
        </button>
        <button
          type="button"
          className="scientific-btn scientific-btn-ghost scientific-btn--xs"
          onClick={handleClearCache}
        >
          Limpar cache local do Workspace
        </button>
        <AppReportProblemButton
          origem="workspace_cientifico_dev"
          pagina="Workspace Científico"
          componente="ScientificWorkspaceDiagnosticsPanel"
          acao="diagnostico_dev"
          tipo="outro"
          label="Reportar problema"
          variant="secondary"
          size="scientific-btn--xs"
          extraContext={feedbackContext}
          className="scientific-btn--xs"
        />
      </div>
    </section>
  );
}
