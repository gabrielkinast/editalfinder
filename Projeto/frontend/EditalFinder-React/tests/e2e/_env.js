/**
 * Carrega variáveis de .env.local para o processo Node do Playwright (sem commitar secrets).
 * Vite já embute VITE_* no build; este loader garante leitura no config e nos helpers.
 */
import { existsSync, readFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '../..');

export const AUTH_STORAGE_PATH = resolve(ROOT, 'playwright/.auth/user.json');

/** Basename web (GitHub Pages / preview). Tauri usa vazio — E2E web sempre com prefixo. */
export const E2E_BASE_PATH = normalizeBasePath(process.env.E2E_BASE_PATH ?? '/editalfinder');

export const E2E_HOST = process.env.E2E_HOST || '127.0.0.1';
export const E2E_PORT = process.env.E2E_PORT || '4173';
export const E2E_ORIGIN = `http://${E2E_HOST}:${E2E_PORT}`;

/** baseURL do Playwright — deve terminar com o basename (barra final opcional). */
export const E2E_BASE_URL =
  process.env.E2E_BASE_URL || `${E2E_ORIGIN}${E2E_BASE_PATH}`;

function normalizeBasePath(raw) {
  const s = String(raw || '').trim();
  if (!s || s === '/') return '';
  const withSlash = s.startsWith('/') ? s : `/${s}`;
  return withSlash.replace(/\/$/, '');
}

function parseEnvLine(line) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) return null;
  const eq = trimmed.indexOf('=');
  if (eq < 0) return null;
  const key = trimmed.slice(0, eq).trim();
  let val = trimmed.slice(eq + 1).trim();
  if (
    (val.startsWith('"') && val.endsWith('"')) ||
    (val.startsWith("'") && val.endsWith("'"))
  ) {
    val = val.slice(1, -1);
  }
  return { key, val };
}

/** Carrega .env.local e .env (não sobrescreve vars já definidas no shell). */
export function loadLocalEnvFiles() {
  for (const name of ['.env.local', '.env']) {
    const filePath = resolve(ROOT, name);
    if (!existsSync(filePath)) continue;
    const text = readFileSync(filePath, 'utf8');
    for (const line of text.split(/\r?\n/)) {
      const parsed = parseEnvLine(line);
      if (!parsed) continue;
      if (process.env[parsed.key] == null || process.env[parsed.key] === '') {
        process.env[parsed.key] = parsed.val;
      }
    }
  }
}

export function isAuthConfigured() {
  const email = String(process.env.E2E_USER_EMAIL || '').trim();
  const password = String(process.env.E2E_USER_PASSWORD || '');
  return Boolean(email && password);
}

export function hasSupabaseEnv() {
  return Boolean(
    String(process.env.VITE_SUPABASE_URL || '').trim() &&
      String(process.env.VITE_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_KEY || '').trim(),
  );
}

export function safeSupabaseHost() {
  const url = String(process.env.VITE_SUPABASE_URL || '').trim();
  if (!url) return null;
  try {
    return new URL(url).host;
  } catch {
    return null;
  }
}

/** Log seguro no startup do Playwright (sem keys/tokens). */
export function logE2eEnvSummary() {
  const host = safeSupabaseHost();
  // eslint-disable-next-line no-console
  console.log('[e2e] env summary:', {
    baseURL: E2E_BASE_URL,
    basePath: E2E_BASE_PATH || '(root)',
    hasSupabaseUrl: Boolean(process.env.VITE_SUPABASE_URL),
    hasSupabaseAnonKey: Boolean(
      process.env.VITE_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_KEY,
    ),
    supabaseHost: host || '(n/a)',
    authConfigured: isAuthConfigured(),
  });
}

export function ensureAuthDir() {
  mkdirSync(dirname(AUTH_STORAGE_PATH), { recursive: true });
}
