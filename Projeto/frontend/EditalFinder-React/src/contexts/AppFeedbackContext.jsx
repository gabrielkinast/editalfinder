import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useAuth } from './AuthContext';
import {
  flushPendingAppFeedback,
  submitAppFeedback,
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

function safeFlushPending(onSent) {
  flushPendingAppFeedback()
    .then((r) => {
      if (r?.sent > 0) onSent?.(r.sent);
    })
    .catch((error) => {
      if (import.meta.env.DEV) {
        console.warn('[AppFeedback] flush failed', error);
      }
    });
}

export function AppFeedbackProvider({ children }) {
  const { user: appUser, authenticated, loading: authLoading } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContext, setModalContext] = useState({});
  const [lastReportable, setLastReportable] = useState(null);
  const [toast, setToast] = useState(null);

  const authUserId = appUser?.auth_user_id ?? null;

  const openAppFeedbackModal = useCallback((context = {}) => {
    setModalContext(context && typeof context === 'object' ? context : {});
    setModalOpen(true);
    safeFlushPending((sent) => {
      setToast({
        message: `${sent} reporte(s) pendente(s): abrimos o Gmail — revise e envie a mensagem.`,
        type: 'success',
        context: null,
        actionLabel: null,
      });
      window.setTimeout(() => setToast(null), 5000);
    });
  }, []);

  const closeAppFeedbackModal = useCallback(() => {
    setModalOpen(false);
    setModalContext({});
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
    try {
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
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('[AppFeedback] reporter install failed', error);
      }
    }
    return () => {
      try {
        uninstallGlobalErrorReporter();
      } catch {
        /* ignore */
      }
    };
  }, [showAppErrorToast, openAppFeedbackModal]);

  const submitFeedback = useCallback(
    async ({ tipo, severidade, comment, context }) => {
      try {
        return await submitAppFeedback(
          { tipo, severidade, descricao: comment, comment },
          context || {},
          {
            appUser,
            authenticated,
            authLoading,
            authUserId,
          },
        );
      } catch (error) {
        if (import.meta.env.DEV) {
          console.warn('[AppFeedback] submit failed', error);
        }
        return {
          ok: false,
          status: 'failed',
          message: 'Não foi possível processar o relatório. Tente novamente.',
        };
      }
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
      authBlockMessage: null,
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
          openAppFeedbackModal(ctx || { origem: 'toast_error', tipo: 'other' });
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
