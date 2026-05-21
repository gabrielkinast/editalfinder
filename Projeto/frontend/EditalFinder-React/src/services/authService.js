import { supabase, isSupabaseConfigured } from './api';
import { authSignupDevLog, formatSupabaseError } from '../utils/authSignupDevLog';
import {
  getAuthCallbackRedirectUrl,
  getAuthRedirectLogMeta,
} from '../utils/authCallbackRoute';

const STORAGE_KEY = 'editalFinderUser';

/** Perfil padrão para novos utilizadores (regra de negócio existente). */
const DEFAULT_SIGNUP_PROFILE = {
  tipo_usuario: 'Consultor',
  nivel_acesso: 2,
  status: 'Ativo',
};

/** Normaliza e-mail para comparação e gravação (trim + minúsculas). */
export function normalizeAuthEmail(email) {
  return String(email ?? '').trim().toLowerCase();
}

/**
 * Monta o objecto de utilizador usado na app (estado React + cache).
 * Mantém aliases `tipo`, `nivel`, `email` para compatibilidade com código existente.
 */
export function buildAppUser(profileRow, authUserId) {
  if (!profileRow) return null;
  const authUid = authUserId ?? profileRow.auth_user_id ?? null;
  return {
    id_usuario: profileRow.id_usuario,
    auth_user_id: authUid,
    nome: profileRow.nome,
    nome_email: profileRow.nome_email,
    tipo_usuario: profileRow.tipo_usuario,
    nivel_acesso: profileRow.nivel_acesso,
    status: profileRow.status,
    tipo: profileRow.tipo_usuario,
    nivel: profileRow.nivel_acesso,
    email: profileRow.nome_email,
  };
}

export function persistProfileCache(user) {
  if (!user || typeof user !== 'object') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  } catch {
    /* ignore */
  }
}

export function clearProfileCache() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

/**
 * Apenas DEV: reidratar sessão “legada” sem Supabase Auth (perfil sem auth_user_id em cache).
 * TODO: remover quando todos os utilizadores tiverem Supabase Auth.
 */
export function hydrateDevLegacyFromCache() {
  if (!import.meta.env.DEV) return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const u = JSON.parse(raw);
    if (!u?.id_usuario) return null;
    if (u.auth_user_id) return null;
    return u;
  } catch {
    return null;
  }
}

/** @deprecated Preferir sessão Supabase + buildAppUser; mantido para leitura síncrona pontual. */
export function getUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export async function getCurrentSession() {
  if (!isSupabaseConfigured) return null;
  const { data, error } = await supabase.auth.getSession();
  if (error) {
    console.warn('[authService] getCurrentSession', error.message);
    return null;
  }
  return data.session ?? null;
}

/** Perfil `public.usuario` ligado ao utilizador Auth actual. */
export async function fetchProfileByAuthUserId(authUserId) {
  if (!authUserId || !isSupabaseConfigured) return null;
  const { data, error } = await supabase
    .from('usuario')
    .select('*')
    .eq('auth_user_id', authUserId)
    .maybeSingle();

  if (error && error.code !== 'PGRST116') {
    console.warn('[authService] fetchProfileByAuthUserId', error.code || error.message);
    return null;
  }
  return data || null;
}

export async function getCurrentProfile() {
  const session = await getCurrentSession();
  if (!session?.user?.id) return null;
  const row = await fetchProfileByAuthUserId(session.user.id);
  return row ? buildAppUser(row, session.user.id) : null;
}

/**
 * Cria linha em `public.usuario` para o utilizador Auth autenticado (requer sessão JWT).
 * @returns {Promise<object|null>} linha criada ou null em erro
 */
