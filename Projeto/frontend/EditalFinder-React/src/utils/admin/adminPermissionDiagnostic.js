import { getRuntimeContext } from '../feedback/runtimeContext.js';
import {
  classifySupabaseError,
  getSupabaseSafeErrorDetails,
  getSupabaseFriendlyMessage,
} from '../supabase/supabaseErrorClassifier.js';
import { sessionUserId } from '../permissions.js';
import { redactSensitiveFeedbackObject } from '../feedback/appFeedbackSensitive.js';

/**
 * Diagnóstico seguro admin UI vs RLS Supabase.
 */
export function buildAdminPermissionDiagnostic({
  user,
  frontendRole,
  frontendIsAdmin,
  operation = 'insert',
  table = 'edital',
  route = '/cadastros',
  error,
  errorKind,
  isAuthenticated = Boolean(user),
  localDraftId = null,
}) {
  const safeDetails = getSupabaseSafeErrorDetails(error);
  const kind = errorKind || classifySupabaseError(error);
  const runtime = getRuntimeContext();
  const uid = sessionUserId(user);
  const friendly = getSupabaseFriendlyMessage(error, { frontendIsAdmin, operation });

  const diagnostic = redactSensitiveFeedbackObject({
    isAuthenticated,
    hasUserId: uid != null,
    userEmail: user?.nome_email || user?.email || null,
    frontendRole: frontendRole || user?.tipo || user?.tipo_usuario || null,
    frontendIsAdmin: Boolean(frontendIsAdmin),
    operation,
    table,
    route,
    supabaseErrorKind: kind,
    supabaseCode: safeDetails.code,
    supabaseStatus: safeDetails.status,
    supabaseMessage: safeDetails.message,
    supabaseHint: safeDetails.hint,
    runtime: runtime.runtime,
    localDraftId,
    possibleMissingFields: ['created_by', 'id_usuario'],
    note: 'Payload manual não envia created_by/id_usuario neste patch — apenas diagnóstico.',
  });

  const reportMetadata = {
    origem: operation === 'update' ? 'manual_edital_update' : 'manual_edital_create',
    componente: 'Cadastros',
    acao: 'submit',
    operation,
    table,
    errorKind: kind,
    supabaseCode: safeDetails.code,
    supabaseStatus: safeDetails.status,
    supabaseMessage: safeDetails.message,
    supabaseHint: safeDetails.hint,
    frontendIsAdmin: Boolean(frontendIsAdmin),
    frontendRole: diagnostic.frontendRole,
    isAuthenticated,
    hasUserId: uid != null,
    route,
    localDraftId,
  };

  return {
    title: friendly.title,
    message: friendly.message,
    errorKind: kind,
    diagnostic,
    reportMetadata,
    safeDetails,
  };
}
