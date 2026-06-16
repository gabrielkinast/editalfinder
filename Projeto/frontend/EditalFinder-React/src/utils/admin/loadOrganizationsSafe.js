import { dataService } from '../../services/dataService';
import { isMissingPostgrestTableError } from '../supabase/postgrestErrors';

/**
 * Carrega organizações sem bloquear o formulário de edital se a tabela não existir no PostgREST.
 * @returns {Promise<{ ok: boolean, organizations: object[], reason: string|null, error?: unknown }>}
 */
export async function loadOrganizationsSafe() {
  try {
    const organizations = await dataService.getOrganizations();

    if (!Array.isArray(organizations)) {
      return {
        ok: false,
        organizations: [],
        reason: 'invalid_response',
      };
    }

    return {
      ok: true,
      organizations,
      reason: null,
    };
  } catch (error) {
    if (isMissingPostgrestTableError(error)) {
      return {
        ok: false,
        organizations: [],
        reason: 'table_not_exposed',
        error,
      };
    }

    return {
      ok: false,
      organizations: [],
      reason: 'load_failed',
      error,
    };
  }
}