export async function createInternalProfileRow({
  authUserId,
  nome,
  email,
  tipo_usuario = DEFAULT_SIGNUP_PROFILE.tipo_usuario,
  nivel_acesso = DEFAULT_SIGNUP_PROFILE.nivel_acesso,
  status = DEFAULT_SIGNUP_PROFILE.status,
}) {
  if (!isSupabaseConfigured || !authUserId) return null;

  const insertRow = {
    auth_user_id: authUserId,
    nome: String(nome ?? '').trim(),
    nome_email: normalizeAuthEmail(email),
    tipo_usuario,
    nivel_acesso,
    status,
  };

  authSignupDevLog('profile_insert_start', {
    payload: insertRow,
    auth_user_id: authUserId,
  });

  const session = await getCurrentSession();
  authSignupDevLog('profile_insert_session', {
    hasSession: !!session,
    hasAccessToken: !!session?.access_token,
    auth_uid_from_session: session?.user?.id ?? null,
    auth_uid_expected: authUserId,
    auth_uid_match: session?.user?.id === authUserId,
  });

  const { data: created, error: insErr } = await supabase
    .from('usuario')
    .insert([insertRow])
    .select('id_usuario, nome, nome_email, tipo_usuario, nivel_acesso, status, auth_user_id')
    .single();

  if (insErr) {
    authSignupDevLog('profile_insert_error', {
      ...formatSupabaseError(insErr),
      auth_user_id: authUserId,
    });
    return { error: insErr, row: null };
  }

  authSignupDevLog('profile_insert_ok', {
    id_usuario: created?.id_usuario,
    auth_user_id: created?.auth_user_id,
  });
  return { error: null, row: created };
}

/**
 * Garante perfil interno após login/confirmação de e-mail (fallback se trigger SQL não existir).
 */
export async function ensureInternalProfileFromAuthUser(authUser, overrides = {}) {
  if (!authUser?.id || !isSupabaseConfigured) return null;

  const existing = await fetchProfileByAuthUserId(authUser.id);
  if (existing) {
    return buildAppUser(existing, authUser.id);
  }

  const session = await getCurrentSession();
  if (!session?.access_token) {
    authSignupDevLog('ensure_profile_skip_no_session', { auth_user_id: authUser.id });
    return null;
  }

  const emailNorm = normalizeAuthEmail(overrides.email ?? authUser.email);
  const nomeTrim =
    String(overrides.nome ?? authUser.user_metadata?.nome ?? '').trim() ||
    emailNorm.split('@')[0] ||
    'Utilizador';

  const result = await createInternalProfileRow({
    authUserId: authUser.id,
    nome: nomeTrim,
    email: emailNorm,
  });

  if (result.error) {
    if (result.error.code === '23505') {
      const row = await fetchProfileByAuthUserId(authUser.id);
      return row ? buildAppUser(row, authUser.id) : null;
    }
    return null;
  }

  return result.row ? buildAppUser(result.row, authUser.id) : null;
}

function profileInsertErrorMessage(insErr) {
  const code = insErr?.code;
  if (code === '23505') {
    return 'Já existe uma conta com este e-mail.';
  }
  if (code === '42501' || /permission denied|row-level security|RLS/i.test(insErr?.message || '')) {
    return (
      'Conta criada no login seguro, mas o perfil interno não pôde ser gravado (permissão RLS). ' +
      'Um administrador deve aplicar a política de cadastro ou o trigger automático no Supabase.'
    );
  }
  return (
    'Não foi possível concluir o cadastro (perfil interno). ' +
    'Se confirmou o e-mail, tente entrar novamente; se persistir, contacte o suporte.'
  );
}

/**
 * Login com Supabase Auth (fonte de verdade da sessão).
 */
