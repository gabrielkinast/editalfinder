/**
 * Configuração central lida de import.meta.env (Vite).
 * Nunca coloque chaves reais aqui — use .env.local
 */

function trimStr(v) {
  if (v == null) return '';
  return String(v).trim();
}

function str(key, fallback = '') {
  const v = trimStr(import.meta.env[key]);
  return v || fallback;
}

function truthyEnv(key, defaultValue = false) {
  const raw = import.meta.env[key];
  if (raw == null || raw === '') return defaultValue;
  const s = String(raw).trim().toLowerCase();
  return s === '1' || s === 'true' || s === 'yes' || s === 'on';
}

/** local | staging | production (texto livre para a UI / logs) */
export const APP_ENV = str('VITE_APP_ENV', 'local');

export const APP_NAME = str('VITE_APP_NAME', 'EditalFinder');

/** URL do projeto Supabase */
export const SUPABASE_URL = str('VITE_SUPABASE_URL');

/**
 * Chave anon/public (RLS). Aceita também VITE_SUPABASE_KEY legado.
 * Nunca use service_role no frontend.
 */
export const SUPABASE_ANON_KEY = str('VITE_SUPABASE_ANON_KEY') || str('VITE_SUPABASE_KEY');

export const isSupabaseConfigured = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

/** Nomes das views expostas ao front (ajustável por ambiente) */
export const VIEW_EDITAIS = str('VITE_VIEW_EDITAIS', 'vw_editais_front');
export const VIEW_NOTICIAS = str('VITE_VIEW_NOTICIAS', 'vw_noticias_front');
export const VIEW_PESQUISAS = str('VITE_VIEW_PESQUISAS', 'vw_pesquisas_front');
export const VIEW_FORNECEDORES = str('VITE_VIEW_FORNECEDORES', 'vw_fornecedores_front');
export const VIEW_INVESTIMENTOS = str('VITE_VIEW_INVESTIMENTOS', 'vw_investimentos_front');

/** Feature flags */
export const FEATURE_PORTAIS_ESTRATEGICOS = truthyEnv('VITE_ENABLE_PORTAIS_ESTRATEGICOS', true);
export const FEATURE_FORNECEDORES = truthyEnv('VITE_ENABLE_FORNECEDORES', true);
export const FEATURE_INVESTIMENTOS = truthyEnv('VITE_ENABLE_INVESTIMENTOS', true);
export const FEATURE_RADAR = truthyEnv('VITE_ENABLE_RADAR', true);
export const ENABLE_DEBUG_PIPELINE = truthyEnv('VITE_ENABLE_DEBUG_PIPELINE', false);

/**
 * Em desenvolvimento: avisa se faltar configuração crítica para dados remotos.
 * Nunca regista URLs completas com query nem chaves.
 */
function warnMissingCriticalEnvInDev() {
  if (!import.meta.env.DEV) return;
  const missing = [];
  if (!str('VITE_SUPABASE_URL')) missing.push('VITE_SUPABASE_URL');
  const anon = str('VITE_SUPABASE_ANON_KEY') || str('VITE_SUPABASE_KEY');
  if (!anon) missing.push('VITE_SUPABASE_ANON_KEY (ou VITE_SUPABASE_KEY legado)');
  if (missing.length === 0) return;
  console.error(
    `[EditalFinder | ${APP_ENV}] Configuração incompleta: defina em .env.local: ${missing.join(', ')}. ` +
      'Sem estes valores não há ligação ao Supabase (listas vazias além do login de demonstração). ' +
      'Veja .env.example — use apenas a chave anon, nunca service_role.'
  );
}

warnMissingCriticalEnvInDev();
