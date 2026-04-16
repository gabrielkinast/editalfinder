import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  throw new Error('Variáveis de ambiente VITE_SUPABASE_URL e VITE_SUPABASE_KEY não definidas. Crie o arquivo .env baseado no .env.example.');
}

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