export async function loginWithSupabaseAuth(email, password) {
  if (!isSupabaseConfigured) {
    throw new Error('Supabase não configurado.');
  }
  const emailNorm = normalizeAuthEmail(email);
  const { data, error } = await supabase.auth.signInWithPassword({
    email: emailNorm,
    password: String(password ?? ''),
  });

  if (error) {
    const msg = error.message || 'Falha na autenticação.';
    throw new Error(msg);
  }

  const authId = data.user?.id;
  if (!authId) {
    await supabase.auth.signOut();
    throw new Error('Sessão inválida após login.');
  }

  let profile = await fetchProfileByAuthUserId(authId);
  if (!profile) {
    const ensured = await ensureInternalProfileFromAuthUser(data.user, { email: emailNorm });
    if (ensured) {
      persistProfileCache(ensured);
      return ensured;
    }
    await supabase.auth.signOut();
    throw new Error('Perfil interno não encontrado para este usuário.');
  }

  const user = buildAppUser(profile, authId);
  persistProfileCache(user);
  return user;
}

/**
 * DEV apenas: login legado por `public.usuario.senha` (sem Supabase Auth).
 * TODO: remover antes de endurecimento de produção.
 */
async function tryLegacyDevLogin(email, password) {
  if (!import.meta.env.DEV || !isSupabaseConfigured) return null;

  const emailNorm = normalizeAuthEmail(email);
  const { data: usuario, error } = await supabase
    .from('usuario')
    .select('*')
    .eq('nome_email', emailNorm)
    .maybeSingle();

  if (error || !usuario) return null;
  if (usuario.senha !== password) return null;

  if (String(usuario.status || '').toLowerCase() === 'inativo') {
    throw new Error('Este usuário está inativo e não pode realizar login.');
  }

  const user = buildAppUser(usuario, usuario.auth_user_id || null);
  persistProfileCache(user);
  return user;
}

/** Conta demo sem linha Auth (apenas DEV). */
function tryDemoDevLogin(emailNorm, password) {
  if (!import.meta.env.DEV) return null;
  if (emailNorm === 'admin@finder.com' && password === '123456') {
    const userData = {
      id_usuario: 1,
      auth_user_id: null,
      email: emailNorm,
      nome_email: emailNorm,
      nome: 'Administrador',
      tipo_usuario: 'Administrador',
      nivel_acesso: 1,
      status: 'Ativo',
      tipo: 'Administrador',
      nivel: 1,
    };
    persistProfileCache(userData);
    return userData;
  }
  return null;
}

/**
 * Login: Supabase Auth → perfil por `auth_user_id`.
 * Fallback DEV: tabela `usuario` com senha em texto OU demo admin (ver documentação).
 */
export async function login(email, password) {
  const emailNorm = normalizeAuthEmail(email);
  const pwd = String(password ?? '');

  if (!isSupabaseConfigured) {
    const demo = import.meta.env.DEV ? tryDemoDevLogin(emailNorm, pwd) : null;
    if (demo) return demo;
    throw new Error('Supabase não configurado.');
  }

  try {
    return await loginWithSupabaseAuth(emailNorm, pwd);
  } catch (e) {
    if (import.meta.env.DEV) {
      const demo = tryDemoDevLogin(emailNorm, pwd);
      if (demo) return demo;
      const legacy = await tryLegacyDevLogin(email, pwd);
      if (legacy) return legacy;
    }
    throw e;
  }
}

/**
 * Registo: Supabase Auth + perfil em `public.usuario` (sem gravar `senha` na tabela).
 *
 * @returns {Promise<
 *   | { status: 'complete'; user: object }
 *   | { status: 'pending_email_confirmation'; email: string; authUserId: string; message: string }
 * >}
 */
