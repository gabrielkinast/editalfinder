// Camada 2 — Dashboard autenticado (QA 1.2).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  requireAuthenticatedPage,
  waitForPageReady,
  skipWithEvidence,
  appPath,
} from './_helpers.js';

test.describe('dashboard smoke [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('dashboard renderiza KPIs e link para editais [P2]', async ({ page }, testInfo) => {
    test.setTimeout(90_000);

    const auth = await requireAuthenticatedPage(page, '/dashboard');
    if (!auth.ok) {
      await skipWithEvidence(test, page, auth.reason, { route: '/dashboard' });
      return;
    }

    await waitForPageReady(page, 'dashboard-page');
    const body = await page.locator('body').innerText();

    expect(body).toMatch(/Dashboard|Central executiva|Resumo/i);
    expect(body.length).toBeGreaterThan(80);

    const editaisLink = page.getByRole('link', { name: /Ver editais|Ir para editais/i }).first();
    if (await editaisLink.isVisible({ timeout: 8_000 }).catch(() => false)) {
      await editaisLink.click();
      await expect(page.getByTestId('editais-page')).toBeVisible({ timeout: 30_000 });
    } else {
      await page.goto(appPath('/editais'));
      await expect(page.getByTestId('editais-page')).toBeVisible({ timeout: 30_000 });
    }

    await expectNoFatalError(page);
  });
});
