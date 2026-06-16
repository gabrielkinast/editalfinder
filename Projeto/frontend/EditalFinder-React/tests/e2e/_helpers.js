// Helpers compartilhados para os specs E2E (QA 1.1 — harness; QA 1.2 — expanded suite).
import { expect } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  E2E_BASE_PATH,
  isAuthConfigured,
  hasSupabaseEnv,
} from './_env.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

/** Evidências gerais QA 1.2 (skips, export, etc.). */
export const DEBUG_E2E_DIR = resolve(__dirname, '../../qa/artifacts/playwright/debug-e2e');

export { isAuthConfigured, hasSupabaseEnv } from './_env.js';

export const FATAL_ERROR_TEXTS = [
  'Não foi possível carregar',
  'Não foi possível carregar os dados do edital',
];

export const SKIP_NO_AUTH =
  'E2E_USER_EMAIL e E2E_USER_PASSWORD não configurados — defina no shell ou .env.local (não commitar).';

export const SKIP_NO_SUPABASE =
  'VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY ausentes no build — testes de dados reais ignorados.';

export const SKIP_NO_CATALOG =
  'Catálogo vazio ou barra de stats indisponível — verifique auth, RLS e env do preview.';

export const SKIP_NO_WRITE =
  'SKIP_WRITE_OPT_IN_DISABLED: set E2E_ALLOW_WRITE_TESTS=1 to create a manual edital';

/** Escrita real em Cadastros exige flag explícita. */
export function isWriteTestsAllowed() {
  return String(process.env.E2E_ALLOW_WRITE_TESTS || '').trim() === '1';
}

export function skipIfNoWriteTests(test) {
  if (!isWriteTestsAllowed()) {
    test.skip(true, SKIP_NO_WRITE);
  }
}

/**
 * Caminho relativo para page.goto com baseURL que inclui basename.
 * Playwright resolve new URL(relative, baseURL) — paths absolutos (/foo) ignoram o basename.
 */
