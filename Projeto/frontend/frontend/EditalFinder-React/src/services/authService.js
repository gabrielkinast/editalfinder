import { supabase, isSupabaseConfigured } from './api';

const STORAGE_KEY = 'editalFinderUser';

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

  const profile = await fetchProfileByAuthUserId(authId);
  if (!profile) {
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

  const { data: signData, error: signErr } = await supabase.auth.signUp({
    email: emailNorm,
    password: pwd,
    options: {
      data: { nome: nomeTrim },
    },
  });

  if (signErr) {
    if (/already registered|already exists|User already/i.test(signErr.message || '')) {
      throw new Error('Já existe uma conta com este e-mail.');
    }
    throw new Error(signErr.message || 'Não foi possível criar a conta.');
  }

  const authUser = signData.user;
  if (!authUser?.id) {
    throw new Error('Registo incompleto. Tente novamente.');
  }

  const insertRow = {
    auth_user_id: authUser.id,
    nome: nomeTrim,
    nome_email: emailNorm,
    tipo_usuario: 'Consultor',
    nivel_acesso: 2,
    status: 'Ativo',
  };

  const { data: created, error: insErr } = await supabase
    .from('usuario')
    .insert([insertRow])
    .select('id_usuario, nome, nome_email, tipo_usuario, nivel_acesso, status, auth_user_id')
    .single();

  if (insErr) {
    await supabase.auth.signOut();
    clearProfileCache();
    if (insErr.code === '23505') {
      throw new Error('Já existe uma conta com este e-mail.');
    }
    console.warn('[authService] register insert', insErr.code || insErr.message);
    throw new Error('Conta criada no Auth, mas falhou ao criar o perfil interno. Contacte o suporte.');
  }

  if (!signData.session) {
    await supabase.auth.signOut();
    clearProfileCache();
    throw new Error(
      'Conta criada. Confirme o link enviado ao seu e-mail para iniciar sessão (ou desative confirmação de e-mail no Supabase para testes locais).',
    );
  }

  const user = buildAppUser(created, authUser.id);
  persistProfileCache(user);
  return user;
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
 * Não expor tipo/nível/status vindos do cliente no insert público — aqui só leitura legado DEV.
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
  loginWithSupabaseAuth,
  login,
  registerWithSupabaseAuth,
  registerUser,
  logout,
};
