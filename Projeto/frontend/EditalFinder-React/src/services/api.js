import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://fptjlvzzfphltuucklau.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwdGpsdnp6ZnBobHR1dWNrbGF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMyNTY0ODksImV4cCI6MjA4ODgzMjQ4OX0.u_Psx-qozH2QEBCsIxNemrhhBUEjHm-iiFJPp6R71AQ';

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
