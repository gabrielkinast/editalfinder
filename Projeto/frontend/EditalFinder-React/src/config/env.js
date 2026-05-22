/**
 * Configuração central lida de import.meta.env (Vite).
 * Nunca coloque chaves reais aqui — use .env.local
 */

import { DEFAULT_SUPPORT_EMAIL } from '../constants/editalFeedbackConfig';

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
  if (raw == null) return defaultValue;
  const s = String(raw).trim();
  if (s === '') return defaultValue;
  const sl = s.toLowerCase();
  return sl === '1' || sl === 'true' || sl === 'yes' || sl === 'on';
}

/** local | staging | production (texto livre para a UI / logs) */
export const APP_ENV = str('VITE_APP_ENV', 'local');

export const APP_NAME = str('VITE_APP_NAME', 'EditalFinder');

/**
 * URL pública da app (com basename, sem barra final).
 * Produção: https://seudominio.com/editalfinder
 */
export const PUBLIC_SITE_URL = str('VITE_PUBLIC_SITE_URL');

/** URL absoluta do callback de confirmação de e-mail. */
export const AUTH_CALLBACK_URL = str('VITE_AUTH_CALLBACK_URL');

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

/** Concursos & Seleções — views públicas (RLS + anon) */
export const VIEW_CONCURSOS = str('VITE_VIEW_CONCURSOS', 'vw_concursos_front');
export const VIEW_VESTIBULARES = str('VITE_VIEW_VESTIBULARES', 'vw_vestibulares_front');

/** Feature flags */
export const FEATURE_PORTAIS_ESTRATEGICOS = truthyEnv('VITE_ENABLE_PORTAIS_ESTRATEGICOS', true);
export const FEATURE_FORNECEDORES = truthyEnv('VITE_ENABLE_FORNECEDORES', true);
export const FEATURE_INVESTIMENTOS = truthyEnv('VITE_ENABLE_INVESTIMENTOS', true);
export const FEATURE_RADAR = truthyEnv('VITE_ENABLE_RADAR', true);
export const ENABLE_CONCURSOS = truthyEnv('VITE_ENABLE_CONCURSOS', true);
/** Favoritos persistentes (RLS + anon) — view leitura, tabela escrita. */
export const VIEW_EDITAIS_FAVORITOS = str(
  'VITE_VIEW_EDITAIS_FAVORITOS',
  'vw_editais_favoritos_front',
);
export const TABLE_EDITAL_FAVORITO = str('VITE_TABLE_EDITAL_FAVORITO', 'edital_favorito');
export const FEATURE_EDITAL_FAVORITOS = truthyEnv('VITE_ENABLE_EDITAL_FAVORITOS', true);
/** POST JSON para reporte de problemas em editais (Edge Function ou API). */
export const EDITAL_FEEDBACK_ENDPOINT = str('VITE_EDITAL_FEEDBACK_ENDPOINT');
/** Em DEV: simular sucesso quando endpoint ausente (testes de UI). */
export const EDITAL_FEEDBACK_MOCK_DEV = truthyEnv('VITE_EDITAL_FEEDBACK_MOCK_DEV', false);
/** E-mail de suporte (referência; envio real no backend). */
export const SUPPORT_EMAIL = str('VITE_SUPPORT_EMAIL') || DEFAULT_SUPPORT_EMAIL;
export const ENABLE_DEBUG_PIPELINE = truthyEnv('VITE_ENABLE_DEBUG_PIPELINE', false);
/** Workspace do Consultor — rota /workspace-consultor e item de menu. */
export const ENABLE_CONSULTOR_WORKSPACE = truthyEnv('VITE_ENABLE_CONSULTOR_WORKSPACE', false);
/** Workspace Científico — rota /workspace-cientifico e item de menu. */
export const ENABLE_SCIENTIFIC_WORKSPACE = truthyEnv('VITE_ENABLE_SCIENTIFIC_WORKSPACE', false);
/** IA científica — apenas via backend/Edge Function; nunca true com chave no Vite. */
export const ENABLE_SCIENTIFIC_AI = truthyEnv('VITE_ENABLE_SCIENTIFIC_AI', false);

if (import.meta.env.DEV) {
  console.info('[consultor-workspace] env_flag', {
    raw: import.meta.env.VITE_ENABLE_CONSULTOR_WORKSPACE,
    parsed: ENABLE_CONSULTOR_WORKSPACE,
  });
  console.info('[scientific-workspace] env_flag', {
    raw: import.meta.env.VITE_ENABLE_SCIENTIFIC_WORKSPACE,
    parsed: ENABLE_SCIENTIFIC_WORKSPACE,
  });
}

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
