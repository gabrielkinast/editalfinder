import { createClient } from '@supabase/supabase-js';
import { SUPABASE_URL, SUPABASE_ANON_KEY, isSupabaseConfigured, APP_ENV } from '../config/env.js';

export { isSupabaseConfigured } from '../config/env.js';

function logMissingConfigOnce() {
  if (typeof window === 'undefined') return;
  console.warn(
    `[${APP_ENV} | EditalFinder] Supabase não configurado: defina VITE_SUPABASE_URL e VITE_SUPABASE_ANON_KEY em .env.local (veja .env.example). Sem isso não há dados remotos; o login de demonstração pode continuar a funcionar.`
  );
}

if (!isSupabaseConfigured) {
  logMissingConfigOnce();
}

/**
 * Cliente Supabase browser-only com chave anon.
 * Sem .env válido, usa host inválido só para satisfazer imports — não envie dados sensíveis.
 */
export const supabase = isSupabaseConfigured
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : createClient('https://offline.invalid', 'public-anon-placeholder-not-used');

/**
 * Mensagem para UI ou logs (nunca inclui segredos).
 */
export function getSupabaseConfigHint() {
  if (isSupabaseConfigured) {
    return { ok: true, host: (() => {
      try {
        return new URL(SUPABASE_URL).host;
      } catch {
        return '(url inválida)';
      }
    })() };
  }
  return {
    ok: false,
    message: 'Faltam VITE_SUPABASE_URL e/ou VITE_SUPABASE_ANON_KEY no .env.local.',
  };
}
