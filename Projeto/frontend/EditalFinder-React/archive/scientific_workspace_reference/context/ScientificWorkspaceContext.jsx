import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { addScientificNotebookEntry } from '../utils/scientific/scientificNotebookStorage';
import { findNotebookByEntryKey, getScientificNotebookEntryKey } from '../utils/scientific/getScientificNotebookEntryKey';
import { scientificScrollToSection } from '../utils/scientific/scientificScrollToSection';
import { scientificButtonClick } from '../utils/scientific/scientificButtonClick';
import {
  showScientificToastPayload,
  SCIENTIFIC_TOAST_MESSAGES,
} from '../utils/scientific/showScientificToast';
import {
  loadScientificStudyProgress,
  setScientificStudyProgressStatus,
  getProgressStatusFromMap,
} from '../utils/scientific/scientificStudyProgressStorage';
import { buildMasteryCheckQuestions } from '../utils/scientific/buildMasteryCheckQuestions';
import { upsertMasteryCheck, loadScientificMasteryChecks } from '../utils/scientific/scientificMasteryStorage';
import { awardScientificXp, loadScientificXp } from '../utils/scientific/scientificXpStorage';
import { buildScientificLevelSummary } from '../utils/scientific/buildScientificLevelSummary';
import { buildScientificBadges } from '../utils/scientific/buildScientificBadges';
import {
  loadScientificBookProgress,
  updateBookProgressEntry,
} from '../utils/scientific/scientificBookProgressStorage';
import { loadStudySessions, addStudySession } from '../utils/scientific/scientificStudySessionStorage';
import { calculateSessionXp, sessionXpProgressKey } from '../utils/scientific/scientificSessionXp';
import { notebookEntryFromProfessorQuestion } from '../utils/scientific/notebookEntryFromProfessorQuestion';
import { logScientificWorkspace } from '../utils/scientific/scientificWorkspaceLog';
import ScientificMasteryCheckModal from '../components/scientific/ScientificMasteryCheckModal';
import ScientificBookProgressModal from '../components/scientific/ScientificBookProgressModal';
import ScientificStudySessionModal from '../components/scientific/ScientificStudySessionModal';

const ScientificWorkspaceContext = createContext(null);

const TOAST_BY_STATUS = {
  saved: { message: SCIENTIFIC_TOAST_MESSAGES.saved, type: 'success' },
  updated: { message: SCIENTIFIC_TOAST_MESSAGES.updated, type: 'success' },
  unchanged: { message: SCIENTIFIC_TOAST_MESSAGES.alreadySaved, type: 'info' },
};

const FALLBACK_CONTEXT = {
  notebookItems: [],
  saveToNotebook: () => ({ row: null, status: 'unchanged' }),
  isInNotebook: () => false,
  getSaveFlash: () => null,
  scrollToSection: () => false,
  showToast: () => {},
  toast: null,
  studyProgress: {},
  getStudyProgressStatus: () => 'a_estudar',
  setStudyProgressStatus: () => {},
  requestStudyStatusChange: () => {},
  masteryChecks: {},
  xpState: { totalXp: 0 },
  levelSummary: null,
  badges: [],
  bookProgress: {},
  updateBookProgress: () => {},
  openBookProgressModal: () => {},
  studySessions: [],
  openStudySessionModal: () => {},
  completeStudySession: () => {},
  applyStudyStatus: () => {},
};

