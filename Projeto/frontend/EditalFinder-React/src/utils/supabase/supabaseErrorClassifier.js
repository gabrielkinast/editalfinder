/**
 * Classificação segura de erros Supabase/PostgREST (sem secrets).
 */

export const SUPABASE_ERROR_KIND = {
  RLS_POLICY: 'rls_policy',
  PERMISSION_DENIED: 'permission_denied',
  NETWORK: 'network',
  VALIDATION: 'validation',
  SCHEMA: 'schema',
  DUPLICATE: 'duplicate',
  UNKNOWN: 'unknown',
};

const RLS_MARKERS = [
  'row-level security',
  'violates row-level security',
  'new row violates row-level security policy',
];

function normMessage(error) {
  return String(error?.message || error?.error_description || '').toLowerCase();
}

function normCode(error) {
  return String(error?.code || error?.status || '').trim();
}

function normStatus(error) {
  const s = error?.status ?? error?.statusCode;
  if (s == null || s === '') return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

export function classifySupabaseError(error) {
  if (!error) return SUPABASE_ERROR_KIND.UNKNOWN;

  const message = normMessage(error);
  const code = normCode(error);
  const status = normStatus(error);
  const blob = `${message} ${code} ${JSON.stringify(error?.details || '')}`.toLowerCase();

  if (
    code === '23505' ||
    message.includes('duplicate key') ||
    message.includes('unique constraint')
  ) {
    return SUPABASE_ERROR_KIND.DUPLICATE;
  }

  if (
    code === 'PGRST204' ||
    code === 'PGRST205' ||
    message.includes('schema cache') ||
    message.includes('could not find') ||
    message.includes('column') && message.includes('not found') ||
    message.includes('relation') && message.includes('does not exist')
  ) {
    return SUPABASE_ERROR_KIND.SCHEMA;
  }

  if (
    message.includes('failed to fetch') ||
    message.includes('networkerror') ||
    message.includes('load failed') ||
    message.includes('network request failed') ||
    message.includes('cors') ||
    code === 'ECONNREFUSED' ||
    status === 0
  ) {
    return SUPABASE_ERROR_KIND.NETWORK;
  }

  if (
    status === 401 ||
    status === 403 ||
    code === '42501' ||
    code === 'PGRST301' ||
    message.includes('permission denied') ||
    message.includes('insufficient privileges') ||
    message.includes('not authorized')
  ) {
    if (RLS_MARKERS.some((m) => message.includes(m)) || message.includes('policy')) {
      return SUPABASE_ERROR_KIND.RLS_POLICY;
    }
    return SUPABASE_ERROR_KIND.PERMISSION_DENIED;
  }

  if (
    RLS_MARKERS.some((m) => message.includes(m)) ||
    (message.includes('policy') && (message.includes('violat') || message.includes('security')))
  ) {
    return SUPABASE_ERROR_KIND.RLS_POLICY;
  }

  if (
    message.includes('violates not-null') ||
    message.includes('invalid input') ||
    message.includes('required') ||
    message.includes('check constraint') ||
    code === '23502' ||
    code === '23514' ||
    code === '22P02'
  ) {
    return SUPABASE_ERROR_KIND.VALIDATION;
  }

  return SUPABASE_ERROR_KIND.UNKNOWN;
}

/** Detalhes seguros para UI/reporte — nunca tokens/keys. */
export function getSupabaseSafeErrorDetails(error) {
  if (!error || typeof error !== 'object') {
    return { message: String(error || ''), code: null, details: null, hint: null, status: null };
  }

  const safe = {
    message: String(error.message || error.error_description || '').slice(0, 500),
    code: error.code != null ? String(error.code) : null,
    details:
      error.details != null
        ? String(error.details).slice(0, 300)
        : error.hint != null
          ? null
          : null,
    hint: error.hint != null ? String(error.hint).slice(0, 300) : null,
    status: normStatus(error),
  };

  const blob = JSON.stringify(safe).toLowerCase();
  if (
    blob.includes('access_token') ||
    blob.includes('refresh_token') ||
    blob.includes('service_role') ||
    blob.includes('bearer ')
  ) {
    return {
      message: '[mensagem redigida]',
      code: safe.code,
      details: null,
      hint: null,
      status: safe.status,
    };
  }

  return safe;
}

/**
 * Mensagem amigável para cadastro manual.
 * @param {unknown} error
 * @param {{ frontendIsAdmin?: boolean, operation?: string }} [context]
 */
export function getSupabaseFriendlyMessage(error, context = {}) {
  const kind = classifySupabaseError(error);
  const admin = Boolean(context.frontendIsAdmin);

  if (kind === SUPABASE_ERROR_KIND.RLS_POLICY || kind === SUPABASE_ERROR_KIND.PERMISSION_DENIED) {
    if (admin) {
      return {
        title: 'Permissão de administrador não reconhecida pelo banco',
        message:
          'O aplicativo identificou seu perfil como administrador, mas o Supabase bloqueou o cadastro por regra de segurança. Seus dados não foram perdidos e foram mantidos na tela/salvos como rascunho local.',
        kind,
      };
    }
    return {
      title: 'Não foi possível cadastrar este edital',
      message:
        'O banco de dados bloqueou a operação por regra de permissão. Seus dados não foram perdidos.',
      kind,
    };
  }

  if (kind === SUPABASE_ERROR_KIND.DUPLICATE) {
    return {
      title: 'Edital já cadastrado',
      message: 'Já existe um registro com o mesmo link ou identificador único. Ajuste o link e tente novamente.',
      kind,
    };
  }

  if (kind === SUPABASE_ERROR_KIND.NETWORK) {
    return {
      title: 'Falha de conexão',
      message:
        'Não foi possível contactar o Supabase. Verifique a internet e tente novamente. Rascunho salvo localmente.',
      kind,
    };
  }

  if (kind === SUPABASE_ERROR_KIND.SCHEMA) {
    return {
      title: 'Incompatibilidade de schema',
      message:
        'O servidor rejeitou o cadastro por diferença de estrutura (coluna/tabela). Rascunho salvo localmente.',
      kind,
    };
  }

  if (kind === SUPABASE_ERROR_KIND.VALIDATION) {
    return {
      title: 'Dados inválidos',
      message: 'Revise os campos obrigatórios e o formato dos valores antes de tentar novamente.',
      kind,
    };
  }

  const details = getSupabaseSafeErrorDetails(error);
  return {
    title: 'Não foi possível salvar',
    message: details.message || 'Ocorreu um erro inesperado ao salvar o edital.',
    kind,
  };
}

export function shouldSaveManualEditalDraft(errorKind) {
  return [
    SUPABASE_ERROR_KIND.RLS_POLICY,
    SUPABASE_ERROR_KIND.PERMISSION_DENIED,
    SUPABASE_ERROR_KIND.NETWORK,
    SUPABASE_ERROR_KIND.SCHEMA,
  ].includes(errorKind);
}
