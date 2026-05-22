import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useAuth } from './AuthContext';
import { buildAppFeedbackPayload } from '../utils/feedback/buildAppFeedbackPayload';
import {
  createAppFeedback,
  flushPendingAppFeedback,
  MSG_APP_FEEDBACK_NOT_AUTHENTICATED,
} from '../services/appFeedbackService';
import {
  installGlobalErrorReporter,
  registerGlobalErrorReporterHandlers,
  uninstallGlobalErrorReporter,
} from '../utils/errors/globalErrorReporter';
import { registerActionErrorHandlers } from '../utils/errors/reportableActionError';
import AppFeedbackModal from '../components/feedback/AppFeedbackModal';
import AppFeedbackToast from '../components/feedback/AppFeedbackToast';

const AppFeedbackContext = createContext(null);

export function AppFeedbackProvider({ children }) {
  const { user: appUser, authenticated, loading: authLoading } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContext, setModalContext] = useState(null);
  const [lastReportable, setLastReportable] = useState(null);
  const [toast, setToast] = useState(null);

  const authUserId = appUser?.auth_user_id ?? null;

  const openAppFeedbackModal = useCallback((context = {}) => {
    setModalContext(context);
    setModalOpen(true);
  }, []);

  const closeAppFeedbackModal = useCallback(() => {
    setModalOpen(false);
    setModalContext(null);
  }, []);

  const showAppToast = useCallback((message, context = null, type = 'error') => {
    setToast({
      message,
      type,
      context,
      actionLabel: type === 'error' ? 'Reportar problema' : null,
    });
    window.setTimeout(() => setToast(null), 8000);
  }, []);

  const showAppErrorToast = useCallback(
    (message, context = null) => {
      if (context) setLastReportable(context);
      showAppToast(message, context, 'error');
    },
    [showAppToast],
  );

  const showAppSuccessToast = useCallback(
    (message) => {
      showAppToast(message, null, 'success');
      window.setTimeout(() => setToast(null), 3200);
    },
    [showAppToast],
  );

  useEffect(() => {
    registerGlobalErrorReporterHandlers({
      onReportableError: (ctx) => setLastReportable(ctx),
      showErrorToast: showAppErrorToast,
    });
    registerActionErrorHandlers({
      showErrorToast: showAppErrorToast,
      openFeedbackModal: openAppFeedbackModal,
      setLastReportable,
    });
    installGlobalErrorReporter();
    return () => uninstallGlobalErrorReporter();
  }, [showAppErrorToast, openAppFeedbackModal]);

  useEffect(() => {
    if (!authenticated || authLoading) return;
    flushPendingAppFeedback({
      appUser,
      authenticated,
      authLoading,
      authUserId,
    }).then((r) => {
      if (r.flushed > 0) {
        showAppSuccessToast(`${r.flushed} relatório(s) pendente(s) enviado(s).`);
      }
    });
  }, [authenticated, authLoading, appUser, authUserId, showAppSuccessToast]);

  const submitFeedback = useCallback(
    async ({ tipo, comment, context }) => {
      const base = context?.payload || buildAppFeedbackPayload({
        tipo: tipo || context?.tipo || 'outro',
        origem: context?.origem || 'user_report',
        pagina: context?.pagina,
        componente: context?.componente,
        acao: context?.acao,
        error: context?.error,
        errorInfo: context?.errorInfo,
        comment,
        extraContext: context?.extraContext,
      });

      const payload = {
        ...base,
        tipo_feedback: tipo || base.tipo_feedback,
        comentario: comment || base.comentario,
      };

      return createAppFeedback(payload, {
        appUser,
        authenticated,
        authLoading,
        authUserId,
      });
    },
    [appUser, authenticated, authLoading, authUserId],
  );

  const value = useMemo(
    () => ({
      openAppFeedbackModal,
      closeAppFeedbackModal,
      lastReportable,
      setLastReportable,
      showAppErrorToast,
      showAppSuccessToast,
      submitFeedback,
      authenticated,
      authLoading,
      authBlockMessage: authLoading
        ? 'Carregando conta…'
        : !authenticated
          ? MSG_APP_FEEDBACK_NOT_AUTHENTICATED
          : null,
    }),
    [
      openAppFeedbackModal,
      closeAppFeedbackModal,
      lastReportable,
      showAppErrorToast,
      showAppSuccessToast,
      submitFeedback,
      authenticated,
      authLoading,
    ],
  );

  return (
    <AppFeedbackContext.Provider value={value}>
      {children}
      <AppFeedbackModal
        open={modalOpen}
        context={modalContext}
        onClose={closeAppFeedbackModal}
        onSubmit={submitFeedback}
        onSuccess={(msg) => {
          showAppSuccessToast(msg);
          closeAppFeedbackModal();
        }}
        authBlockMessage={value.authBlockMessage}
      />
      <AppFeedbackToast
        toast={toast}
        onAction={() => {
          const ctx = toast?.context || lastReportable;
          openAppFeedbackModal(ctx || { origem: 'toast_error', tipo: 'outro' });
          setToast(null);
        }}
        onDismiss={() => setToast(null)}
      />
    </AppFeedbackContext.Provider>
  );
}

export function useAppFeedback() {
  const ctx = useContext(AppFeedbackContext);
  if (!ctx) {
    return {
      openAppFeedbackModal: () => {},
      showAppErrorToast: () => {},
      showAppSuccessToast: () => {},
      lastReportable: null,
    };
  }
  return ctx;
}

export default AppFeedbackContext;