export function ScientificWorkspaceProvider({
  children,
  notebookItems = [],
  onNotebookChange,
}) {
  const safeNotebookItems = Array.isArray(notebookItems) ? notebookItems : [];
  const [toast, setToast] = useState(null);
  const [flashKeys, setFlashKeys] = useState({});
  const [studyProgress, setStudyProgress] = useState(() => loadScientificStudyProgress());
  const [masteryChecks, setMasteryChecks] = useState(() => loadScientificMasteryChecks());
  const [xpState, setXpState] = useState(() => loadScientificXp());
  const [bookProgress, setBookProgress] = useState(() => loadScientificBookProgress());
  const [masteryPending, setMasteryPending] = useState(null);
  const [bookPending, setBookPending] = useState(null);
  const [studySessions, setStudySessions] = useState(() => loadStudySessions().sessions);
  const [sessionModal, setSessionModal] = useState({ open: false, initial: {}, studyBlocks: [] });

  useEffect(() => {
    logScientificWorkspace('study_progress_loaded', {
      count: Object.keys(studyProgress).length,
    });
    logScientificWorkspace('mastery_checks_loaded', {
      count: Object.keys(masteryChecks).length,
    });
    logScientificWorkspace('xp_loaded', { totalXp: xpState.totalXp });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const showToast = useCallback((message, type = 'success') => {
    if (!message) {
      setToast(null);
      return;
    }
    setToast(showScientificToastPayload(message, type));
  }, []);

  const isInNotebook = useCallback(
    (entry) => Boolean(findNotebookByEntryKey(safeNotebookItems, entry)),
    [safeNotebookItems],
  );

  const getSaveFlash = useCallback(
    (entry) => {
      const key = getScientificNotebookEntryKey(entry);
      return key ? flashKeys[key] || null : null;
    },
    [flashKeys],
  );

  const getStudyProgressStatus = useCallback(
    (progressKey) => getProgressStatusFromMap(studyProgress, progressKey),
    [studyProgress],
  );

  const applyStudyStatus = useCallback((progressKey, status) => {
    const next = setScientificStudyProgressStatus(progressKey, status);
    setStudyProgress(next);
    logScientificWorkspace('study_progress_changed', { progressKey, status });
  }, []);

  const refreshGamification = useCallback(
    (nextXp) => {
      const xp = nextXp || xpState;
      setXpState(xp);
      logScientificWorkspace('study_progress_summary_generated', {
        totalXp: xp.totalXp,
      });
    },
    [xpState],
  );

  const confirmMasteryFlow = useCallback(
    (answers, pending) => {
      const p = pending || masteryPending;
      if (!p) return;

      const filled = (answers || []).filter((a) => String(a || '').trim().length > 10).length >= 2;
      const questions = p.questions || [];
      const answerRecords = questions.map((q, i) => ({
        questionId: q.id,
        question: q.question,
        answer: answers?.[i] || '',
      }));

      const xpResult = awardScientificXp({
        progressKey: p.progressKey,
        canonicalKey: p.canonicalKey,
        kind: p.kind,
        title: p.title,
        bonusAnswers: filled,
      });

      upsertMasteryCheck({
        progressKey: p.progressKey,
        canonicalKey: p.canonicalKey,
        kind: p.kind,
        title: p.title,
        level: p.level,
        questions,
        answers: answerRecords,
        xpAwarded: xpResult.xp,
        confirmedAt: new Date().toISOString(),
      });

      setMasteryChecks(loadScientificMasteryChecks());
      applyStudyStatus(p.progressKey, 'dominado');
      if (xpResult.awarded) {
        refreshGamification(xpResult.state);
        showToast(`Domínio confirmado! +${xpResult.xp} XP`, 'success');
      } else {
        showToast('Domínio confirmado (XP já concedido antes).', 'info');
      }
      setMasteryPending(null);
    },
    [masteryPending, applyStudyStatus, refreshGamification, showToast],
  );

  const requestStudyStatusChange = useCallback(
    (progressKey, status, itemMeta = {}) => {
      if (status === 'dominado') {
        const previousStatus = getProgressStatusFromMap(studyProgress, progressKey);
        const questions = buildMasteryCheckQuestions({
          canonicalKey: itemMeta.canonicalKey,
          kind: itemMeta.kind,
          title: itemMeta.title,
          level: itemMeta.level,
          relatedTopics: itemMeta.relatedTopics,
          whyItMatters: itemMeta.whyItMatters,
          shortExplanation: itemMeta.shortExplanation,
        });
        setMasteryPending({
          progressKey,
          previousStatus,
          questions,
          canonicalKey: itemMeta.canonicalKey,
          kind: itemMeta.kind,
          title: itemMeta.title,
          level: itemMeta.level,
          areaLabel: itemMeta.areaLabel,
          itemType: itemMeta.itemType,
        });
        return;
      }
      applyStudyStatus(progressKey, status);
    },
    [studyProgress, applyStudyStatus],
  );

  const setStudyProgressStatusHandler = useCallback(
    (progressKey, status, itemMeta) => {
      requestStudyStatusChange(progressKey, status, itemMeta);
    },
    [requestStudyStatusChange],
  );

  const openBookProgressModal = useCallback((payload) => {
    setBookPending(payload);
  }, []);

  const openStudySessionModal = useCallback((payload = {}) => {
    setSessionModal({
      open: true,
      initial: payload,
      studyBlocks: payload.studyBlocks || [],
      activeInterests: payload.activeInterests || [],
      goalRoutes: payload.goalRoutes || [],
      notebookItems: payload.notebookItems || safeNotebookItems,
    });
    logScientificWorkspace('study_session_modal_requested', {
      canonicalKey: payload.canonicalKey,
    });
  }, []);

  const updateBookProgress = useCallback(
    (patch) => {
      const next = updateBookProgressEntry(patch.bookKey, patch);
      setBookProgress(next);

      if (patch.status === 'lido') {
        requestStudyStatusChange(patch.bookKey, 'dominado', {
          canonicalKey: patch.area,
          kind: 'book',
          title: patch.title,
          areaLabel: patch.areaLabel || patch.area,
          level: 'lido',
          whyItMatters: patch.notes,
          shortExplanation: patch.currentChapter,
        });
      } else if (patch.status === 'lendo') {
        applyStudyStatus(patch.bookKey, 'estudando');
      }
      setBookPending(null);
    },
    [requestStudyStatusChange, applyStudyStatus],
  );

  const saveToNotebook = useCallback(
    (entry, meta = {}) => {
      scientificButtonClick({
        action: meta.action || 'save_notebook',
        itemId: entry?.id,
        label: meta.label,
      });

      const result = addScientificNotebookEntry(entry || {});
      onNotebookChange?.();

      if (meta.action === 'save_route' || meta.action === 'save_goal_route') {
        const routeKey = getScientificNotebookEntryKey(entry);
        if (routeKey) {
          const xpResult = awardScientificXp({
            progressKey: `route-saved-${routeKey}`,
            canonicalKey: entry.interesses?.[0] || '',
            kind: 'route_saved',
            title: entry.titulo || 'Rota salva',
            reason: 'rota_salva',
          });
          if (xpResult.awarded) refreshGamification(xpResult.state);
        }
      }

      const key = getScientificNotebookEntryKey(entry);
      if (key) {
        setFlashKeys((prev) => ({ ...prev, [key]: result.status }));
      }

      const payload = TOAST_BY_STATUS[result.status] || TOAST_BY_STATUS.saved;
      showToast(payload.message, payload.type);

      window.setTimeout(() => {
        if (!key) return;
        setFlashKeys((prev) => {
          const n = { ...prev };
          delete n[key];
          return n;
        });
      }, 2200);
      window.setTimeout(() => setToast(null), 2400);

      return result;
    },
    [onNotebookChange, showToast, refreshGamification],
  );

  const completeStudySession = useCallback(
    (payload) => {
      const selectedItems = (payload.selectedItems || []).filter((i) => i?.progressKey);
      if (!selectedItems.length) {
        showToast('Selecione pelo menos um item para salvar a sessão.', 'info');
        return;
      }

      const sessionId = `session-${Date.now()}`;
      const reflection = payload.reflection || {};

      for (const item of selectedItems) {
        if (item.progressKey) {
          applyStudyStatus(item.progressKey, 'estudando');
        }
      }

      const professorQ = String(reflection.professorQuestion || '').trim();
      if (payload.saveProfessorToNotebook && professorQ.length >= 10) {
        saveToNotebook(
          notebookEntryFromProfessorQuestion({
            interestId: payload.canonicalKey,
            label: payload.areaLabel,
            question: professorQ,
          }),
          { action: 'save_professor_question', label: 'Pergunta da sessão' },
        );
      }

      const xpAmount = calculateSessionXp({
        durationMinutes: payload.durationMinutes,
        reflection,
        hasProfessorQuestion: professorQ.length >= 10,
      });

      const xpResult = awardScientificXp({
        progressKey: sessionXpProgressKey(sessionId),
        canonicalKey: payload.canonicalKey,
        kind: 'study_session',
        title: payload.title || 'Sessão de estudo',
        reason: 'sessao_estudo',
        customXp: xpAmount,
      });

      const session = {
        id: sessionId,
        title: payload.title,
        canonicalKey: payload.canonicalKey,
        areaLabel: payload.areaLabel,
        goalRouteId: payload.goalRouteId,
        focus: payload.focus,
        plannedMinutes: payload.plannedMinutes,
        startedAt: payload.startedAt,
        finishedAt: payload.finishedAt,
        durationMinutes: payload.durationMinutes,
        selectedItems: selectedItems.map((item) => ({
          ...item,
          statusBefore: item.statusBefore || 'none',
          statusAfter: item.statusAfter || 'estudando',
        })),
        reflection,
        xpAwarded: xpResult.awarded ? xpAmount : 0,
      };

      addStudySession(session);
      setStudySessions(loadStudySessions().sessions);

      if (xpResult.awarded) {
        refreshGamification(xpResult.state);
        showToast(`Sessão salva! +${xpAmount} XP`, 'success');
      } else {
        showToast('Sessão salva.', 'success');
      }
      logScientificWorkspace('study_session_saved', {
        id: sessionId,
        xp: session.xpAwarded,
        items: selectedItems.length,
        focus: payload.focus,
      });
      setSessionModal((s) => ({ ...s, open: false }));
    },
    [applyStudyStatus, saveToNotebook, refreshGamification, showToast],
  );

  const scrollToSection = useCallback(
    (sectionId, source, label) =>
      scientificScrollToSection(sectionId, {
        source,
        label,
        onToast: (payload) => {
          if (payload) showToast(payload.message, payload.type);
          else setToast(null);
        },
      }),
    [showToast],
  );

  const levelSummary = useMemo(() => buildScientificLevelSummary(xpState), [xpState]);

  const badges = useMemo(
    () =>
      buildScientificBadges({
        studyProgress,
        xpState,
        notebookItems: safeNotebookItems,
        bookProgress,
      }),
    [studyProgress, xpState, safeNotebookItems, bookProgress],
  );

  const value = useMemo(
    () => ({
      notebookItems: safeNotebookItems,
      saveToNotebook,
      isInNotebook,
      getSaveFlash,
      scrollToSection,
      showToast,
      toast,
      studyProgress,
      getStudyProgressStatus,
      setStudyProgressStatus: setStudyProgressStatusHandler,
      requestStudyStatusChange,
      masteryChecks,
      xpState,
      levelSummary,
      badges,
      bookProgress,
      updateBookProgress,
      openBookProgressModal,
      studySessions,
      openStudySessionModal,
      completeStudySession,
      applyStudyStatus,
    }),
    [
      safeNotebookItems,
      saveToNotebook,
      isInNotebook,
      getSaveFlash,
      scrollToSection,
      showToast,
      toast,
      studyProgress,
      getStudyProgressStatus,
      setStudyProgressStatusHandler,
      requestStudyStatusChange,
      masteryChecks,
      xpState,
      levelSummary,
      badges,
      bookProgress,
      updateBookProgress,
      openBookProgressModal,
      studySessions,
      openStudySessionModal,
      completeStudySession,
      applyStudyStatus,
    ],
  );

  return (
    <ScientificWorkspaceContext.Provider value={value}>
      {children}
      <ScientificMasteryCheckModal
        open={Boolean(masteryPending)}
        pending={masteryPending}
        onConfirmMastery={(answers) => confirmMasteryFlow(answers)}
        onMarkStudying={() => {
          if (masteryPending) applyStudyStatus(masteryPending.progressKey, 'estudando');
          setMasteryPending(null);
        }}
        onDefer={() => {
          if (masteryPending) {
            applyStudyStatus(
              masteryPending.progressKey,
              masteryPending.previousStatus || 'a_estudar',
            );
          }
          setMasteryPending(null);
        }}
        onClose={() => setMasteryPending(null)}
      />
      <ScientificBookProgressModal
        open={Boolean(bookPending)}
        book={bookPending?.book}
        bookKey={bookPending?.bookKey}
        canonicalKey={bookPending?.canonicalKey}
        areaLabel={bookPending?.areaLabel}
        initial={bookPending?.bookKey ? bookProgress[bookPending.bookKey] : null}
        onSave={updateBookProgress}
        onClose={() => setBookPending(null)}
      />
      <ScientificStudySessionModal
        open={sessionModal.open}
        initial={sessionModal.initial}
        studyBlocks={sessionModal.studyBlocks}
        activeInterests={sessionModal.activeInterests}
        goalRoutes={sessionModal.goalRoutes}
        notebookItems={sessionModal.notebookItems}
        onClose={() => setSessionModal((s) => ({ ...s, open: false }))}
      />
    </ScientificWorkspaceContext.Provider>
  );
}

export function useScientificWorkspace() {
  const ctx = useContext(ScientificWorkspaceContext);
  return ctx ?? FALLBACK_CONTEXT;
}

export default ScientificWorkspaceContext;
