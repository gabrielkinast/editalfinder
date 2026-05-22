import { useEffect, useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import { useScientificWorkspace } from '../../context/ScientificWorkspaceContext';
import { interestLabelById } from '../../utils/scientific/scientificInterestsConfig';
import { SESSION_DURATION_OPTIONS } from '../../utils/scientific/scientificStudySessionStorage';
import {
  SESSION_FOCUS_OPTIONS,
  SESSION_LEVEL_OPTIONS,
  SESSION_STATUS_OPTIONS,
  SESSION_QUANTITY_OPTIONS,
  SESSION_SOURCE_OPTIONS,
  KIND_DISPLAY_LABELS,
  SOURCE_DISPLAY_LABELS,
  FOCUS_DESCRIPTIONS,
  displaySessionItemStatus,
} from '../../utils/scientific/scientificStudySessionConstants';
import {
  getStudySessionPipeline,
  logStudySessionRecommendedSelected,
} from '../../utils/scientific/getStudySessionPipeline';
import { buildStudySessionAreaOptions, getAreaOptionLabel } from '../../utils/scientific/buildStudySessionAreaOptions';
import { resolveStudySessionModalDefaults } from '../../utils/scientific/resolveStudySessionModalDefaults';
import { formatStudySessionCounter } from '../../utils/scientific/formatStudySessionCounter';
import {
  AREA_SCOPE_ALL_ACTIVE,
  AREA_SCOPE_GOAL_ROUTE,
  isSpecialAreaScope,
} from '../../utils/scientific/studySessionAreaScope';
import { logScientificWorkspace } from '../../utils/scientific/scientificWorkspaceLog';

function SessionItemRow({ item, checked, onToggle }) {
  const kindLabel = KIND_DISPLAY_LABELS[item.kind] || item.kind;
  const sourceLabel = SOURCE_DISPLAY_LABELS[item.source] || item.source;
  const statusLabel = displaySessionItemStatus(item.status, item);
  const levelPart = item.level ? ` · ${item.level}` : '';

  return (
    <label className="scientific-session-item-pick scientific-session-item-pick--rich">
      <input type="checkbox" checked={checked} onChange={onToggle} />
      <span className="scientific-session-item-body">
        <span className="scientific-session-item-title">{item.title}</span>
        <span className="scientific-muted scientific-session-item-meta">
          {kindLabel} · {item.areaLabel || item.canonicalKey}
          {levelPart} · {statusLabel}
        </span>
        {item.subtitle && !String(item.subtitle).match(/^Lendo\s+\d+%$/i) && (
          <span className="scientific-muted scientific-session-item-sub">{item.subtitle}</span>
        )}
        <span className="scientific-muted scientific-session-item-origin">
          Origem: {sourceLabel}
        </span>
      </span>
    </label>
  );
}

export default function ScientificStudySessionModal({
  open,
  initial,
  studyBlocks = [],
  activeInterests = [],
  goalRoutes = [],
  notebookItems = [],
  onClose,
}) {
  const ctx = useScientificWorkspace();
  const [phase, setPhase] = useState('setup');
  const [areaSelection, setAreaSelection] = useState('');
  const [plannedMinutes, setPlannedMinutes] = useState(30);
  const [focus, setFocus] = useState('mixed');
  const [levelFilter, setLevelFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [originFilter, setOriginFilter] = useState('');
  const [quantity, setQuantity] = useState(10);
  const [search, setSearch] = useState('');
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [goalRouteId, setGoalRouteId] = useState(null);
  const [selectedKeys, setSelectedKeys] = useState(new Set());
  const [startedAt, setStartedAt] = useState(null);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [reflection, setReflection] = useState({
    learned: '',
    understood: '',
    confused: '',
    nextAction: '',
    professorQuestion: '',
  });
  const [saveProfessorToNotebook, setSaveProfessorToNotebook] = useState(true);

  const areaOptions = useMemo(
    () =>
      buildStudySessionAreaOptions({
        studyBlocks,
        activeInterests,
        goalRoutes,
        includeReviewOption: focus === 'review',
      }),
    [studyBlocks, activeInterests, goalRoutes, focus],
  );

  const pipeline = useMemo(
    () =>
      getStudySessionPipeline({
        studyBlocks,
        activeInterests,
        areaSelection,
        goalRoutes,
        goalRouteId,
        progressState: ctx.studyProgress,
        bookProgress: ctx.bookProgress,
        notebookItems,
        focus,
        level: levelFilter,
        status: statusFilter,
        search,
        origin: originFilter,
        quantity,
        plannedMinutes,
      }),
    [
      studyBlocks,
      activeInterests,
      areaSelection,
      goalRoutes,
      goalRouteId,
      notebookItems,
      ctx.studyProgress,
      ctx.bookProgress,
      focus,
      levelFilter,
      statusFilter,
      originFilter,
      search,
      quantity,
      plannedMinutes,
    ],
  );

  const visibleItems = pipeline.visible;
  const itemByKey = useMemo(() => {
    const m = new Map();
    for (const item of pipeline.pool) {
      m.set(item.progressKey, item);
    }
    return m;
  }, [pipeline.pool]);

  const counterCopy = useMemo(
    () =>
      formatStudySessionCounter({
        areaSelection,
        areaOptions,
        totalInScope: pipeline.poolMeta?.totalInScope ?? pipeline.totalAfter,
        distinctAreas: pipeline.poolMeta?.distinctAreas ?? 0,
        displayedCount: pipeline.displayedCount,
        selectedCount: selectedKeys.size,
      }),
    [areaSelection, areaOptions, pipeline, selectedKeys.size],
  );

  const focusDescription = FOCUS_DESCRIPTIONS[focus] || '';

  useEffect(() => {
    if (!open) return;
    setPhase('setup');
    const defaults = resolveStudySessionModalDefaults(initial);
    const firstBlockKey = studyBlocks[0]?.canonicalKey || studyBlocks[0]?.interestId || '';
    setAreaSelection(
      defaults.areaSelection ||
        initial?.canonicalKey ||
        initial?.areaSelection ||
        firstBlockKey ||
        AREA_SCOPE_ALL_ACTIVE,
    );
    setPlannedMinutes(defaults.plannedMinutes ?? initial?.plannedMinutes ?? 30);
    setFocus(defaults.focus || initial?.focus || 'mixed');
    setLevelFilter(defaults.levelFilter || initial?.levelFilter || '');
    setStatusFilter(defaults.statusFilter || '');
    setOriginFilter(initial?.originFilter || '');
    setQuantity(
      defaults.quantity ?? initial?.quantity ?? (defaults.focus === 'review' ? 0 : 10),
    );
    setSearch(initial?.search || '');
    setAdvancedOpen(false);
    setGoalRouteId(defaults.goalRouteId || initial?.goalRouteId || goalRoutes[0]?.id || null);
    const pre = initial?.selectedProgressKeys || [];
    setSelectedKeys(new Set(pre.length ? pre : []));
    setStartedAt(null);
    setElapsedSec(0);
    setReflection({
      learned: '',
      understood: '',
      confused: '',
      nextAction: '',
      professorQuestion: '',
    });
    logScientificWorkspace('study_session_modal_open', {
      areaSelection: defaults.areaSelection,
      focus: defaults.focus,
      openSource: initial?.openSource,
    });
  }, [open, initial, studyBlocks, goalRoutes]);

  useEffect(() => {
    if (!open || phase !== 'running' || !startedAt) {
      return undefined;
    }
    const t = window.setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(t);
  }, [open, phase, startedAt]);

  useEffect(() => {
    if (!open) {
      setPhase('setup');
      setStartedAt(null);
      setElapsedSec(0);
    }
  }, [open]);

  const toggleItem = (key) => {
    setSelectedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const selectRecommended = () => {
    const keys = pipeline.recommendedKeys.filter((k) => itemByKey.has(k));
    setSelectedKeys(new Set(keys));
    logStudySessionRecommendedSelected(keys.length, focus, plannedMinutes);
  };

  const selectAllVisible = () => {
    setSelectedKeys(new Set(visibleItems.map((i) => i.progressKey)));
  };

  const clearSelection = () => setSelectedKeys(new Set());

  const startSession = () => {
    setStartedAt(Date.now());
    setPhase('running');
    logScientificWorkspace('study_session_started', { areaSelection, focus, plannedMinutes });
  };

  const formatTimer = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const handleSave = () => {
    const durationMinutes = Math.max(
      plannedMinutes,
      Math.round(elapsedSec / 60) || plannedMinutes,
    );
    const selectedItems = [...selectedKeys]
      .map((key) => itemByKey.get(key))
      .filter(Boolean)
      .map((i) => ({
        progressKey: i.progressKey,
        kind: i.kind,
        title: i.title,
        level: i.level,
        statusBefore: i.status,
        statusAfter: 'estudando',
      }));

    const areaLabel = getAreaOptionLabel(areaSelection, areaOptions);
    const saveCanonicalKey = isSpecialAreaScope(areaSelection)
      ? selectedItems[0]?.canonicalKey ||
        studyBlocks[0]?.canonicalKey ||
        studyBlocks[0]?.interestId ||
        'geral'
      : areaSelection;

    let title = `Sessão — ${areaLabel}`;
    if (areaSelection === AREA_SCOPE_ALL_ACTIVE) title = 'Sessão — várias áreas ativas';
    if (areaSelection === AREA_SCOPE_GOAL_ROUTE) title = 'Sessão — rota sugerida';

    ctx.completeStudySession?.({
      title,
      canonicalKey: saveCanonicalKey,
      areaLabel,
      areaSelection,
      goalRouteId: goalRouteId || initial?.goalRouteId || null,
      plannedMinutes,
      durationMinutes,
      focus,
      startedAt: startedAt ? new Date(startedAt).toISOString() : new Date().toISOString(),
      finishedAt: new Date().toISOString(),
      selectedItems,
      reflection,
      saveProfessorToNotebook,
    });
    onClose?.();
  };

  const canStart = areaSelection && selectedKeys.size > 0;

  if (!open) return null;

  return (
    <Modal onClose={onClose} className="scientific-session-modal" portal zIndex={1220}>
      <div className="scientific-session-modal-inner scientific-session-modal-inner--wide">
        {phase === 'setup' ? (
          <header className="scientific-session-setup-header">
            <h2>O que você quer estudar agora?</h2>
            <p className="scientific-muted scientific-session-setup-sub">
              Escolha uma área, um foco e alguns itens. A sessão salva reflexão, progresso e XP.
            </p>
          </header>
        ) : (
          <h2>Sessão de estudo</h2>
        )}

        {phase === 'setup' && (
          <>
            <div className="scientific-session-filters-grid scientific-session-filters-primary">
              <label className="scientific-trail-filter-label">
                Área
                <select
                  className="scientific-search-input"
                  value={areaSelection}
                  onChange={(e) => {
                    setAreaSelection(e.target.value);
                    setSelectedKeys(new Set());
                  }}
                >
                  {areaOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="scientific-trail-filter-label">
                Duração planejada
                <select
                  className="scientific-search-input"
                  value={plannedMinutes}
                  onChange={(e) => setPlannedMinutes(Number(e.target.value))}
                >
                  {SESSION_DURATION_OPTIONS.map((d) => (
                    <option key={d.minutes} value={d.minutes}>
                      {d.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="scientific-trail-filter-label">
                Foco
                <select
                  className="scientific-search-input"
                  value={focus}
                  onChange={(e) => {
                    setFocus(e.target.value);
                    setSelectedKeys(new Set());
                  }}
                >
                  {SESSION_FOCUS_OPTIONS.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {focusDescription && (
              <p className="scientific-session-focus-hint">{focusDescription}</p>
            )}

            <div className="scientific-session-filters-grid scientific-session-filters-secondary">
              <label className="scientific-trail-filter-label">
                Nível
                <select
                  className="scientific-search-input"
                  value={levelFilter}
                  onChange={(e) => setLevelFilter(e.target.value)}
                >
                  {SESSION_LEVEL_OPTIONS.map((o) => (
                    <option key={o.id || 'all'} value={o.id}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="scientific-trail-filter-label">
                Quantidade
                <select
                  className="scientific-search-input"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                >
                  {SESSION_QUANTITY_OPTIONS.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="scientific-trail-filter-label scientific-session-search-label">
                Busca
                <input
                  type="search"
                  className="scientific-search-input"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Tópico, livro, ideia…"
                />
              </label>
            </div>

            <div className="scientific-session-advanced">
              <button
                type="button"
                className="scientific-btn scientific-btn-ghost scientific-btn--xs scientific-session-advanced-toggle"
                onClick={() => setAdvancedOpen((v) => !v)}
                aria-expanded={advancedOpen}
              >
                {advancedOpen ? '▾' : '▸'} Filtros avançados
              </button>
              {advancedOpen && (
                <div className="scientific-session-filters-grid scientific-session-filters-advanced">
                  <label className="scientific-trail-filter-label">
                    Status
                    <select
                      className="scientific-search-input"
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                    >
                      {SESSION_STATUS_OPTIONS.map((o) => (
                        <option key={o.id || 'all'} value={o.id}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="scientific-trail-filter-label">
                    Origem
                    <select
                      className="scientific-search-input"
                      value={originFilter}
                      onChange={(e) => setOriginFilter(e.target.value)}
                    >
                      {SESSION_SOURCE_OPTIONS.map((o) => (
                        <option key={o.id || 'all'} value={o.id}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              )}
            </div>

            <p className="scientific-session-counter" role="status">
              <strong>{counterCopy.headline}</strong>
              <br />
              <span className="scientific-muted">{counterCopy.sub}</span>
            </p>

            {pipeline.emptyFocusMessage && (
              <p className="scientific-empty-hint">{pipeline.emptyFocusMessage}</p>
            )}

            <div className="scientific-session-bulk-actions">
              <button
                type="button"
                className="scientific-btn scientific-btn-ghost scientific-btn--xs"
                onClick={selectRecommended}
              >
                Selecionar recomendados
              </button>
              <button
                type="button"
                className="scientific-btn scientific-btn-ghost scientific-btn--xs"
                onClick={selectAllVisible}
                disabled={!visibleItems.length}
              >
                Selecionar todos visíveis
              </button>
              <button
                type="button"
                className="scientific-btn scientific-btn-ghost scientific-btn--xs"
                onClick={clearSelection}
              >
                Limpar seleção
              </button>
            </div>

            <ul className="scientific-session-item-pick-list scientific-session-item-pick-list--tall">
              {visibleItems.map((item) => (
                <li key={item.progressKey}>
                  <SessionItemRow
                    item={item}
                    checked={selectedKeys.has(item.progressKey)}
                    onToggle={() => toggleItem(item.progressKey)}
                  />
                </li>
              ))}
            </ul>

            <div className="scientific-mastery-actions">
              <button
                type="button"
                className="scientific-btn scientific-btn-primary"
                disabled={!canStart}
                onClick={startSession}
              >
                Iniciar cronômetro
              </button>
              <button type="button" className="scientific-btn scientific-btn-ghost" onClick={onClose}>
                Cancelar
              </button>
            </div>
          </>
        )}

        {phase === 'running' && (
          <>
            <p className="scientific-session-timer">{formatTimer(elapsedSec)}</p>
            <p className="scientific-muted">
              Meta: {plannedMinutes} min ·{' '}
              {SESSION_FOCUS_OPTIONS.find((f) => f.id === focus)?.label} ·{' '}
              {getAreaOptionLabel(areaSelection, areaOptions)}
            </p>
            <ul className="scientific-study-ul">
              {[...selectedKeys].map((key) => {
                const item = itemByKey.get(key);
                return <li key={key}>{item?.title || key}</li>;
              })}
            </ul>
            <div className="scientific-mastery-actions">
              <button
                type="button"
                className="scientific-btn scientific-btn-primary"
                onClick={() => setPhase('finish')}
              >
                Finalizar sessão
              </button>
            </div>
          </>
        )}

        {phase === 'finish' && (
          <>
            <p className="scientific-muted">
              Registre o que saiu desta sessão. Isso alimenta seu histórico e pode gerar XP bônus.
            </p>
            <label className="scientific-note-label">
              O que você estudou?
              <textarea
                className="scientific-note-textarea"
                rows={2}
                value={reflection.learned}
                onChange={(e) => setReflection((r) => ({ ...r, learned: e.target.value }))}
              />
            </label>
            <label className="scientific-note-label">
              O que entendeu melhor?
              <textarea
                className="scientific-note-textarea"
                rows={2}
                value={reflection.understood}
                onChange={(e) => setReflection((r) => ({ ...r, understood: e.target.value }))}
              />
            </label>
            <label className="scientific-note-label">
              O que ainda ficou confuso?
              <textarea
                className="scientific-note-textarea"
                rows={2}
                value={reflection.confused}
                onChange={(e) => setReflection((r) => ({ ...r, confused: e.target.value }))}
              />
            </label>
            <label className="scientific-note-label">
              Qual é a próxima ação?
              <textarea
                className="scientific-note-textarea"
                rows={2}
                value={reflection.nextAction}
                onChange={(e) => setReflection((r) => ({ ...r, nextAction: e.target.value }))}
              />
            </label>
            <label className="scientific-note-label">
              Pergunta para professor (opcional)
              <textarea
                className="scientific-note-textarea"
                rows={2}
                value={reflection.professorQuestion}
                onChange={(e) =>
                  setReflection((r) => ({ ...r, professorQuestion: e.target.value }))
                }
              />
            </label>
            <label className="scientific-session-item-pick">
              <input
                type="checkbox"
                checked={saveProfessorToNotebook}
                onChange={(e) => setSaveProfessorToNotebook(e.target.checked)}
              />
              Salvar pergunta no caderno
            </label>

            <p className="scientific-route-label">Marcar como dominado (abre verificação)</p>
            <ul className="scientific-session-item-pick-list">
              {[...selectedKeys].map((key) => {
                const item = itemByKey.get(key);
                if (!item) return null;
                return (
                  <li key={key}>
                    <button
                      type="button"
                      className="scientific-btn scientific-btn-ghost scientific-btn--xs"
                      onClick={() =>
                        ctx.requestStudyStatusChange?.(key, 'dominado', {
                          canonicalKey: item.canonicalKey,
                          kind: item.kind,
                          title: item.title,
                          areaLabel: item.areaLabel,
                        })
                      }
                    >
                      Verificar domínio: {item.title.slice(0, 40)}
                    </button>
                  </li>
                );
              })}
            </ul>

            <div className="scientific-mastery-actions">
              <button
                type="button"
                className="scientific-btn scientific-btn-primary"
                onClick={handleSave}
              >
                Salvar sessão
              </button>
              <button type="button" className="scientific-btn scientific-btn-ghost" onClick={onClose}>
                Cancelar
              </button>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}