export async function registerWithSupabaseAuth({ nome, email, password }) {
  if (!isSupabaseConfigured) {
    throw new Error('Cadastro indisponível. Verifique a configuração do Supabase.');
  }

  const nomeTrim = String(nome ?? '').trim();
  const emailNorm = normalizeAuthEmail(email);
  const pwd = String(password ?? '');

  if (!nomeTrim) throw new Error('Informe seu nome.');
  if (!emailNorm || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailNorm)) {
    throw new Error('Informe um e-mail válido.');
  }
  if (!pwd || pwd.length < 6) {
    throw new Error('A senha deve ter pelo menos 6 caracteres.');
  }

  authSignupDevLog('signUp_start', { email: emailNorm, nome: nomeTrim });

  const emailRedirectTo = getAuthCallbackRedirectUrl();
  authSignupDevLog('signUp_redirect', getAuthRedirectLogMeta(emailRedirectTo));

  const { data: signData, error: signErr } = await supabase.auth.signUp({
    email: emailNorm,
    password: pwd,
    options: {
      data: { nome: nomeTrim },
      emailRedirectTo,
    },
  });

  if (signErr) {
    const errText = `${signErr.message || ''} ${signErr.code || ''}`.toLowerCase();
    if (/email rate limit exceeded|rate limit exceeded.*email/i.test(errText)) {
      authSignupDevLog('email_rate_limit_exceeded', formatSupabaseError(signErr));
      throw new Error(
        'Limite temporário de envio de e-mails atingido. Tente novamente mais tarde ou use uma conta já criada.',
      );
    }
    authSignupDevLog('signUp_error', formatSupabaseError(signErr));
    if (/already registered|already exists|User already/i.test(signErr.message || '')) {
      throw new Error('Já existe uma conta com este e-mail.');
    }
    throw new Error(signErr.message || 'Não foi possível criar a conta.');
  }

  const authUser = signData.user;
  const session = signData.session;

  authSignupDevLog('signUp_result', {
    userId: authUser?.id ?? null,
    hasUser: !!authUser?.id,
    hasSession: !!session,
    hasAccessToken: !!session?.access_token,
    emailConfirmedAt: authUser?.email_confirmed_at ?? null,
  });

  if (!authUser?.id) {
    throw new Error('Registo incompleto. Tente novamente.');
  }

  if (!session?.access_token) {
    authSignupDevLog('signUp_pending_email', {
      auth_user_id: authUser.id,
      note: 'Sem sessão JWT — não inserir em public.usuario com cliente anon (RLS).',
    });
    return {
      status: 'pending_email_confirmation',
      email: emailNorm,
      authUserId: authUser.id,
      message: 'Conta criada. Confirme seu e-mail e depois faça login.',
    };
  }

  let profileResult = await createInternalProfileRow({
    authUserId: authUser.id,
    nome: nomeTrim,
    email: emailNorm,
  });

  if (profileResult.error) {
    authSignupDevLog('profile_insert_retry_refresh', { auth_user_id: authUser.id });
    await supabase.auth.refreshSession();
    profileResult = await createInternalProfileRow({
      authUserId: authUser.id,
      nome: nomeTrim,
      email: emailNorm,
    });
  }

  if (profileResult.error) {
    clearProfileCache();
    throw new Error(profileInsertErrorMessage(profileResult.error));
  }

  const user = buildAppUser(profileResult.row, authUser.id);
  persistProfileCache(user);

  authSignupDevLog('signUp_complete', {
    id_usuario: user.id_usuario,
    auth_user_id: authUser.id,
  });

  return { status: 'complete', user };
}

/** Compatível com `Login` / `AuthContext` que enviam `senha`. */
export async function registerUser(payload) {
  return registerWithSupabaseAuth({
    nome: payload.nome,
    email: payload.email,
    password: payload.senha ?? payload.password,
  });
}

export async function logout() {
  if (isSupabaseConfigured) {
    await supabase.auth.signOut();
  }
  clearProfileCache();
}

/**
 * Auth custom + tabela `usuario` (senha em texto no MVP antigo).
 * TODO: substituir por hash ou remover após migração total para Supabase Auth.
 */
export const authService = {
  normalizeAuthEmail,
  buildAppUser,
  persistProfileCache,
  clearProfileCache,
  hydrateDevLegacyFromCache,
  getUser,
  getCurrentSession,
  getCurrentProfile,
  fetchProfileByAuthUserId,
  createInternalProfileRow,
  ensureInternalProfileFromAuthUser,
  loginWithSupabaseAuth,
  login,
  registerWithSupabaseAuth,
  registerUser,
  logout,
};
