import {
  classifySupabaseError,
  shouldSaveManualEditalDraft,
} from '../supabase/supabaseErrorClassifier.js';
import { savePendingManualEditalDraft } from './pendingManualEditalDrafts.js';
import { buildAdminPermissionDiagnostic } from './adminPermissionDiagnostic.js';
import { getRuntimeContext } from '../feedback/runtimeContext.js';
import { isAdminUser, sessionUserId } from '../permissions.js';

/**
 * Processa falha de insert/update manual de edital — retorna estado para UI.
 * @param {object} params
 * @returns {{ saveError: object, localDraftId: string|null }}
 */
export function processManualEditalSaveError({
  error,
  formPayload,
  user,
  authenticated,
  operation = 'insert',
  editingId = null,
}) {
  const errorKind = classifySupabaseError(error);
  const frontendIsAdmin = isAdminUser(user);
  const runtime = getRuntimeContext();

  let localDraftId = null;
  if (shouldSaveManualEditalDraft(errorKind)) {
    localDraftId = savePendingManualEditalDraft(formPayload, {
      operation,
      table: 'edital',
      route: '/cadastros',
      errorKind,
      errorMessage: String(error?.message || '').slice(0, 300),
      supabaseCode: error?.code != null ? String(error.code) : null,
      supabaseStatus: error?.status ?? null,
      runtime: runtime.runtime,
      frontendIsAdmin,
      isAuthenticated: Boolean(authenticated),
      hasUserId: sessionUserId(user) != null,
      editingId,
    });
  }

  const result = buildAdminPermissionDiagnostic({
    user,
    frontendIsAdmin,
    frontendRole: user?.tipo || user?.tipo_usuario,
    operation,
    error,
    errorKind,
    isAuthenticated: authenticated,
    localDraftId,
  });

  return {
    saveError: {
      ...result,
      localDraftId,
      operation,
    },
    localDraftId,
  };
}

/** Contexto para AppFeedbackModal / reporte. */
export function buildManualEditalReportContext(saveError) {
  if (!saveError) return {};
  const meta = saveError.reportMetadata || {};
  return {
    origem: meta.origem || 'manual_edital_create',
    pagina: 'cadastros',
    componente: 'Cadastros',
    acao: 'submit',
    tipo: 'cadastro',
    severidade: 'alta',
    error: {
      message: saveError.safeDetails?.message,
      code: saveError.safeDetails?.code,
      name: 'SupabaseSaveError',
    },
    extraContext: meta,
  };
}
