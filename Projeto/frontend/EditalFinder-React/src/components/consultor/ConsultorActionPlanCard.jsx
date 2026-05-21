import { useCallback, useEffect, useMemo, useState } from 'react';
import { buildConsultorActionPlan } from '../../utils/consultor/buildConsultorActionPlan';
import {
  applyActionPlanDoneState,
  loadActionPlanDone,
  saveActionPlanDone,
  toggleActionPlanDoneEntry,
} from '../../utils/consultor/consultorActionPlanStorage';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';

const PRIORITY_LABEL = {
  alta: 'Alta',
  media: 'Média',
  baixa: 'Baixa',
};

const VISIBLE_LIMIT = 5;

/**
 * Card “Plano de ação do consultor” — checklist derivado do estado do Workspace.
 */
export default function ConsultorActionPlanCard({
  cliente = null,
  profileCompleteness = 0,
  hasBriefing = false,
  selectedOpportunities = [],
  topMatches = [],
  precadSummary = null,
  deadlineSummary = null,
  canAct = true,
  onOpenBriefing,
  onOpenClientForm,
  onOpenPortfolio,
  onOpenPreProject,
  onOpenTriageReport,
  onGeneratePreProjectFromSelection,
}) {
  const [showAll, setShowAll] = useState(false);
  const [doneEntries, setDoneEntries] = useState([]);

  const clienteId = cliente?.id_cliente ?? cliente?.id ?? null;

  useEffect(() => {
    setShowAll(false);
    setDoneEntries(loadActionPlanDone(clienteId));
  }, [clienteId]);

  const baseActions = useMemo(
    () =>
      buildConsultorActionPlan({
        cliente,
        profileCompleteness,
        hasBriefing,
        selectedOpportunities,
        topMatches,
        precadSummary,
        deadlineSummary,
      }),
    [
      cliente,
      profileCompleteness,
      hasBriefing,
      selectedOpportunities,
      topMatches,
      precadSummary,
      deadlineSummary,
    ],
  );

  const actions = useMemo(
    () => applyActionPlanDoneState(baseActions, doneEntries),
    [baseActions, doneEntries],
  );

  useEffect(() => {
    if (!clienteId) return;
    logConsultorWorkspace('action_plan_generated', {
      id_cliente: clienteId,
      count: actions.length,
      pending: actions.filter((a) => a.status !== 'concluida').length,
    });
  }, [clienteId, actions]);

  const persistDone = useCallback(
    (next) => {
      setDoneEntries(next);
      saveActionPlanDone(clienteId, next);
    },
    [clienteId],
  );

  const runAction = useCallback(
    (action) => {
      if (!canAct && action.actionType !== 'open_portfolio') return;
      logConsultorWorkspace('action_plan_item_click', {
        id_cliente: clienteId,
        action_id: action.id,
        action_type: action.actionType,
      });
      switch (action.actionType) {
        case 'open_briefing':
          onOpenBriefing?.();
          break;
        case 'open_client_form':
          onOpenClientForm?.();
          break;
        case 'open_portfolio':
          onOpenPortfolio?.();
          break;
        case 'open_triage_report':
          onOpenTriageReport?.();
          break;
        case 'open_preproject':
          if (
            action.id === 'generate_preproject' &&
            selectedOpportunities.length > 0 &&
            onGeneratePreProjectFromSelection
          ) {
            onGeneratePreProjectFromSelection();
          } else {
            onOpenPreProject?.();
          }
          break;
        default:
          break;
      }
    },
    [
      canAct,
      clienteId,
      onOpenBriefing,
      onOpenClientForm,
      onOpenPortfolio,
      onOpenTriageReport,
      onOpenPreProject,
      onGeneratePreProjectFromSelection,
      selectedOpportunities.length,
    ],
  );

  const handleToggleDone = useCallback(
    (action) => {
      const isDone = action.status === 'concluida';
      const nextDone = !isDone;
      const next = toggleActionPlanDoneEntry(doneEntries, action.id, action.reopenKey, nextDone);
      persistDone(next);
      if (nextDone) {
        logConsultorWorkspace('action_plan_item_done', {
          id_cliente: clienteId,
          action_id: action.id,
        });
      } else {
        logConsultorWorkspace('action_plan_item_reopened', {
          id_cliente: clienteId,
          action_id: action.id,
        });
      }
    },
    [doneEntries, persistDone, clienteId],
  );

  if (!cliente) return null;

  const visibleActions = showAll ? actions : actions.slice(0, VISIBLE_LIMIT);
  const hasMore = actions.length > VISIBLE_LIMIT;
  const allClear = actions.length === 0 || actions.every((a) => a.status === 'concluida');

  return (
    <section className="consultor-section consultor-section--action-plan consultor-placeholder-card consultor-action-plan-card">
      <div className="consultor-section-head">
        <div>
          <h3 className="consultor-section-title consultor-placeholder-title">Plano de ação do consultor</h3>
          <p className="consultor-section-sub consultor-placeholder-desc">
            Próximos passos sugeridos com base no perfil, carteira, seleção e pré-projeto.
          </p>
        </div>
      </div>

      {allClear ? (
        <p className="consultor-action-plan-empty">
          Tudo pronto para a próxima conversa com o cliente.
        </p>
      ) : (
        <ul className="consultor-action-plan-list">
          {visibleActions.map((action) => (
            <li
              key={action.id}
              className={`consultor-action-plan-item consultor-action-plan-item--${action.status}`}
            >
              <div className="consultor-action-plan-item-head">
                <span
                  className={`consultor-action-plan-priority consultor-action-plan-priority--${action.priority}`}
                >
                  {PRIORITY_LABEL[action.priority] || action.priority}
                </span>
                <span className="consultor-action-plan-status">
                  {action.status === 'concluida'
                    ? 'Concluída'
                    : action.status === 'em_andamento'
                      ? 'Em andamento'
                      : 'Pendente'}
                </span>
              </div>
              <p className="consultor-action-plan-title">{action.title}</p>
              {action.description ? (
                <p className="consultor-action-plan-desc">{action.description}</p>
              ) : null}
              <div className="consultor-action-plan-item-actions">
                {action.status !== 'concluida' ? (
                  <button
                    type="button"
                    className="btn-view consultor-action-plan-cta"
                    onClick={() => runAction(action)}
                    disabled={!canAct && action.actionType !== 'open_portfolio'}
                  >
                    {action.actionLabel}
                  </button>
                ) : null}
                <button
                  type="button"
                  className="btn-detalhes dash-action-outline consultor-action-plan-done-btn"
                  onClick={() => handleToggleDone(action)}
                  aria-pressed={action.status === 'concluida'}
                >
                  {action.status === 'concluida' ? 'Reabrir' : 'Concluir'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {hasMore && !allClear ? (
        <button
          type="button"
          className="consultor-action-plan-show-all"
          onClick={() => setShowAll((v) => !v)}
        >
          {showAll ? 'Mostrar menos' : `Ver todas as ações (${actions.length})`}
        </button>
      ) : null}
    </section>
  );
}