export function appPath(route = '/') {
  const r = String(route ?? '/').trim();
  if (!r || r === '/') return './';
  const cleaned = r.replace(/^\//, '');
  return `./${cleaned}`;
}

/** Alias legível para specs. */
export function appUrl(route = '/') {
  return appPath(route);
}

export function skipIfNoAuth(test) {
  if (!isAuthConfigured()) {
    test.skip(true, SKIP_NO_AUTH);
  }
}

export function skipIfNoSupabase(test) {
  if (!hasSupabaseEnv()) {
    test.skip(true, SKIP_NO_SUPABASE);
  }
}

/** Habilita instrumentação dev de QA via localStorage antes da app montar. */
export async function enableQaDebug(page) {
  await page.addInitScript(() => {
    try {
      localStorage.setItem('EDITALFINDER_DEBUG_EXTERNAL_LINKS', '1');
      localStorage.setItem('EDITALFINDER_DEBUG_ROUTES', '1');
      localStorage.setItem('EDITALFINDER_DEBUG_DATA_COUNTS', '1');
    } catch {
      /* ignore */
    }
  });
}

/** Coleta erros de console durante o teste. */
export function collectConsoleErrors(page) {
  const errors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', (err) => errors.push(String(err)));
  return errors;
}

/** Falha se algum texto fatal estiver visível no body. */
export async function expectNoFatalError(page) {
  const body = await page.locator('body').innerText();
  for (const marker of FATAL_ERROR_TEXTS) {
    expect(body, `texto fatal encontrado: "${marker}"`).not.toContain(marker);
  }
}

/** Login real via formulário — nunca loga senha. */
export async function loginIfConfigured(page) {
  if (!isAuthConfigured()) return false;

  const email = String(process.env.E2E_USER_EMAIL).trim();
  const password = String(process.env.E2E_USER_PASSWORD);

  await page.goto(appPath('/login'));
  await expect(page.getByTestId('login-page')).toBeVisible({ timeout: 15_000 });

  await page.locator('#email').fill(email);
  await page.locator('#password').fill(password);
  await page.getByTestId('login-submit').click();

  await page.waitForURL(
    (url) => {
      const path = url.pathname;
      const suffix = E2E_BASE_PATH ? `${E2E_BASE_PATH}/dashboard` : '/dashboard';
      return path.endsWith('/dashboard') || path.endsWith(suffix);
    },
    { timeout: 45_000 },
  );

  await expect(page.getByTestId('dashboard-page')).toBeVisible({ timeout: 20_000 });
  return true;
}

export async function safeClickByTestId(page, testId, options = {}) {
  const loc = page.getByTestId(testId).first();
  await expect(loc).toBeVisible({ timeout: options.timeout ?? 10_000 });
  await loc.click();
}

export async function getVisibleTextSnapshot(page) {
  return page.locator('body').innerText();
}

/**
 * @deprecated Preferir requireCatalogReady de ./_catalog.js (QA 1.1B).
 * Mantido como alias fino para compatibilidade.
 */
export async function requireCatalogData(page, test, slug = 'catalog') {
  const { requireCatalogReady } = await import('./_catalog.js');
  return requireCatalogReady(page, test, slug);
}

/** Detecta se a página atual é login (rota protegida redirecionou). */
export async function isLoginPage(page) {
  return page.getByTestId('login-page').isVisible({ timeout: 5_000 }).catch(() => false);
}

/**
 * Aguarda página estável (sem skeleton de loading comum).
 * @param {import('@playwright/test').Page} page
 * @param {string} [pageTestId] — testid do wrapper principal
 */
export async function waitForPageReady(page, pageTestId, timeout = 60_000) {
  if (pageTestId) {
    await expect(page.getByTestId(pageTestId)).toBeVisible({ timeout });
  }
  const loading = page.getByTestId('editais-loading');
  if (await loading.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await loading.waitFor({ state: 'hidden', timeout }).catch(() => {});
  }
}

/**
 * Navega para rota autenticada; retorna { ok, reason }.
 */
export async function requireAuthenticatedPage(page, route = '/editais', timeout = 60_000) {
  const { ensureAuthenticatedOnEditais } = await import('./_catalog.js');
  if (route === '/editais' || route === 'editais') {
    return ensureAuthenticatedOnEditais(page, timeout);
  }

  await page.goto(appPath(route), { waitUntil: 'domcontentloaded', timeout });

  if (await isLoginPage(page)) {
    if (!isAuthConfigured()) {
      return { ok: false, reason: 'redirected_to_login_no_credentials' };
    }
    const relogged = await loginIfConfigured(page);
    if (!relogged) return { ok: false, reason: 'redirected_to_login_relogin_failed' };
    await page.goto(appPath(route), { waitUntil: 'domcontentloaded', timeout });
  }

  if (await isLoginPage(page)) {
    return { ok: false, reason: 'still_on_login_after_relogin' };
  }
  return { ok: true };
}

/** Salva JSON/TXT de evidência em debug-e2e (sem secrets). */
export async function saveE2EEvidence(slug, data = {}, page = null) {
  mkdirSync(DEBUG_E2E_DIR, { recursive: true });
  const safe = { ...data, timestamp: new Date().toISOString() };
  for (const key of Object.keys(safe)) {
    const lk = key.toLowerCase();
    if (lk.includes('password') || lk.includes('token') || lk.includes('secret')) {
      safe[key] = '[REDACTED]';
    }
  }
  writeFileSync(resolve(DEBUG_E2E_DIR, `${slug}.json`), JSON.stringify(safe, null, 2));
  if (page) {
    const bodyPreview = await page.locator('body').innerText().catch(() => '');
    writeFileSync(
      resolve(DEBUG_E2E_DIR, `${slug}.txt`),
      [`slug: ${slug}`, `url: ${page.url()}`, '', bodyPreview.slice(0, 3500)].join('\n'),
    );
    await page
      .screenshot({ path: resolve(DEBUG_E2E_DIR, `${slug}.png`), fullPage: true })
      .catch(() => {});
  }
}

/** Skip com evidência persistida (QA 1.2). */
export async function skipWithEvidence(test, page, reason, metadata = {}) {
  await saveE2EEvidence(`skip-${reason}`, { reason, ...metadata }, page);
  test.skip(true, `${reason} — evidência: debug-e2e/skip-${reason}.*`);
}

/** Primeiro card visível na lista de editais. */
export async function getFirstVisibleCard(page) {
  return getFirstVisibleEditalCard(page);
}

/** Primeiro card visível na lista de editais (alias explícito QA 1.3C). */
export async function getFirstVisibleEditalCard(page) {
  const cards = page.getByTestId('edital-card');
  const count = await cards.count();
  for (let i = 0; i < count; i += 1) {
    const card = cards.nth(i);
    if (await card.isVisible().catch(() => false)) return card;
  }
  return null;
}

/** Título legível do card (primeira linha significativa). */
export async function getCardTitle(card) {
  if (!card) return '';
  const text = await card.innerText().catch(() => '');
  const line = text.split('\n').map((l) => l.trim()).find((l) => l.length >= 4);
  return line ? line.slice(0, 80) : text.slice(0, 80);
}

const SEARCHABLE_TITLE_SKIP_RE =
  /^(pdf|detalhes|favorit|aberto|encerrado|vencendo|sem prazo|—|-|\d+\/\d+\/\d+)/i;

/** Extrai termo curto e pesquisável do card, ignorando badges e metadados. */
export async function getSearchableCardTitle(card) {
  if (!card) return '';
  const text = await card.innerText().catch(() => '');
  for (const line of text.split('\n').map((l) => l.trim())) {
    if (
      line.length >= 4 &&
      !SEARCHABLE_TITLE_SKIP_RE.test(line) &&
      /[a-zA-ZÀ-ú]{3,}/.test(line)
    ) {
      const words = line.split(/\s+/).filter((w) => w.length >= 2);
      if (words.length >= 1) return words.slice(0, 3).join(' ').slice(0, 40);
    }
  }
  return getCardTitle(card);
}

/**
 * Aguarda app autenticado estável após login (dashboard visível).
 * @param {import('@playwright/test').Page} page
 */
export async function waitForAuthenticatedAppReady(page) {
  await expect(page.getByTestId('dashboard-page')).toBeVisible({ timeout: 20_000 });
}

/**
 * Aguarda catálogo de editais pronto (wrapper + stats, sem loading).
 * @param {import('@playwright/test').Page} page
 */
export async function waitForEditaisCatalogReady(page, timeout = 60_000) {
  await waitForPageReady(page, 'editais-page', timeout);
  await expect(page.getByTestId('editais-stats-bar')).toBeVisible({ timeout });
  const loading = page.getByTestId('editais-loading');
  if (await loading.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await loading.waitFor({ state: 'hidden', timeout }).catch(() => {});
  }
}

/** Abre sidebar mobile de filtros, se necessário. */
export async function openEditaisSidebarIfNeeded(page) {
  const panel = page.getByTestId('semantic-status-filters');
  if (await panel.isVisible({ timeout: 1_500 }).catch(() => false)) return true;

  const mobileToggle = page.locator('.filter-toggle-mobile');
  if (await mobileToggle.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await mobileToggle.click();
    await page.waitForTimeout(350);
  }
  return page.getByTestId('semantic-status-filters').isVisible({ timeout: 5_000 }).catch(() => false);
}

/**
 * Expande a seção "Filtrar por status" (collapse defaultOpen=false).
 * @returns {Promise<boolean>}
 */
export async function openStatusFilterSection(page) {
  await openEditaisSidebarIfNeeded(page);

  const panel = page.getByTestId('semantic-status-filters');
  if (await panel.isVisible({ timeout: 2_000 }).catch(() => false)) return true;

  const section = page.getByTestId('semantic-status-section');
  const toggle = page.getByTestId('semantic-status-section-toggle');
  if (await toggle.isVisible({ timeout: 3_000 }).catch(() => false)) {
    const isOpen = await section.getAttribute('open');
    if (!isOpen) {
      await toggle.click();
      await page.waitForTimeout(250);
    }
  }

  return panel.isVisible({ timeout: 5_000 }).catch(() => false);
}

const DEFAULT_STATUS_PREFERRED = ['aberto', 'sem_prazo', 'encerrado', 'indefinido'];

/**
 * Marca o primeiro checkbox de status visível (preferência por ids).
 * @returns {Promise<{ id: string, checkbox: import('@playwright/test').Locator } | null>}
 */
export async function toggleFirstAvailableStatusFilter(page, preferred = DEFAULT_STATUS_PREFERRED) {
  for (const id of preferred) {
    const cb = page.getByTestId(`semantic-status-${id}`);
    if (await cb.isVisible({ timeout: 1_000 }).catch(() => false)) {
      await cb.check();
      await expect(cb).toBeChecked();
      return { id, checkbox: cb };
    }
  }

  const panel = page.getByTestId('semantic-status-filters');
  const first = panel.locator('input[type="checkbox"]').first();
  if (await first.isVisible({ timeout: 2_000 }).catch(() => false)) {
    const testId = await first.getAttribute('data-testid');
    await first.check();
    await expect(first).toBeChecked();
    return { id: testId?.replace('semantic-status-', '') || 'unknown', checkbox: first };
  }

  return null;
}

/** Navega para aba Editais em Cadastros (admin cai em Usuários por padrão). */
export async function navigateCadastrosEditaisTab(page) {
  const tab = page.getByTestId('cadastros-tab-editais');
  await expect(tab).toBeVisible({ timeout: 10_000 });
  if ((await tab.getAttribute('class'))?.includes('active')) return;
  await tab.click();
  await expect(page.locator('.cad-hero-editais')).toBeVisible({ timeout: 10_000 });
}

/** Fecha modal de edital admin sem salvar. */
export async function closeAdminEditalModal(page) {
  const titulo = page.getByTestId('edital-form-titulo');
  await expect(titulo).toBeVisible({ timeout: 8_000 });

  const cancel = page.getByTestId('edital-form-cancel');
  if (await cancel.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await cancel.click();
  } else {
    const close = page.getByTestId('edital-form-close');
    if (await close.count()) {
      await close.first().click();
    } else {
      await page.keyboard.press('Escape');
    }
  }

  await expect(titulo).not.toBeVisible({ timeout: 8_000 });
}

/**
 * Clica em botão de download e aguarda evento; retorna { ok, reason }.
 */
export async function safeDownloadClick(page, locator, options = {}) {
  const timeout = options.timeout ?? 25_000;
  try {
    await expect(locator).toBeVisible({ timeout: 10_000 });
  } catch {
    return { ok: false, reason: 'download_button_not_visible' };
  }

  page.once('dialog', (dialog) => dialog.accept().catch(() => {}));

  try {
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout }),
      locator.click(),
    ]);
    const suggested = download.suggestedFilename();
    await download.cancel().catch(() => {});
    if (!suggested) return { ok: false, reason: 'download_no_filename' };
    return { ok: true, filename: suggested };
  } catch (err) {
    return { ok: false, reason: 'download_timeout_or_blocked', detail: String(err?.message || err) };
  }
}

/** Abre sidebar de filtros em viewport mobile e expande seção de status. */
export async function ensureEditaisFiltersVisible(page) {
  return openStatusFilterSection(page);
}

/**
 * Fecha o modal de reporte de problema (QA 1.2 fix).
 * Usa botões com data-testid="report-problem-close" dentro do dialog ativo.
 */
export async function closeReportProblemModal(page) {
  const modal = page.getByTestId('report-problem-modal');
  await expect(modal).toBeVisible();

  const dialog = page.getByRole('dialog').filter({ has: modal });
  const closeBtn = dialog.getByTestId('report-problem-close');
  if (await closeBtn.count()) {
    await closeBtn.first().click();
  } else {
    const innerClose = modal.getByRole('button', { name: /fechar|cancelar/i });
    if (await innerClose.count()) {
      await innerClose.last().click();
    } else {
      await page.keyboard.press('Escape');
    }
  }

  await expect(modal).not.toBeVisible({ timeout: 8_000 });
}
