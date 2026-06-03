/**
 * Diagnóstico DEV do Workspace do Consultor (não loga em produção).
 */
import { ENABLE_CONSULTOR_WORKSPACE } from '../config/env';

export function logConsultorWorkspaceAvailabilityCheck({
  canViewCadastros = false,
  userRole = null,
  menuVisible = false,
} = {}) {
  if (!import.meta.env.DEV) return;

  console.info('[workspace-consultor] availability_check', {
    flag: ENABLE_CONSULTOR_WORKSPACE,
    hasRoute: ENABLE_CONSULTOR_WORKSPACE,
    canView: Boolean(canViewCadastros),
    menuVisible: Boolean(menuVisible),
    userRole,
  });
}
